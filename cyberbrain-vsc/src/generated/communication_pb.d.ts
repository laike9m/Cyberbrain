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

export class CursorPosition extends jspb.Message {
  hasFileName(): boolean;
  clearFileName(): void;
  getFileName(): string | undefined;
  setFileName(value: string): void;

  hasLine(): boolean;
  clearLine(): void;
  getLine(): number | undefined;
  setLine(value: number): void;

  hasCharacter(): boolean;
  clearCharacter(): void;
  getCharacter(): number | undefined;
  setCharacter(value: number): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): CursorPosition.AsObject;
  static toObject(includeInstance: boolean, msg: CursorPosition): CursorPosition.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: CursorPosition, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): CursorPosition;
  static deserializeBinaryFromReader(message: CursorPosition, reader: jspb.BinaryReader): CursorPosition;
}

export namespace CursorPosition {
  export type AsObject = {
    fileName?: string,
    line?: number,
    character?: number,
  }
}

export class FrameLocater extends jspb.Message {
  hasFrameId(): boolean;
  clearFrameId(): void;
  getFrameId(): number | undefined;
  setFrameId(value: number): void;

  hasFilename(): boolean;
  clearFilename(): void;
  getFilename(): string | undefined;
  setFilename(value: string): void;

  hasStartLineno(): boolean;
  clearStartLineno(): void;
  getStartLineno(): number | undefined;
  setStartLineno(value: number): void;

  hasEndLineno(): boolean;
  clearEndLineno(): void;
  getEndLineno(): number | undefined;
  setEndLineno(value: number): void;

  hasCallsiteFilename(): boolean;
  clearCallsiteFilename(): void;
  getCallsiteFilename(): string | undefined;
  setCallsiteFilename(value: string): void;

  hasCallsiteLineno(): boolean;
  clearCallsiteLineno(): void;
  getCallsiteLineno(): number | undefined;
  setCallsiteLineno(value: number): void;

  hasArguments(): boolean;
  clearArguments(): void;
  getArguments(): string | undefined;
  setArguments(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): FrameLocater.AsObject;
  static toObject(includeInstance: boolean, msg: FrameLocater): FrameLocater.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: FrameLocater, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): FrameLocater;
  static deserializeBinaryFromReader(message: FrameLocater, reader: jspb.BinaryReader): FrameLocater;
}

export namespace FrameLocater {
  export type AsObject = {
    frameId?: number,
    filename?: string,
    startLineno?: number,
    endLineno?: number,
    callsiteFilename?: string,
    callsiteLineno?: number,
    arguments?: string,
  }
}

export class FrameLocaterList extends jspb.Message {
  clearFrameLocatersList(): void;
  getFrameLocatersList(): Array<FrameLocater>;
  setFrameLocatersList(value: Array<FrameLocater>): void;
  addFrameLocaters(value?: FrameLocater, index?: number): FrameLocater;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): FrameLocaterList.AsObject;
  static toObject(includeInstance: boolean, msg: FrameLocaterList): FrameLocaterList.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: FrameLocaterList, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): FrameLocaterList;
  static deserializeBinaryFromReader(message: FrameLocaterList, reader: jspb.BinaryReader): FrameLocaterList;
}

export namespace FrameLocaterList {
  export type AsObject = {
    frameLocatersList: Array<FrameLocater.AsObject>,
  }
}

export class Frame extends jspb.Message {
  hasBackTrace(): boolean;
  clearBackTrace(): void;
  getBackTrace(): string | undefined;
  setBackTrace(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Frame.AsObject;
  static toObject(includeInstance: boolean, msg: Frame): Frame.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Frame, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Frame;
  static deserializeBinaryFromReader(message: Frame, reader: jspb.BinaryReader): Frame;
}

export namespace Frame {
  export type AsObject = {
    backTrace?: string,
  }
}

