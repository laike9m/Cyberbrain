// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import { MessageCenter } from "./messaging";
import { underDevMode } from "./utils";

export function activate(context: vscode.ExtensionContext) {
  let disposable = vscode.commands.registerCommand(
    "cyberbrain.init",
    async () => {
      let messageCenter = new MessageCenter(context);
      await messageCenter.wait();
    }
  );

  context.subscriptions.push(disposable);

  // For ease of development and testing.
  if (underDevMode(context)) {
    vscode.commands.executeCommand("cyberbrain.init");
  }
}

// this method is called when your extension is deactivated
export function deactivate() {}
