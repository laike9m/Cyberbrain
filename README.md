# Cyberbrain: Python debugging, **redefined**.

[![support-version](https://img.shields.io/pypi/pyversions/cyberbrain)](https://img.shields.io/pypi/pyversions/cyberbrain)
[![PyPI implementation](https://img.shields.io/pypi/implementation/cyberbrain.svg)](https://pypi.org/project/cyberbrain/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/cyberbrain.svg)](https://pypi.org/project/cyberbrain/)
[!["GitHub Discussions"](https://img.shields.io/badge/%20GitHub-%20Discussions-gray.svg?longCache=true&logo=github&colorB=purple)](https://github.com/laike9m/Cyberbrain/discussions)
[![Discord](https://img.shields.io/discord/751695524628922449.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/5zGS5V5)

Cyberbrain aims to free programmers from debugging. It is the **only** debugger that:

- **Backtraces variable changes**.

- **Persists every state** of program execution.

- **Preserves variables' values** without truncating them.

- Lets you **debug loops** with confidence.

[Read more about these features](docs/Features.md).

Never spend hours stepping through a program, let Cyberbrain tell you what happened.

![](https://user-images.githubusercontent.com/2592205/95418789-1820b480-08ed-11eb-9b3e-61c8cdbf187a.png)

## Install

Cyberbrain consists of a Python library and various editor/IDE integrations. Currently it supports **[VS Code](https://code.visualstudio.com/)** and **[Gitpod](https://www.gitpod.io/)**. See our [plan](https://github.com/laike9m/Cyberbrain/issues/24) on expanding the support.

To install Cyberbrain:

```
pip install cyberbrain
code --install-extension laike9m.cyberbrain
```

You can also install from [PyPI](https://pypi.org/project/cyberbrain/) , [VS Code marketplace](https://marketplace.visualstudio.com/items?itemName=laike9m.cyberbrain) or [Open VSX](https://open-vsx.org/extension/laike9m/cyberbrain) .

**Or, you can try Cyberbrain online:** [![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#snapshot/5c40c10d-8579-4913-a237-4cc1a6b24205)

## How to Use

Suppose you want to trace a function `foo`, just decorate it with `@trace`:

```python
from cyberbrain import trace

@trace  # You can disable tracing with `@trace(disabled=True)`
def foo():
    ...
```

Cyberbrain keeps your workflow unchanged. You run a program (from vscode or command line, both work), call **"Initialize Cyberbrain"** from the [command palette](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette), and a new panel will be opened to visualize how your program executed.

The following gif demonstrates the workflow (click to view the full size image):

![usage](https://user-images.githubusercontent.com/2592205/95430485-ac484700-0900-11eb-814f-41ca84c022f9.gif)

Read our **[documentation](docs/Features.md)** to learn more about Cyberbrain's features and limitations.

❗Note on use❗
- Cyberbrain may conflict with other debuggers. If you set breakpoints and use VSC's debugger, Cyberbrain may not function normally. Generally speaking, **prefer "Run Without Debugging"** (like shown in the gif).
- To run Cyberbrain multiple times with different programs, you need to:     
    1. **Kill the program by Ctrl+C** (Cyberbrain will halt your program from exiting).
    2. **Run another program.**
    3. **Run "Initialize Cyberbrain" again.**

## Status Quo and Milestones

*Updated 2020.10*

Cyberbrain is new and under active development, bugs are expected. If you met any, I appreciate if you can [create an issue](https://github.com/laike9m/Cyberbrain/issues/new). At this point, you should **NOT** use Cyberbrain in production.

Milestones for the project are listed below, which may change over time. Generally speaking, we'll release 1.0 when it reaches  "*Production ready*".

| Milestone        | Description                                                           | Status |
|------------------|-----------------------------------------------------------------------|--------|
| Examples ready   | Cyberbrain works on examples (in the `examples/` folder)      | ✔️ |
| Scripts ready     | Cyberbrain can work with most "scripting" programs                      | WIP |
| Announcement ready | Cyberbrain is ready to be shared on Hacker News and Reddit. **Please don't broadcast Cyberbrain before it reaches this milestone.**                  | Not started    |
| Production ready | Cyberbrain can work with most programs in production                  | Not started    |

Note that v1.0 means Cyberbrain is stable in the features it supports, it does **NOT** mean Cyberbrain is feature complete. Major features planned for each future version are listed below. Again, expect it to change at any time.

| Version | Features                        |
|:-------:|---------------------------------|
| 1.0     | Code & trace interaction ([#7][m1]), API specification |
| 2.0     | Multi-frame tracing             |
| 3.0     | `async` support, remote debugging |
| 4.0     | Fine-grained symbol tracing     |
| 5.0     | Multi-threading support |

[m1]: https://github.com/laike9m/Cyberbrain/issues/7

Visit the project's [kanban](https://github.com/laike9m/Cyberbrain/projects/1) to learn more about the current development schedule.

## How does it compare to other tools?

<details>
<summary>PySnooper</summary>
<a href="https://github.com/cool-RR/PySnooper">PySnooper</a> and Cyberbrain share the same goal of reducing programmers' work while debugging, with a fundamental difference: Cyberbrain traces and shows the sources of each variable change, while PySnooper only logs them. The differences should be pretty obvious after you tried both.
</details>

<details>
<summary>Debug Visualizer</summary>
<a href="https://marketplace.visualstudio.com/items?itemName=hediet.debug-visualizer">Debug visualizer</a> and Cyberbrain have different goals. Debug visualizer visualizes data structures, while Cyberbrain visualizes program execution (but also lets you inspect values).
</details>

## Community

- 💬 **[GitHub Discussions](https://github.com/laike9m/Cyberbrain/discussions)** (for general discussions)
- 🤖 **[Discord](https://discord.gg/5zGS5V5)** (for more instant discussions. I'm happy to chat any time!)
- 🐦 **Twitter [@PyCyberbrain](https://twitter.com/PyCyberbrain)** (for announcement)

## Interested in Contributing?
Get started [here](https://github.com/laike9m/Cyberbrain/blob/master/docs/Development.md).

## Support

I'm almost working full time (besides my regular job) on Cyberbrain. This project is huge, complicated and will last for years, however it will reshape how people think and do debugging. That's why I need **your** support. Let's make it the best Python debugging tool 🤟!

[:heart: Sponsor on GitHub](https://github.com/sponsors/laike9m)

[![](https://www.buymeacoffee.com/assets/img/guidelines/download-assets-1.svg)](https://www.buymeacoffee.com/cyberbrain)

## Contributors ✨

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://www.kawabangga.com"><img src="https://avatars0.githubusercontent.com/u/9675939?v=4" width="100px;" alt=""/><br /><sub><b>laixintao</b></sub></a><br /><a href="https://github.com/laike9m/Cyberbrain/commits?author=laixintao" title="Documentation">📖</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!