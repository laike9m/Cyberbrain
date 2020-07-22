"""Some basic data structures used throughout the project."""

from __future__ import annotations

import os
from collections import defaultdict
from typing import Any

import attr
import shortuuid
from deepdiff import Delta

from . import utils

_dummy = object()


class UUIDGenerator:

    counter = defaultdict(int)

    @classmethod
    def generate_uuid(cls) -> str:
        """Generates a 8-char uuid."""
        if utils.run_as_test():
            # When run in test, generates predictable uids so we can assert on them.
            test_name = (
                # When executed in global scope, $PYTEST_CURRENT_TEST is not set.
                os.environ.get("PYTEST_CURRENT_TEST", "global")
                .split(":")[-1]
                .split(" ")[0]
            )
            count = cls.counter[test_name]
            cls.counter[test_name] += 1
            return f"{test_name}:{count}"
        else:
            assert False, "This branch shouldn't be called."
            return shortuuid.uuid()[:8]


@attr.s(auto_attribs=True)
class Event:
    target: str
    # TODO: remove the default values
    lineno: int = attr.ib(default=0)
    filename: str = attr.ib(eq=False, default=0)
    uid: string = attr.ib(factory=UUIDGenerator.generate_uuid, eq=False, repr=False)


@attr.s(auto_attribs=True)
class InitialValue(Event):
    """Identifiers come from other places, or simply exist before tracking starts.

    e.g. Global variables, passed in arguments.

    This also counts:

    a = 1
    cyberbrain.init()
    a = 2  --> emit two events: first InitialValue, then Mutation.
    cyberbrain.init()

    Compared to this one, which only emits a Creation event.

    cyberbrain.init()
    a = 2  # 'a' doesn't exist before.
    cyberbrain.init()
    '"""

    # kw_only is required to make inheritance work
    # see https://github.com/python-attrs/attrs/issues/38
    value: Any = attr.ib(kw_only=True)
    # TODO: Add sources if it's a function parameter.


@attr.s(auto_attribs=True)
class Creation(Event):
    """An identifiers is created in the current frame."""

    value: Any = attr.ib(kw_only=True)
    sources: set[str] = set()  # Source can be empty, like a = 1


# For now, we don't want to compare delta, so disable auto-generated __eq__.
@attr.s(auto_attribs=True, eq=False)
class Mutation(Event):
    """An identifier is mutated."""

    # Represents the diffs from before and after the mutation.
    delta: Delta = Delta({})

    sources: set[str] = set()  # Source can be empty, like a = 1

    # Value is optional. It is set on demand during testing. Other code MUSTN'T rely
    # on it.
    value: Any = _dummy

    def __eq__(self, other: Mutation):
        return (self.target, self.value, self.sources, self.lineno) == (
            other.target,
            other.value,
            other.sources,
            other.lineno,
        )


@attr.s(auto_attribs=True, eq=False)
class Deletion(Event):
    """An identifiers is deleted."""

    def __eq__(self, other: Deletion):
        print(self, other)
        return (self.target, self.lineno) == (other.target, other.lineno)


class Symbol:
    """An identifier at a certain point of program execution.

    Symbols are specific to a frame.
    """

    def __init__(self, name: str, snapshot=None):
        self.name = name
        self.snapshot = snapshot

    def __eq__(self, other):
        return self.name == other.name
