// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from "vscode";
import { RpcServer } from "./rpc_server";

export function activate(context: vscode.ExtensionContext) {
  new RpcServer(context).start();
}

// this method is called when your extension is deactivated
export function deactivate() {}
