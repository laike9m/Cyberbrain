import * as vscode from "vscode";
import * as path from "path";

// let currentPanel: vscode.WebviewPanel | undefined = undefined;

export function activateWebView(context: vscode.ExtensionContext) {
  let currentPanel = vscode.window.createWebviewPanel(
    "Cyberbrain",
    "Cyberbrain Backtrace",
    vscode.ViewColumn.Two,
    {
      enableScripts: true, // 启用JS，默认禁用
      retainContextWhenHidden: true, // webview被隐藏时保持状态，避免被重置
    }
  );

  // Get the special URI to use with the webview
  const visJsURL = currentPanel.webview.asWebviewUri(
    vscode.Uri.file(
      path.join(
        context.extensionPath,
        "node_modules",
        "vis-network",
        "dist",
        "vis-network.min.js"
      )
    )
  );

  setWebViewContent(currentPanel, visJsURL);
  return currentPanel;
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
  webView: vscode.WebviewPanel,
  visJsURL: vscode.Uri | null
) {
  webView.webview.html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Tracing Result</title>
    <script type="text/javascript" src="${visJsURL}"></script>
</head>
<body>
    <div id='vis' >
    <script>
        const vscode = acquireVsCodeApi();
        setTimeout(() => {
          // Wait a while so listener can start.
          vscode.postMessage("Webview ready");
        }, 500);
    
        window.addEventListener('message', event => {
          console.log(event.data);
      
          let nodes = new vis.DataSet([
            {id: 1, label: 'Node 1'},
            {id: 2, label: 'Node 2'},
            {id: 3, label: 'Node 3'},
            {id: 4, label: 'Node 4'},
            {id: 5, label: 'Node 5'}
          ]);
          
          var edges = new vis.DataSet([
            {from: 1, to: 3},
            {from: 1, to: 2},
            {from: 2, to: 4},
            {from: 2, to: 5},
            {from: 3, to: 3}
          ]);
            
          var container = document.getElementById('vis');
          var data = {
            nodes: nodes,
            edges: edges
          };
          var options = {};
          var network = new vis.Network(container, data, options);
        });
    </script>
</body>
</html>`;
}
