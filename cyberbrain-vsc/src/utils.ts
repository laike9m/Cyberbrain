import * as vscode from "vscode";

// TODO: Learn from
//   https://github.com/cuthbertLab/jsonpickleJS/blob/master/js/unpickler.js
//   and implement a better version of decode.
//   Maybe use https://stackoverflow.com/a/46132163.
export function decodeJson(jsonString: string) {
  return JSON.parse(jsonString);
}

export function doIfInDevMode(context: vscode.ExtensionContext, callback: any) {
  // ExtensionMode: Production = 1, Development = 2, Test = 3.
  if (context.extensionMode === 2) {
    callback();
  }
}

export function underTestMode(context: vscode.ExtensionContext) {
  // ExtensionMode: Production = 1, Development = 2, Test = 3.
  return context.extensionMode === 3;
}
