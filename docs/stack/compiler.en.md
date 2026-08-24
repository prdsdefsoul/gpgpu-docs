# Operators and Compilation

This layer answers a single question: **which machine code executes this operator**.

## Two parallel routes

```
                      ┌────────────────────────────────┐
   operator call ──┬─> │ Route A: call a prebuilt library│ ──> a ready, heavily tuned kernel
                   │   └────────────────────────────────┘
                   │   ┌────────────────────────────────┐
                   └─> │ Route B: generate with compiler │ ──> a kernel specialized to this case
                       └────────────────────────────────┘
```

**Route A (operator libraries)** serves high-frequency, regularly shaped operators such as matrix multiply and convolution. Vendors pour engineering effort into hand-tuning these for each architecture generation, and the result is usually hard to beat. CUDA has cuBLAS and cuDNN; ROCm has rocBLAS and MIOpen.

**Route B (compilation)** serves custom operators, long-tail operators, and anything that benefits from **operator fusion**. Fusion is where this route earns its keep: merging several element-wise operators into one kernel eliminates round trips of intermediate results through device memory — and memory traffic, not arithmetic, is usually the real bottleneck.

Real systems use both: the hot operators go to libraries, the rest go through the compiler.

## The compilation path: source to machine code

Taking CUDA as the example, a `.cu` file goes roughly through:

```
  .cu source
     │
     ├─ split ───> host code ──> handed to the system C++ compiler
     │
     └──────────> device code
                     │
                     ▼
                front end (Clang/LLVM based)
                     │
                     ▼
                NVVM IR (a dialect of LLVM IR)
                     │
                     ▼
                PTX (virtual ISA, stable across architectures)
                     │
                     ▼
                SASS (real ISA, bound to one architecture)
                     │
                     ▼
                packed into a fatbinary, embedded in the host executable
```

### What PTX and SASS each do

This is the single most important pair of concepts in GPU compilation:

| | PTX | SASS |
| --- | --- | --- |
| Nature | A **virtual** ISA — a stable abstraction layer | The **real** ISA the hardware executes |
| Portability | Compatible across generations | Bound to a specific architecture version |
| Generated | At compile time | At compile time (AOT) or at run time (JIT) |

The layering buys **forward compatibility**: ship PTX inside the binary, and on a device newer than the compiler knew about, the driver can compile that PTX to the architecture's SASS on the spot. The cost is JIT latency on first run, usually softened by a compilation cache.

### The fatbinary

One binary can carry **SASS for several architectures** plus a PTX fallback. At load time the driver picks the closest match.

That explains a familiar experience: a program is unusually slow the first time it runs on a new card and normal afterwards — the first run JIT-compiled the PTX, later runs hit the cache. It also explains the opposite failure: if the build generated code for none of the target architectures and shipped no PTX, the program fails outright with "no kernel image available".

### Choosing between JIT and AOT

| | AOT | JIT |
| --- | --- | --- |
| When compiled | At build time | At run time |
| Startup cost | None | Compilation on first use |
| Shape specialization | Only the general case | Can specialize to actual tensor shapes |
| Forward compatibility | Depends on shipping PTX | Naturally handles newer architectures |

Deep learning frameworks lean heavily on JIT, precisely because tensor shapes are not known until run time and specialization pays real dividends.

## AI compilers: TVM and MLIR

A traditional compiler takes source code with unambiguous sequential semantics. An AI compiler takes something different — a **computation graph** — and must decide both *what* to compute and *how to arrange* the computation.

### Progressive lowering

The defining structure of an AI compiler is a stack of **intermediate representations**, descending from mathematical semantics toward hardware:

```
Graph-level IR        Operators: matmul, conv, relu — hardware independent
    │
    ▼
Loop-level IR         Explicit loop nests and access indices
    │
    ▼                 ← tiling, vectorization, parallelization, software pipelining happen here
Hardware-aware IR     Thread binding, shared memory allocation
    │
    ▼
Target code           PTX / LLVM IR / a specific ISA
```

**MLIR** provides exactly this — infrastructure for defining multiple IR levels and converting between them. It is not itself a compiler but a framework for building one, using dialects to let several abstraction levels coexist in one system.

**TVM** puts its weight on **schedule search**. One computation description admits an enormous number of loop arrangements (tile sizes, loop order, whether to vectorize), and the performance spread between them can span orders of magnitude. TVM searches that space automatically.

### The main optimizations

| Optimization | What it does | Why it works |
| --- | --- | --- |
| Operator fusion | Merges adjacent operators into one kernel | Removes device-memory round trips for intermediates |
| Tiling | Cuts large loops into cache- or shared-memory-sized blocks | Improves data reuse, cuts memory traffic |
| Layout transformation | Rearranges tensors in memory | Makes accesses contiguous and coalescible |
| Vectorization | Processes several elements per instruction | Raises per-instruction throughput |
| Constant folding / DCE | Generic graph-level simplification | Removes useless work |

**Tiling** is the entry point for understanding GPU performance work; the [tiled reduction example](../examples/tiled-reduction.en.md) shows it in its simplest form using NumPy.

## A documentation perspective on this layer

The difficulty here is the spread in reader background — from "I just want my program to run" to "I need to write a custom pass".

- **Split the user journeys.** Getting a program running on a new card and adding a compiler pass are two entirely different readers; put them on one page and neither finishes it.
- **Give architecture versions and compile flags as a copyable table.** This is the most looked-up and most error-prone information on the page, and it deserves a table rather than being scattered through prose.
- **Make error messages searchable.** A message like "no kernel image is available for execution on the device" deserves its own findable entry explaining that the build produced no code for that architecture.

---

Previous: [Runtime and Execution Model](runtime.en.md) ｜ Next: [Framework Integration](framework.en.md)
