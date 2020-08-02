/*
Handles incoming messages from Python and forwards them to webview.
*/

import * as grpc from "@grpc/grpc-js";
import { CursorPosition, State } from "./generated/communication_pb";
import { postMessageToBacktracePanel } from "./webview";
import { RpcClient } from "./rpc_client";
import { Position, TextDocument } from "vscode";
import * as assert from "assert";
import { Frame } from "./frame";

export class MessageCenter {
  private rpcClient: RpcClient;

  constructor() {
    this.rpcClient = RpcClient.getClient();
  }

  async start() {
    await this.rpcClient.waitForReady();

    let state = new State();
    state.setStatus(State.Status.CLIENT_READY);
    this.handleServerState(this.rpcClient.syncState(state));

    // TODO: Pass real cursor position.
    await this.findFrames(undefined, undefined);
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
    let frame = new Frame(frameProto);
  }

  private handleServerState(call: grpc.ClientReadableStream<State>) {
    call.on("data", function (serverState: State) {
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
    call.on("end", function () {
      console.log("syncState call ends");
    });
    call.on("error", function (err: any) {
      console.log(`syncState error: ${err}`);
    });
    call.on("status", function (status: any) {
      console.log(`Received server RPC status: ${status}`);
    });
  }
}
