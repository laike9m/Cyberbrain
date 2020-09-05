function assertEqual(item1, item2, msg) {
  if (msg === undefined) {
    msg = `${item1} ${item2}`;
  }
  console.assert(item1 === item2, msg);
}

export class Loop {
  constructor(startOffset, endOffset, startLineno) {
    this.startLineno = startLineno;
    this.startOffset = startOffset;
    this.endOffset = endOffset;
    this.counter = 0;
    this.parent = undefined;
    this.children = new Set();

    // The index of the first event in each iteration of this loop.
    // Maps counter to index. Note that the counter includes parent's counter, like [0,0,1]
    this._iterationStarts = new Map();
  }

  addIterationStart(counters, eventIndex) {
    // We can't use array as keys directly, since we don't keep the array objects.
    this._iterationStarts.set(counters.toString(), eventIndex);
  }

  getCurrentIterationStart() {
    return this._iterationStarts.get(this.getCounters().toString());
  }

  /* Returns the index of the last iteration that the loop has.
   * Note that this method needs improving. Right now the count might be actual size + 1,
   * because we only counts "jump back", and does not check whether the iteration exists.
   */
  get maxIteration() {
    return this._iterationStarts.size - 1;
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

TODO: Decide whether to show JumpBackToLoopStart node in trace graph.
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
    if (visibleEvent.offset < loop.startOffset) continue;
    if (visibleEvent.offset > loop.endOffset) break;
    eventsToHide.set(visibleEvent.offset, visibleEvent);
  }

  // Calculates events that should be made visible, in this loop.
  let maxReachedOffset = -1;
  for (let i = loop.getCurrentIterationStart(); i < events.length; i++) {
    let event = events[i];
    let offset = event.offset;
    if (offset > loop.endOffset) break;
    if (offset > maxReachedOffset) {
      maxReachedOffset = offset;
      if (!eventsToShow.has(event.offset)) {
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

  console.assert(eventsToShow.size === eventsToHide.size);
  return [eventsToHide, eventsToShow];
}
