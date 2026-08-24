# GPGPU Software Stack — Bilingual Documentation

A layered walkthrough of the GPGPU software stack, written for people **new to heterogeneous computing** and published in both Chinese and English.

## What this documentation is for

A question that comes up constantly for newcomers: you write a single line of `torch.matmul(a, b)` — how many layers sit between that line of Python and the machine instructions that actually run on the GPU? What does each layer own? And when something breaks, which layer should you look at?

This documentation splits that path into five layers and, for each one, answers the same three questions: **what goes in, what comes out, and where the boundary lies**.

<div class="grid cards" markdown>

- :material-layers-outline: **[Layer Overview](stack/overview.en.md)**

    Starting from one `matmul` call, the five layers of the call chain and the boundaries between them

- :material-chip: **[Driver Layer](stack/driver.en.md)**

    How kernel-mode and user-mode drivers divide the work: command submission and memory management

- :material-play-circle-outline: **[Runtime and Execution Model](stack/runtime.en.md)**

    The host–device asynchronous model, streams and events, the memory model, and kernel launch configuration

- :material-cog-transfer-outline: **[Operators and Compilation](stack/compiler.en.md)**

    From source to target ISA: JIT versus AOT, operator libraries, and AI compilers

- :material-language-python: **[Framework Integration](stack/framework.en.md)**

    How deep learning frameworks dispatch operators to a device, and what it takes to bring up a new backend

</div>

## How this site is built

This site is itself an exercise in **Docs-as-Code**. How it is built is as much a part of the project as what it says:

| Aspect | Approach |
| --- | --- |
| Source format | All content lives as Markdown under `docs/`, versioned in Git |
| Site generation | MkDocs with the Material theme |
| Localization | `mkdocs-static-i18n` using the `.en.md` suffix structure, with one-to-one page parity |
| Build validation | `mkdocs build --strict` — broken links and configuration warnings fail the build |
| Continuous integration | GitHub Actions builds and deploys to GitHub Pages on every push to `main` |
| Terminology | The bilingual [glossary](glossary.en.md) is the single source of truth for wording |

The full build and deployment pipeline is documented in the repository `README.md`.

## Scope and disclaimer

- This documentation aims at **conceptual understanding**. It is not any vendor's official manual. For exact API behaviour, parameter semantics, or performance figures, defer to the vendor documentation.
- Examples draw primarily on publicly documented CUDA concepts, simply because that ecosystem has the most complete public material. ROCm, MUSA, and other heterogeneous stacks are structurally very similar; corresponding terms are noted where they differ.
- Every code sample runs on a **CPU-only machine**. The examples use NumPy to model GPU tiling and reduction so that the execution model is easy to follow — they do not launch real kernels.

!!! note "About this project"
    Written by Jiahui Li, a technical writer working on developer documentation and bilingual technical writing. This site has two purposes: to work the layering of the GPGPU software stack into something explainable, and to walk the full Docs-as-Code toolchain end to end — from Markdown source to automated deployment.
