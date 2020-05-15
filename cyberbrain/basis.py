"""Some basic data structures used throughout the project."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeVar, Optional

from deepdiff import Delta

_dummy = object()


# TODO: Event class should contain the location where the change happened.


@dataclass
class InitialValue:
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

    target: str
    value: Any
    # TODO: Add sources if it's a function parameter.


@dataclass
class Creation:
    """An identifiers is created in the current frame."""

    target: str
    value: any
    sources: set[str] = field(default_factory=set)  # Source can be empty, like a = 1


@dataclass
class Mutation:
    """An identifier is mutated."""

    target: str

    # TODO: Use a regular class, and store pickled delta instead of a Delta object.
    #   Then use @property to return Delta(pickled_delta).
    # Represents the diffs from before and after the mutation.
    delta: Optional[Delta] = None

    sources: set[str] = field(default_factory=set)  # Source can be empty, like a = 1

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


@dataclass
class Deletion:
    """An identifiers is deleted."""

    target: str

    def __eq__(self, other):
        if isinstance(other, Deletion):
            return self.target == other.target
        if isinstance(other, dict):
            return self.target == other["target"]
        return False


Event = TypeVar("Event", InitialValue, Creation, Mutation, Deletion)
