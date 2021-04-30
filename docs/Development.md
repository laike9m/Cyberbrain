# Development environment setup

[![](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![](https://img.shields.io/badge/code_style-prettier--eslint-blueviolet)](https://github.com/prettier/prettier-eslint-cli) [![Build Status](https://dev.azure.com/laike9m/laike9m/_apis/build/status/laike9m.Cyberbrain?branchName=master)](https://dev.azure.com/laike9m/laike9m/_build/latest?definitionId=1&branchName=master)

## Prerequisites

Make sure you have Python>=3.7 and the latest version of VS Code installed.

**Important: During development, make sure the Cyberbrain Python library and VS Code extension are NOT installed.**

## Install Dependencies

### Install dependencies for the Python library
  
   We'll use [Poetry](https://python-poetry.org/) to manage dependencies. Assuming you've installed Poetry and set it up correctly, run:
   ```
   poetry install
   ```

### [Install the Python package **being developed**](#editable-install)
  
  To be able to test the changes we made locally, we have to install it from our computer directly. We use [editable install](https://pip.pypa.io/en/stable/cli/pip_install/#install-editable) to achieve this:

  ```bash
  # Make sure you're in the root folder, aka "Cyberbrain"
  pip install -e .
  
  # The following output means the installation has succeeded:
  #   Installing collected packages: cyberbrain
  #   Running setup.py develop for cyberbrain
  #   Successfully installed cyberbrain
  ```
  
  In case you have multiple versions of Python installed, make sure you chose the Python version that you intend to use in VS Code.

  ![image](https://user-images.githubusercontent.com/2592205/116657768-cf415380-a943-11eb-87db-9fa87eeddff5.png)

### Install dependencies for VS Code

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

- From VS Code's UI (recommended)

  1. **Make sure `cyberbrain-vsc` is opened as a top-level folder in VS Code**. If you opened the root directory `Cyberbrain`, though `cyberbrain-vsc` is included, it will NOT work.

  2. You should then see the two options ("Run Extension" and "Extension Tests") show up in the Run view. This means that VS Code has recognized the extension we're developing.

      <img src="https://user-images.githubusercontent.com/2592205/106569059-f32dfe00-64e8-11eb-853f-2d0e499683e4.png" height=400px>

  3. Choose "Extension Tests", and click the "run" icon ▶
  4. A new VS Code window will pop up and run the tests.
    
- From command line

   ```
   cd cyberbrain-vsc && npm test
   ```

  This will open a new VS Code window and run the tests.
  
  Note that if you're using the latest version of VS Code, the test runner will complain that a VS Code window has already been opened. You can download and use the [Insiders version](https://code.visualstudio.com/insiders/) for development to solve this issue.
  
## Run the extension under development

Click "Run Extension"

<img src="https://user-images.githubusercontent.com/2592205/106569059-f32dfe00-64e8-11eb-853f-2d0e499683e4.png" height=400px>

Then open a file under the [`examples/`](https://github.com/laike9m/Cyberbrain/tree/master/examples) folder, [run it](https://github.com/laike9m/Cyberbrain#how-to-use) like you would normally do.

## Code Style

We use 
- [black](https://github.com/psf/black) for Python formatting.
- [prettier-eslint-cli](https://github.com/prettier/prettier-eslint-cli) for TypeScript/JavaScript formatting.

You should be able to find the corresponding plugins that do auto-formatting for your editor or IDE of choose.

- If you're using VS Code:
  - The official [Python plugin](https://marketplace.visualstudio.com/items?itemName=ms-python.python) lets you set black as the formatter.
  - [Prettier ESLint
](https://marketplace.visualstudio.com/items?itemName=rvest.vs-code-prettier-eslint)
- If you're using JetBrains' IDEs, there might be other ways, but I tend to use [File Watchers](https://www.jetbrains.com/help/idea/using-file-watchers.html):
  
  ![](https://user-images.githubusercontent.com/2592205/113659455-e51a6c00-9656-11eb-9eb1-fa18296380bc.png)
  
  - TypeScript
  
  ![](https://user-images.githubusercontent.com/2592205/113659541-1abf5500-9657-11eb-9058-e0069068a20d.png)
    
  - JavaScript
  
  ![](https://user-images.githubusercontent.com/2592205/113659628-480c0300-9657-11eb-9105-91e76b80a6b4.png)

  - Python
  
  ![](https://user-images.githubusercontent.com/2592205/113659684-6f62d000-9657-11eb-9036-ca744e7b5f68.png)

Code style will be checked for any PR, so make sure to get them right before filing a PR.

## Packaging

```
# Build the Python package.
poetry build

# Build the VS Code package.
cd cyberbrain-vsc && vsce package --no-yarn
```

This is just FYI. As of now only me have the permission to publish new versions.
