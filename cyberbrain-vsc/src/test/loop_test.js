/*
If we need to migrate tests to TS, see:
https://dev.to/daniel_werner/testing-typescript-with-mocha-and-chai-5cl8
 */

// Need to set isDevMode to avoid ReferenceError: isDevMode is not defined
// https://stackoverflow.com/a/59243202/2142577
const global = (0, eval)("this");
global.isDevMode = false;

import hamjest from "hamjest";

import { Loop, TraceData } from "../trace_data.js";

const { assertThat, contains, hasProperty, hasProperties } = hamjest;

let cl = console.log;

describe("Test nested loops", function() {
  function createTraceData() {
    return new TraceData({
      events: [
        { type: "Binding", index: 0, offset: 0, lineno: 1 },
        { type: "Binding", index: 1, offset: 2, lineno: 2 },
        { type: "Binding", index: 2, offset: 4, lineno: 3 },
        { type: "JumpBackToLoopStart", index: 3, offset: 6, lineno: 4 },
        { type: "Binding", index: 4, offset: 2, lineno: 2 },
        { type: "Binding", index: 5, offset: 4, lineno: 3 },
        { type: "JumpBackToLoopStart", index: 6, offset: 6, lineno: 4 },
        { type: "Binding", index: 7, offset: 8, lineno: 5 },
        { type: "JumpBackToLoopStart", index: 8, offset: 10, lineno: 6 },
        { type: "Binding", index: 9, offset: 0, lineno: 1 },
        { type: "Binding", index: 10, offset: 2, lineno: 2 },
        { type: "Binding", index: 11, offset: 4, lineno: 3 },
        { type: "JumpBackToLoopStart", index: 12, offset: 6, lineno: 4 },
        { type: "Binding", index: 13, offset: 2, lineno: 2 },
        { type: "Binding", index: 14, offset: 4, lineno: 3 },
        { type: "JumpBackToLoopStart", index: 15, offset: 6, lineno: 4 },
        { type: "Binding", index: 16, offset: 8, lineno: 5 },
        { type: "JumpBackToLoopStart", index: 17, offset: 10, lineno: 6 },
        { type: "Binding", index: 18, offset: 12, lineno: 7 }
      ],
      loops: [new Loop(0, 10, 0, 6), new Loop(2, 6, 1, 4)],
      tracingResult: {}
    });
  }

  it("Test loop initialization", function() {
    const traceData = createTraceData();
    assertThat(
      traceData.visibleEventsArray,
      contains(
        { type: "Binding", index: 0, offset: 0, lineno: 1 },
        { type: "Binding", index: 1, offset: 2, lineno: 2 },
        { type: "Binding", index: 2, offset: 4, lineno: 3 },
        { type: "Binding", index: 7, offset: 8, lineno: 5 },
        { type: "Binding", index: 18, offset: 12, lineno: 7 }
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
      traceData.updateVisibleEvents(traceData.loops[0]);
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 9, offset: 0, lineno: 1 },
        { type: "Binding", index: 10, offset: 2, lineno: 2 },
        { type: "Binding", index: 11, offset: 4, lineno: 3 },
        { type: "Binding", index: 16, offset: 8, lineno: 5 },
        { type: "Binding", index: 18, offset: 12, lineno: 7 }
      ]);
    });

    it("(1, 0) -> (1, 1)", function() {
      traceData.loops[1].counter = 1;
      traceData.updateVisibleEvents(traceData.loops[1]);
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 9, offset: 0, lineno: 1 },
        { type: "Binding", index: 13, offset: 2, lineno: 2 },
        { type: "Binding", index: 14, offset: 4, lineno: 3 },
        { type: "Binding", index: 16, offset: 8, lineno: 5 },
        { type: "Binding", index: 18, offset: 12, lineno: 7 }
      ]);
    });
  });

  describe("Test increase counter", function() {
    let traceData = createTraceData();

    it("(0, 0) -> (0, 1)", function() {
      traceData.loops[1].counter = 1;
      traceData.updateVisibleEvents(traceData.loops[1]);
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 0, offset: 0, lineno: 1 },
        { type: "Binding", index: 4, offset: 2, lineno: 2 },
        { type: "Binding", index: 5, offset: 4, lineno: 3 },
        { type: "Binding", index: 7, offset: 8, lineno: 5 },
        { type: "Binding", index: 18, offset: 12, lineno: 7 }
      ]);
    });

    it("(0, 0) -> (0, 1)", function() {
      traceData.loops[0].counter = 1;
      traceData.updateVisibleEvents(traceData.loops[0]);
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 9, offset: 0, lineno: 1 },
        { type: "Binding", index: 13, offset: 2, lineno: 2 },
        { type: "Binding", index: 14, offset: 4, lineno: 3 },
        { type: "Binding", index: 16, offset: 8, lineno: 5 },
        { type: "Binding", index: 18, offset: 12, lineno: 7 }
      ]);
    });
  });

  describe("Test decrease counter", function() {
    let traceData = createTraceData();
    traceData.loops[0].counter = 1;
    traceData.updateVisibleEvents(traceData.loops[0]);
    traceData.loops[1].counter = 1;
    traceData.updateVisibleEvents(traceData.loops[1]);

    it("(1, 1) -> (0, 1)", function() {
      traceData.loops[0].counter = 0;
      traceData.updateVisibleEvents(traceData.loops[0]);
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 0, offset: 0, lineno: 1 },
        { type: "Binding", index: 4, offset: 2, lineno: 2 },
        { type: "Binding", index: 5, offset: 4, lineno: 3 },
        { type: "Binding", index: 7, offset: 8, lineno: 5 },
        { type: "Binding", index: 18, offset: 12, lineno: 7 }
      ]);
    });

    it("(0, 1) -> (0, 0)", function() {
      traceData.loops[1].counter = 0;
      traceData.updateVisibleEvents(traceData.loops[1]);
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 0, offset: 0, lineno: 1 },
        { type: "Binding", index: 1, offset: 2, lineno: 2 },
        { type: "Binding", index: 2, offset: 4, lineno: 3 },
        { type: "Binding", index: 7, offset: 8, lineno: 5 },
        { type: "Binding", index: 18, offset: 12, lineno: 7 }
      ]);
    });
  });

  describe("Test decrease counter", function() {
    let traceData = createTraceData();
    traceData.loops[0].counter = 1;
    traceData.updateVisibleEvents(traceData.loops[0]);
    traceData.loops[1].counter = 1;
    traceData.updateVisibleEvents(traceData.loops[1]);

    it("(1, 1) -> (1, 0)", function() {
      traceData.loops[1].counter = 0;
      traceData.updateVisibleEvents(traceData.loops[1]);
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 9, offset: 0, lineno: 1 },
        { type: "Binding", index: 10, offset: 2, lineno: 2 },
        { type: "Binding", index: 11, offset: 4, lineno: 3 },
        { type: "Binding", index: 16, offset: 8, lineno: 5 },
        { type: "Binding", index: 18, offset: 12, lineno: 7 }
      ]);
    });

    it("(1, 0) -> (0, 0)", function() {
      traceData.loops[0].counter = 0;
      traceData.updateVisibleEvents(traceData.loops[0]);
      assertThat(traceData.visibleEventsArray, [
        { type: "Binding", index: 0, offset: 0, lineno: 1 },
        { type: "Binding", index: 1, offset: 2, lineno: 2 },
        { type: "Binding", index: 2, offset: 4, lineno: 3 },
        { type: "Binding", index: 7, offset: 8, lineno: 5 },
        { type: "Binding", index: 18, offset: 12, lineno: 7 }
      ]);
    });
  });
});

