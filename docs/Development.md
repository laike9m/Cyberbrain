<img src="https://img.shields.io/badge/code%20style-black-000000.svg">
<a href="#badge">
    <img alt="code style: prettier" src="https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square"></a>

[![Build Status](https://dev.azure.com/laike9m/laike9m/_apis/build/status/laike9m.Cyberbrain?branchName=master)](https://dev.azure.com/laike9m/laike9m/_build/latest?definitionId=2&branchName=master)


# Development environment setup

## Prerequisites

Make sure you have Python 3.7+ and the latest version of VS Code installed.

## Protocol Buffer
- [Install protoc](https://google.github.io/proto-lens/installing-protoc.html)

## Python
We'll use [Poetry](https://python-poetry.org/) to manage dependencies. Make sure you have set it up correctly.
```
poetry install
```
This will install dev dependencies as well.

## VS Code

Make sure you have **Node.js 12** and npm installed. There's no guarantee that other versions will work.

On Mac, you can `brew install node@12 && brew link --force --overwrite node@12` and add `/usr/local/opt/node@12/bin` to your $PATH.

Then `npm install` inside the `cyberbrain-vsc` folder.

### If you're using PyCharm
Install [Protocol Buffer Editor](https://plugins.jetbrains.com/plugin/14004-protocol-buffer-editor).

# Start making changes

- `make gen_setup`
   
   Generate the latest setup.py, which you can use for [editable install](https://stackoverflow.com/a/35064498/2142577).
    
- `make proto_compile`

   Generate language specific code for proto. Run it after you've changed any `.proto` file.
