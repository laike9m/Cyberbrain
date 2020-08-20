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

function assertEqual(item1, item2, msg) {
  if (msg === undefined) {
    msg = `${item1} ${item2}`;
  }
  console.assert(item1 === item2, msg);
}

export class Loop {
  constructor(startOffset, endOffset) {
    this.startOffset = startOffset;
    this.endOffset = endOffset;
    this.counter = 0;
    this.parent = undefined;
    this.children = new Set();

    // The index of the first event in each iteration of this loop.
    // Maps counter to index. Note that the counter includes parent's counter, like [0,0,1]
    this.iterationStarts = new Map();
  }

  addIterationStart(counters, eventIndex) {
    this.iterationStarts.set(counters, eventIndex);
  }

  getCurrentIterationStart() {
    return this.iterationStarts[this.counter];
  }

  setEndOffset(eventOffset) {
    this.endOffset = Math.max(this.endOffset, eventOffset);
  }

  setLoopCounter(value) {
    self.loopCounter = value;
  }
}

/*

Parameters:
  events: a sequence of events in one frame, sorted by the order they occurred.
  loops: a array of loops, sorted by loop start offset.

Returns:
  a list of events that will be shown in the trace graph

Meanwhile, loops are filled with iteration starts.

TODO: Decide whether to show JumpBackToLoopStart node in trace graph.
 */
export function getVisibleEventsAndUpdateLoops(events, loops) {
  let loopStack = [];
  let maxReachedOffset = 0;
  let visibleEvents = [];
  let previousEventOffset = -2;

  for (let event of events) {
    let offset = event.offset;
    // For initial state, all loop counters are 0, thus visible events should form a
    // sequence in which the next event always has a larger offset than the previous one.
    if (offset > maxReachedOffset) {
      maxReachedOffset = offset;
      visibleEvents.push(event);
    }

    // Checks whether there actually is another iteration by inspecting whether the offset of
    // next event is smaller than the current one.
    if (
      event.type === "JumpBackToLoopStart" &&
      event.index < events.length - 1 &&
      events[event.index + 1].offset < offset
    ) {
      loopStack[loopStack.length - 1].counter++;
      loopStack[loopStack.length - 1].addIterationStart(
        loopStack.map((loop) => loop.counter),
        event.index + 1 // The event following JumpBackToLoopStart is next iteration's start.
      );
    }

    // Pushes loop onto the stack.
    for (let loop of loops) {
      if (
        previousEventOffset < loop.startOffset &&
        loop.startOffset <= offset
      ) {
        if (loopStack.length > 0 && loop.parent === undefined) {
          loopStack[loopStack.length - 1].children.add(loop);
          loop.parent = loopStack[loopStack.length - 1];
        }
        loopStack.push(loop);
        loop.addIterationStart(
          loopStack.map((loop) => loop.counter),
          event.index
        );
      }
    }
    previousEventOffset = offset;

    // Pops loop out of the stack.
    if (
      loopStack.length > 0 &&
      loopStack[loopStack.length - 1].endOffset < offset
    ) {
      loopStack.pop().counter = 0;
    }
  }

  // Restores to the initial state.
  for (let loop of loops) {
    loop.counter = 0;
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
