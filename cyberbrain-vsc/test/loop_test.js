/*
If we need to migrate tests to TS, see:
https://dev.to/daniel_werner/testing-typescript-with-mocha-and-chai-5cl8
 */

import pkg from "chai";

import {
  generateNodeUpdate,
  getVisibleEventsAndUpdateKnots,
  Knot,
} from "../src/loop.js";

const { assert } = pkg;

describe("getVisibleEventsAndUpdateKnots tests", function () {
  it("Nested loop works", function () {
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
        type: "JumpBackToKnot",
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
        type: "JumpBackToKnot",
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
        type: "JumpBackToKnot",
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
        type: "JumpBackToKnot",
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
        type: "JumpBackToKnot",
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
        type: "JumpBackToKnot",
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
    let knots = new Map([
      [0, new Knot(0)],
      [2, new Knot(2)],
    ]); // Maps offset to knots.
    assert.deepEqual(getVisibleEventsAndUpdateKnots(events, knots), [
      { type: "Binding", index: 1, offset: 2 },
      { type: "Binding", index: 2, offset: 4 },
      { type: "JumpBackToKnot", index: 3, offset: 6, jump_target: 2 },
      { type: "Binding", index: 7, offset: 8 },
      { type: "JumpBackToKnot", index: 8, offset: 10, jump_target: 0 },
      { type: "Binding", index: 18, offset: 12 },
    ]);
    assert.deepEqual(
      knots,
      new Map([
        [0, { offset: 0, loopCounter: 0, iterationStarts: [0, 9] }],
        [2, { offset: 2, loopCounter: 0, iterationStarts: [1, 4, 10, 13] }],
      ])
    );
  });
});

describe("generateNodeUpdate tests", function () {
  it("should return empty", function () {
    assert.deepEqual(generateNodeUpdate(), [[], []]);
  });
});
