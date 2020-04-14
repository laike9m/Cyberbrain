"""Some basic data structures used throughout the project."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_dummy = object()


@dataclass
class Mutation:
    target: str
    value: Any = _dummy

    sources: set[str] = field(default_factory=set)  # Source can be empty, like a = 1

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
    target: str

    def __eq__(self, other):
        if isinstance(other, Deletion):
            return self.target == other.target
        if isinstance(other, dict):
            return self.target == other["target"]
        return False
