/* Basically a copy of basis.py */

import {
  Binding as BindingProto,
  Deletion as DeletionProto,
  InitialValue as InitialValueProto,
  JumpBackToLoopStart as JumpBackToLoopStartProto,
  Mutation as MutationProto,
} from "./generated/communication_pb";
import { decodeJson } from "./utils";

enum EventType {
  InitialValue = "InitialValue",
  Binding = "Binding",
  Mutation = "Mutation",
  Deletion = "Deletion",
  JumpBackToLoopStart = "JumpBackToLoopStart",
}

export abstract class Event {
  lineno: number;
  filename: string;
  uid: string;
  // When passing an object to webview, its type is erased. Thus we need to explicitly store it here.
  type: EventType;
  index: number;
  offset: number;

  protected constructor(
    lineno: number,
    filename: string,
    index: number,
    offset: number,
    uid: string,
    type: EventType
  ) {
    this.lineno = lineno;
    this.filename = filename;
    this.index = index;
    this.offset = offset;
    this.uid = uid;
    this.type = type;
  }
}

export class InitialValue extends Event {
  value: any;
  target: string;

  constructor(initialValue: InitialValueProto) {
    super(
      initialValue.getLineno()!,
      initialValue.getFilename()!,
      initialValue.getIndex()!,
      initialValue.getOffset()!,
      initialValue.getUid()!,
      EventType.InitialValue
    );
    this.target = initialValue.getTarget()!;
    this.value = decodeJson(initialValue.getValue()!);
  }
}

export class Binding extends Event {
  target: string;
  value: any;
  sources: string[];

  constructor(binding: BindingProto) {
    super(
      binding.getLineno()!,
      binding.getFilename()!,
      binding.getIndex()!,
      binding.getOffset()!,
      binding.getUid()!,
      EventType.Binding
    );
    this.target = binding.getTarget()!;
    this.value = decodeJson(binding.getValue()!);
    this.sources = binding.getSourcesList();
  }
}

export class Mutation extends Event {
  target: string;
  value: any;
  delta: string;
  sources: string[];

  constructor(mutation: MutationProto) {
    super(
      mutation.getLineno()!,
      mutation.getFilename()!,
      mutation.getIndex()!,
      mutation.getOffset()!,
      mutation.getUid()!,
      EventType.Mutation
    );
    this.target = mutation.getTarget()!;
    this.value = decodeJson(mutation.getValue()!);
    this.delta = mutation.getDelta()!;
    this.sources = mutation.getSourcesList();
  }
}

export class Deletion extends Event {
  target: string;

  constructor(deletion: DeletionProto) {
    super(
      deletion.getLineno()!,
      deletion.getFilename()!,
      deletion.getIndex()!,
      deletion.getOffset()!,
      deletion.getUid()!,
      EventType.Deletion
    );
    this.target = deletion.getTarget()!;
  }
}

export class JumpBackToLoopStart extends Event {
  jump_target: Number;

  constructor(jumpBack: JumpBackToLoopStartProto) {
    super(
      jumpBack.getLineno()!,
      jumpBack.getFilename()!,
      jumpBack.getIndex()!,
      jumpBack.getOffset()!,
      jumpBack.getUid()!,
      EventType.JumpBackToLoopStart
    );
    this.jump_target = jumpBack.getJumpTarget()!;
  }
}

export class Loop {
  startOffset: number;
  endOffset: number;
  startLineno: number;

  constructor(startOffset: number, endOffset: number, startLineno: number) {
    this.startOffset = startOffset;
    this.endOffset = endOffset;
    this.startLineno = startLineno;
  }
}