describe("Test adjacent JumpBackToLoopStart", function() {
  function createTraceData() {
    return new TraceData({
      events: [
        { type: "Binding", index: 0, offset: 0, lineno: 1 },
        { type: "Binding", index: 1, offset: 2, lineno: 2 },
        { type: "Binding", index: 2, offset: 4, lineno: 3 },
        { type: "JumpBackToLoopStart", index: 3, offset: 6, lineno: 4 },
        { type: "Binding", index: 4, offset: 2, lineno: 2 },
        { type: "Binding", index: 5, offset: 4, lineno: 3 },
        { type: "JumpBackToLoopStart", index: 6, offset: 6, lineno: 4 },
        { type: "JumpBackToLoopStart", index: 7, offset: 8, lineno: 5 },
        { type: "Binding", index: 8, offset: 0, lineno: 1 },
        { type: "Binding", index: 9, offset: 2, lineno: 2 },
        { type: "Binding", index: 10, offset: 4, lineno: 3 },
        { type: "JumpBackToLoopStart", index: 11, offset: 6, lineno: 4 },
        { type: "Binding", index: 12, offset: 2, lineno: 2 },
        { type: "Binding", index: 13, offset: 4, lineno: 3 },
        { type: "JumpBackToLoopStart", index: 14, offset: 6, lineno: 4 },
        { type: "JumpBackToLoopStart", index: 15, offset: 8, lineno: 5 }
      ],
      loops: [new Loop(0, 8, 1, 5), new Loop(2, 6, 2, 4)],
      tracingResult: {}
    });
  }

  it("Test initial state", function() {
    const traceData = createTraceData();
    assertThat(
      traceData.visibleEventsArray,
      contains(
        { type: "Binding", index: 0, offset: 0, lineno: 1 },
        { type: "Binding", index: 1, offset: 2, lineno: 2 },
        { type: "Binding", index: 2, offset: 4, lineno: 3 }
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
        { type: "Binding", index: 0, offset: 0, lineno: 1 },
        { type: "JumpBackToLoopStart", index: 1, offset: 4, lineno: 3 },
        { type: "Binding", index: 2, offset: 0, lineno: 1 },
        { type: "Binding", index: 3, offset: 2, lineno: 2 },
        { type: "JumpBackToLoopStart", index: 4, offset: 4, lineno: 3 }
      ],
      loops: [new Loop(0, 4, 1, 3)],
      tracingResult: {}
    });
  }

  it("Test getVisibleEventsAndUpdateLoops", function() {
    const traceData = createTraceData();
    assertThat(
      traceData.visibleEventsArray,
      contains({ type: "Binding", index: 0, offset: 0, lineno: 1 })
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
    traceData.updateVisibleEvents(traceData.loops[0]);
    assertThat(traceData.visibleEventsArray, [
      { type: "Binding", index: 2, offset: 0, lineno: 1 },
      { type: "Binding", index: 3, offset: 2, lineno: 2 }
    ]);
  });
});

describe("Test empty inner loop.", function() {
  function createTraceData() {
    return new TraceData({
      events: [
        { type: "Binding", index: 0, offset: 0, lineno: 1 },
        { type: "Binding", index: 1, offset: 2, lineno: 2 },
        { type: "JumpBackToLoopStart", index: 2, offset: 4, lineno: 3 },
        { type: "JumpBackToLoopStart", index: 3, offset: 6, lineno: 4 },
        { type: "Binding", index: 4, offset: 0, lineno: 1 }, // Skipped the inner loop.
        { type: "JumpBackToLoopStart", index: 6, offset: 6, lineno: 4 }
      ],
      loops: [new Loop(0, 6, 1, 4), new Loop(2, 4, 2, 3)],
      tracingResult: {}
    });
  }

  it("Test initialize loops", function() {
    const traceData = createTraceData();
    assertThat(
      traceData.loops,
      contains(
        hasProperties({
          startOffset: 0,
          endOffset: 6,
          _iterationStarts: new Map([
            ["0", 0],
            ["1", 4]
          ]),
          _iterationEnds: new Map([
            ["0", 3],
            ["1", 6]
          ])
        }),
        hasProperties({
          startOffset: 2,
          endOffset: 4,
          _iterationStarts: new Map([["0,0", 1]]),
          _iterationEnds: new Map([["0,0", 2]])
        })
      )
    );
  });
});

describe("Test early return from loop.", function() {
  function createTraceData() {
    return new TraceData({
      /*
      def f(a):  # 1 is passed in
        while True:
          b = a  # offset: 0
          if b == 2:
            return b # offset: 2
          else:
            a = 2  # offset: 4
       */
      events: [
        { type: "Binding", index: 0, offset: 0, lineno: 1, id: "0" }, // b = a
        { type: "Binding", index: 1, offset: 4, lineno: 3, id: "1" }, // a = 2
        {
          type: "JumpBackToLoopStart",
          index: 2,
          offset: 6,
          lineno: 4,
          id: "2"
        },
        { type: "Binding", index: 3, offset: 0, lineno: 1, id: "3" }, // b = a
        { type: "Return", index: 4, offset: 2, lineno: 2, id: "4" } // return b
      ],
      loops: [new Loop(0, 6, 1, 4)],
      tracingResult: { "3": ["1"], "4": ["3"] }
    });
  }
  let traceData = createTraceData();

  it("Test initialize loops", function() {
    assertThat(
      traceData.loops,
      contains(
        hasProperties({
          startOffset: 0,
          endOffset: 6,
          _iterationStarts: new Map([
            ["0", 0],
            ["1", 3]
          ]),
          _iterationEnds: new Map([
            ["0", 2],
            ["1", 4]
          ])
        })
      )
    );
  });

  it("0 -> 1", function() {
    traceData.loops[0].counter = 1;
    traceData.updateVisibleEvents(traceData.loops[0]);
    // Once we fixed #19, { type: "Binding", index: 1, offset: 4, lineno: 3, id: "1" }
    // should be visible because it is the source of a visible node:
    // { type: "Binding", index: 3, offset: 0, lineno: 1, id: "3" } which is "b = a".
    assertThat(traceData.visibleEventsArray, [
      { type: "Binding", index: 3, offset: 0, lineno: 1, id: "3" },
      { type: "Return", index: 4, offset: 2, lineno: 2, id: "4" }
    ]);
  });

  // Note that this operation should remove the "Return" node because it references
  // an invisible node { type: "Binding", index: 3, offset: 0, lineno: 1, id: "3" }
  it("1 -> 0", function() {
    traceData.loops[0].counter = 0;
    traceData.updateVisibleEvents(traceData.loops[0]);
    assertThat(traceData.visibleEventsArray, [
      { type: "Binding", index: 0, offset: 0, lineno: 1, id: "0" },
      { type: "Binding", index: 1, offset: 4, lineno: 3, id: "1" }
    ]);
  });
});

// Test case comes from https://github.com/laike9m/Cyberbrain/issues/47
// But it's actually verifying the bug in #108 has been fixed.
describe("Test issue47 self assignment.", function() {
  function createTraceData() {
    return new TraceData({
      /*
      def fib(n):  # Assuming n = 2
          a, b = 0, 1
          for _ in range(n):
              a, b = b, a + b
          return b
       */
      events: [
        { type: "Binding", index: 0, offset: 0, lineno: 1, id: "0" }, // a = 0
        { type: "Binding", index: 1, offset: 2, lineno: 2, id: "1" }, // b = 1
        { type: "Binding", index: 2, offset: 4, lineno: 3, id: "2" }, // a = b
        { type: "Binding", index: 3, offset: 6, lineno: 4, id: "3" }, // b = a + b
        {
          type: "JumpBackToLoopStart",
          index: 4,
          offset: 8,
          lineno: 5,
          id: "4"
        },
        { type: "Binding", index: 5, offset: 4, lineno: 3, id: "5" }, // a = b
        { type: "Binding", index: 6, offset: 6, lineno: 4, id: "6" }, // b = a + b
        { type: "Return", index: 7, offset: 10, lineno: 6, id: "7" } // return b
      ],
      loops: [new Loop(4, 8, 3, 5)],
      tracingResult: {
        "2": ["1"],
        "3": ["2", "1"],
        "5": ["3"],
        "6": ["5", "3"],
        "7": ["6"]
      }
    });
  }

  let traceData = createTraceData();

  it("Test initialize loops", function() {
    assertThat(
      traceData.loops,
      contains(
        hasProperties({
          startOffset: 4,
          endOffset: 8,
          _iterationStarts: new Map([
            ["0", 2],
            ["1", 5]
          ]),
          _iterationEnds: new Map([
            ["0", 4],
            ["1", 6]
          ])
        })
      )
    );
    assertThat(traceData.visibleEventsArray, [
      { type: "Binding", index: 0, offset: 0, lineno: 1, id: "0" }, // a = 0
      { type: "Binding", index: 1, offset: 2, lineno: 2, id: "1" }, // b = 1
      { type: "Binding", index: 2, offset: 4, lineno: 3, id: "2" }, // a = b
      { type: "Binding", index: 3, offset: 6, lineno: 4, id: "3" }, // b = a + b
      { type: "Return", index: 7, offset: 10, lineno: 6, id: "7" } // return b
    ]);
  });

  it("0 -> 1", function() {
    traceData.loops[0].counter = 1;
    traceData.updateVisibleEvents(traceData.loops[0]);
    assertThat(traceData.visibleEventsArray, [
      { type: "Binding", index: 0, offset: 0, lineno: 1, id: "0" }, // a = 0
      { type: "Binding", index: 1, offset: 2, lineno: 2, id: "1" }, // b = 1
      { type: "Binding", index: 5, offset: 4, lineno: 3, id: "5" }, // a = b
      { type: "Binding", index: 6, offset: 6, lineno: 4, id: "6" }, // b = a + b
      { type: "Return", index: 7, offset: 10, lineno: 6, id: "7" } // return b
    ]);
  });
});
