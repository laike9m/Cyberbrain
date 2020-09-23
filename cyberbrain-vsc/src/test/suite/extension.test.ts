import * as vscode from "vscode";
import * as path from "path";
import { spawn } from "child_process";

let cl = console.log;

const cbRoot = path.resolve(__dirname, "../../../..");

const examples = [
  { file: "examples/hello.py", args: ["-m", "examples.hello"] },
  { file: "examples/nonlocal.py", args: ["-m", "examples.nonlocal"] },
  { file: "examples/loop.py", args: ["-m", "examples.loop"] },
  {
    file: "examples/word_count/wc.py",
    args: ["-m", "examples.word_count.wc", "examples/word_count/inputs/*.txt"]
  },
  {
    file: "examples/telephone/main.py",
    args: ["-m", "examples.telephone.main"]
  }
];

suite("Extension Test Suite", function() {
  this.timeout(0); // Disabled timeout.

  test("Render Trace Graph", async function() {
    for (const example of examples) {
      await runTest(example);
    }
  });

  async function runTest(example: any) {
    // Launches cb Python server.
    const fileBeingTraced = path.resolve(cbRoot, example.file);
    let serverProcess = spawn("python", example.args, {
      cwd: cbRoot,
      shell: true
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

    // Opens webview to show the trace graph.
    vscode.commands.executeCommand("cyberbrain.init");

    // Waits for 5 seconds so we have time to inspect the trace graph.
    return new Promise(resolve => {
      setTimeout(() => {
        serverProcess.kill();
        resolve();
      }, 5000);
    });
  }
});
