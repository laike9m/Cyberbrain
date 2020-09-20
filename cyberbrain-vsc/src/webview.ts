import * as vscode from "vscode";
import * as path from "path";
import { underDevMode } from "./utils";

// let currentPanel: vscode.WebviewPanel | undefined = undefined;

export function createWebView() {
  return vscode.window.createWebviewPanel(
    "Cyberbrain",
    "Cyberbrain Trace Graph",
    vscode.ViewColumn.Two,
    {
      enableScripts: true, // 启用JS，默认禁用
      retainContextWhenHidden: true // webview被隐藏时保持状态，避免被重置
    }
  );
}

/*
On the backend, frames are stored in a tree

UI interaction:

# Picking frames
1. User clicks on a location in VSC
2. Extension sends a location to backend
3. Backend returns the first 5 frames that contain the specified code location, with
   the callsite location.
   (In the future we can extend the max number of candidates.)
4. User picks a frame
5. The identity of the picked frame is sent to backend
6. Backend sends back tracing results for the picked frame

Steps 2 ~ 5 won't happen if there's only one frame.

If there's no frame that matches the current location, nothing will happen.

# Map tracing result to code
TBD. But for now, we should prevent frame selection process from happening (again) if
tracing is present and code location didn't go out of the frame's scope.

# By default, we should show previous frame + current frame + 1-level frames derived
from the current frame. We will let users configure this on extension UI.
 */

export function setWebViewContent(
  context: vscode.ExtensionContext,
  webviewPanel: vscode.WebviewPanel
) {
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
  const visualizationJsURL = createWebviewUri(`${jsDir}/visualize.js`);
  const loopJsURL = createWebviewUri(`${jsDir}/loop.js`);

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
    <script type="module" src="${loopJsURL}"></script>
    <script type="module" src="${visNetworkJsURL}"></script>
    <script type="module" src="${visualizationJsURL}"></script>
    <link rel="stylesheet" type="text/css" href="${visNetworkCssURL}" />
    <style type="text/css">
      #vis{
        width: 100%;
        height: 600px;  /* If use 100%, height would be very small */
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
}
