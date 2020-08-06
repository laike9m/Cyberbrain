/* Basically a copy of basis.py */

import {
  Binding as BindingProto,
  Deletion as DeletionProto,
  InitialValue as InitialValueProto,
  Mutation as MutationProto,
} from "./generated/communication_pb";
import { decodeJson } from "./utils";

enum EventType {
  InitialValue = "InitialValue",
  Binding = "Binding",
  Mutation = "Mutation",
  Deletion = "Deletion",
}

export abstract class Event {
  target: string;
  lineno: number;
  filename: string;
  uid: string;
  // When passing an object to webview, its type is erased. Thus we need to explicitly store it here.
  type: EventType;

  protected constructor(
    target: string,
    lineno: number,
    filename: string,
    uid: string,
    type: EventType
  ) {
    this.target = target;
    this.lineno = lineno;
    this.filename = filename;
    this.uid = uid;
    this.type = type;
  }
}

export class InitialValue extends Event {
  value: any;

  constructor(initialValue: InitialValueProto) {
    super(
      initialValue.getTarget()!,
      initialValue.getLineno()!,
      initialValue.getFilename()!,
      initialValue.getUid()!,
      EventType.InitialValue
    );
    this.value = decodeJson(initialValue.getValue()!);
  }
}

export class Binding extends Event {
  value: any;
  sources: string[];

  constructor(binding: BindingProto) {
    super(
      binding.getTarget()!,
      binding.getLineno()!,
      binding.getFilename()!,
      binding.getUid()!,
      EventType.Binding
    );
    this.value = decodeJson(binding.getValue()!);
    this.sources = binding.getSourcesList();
  }
}

export class Mutation extends Event {
  value: any;
  delta: string;
  sources: string[];

  constructor(mutation: MutationProto) {
    super(
      mutation.getTarget()!,
      mutation.getLineno()!,
      mutation.getFilename()!,
      mutation.getUid()!,
      EventType.Mutation
    );
    this.value = decodeJson(mutation.getValue()!);
    this.delta = mutation.getDelta()!;
    this.sources = mutation.getSourcesList();
  }
}

export class Deletion extends Event {
  constructor(deletion: DeletionProto) {
    super(
      deletion.getTarget()!,
      deletion.getLineno()!,
      deletion.getFilename()!,
      deletion.getUid()!,
      EventType.Deletion
    );
  }
}
