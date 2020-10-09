# Cyberbrain: Python debugging, **redefined**.

[![support-version](https://img.shields.io/pypi/pyversions/cyberbrain)](https://img.shields.io/pypi/pyversions/cyberbrain)
[![PyPI implementation](https://img.shields.io/pypi/implementation/cyberbrain.svg)](https://pypi.org/project/cyberbrain/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/cyberbrain.svg)](https://pypi.org/project/cyberbrain/)

Cyberbrain is a Python debugging solution aiming to **free programmers**. It visualizes **program execution** and **how each variable changes**.

Never spend hours stepping through a program, let Cyberbrain tell you.

![](https://user-images.githubusercontent.com/2592205/95418789-1820b480-08ed-11eb-9b3e-61c8cdbf187a.png)

## Install

Cyberbrain consists of a Python library and various editor/IDE integrations. Currently VS Code is the only supported editor, but we have **[plans](https://github.com/laike9m/Cyberbrain/issues/24)** to expand the support.

To install Cyberbrain:

```
pip install cyberbrain
code --install-extension laike9m.cyberbrain
```

Or if you prefer, install from [PyPI](https://pypi.org/project/cyberbrain/) and [VS Code marketplace](https://marketplace.visualstudio.com/items?itemName=laike9m.cyberbrain).

**Or, you can try Cyberbrain directly from your browser:** [![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#snapshot/a473ffc1-a764-4062-953c-5a95e13404c1)

## How to Use

Suppose you want to trace a function called `foo`, just decorate it with `@trace`:

```python
from cyberbrain import trace

@trace  # You can disable tracing with `@trace(disabled=True)`
def foo():
    ...
```

Cyberbrain keeps your workflow unchanged. You run a program (from vscode or command line, both work), call **"Initialize Cyberbrain"** from the [command palette](https://code.visualstudio.com/docs/getstarted/userinterface#_command-palette), and a new panel will be opened to visualize how your program execution.

The following gif demonstrates the workflow (click to view the full size image):

![usage](https://user-images.githubusercontent.com/2592205/95430485-ac484700-0900-11eb-814f-41ca84c022f9.gif)

Features provided:
- Dataflow analysis
- Variable tracing (try hover on any variable, it only highlights **relevant** variables)
- Object inspection (value is logged in the opened devtools console)
- Expect more to come 🤟

Read our [documentation](docs/Features.md) to learn more about Cyberbrain's features.

Note: Cyberbrain may conflict with other debuggers. If you set breakpoints and use VSC's debugger, Cyberbrain may not function normally. Generally speaking, **prefer "Run Without Debugging"** (like shown in the gif).

## Status Quo and Milestones

*Updated 2020.9*

Cyberbrain is new and under active development, bugs are expected. If you met any, I appreciate if you can [create an issue](https://github.com/laike9m/Cyberbrain/issues/new). At this point, you should **NOT** use Cyberbrain in production.

Milestones for the project are listed below, which may change over time. Generally speaking, we'll release 1.0 when it reaches  "*Production ready*".

| Milestone        | Description                                                           | Status |
|------------------|-----------------------------------------------------------------------|--------|
| Examples ready   | Cyberbrain works on examples (in the `examples/` folder)      | WIP    |
| Live demo ready  | Cyberbrain can work with code you write in a live demo, in most cases | Not started    |
| Scripts ready     | Cyberbrain can work with most "scripting" programs                      | Not started    |
| Announcement ready | Cyberbrain is ready to be shared on Hacker News and Reddit. **Please don't broadcast Cyberbrain before it reaches this milestone.**                  | Not started    |
| Production ready | Cyberbrain can work with most programs in production                  | Not started    |

Note that v1.0 means Cyberbrain is stable in the features it supports, it does **NOT** mean Cyberbrain is feature complete. Major features planned for each future version are listed below. Again, expect it to change at any time.

| Version | Features                        |
|:-------:|---------------------------------|
| 1.0     | Code & trace interaction ([#7][m1]), remote debugging, trace dump
| 2.0     | Multi-frame tracing             |
| 3.0     | Fine-grained symbol tracing     |
| 4.0     | Async & multi-threading support |

[m1]: https://github.com/laike9m/Cyberbrain/issues/7

Visit the project's [kanban](https://github.com/laike9m/Cyberbrain/projects/1) to learn more about the current development schedule.

## How does it compare to PySnooper?

Cyberbrain and PySnooper share the same goal of reducing programmers' work while debugging. However they are fundamentally different: Cyberbrain traces and shows the sources of each variable change, while PySnooper only logs them. The differences should be pretty obvious after you tried both.

## Community

Join the [Cyberbrain community Discord](https://discord.gg/2TFYtBh) 💬 and follow us on Twitter [@PyCyberbrain](https://twitter.com/PyCyberbrain) 🐦.

All questions & suggestions & discussions welcomed.

## Interested in Contributing?
Get started [here](https://github.com/laike9m/Cyberbrain/blob/master/docs/Development.md).

## Support

Cyberbrain is a **long-term** project, your support is critical to sustain it. Let's make it the best Python debugging tool 🤟!

[![](https://www.buymeacoffee.com/assets/img/guidelines/download-assets-1.svg)](https://www.buymeacoffee.com/cyberbrain)
