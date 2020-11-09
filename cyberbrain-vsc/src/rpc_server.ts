import * as grpc from "@grpc/grpc-js";
import { CommunicationService } from "./generated/communication_grpc_pb";
import { Empty } from "google-protobuf/google/protobuf/empty_pb";
import { openTraceGraph } from "./webview";
import * as vscode from "vscode";
import { underTestMode } from "./utils";
import { Frame } from "./frame";

let cl = console.log;

export class RpcServer {
  // Allow any size of payload to come. Default is 4MB.
  private options = { "grpc.max_receive_message_length": -1 };
  private server: grpc.Server;
  private readonly context: vscode.ExtensionContext;
  private readonly listeningPort = 1989; // TODO: Make it configurable.

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.server = new grpc.Server(this.options);

    // See https://git.io/JkvHJ on how to create a server.
    this.server.addService(CommunicationService, {
      sendFrame: (
        call: grpc.ServerUnaryCall<any, any>,
        callback: grpc.sendUnaryData<any>
      ) => {
        // Responds with an empty proto.
        callback(null, new Empty());

        // Sends data to the trace graph in webview.
        let webviewPanel = openTraceGraph(this.context);
        webviewPanel.webview.onDidReceiveMessage(
          (message: string) => {
            cl(message); // webview ready.
            if (message == "Webview ready") {
              webviewPanel.webview.postMessage(new Frame(call.request));

              // If under test, don't open the devtools window because it will cover the trace graph.
              if (!underTestMode(this.context)) {
                vscode.commands.executeCommand(
                  "workbench.action.webview.openDeveloperTools"
                );
              }
            }
          },
          undefined,
          this.context.subscriptions
        );
      }
    });
  }

  start() {
    this.server.bindAsync(
      `0.0.0.0:${this.listeningPort}`,
      grpc.ServerCredentials.createInsecure(),
      (err, port) => {
        if (err !== null) {
          cl(err);
        } else {
          cl(`Listening on 0.0.0.0:${this.listeningPort}`);
          this.server.start();
        }
      }
    );
  }
}
