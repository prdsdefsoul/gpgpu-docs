# GPGPU 软件栈中英双语文档

这是一份面向**异构计算初学者**的 GPGPU 软件栈分层说明文档，中英双语撰写。

## 这份文档想解决什么问题

刚接触 GPU 软件栈的人常见的困惑是：明明只写了一行 `torch.matmul(a, b)`，从这行 Python 到 GPU 上真正跑起来的机器指令之间，究竟隔了多少层？每一层各自负责什么？出问题时应该去哪一层查？

本文档把这条路径拆成五层，逐层说明**它的输入是什么、输出是什么、边界在哪里**：

<div class="grid cards" markdown>

- :material-layers-outline: **[分层总览](stack/overview.md)**

    从一次 `matmul` 调用出发，看清整条调用链的五层结构与各层边界

- :material-chip: **[驱动层](stack/driver.md)**

    内核态驱动与用户态驱动的分工、命令提交、显存管理

- :material-play-circle-outline: **[Runtime 与执行模型](stack/runtime.md)**

    Host-Device 异步模型、流与事件、内存模型、kernel 启动配置

- :material-cog-transfer-outline: **[算子与编译层](stack/compiler.md)**

    源码到目标 ISA 的编译路径、JIT 与 AOT、算子库与 AI 编译器

- :material-language-python: **[框架接入层](stack/framework.md)**

    深度学习框架如何把算子分发到具体设备，新后端接入的典型路径

</div>

## 文档工程说明

这个站点本身也是一次 **Docs-as-Code** 实践，它的构建方式和文档内容同样是本项目想展示的东西：

| 环节 | 做法 |
| --- | --- |
| 内容格式 | 全部内容以 Markdown 存放在 `docs/` 下，纳入 Git 版本管理 |
| 站点生成 | MkDocs + Material 主题 |
| 多语言 | `mkdocs-static-i18n` 插件，采用 `.en.md` 后缀结构，中英文页面一一对应 |
| 构建校验 | `mkdocs build --strict`，死链与配置警告一律视为构建失败 |
| 持续集成 | GitHub Actions：推送到 `main` 即自动构建并部署到 GitHub Pages |
| 术语一致性 | 中英对照[术语表](glossary.md)作为单一事实来源，正文用词以其为准 |

完整的构建与部署链路说明见仓库根目录的 `README.md`。

## 内容边界与免责说明

- 本文档面向**概念理解**，不是任何一家厂商的官方手册。涉及具体 API 行为、参数语义与性能数字时，请以对应厂商的官方文档为准。
- 示例以 CUDA 生态的公开概念为主要参照，因为它的公开资料最完整；ROCm、MUSA 等其他异构计算栈在分层结构上高度相似，文中会指出对应关系。
- 所有代码示例均可在**纯 CPU 环境**下运行 —— 示例用 NumPy 模拟 GPU 的分块与归约思想，目的是把执行模型讲清楚，而不是跑真实的 kernel。

!!! note "关于这个项目"
    作者李家慧，技术文档工程师，长期从事开发者文档与中英双语技术写作。建这个站点的目的有二：一是把 GPGPU 软件栈的分层结构梳理成自己能讲清楚的东西，二是完整走一遍 Docs-as-Code 的工具链 —— 从 Markdown 源文件到 CI 自动部署。
