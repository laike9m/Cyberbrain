"""Some basic data structures used throughout the project."""

from dataclasses import dataclass
from typing import Any

_dummy = object()


@dataclass
class Mutation:
    target: str
    value: Any
    source: Any = None  # Source can be empty, like a = 1

    def __eq__(self, other):
        if isinstance(other, Mutation):
            return (self.target, self.value, self.source) == (
                other.target,
                other.value,
                other.source,
            )
        if isinstance(other, dict):
            return (self.target, self.value, self.source) == (
                other["target"],
                other["value"],
                other["source"],
            )
        return False
