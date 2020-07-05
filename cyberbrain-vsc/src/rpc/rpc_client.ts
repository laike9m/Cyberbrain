import * as grpc from "@grpc/grpc-js";
import { CommunicationClient } from "./communication_grpc_pb";

let rpcClient = new CommunicationClient('localhost:50051', grpc.credentials.createInsecure());


export { rpcClient };
