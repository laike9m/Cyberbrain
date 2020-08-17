export function foo() {
  console.log("Successfully imported the loop module. 😀😀😀");
}

// TODO:
//  - Events should have some extra attributes:
//    * An index to represent the order they occurred. Index is frame specific.
//    * The offset in frame, so that we can detect knots by comparing jump destination
//      and event offset.
//  - Add a new type of event: JumpBackToKnot, which can originate from:
//    * JUMP_ABSOLUTE (normal iteration ends)
//    * POP_JUMP_IF_FALSE (break/continue), and other conditional jump instructions.
//    Each JumpBackToKnot represents an *actual jump back that happened*.
//  - JumpBackToKnot events should have attributes:
//    * Jump target offset

/*
What is a knot?
A knot represents a loop. To be more specific, it is the place where a loop starts.
When one iteration ends, the program will jump back to the code location that a knot
represents.

We use knots to record loop starts, but we don't record where a loop ends. Reasons are:
1. It's unnecessary, we know an iteration ends if the program jumps back to a knot.
2. Different iterations of the same loop can exit at different positions (e.g. continue)

Usually, knots have the same offset with FOR_ITER instructions, but since FOR_ITER does
not lead to any events, knots is "placed" right before the first event in the loop, and we
store the index of the first loop event in each iterations. Later when updating nodes,
we can just traverse from the firstLoopEventIndex corresponding to the current loop counter.
 */
export class Knot {
  constructor(offset) {
    this.offset = offset;
    this.loopCounter = 0;

    // The index of the first event in each iteration of this loop.
    this.iterationStarts = [];
  }

  addIterationStart(eventIndex) {
    this.iterationStarts.push(eventIndex);
  }

  setCounter(value) {
    self.loopCounter = value;
  }
}

/*

Parameters:
  events: a sequence of events, sorted by the order they occurred.
  knots: a map of knots, keyed by offset.

Returns:
  a list of events that will be shown in the trace graph

Meanwhile, knots are filled with insertion starts.

TODO: Decide whether to show JumpBackToKnot node in trace graph.
 */
export function getVisibleEventsAndUpdateKnots(events, knots) {
  let knotOffsets = Array.from(knots.keys());
  knotOffsets.sort();
  let currentKnotOffset = knotOffsets[0];

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
    // Find all iteration starts, which are events that come after a knot.
    // currentKnotOffset is set to the knot that's coming next, or null if it's already
    // the last knot.
    if (currentKnotOffset !== null && offset >= currentKnotOffset) {
      knots.get(currentKnotOffset).addIterationStart(event.index);
      let knotIndex = knotOffsets.indexOf(currentKnotOffset);
      currentKnotOffset =
        knotIndex === knotOffsets.length - 1
          ? null
          : knotOffsets[knotIndex + 1];
    }
    // Check whether there actually is another iteration by inspecting whether the offset of
    // next event is smaller than the current one.
    if (
      event.type === "JumpBackToKnot" &&
      event.index < events.length - 1 &&
      events[event.index + 1].offset < offset
    ) {
      currentKnotOffset = event.jump_target;
    }
  }
  return visibleEvents;
}

/*
When updating, the original events sequence passed from backend will act as the index
for locating events efficiently.
 */
export function generateNodeUpdate() {
  return [/* nodes added */ [], /* nodes removed */ []];
}
