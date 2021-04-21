import * as vscode from "vscode";

export function isDevMode(context: vscode.ExtensionContext) {
  // ExtensionMode: Production = 1, Development = 2, Test = 3.
  return context.extensionMode === 2;
}

export function isTestMode(context: vscode.ExtensionContext) {
  // ExtensionMode: Production = 1, Development = 2, Test = 3.
  return context.extensionMode === 3;
}
