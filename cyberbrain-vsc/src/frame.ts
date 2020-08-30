/* Holding a frame passed from backend and handles console logging. */

import { Frame as FrameProto } from "./generated/communication_pb";

import { Binding, Deletion, Event, InitialValue, Mutation } from "./basis";

export class Frame {
  filename?: string;
  events: Array<Event> = [];
  identifiers: Array<string> = [];

  // Maps events to relevant predecessor events.
  tracingResult: Record<
    /* event uid */ string,
    /* predecessor event uids */ string[]
  > = {};

  constructor(frame: FrameProto) {
    this.filename = frame.getFilename();
    frame.getEventsList().forEach((event) => {
      if (event.hasInitialValue()) {
        this.events.push(new InitialValue(event.getInitialValue()!));
      }
      if (event.hasBinding()) {
        this.events.push(new Binding(event.getBinding()!));
      }
      if (event.hasMutation()) {
        this.events.push(new Mutation(event.getMutation()!));
      }
      if (event.hasDeletion()) {
        this.events.push(new Deletion(event.getDeletion()!));
      }
    });
    this.identifiers = frame.getIdentifiersList();
    frame.getTracingResultMap().forEach((predecessorEventUidList, eventUid) => {
      this.tracingResult[eventUid] = predecessorEventUidList.getEventUidsList();
    });
  }

  // Takes a event uid and logs its value to console.
  logValue(eventUid: string) {
    // TODO: implement
  }
}
