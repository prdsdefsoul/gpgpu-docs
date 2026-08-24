# Layer Overview

## Starting from one line of code

Suppose you write this in Python:

```python
c = torch.matmul(a, b)      # a and b both live on the GPU
```

Before that line returns, the request has crossed the five layers below. Understanding a GPU software stack is essentially understanding **what each layer takes in, what it produces, and what it leaves to the next one**.

```
┌─────────────────────────────────────────────────┐
│  Application / DL framework   PyTorch, TF        │
├─────────────────────────────────────────────────┤
│  ① Framework integration      dispatch           │  → decides "who executes this operator"
├─────────────────────────────────────────────────┤
│  ② Operators & compilation    library / compiler │  → decides "which machine code runs"
├─────────────────────────────────────────────────┤
│  ③ Runtime                    streams, memory    │  → decides "when, and in what shape"
├─────────────────────────────────────────────────┤
│  ④ User-mode driver (UMD)     command encoding   │  → turns requests into hardware commands
├─────────────────────────────────────────────────┤
│  ⑤ Kernel-mode driver (KMD)   scheduling, MMU    │  → actually talks to the hardware
├─────────────────────────────────────────────────┤
│  Hardware                     compute units, VRAM│
└─────────────────────────────────────────────────┘
```

## What each layer owns

### ① Framework integration

Having received `torch.matmul(a, b)`, the framework first inspects the **device type** and **data type** of the two input tensors, then uses its dispatch mechanism (in PyTorch, the dispatcher) to look up the implementation registered for that device.

- **Input**: a framework-level operator call plus tensor metadata (shape, dtype, device, memory layout)
- **Output**: a call into a concrete backend implementation
- **The question that matters**: is there an implementation registered for this operator on the target device? If not, does the call silently fall back to CPU?

### ② Operators and compilation

This layer answers "which machine code performs the computation". There are two routes:

- **Call a prebuilt operator library.** For high-frequency, regularly shaped operators like matrix multiply, vendors ship heavily tuned libraries — cuBLAS and cuDNN in the CUDA ecosystem. The framework calls straight into them; nothing is compiled on the spot.
- **Generate code with a compiler.** For custom operators, or wherever operator fusion pays off, a compiler lowers the computation step by step down to the target ISA. AI compilers (TVM, the MLIR ecosystem) do their work here.

- **Input**: operator semantics, tensor shapes, target architecture
- **Output**: an executable kernel binary and its launch configuration

### ③ Runtime

The runtime is the host-side **programming interface** to the device, and the layer where the asynchronous execution model actually lives. It manages:

- Device contexts, and allocation and release of device memory
- Data movement between host and device
- **Streams (or queues)**: operations within one stream execute in order; separate streams may run concurrently
- **Events**: cross-stream synchronization and timing
- Kernel launches: submitting the kernel, its launch configuration (grid and block dimensions), and its arguments

- **Input**: API calls from the application or higher-level libraries
- **Output**: a sequence of asynchronous tasks enqueued on the device

See [Runtime and Execution Model](runtime.en.md).

### ④ User-mode driver (UMD)

Runtime calls must eventually become **command packets** the hardware understands. The UMD lives inside the user process address space and encodes kernel launches, memory copies, and similar requests into a command buffer, which it writes to a submission queue.

Making the UMD a separate layer pays off because the vast majority of command encoding then requires no trip into the kernel, avoiding a system call on a very hot path.

### ⑤ Kernel-mode driver (KMD)

The KMD is an OS kernel module and the only component that genuinely touches hardware registers. It handles:

- Physical allocation of device memory and its page table mappings
- Context creation and hardware scheduling
- Notifying the hardware of new work (the doorbell)
- Interrupt handling and error reporting

See [Driver Layer](driver.en.md).

## Why the layering is worth internalizing

The practical value of the layering is **fault isolation**. "It's slow" can originate in entirely different layers:

| Symptom | Most likely layer | Where to look |
| --- | --- | --- |
| "Operator not implemented", or performance suspiciously close to CPU | ① Framework integration | Is the operator registered? Is it silently falling back to CPU? |
| A single operator is slow in isolation | ② Operators & compilation | Did it reach the tuned library implementation? Does the compiled binary match this architecture? |
| Individual operators are fine, but overall utilization is low with visible idle gaps | ③ Runtime | Is a synchronizing call breaking the pipeline? Do copies overlap with compute? |
| Errors mentioning illegal addresses, lost context, or a device falling off the bus | ④⑤ Driver layers | Out-of-bounds access, page mapping, hardware timeout and reset |

## Mapping to other heterogeneous stacks

The layering is broadly the same across vendors; mostly the names differ:

| Concept | CUDA | ROCm | Generic term |
| --- | --- | --- | --- |
| High-level runtime API | CUDA Runtime API | HIP Runtime API | Runtime |
| Low-level device API | CUDA Driver API | HIP Driver API | Driver API |
| Unit of lockstep execution | Warp (32 threads) | Wavefront (usually 64 threads) | Warp |
| Thread group | Block | Workgroup | Thread block |
| Intermediate representation | PTX | Directly to GCN/RDNA ISA | Virtual ISA |
| Basic linear algebra library | cuBLAS | rocBLAS | BLAS library |

So once you can read one vendor's stack, moving to another costs mostly terminology mapping and specific API differences — not a rethink of the structure.

---

Next: [Driver Layer](driver.en.md)
