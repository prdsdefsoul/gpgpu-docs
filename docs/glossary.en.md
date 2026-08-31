# Glossary

A bilingual glossary. Wording throughout this site follows this table.

Within this project the glossary is the **single source of truth**: when a page is translated, a concept must use the fixed rendering given here. The same concept may never appear under two different translations on two different pages. This is the most basic — and most frequently violated — rule in multilingual documentation work.

## Stack and layering

| English | 中文 | Notes |
| --- | --- | --- |
| GPGPU (General-Purpose computing on GPU) | 通用图形处理器计算 | Non-graphics general computation on a GPU |
| Software stack | 软件栈 | The full layering from framework down to driver |
| Kernel-Mode Driver (KMD) | 内核态驱动 | The driver component running inside the OS kernel |
| User-Mode Driver (UMD) | 用户态驱动 | The driver component running in the application address space |
| Runtime | 运行时 | The host-side programming interface to the device; kept in English on this site |
| Driver API | 驱动 API | The lower-level device interface — still user-mode, not the kernel driver itself |
| Heterogeneous computing | 异构计算 | Computing across processors of differing architectures |
| Doorbell | doorbell | A memory-mapped register the UMD writes to signal the hardware that new commands are queued. A memory write rather than a system call, which keeps the submission path cheap |

## Execution model

| English | 中文 | Notes |
| --- | --- | --- |
| Host | 主机端 | The CPU side; usually kept in English on this site |
| Device | 设备端 | The GPU side; usually kept in English on this site |
| Kernel | 核函数 | A function executing on the device; kept in English to avoid collision with "kernel mode" |
| Grid | 网格 | All thread blocks in one kernel launch |
| Block / Thread block | 线程块 | A group of threads scheduled together onto one compute unit |
| Warp | 线程束 | The hardware scheduling granularity in CUDA, typically 32 threads |
| Wavefront | 线程束 | The ROCm equivalent, typically 64 threads |
| Thread | 线程 | The smallest unit of execution |
| Branch divergence | 分支发散 | Threads in one warp taking different branches, forcing serial execution |
| Occupancy | 占用率 | Resident warps per compute unit as a fraction of the hardware maximum |
| Stream / Queue | 流 | An in-order queue of device tasks |
| Event | 事件 | A marker inserted into a stream, used for cross-stream sync and timing |
| Synchronization | 同步 | Waiting for previously submitted work to complete |
| Asynchronous | 异步 | Return from the call does not imply the operation has completed |

## Memory

| English | 中文 | Notes |
| --- | --- | --- |
| Device memory | 设备内存 / 显存 | Memory on the GPU |
| Pageable memory | 可分页内存 | Ordinary host memory, which the OS may swap out |
| Pinned / Page-locked memory | 页锁定内存 | Host memory that cannot be swapped out, enabling truly asynchronous copies |
| Unified memory | 统一内存 | A single pointer valid on host and device, with pages migrated on demand |
| Shared memory | 共享内存 | Fast on-chip memory shared within a thread block |
| Global memory | 全局内存 | Main device memory, visible to all threads |
| Caching allocator | 缓存分配器 | A memory pool a framework maintains on top of device memory |
| Memory coalescing | 访存合并 | Merging the accesses of one warp into a few memory transactions |
| Page table | 页表 | The virtual-to-physical address mapping |

## Compilation

| English | 中文 | Notes |
| --- | --- | --- |
| Intermediate Representation (IR) | 中间表示 | An intermediate form used during compilation |
| PTX (Parallel Thread Execution) | PTX | CUDA's virtual ISA, stable across architectures; kept in English |
| SASS | SASS | CUDA's real ISA, bound to a specific architecture; kept in English |
| ISA (Instruction Set Architecture) | 指令集架构 | |
| Virtual ISA | 虚拟指令集 | A stable abstraction that does not map directly to hardware |
| fatbinary | fatbinary | A binary format packaging code for multiple architectures; kept in English |
| AOT (Ahead-Of-Time) compilation | 提前编译 | Compilation performed at build time |
| JIT (Just-In-Time) compilation | 即时编译 | Compilation performed at run time |
| Lowering | 下降 / 逐级下降 | Transforming a higher-level IR into one closer to the hardware |
| Dialect | 方言 | A set of custom operations and types in MLIR |
| Operator fusion | 算子融合 | Merging several operators into a single kernel |
| Tiling | 分块 | Splitting a large loop into blocks that fit cache or shared memory |
| Vectorization | 向量化 | Processing several elements per instruction |
| Auto-tuning | 自动调优 | Automatically searching a schedule space for a fast implementation |
| Schedule | 调度 | How a computation's loops are arranged, kept separate from its semantics |

## Framework integration

| English | 中文 | Notes |
| --- | --- | --- |
| Operator / Op | 算子 | A single computation node in a graph |
| Dispatcher | 分发器 | The mechanism selecting an operator implementation by device and dtype |
| Backend | 后端 | The set of operator implementations for one device |
| In-tree backend | 树内后端 | A backend merged into the framework's main repository |
| Out-of-tree backend | 树外后端 | A backend shipped as a separate repository and package |
| Operator coverage | 算子覆盖度 | The share of operators implemented on the target device |
| Fallback | 回落 | Executing on CPU when the target device has no implementation |
| Computation graph | 计算图 | The directed graph of operators and their data dependencies |
| Mixed precision | 混合精度 | Training with fp32 alongside fp16 or bf16 |

## Translation conventions

Beyond the entries above, this site follows a few general rules:

1. **Spell out on first use, then abbreviate.** For example: Kernel-Mode Driver (KMD) on first mention, KMD thereafter.
2. **Keep terms in English where the Chinese technical community already uses them that way** — kernel, warp, stream, PTX. Forcing a translation raises the reader's cost rather than lowering it.
3. **Concepts must correspond one-to-one across languages.** Where the Chinese page says 线程束, the English page says warp or wavefront in the same position. Neither side may carry a concept the other lacks.
4. **Disambiguate collisions explicitly.** On this site "内核" always means the operating system kernel; a device function is always written as *kernel*, untranslated, so that 内核函数 and 内核态 never blur together.

---

Previous: [Tiled Reduction](examples/tiled-reduction.en.md) ｜ Back to: [Home](index.en.md)
