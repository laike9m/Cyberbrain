import * as vscode from "vscode";
import * as express from "express";
import * as bodyParser from "body-parser";
import { openTraceGraph } from "./webview";
import { isTestMode } from "./utils";
import { decode } from "@msgpack/msgpack";

let cl = console.log;

/*
RPC server that communicates with the running Python program.
 */
export class RpcServer {
  private server: express.Express;
  private readonly context: vscode.ExtensionContext;
  private readonly listeningPort = 1989; // TODO: Make it configurable.
  
  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.server = express();
    this.server.use(bodyParser.raw({ limit: "10GB" }));

    this.server.post("/frame", (req, res) => {
      cl("get message");
      // Hides the debug console on the bottom.
      vscode.commands.executeCommand("workbench.action.closePanel");

      // Sends data to the trace graph in webview.
      let webviewPanel = openTraceGraph(this.context);
      webviewPanel.webview.onDidReceiveMessage(
        (message: string) => {
          if (message === "Webview ready") {
            webviewPanel.webview.postMessage(decode(req.body));

            // If under test, don't open the devtools window because it will cover the trace graph.
            if (!isTestMode(this.context)) {
              vscode.commands.executeCommand(
                "workbench.action.webview.openDeveloperTools"
              );
            }
          }
        },
        undefined,
        this.context.subscriptions
      );

      res.send("success");
    });
  }

  start() {
    this.server.listen(`${this.listeningPort}`, () =>
      cl(`Listening on ${this.listeningPort}`)
    );
  }
}
