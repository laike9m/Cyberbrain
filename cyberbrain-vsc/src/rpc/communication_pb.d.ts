// package: 
// file: communication.proto

import * as jspb from "google-protobuf";

export class State extends jspb.Message {
  hasStatus(): boolean;
  clearStatus(): void;
  getStatus(): State.StatusMap[keyof State.StatusMap] | undefined;
  setStatus(value: State.StatusMap[keyof State.StatusMap]): void;

  hasMessage(): boolean;
  clearMessage(): void;
  getMessage(): string | undefined;
  setMessage(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): State.AsObject;
  static toObject(includeInstance: boolean, msg: State): State.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: State, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): State;
  static deserializeBinaryFromReader(message: State, reader: jspb.BinaryReader): State;
}

export namespace State {
  export type AsObject = {
    status?: State.StatusMap[keyof State.StatusMap],
    message?: string,
  }

  export interface StatusMap {
    CLIENT_READY: 1;
    SERVER_READY: 2;
    EXECUTION_COMPLETE: 3;
    BACKTRACING_COMPLETE: 4;
  }

  export const Status: StatusMap;
}

export class Location extends jspb.Message {
  hasLocation(): boolean;
  clearLocation(): void;
  getLocation(): string | undefined;
  setLocation(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Location.AsObject;
  static toObject(includeInstance: boolean, msg: Location): Location.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Location, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Location;
  static deserializeBinaryFromReader(message: Location, reader: jspb.BinaryReader): Location;
}

export namespace Location {
  export type AsObject = {
    location?: string,
  }
}

export class FrameBackTrace extends jspb.Message {
  hasBackTrace(): boolean;
  clearBackTrace(): void;
  getBackTrace(): string | undefined;
  setBackTrace(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): FrameBackTrace.AsObject;
  static toObject(includeInstance: boolean, msg: FrameBackTrace): FrameBackTrace.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: FrameBackTrace, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): FrameBackTrace;
  static deserializeBinaryFromReader(message: FrameBackTrace, reader: jspb.BinaryReader): FrameBackTrace;
}

export namespace FrameBackTrace {
  export type AsObject = {
    backTrace?: string,
  }
}

