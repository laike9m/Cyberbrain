/*
Handles incoming messages from Python and forwards them to webview.
*/

import * as grpc from "@grpc/grpc-js";
import {State} from "./generated/communication_pb";
import {postMessageToBacktracePanel} from "./webview";
import {RpcClient} from "./rpc_client";


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
    }

    handleServerState(call: grpc.ClientReadableStream<State>) {
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
}