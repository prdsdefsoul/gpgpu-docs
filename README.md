# GPGPU 软件栈中英双语文档

[![Build and Deploy Docs](https://github.com/prdsdefsoul/gpgpu-docs/actions/workflows/deploy.yml/badge.svg)](https://github.com/prdsdefsoul/gpgpu-docs/actions/workflows/deploy.yml)

一份面向异构计算初学者的 GPGPU 软件栈分层文档，中英双语，用 **Docs-as-Code** 方式构建与发布。

**在线阅读**：https://prdsdefsoul.github.io/gpgpu-docs/

## 这个项目是什么

两件事各占一半：

1. **内容** —— 把从 `torch.matmul(a, b)` 到 GPU 机器指令之间的五层结构讲清楚：框架接入层、算子与编译层、Runtime、用户态驱动、内核态驱动。每一层说明它的输入、输出和边界，并给出"出问题时该查哪一层"的对照表。
2. **文档工程** —— 完整走一遍 Docs-as-Code 链路：Markdown 源文件纳入 Git、MkDocs 生成静态站点、`mkdocs-static-i18n` 管理中英双语、GitHub Actions 做 CI 构建与自动部署、`--strict` 模式把死链变成构建失败。

## 目录结构

```
gpgpu-docs/
├── docs/                          # 全部文档源文件（Markdown）
│   ├── index.md / index.en.md     # 首页（中文 / 英文）
│   ├── stack/                     # 软件栈分层
│   │   ├── overview.md            #   分层总览
│   │   ├── driver.md              #   驱动层
│   │   ├── runtime.md             #   Runtime 与执行模型
│   │   ├── compiler.md            #   算子与编译层
│   │   └── framework.md           #   框架接入层
│   ├── examples/
│   │   └── tiled-reduction.md     # 示例验证：分块归约
│   └── glossary.md                # 中英对照术语表
├── examples/
│   └── tiled_reduction.py         # 可运行的示例脚本（纯 CPU，不需要 GPU）
├── .github/workflows/deploy.yml   # CI：构建、校验、部署
├── mkdocs.yml                     # 站点配置
└── requirements.txt               # 依赖锁定
```

每个 `xxx.md` 都有一个对应的 `xxx.en.md`，这是 `mkdocs-static-i18n` 的 **suffix 结构**：中文是默认语言，构建到站点根目录；英文构建到 `/en/` 子路径。

## 本地开发

```bash
# 1. 建虚拟环境并安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. 起本地服务，改文件即自动刷新，默认 http://127.0.0.1:8000
mkdocs serve

# 3. 严格模式构建（提交前跑一遍，等价于 CI 里的检查）
mkdocs build --strict
```

`--strict` 会把死链、nav 中引用了不存在的文件等警告升级为错误。本地跑通了，CI 就不会因为这类问题挂掉。

## 运行示例

```bash
python3 examples/tiled_reduction.py
```

示例用 NumPy 模拟 GPU 的分块归约，演示 grid / block 划分与浮点归约的精度差异。**不需要 GPU**，纯 CPU 环境即可运行。这个脚本也在 CI 里跑 —— 文档中引用的示例必须真的能跑通，否则不给发布。

## CI/CD 流水线

`.github/workflows/deploy.yml` 定义了两个作业：

```
push 到 main / 对 main 提 PR
        │
        ▼
┌─────────────────────────────────┐
│ build                           │
│  1. 检出代码                    │
│  2. 装 Python 3.12（带 pip 缓存）│
│  3. 装依赖                      │
│  4. 跑示例脚本 ← 质量门禁       │
│  5. mkdocs build --strict ← 门禁│
│  6. 上传构建产物（仅 push）     │
└──────────────┬──────────────────┘
               │ build 成功
               ▼
┌─────────────────────────────────┐
│ deploy（仅 push 到 main）       │
│  部署产物到 GitHub Pages        │
└─────────────────────────────────┘
```

设计上的两个取舍：

- **PR 只构建不部署。** 让死链和跑不通的示例在合并前就被拦下来，同时避免未评审的内容进入线上站点。
- **用 Pages artifact 而不是 gh-pages 分支。** 构建产物通过 `upload-pages-artifact` / `deploy-pages` 直接交给 Pages，不需要往仓库里再推一个分支，仓库历史干净，也不必给 CI 配置额外的写权限。

### 首次启用 Pages

仓库 **Settings → Pages → Build and deployment → Source** 选 **GitHub Actions**（不是 "Deploy from a branch"）。这一步只需做一次。

## 内容边界

- 面向**概念理解**，不是任何厂商的官方手册。具体 API 行为、参数语义和性能数字请以厂商官方文档为准。
- 主要参照 CUDA 生态的公开概念（公开资料最完整），并在文中标注 ROCm 等其他栈的对应术语。
- 所有代码示例都能在纯 CPU 环境运行，目的是讲清执行模型，不是跑真实 kernel。

## 关于

作者：李家慧，技术文档工程师。建这个站点的目的是把 GPGPU 软件栈梳理成自己能讲清楚的东西，同时完整实践一遍 Docs-as-Code 工具链。

## 许可

内容采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，代码采用 MIT。
