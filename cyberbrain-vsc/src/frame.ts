/* Holding a frame passed from backend and handles console logging. */

import {
  Frame as FrameProto,
  FrameLocater
} from "./generated/communication_pb";

import {
  Binding,
  Deletion,
  Event,
  InitialValue,
  JumpBackToLoopStart,
  Loop,
  Mutation,
  Return
} from "./basis";

// Essentially the FrameLocater proto message.
class FrameMetadata {
  frame_id?: String;
  frame_name?: String;
  filename?: String;
  start_lineno?: Number;
  end_lineno?: Number;
  callsite_filename?: String;
  callsite_lineno?: Number;
  arguments?: String;

  constructor(locater: FrameLocater) {
    this.frame_id = locater.getFrameId();
    this.frame_name = locater.getFrameName();
    this.filename = locater.getFilename();
    this.start_lineno = locater.getStartLineno();
    this.end_lineno = locater.getEndLineno();
    this.callsite_filename = locater.getCallsiteFilename();
    this.callsite_lineno = locater.getCallsiteLineno();
    this.arguments = locater.getArguments();
  }
}

export class Frame {
  metadata: FrameMetadata;
  events: Array<Event> = [];
  identifiers: Array<string> = [];
  loops: Array<Loop> = [];

  // Maps events to relevant predecessor events.
  tracingResult: Record<
    /* event uid */ string,
    /* predecessor event uids */ string[]
  > = {};

  constructor(frame: FrameProto) {
    this.metadata = new FrameMetadata(frame.getMetadata()!);
    frame.getEventsList().forEach(event => {
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
      if (event.hasReturn()) {
        this.events.push(new Return(event.getReturn()!));
      }
      if (event.hasJumpBackToLoopStart()) {
        this.events.push(
          new JumpBackToLoopStart(event.getJumpBackToLoopStart()!)
        );
      }
    });
    frame.getLoopsList().forEach(loop => {
      this.loops.push(
        new Loop(
          loop.getStartOffset()!,
          loop.getEndOffset()!,
          loop.getStartLineno()!
        )
      );
    });
    this.identifiers = frame.getIdentifiersList();
    frame.getTracingResultMap().forEach((predecessorEventUidList, eventUid) => {
      this.tracingResult[eventUid] = predecessorEventUidList.getEventIdsList();
    });
  }

  // Takes a event uid and logs its value to console.
  logValue(eventUid: string) {
    // TODO: implement
  }
}
