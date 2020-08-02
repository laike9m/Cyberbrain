// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { activateWebView } from "./webview";
import { MessageCenter } from "./messaging";

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

    // The command has been defined in the package.json file
    // Now provide the implementation of the command with registerCommand
    // The commandId parameter must match the command field in package.json
    let disposable = vscode.commands.registerCommand('cyberbrain.init', async () => {
        console.clear();
        vscode.window.showInformationMessage('Hello World from cyberbrain!');
        let messageCenter = new MessageCenter();
        await messageCenter.start();
    });

    context.subscriptions.push(disposable);
    activateWebView(context);

    // TODO: do nothing if devtools is already opened. Move to webview.ts
    // Should be easy once https://github.com/microsoft/vscode/issues/103610 is fixed.
    // vscode.commands.executeCommand('workbench.action.toggleDevTools');
}

// this method is called when your extension is deactivated
export function deactivate() {
}
