let cl = console.log;

/* Initialize the trace graph.

Parameters:
  events: a sequence of events in one frame, sorted by the order they occurred.
  loops: a array of loops, sorted by loop start offset.

Returns:
  - A list of events that should be displayed in the trace graph initially.
  - Updated loops.
  - A mapping from a lineno to its rank among all appeared linen numbers.
    For example, appeared line numbers are 2, 3, 5
    returned mapping is {2 => 1, 3 => 2, 5 => 3}

Updates:
  The passed in loops, whose iterations are detected and recorded.

 */
export function getInitialState(events, loops) {
  let loopStack = [];
  let maxReachedOffset = -1;
  let visibleEvents = [];
  let previousEventOffset = -2;
  let appearedLineNumbers = new Set();

  for (let event of events) {
    let offset = event.offset;
    appearedLineNumbers.add(event.lineno);

    // For initial state, all loop counters are 0, thus visible events should form a
    // sequence in which the next event always has a larger offset than the previous one.
    //
    // Note that we use >= instead of >. This is because we may need to two nodes of the
    // same offset. e.g.
    //
    //    nonlocal a
    //    a = 1
    //
    // In this case, the initial value event and binding event has the same offset because
    // they are both triggered by the STORE_DEREF instruction.
    if (offset >= maxReachedOffset) {
      maxReachedOffset = offset;

      // Don't include JumpBackToLoopStart in visible events.
      if (event.type !== "JumpBackToLoopStart") {
        visibleEvents.push(event);
      }
    }

    // Pops loop out of the stack.
    if (
      loopStack.length > 0 &&
      loopStack[loopStack.length - 1].endOffset < offset
    ) {
      loopStack.pop().counter = 0;
    }

    let currentLoop = loopStack[loopStack.length - 1];
    let nextEventIndex = event.index + 1;

    if (
      event.type === "JumpBackToLoopStart" &&
      event.index < events.length - 1 &&
      events[nextEventIndex].offset < offset
    ) {
      currentLoop.incrementCounter();
      currentLoop.addIterationStart(
        loopStack.map(loop => loop.counter),
        nextEventIndex // The event following JumpBackToLoopStart is next iteration's start.
      );
    }

    // Pushes loop onto the stack.
    for (let loop of loops) {
      if (
        previousEventOffset < loop.startOffset &&
        loop.startOffset <= offset
      ) {
        if (loopStack.length > 0 && loop.parent === undefined) {
          currentLoop.children.add(loop);
          loop.parent = currentLoop;
        }
        loopStack.push(loop);
        loop.addIterationStart(
          loopStack.map(loop => loop.counter),
          event.index
        );
      }
    }
    previousEventOffset = offset;
  }

  // Restores to the initial state.
  for (let loop of loops) {
    loop.counter = 0;
  }

  let linenoMapping = new Map();
  Array.from(appearedLineNumbers)
    .sort((a, b) => a - b)
    .forEach((lineno, ranking) => {
      linenoMapping.set(lineno, ranking);
    });

  return [visibleEvents, loops, linenoMapping];
}
