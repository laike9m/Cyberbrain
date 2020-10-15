/*
If we need to migrate tests to TS, see:
https://dev.to/daniel_werner/testing-typescript-with-mocha-and-chai-5cl8
 */

// Need to set isDevMode to avoid ReferenceError: isDevMode is not defined
// https://stackoverflow.com/a/59243202/2142577
const global = (0, eval)("this");
global.isDevMode = false;

import hamjest from "hamjest";

import { Loop, TraceData } from "../src/trace_data.js";

const { assertThat, contains, hasProperty, hasProperties } = hamjest;

let cl = console.log;

let traceData = new TraceData();

function getUpdatedVisibleEvents(oldVisibleEvents, eventsToShow) {
  let offsetToEvent = new Map();
  for (let event of oldVisibleEvents) {
    offsetToEvent.set(event.offset, event);
  }
  for (let [offset, event] of eventsToShow.entries()) {
    offsetToEvent.set(offset, event);
  }
  let newEvents = Array.from(offsetToEvent.values());
  newEvents.sort((e1, e2) => e1.offset - e2.offset);
  return newEvents;
}

describe("Test nested loops", function() {
  function prepareInitialState() {
    let events = [
      { type: "Binding", index: 0, offset: 0 },
      { type: "Binding", index: 1, offset: 2 },
      { type: "Binding", index: 2, offset: 4 },
      { type: "JumpBackToLoopStart", index: 3, offset: 6 },
      { type: "Binding", index: 4, offset: 2 },
      { type: "Binding", index: 5, offset: 4 },
      { type: "JumpBackToLoopStart", index: 6, offset: 6 },
      { type: "Binding", index: 7, offset: 8 },
      { type: "JumpBackToLoopStart", index: 8, offset: 10 },
      { type: "Binding", index: 9, offset: 0 },
      { type: "Binding", index: 10, offset: 2 },
      { type: "Binding", index: 11, offset: 4 },
      { type: "JumpBackToLoopStart", index: 12, offset: 6 },
      { type: "Binding", index: 13, offset: 2 },
      { type: "Binding", index: 14, offset: 4 },
      { type: "JumpBackToLoopStart", index: 15, offset: 6 },
      { type: "Binding", index: 16, offset: 8 },
      { type: "JumpBackToLoopStart", index: 17, offset: 10 },
      { type: "Binding", index: 18, offset: 12 }
    ];
    let loops = [new Loop(0, 10), new Loop(2, 6)];
    return [events].concat(traceData.initialize(events, loops));
  }

  it("Test getVisibleEventsAndUpdateLoops", function() {
    let [_, visibleEvents, loops] = prepareInitialState();
    assertThat(
      visibleEvents,
      contains(
        { type: "Binding", index: 0, offset: 0 },
        { type: "Binding", index: 1, offset: 2 },
        { type: "Binding", index: 2, offset: 4 },
        { type: "Binding", index: 7, offset: 8 },
        { type: "Binding", index: 18, offset: 12 }
      )
    );

    assertThat(
      loops,
      contains(
        hasProperties({
          startOffset: 0,
          endOffset: 10,
          counter: 0,
          parent: undefined,
          _iterationStarts: new Map([
            ["0", 0],
            ["1", 9]
          ])
        }),
        hasProperties({
          startOffset: 2,
          endOffset: 6,
          counter: 0,
          parent: hasProperty("endOffset", 10),
          _iterationStarts: new Map([
            ["0,0", 1],
            ["0,1", 4],
            ["1,0", 10],
            ["1,1", 13]
          ])
        })
      )
    );
  });

  describe("Test increase counter", function() {
    let [events, visibleEvents, loops] = prepareInitialState();

    loops[0].counter = 1;
    const [eventsToHide0, eventsToShow0] = loops[0].generateNodeUpdate(
      events,
      visibleEvents
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow0);

    describe("(0, 0) -> (1, 0)", function() {
      it("Test eventsToHide is correct", function() {
        assertThat(Array.from(eventsToHide0.values()), [
          { type: "Binding", index: 0, offset: 0 },
          { type: "Binding", index: 1, offset: 2 },
          { type: "Binding", index: 2, offset: 4 },
          { type: "Binding", index: 7, offset: 8 }
        ]);
      });

      it("Test eventsToShow is correct", function() {
        assertThat(Array.from(eventsToShow0.values()), [
          { type: "Binding", index: 9, offset: 0 },
          { type: "Binding", index: 10, offset: 2 },
          { type: "Binding", index: 11, offset: 4 },
          { type: "Binding", index: 16, offset: 8 }
        ]);
      });
    });

    loops[1].counter = 1;
    const [eventsToHide1, eventsToShow1] = loops[1].generateNodeUpdate(
      events,
      visibleEvents
    );

    describe("(1, 0) -> (1, 1)", function() {
      it("Test eventsToHide is correct", function() {
        assertThat(
          Array.from(eventsToHide1.values()),
          contains(
            { type: "Binding", index: 10, offset: 2 },
            { type: "Binding", index: 11, offset: 4 }
          )
        );
      });

      it("Test eventsToShow is correct", function() {
        assertThat(
          Array.from(eventsToShow1.values()),
          contains(
            { type: "Binding", index: 13, offset: 2 },
            { type: "Binding", index: 14, offset: 4 }
          )
        );
      });
    });
  });

  describe("Test increase counter", function() {
    let [events, visibleEvents, loops] = prepareInitialState();
    loops[1].counter = 1;
    const [eventsToHide0, eventsToShow0] = loops[1].generateNodeUpdate(
      events,
      visibleEvents
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow0);

    describe("(0, 0) -> (0, 1)", function() {
      it("Test eventsToHide is correct", function() {
        assertThat(
          Array.from(eventsToHide0.values()),
          contains(
            { type: "Binding", index: 1, offset: 2 },
            { type: "Binding", index: 2, offset: 4 }
          )
        );
      });

      it("Test eventsToShow is correct", function() {
        assertThat(
          Array.from(eventsToShow0.values()),
          contains(
            { type: "Binding", index: 4, offset: 2 },
            { type: "Binding", index: 5, offset: 4 }
          )
        );
      });
    });

    loops[0].counter = 1;
    const [eventsToHide1, eventsToShow1] = loops[0].generateNodeUpdate(
      events,
      visibleEvents
    );

    describe("(0, 1) -> (1, 1)", function() {
      it("Test eventsToHide is correct", function() {
        assertThat(
          Array.from(eventsToHide1.values()),
          contains(
            { type: "Binding", index: 0, offset: 0 },
            { type: "Binding", index: 4, offset: 2 },
            { type: "Binding", index: 5, offset: 4 },
            { type: "Binding", index: 7, offset: 8 }
          )
        );
      });

      it("Test eventsToShow is correct", function() {
        assertThat(
          Array.from(eventsToShow1.values()),
          contains(
            { type: "Binding", index: 9, offset: 0 },
            { type: "Binding", index: 13, offset: 2 },
            { type: "Binding", index: 14, offset: 4 },
            { type: "Binding", index: 16, offset: 8 }
          )
        );
      });
    });
  });

  describe("Test decrease counter", function() {
    let [events, visibleEvents, loops] = prepareInitialState();

    // Increase then decrease.
    loops[0].counter = 1;
    let [eventsToHide, eventsToShow] = loops[0].generateNodeUpdate(
      events,
      visibleEvents
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow);

    loops[1].counter = 1;
    [eventsToHide, eventsToShow] = loops[1].generateNodeUpdate(
      events,
      visibleEvents
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow);

    loops[0].counter = 0;
    let [eventsToHide0, eventsToShow0] = loops[0].generateNodeUpdate(
      events,
      visibleEvents
    );

    describe("(1, 1) -> (0, 1)", function() {
      it("Test eventsHide is correct", function() {
        assertThat(
          Array.from(eventsToHide0.values()),
          contains(
            { type: "Binding", index: 9, offset: 0 },
            { type: "Binding", index: 13, offset: 2 },
            { type: "Binding", index: 14, offset: 4 },
            { type: "Binding", index: 16, offset: 8 }
          )
        );
      });

      it("Test eventsToShow is correct", function() {
        assertThat(
          Array.from(eventsToShow0.values()),
          contains(
            { type: "Binding", index: 0, offset: 0 },
            { type: "Binding", index: 4, offset: 2 },
            { type: "Binding", index: 5, offset: 4 },
            { type: "Binding", index: 7, offset: 8 }
          )
        );
      });
    });

    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow0);
    loops[1].counter = 0;
    let [eventsToHide1, eventsToShow1] = loops[1].generateNodeUpdate(
      events,
      visibleEvents
    );

    describe("(0, 1) -> (0, 0)", function() {
      it("Test eventsToHide is correct", function() {
        assertThat(
          Array.from(eventsToHide1.values()),
          contains(
            { type: "Binding", index: 4, offset: 2 },
            { type: "Binding", index: 5, offset: 4 }
          )
        );
      });

      it("Test eventsToShow is correct", function() {
        assertThat(
          Array.from(eventsToShow1.values()),
          contains(
            { type: "Binding", index: 1, offset: 2 },
            { type: "Binding", index: 2, offset: 4 }
          )
        );
      });
    });
  });

  describe("Test decrease counter", function() {
    let [events, visibleEvents, loops] = prepareInitialState();

    // Increase then decrease.
    loops[0].counter = 1;
    let [eventsToHide, eventsToShow] = loops[0].generateNodeUpdate(
      events,
      visibleEvents
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow);

    loops[1].counter = 1;
    [eventsToHide, eventsToShow] = loops[1].generateNodeUpdate(
      events,
      visibleEvents
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow);

    loops[1].counter = 0;
    let [eventsToHide0, eventsToShow0] = loops[1].generateNodeUpdate(
      events,
      visibleEvents
    );

    describe("(1, 1) -> (1, 0)", function() {
      it("Test eventsToHide is correct", function() {
        assertThat(
          Array.from(eventsToHide0.values()),
          contains(
            { type: "Binding", index: 13, offset: 2 },
            { type: "Binding", index: 14, offset: 4 }
          )
        );
      });

      it("Test eventsToShow is correct", function() {
        assertThat(
          Array.from(eventsToShow0.values()),
          contains(
            { type: "Binding", index: 10, offset: 2 },
            { type: "Binding", index: 11, offset: 4 }
          )
        );
      });
    });

    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow0);
    loops[0].counter = 0;
    let [eventsToHide1, eventsToShow1] = loops[0].generateNodeUpdate(
      events,
      visibleEvents
    );

    describe("(1, 0) -> (0, 0)", function() {
      it("Test eventsHide is correct", function() {
        assertThat(
          Array.from(eventsToHide1.values()),
          contains(
            { type: "Binding", index: 9, offset: 0 },
            { type: "Binding", index: 10, offset: 2 },
            { type: "Binding", index: 11, offset: 4 },
            { type: "Binding", index: 16, offset: 8 }
          )
        );
      });

      it("Test eventsToShow is correct", function() {
        assertThat(
          Array.from(eventsToShow1.values()),
          contains(
            { type: "Binding", index: 0, offset: 0 },
            { type: "Binding", index: 1, offset: 2 },
            { type: "Binding", index: 2, offset: 4 },
            { type: "Binding", index: 7, offset: 8 }
          )
        );
      });
    });
  });
});

