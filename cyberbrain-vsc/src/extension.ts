// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import { activateWebView } from "./webview";
import { MessageCenter } from "./messaging";

export function activate(context: vscode.ExtensionContext) {
  let disposable = vscode.commands.registerCommand(
    "cyberbrain.init",
    async () => {
      let webviewPanel = activateWebView(context);
      let messageCenter = new MessageCenter(context, webviewPanel);
      await messageCenter.start();
    }
  );

  context.subscriptions.push(disposable);
}

// this method is called when your extension is deactivated
export function deactivate() {}
