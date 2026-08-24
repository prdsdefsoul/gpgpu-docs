# Framework Integration

This layer decides **who executes an operator call**. For a chip vendor it is also the layer that determines whether new hardware can actually be used by the ecosystem.

## Dispatch

In PyTorch, `torch.matmul(a, b)` is not an implementation but a **dispatch entry point**. At run time the framework looks up which implementation to call based on the tensors' properties:

```
torch.matmul(a, b)
       │
       ▼
   Dispatcher ──── lookup keys: device type (CPU / CUDA / custom backend)
       │                        data type (fp32 / fp16 / bf16 ...)
       │                        autograd, quantization, ...
       ▼
   matched backend impl ──> calls an operator library or a compiled kernel
```

The same operator has several implementations registered under different keys. This keeps the framework front end uniform while letting backends grow independently — and it means **bringing up new hardware is, fundamentally, registering your implementations in that table**.

## Bringing up a new backend

A new chip has two broad routes into a framework.

### In-tree

Merge the backend into the framework's main repository. It stays in step with framework releases and works out of the box for users; the price is keeping pace with upstream changes indefinitely, and a high bar to get merged.

### Out-of-tree

Ship as a separate repository and package, registered through the framework's extension mechanism. PyTorch reserves device types such as `PrivateUse1` precisely so third-party backends can register a complete device backend without patching framework source.

Most new hardware starts out-of-tree, for a practical reason: iteration speed is not tied to upstream release cadence.

## What a backend has to cover

Registering a handful of operators will not run a real model. A usable backend needs at least:

| Component | Responsibility | Consequence of skipping it |
| --- | --- | --- |
| Device management | Enumeration, current-device switching, property queries | The framework cannot see the device |
| Memory allocator | Device allocation and release, normally with a **caching allocator** | Every allocation hits the driver; performance collapses |
| Operator implementations | Registering each operator for this device | Uncovered operators error out or fall back to CPU |
| Streams and events | Matching the framework's asynchronous semantics | Cannot cooperate with the framework's concurrency model |
| Type support | fp32 / fp16 / bf16 and friends | Mixed-precision training will not run |
| Serialization | Moving tensors between this device and the CPU | Checkpoints cannot be saved |

### Why the caching allocator is not optional

Training allocates and frees tensors constantly. If every one of those went to the driver, synchronization overhead alone would dominate the training loop.

So frameworks add a **caching allocator** above device memory: grab a large block from the driver once, then allocate and free within it, returning freed blocks to a pool for reuse. This is also the origin of the familiar "memory usage only ever goes up" observation — the framework is holding freed memory in its own pool rather than returning it to the driver.

## Operator coverage and fallback

No new backend covers every operator at once. Uncovered operators are handled one of two ways:

- **Raise an error**: tell the user plainly that the operator is unsupported. Unambiguous, but the experience is "it doesn't run".
- **Fall back to CPU**: copy the tensor to the host, compute there, copy back. The model runs, but every fallback costs two cross-device copies and a synchronization.

What makes fallback dangerous is that it is **silent**: the model works, performance is a fraction of what was expected, and the user has no idea why.

!!! tip "A textbook documentation problem"
    The table of "which operators are supported, and which fall back" is the highest-value and most frequently missing page in new-backend documentation. It is what lets a user decide in minutes whether their model is viable — instead of discovering after two days that the performance problem was a silent fallback.

    It has one other property: it must be **generated from the code**. A hand-maintained support list will drift out of date within two releases.

## A documentation perspective on this layer

The readers here are **ML engineers trying to port their own model**, and their questions are concrete:

- **Give a minimal migration path.** Readers want to know which lines of their existing training script change — not how the backend is architected.
- **Generate the operator support table automatically, and version it.** See above.
- **State performance expectations.** Which scenarios are already optimized and which are still in progress: saying so beats letting users find out by collision.
- **Organize troubleshooting by symptom, not by module.** Users arrive holding an error message, not a module name.

---

Previous: [Operators and Compilation](compiler.en.md) ｜ Next: [Tiled Reduction](../examples/tiled-reduction.en.md)
