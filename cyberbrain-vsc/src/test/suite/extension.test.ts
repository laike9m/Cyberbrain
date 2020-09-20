import * as vscode from "vscode";
import * as path from "path";

let cl = console.log;

const fileBeingTraced = path.resolve(__dirname, "../../../../examples/loop.py");

vscode.workspace.openTextDocument(fileBeingTraced).then(doc => {
  vscode.window.showTextDocument(doc, vscode.ViewColumn.One);
});

suite("Extension Test Suite", function() {
  this.timeout(6000);

  test("Render Trace Graph", done => {
    setTimeout(() => {
      done();
    }, 5000);
  });
});
