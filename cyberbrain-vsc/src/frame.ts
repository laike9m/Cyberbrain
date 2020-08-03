/* Holding a frame passed from backend and handles console logging. */

import {
  Event as EventProto,
  Frame as FrameProto,
} from "./generated/communication_pb";

import { Binding, Deletion, Event, InitialValue, Mutation } from "./basis";

export class Frame {
  filename?: string;
  events: Record</* identifier */ string, Event[]> = {};

  // Maps events to relevant predecessor events.
  tracingResult: Record<
    /* event uid */ string,
    /* predecessor event uids */ string[]
  > = {};

  constructor(frame: FrameProto) {
    this.filename = frame.getFilename();
    frame.getEventsMap().forEach((eventList, identifier) => {
      let event: EventProto;
      if (!this.events.hasOwnProperty(identifier)) {
        this.events[identifier] = [];
      }
      for (event of eventList.getEventsList()) {
        if (event.hasInitialValue()) {
          this.events[identifier].push(
            new InitialValue(event.getInitialValue()!)
          );
        }
        if (event.hasBinding()) {
          this.events[identifier].push(new Binding(event.getBinding()!));
        }
        if (event.hasMutation()) {
          this.events[identifier].push(new Mutation(event.getMutation()!));
        }
        if (event.hasDeletion()) {
          this.events[identifier].push(new Deletion(event.getDeletion()!));
        }
      }
    });
    frame.getTracingResultMap().forEach((predecessorEventUidList, eventUid) => {
      this.tracingResult[eventUid] = predecessorEventUidList.getEventUidsList();
    });
  }

  // Takes a event uid and logs its value to console.
  logValue(eventUid: string) {
    // TODO: implement
  }
}
