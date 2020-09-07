let cl = console.log;

function debugLog(...messages) {
  // isDevMode is set in webview.ts
  if (isDevMode) {
    messages.forEach(msg => console.log(msg));
  }
}

export class Loop {
  constructor(startOffset, endOffset, startLineno) {
    this.startLineno = startLineno;
    this.startOffset = startOffset;
    this.endOffset = endOffset;
    this.counter = 0;
    this.parent = undefined;
    this.children = new Set();

    // Note that the number of iterations != maxCounter
    //
    // for i in range(2):
    //   for j in range(2):
    //
    // For the inner loop, number of iterations is 4, but maxCounter is 1.
    this.maxCounter = 0;

    // The index of the first event in each iteration of this loop.
    // Maps counter to index. Note that the counter includes parent's counter, like [0,0,1]
    this._iterationStarts = new Map();
  }

  incrementCounter() {
    this.counter++;
    this.maxCounter = Math.max(this.counter, this.maxCounter);
  }

  addIterationStart(counters, eventIndex) {
    // We can't use array as keys directly, since we don't keep the array objects.
    this._iterationStarts.set(counters.toString(), eventIndex);
  }

  getCurrentIterationStart() {
    return this._iterationStarts.get(this.getCounters().toString());
  }

  /* Calculates the counters array from top-level loop to the modified loop.
   *  Outer loop's counter will precedes inner loops'.
   */
  getCounters() {
    let counters = [this.counter];
    let parentLoop = this.parent;
    while (parentLoop !== undefined) {
      counters.unshift(parentLoop.counter);
      parentLoop = parentLoop.parent;
    }
    return counters;
  }
}

/*

Parameters:
  events: a sequence of events in one frame, sorted by the order they occurred.
  loops: a array of loops, sorted by loop start offset.

Returns:
  a list of events that should be displayed in the trace graph initially.

Meanwhile, loops are filled with iteration starts.

 */
export function getInitialState(events, loops) {
  let loopStack = [];
  let maxReachedOffset = -1;
  let visibleEvents = [];
  let previousEventOffset = -2;

  for (let event of events) {
    let offset = event.offset;
    // For initial state, all loop counters are 0, thus visible events should form a
    // sequence in which the next event always has a larger offset than the previous one.
    if (offset > maxReachedOffset) {
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
      debugLog("Pops: ", loopStack[loopStack.length - 1]);
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
      debugLog(`set ${currentLoop.getCounters()}: ${nextEventIndex}`);
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
        debugLog(`set ${loopStack.map(loop => loop.counter)}: ${event.index}`);
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

  return [visibleEvents, loops];
}

/*

Parameters:
  events: a sequence of events in one frame, sorted by the order they occurred.
  visibleEvents: currently visible events, does it need to be sorted?
  loop: a loop whose counter is modified.

Returns:
  item 1: nodes to hide
  item 2: nodes to show
 */
export function generateNodeUpdate(events, visibleEvents, loop) {
  // Maps offset to events.
  let eventsToHide = new Map();
  let eventsToShow = new Map();

  // Calculates events that should be hidden.
  for (let visibleEvent of visibleEvents) {
    if (visibleEvent.offset < loop.startOffset) {
      continue;
    }
    if (visibleEvent.offset > loop.endOffset) {
      break;
    }
    eventsToHide.set(visibleEvent.offset, visibleEvent);
  }

  // Calculates events that should be made visible, in this loop.
  let maxReachedOffset = -1;
  debugLog(
    `loop.getCurrentIterationStart(): ${loop.getCurrentIterationStart()}, events.length: ${
      events.length
    }`
  );
  for (let i = loop.getCurrentIterationStart(); i < events.length; i++) {
    let event = events[i];
    let offset = event.offset;
    debugLog(event);
    debugLog(`offset: ${offset}, loop.endOffset: ${loop.endOffset}`);
    if (offset > loop.endOffset) {
      break;
    }
    if (offset > maxReachedOffset) {
      maxReachedOffset = offset;
      if (
        !eventsToShow.has(event.offset) &&
        event.type !== "JumpBackToLoopStart"
      ) {
        // Only set once (target iteration), don't let later iterations override the result.
        eventsToShow.set(event.offset, event);
      }
    }
  }

  // Calculates events that should be made visible in inner loops if any.
  for (let innerLoop of loop.children) {
    const [_, eventsToShowFromInner] = generateNodeUpdate(
      events,
      visibleEvents,
      innerLoop
    );
    // Merge and let results from inner loops override outer loops
    eventsToShow = new Map([...eventsToShow, ...eventsToShowFromInner]);
  }

  return [eventsToHide, eventsToShow];
}
