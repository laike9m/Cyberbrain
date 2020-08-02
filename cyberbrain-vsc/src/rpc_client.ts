import * as grpc from "@grpc/grpc-js";
import { CommunicationClient } from "./generated/communication_grpc_pb";
import {
    CursorPosition,
    Frame,
    FrameLocater,
    FrameLocaterList,
    State
} from "./generated/communication_pb";

// Singleton RPC client.
export class RpcClient {
    private static _instance: RpcClient;
    readonly innerClient: CommunicationClient;

    private constructor() {
        this.innerClient = new CommunicationClient('localhost:50051', grpc.credentials.createInsecure());
    }

    static getClient() {
        if (!RpcClient._instance) {
            RpcClient._instance = new RpcClient();
        }
        return RpcClient._instance;
    }

    async waitForReady() {
        console.log("Waiting for connection ready...");
        const deadline = new Date();
        deadline.setSeconds(deadline.getSeconds() + 20);
        return new Promise((resolve, reject) => {
            grpc.waitForClientReady(this.innerClient, deadline, function (error) {
                if (error === undefined) {
                    console.log("Connected to server 🎉");
                    resolve();
                } else {
                    reject(error);
                }
            });
        });
    }

    syncState(state: State): grpc.ClientReadableStream<State> {
        return this.innerClient.syncState(state);
    }

    async findFrames(position: CursorPosition): Promise<FrameLocaterList> {
        return new Promise((resolve, reject) => {
            this.innerClient.findFrames(position, function (error, frameLocaterList) {
                if (error === null) {
                    resolve(frameLocaterList);
                } else {
                    reject(error);
                }
            });
        });
    }

    async getFrame(frameLocater: FrameLocater): Promise<Frame> {
        return new Promise((resolve, reject) => {
            this.innerClient.getFrame(frameLocater, function (error, frame) {
                if (error === null) {
                    resolve(frame);
                } else {
                    reject(error);
                }
            });
        });
    }
}
