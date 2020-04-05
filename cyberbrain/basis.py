"""Some basic data structures used throughout the project."""

from dataclasses import dataclass
from typing import Any


@dataclass
class Mutation:
    target: str
    value: Any

    def __eq__(self, other):
        if isinstance(other, Mutation):
            return (self.target, self.value) == (other.target, other.value)
        if isinstance(other, tuple):
            return (self.target, self.value) == other
        return False
