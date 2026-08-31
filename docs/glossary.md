# 术语表

中英对照术语表，本站点正文用词以此表为准。

这张表在本项目里的定位是**单一事实来源（single source of truth）**：中英文页面在翻译时，同一概念必须使用表中的固定译法，不允许在不同页面出现同义异译。这是技术文档多语言工程里最基础、也最容易失守的一条规范。

## 软件栈与分层

| English | 中文 | 说明 |
| --- | --- | --- |
| GPGPU (General-Purpose computing on GPU) | 通用图形处理器计算 | 用 GPU 做非图形的通用计算 |
| Software stack | 软件栈 | 从框架到驱动的完整层次结构 |
| Kernel-Mode Driver (KMD) | 内核态驱动 | 运行在操作系统内核中的驱动部分 |
| User-Mode Driver (UMD) | 用户态驱动 | 运行在应用进程地址空间中的驱动部分 |
| Runtime | 运行时 | Host 侧操作设备的编程接口层；本文档中保留英文 |
| Driver API | 驱动 API | 底层设备接口，仍属用户态，不是内核驱动本身 |
| Heterogeneous computing | 异构计算 | 在不同架构的处理器上协同计算 |
| Doorbell | doorbell | 用户态驱动向一个内存映射寄存器写值，通知硬件有新命令待执行。是一次内存写而非系统调用，因此提交路径很轻 |

## 执行模型

| English | 中文 | 说明 |
| --- | --- | --- |
| Host | 主机端 | 指 CPU 侧；本文档中多数场合保留英文 |
| Device | 设备端 | 指 GPU 侧；本文档中多数场合保留英文 |
| Kernel | 核函数 | 在设备上执行的函数；本文档中保留英文以免与"内核态"混淆 |
| Grid | 网格 | 一次 kernel 启动的全部线程块 |
| Block / Thread block | 线程块 | 被整体调度到同一计算单元的一组线程 |
| Warp | 线程束 | CUDA 中的硬件调度粒度，通常为 32 线程 |
| Wavefront | 线程束 | ROCm 中的对应概念，通常为 64 线程 |
| Thread | 线程 | 最小执行单元 |
| Branch divergence | 分支发散 | 同一线程束内线程走向不同分支，导致串行执行 |
| Occupancy | 占用率 | 计算单元上实际驻留的线程束数与理论上限之比 |
| Stream / Queue | 流 | 按序执行的任务队列 |
| Event | 事件 | 插入流中的标记点，用于跨流同步与计时 |
| Synchronization | 同步 | 等待先前提交的操作完成 |
| Asynchronous | 异步 | 调用返回不代表操作已完成 |

## 内存

| English | 中文 | 说明 |
| --- | --- | --- |
| Device memory | 设备内存 / 显存 | GPU 上的内存 |
| Pageable memory | 可分页内存 | 普通 Host 内存，可被操作系统换出 |
| Pinned / Page-locked memory | 页锁定内存 | 不可换出的 Host 内存，支持真正的异步拷贝 |
| Unified memory | 统一内存 | Host 与 Device 共用同一指针，由系统按需迁移 |
| Shared memory | 共享内存 | 线程块内共享的片上高速内存 |
| Global memory | 全局内存 | 设备上所有线程可见的主显存 |
| Caching allocator | 缓存分配器 | 框架在设备内存之上自建的内存池 |
| Memory coalescing | 访存合并 | 同一线程束的访存被合并成少数几次事务 |
| Page table | 页表 | 虚拟地址到物理地址的映射表 |

## 编译

| English | 中文 | 说明 |
| --- | --- | --- |
| Intermediate Representation (IR) | 中间表示 | 编译过程中的中间形式 |
| PTX (Parallel Thread Execution) | PTX | CUDA 的虚拟 ISA，跨架构稳定；保留英文 |
| SASS | SASS | CUDA 的真实 ISA，与具体架构绑定；保留英文 |
| ISA (Instruction Set Architecture) | 指令集架构 | |
| Virtual ISA | 虚拟指令集 | 不直接对应硬件的稳定抽象层 |
| fatbinary | fatbinary | 打包多架构代码的二进制格式；保留英文 |
| AOT (Ahead-Of-Time) compilation | 提前编译 | 构建时完成编译 |
| JIT (Just-In-Time) compilation | 即时编译 | 运行时完成编译 |
| Lowering | 下降 / 逐级下降 | 从高层 IR 转换到更贴近硬件的低层 IR |
| Dialect | 方言 | MLIR 中一组自定义操作与类型的集合 |
| Operator fusion | 算子融合 | 把多个算子合并为一个 kernel |
| Tiling | 分块 | 把大循环切成适配缓存或共享内存的小块 |
| Vectorization | 向量化 | 用宽指令一次处理多个元素 |
| Auto-tuning | 自动调优 | 在调度空间中自动搜索高性能实现 |
| Schedule | 调度 | 计算的循环排布方式，与计算语义相分离 |

## 框架接入

| English | 中文 | 说明 |
| --- | --- | --- |
| Operator / Op | 算子 | 计算图中的一个计算节点 |
| Dispatcher | 分发器 | 根据设备与数据类型选择算子实现的机制 |
| Backend | 后端 | 某一设备上的算子实现集合 |
| In-tree backend | 树内后端 | 代码合入框架主仓库的后端 |
| Out-of-tree backend | 树外后端 | 以独立仓库和安装包形式存在的后端 |
| Operator coverage | 算子覆盖度 | 已在目标设备上实现的算子比例 |
| Fallback | 回落 | 目标设备无实现时改由 CPU 执行 |
| Computation graph | 计算图 | 算子及其数据依赖构成的有向图 |
| Mixed precision | 混合精度 | 训练中混用 fp32 与 fp16 / bf16 |

## 译法约定

除逐条对照之外，本站点遵循以下几条通用约定：

1. **首次出现给全称加缩写，此后只用缩写。** 例如：内核态驱动（Kernel-Mode Driver, KMD），之后统一写 KMD。
2. **已在中文技术社区形成稳定英文用法的词保留英文。** 例如 kernel、warp、stream、PTX。强行翻译反而增加读者的理解成本。
3. **同一概念在中英文页面必须严格对应。** 中文页写"线程束"，英文页对应位置必须是 warp / wavefront，不能出现只在一侧存在的概念。
4. **区分容易混淆的同形词。** "内核"在本文档中一律指操作系统内核（kernel-mode），设备上执行的函数一律写作 kernel 不译，避免"内核函数"与"内核态"混为一谈。

---

上一页：[分块归约示例](examples/tiled-reduction.md) ｜ 返回：[首页](index.md)
