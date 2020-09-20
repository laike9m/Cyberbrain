import * as vscode from "vscode";
import * as path from "path";
import { spawn } from "child_process";

let cl = console.log;

const cbRoot = path.resolve(__dirname, "../../../..");

// const fileBeingTraced = path.resolve(cbRoot, "examples/loop.py");
const fileBeingTraced = path.resolve(cbRoot, "examples/word_count/wc.py");

let serverProcess = spawn("python", ["-m", "examples.word_count.wc"], {
  cwd: cbRoot
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

vscode.workspace.openTextDocument(fileBeingTraced).then(doc => {
  vscode.window.showTextDocument(doc, vscode.ViewColumn.One);
});

suite("Extension Test Suite", function() {
  this.timeout(6000);

  test("Render Trace Graph", done => {
    setTimeout(() => {
      serverProcess.kill();
      done();
    }, 5000);
  });
});
