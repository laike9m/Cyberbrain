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

describe("Test nested loops", function() {
  function createTraceData() {
    return new TraceData({
      events: [
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
      ],
      loops: [new Loop(0, 10), new Loop(2, 6)],
      tracingResult: {}
    });
  }

  it("Test loop initialization", function() {
    const traceData = createTraceData();
    assertThat(
      traceData.visibleEventsArray,
      contains(
        { type: "Binding", index: 0, offset: 0 },
        { type: "Binding", index: 1, offset: 2 },
        { type: "Binding", index: 2, offset: 4 },
        { type: "Binding", index: 7, offset: 8 },
        { type: "Binding", index: 18, offset: 12 }
      )
    );

    assertThat(
      traceData.loops,
      contains(
        hasProperties({
          startOffset: 0,
          endOffset: 10,
          counter: 0,
          parent: undefined,
          _iterationStarts: new Map([
            ["0", 0],
            ["1", 9]
          ]),
          _iterationEnds: new Map([
            ["0", 8],
            ["1", 17]
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
          ]),
          _iterationEnds: new Map([
            ["0,0", 3],
            ["0,1", 6],
            ["1,0", 12],
            ["1,1", 15]
          ])
        })
      )
    );
  });

  describe("Test increase counter", function() {
    let traceData = createTraceData();

    it("(0, 0) -> (1, 0)", function() {
      traceData.loops[0].counter = 1;
      traceData.updateVisibleEvents();
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 9, offset: 0 },
        { type: "Binding", index: 10, offset: 2 },
        { type: "Binding", index: 11, offset: 4 },
        { type: "Binding", index: 16, offset: 8 },
        { type: "Binding", index: 18, offset: 12 }
      ]);
    });

    it("(1, 0) -> (1, 1)", function() {
      traceData.loops[1].counter = 1;
      traceData.updateVisibleEvents();
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 9, offset: 0 },
        { type: "Binding", index: 13, offset: 2 },
        { type: "Binding", index: 14, offset: 4 },
        { type: "Binding", index: 16, offset: 8 },
        { type: "Binding", index: 18, offset: 12 }
      ]);
    });
  });

  describe("Test increase counter", function() {
    let traceData = createTraceData();

    it("(0, 0) -> (0, 1)", function() {
      traceData.loops[1].counter = 1;
      traceData.updateVisibleEvents();
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 0, offset: 0 },
        { type: "Binding", index: 4, offset: 2 },
        { type: "Binding", index: 5, offset: 4 },
        { type: "Binding", index: 7, offset: 8 },
        { type: "Binding", index: 18, offset: 12 }
      ]);
    });

    it("(0, 0) -> (0, 1)", function() {
      traceData.loops[0].counter = 1;
      traceData.updateVisibleEvents();
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 9, offset: 0 },
        { type: "Binding", index: 13, offset: 2 },
        { type: "Binding", index: 14, offset: 4 },
        { type: "Binding", index: 16, offset: 8 },
        { type: "Binding", index: 18, offset: 12 }
      ]);
    });
  });

  describe("Test decrease counter", function() {
    let traceData = createTraceData();
    traceData.loops[0].counter = 1;
    traceData.loops[1].counter = 1;
    traceData.updateVisibleEvents();

    it("(1, 1) -> (0, 1)", function() {
      traceData.loops[0].counter = 0;
      traceData.updateVisibleEvents();
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 0, offset: 0 },
        { type: "Binding", index: 4, offset: 2 },
        { type: "Binding", index: 5, offset: 4 },
        { type: "Binding", index: 7, offset: 8 },
        { type: "Binding", index: 18, offset: 12 }
      ]);
    });

    it("(0, 1) -> (0, 0)", function() {
      traceData.loops[1].counter = 0;
      traceData.updateVisibleEvents();
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 0, offset: 0 },
        { type: "Binding", index: 1, offset: 2 },
        { type: "Binding", index: 2, offset: 4 },
        { type: "Binding", index: 7, offset: 8 },
        { type: "Binding", index: 18, offset: 12 }
      ]);
    });
  });

  describe("Test decrease counter", function() {
    let traceData = createTraceData();
    traceData.loops[0].counter = 1;
    traceData.loops[1].counter = 1;
    traceData.updateVisibleEvents();

    it("(1, 1) -> (1, 0)", function() {
      traceData.loops[1].counter = 0;
      traceData.updateVisibleEvents();
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 9, offset: 0 },
        { type: "Binding", index: 10, offset: 2 },
        { type: "Binding", index: 11, offset: 4 },
        { type: "Binding", index: 16, offset: 8 },
        { type: "Binding", index: 18, offset: 12 }
      ]);
    });

    it("(1, 0) -> (0, 0)", function() {
      traceData.loops[0].counter = 0;
      traceData.updateVisibleEvents();
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 0, offset: 0 },
        { type: "Binding", index: 1, offset: 2 },
        { type: "Binding", index: 2, offset: 4 },
        { type: "Binding", index: 7, offset: 8 },
        { type: "Binding", index: 18, offset: 12 }
      ]);
    });
  });
});

describe("Test adjacent JumpBackToLoopStart", function() {
  function createTraceData() {
    return new TraceData({
      events: [
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
      ],
      loops: [new Loop(0, 8), new Loop(2, 6)],
      tracingResult: {}
    });
  }

  it("Test initial state", function() {
    const traceData = createTraceData();
    assertThat(
      traceData.visibleEventsArray,
      contains(
        { type: "Binding", index: 0, offset: 0 },
        { type: "Binding", index: 1, offset: 2 },
        { type: "Binding", index: 2, offset: 4 },
        { type: "Binding", index: 16, offset: 10 }
      )
    );

    assertThat(
      traceData.loops,
      contains(
        hasProperties({
          startOffset: 0,
          endOffset: 8,
          counter: 0,
          parent: undefined,
          _iterationStarts: new Map([
            ["0", 0],
            ["1", 8]
          ]),
          _iterationEnds: new Map([
            ["0", 7],
            ["1", 15]
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
          ]),
          _iterationEnds: new Map([
            ["0,0", 3],
            ["0,1", 6],
            ["1,0", 11],
            ["1,1", 14]
          ])
        })
      )
    );
  });
});

describe("Test loop with empty first iteration.", function() {
  function createTraceData() {
    return new TraceData({
      events: [
        { type: "Binding", index: 0, offset: 0 },
        { type: "JumpBackToLoopStart", index: 1, offset: 4 },
        { type: "Binding", index: 2, offset: 0 },
        { type: "Binding", index: 3, offset: 2 },
        { type: "JumpBackToLoopStart", index: 4, offset: 4 }
      ],
      loops: [new Loop(0, 4)],
      tracingResult: {}
    });
  }

  it("Test getVisibleEventsAndUpdateLoops", function() {
    const traceData = createTraceData();
    assertThat(
      traceData.visibleEventsArray,
      contains({ type: "Binding", index: 0, offset: 0 })
    );

    assertThat(
      traceData.loops,
      contains(
        hasProperties({
          startOffset: 0,
          endOffset: 4,
          counter: 0,
          parent: undefined,
          _iterationStarts: new Map([
            ["0", 0],
            ["1", 2]
          ]),
          _iterationEnds: new Map([
            ["0", 1],
            ["1", 4]
          ])
        })
      )
    );
  });

  it("0 -> 1", function() {
    let traceData = createTraceData();
    traceData.loops[0].counter = 1;
    traceData.updateVisibleEvents();
    assertThat(traceData.visibleEventsArray, [
      { type: "Binding", index: 2, offset: 0 },
      { type: "Binding", index: 3, offset: 2 }
    ]);
  });
});
