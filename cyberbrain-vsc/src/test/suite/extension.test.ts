// Sometimes to make the test work, VS Code needs to be launched from command line.
// e.g. /Applications/Visual\ Studio\ Code\ -\ Insiders.app/Contents/MacOS/Electron

import * as vscode from "vscode";
import * as path from "path";
import { spawn, spawnSync } from "child_process";

let cl = console.log;

const cbRoot = path.resolve(__dirname, "../../../..");

// We have to identify the actual interpreter being used to correctly load local libs.
const interpreterPath: string = spawnSync("pdm", ["info"], {
  cwd: cbRoot
})
  .stdout.toString()
  .match(/(?<=Python Interpreter: )\S+/)![0];

cl("Python interpreter path: " + interpreterPath);

// Timeout is in seconds.
const examples = [
  { file: "examples/hello.py", args: ["-m", "examples.hello"], timeout: 3 },
  {
    file: "examples/nonlocal.py",
    args: ["-m", "examples.nonlocal"],
    timeout: 4
  },
  { file: "examples/loop.py", args: ["-m", "examples.loop"], timeout: 4 },
  {
    file: "examples/word_count/wc.py",
    args: ["-m", "examples.word_count.wc", "examples/word_count/inputs/*.txt"],
    timeout: 5
  },
  {
    file: "examples/telephone/telephone.py",
    args: ["-m", "examples.telephone.telephone"],
    timeout: 5
  },
  {
    file: "examples/bottles_of_beer/bottle.py",
    args: ["-m", "examples.bottles_of_beer.bottle"],
    timeout: 5
  },
  {
    file: "examples/twelve_days/twelve.py",
    args: ["-m", "examples.twelve_days.twelve"],
    timeout: 5
  },
  {
    file: "examples/rhymer/rhymer.py",
    args: ["-m", "examples.rhymer.rhymer"],
    timeout: 5
  },
  {
    file: "examples/mad_libs/mad_libs.py",
    args: ["-m", "examples.mad_libs.mad_libs"],
    timeout: 5
  },
  {
    file: "examples/issue47.py",
    args: ["-m", "examples.issue47"],
    timeout: 3
  },
  {
    file: "examples/password/password.py",
    args: [
      "-m",
      "examples.password.password",
      "examples/password/sonnets/*",
      "-s 1",
      "--l33t"
    ],
    timeout: 13,
    excludeWindows: true // Windows does not support "*" expansion, so don't run it.
  }
];

suite("Extension Test Suite", function() {
  this.timeout(0); // Disabled timeout.

  test("Render Trace Graph", async function() {
    for (const example of examples) {
      if (process.platform === "win32" && example.excludeWindows) {
        continue;
      }
      await runTest(example);
    }
  });

  async function runTest(example: any) {
    // Launches cb Python server.
    const fileBeingTraced = path.resolve(cbRoot, example.file);
    let serverProcess = spawn(interpreterPath, example.args, {
      cwd: cbRoot,
      shell: true // Required for wildcard expansion to work.
    });

    serverProcess.stdout.on("data", data => {
      console.log(`stdout: ${data}`);
    });

    serverProcess.stderr.on("data", data => {
      console.error(`stderr: ${data}`);
    });

    serverProcess.on("close", code => {
      console.log(`Server exited with code ${code}`);
    });

    // Opens the source file.
    vscode.workspace.openTextDocument(fileBeingTraced).then(doc => {
      vscode.window.showTextDocument(doc, vscode.ViewColumn.One);
    });

    // Waits for enough time so we can review the trace graph.
    // TODO: Find a way to detect trace graph rendering ready, and make wait time flexible.
    return new Promise(resolve => {
      setTimeout(() => {
        serverProcess.kill();
        resolve(0);
      }, 1000 * example.timeout);
    });
  }
});
