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
  };

  export interface StatusMap {
    CLIENT_READY: 1;
    SERVER_READY: 2;
    EXECUTION_COMPLETE: 3;
    BACKTRACING_COMPLETE: 4;
  }

  export const Status: StatusMap;
}

export class CursorPosition extends jspb.Message {
  hasFilename(): boolean;
  clearFilename(): void;
  getFilename(): string | undefined;
  setFilename(value: string): void;

  hasLineno(): boolean;
  clearLineno(): void;
  getLineno(): number | undefined;
  setLineno(value: number): void;

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
    filename?: string,
    lineno?: number,
    character?: number,
  };
}

export class FrameLocater extends jspb.Message {
  hasFrameId(): boolean;
  clearFrameId(): void;
  getFrameId(): string | undefined;
  setFrameId(value: string): void;

  hasFrameName(): boolean;
  clearFrameName(): void;
  getFrameName(): string | undefined;
  setFrameName(value: string): void;

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
    frameId?: string,
    frameName?: string,
    filename?: string,
    startLineno?: number,
    endLineno?: number,
    callsiteFilename?: string,
    callsiteLineno?: number,
    arguments?: string,
  };
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
  };
}

export class InitialValue extends jspb.Message {
  hasUid(): boolean;
  clearUid(): void;
  getUid(): string | undefined;
  setUid(value: string): void;

  hasFilename(): boolean;
  clearFilename(): void;
  getFilename(): string | undefined;
  setFilename(value: string): void;

  hasLineno(): boolean;
  clearLineno(): void;
  getLineno(): number | undefined;
  setLineno(value: number): void;

  hasTarget(): boolean;
  clearTarget(): void;
  getTarget(): string | undefined;
  setTarget(value: string): void;

  hasValue(): boolean;
  clearValue(): void;
  getValue(): string | undefined;
  setValue(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): InitialValue.AsObject;
  static toObject(includeInstance: boolean, msg: InitialValue): InitialValue.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: InitialValue, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): InitialValue;
  static deserializeBinaryFromReader(message: InitialValue, reader: jspb.BinaryReader): InitialValue;
}

export namespace InitialValue {
  export type AsObject = {
    uid?: string,
    filename?: string,
    lineno?: number,
    target?: string,
    value?: string,
  };
}

export class Binding extends jspb.Message {
  hasUid(): boolean;
  clearUid(): void;
  getUid(): string | undefined;
  setUid(value: string): void;

  hasFilename(): boolean;
  clearFilename(): void;
  getFilename(): string | undefined;
  setFilename(value: string): void;

  hasLineno(): boolean;
  clearLineno(): void;
  getLineno(): number | undefined;
  setLineno(value: number): void;

  hasTarget(): boolean;
  clearTarget(): void;
  getTarget(): string | undefined;
  setTarget(value: string): void;

  hasValue(): boolean;
  clearValue(): void;
  getValue(): string | undefined;
  setValue(value: string): void;

  clearSourcesList(): void;
  getSourcesList(): Array<string>;
  setSourcesList(value: Array<string>): void;
  addSources(value: string, index?: number): string;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Binding.AsObject;
  static toObject(includeInstance: boolean, msg: Binding): Binding.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Binding, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Binding;
  static deserializeBinaryFromReader(message: Binding, reader: jspb.BinaryReader): Binding;
}

export namespace Binding {
  export type AsObject = {
    uid?: string,
    filename?: string,
    lineno?: number,
    target?: string,
    value?: string,
    sourcesList: Array<string>,
  };
}

export class Mutation extends jspb.Message {
  hasUid(): boolean;
  clearUid(): void;
  getUid(): string | undefined;
  setUid(value: string): void;

  hasFilename(): boolean;
  clearFilename(): void;
  getFilename(): string | undefined;
  setFilename(value: string): void;

  hasLineno(): boolean;
  clearLineno(): void;
  getLineno(): number | undefined;
  setLineno(value: number): void;

  hasTarget(): boolean;
  clearTarget(): void;
  getTarget(): string | undefined;
  setTarget(value: string): void;

  hasValue(): boolean;
  clearValue(): void;
  getValue(): string | undefined;
  setValue(value: string): void;

  hasDelta(): boolean;
  clearDelta(): void;
  getDelta(): string | undefined;
  setDelta(value: string): void;

  clearSourcesList(): void;
  getSourcesList(): Array<string>;
  setSourcesList(value: Array<string>): void;
  addSources(value: string, index?: number): string;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Mutation.AsObject;
  static toObject(includeInstance: boolean, msg: Mutation): Mutation.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Mutation, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Mutation;
  static deserializeBinaryFromReader(message: Mutation, reader: jspb.BinaryReader): Mutation;
}

