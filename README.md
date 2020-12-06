# Cyberbrain: Python debugging, **redefined**.

[![support-version](https://img.shields.io/pypi/pyversions/cyberbrain)](https://img.shields.io/pypi/pyversions/cyberbrain)
[![PyPI implementation](https://img.shields.io/pypi/implementation/cyberbrain.svg)](https://pypi.org/project/cyberbrain/)
[![PyPI version shields.io](https://img.shields.io/pypi/v/cyberbrain.svg)](https://pypi.org/project/cyberbrain/)
[!["GitHub Discussions"](https://img.shields.io/badge/%20GitHub-%20Discussions-gray.svg?longCache=true&logo=github&colorB=purple)](https://github.com/laike9m/Cyberbrain/discussions)
[![Discord](https://img.shields.io/discord/751695524628922449.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/5zGS5V5)

Cyberbrain aims to free programmers from debugging. It lets you:

- **Backtraces variable changes**.

- See **every state** of program execution, including **variables' values**

- **Debug loops** with confidence.

Never spend hours stepping through a program, let Cyberbrain tell you what happened.

![](https://user-images.githubusercontent.com/2592205/95418789-1820b480-08ed-11eb-9b3e-61c8cdbf187a.png)

[Read more](docs/Features.md) about existing features, and [roadmaps](#roadmaps) for features to come.

## Install

Cyberbrain consists of a Python library and various editor/IDE integrations. Currently it supports **[VS Code](https://code.visualstudio.com/)**. See our [plan](https://github.com/laike9m/Cyberbrain/issues/24) on expanding the support.

To install Cyberbrain:

```
pip install cyberbrain
code --install-extension laike9m.cyberbrain
```

You can also install from [PyPI](https://pypi.org/project/cyberbrain/), [VS Code marketplace](https://marketplace.visualstudio.com/items?itemName=laike9m.cyberbrain).

## How to Use

Suppose you want to trace a function `foo`, just decorate it with `@trace`:

```python
from cyberbrain import trace

# As of now, you can only have one @trace decorator in the whole program.
# We may change this in version 2.0, see https://github.com/laike9m/Cyberbrain/discussions/73

@trace  # Disable tracing with `@trace(disabled=True)`
def foo():
    ...
```

Cyberbrain keeps your workflow unchanged. You run a program (from vscode or command line, both work), and a new panel will be opened to visualize how your program executed.

The following gif demonstrates the workflow (click to view the full size image):

![usage](https://user-images.githubusercontent.com/2592205/98645630-1d579180-22e7-11eb-8860-3a844f58a252.gif)

Read our **[documentation](docs/Features.md)** to learn more about Cyberbrain's features and limitations.

❗Note on use❗
- Cyberbrain may conflict with other debuggers. If you set breakpoints and use VSC's debugger, Cyberbrain may not function normally. Generally speaking, **prefer "Run Without Debugging"** (like shown in the gif).
- If you have multiple VS Code window opened, the trace graph will always be created in the first one. [#72](https://github.com/laike9m/Cyberbrain/discussions/72) is tracking this issue.
- When having multiple decorators, you should put `@trace` as the innermost one. 
  ```python
  @app.route("/")
  @trace
  def hello_world():
      x = [1, 2, 3]
      return "Hello, World!"
  ```

## Roadmaps

*Updated 2020.11*

Cyberbrain is new and under active development, bugs are expected. If you met any, please [create an issue](https://github.com/laike9m/Cyberbrain/issues/new). At this point, you should **NOT** use Cyberbrain in production. We'll release 1.0 when it's ready for production.

Major features planned for future versions are listed below. It may change over time.

| Version | Features                        |
|:-------:|---------------------------------|
| 1.0     | Code & trace interaction ([#7][m1]), API specification |
| 2.0     | Multi-frame tracing (👉 [I need your feedback for this feature](https://github.com/laike9m/Cyberbrain/discussions/73))   |
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

<details>
<summary>Python Tutor</summary>
<a href="http://pythontutor.com/">Python Tutor</a> is for education purposes, you can't use it to debug your own programs. It's a brilliant tool for its purpose and I do it like it very much.
</details>

## Community

- 💬 **[GitHub Discussions](https://github.com/laike9m/Cyberbrain/discussions)** (for general discussions)
- 🤖 **[Discord](https://discord.gg/5zGS5V5)** (for more instant discussions. I'm happy to chat any time!)
- 🐦 **Twitter [@PyCyberbrain](https://twitter.com/PyCyberbrain)** (for announcements)

## Interested in Contributing?
See the [development guide](https://github.com/laike9m/Cyberbrain/blob/master/docs/Development.md). This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. **Contributions of ANY kind welcome!**

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-10-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Thanks goes to these wonderful contributors ✨

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://www.kawabangga.com"><img src="https://avatars0.githubusercontent.com/u/9675939?v=4" width="30px;" alt=""/><br /><sub><b>laixintao</b></sub></a><br /><a href="https://github.com/laike9m/Cyberbrain/commits?author=laixintao" title="Documentation">📖</a> <a href="#financial-laixintao" title="Financial">💵</a></td>
    <td align="center"><a href="http://yihong.run"><img src="https://avatars1.githubusercontent.com/u/15976103?v=4" width="30px;" alt=""/><br /><sub><b>yihong</b></sub></a><br /><a href="#financial-yihong0618" title="Financial">💵</a> <a href="#ideas-yihong0618" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/dingge2016"><img src="https://avatars1.githubusercontent.com/u/20748513?v=4" width="30px;" alt=""/><br /><sub><b>dingge2016</b></sub></a><br /><a href="#financial-dingge2016" title="Financial">💵</a></td>
    <td align="center"><a href="https://frostming.com"><img src="https://avatars3.githubusercontent.com/u/16336606?v=4" width="30px;" alt=""/><br /><sub><b>Frost Ming</b></sub></a><br /><a href="https://github.com/laike9m/Cyberbrain/issues?q=author%3Afrostming" title="Bug reports">🐛</a> <a href="https://github.com/laike9m/Cyberbrain/commits?author=frostming" title="Documentation">📖</a></td>
    <td align="center"><a href="https://linw1995.com/"><img src="https://avatars0.githubusercontent.com/u/13523027?v=4" width="30px;" alt=""/><br /><sub><b>林玮 (Jade Lin)</b></sub></a><br /><a href="https://github.com/laike9m/Cyberbrain/issues?q=author%3Alinw1995" title="Bug reports">🐛</a> <a href="#ideas-linw1995" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://www.linkedin.com/in/alex-hall-8532079a/"><img src="https://avatars0.githubusercontent.com/u/3627481?v=4" width="30px;" alt=""/><br /><sub><b>Alex Hall</b></sub></a><br /><a href="#ideas-alexmojaki" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/inkuang"><img src="https://avatars1.githubusercontent.com/u/38498747?v=4" width="30px;" alt=""/><br /><sub><b>inkuang</b></sub></a><br /><a href="https://github.com/laike9m/Cyberbrain/issues?q=author%3Ainkuang" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/no1xsyzy"><img src="https://avatars0.githubusercontent.com/u/7346170?v=4" width="30px;" alt=""/><br /><sub><b>Siyuan Xu</b></sub></a><br /><a href="https://github.com/laike9m/Cyberbrain/issues?q=author%3Ano1xsyzy" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://ram.rachum.com"><img src="https://avatars1.githubusercontent.com/u/56778?v=4" width="30px;" alt=""/><br /><sub><b>Ram Rachum</b></sub></a><br /><a href="#ideas-cool-RR" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/poltronSuperstar"><img src="https://avatars1.githubusercontent.com/u/22001372?v=4" width="30px;" alt=""/><br /><sub><b>foo bar</b></sub></a><br /><a href="#financial-poltronSuperstar" title="Financial">💵</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->


## Support

I'm almost working full time (besides my regular job) on Cyberbrain. This project is huge, complicated and will last for years, however it will reshape how people think and do debugging. That's why I need **your** support. Let's make it the best Python debugging tool 🤟!

[:heart: Sponsor on GitHub](https://github.com/sponsors/laike9m)

[![](https://www.buymeacoffee.com/assets/img/guidelines/download-assets-1.svg)](https://www.buymeacoffee.com/cyberbrain)
