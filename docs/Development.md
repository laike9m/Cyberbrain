# Development environment setup

[![](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![](https://img.shields.io/badge/code_style-prettier--eslint-blueviolet)](https://github.com/prettier/prettier-eslint-cli) [![Build Status](https://dev.azure.com/laike9m/laike9m/_apis/build/status/laike9m.Cyberbrain?branchName=master)](https://dev.azure.com/laike9m/laike9m/_build/latest?definitionId=2&branchName=master)

## Prerequisites

Make sure you have Python 3.7+ and the latest version of VS Code installed.

## Install Dependencies

### Protocol Buffer
[Protocol Buffer Compiler Installation](https://grpc.io/docs/protoc-installation/)

### Python
We'll use [Poetry](https://python-poetry.org/) to manage dependencies. Make sure you have set it up correctly.
```
poetry install
```
This will install dev dependencies as well.

### VS Code

Make sure you have **Node.js 12** and npm installed. There's no guarantee that other versions will work.

On Mac, you can `brew install node@12 && brew link --force --overwrite node@12` and add `/usr/local/opt/node@12/bin` (or whatever the binary path is) to your $PATH.

Then `npm install` inside the `cyberbrain-vsc` folder.

### If you're using PyCharm
Install [Protocol Buffer Editor](https://plugins.jetbrains.com/plugin/14004-protocol-buffer-editor).

## Tests

```
# Run Python unit tests.
pytest --assert=plain

# Run end-to-end tests. This will open a new VS Code window.
# Also you need to close the process manully at the end.
cd cyberbrain-vsc && npm run test
```

TODO: complete this part.

## Packaging

```
# Build the Python package.
poetry build

# Build the VS Code package.
cd cyberbrain-vsc && vsce package --no-yarn
```

You can't publish them, but can use them for testing.

## Others

- `make gen_setup`
   
   Generate the latest setup.py, which you can use for [editable install](https://stackoverflow.com/a/35064498/2142577).
    
- `make proto_compile`

   Run it after you've changed any `.proto` file to generate language specific code for protos.
