import * as vscode from "vscode";
import * as path from "path";
import { underDevMode } from "./utils";

export function openTraceGraph(
  context: vscode.ExtensionContext
): vscode.WebviewPanel {
  let webviewPanel = vscode.window.createWebviewPanel(
    "Cyberbrain",
    "Cyberbrain Trace Graph",
    vscode.ViewColumn.Two,
    {
      enableScripts: true, // 启用JS，默认禁用
      retainContextWhenHidden: true // webview被隐藏时保持状态，避免被重置
    }
  );
  function createWebviewUri(relativePath: string) {
    return webviewPanel.webview.asWebviewUri(
      vscode.Uri.file(
        path.join(context.extensionPath, path.normalize(relativePath))
      )
    );
  }

  // ExtensionMode: Production = 1, Development = 2, Test = 3.
  // See https://git.io/JJFvy. Use files in the src folder for development.
  let jsDir = "out";
  if (underDevMode(context)) {
    jsDir = "src";
  }

  // Get the special URI to use with the webview
  const visNetworkJsURL = createWebviewUri(
    "node_modules/vis-network/dist/vis-network.min.js"
  );
  const visNetworkCssURL = createWebviewUri(
    "node_modules/vis-network/styles/vis-network.min.css"
  );
  const randomColorJsURL = createWebviewUri(
    "node_modules/randomcolor/randomColor.js"
  );
  const traceGraphJsURL = createWebviewUri(`${jsDir}/trace_graph.js`);
  const valueJsURL = createWebviewUri(`${jsDir}/value.js`);
  const traceDataJsURL = createWebviewUri(`${jsDir}/trace_data.js`);

  let isDevMode = false;
  if (underDevMode(context)) {
    isDevMode = true;
  }

  webviewPanel.webview.html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Tracing Result</title>
    <script>const isDevMode = ${isDevMode};</script>
    <script type="text/javascript" src="${randomColorJsURL}"></script>
    <script type="module" src="${valueJsURL}"></script>
    <script type="module" src="${traceDataJsURL}"></script>
    <script type="module" src="${visNetworkJsURL}"></script>
    <script type="module" src="${traceGraphJsURL}"></script>
    <link rel="stylesheet" type="text/css" href="${visNetworkCssURL}" />
    <style type="text/css">
      #vis{
        width: 100%;
        height: 100%;
        border: 1px solid lightgray;
        position: absolute;
        top: 0px;
        right: 0px;
        bottom: 0px;
        left: 0px;
      }
      #node-popUp {
        display:none;
        position:absolute;
        top:350px;
        left:170px;
        z-index:299;
        width:250px;
        height:120px;
        background-color: #f9f9f9;
        border-style:solid;
        border-width:3px;
        border-color: #5394ed;
        padding:10px;
        text-align: center;
      }
      .vis-manipulation {
        width: 155px !important;
        background: rgba(0,0,0,0) !important;  /* Transparent */
      }
    </style>
</head>
<body>
    <div id="node-popUp">
      <span id="node-operation">node</span> <br>
      <table style="margin:auto;">
        <tr>
          <td>Counter</td>
          <td><input id="node-label" /></td>
        </tr>
      </table>
      <input type="button" value="save" id="node-saveButton" />
      <input type="button" value="cancel" id="node-cancelButton" />
    </div>
    <div id='vis'>
    <script>
        const vscode = acquireVsCodeApi();
        vscode.postMessage("Webview ready");
    </script>
</body>
</html>`;

  return webviewPanel;
}
