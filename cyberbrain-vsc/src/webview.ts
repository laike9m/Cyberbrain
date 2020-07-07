import * as vscode from 'vscode';
import * as path from "path";

export function activateWebView(context: vscode.ExtensionContext) {
    const panel = vscode.window.createWebviewPanel(
        'Cyberbrain',
        'Cyberbrain Backtrace',
        vscode.ViewColumn.Two,
        {}
    );

    // Get the special URI to use with the webview
    const loadingGifSrc = panel.webview.asWebviewUri(vscode.Uri.file(
        path.join(context.extensionPath, 'static', 'images', 'loading.gif')
    ));

    panel.webview.html = getInitialContent(loadingGifSrc);
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
</body>
</html>`;
}