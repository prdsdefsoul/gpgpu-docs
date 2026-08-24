# Driver Layer

The driver layer sits at the bottom of the stack and is the only part that touches hardware registers directly. It is normally split into a **kernel-mode driver (KMD)** and a **user-mode driver (UMD)**.

## Why the split exists

Launching a kernel means encoding the kernel address, arguments, and grid/block configuration into commands the hardware can parse. If every launch had to trap into the kernel, system call overhead alone would dominate any workload built from many small kernels.

So the division of labour in a modern GPU driver is:

- **The UMD does almost everything, in user space** — command encoding, argument packing, state tracking. None of it requires privilege.
- **The KMD does only what the kernel must do** — physical memory allocation, page table mapping, hardware scheduling, interrupt handling.

The cost: the UMD shares an address space with the application, so a fault there takes the application down; a fault in the KMD affects the whole system. This is also why an out-of-bounds device write usually surfaces as an in-process "illegal address" error, while a hardware timeout triggers a global device reset.

## Kernel-mode driver (KMD)

### Memory management

The KMD owns the allocator for device physical memory and establishes the mapping from **device virtual addresses to physical addresses**. A GPU has its own MMU and page tables, entirely separate from those on the CPU side.

An allocation request such as `cudaMalloc` reaches the KMD roughly as:

1. Find a free, suitably aligned region in device physical memory
2. Create a mapping for it in that process's GPU page tables
3. Return the device virtual address to the caller

Grasping this explains a common gotcha: **a device pointer cannot be dereferenced on the host**. It is an address in the GPU's page tables, and the CPU's MMU knows nothing about it.

### Contexts and isolation

Every process using the GPU gets its own **context**, with its own page tables and its own command queue state. The context is the hardware-level unit of isolation — one process cannot reach another's device memory through a device pointer.

Context switches are not free. A single GPU shared between several processes generally performs worse than the same total work running in one process across several streams, and this is why.

### Command submission and the doorbell

After the UMD writes commands into a shared **ring buffer**, it must tell the hardware there is new work. That notification is usually called a **doorbell** — the UMD writes to a specific memory-mapped register, and the hardware begins fetching.

The doorbell is a memory write, not a system call, which is what keeps the submission path cheap.

### Interrupts and error reporting

Kernel completion, copy completion, and errors all reach the KMD as interrupts, which it then reports upward. That path determines two things:

- **Errors from asynchronous APIs are reported late.** An illegal access inside a kernel may not surface until several API calls later. This is the single easiest trap to fall into when debugging GPU errors.
- Hardware that stops responding triggers **timeout detection and reset**, which the application sees as the device disappearing.

## User-mode driver (UMD)

The UMD is a shared library loaded into the application process by the runtime. Its main jobs:

| Job | Description |
| --- | --- |
| Command encoding | Encoding kernel launches, memory copies, and so on into the hardware command format |
| Queue management | Maintaining the ring buffer write pointer and ringing the doorbell at the right moments |
| Binary loading | Parsing compiled artifacts and selecting the right code for the current architecture (see [Operators and Compilation](compiler.en.md)) |
| Talking to the KMD | Requesting privileged operations such as memory allocation and context creation via `ioctl` and friends |

## Driver API versus Runtime API

The CUDA ecosystem exposes two host-side interfaces, and this is where newcomers most often get confused:

| | Driver API | Runtime API |
| --- | --- | --- |
| Typical symbols | `cuCtxCreate`, `cuModuleLoad`, `cuLaunchKernel` | `cudaMalloc`, `cudaMemcpy`, `<<<...>>>` |
| Context handling | Created and managed explicitly | Created implicitly, bound per thread |
| Module loading | Explicitly loads cubin / PTX modules | Linked at compile time, loaded automatically |
| Typical use | Runtimes and JIT frameworks needing fine control | Ordinary application code |

Note: **the "Driver API" is still a user-mode C interface.** It is not the kernel driver. The real KMD is invisible to applications, which can only reach it indirectly through these two APIs. The naming invites misreading, and it is worth calling out explicitly in documentation.

## A documentation perspective on this layer

The driver layer is the hardest to document and the easiest to get wrong, because its behaviour depends heavily on implementation details and public material is scarce. A few practical rules:

- **Separate the interface contract from the current implementation.** "Commands execute in submission order" is a contract and belongs in the documentation. "The current implementation uses 4 KB pages" is an implementation detail that becomes wrong in the next release.
- **Error codes need a diagnostic path, not a restatement.** "Illegal address access" carries no information on its own. What helps is telling the reader that the error may be reported late and that re-running synchronously will locate the real fault site.
- **Say explicitly which behaviours are undefined.** Undefined behaviour left undocumented becomes behaviour users depend on, and eventually a compatibility obligation.

---

Previous: [Layer Overview](overview.en.md) ｜ Next: [Runtime and Execution Model](runtime.en.md)