describe("Test adjacent JumpBackToLoopStart", function() {
  function prepareInitialState() {
    let events = [
      { type: "Binding", index: 0, offset: 0 },
      { type: "Binding", index: 1, offset: 2 },
      { type: "Binding", index: 2, offset: 4 },
      { type: "JumpBackToLoopStart", index: 3, offset: 6 },
      { type: "Binding", index: 4, offset: 2 },
      { type: "Binding", index: 5, offset: 4 },
      { type: "JumpBackToLoopStart", index: 6, offset: 6 },
      { type: "JumpBackToLoopStart", index: 7, offset: 8 },
      { type: "Binding", index: 8, offset: 0 },
      { type: "Binding", index: 9, offset: 2 },
      { type: "Binding", index: 10, offset: 4 },
      { type: "JumpBackToLoopStart", index: 11, offset: 6 },
      { type: "Binding", index: 12, offset: 2 },
      { type: "Binding", index: 13, offset: 4 },
      { type: "JumpBackToLoopStart", index: 14, offset: 6 },
      { type: "JumpBackToLoopStart", index: 15, offset: 8 },
      { type: "Binding", index: 16, offset: 10 }
    ];
    let loops = [new Loop(0, 8), new Loop(2, 6)];
    return [events].concat(traceData.initialize(events, loops));
  }

  it("Test initial state", function() {
    let [_, visibleEvents, loops] = prepareInitialState();
    assertThat(
      visibleEvents,
      contains(
        { type: "Binding", index: 0, offset: 0 },
        { type: "Binding", index: 1, offset: 2 },
        { type: "Binding", index: 2, offset: 4 },
        { type: "Binding", index: 16, offset: 10 }
      )
    );

    assertThat(
      loops,
      contains(
        hasProperties({
          startOffset: 0,
          endOffset: 8,
          counter: 0,
          parent: undefined,
          _iterationStarts: new Map([
            ["0", 0],
            ["1", 8]
          ])
        }),
        hasProperties({
          startOffset: 2,
          endOffset: 6,
          counter: 0,
          parent: hasProperty("endOffset", 8),
          _iterationStarts: new Map([
            ["0,0", 1],
            ["0,1", 4],
            ["1,0", 9],
            ["1,1", 12]
          ])
        })
      )
    );
  });
});

