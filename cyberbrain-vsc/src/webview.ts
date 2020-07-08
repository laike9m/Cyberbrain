import * as vscode from 'vscode';
import * as path from "path";

let currentPanel: vscode.WebviewPanel | undefined = undefined;

export function activateWebView(context: vscode.ExtensionContext) {
    if (currentPanel) {
        currentPanel.reveal(vscode.ViewColumn.Two);
    } else {
        currentPanel = vscode.window.createWebviewPanel(
            'Cyberbrain',
            'Cyberbrain Backtrace',
            vscode.ViewColumn.Two,
            {
                enableScripts: true, // 启用JS，默认禁用
                retainContextWhenHidden: true, // webview被隐藏时保持状态，避免被重置
            }
        );

        // Get the special URI to use with the webview
        const loadingGifSrc = currentPanel.webview.asWebviewUri(vscode.Uri.file(
            path.join(context.extensionPath, 'static', 'images', 'loading.gif')
        ));

        currentPanel.webview.html = getInitialContent(loadingGifSrc);
    }
}

export function postMessageToBacktracePanel() {
    currentPanel!.webview.postMessage({server: 'ready'});
}

function getInitialContent(gifSrc: vscode.Uri) {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cat Coding</title>
</head>
<body>
    <h1>Loading...</h1>
    <img src="${gifSrc}" alt="loading" />
    <script>
        window.addEventListener('message', event => {
            console.log("Webview got message: " + JSON.stringify(event.data));
        });
    </script>
</body>
</html>`;
}