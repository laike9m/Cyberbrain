# Development environment setup

[![](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![](https://img.shields.io/badge/code_style-prettier--eslint-blueviolet)](https://github.com/prettier/prettier-eslint-cli) [![Build Status](https://dev.azure.com/laike9m/laike9m/_apis/build/status/laike9m.Cyberbrain?branchName=master)](https://dev.azure.com/laike9m/laike9m/_build/latest?definitionId=1&branchName=master)

## Prerequisites

Make sure you have Python 3.7+ and the latest version of VS Code installed.

**Important: During development, make sure the Cyberbrain Python library and VS Code extension are NOT installed.**

## Install Dependencies

- Install dependecies for the Python library
  
   We'll use [Poetry](https://python-poetry.org/) to manage dependencies. Assuming you've installed Poetry and set it up correctly, run:
   ```
   poetry install
   ```

- VS Code

   Make sure you have **Node.js 12** and npm installed. There's no guarantee that other versions will work.

   On Mac, you can `brew install node@12 && brew link --force --overwrite node@12` and add `/usr/local/opt/node@12/bin` (or whatever the binary path is) to your `$PATH`.

   Then `npm install` inside the `cyberbrain-vsc` folder.

## Run Tests

After installing dependencies, you always want to run the tests to make sure everything works correctly.

### Run Python Tests

In the project root directory.

```
pytest --assert=plain
```

### Run JavaScript Tests

```
cd cyberbrain-vsc && npm run unittest
```

### Run End-to-End Tests in VS Code

There are two ways to run the e2e tests.

- From command line

   ```
   cd cyberbrain-vsc && npm run test
   ```

   This will open a new VS Code window and run the tests

- From VS Code's UI

  1. **Make sure `cyberbrain-vsc` is opened as a top-level folder in VS Code**. If you opened the root directory `Cyberbrain`, though `cyberbrain-vsc` is included, it will NOT work.

  2. You should then see the two options ("Run Extension" and "Extension Tests") show up in the Run view. This means that VS Code has recognized the extension we're developing.

      <img src="https://user-images.githubusercontent.com/2592205/106569059-f32dfe00-64e8-11eb-853f-2d0e499683e4.png" height=400px>

  3. Choose "Extension Tests", and click the "run" icon ▶
  4. A new VS Code window will pop up and run the tests.


## Packaging

```
# Build the Python package.
poetry build

# Build the VS Code package.
cd cyberbrain-vsc && vsce package --no-yarn
```

Normally you don't need to do packaging, because I'm the only one that can publish new versions.

## Others

- `make gen_setup`
   
   Generate the latest setup.py, which you can use for [editable install](https://stackoverflow.com/a/35064498/2142577). Only use it if you know what you're doing.