describe("Test loop with empty first iteration.", function() {
  function prepareInitialState() {
    let events = [
      { type: "Binding", index: 0, offset: 0 },
      { type: "JumpBackToLoopStart", index: 1, offset: 4 },
      { type: "Binding", index: 2, offset: 0 },
      { type: "Binding", index: 3, offset: 2 },
      { type: "JumpBackToLoopStart", index: 4, offset: 4 }
    ];
    let loops = [new Loop(0, 4)];
    return [events].concat(traceData.initialize(events, loops));
  }

  it("Test getVisibleEventsAndUpdateLoops", function() {
    let [_, visibleEvents, loops] = prepareInitialState();
    assertThat(
      visibleEvents,
      contains({ type: "Binding", index: 0, offset: 0 })
    );

    assertThat(
      loops,
      contains(
        hasProperties({
          startOffset: 0,
          endOffset: 4,
          counter: 0,
          parent: undefined,
          _iterationStarts: new Map([
            ["0", 0],
            ["1", 2]
          ])
        })
      )
    );
  });

  it("0 -> 1", function() {
    let [events, visibleEvents, loops] = prepareInitialState();
    loops[0].counter = 1;
    let [_, eventsToShow] = loops[0].generateNodeUpdate(events, visibleEvents);
    assertThat(
      Array.from(eventsToShow.values()),
      contains(
        { type: "Binding", index: 2, offset: 0 },
        { type: "Binding", index: 3, offset: 2 }
      )
    );
  });
});
