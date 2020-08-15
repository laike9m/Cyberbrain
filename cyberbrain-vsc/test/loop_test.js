import pkg from "chai";

import {
  generateInitialNodesAndKnots,
  generateNodeUpdate,
} from "../src/loop.js";

const { assert } = pkg;

describe("generateInitialNodesAndKnots tests", function () {
  it("should return empty", function () {
    assert.deepEqual(generateInitialNodesAndKnots(), [[], []]);
  });
});

describe("generateNodeUpdate tests", function () {
  it("should return empty", function () {
    assert.deepEqual(generateNodeUpdate(), [[], []]);
  });
});
