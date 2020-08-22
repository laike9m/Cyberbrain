/*
If we need to migrate tests to TS, see:
https://dev.to/daniel_werner/testing-typescript-with-mocha-and-chai-5cl8
 */

import pkg from "chai";
import {
  generateNodeUpdate,
  getVisibleEventsAndUpdateLoops,
  Loop,
} from "../src/loop.js";
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
      jump_target: 2,
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
      jump_target: 2,
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
      jump_target: 0,
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
      jump_target: 2,
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
      jump_target: 2,
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
      jump_target: 0,
    },
    {
      type: "Binding",
      index: 18,
      offset: 12,
    },
  ];
  let loops = [new Loop(0, 10), new Loop(2, 6)];

  it("Test getVisibleEventsAndUpdateLoops", function () {
    let visibleEvents = getVisibleEventsAndUpdateLoops(events, loops);
    assert.deepEqual(visibleEvents, [
      { type: "Binding", index: 0, offset: 0 },
      { type: "Binding", index: 1, offset: 2 },
      { type: "Binding", index: 2, offset: 4 },
      { type: "JumpBackToLoopStart", index: 3, offset: 6, jump_target: 2 },
      { type: "Binding", index: 7, offset: 8 },
      { type: "JumpBackToLoopStart", index: 8, offset: 10, jump_target: 0 },
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

  describe("Test increase counter in outer loop, (0, 0) -> (1, 0)", function () {
    let visibleEvents = getVisibleEventsAndUpdateLoops(events, loops);
    loops[0].counter = 1;
    const [eventsToHide, eventsToShow] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[0]
    );
    loops[0].counter = 0; // Restore state.

    it("eventsToHide and eventsToShow are of the same size", function () {
      assert.equal(eventsToHide.size, eventsToShow.size);
    });

    it("Test eventsToHide is correct", function () {
      assert.deepEqual(Array.from(eventsToHide.values()), [
        { type: "Binding", index: 0, offset: 0 },
        { type: "Binding", index: 1, offset: 2 },
        { type: "Binding", index: 2, offset: 4 },
        {
          type: "JumpBackToLoopStart",
          index: 3,
          offset: 6,
          jump_target: 2,
        },
        { type: "Binding", index: 7, offset: 8 },
        {
          type: "JumpBackToLoopStart",
          index: 8,
          offset: 10,
          jump_target: 0,
        },
      ]);
    });

    it("Test eventsToShow is correct", function () {
      assert.deepEqual(Array.from(eventsToShow.values()), [
        { type: "Binding", index: 9, offset: 0 },
        { type: "Binding", index: 10, offset: 2 },
        { type: "Binding", index: 11, offset: 4 },
        {
          type: "JumpBackToLoopStart",
          index: 12,
          offset: 6,
          jump_target: 2,
        },
        { type: "Binding", index: 16, offset: 8 },
        {
          type: "JumpBackToLoopStart",
          index: 17,
          offset: 10,
          jump_target: 0,
        },
      ]);
    });
  });

  describe("Test increase counter in inner loop, (0, 0) -> (0, 1)", function () {
    let visibleEvents = getVisibleEventsAndUpdateLoops(events, loops);
    loops[1].counter = 1;
    const [eventsToHide, eventsToShow] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[1]
    );
    loops[1].counter = 0; // Restore state.

    it("eventsToHide and eventsToShow are of the same size", function () {
      assert.equal(eventsToHide.size, eventsToShow.size);
    });

    it("Test eventsToHide is correct", function () {
      assert.deepEqual(Array.from(eventsToHide.values()), [
        { type: "Binding", index: 1, offset: 2 },
        { type: "Binding", index: 2, offset: 4 },
        {
          type: "JumpBackToLoopStart",
          index: 3,
          offset: 6,
          jump_target: 2,
        },
      ]);
    });

    it("Test eventsToShow is correct", function () {
      assert.deepEqual(Array.from(eventsToShow.values()), [
        { type: "Binding", index: 4, offset: 2 },
        { type: "Binding", index: 5, offset: 4 },
        {
          type: "JumpBackToLoopStart",
          index: 6,
          offset: 6,
          jump_target: 2,
        },
      ]);
    });
  });

  describe("Test decrease counter in outer loop, (1, 0) -> (0, 0)", function () {
    let visibleEvents = getVisibleEventsAndUpdateLoops(events, loops);

    // Increase then decrease.
    loops[0].counter = 1;
    let [eventsToHide, eventsToShow] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[0]
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow);

    loops[0].counter = 0;
    [eventsToHide, eventsToShow] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[0]
    );

    it("eventsToHide and eventsToShow are of the same size", function () {
      assert.equal(eventsToHide.size, eventsToShow.size);
    });

    it("Test eventsToHide is correct", function () {
      assert.deepEqual(Array.from(eventsToHide.values()), [
        { type: "Binding", index: 9, offset: 0 },
        { type: "Binding", index: 10, offset: 2 },
        { type: "Binding", index: 11, offset: 4 },
        {
          type: "JumpBackToLoopStart",
          index: 12,
          offset: 6,
          jump_target: 2,
        },
        { type: "Binding", index: 16, offset: 8 },
        {
          type: "JumpBackToLoopStart",
          index: 17,
          offset: 10,
          jump_target: 0,
        },
      ]);
    });

    it("Test eventsToShow is correct", function () {
      assert.deepEqual(Array.from(eventsToShow.values()), [
        { type: "Binding", index: 0, offset: 0 },
        { type: "Binding", index: 1, offset: 2 },
        { type: "Binding", index: 2, offset: 4 },
        {
          type: "JumpBackToLoopStart",
          index: 3,
          offset: 6,
          jump_target: 2,
        },
        { type: "Binding", index: 7, offset: 8 },
        {
          type: "JumpBackToLoopStart",
          index: 8,
          offset: 10,
          jump_target: 0,
        },
      ]);
    });
  });

  describe("Test decrease counter in inner loop, (0, 1) -> (0, 0)", function () {
    let visibleEvents = getVisibleEventsAndUpdateLoops(events, loops);

    // Increase then decrease.
    loops[1].counter = 1;
    let [eventsToHide, eventsToShow] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[1]
    );
    visibleEvents = getUpdatedVisibleEvents(visibleEvents, eventsToShow);

    loops[1].counter = 0;
    [eventsToHide, eventsToShow] = generateNodeUpdate(
      events,
      visibleEvents,
      loops[1]
    );

    it("eventsToHide and eventsToShow are of the same size", function () {
      assert.equal(eventsToHide.size, eventsToShow.size);
    });

    it("Test eventsToHide is correct", function () {
      assert.deepEqual(Array.from(eventsToHide.values()), [
        { type: "Binding", index: 4, offset: 2 },
        { type: "Binding", index: 5, offset: 4 },
        {
          type: "JumpBackToLoopStart",
          index: 6,
          offset: 6,
          jump_target: 2,
        },
      ]);
    });

    it("Test eventsToShow is correct", function () {
      assert.deepEqual(Array.from(eventsToShow.values()), [
        { type: "Binding", index: 1, offset: 2 },
        { type: "Binding", index: 2, offset: 4 },
        {
          type: "JumpBackToLoopStart",
          index: 3,
          offset: 6,
          jump_target: 2,
        },
      ]);
    });
  });
});

// TODO: test (0, 1) -> (1, 1), (1, 0) -> (1, 1), (1, 1) -> (1, 0), (1, 1) -> (0, 1)
