# Worked Example: Tiled Reduction

This example uses a NumPy program that **runs on a CPU-only machine** to demonstrate one of the most basic parallel patterns on a GPU: tiled reduction.

The point is not to launch a real kernel, but to turn the grid/block partitioning from [Runtime and Execution Model](../stack/runtime.en.md) and the tiling idea from [Operators and Compilation](../stack/compiler.en.md) into code that runs, produces deterministic output, and can be checked.

## The problem

Sum an array of 100,000 elements.

On a CPU that is a loop from one end to the other. On a GPU it cannot be: a single thread accumulating serially leaves thousands of compute units idle, and having every thread write one accumulator creates severe write contention.

## Two-stage reduction

The GPU approach splits the reduction into two stages:

```
input array (100,000 elements)
   │
   │  Stage 1: split into 391 blocks, each responsible for 256 elements
   ▼
 ┌────────┬────────┬────────┬─────┬────────┐
 │ block0 │ block1 │ block2 │ ... │block390│   ← blocks reduce in parallel
 └───┬────┴───┬────┴───┬────┴─────┴───┬────┘
     │        │        │              │
     ▼        ▼        ▼              ▼
  partial  partial  partial   ...  partial     ← 391 partial sums
     └────────┴────────┴──────────────┘
                     │
                     │  Stage 2: reduce the 391 partials
                     ▼
                 final result
```

The key property is that **blocks do not communicate**. Each block handles only its own 256 elements; within a block, threads can cooperate through shared memory and synchronize with each other, but combining across blocks requires a separate stage. This is what "no ordering is guaranteed between blocks" from the [runtime page](../stack/runtime.en.md) means in practice.

## The code

Full source is in `examples/tiled_reduction.py`. These two functions are the core:

```python
def block_partial_sums(data: np.ndarray, block_size: int) -> np.ndarray:
    """Stage 1: each block reduces its own slice into a partial sum."""
    n = data.size
    # grid size = ceiling division; the last block may be partial and needs padding
    grid_size = (n + block_size - 1) // block_size
    padded_len = grid_size * block_size

    padded = np.zeros(padded_len, dtype=data.dtype)
    padded[:n] = data

    # each row is the slice one block is responsible for
    tiles = padded.reshape(grid_size, block_size)
    return tiles.sum(axis=1)


def tiled_sum(data: np.ndarray, block_size: int = 256) -> float:
    """Stage 1 produces partials; stage 2 reduces them to a scalar."""
    partials = block_partial_sums(data, block_size)
    return float(partials.sum())
```

Two details are worth noting, because both have direct counterparts in a real kernel:

- **Ceiling division and padding.** `(n + block_size - 1) // block_size` is the standard way to compute grid size. 100,000 is not a multiple of 256, so the last block holds only 160 valid elements and the remaining 96 slots are padded with zero — safe for a sum, but a max-reduction would have to pad with `-inf` instead. In a real kernel this corresponds to a **bounds check**.
- **A block size of 256.** That is a multiple of 32, the warp size. A non-multiple leaves idle lanes in the final warp.

## Running it

```bash
python3 examples/tiled_reduction.py
```

Actual output:

```text
==========================================================
分块归约示例 / Tiled reduction demo
==========================================================
元素总数 n           : 100000
block 大小           : 256
grid 大小 (block 数) : 391
局部和数组长度       : 391
补零的元素个数       : 96
----------------------------------------------------------
NumPy 参考结果       : 50062.493666216
串行累加结果         : 50062.493666217
两阶段分块归约结果   : 50062.493666216
----------------------------------------------------------
分块 vs 参考的绝对差 : 7.276e-12
串行 vs 参考的绝对差 : 6.912e-10
校验通过：三种求和方式在浮点容差范围内一致。
==========================================================
```

## Why the check uses a tolerance rather than equality

The three results above do not agree in their final digits. That is not a bug — **floating-point addition is not associative**:

`(a + b) + c` is not necessarily equal to `a + (b + c)`

Change the order of summation and you change how rounding error accumulates. Tiled reduction turns a linear summation into a tree-shaped one, so a small difference from serial accumulation is unavoidable.

The interesting part: **the tree is usually more accurate**. In the output above, the tiled result differs from the NumPy reference by `7e-12` while serial accumulation differs by `6.9e-10` — two orders of magnitude worse. The reason is that in serial accumulation the running total keeps growing, so each small addend loses more significant bits; a tree reduction always adds numbers of comparable magnitude.

!!! warning "Something GPU documentation has to say out loud"
    A user moves a computation from CPU to GPU, sees the last few digits disagree, and concludes the GPU got it wrong. Unless the documentation says up front that parallel reduction changes summation order and therefore necessarily changes rounding, this question keeps arriving through support channels.

    The corresponding documentation action: state clearly, in any numerically sensitive section, **which operations are not bit-reproducible**, and recommend how to compare (tolerance-based, with guidance on choosing the tolerance).

## How this differs from a real kernel

The example deliberately omits several things a real GPU reduction must handle. Listing them so the simplification does not mislead:

| This example | A real kernel |
| --- | --- |
| `tiles.sum(axis=1)` reduces a block in one step | Multiple rounds of tree reduction over shared memory, with block-level synchronization |
| Padding handles the boundary | Conditional bounds checks for out-of-range threads |
| Stage 2 uses a NumPy sum | Typically a second kernel launch, or atomics |
| No notion of a memory hierarchy | Explicit staging between global and shared memory |

---

Previous: [Framework Integration](../stack/framework.en.md) ｜ Next: [Glossary](../glossary.en.md)
