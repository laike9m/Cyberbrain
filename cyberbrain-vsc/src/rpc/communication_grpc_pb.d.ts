// GENERATED CODE -- DO NOT EDIT!

// package: 
// file: communication.proto

import * as communication_pb from "./communication_pb";
import * as grpc from "@grpc/grpc-js";

interface ICommunicationService extends grpc.ServiceDefinition<grpc.UntypedServiceImplementation> {
  syncState: grpc.MethodDefinition<communication_pb.State, communication_pb.State>;
  getFrameBackTrace: grpc.MethodDefinition<communication_pb.Location, communication_pb.FrameBackTrace>;
}

export const CommunicationService: ICommunicationService;

export class CommunicationClient extends grpc.Client {
  constructor(address: string, credentials: grpc.ChannelCredentials, options?: object);
  syncState(argument: communication_pb.State, callback: grpc.requestCallback<communication_pb.State>): grpc.ClientUnaryCall;
  syncState(argument: communication_pb.State, metadataOrOptions: grpc.Metadata | grpc.CallOptions | null, callback: grpc.requestCallback<communication_pb.State>): grpc.ClientUnaryCall;
  syncState(argument: communication_pb.State, metadata: grpc.Metadata | null, options: grpc.CallOptions | null, callback: grpc.requestCallback<communication_pb.State>): grpc.ClientUnaryCall;
  getFrameBackTrace(argument: communication_pb.Location, callback: grpc.requestCallback<communication_pb.FrameBackTrace>): grpc.ClientUnaryCall;
  getFrameBackTrace(argument: communication_pb.Location, metadataOrOptions: grpc.Metadata | grpc.CallOptions | null, callback: grpc.requestCallback<communication_pb.FrameBackTrace>): grpc.ClientUnaryCall;
  getFrameBackTrace(argument: communication_pb.Location, metadata: grpc.Metadata | null, options: grpc.CallOptions | null, callback: grpc.requestCallback<communication_pb.FrameBackTrace>): grpc.ClientUnaryCall;
}
