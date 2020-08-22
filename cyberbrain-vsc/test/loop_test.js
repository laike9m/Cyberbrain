/*
If we need to migrate tests to TS, see:
https://dev.to/daniel_werner/testing-typescript-with-mocha-and-chai-5cl8
 */

import pkg from "chai";
import { generateNodeUpdate, getInitialState, Loop } from "../src/loop.js";
import chaiSubset from "chai-subset";

const { assert, use } = pkg;
use(chaiSubset);

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

describe("Test nested loops", function () {
  function prepareInitialState() {
    let events = [
      {
        type: "Binding",
        index: 0,
        offset: 0,
      },
      {
        type: "Binding",
        index: 1,
        offset: 2,
      },
      {
        type: "Binding",
        index: 2,
        offset: 4,
      },
      {
        type: "JumpBackToLoopStart",
        index: 3,
        offset: 6,
      },
      {
        type: "Binding",
        index: 4,
        offset: 2,
      },
      {
        type: "Binding",
        index: 5,
        offset: 4,
      },
      {
        type: "JumpBackToLoopStart",
        index: 6,
        offset: 6,
      },
      {
        type: "Binding",
        index: 7,
        offset: 8,
      },
      {
        type: "JumpBackToLoopStart",
        index: 8,
        offset: 10,
      },
      {
        type: "Binding",
        index: 9,
        offset: 0,
      },
      {
        type: "Binding",
        index: 10,
        offset: 2,
      },
      {
        type: "Binding",
        index: 11,
        offset: 4,
      },
      {
        type: "JumpBackToLoopStart",
        index: 12,
        offset: 6,
      },
      {
        type: "Binding",
        index: 13,
        offset: 2,
      },
      {
        type: "Binding",
        index: 14,
        offset: 4,
      },
      {
        type: "JumpBackToLoopStart",
        index: 15,
        offset: 6,
      },
      {
        type: "Binding",
        index: 16,
        offset: 8,
      },
      {
        type: "JumpBackToLoopStart",
        index: 17,
        offset: 10,
      },
      {
        type: "Binding",
        index: 18,
        offset: 12,
      },
    ];
    let loops = [new Loop(0, 10), new Loop(2, 6)];
    return [events].concat(getInitialState(events, loops));
  }

  it("Test getVisibleEventsAndUpdateLoops", function () {
    let [_, visibleEvents, loops] = prepareInitialState();
    assert.deepEqual(visibleEvents, [
      { type: "Binding", index: 0, offset: 0 },
      { type: "Binding", index: 1, offset: 2 },
      { type: "Binding", index: 2, offset: 4 },
      { type: "JumpBackToLoopStart", index: 3, offset: 6 },
      { type: "Binding", index: 7, offset: 8 },
      { type: "JumpBackToLoopStart", index: 8, offset: 10 },
      { type: "Binding", index: 18, offset: 12 },
    ]);
    assert.containSubset(loops, [
      {
        startOffset: 0,
        endOffset: 10,
        counter: 0,
        parent: undefined,
        _iterationStarts: new Map([
          ["0", 0],
          ["1", 9],
        ]),
      },
      {
        startOffset: 2,
        endOffset: 6,
        counter: 0,
        parent: {
          endOffset: 10,
        },
        _iterationStarts: new Map([
          ["0,0", 1],
          ["0,1", 4],
          ["1,0", 10],
          ["1,1", 13],
        ]),
      },
    ]);
  });

  describe("Test increase counter", function () {
    let [events, visibleEvents, loops] = prepareInitialState();

    loops[0].counter = 1;
    const [eventsToHide0, eventsToShow0] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[0]
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow0);

    describe("(0, 0) -> (1, 0)", function () {
      it("Test eventsToHide is correct", function () {
        assert.deepEqual(Array.from(eventsToHide0.values()), [
          { type: "Binding", index: 0, offset: 0 },
          { type: "Binding", index: 1, offset: 2 },
          { type: "Binding", index: 2, offset: 4 },
          { type: "JumpBackToLoopStart", index: 3, offset: 6 },
          { type: "Binding", index: 7, offset: 8 },
          { type: "JumpBackToLoopStart", index: 8, offset: 10 },
        ]);
      });

      it("Test eventsToShow is correct", function () {
        assert.deepEqual(Array.from(eventsToShow0.values()), [
          { type: "Binding", index: 9, offset: 0 },
          { type: "Binding", index: 10, offset: 2 },
          { type: "Binding", index: 11, offset: 4 },
          { type: "JumpBackToLoopStart", index: 12, offset: 6 },
          { type: "Binding", index: 16, offset: 8 },
          { type: "JumpBackToLoopStart", index: 17, offset: 10 },
        ]);
      });
    });

    loops[1].counter = 1;
    const [eventsToHide1, eventsToShow1] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[1]
    );

    describe("(1, 0) -> (1, 1)", function () {
      it("Test eventsToHide is correct", function () {
        assert.deepEqual(Array.from(eventsToHide1.values()), [
          { type: "Binding", index: 10, offset: 2 },
          { type: "Binding", index: 11, offset: 4 },
          { type: "JumpBackToLoopStart", index: 12, offset: 6 },
        ]);
      });

      it("Test eventsToShow is correct", function () {
        assert.deepEqual(Array.from(eventsToShow1.values()), [
          { type: "Binding", index: 13, offset: 2 },
          { type: "Binding", index: 14, offset: 4 },
          { type: "JumpBackToLoopStart", index: 15, offset: 6 },
        ]);
      });
    });
  });

  describe("Test increase counter", function () {
    let [events, visibleEvents, loops] = prepareInitialState();
    loops[1].counter = 1;
    const [eventsToHide0, eventsToShow0] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[1]
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow0);

    describe("(0, 0) -> (0, 1)", function () {
      it("Test eventsToHide is correct", function () {
        assert.deepEqual(Array.from(eventsToHide0.values()), [
          { type: "Binding", index: 1, offset: 2 },
          { type: "Binding", index: 2, offset: 4 },
          { type: "JumpBackToLoopStart", index: 3, offset: 6 },
        ]);
      });

      it("Test eventsToShow is correct", function () {
        assert.deepEqual(Array.from(eventsToShow0.values()), [
          { type: "Binding", index: 4, offset: 2 },
          { type: "Binding", index: 5, offset: 4 },
          { type: "JumpBackToLoopStart", index: 6, offset: 6 },
        ]);
      });
    });

    loops[0].counter = 1;
    const [eventsToHide1, eventsToShow1] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[0]
    );

    describe("(0, 1) -> (1, 1)", function () {
      it("Test eventsToHide is correct", function () {
        assert.deepEqual(Array.from(eventsToHide1.values()), [
          { type: "Binding", index: 0, offset: 0 },
          { type: "Binding", index: 4, offset: 2 },
          { type: "Binding", index: 5, offset: 4 },
          { type: "JumpBackToLoopStart", index: 6, offset: 6 },
          { type: "Binding", index: 7, offset: 8 },
          { type: "JumpBackToLoopStart", index: 8, offset: 10 },
        ]);
      });

      it("Test eventsToShow is correct", function () {
        assert.deepEqual(Array.from(eventsToShow1.values()), [
          { type: "Binding", index: 9, offset: 0 },
          { type: "Binding", index: 13, offset: 2 },
          { type: "Binding", index: 14, offset: 4 },
          { type: "JumpBackToLoopStart", index: 15, offset: 6 },
          { type: "Binding", index: 16, offset: 8 },
          { type: "JumpBackToLoopStart", index: 17, offset: 10 },
        ]);
      });
    });
  });

  describe("Test decrease counter", function () {
    let [events, visibleEvents, loops] = prepareInitialState();

    // Increase then decrease.
    loops[0].counter = 1;
    let [eventsToHide, eventsToShow] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[0]
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow);

    loops[1].counter = 1;
    [eventsToHide, eventsToShow] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[1]
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow);

    loops[0].counter = 0;
    let [eventsToHide0, eventsToShow0] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[0]
    );

    describe("(1, 1) -> (0, 1)", function () {
      it("Test eventsHide is correct", function () {
        assert.deepEqual(Array.from(eventsToHide0.values()), [
          { type: "Binding", index: 9, offset: 0 },
          { type: "Binding", index: 13, offset: 2 },
          { type: "Binding", index: 14, offset: 4 },
          { type: "JumpBackToLoopStart", index: 15, offset: 6 },
          { type: "Binding", index: 16, offset: 8 },
          { type: "JumpBackToLoopStart", index: 17, offset: 10 },
        ]);
      });

      it("Test eventsToShow is correct", function () {
        assert.deepEqual(Array.from(eventsToShow0.values()), [
          { type: "Binding", index: 0, offset: 0 },
          { type: "Binding", index: 4, offset: 2 },
          { type: "Binding", index: 5, offset: 4 },
          { type: "JumpBackToLoopStart", index: 6, offset: 6 },
          { type: "Binding", index: 7, offset: 8 },
          { type: "JumpBackToLoopStart", index: 8, offset: 10 },
        ]);
      });
    });

    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow0);
    loops[1].counter = 0;
    let [eventsToHide1, eventsToShow1] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[1]
    );

    describe("(0, 1) -> (0, 0)", function () {
      it("Test eventsToHide is correct", function () {
        assert.deepEqual(Array.from(eventsToHide1.values()), [
          { type: "Binding", index: 4, offset: 2 },
          { type: "Binding", index: 5, offset: 4 },
          { type: "JumpBackToLoopStart", index: 6, offset: 6 },
        ]);
      });

      it("Test eventsToShow is correct", function () {
        assert.deepEqual(Array.from(eventsToShow1.values()), [
          { type: "Binding", index: 1, offset: 2 },
          { type: "Binding", index: 2, offset: 4 },
          { type: "JumpBackToLoopStart", index: 3, offset: 6 },
        ]);
      });
    });
  });

  describe("Test decrease counter", function () {
    let [events, visibleEvents, loops] = prepareInitialState();

    // Increase then decrease.
    loops[0].counter = 1;
    let [eventsToHide, eventsToShow] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[0]
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow);

    loops[1].counter = 1;
    [eventsToHide, eventsToShow] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[1]
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow);

    loops[1].counter = 0;
    let [eventsToHide0, eventsToShow0] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[1]
    );

    describe("(1, 1) -> (1, 0)", function () {
      it("Test eventsToHide is correct", function () {
        assert.deepEqual(Array.from(eventsToHide0.values()), [
          { type: "Binding", index: 13, offset: 2 },
          { type: "Binding", index: 14, offset: 4 },
          { type: "JumpBackToLoopStart", index: 15, offset: 6 },
        ]);
      });

      it("Test eventsToShow is correct", function () {
        assert.deepEqual(Array.from(eventsToShow0.values()), [
          { type: "Binding", index: 10, offset: 2 },
          { type: "Binding", index: 11, offset: 4 },
          { type: "JumpBackToLoopStart", index: 12, offset: 6 },
        ]);
      });
    });

    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow0);
    loops[0].counter = 0;
    let [eventsToHide1, eventsToShow1] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[0]
    );

    describe("(1, 0) -> (0, 0)", function () {
      it("Test eventsHide is correct", function () {
        assert.deepEqual(Array.from(eventsToHide1.values()), [
          { type: "Binding", index: 9, offset: 0 },
          { type: "Binding", index: 10, offset: 2 },
          { type: "Binding", index: 11, offset: 4 },
          { type: "JumpBackToLoopStart", index: 12, offset: 6 },
          { type: "Binding", index: 16, offset: 8 },
          { type: "JumpBackToLoopStart", index: 17, offset: 10 },
        ]);
      });

      it("Test eventsToShow is correct", function () {
        assert.deepEqual(Array.from(eventsToShow1.values()), [
          { type: "Binding", index: 0, offset: 0 },
          { type: "Binding", index: 1, offset: 2 },
          { type: "Binding", index: 2, offset: 4 },
          { type: "JumpBackToLoopStart", index: 3, offset: 6 },
          { type: "Binding", index: 7, offset: 8 },
          { type: "JumpBackToLoopStart", index: 8, offset: 10 },
        ]);
      });
    });
  });
});
