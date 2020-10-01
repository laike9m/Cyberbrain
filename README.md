# Cyberbrain: Python debugging, **redefined**.

Cyberbrain is a Python debugging solution aiming to **free programmers**. It visualizes **program execution** and **how each variable changes**. Never spend hours stepping through the program, let Cyberbrain tell you.

![](https://github.com/laike9m/Cyberbrain/docs/images/p1.png)

## Install

Cyberbrain consists of a Python library and various editor/IDE integrations. Currently VS Code is the only supported editor, but we have **[plans](https://github.com/laike9m/Cyberbrain/issues/24)** to expand the support.

To install Cyberbrain:

```
pip install cyberbrain
code --install-extension laike9m.cyberbrain
```

Or if you prefer, install from [PyPI](https://pypi.org/project/cyberbrain/) and [VS Code marketplace](https://marketplace.visualstudio.com/items?itemName=laike9m.cyberbrain).

## How to Use

Cyberbrain keeps your workflow unchanged. You run a program 

![](https://github.com/laike9m/Cyberbrain/docs/images/usage.gif)

Note: Cyberbrain may conflict with other debuggers. If you set breakpoints and use VSC's debugger, Cyberbrain may not function normally. Generally speaking, **prefer "Run Without Debugging"** (Like shown in the gif).


## Status Quo and Milestones

*Updated 2020.9*

Cyberbrain is still under active development. Milestones for the project are listed below, which may change over time. Generally speaking, we'll release 1.0 when it reaches  "*Production ready*".

| Milestone        | Description                                                           | Status |
|------------------|-----------------------------------------------------------------------|--------|
| Examples ready   | Cyberbrain works on certain examples (in the `examples/` folder)      | WIP    |
| Live demo ready  | Cyberbrain can work with code you write in a live demo, in most cases | Not started    |
| Scripts ready     | Cyberbrain can work with most "scripting" programs                      | Not started    |
| Announcement ready | Cyberbrain is ready to be shared on Hacker News and Reddit. **Please don't broadcast Cyberbrain before it reaches this milestone.**                  | Not started    |
| Production ready | Cyberbrain can work with most programs in production                  | Not started    |

Note that v1.0 means Cyberbrain is stable in the features it supports, it does **NOT** mean Cyberbrain is feature complete. Major features planned for each version are listed below. Again, expect it to change at any time.

| Version | Features                        |
|---------|---------------------------------|
| 1.0     | Mutual interaction between source code and the trace graph ([#7][m1])  |
| 2.0     | Multi-frame tracing             |
| 3.0     | Fine-grained symbol tracing     |
| 4.0     | Async & multi-threading support |

[m1]: https://github.com/laike9m/Cyberbrain/issues/7

## Community

Join the [Cyberbrain community Discord](https://discord.gg/2TFYtBh) 💬

All questions & suggestions & discussions welcomed.

## Interested in Contributing?
Get started [here](https://github.com/laike9m/Cyberbrain/blob/master/docs/Development.md).

## Support

Cyberbrain is a **long-term** project, your support is critical to sustain it. Let's make it the best Python debugging tool 🤟!

[![](https://www.buymeacoffee.com/assets/img/guidelines/download-assets-1.svg)](https://www.buymeacoffee.com/cyberbrain)
