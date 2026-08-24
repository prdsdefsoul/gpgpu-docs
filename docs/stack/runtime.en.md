# Runtime and Execution Model

The runtime is the primary host-side interface for driving the device. Understanding it comes down to one thing: **host and device advance independently**.

## The asynchronous model

In the snippet below, the genuinely confusing part is when each line returns:

```c
cudaMemcpyAsync(d_a, h_a, size, cudaMemcpyHostToDevice, stream);  // returns immediately
myKernel<<<grid, block, 0, stream>>>(d_a, d_c);                   // returns immediately
cudaMemcpyAsync(h_c, d_c, size, cudaMemcpyDeviceToHost, stream);  // returns immediately
cudaStreamSynchronize(stream);                                    // blocks until all three finish
```

The first three lines merely **enqueue** work and return; the host thread carries on. The device consumes the queue in order. Only the last line actually waits.

Two consequences follow directly:

- **The upside**: the host can submit work and get on with something else — preparing the next batch, say. Compute and data movement can overlap.
- **The trap**: errors are reported **late**. An illegal access in the kernel on line two will very likely surface at the synchronization on line four. So the first step in diagnosing a GPU error is usually to force synchronous execution, pulling the reported fault back to where it actually happened.

## Streams

A stream is an **in-order queue of work**. The rules are simple:

- Operations within one stream execute strictly in submission order
- Between streams there is **no ordering guarantee** whatsoever, and they may run concurrently

The classic use of multiple streams is overlapping copies with compute:

```
One stream:   [H2D copy][  compute  ][D2H copy][H2D copy][  compute  ][D2H copy]

Three:        s1: [H2D][  compute  ][D2H]
              s2:      [H2D][  compute  ][D2H]
              s3:           [H2D][  compute  ][D2H]
                       ↑ copies overlap compute; total wall time drops substantially
```

For the overlap to actually happen, host memory usually has to be **page-locked (pinned)**. Copies from pageable memory cannot be genuinely asynchronous, because the OS might swap the pages out mid-copy.

!!! warning "The default stream is not just another stream"
    Operations with no stream specified go to the **default stream**. Under legacy default-stream semantics, that stream synchronizes implicitly with the others — by far the most common reason multiple streams produce no concurrency at all. Modern CUDA offers alternatives, such as per-thread default streams, that change this behaviour.

## Events

An event is a **marker placed into a stream**, with two main uses:

- **Cross-stream synchronization**: making stream B wait on an event in stream A expresses "B depends on part of A's output" as a partial order, without synchronizing everything.
- **Timing**: measuring device-side elapsed time between two events. This is far more accurate than timing on the host, where the timestamps also capture asynchronous submission overhead.

## Memory model

| Kind | Location | Characteristics | Typical use |
| --- | --- | --- | --- |
| Device memory | VRAM | Fast for the device; not dereferenceable by the host | Nearly all computation data |
| Pageable host memory | System RAM | Ordinary `malloc`; may be swapped out | General host data |
| Pinned host memory | System RAM | Not swappable; enables truly async copies | Transfer buffers meant to overlap compute |
| Unified memory | Migrated by the system | One pointer for both sides; pages migrate on demand | Rapid prototyping, pointer-heavy structures |

Unified memory lowers the barrier to entry, but migration has a price: an unfavourable access pattern generates a storm of page faults and migrations, and can perform far worse than explicit management. It is a **trade of control for convenience**, not a free optimization.

## Kernel launch configuration

Launching a kernel means specifying how threads are organized:

```c
myKernel<<<gridDim, blockDim>>>(args);
```

- **Block**: a group of threads scheduled together onto one compute unit. Threads within a block can communicate through on-chip shared memory and can synchronize with each other.
- **Grid**: a set of blocks. Blocks are **independent** — no ordering is guaranteed between them, and you cannot assume they are resident simultaneously.
- **Warp / wavefront**: the granularity the hardware actually schedules. Threads in one warp advance in lockstep; if they diverge at a branch, both paths execute **serially**, cutting effective parallelism.

A few practical trade-offs:

- Block size is normally a multiple of the warp size; otherwise the final warp carries idle lanes
- Blocks that are too large exhaust registers and shared memory, reducing how many blocks stay resident (lower occupancy)
- Blocks that are too small cannot make good use of shared memory or block-level synchronization

The [tiled reduction example](../examples/tiled-reduction.en.md) demonstrates this grid/block partitioning with a NumPy program that runs on a CPU.

## A documentation perspective on this layer

The runtime is what developers touch most often, so its documentation largely determines the onboarding experience. A few lessons:

- **State the synchronization semantics of every API.** "Does this call block?" is the question readers ask most and documentation omits most. Asynchronous APIs especially need it spelled out: returning is not finishing.
- **Write down default behaviour explicitly.** The implicit synchronization of the default stream is the canonical example — leave it out and readers will write code that looks concurrent and runs serially.
- **Make examples runnable.** Runtime concepts are abstract; one runnable example with deterministic output beats three paragraphs of prose.

---

Previous: [Driver Layer](driver.en.md) ｜ Next: [Operators and Compilation](compiler.en.md)