export namespace Mutation {
  export type AsObject = {
    uid?: string,
    filename?: string,
    lineno?: number,
    target?: string,
    value?: string,
    delta?: string,
    sourcesList: Array<string>,
  };
}

export class Deletion extends jspb.Message {
  hasUid(): boolean;
  clearUid(): void;
  getUid(): string | undefined;
  setUid(value: string): void;

  hasFilename(): boolean;
  clearFilename(): void;
  getFilename(): string | undefined;
  setFilename(value: string): void;

  hasLineno(): boolean;
  clearLineno(): void;
  getLineno(): number | undefined;
  setLineno(value: number): void;

  hasTarget(): boolean;
  clearTarget(): void;
  getTarget(): string | undefined;
  setTarget(value: string): void;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Deletion.AsObject;
  static toObject(includeInstance: boolean, msg: Deletion): Deletion.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Deletion, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Deletion;
  static deserializeBinaryFromReader(message: Deletion, reader: jspb.BinaryReader): Deletion;
}

export namespace Deletion {
  export type AsObject = {
    uid?: string,
    filename?: string,
    lineno?: number,
    target?: string,
  };
}

export class Event extends jspb.Message {
  hasInitialValue(): boolean;
  clearInitialValue(): void;
  getInitialValue(): InitialValue | undefined;
  setInitialValue(value?: InitialValue): void;

  hasBinding(): boolean;
  clearBinding(): void;
  getBinding(): Binding | undefined;
  setBinding(value?: Binding): void;

  hasMutation(): boolean;
  clearMutation(): void;
  getMutation(): Mutation | undefined;
  setMutation(value?: Mutation): void;

  hasDeletion(): boolean;
  clearDeletion(): void;
  getDeletion(): Deletion | undefined;
  setDeletion(value?: Deletion): void;

  getValueCase(): Event.ValueCase;
  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): Event.AsObject;
  static toObject(includeInstance: boolean, msg: Event): Event.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: Event, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): Event;
  static deserializeBinaryFromReader(message: Event, reader: jspb.BinaryReader): Event;
}

export namespace Event {
  export type AsObject = {
    initialValue?: InitialValue.AsObject,
    binding?: Binding.AsObject,
    mutation?: Mutation.AsObject,
    deletion?: Deletion.AsObject,
  };

  export enum ValueCase {
    VALUE_NOT_SET = 0,
    INITIAL_VALUE = 1,
    BINDING = 2,
    MUTATION = 3,
    DELETION = 4,
  }
}

export class EventList extends jspb.Message {
  clearEventsList(): void;
  getEventsList(): Array<Event>;
  setEventsList(value: Array<Event>): void;
  addEvents(value?: Event, index?: number): Event;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): EventList.AsObject;
  static toObject(includeInstance: boolean, msg: EventList): EventList.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: EventList, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): EventList;
  static deserializeBinaryFromReader(message: EventList, reader: jspb.BinaryReader): EventList;
}

export namespace EventList {
  export type AsObject = {
    eventsList: Array<Event.AsObject>,
  };
}

export class EventUidList extends jspb.Message {
  clearEventUidsList(): void;
  getEventUidsList(): Array<string>;
  setEventUidsList(value: Array<string>): void;
  addEventUids(value: string, index?: number): string;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): EventUidList.AsObject;
  static toObject(includeInstance: boolean, msg: EventUidList): EventUidList.AsObject;
  static extensions: {[key: number]: jspb.ExtensionFieldInfo<jspb.Message>};
  static extensionsBinary: {[key: number]: jspb.ExtensionFieldBinaryInfo<jspb.Message>};
  static serializeBinaryToWriter(message: EventUidList, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): EventUidList;
  static deserializeBinaryFromReader(message: EventUidList, reader: jspb.BinaryReader): EventUidList;
}

export namespace EventUidList {
  export type AsObject = {
    eventUidsList: Array<string>,
  };
}

export class Frame extends jspb.Message {
  hasFilename(): boolean;
  clearFilename(): void;
  getFilename(): string | undefined;
  setFilename(value: string): void;

  getEventsMap(): jspb.Map<string, EventList>;
  clearEventsMap(): void;
  getTracingResultMap(): jspb.Map<string, EventUidList>;
  clearTracingResultMap(): void;
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
    filename?: string,
    eventsMap: Array<[string, EventList.AsObject]>,
    tracingResultMap: Array<[string, EventUidList.AsObject]>,
  };
}

