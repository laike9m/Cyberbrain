import * as vscode from "vscode";
import { configure, getLogger } from "log4js";

const logFile = "/tmp/cyberbrain.log";

configure({
  appenders: {
    fileAppender: {
      type: "dateFile",
      filename: logFile,
      flags: "w" // Make sure each time an empty file is created.
    }
  },
  categories: {
    default: {
      appenders: ["fileAppender"],
      level: "all"
    }
  }
});
const logger = getLogger();

export function underDevMode(context: vscode.ExtensionContext) {
  // ExtensionMode: Production = 1, Development = 2, Test = 3.
  return context.extensionMode === 2;
}

export function underTestMode(context: vscode.ExtensionContext) {
  // ExtensionMode: Production = 1, Development = 2, Test = 3.
  return context.extensionMode === 3;
}
