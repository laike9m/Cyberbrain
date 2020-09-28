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
    this.id = `loop@line${startLineno}`;

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

  /*

  Parameters:
    events: a sequence of events in one frame, sorted by the order they occurred.
    visibleEvents: currently visible events, does it need to be sorted?
    loop: a loop whose counter is modified.

  Returns:
    item 1: nodes to hide
    item 2: nodes to show

   */
  generateNodeUpdate(events, visibleEvents) {
    // Maps offset to events.
    let eventsToHide = new Map();
    let eventsToShow = new Map();

    // Calculates events that should be hidden.
    for (let visibleEvent of visibleEvents) {
      if (visibleEvent.offset < this.startOffset) {
        continue;
      }
      if (visibleEvent.offset > this.endOffset) {
        break;
      }
      eventsToHide.set(visibleEvent.offset, visibleEvent);
    }

    // Calculates events that should be made visible, in this loop.
    let maxReachedOffset = -1;
    for (let i = this.getCurrentIterationStart(); i < events.length; i++) {
      let event = events[i];
      let offset = event.offset;
      if (offset > this.endOffset) {
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
    for (let innerLoop of this.children) {
      const [_, eventsToShowFromInner] = innerLoop.generateNodeUpdate(
        events,
        visibleEvents
      );
      // Merge and let results from inner loops override outer loops
      eventsToShow = new Map([...eventsToShow, ...eventsToShowFromInner]);
    }

    return [eventsToHide, eventsToShow];
  }
}
