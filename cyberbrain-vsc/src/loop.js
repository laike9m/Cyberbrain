export function foo() {
  console.log("Successfully imported the loop module. 😀😀😀");
}

// TODO:
//  - Events should have some extra attributes:
//    * An index to represent the order they occurred. Index is frame specific.
//    * The offset in frame, so that we can detect loopStarts by comparing jump destination
//      and event offset.
//  - Add a new type of event: JumpBackToLoopStart, which can originate from:
//    * JUMP_ABSOLUTE (normal iteration ends)
//    * POP_JUMP_IF_FALSE (break/continue), and other conditional jump instructions.
//    Each JumpBackToLoopStart represents an *actual jump back that happened*.
//  - JumpBackToLoopStart events should have attributes:
//    * Jump target offset

export class Loop {
  constructor(offset) {
    this.startOffset = offset;
    this.counter = 0;

    // The index of the first event in each iteration of this loop.
    this.iterationStarts = [];
  }

  addIterationStart(eventIndex) {
    this.iterationStarts.push(eventIndex);
  }

  getCurrentIterationStart() {
    return this.iterationStarts[this.counter];
  }

  setLoopCounter(value) {
    self.loopCounter = value;
  }
}

/*

Parameters:
  events: a sequence of events in one frame, sorted by the order they occurred.
  loops: a map of loops, keyed by offset.

Returns:
  a list of events that will be shown in the trace graph

Meanwhile, loops are filled with iteration starts.

TODO: Decide whether to show JumpBackToLoopStart node in trace graph.
 */
export function getVisibleEventsAndUpdateLoops(events, loops) {
  let loopStartOffsets = Array.from(loops.keys());
  loopStartOffsets.sort();
  let currentLoopStartOffset = loopStartOffsets[0];

  let maxReachedOffset = 0;
  let visibleEvents = [];

  for (let event of events) {
    let offset = event.offset;
    // For initial state, all loop counters are 0, thus visible events should form a
    // sequence in which the next event always has a larger offset than the previous one.
    if (offset > maxReachedOffset) {
      maxReachedOffset = offset;
      visibleEvents.push(event);
    }
    // Find all iteration starts, which are events that come after a loopStart.
    // currentLoopStartOffset is set to the loopStart that's coming next, or null if it's already
    // the last loopStart.
    if (currentLoopStartOffset !== null && offset >= currentLoopStartOffset) {
      loops.get(currentLoopStartOffset).addIterationStart(event.index);
      let loopStartIndex = loopStartOffsets.indexOf(currentLoopStartOffset);
      currentLoopStartOffset =
        loopStartIndex === loopStartOffsets.length - 1
          ? null
          : loopStartOffsets[loopStartIndex + 1];
    }
    // Check whether there actually is another iteration by inspecting whether the offset of
    // next event is smaller than the current one.
    if (
      event.type === "JumpBackToLoopStart" &&
      event.index < events.length - 1 &&
      events[event.index + 1].offset < offset
    ) {
      currentLoopStartOffset = event.jump_target;
    }
  }
  return visibleEvents;
}

/*
When updating, the original events sequence passed from backend will act as the index
for locating events efficiently.

Parameters:
  events: a sequence of events in one frame, sorted by the order they occurred.
  loop: a loop whose loop counter is to be modified.
  new_loop_counter: the new value for the loop counter, set by users.

Returns:
  item 1: nodes removed
  item 2: nodes added
 */
export function generateNodeUpdate(events, loop, new_loop_counter) {
  let currentIterationStart = loop.getCurrentIterationStart();
  for (let i = currentIterationStart; i < events.length; i++) {
    let event = events[i];
  }

  // WIP

  return [/* nodes added */ [], /* nodes removed */ []];
}
