"""Some basic data structures used throughout the project."""

from __future__ import annotations

from typing import Any, Optional

import attr
import shortuuid
from deepdiff import Delta

_dummy = object()


# TODO: Event class should contain the location where the change happened.


@attr.s(auto_attribs=True)
class Event:
    target: str
    uid: string = attr.ib(factory=shortuuid.uuid, eq=False)


@attr.s(auto_attribs=True)
class InitialValue(Event):
    """Identifiers come from other places, or simply exist before tracking starts.

    e.g. Global variables, passed in arguments.

    This also counts:

    a = 1
    cyberbrain.init()
    a = 2  --> emit two events: first Inheritance, then Mutation.
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


# For now, we don't want to compare delta, so disable auto-generation of __eq__.
@attr.s(auto_attribs=True, eq=False)
class Mutation(Event):
    """An identifier is mutated."""

    # Represents the diffs from before and after the mutation.
    delta: Optional[Delta] = None

    sources: set[str] = set()  # Source can be empty, like a = 1

    # Value is optional. It is set on demand during testing. Other code MUSTN'T rely
    # on it.
    value: Any = _dummy

    def __eq__(self, other):
        if isinstance(other, Mutation):
            return (self.target, self.value, self.sources) == (
                other.target,
                other.value,
                other.sources,
            )
        if isinstance(other, dict):
            return (self.target, self.value, self.sources) == (
                other["target"],
                other["value"],
                other["sources"],
            )
        return False


@attr.s(auto_attribs=True, eq=False)
class Deletion(Event):
    """An identifiers is deleted."""

    def __eq__(self, other):
        if isinstance(other, Deletion):
            return self.target == other.target
        if isinstance(other, dict):
            return self.target == other["target"]
        return False
