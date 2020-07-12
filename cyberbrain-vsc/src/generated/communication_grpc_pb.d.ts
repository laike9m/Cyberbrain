// GENERATED CODE -- DO NOT EDIT!

// package: 
// file: communication.proto

import * as communication_pb from "./communication_pb";
import * as grpc from "@grpc/grpc-js";

interface ICommunicationService extends grpc.ServiceDefinition<grpc.UntypedServiceImplementation> {
  syncState: grpc.MethodDefinition<communication_pb.State, communication_pb.State>;
  findFrames: grpc.MethodDefinition<communication_pb.CursorPosition, communication_pb.FrameLocaterList>;
  getFrame: grpc.MethodDefinition<communication_pb.FrameLocater, communication_pb.Frame>;
}

export const CommunicationService: ICommunicationService;

export class CommunicationClient extends grpc.Client {
  constructor(address: string, credentials: grpc.ChannelCredentials, options?: object);
  syncState(argument: communication_pb.State, metadataOrOptions?: grpc.Metadata | grpc.CallOptions | null): grpc.ClientReadableStream<communication_pb.State>;
  syncState(argument: communication_pb.State, metadata?: grpc.Metadata | null, options?: grpc.CallOptions | null): grpc.ClientReadableStream<communication_pb.State>;
  findFrames(argument: communication_pb.CursorPosition, callback: grpc.requestCallback<communication_pb.FrameLocaterList>): grpc.ClientUnaryCall;
  findFrames(argument: communication_pb.CursorPosition, metadataOrOptions: grpc.Metadata | grpc.CallOptions | null, callback: grpc.requestCallback<communication_pb.FrameLocaterList>): grpc.ClientUnaryCall;
  findFrames(argument: communication_pb.CursorPosition, metadata: grpc.Metadata | null, options: grpc.CallOptions | null, callback: grpc.requestCallback<communication_pb.FrameLocaterList>): grpc.ClientUnaryCall;
  getFrame(argument: communication_pb.FrameLocater, callback: grpc.requestCallback<communication_pb.Frame>): grpc.ClientUnaryCall;
  getFrame(argument: communication_pb.FrameLocater, metadataOrOptions: grpc.Metadata | grpc.CallOptions | null, callback: grpc.requestCallback<communication_pb.Frame>): grpc.ClientUnaryCall;
  getFrame(argument: communication_pb.FrameLocater, metadata: grpc.Metadata | null, options: grpc.CallOptions | null, callback: grpc.requestCallback<communication_pb.Frame>): grpc.ClientUnaryCall;
}
