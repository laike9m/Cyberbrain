// GENERATED CODE -- DO NOT EDIT!

// package:
// file: communication.proto

import * as communication_pb from "./communication_pb";
import * as google_protobuf_empty_pb from "google-protobuf/google/protobuf/empty_pb";
import * as grpc from "@grpc/grpc-js";

interface ICommunicationService
  extends grpc.ServiceDefinition<grpc.UntypedServiceImplementation> {
  sendFrame: grpc.MethodDefinition<
    communication_pb.Frame,
    google_protobuf_empty_pb.Empty
  >;
}

export const CommunicationService: ICommunicationService;

export class CommunicationClient extends grpc.Client {
  constructor(
    address: string,
    credentials: grpc.ChannelCredentials,
    options?: object
  );
  sendFrame(
    argument: communication_pb.Frame,
    callback: grpc.requestCallback<google_protobuf_empty_pb.Empty>
  ): grpc.ClientUnaryCall;
  sendFrame(
    argument: communication_pb.Frame,
    metadataOrOptions: grpc.Metadata | grpc.CallOptions | null,
    callback: grpc.requestCallback<google_protobuf_empty_pb.Empty>
  ): grpc.ClientUnaryCall;
  sendFrame(
    argument: communication_pb.Frame,
    metadata: grpc.Metadata | null,
    options: grpc.CallOptions | null,
    callback: grpc.requestCallback<google_protobuf_empty_pb.Empty>
  ): grpc.ClientUnaryCall;
}
