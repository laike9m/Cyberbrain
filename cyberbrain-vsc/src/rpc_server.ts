import * as vscode from "vscode";
import * as express from "express";
import * as bodyParser from "body-parser";
import { openTraceGraph } from "./webview";
import { underTestMode } from "./utils";
import { decode } from "@msgpack/msgpack";

let cl = console.log;

export class RpcServer {
  // Allow any size of payload to come. Default is 4MB.
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

      res.send("success");
    });
  }

  start() {
    this.server.listen(`${this.listeningPort}`, () =>
      cl(`Listening on ${this.listeningPort}`)
    );
  }
}
