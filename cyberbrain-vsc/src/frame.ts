/* Holding a frame passed from backend and handles console logging. */

import {Event as EventProto, Frame as FrameProto,} from "./generated/communication_pb";

import {Binding, Deletion, Event, InitialValue, Mutation} from "./basis";

export class Frame {
  filename?: string;
  events!: Record</* identifier */ string, Event[]>;

  // Maps events to relevant predecessor events.
  tracing_result?: Record<
    /* event uid */ string,
    /* predecessor event uids */ string[]
  >;

  constructor(frame: FrameProto) {
    this.filename = frame.getFilename();
    frame.getEventsMap().forEach(function (eventList, identifier) {
      console.log(identifier);
      let event: EventProto;
      for (event of eventList.getEventsList()) {
        if (event.hasInitialValue()) {
          console.log(new InitialValue(event.getInitialValue()!));
        }
        if (event.hasBinding()) {
          console.log(new Binding(event.getBinding()!));
        }
        if (event.hasMutation()) {
          console.log(new Mutation(event.getMutation()!));
        }
        if (event.hasDeletion()) {
          console.log(new Deletion(event.getDeletion()!));
        }
      }
    });
  }
}
