"""Some basic data structures used throughout the project."""

from __future__ import annotations

import enum
import os
from collections import defaultdict
from typing import Any, TYPE_CHECKING

import attr
import shortuuid
from deepdiff import Delta

from . import utils

if TYPE_CHECKING:
    pass

_dummy = object()


class UUIDGenerator:

    counter = defaultdict(int)

    @classmethod
    def generate_uuid(cls) -> str:
        """Generates a 8-char uuid."""
        if utils.run_in_test():
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
            return shortuuid.uuid()[:8]


class EventType(enum.Enum):
    JumpBackToLoopStart = 0
    InitialValue = 1
    Binding = 2
    Mutation = 3
    Deletion = 4


@attr.s(auto_attribs=True)
class Event:
    lineno: int
    # offset and filename are always set, but we don't want to set them in tests, thus
    # giving them a default value.
    index: int = attr.ib(eq=False, default=0)
    offset: int = attr.ib(eq=False, default=0)
    filename: str = attr.ib(eq=False, default="")
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

    Compared to this one, which only emits a Binding event.

    cyberbrain.init()
    a = 2  # 'a' doesn't exist before.
    cyberbrain.init()
    '"""

    target: Symbol = attr.ib(kw_only=True)

    # kw_only is required to make inheritance work
    # see https://github.com/python-attrs/attrs/issues/38
    value: Any = attr.ib(kw_only=True)
    # TODO: Add sources if it's a function parameter.


@attr.s(auto_attribs=True)
class Binding(Event):
    """An identifier is bound to an value.

    A brief explanation of Python's data model.
    http://foobarnbaz.com/2012/07/08/understanding-python-variables/

    Roughly speaking, Binding happens when:
        - A new identifier is used for the first time
        - An identifier is re-assigned
    """

    target: Symbol = attr.ib(kw_only=True)
    value: Any = attr.ib(kw_only=True)
    sources: set[Symbol] = set()  # Source can be empty, like a = 1


# For now, we don't want to compare delta, so disable auto-generated __eq__.
@attr.s(auto_attribs=True, eq=False)
class Mutation(Event):
    """An identifier is mutated.

    Note the difference between Mutation and Binding.

        a = 0       # Binding
        a = 1       # Binding, not Mutation!!
        b = []      # Binding
        b.append(1) # Mutation
    """

    target: Symbol = attr.ib(kw_only=True)

    # Represents the diffs from before and after the mutation.
    delta: Delta = Delta({})

    sources: set[Symbol] = set()  # Source can be empty, like a = 1

    # Value is optional. It is set on demand during testing. Other code MUSTN'T rely
    # on it.
    value: Any = _dummy

    def __eq__(self, other: Mutation):
        return (
            isinstance(other, Mutation)
            and (
                self.target,
                self.value,
                self.sources,
                self.lineno,
            )
            == (other.target, other.value, other.sources, other.lineno)
        )


@attr.s(auto_attribs=True, eq=False)
class Deletion(Event):
    """An identifiers is deleted."""

    target: Symbol = attr.ib(kw_only=True)

    def __eq__(self, other: Deletion):
        return isinstance(other, Deletion) and (self.target, self.lineno) == (
            other.target,
            other.lineno,
        )


@attr.s(auto_attribs=True, eq=False)
class Return(Event):
    """Return from a callable.

    The return event does not have "target" attr because there isn't always one, e.g.
    return 1 + 2, return a if b else c
    """

    value: Any = attr.ib(kw_only=True)
    sources: set[Symbol] = set()

    def __eq__(self, other: Return):
        return isinstance(other, Return) and (self.value, self.sources) == (
            other.value,
            self.sources,
        )


@attr.s
class JumpBackToLoopStart(Event):
    jump_target: int = attr.ib(kw_only=True)


@attr.s
class Loop:
    start_offset: int = attr.ib(kw_only=True)
    end_offset: int = attr.ib(kw_only=True)
    start_lineno: int = attr.ib(kw_only=True)


"""
An edge case that is not handled:
x = a.b
x.foo = bar

a is also changed, but right now we won't be able to know it.
We need a Symbol class to handle this case, like: Symbol('x', references={'a'})

H: 其实我更多想的时，Symbol 可以引用别的 symbol
L: 引用别的 symbol 虽然或许可以让 backtracking 更简单，如果是引用所有相关 symbol 感觉有点滥用，引
   用一些局部（比如同一个 statement）的 symbol 应该是可以的
"""


class Symbol:
    """An identifier at a certain point of program execution.

    Symbols are specific to a frame. For symbols stored in value stack or representing a
    source, snapshot must be provided. For symbols only used for representing a target,
    snapshot can be omitted.
    """

    def __init__(self, name: str, snapshot=None):
        self.name = name
        self.snapshot = snapshot

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        """Test only"""
        return self.name == other.name

    def __repr__(self):
        return f"Symbol('{self.name}')"
