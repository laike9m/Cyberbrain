// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import {State} from './generated/communication_pb';
import {RpcClient} from './rpc_client';
import {activateWebView, postMessageToBacktracePanel} from "./webview";
import * as grpc from "@grpc/grpc-js";


// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

    // Use the console to output diagnostic information (console.log) and errors (console.error)
    // This line of code will only be executed once when your extension is activated
    console.log('Congratulations, your extension "cyberbrain" is now active!');

    // The command has been defined in the package.json file
    // Now provide the implementation of the command with registerCommand
    // The commandId parameter must match the command field in package.json
    let disposable = vscode.commands.registerCommand('cyberbrain.init', async () => {
        // The code you place here will be executed every time your command is executed
        // Display a message box to the user
        vscode.window.showInformationMessage('Hello World from cyberbrain!');

        let rpcClient = RpcClient.getClient();
        await rpcClient.waitForReady();

        let state = new State();
        state.setStatus(State.Status.CLIENT_READY);
        handleServerState(rpcClient.syncState(state));
    });

    context.subscriptions.push(disposable);
    activateWebView(context);
}

function handleServerState(call: grpc.ClientReadableStream<State>) {
    call.on('data', function (serverState: State) {
        switch (serverState?.getStatus()) {
            case State.Status.SERVER_READY:
                postMessageToBacktracePanel("Server is ready");
                break;
            case State.Status.EXECUTION_COMPLETE:
                postMessageToBacktracePanel("Program execution completes");
                break;
            case State.Status.BACKTRACING_COMPLETE:
                postMessageToBacktracePanel("Backtracing completes");
                break;
        }
    });
    call.on('end', function () {
        console.log("syncState call ends");
    });
    call.on('error', function (err: any) {
        console.log(`syncState error: ${err}`);
    });
    call.on('status', function (status: any) {
        console.log(`Received server RPC status: ${status}`);
    });
}

// this method is called when your extension is deactivated
export function deactivate() {
}
