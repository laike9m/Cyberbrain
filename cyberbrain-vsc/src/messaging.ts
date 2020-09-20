/*
Handles incoming messages from Python and forwards them to webview.
*/

import * as grpc from "@grpc/grpc-js";
import { CursorPosition, State } from "./generated/communication_pb";
import { RpcClient } from "./rpc_client";
import * as vscode from "vscode";
import { Position, TextDocument } from "vscode";
import * as assert from "assert";
import { Frame } from "./frame";
import { createWebView, setWebViewContent } from "./webview";
import { underTestMode } from "./utils";

export class MessageCenter {
  private rpcClient: RpcClient;
  private readonly webviewPanel: vscode.WebviewPanel;
  private frame?: Frame;
  private readonly context: vscode.ExtensionContext;

  constructor(context: vscode.ExtensionContext) {
    this.rpcClient = RpcClient.getClient();
    this.context = context;
    this.webviewPanel = createWebView();
  }

  async wait() {
    return new Promise((resolve, reject) => {
      this.webviewPanel.webview.onDidReceiveMessage(
        async message => {
          console.log(message.data);
          switch (message) {
            case "Exit": {
              resolve(); // Extension exits until this is called.
              break;
            }
            case "Webview ready": {
              console.log(message); // webview ready.
              await this.rpcClient.waitForReady();

              let state = new State();
              state.setStatus(State.Status.CLIENT_READY);
              this.handleServerState(this.rpcClient.syncState(state));

              // TODO: Pass real cursor position.
              await this.findFrames(undefined, undefined);

              // If under test, don't open the devtools window because it will cover the trace graph.
              if (!underTestMode(this.context)) {
                vscode.commands.executeCommand(
                  "workbench.action.webview.openDeveloperTools"
                );
              }
              break;
            }
          }
        },
        undefined,
        this.context.subscriptions
      );
      setWebViewContent(this.context, this.webviewPanel);
    });
  }

  async findFrames(document?: TextDocument, position?: Position) {
    console.log(`Calling findFrames with ${document}, ${position}`);
    let frameLocaterList = await this.rpcClient.findFrames(
      new CursorPosition()
    );

    // For now assuming there's only one frame locater.
    // In the future we should expect multiple frame locaters to be returned and add
    // interaction process to users select the frame to visualize.
    assert(frameLocaterList.getFrameLocatersList().length === 1);

    let frameProto = await this.rpcClient.getFrame(
      frameLocaterList.getFrameLocatersList()[0]
    );
    this.frame = new Frame(frameProto);
    console.log(this.frame);
    this.sendMessageToBacktracePanel(this.frame);
  }

  private handleServerState(call: grpc.ClientReadableStream<State>) {
    call.on("data", (serverState: State) => {
      switch (serverState?.getStatus()) {
        case State.Status.SERVER_READY:
          this.sendMessageToBacktracePanel({ "server status": "Ready" });
          break;
        case State.Status.EXECUTION_COMPLETE:
          this.sendMessageToBacktracePanel({
            "server status": "Program execution completes"
          });
          break;
        case State.Status.BACKTRACING_COMPLETE:
          this.sendMessageToBacktracePanel({
            "server status": "Backtracing completes"
          });
          break;
      }
    });
    call.on("end", function() {
      console.log("syncState call ends");
    });
    call.on("error", function(err: any) {
      console.log(`syncState error: ${err}`);
    });
    call.on("status", function(status: any) {
      console.log(`Received server RPC status: ${status}`);
    });
  }

  sendMessageToBacktracePanel(data: object) {
    this.webviewPanel.webview.postMessage(data);
  }
}
