from __future__ import annotations

from collections import defaultdict

from .basis import Change

_INITIAL_STATE = 0


class FrameState:
    """Stores frame state changes and checkpoints.

    Two major functionalities this class provide:
    1. Tells the value of an identifier given a code location.
    2. Easier back tracing.
    """

    def __init__(self):
        self.changes: dict[str, list[Change]] = defaultdict(list)
        # Creates a checkpoint to represent the initial frame state, where pointer
        # points to zero for every identifier.
        self.checkpoints: list[CheckPoint] = [
            CheckPoint(changes_pointer=defaultdict(lambda: _INITIAL_STATE))]

    def add_new_change(self, new_change: Change):
        # Adds new change to changes, including initial state.
        assert new_change.target
        # if not self.changes[new_change.target]:
        #     assert type(new_change) in {Inheritance, Creation}
        self.changes[new_change.target].append(new_change)

        # Creates a new checkpoint.
        new_changes_pointer = self.checkpoints[-1].changes_pointer.copy()
        new_changes_pointer[new_change.target] += 1
        self.checkpoints.append(CheckPoint(changes_pointer=new_changes_pointer))

    def latest_value_of(self, name):
        """Returns the latest value of an identifier."""
        if name not in changes:
            raise AttributeError(f"'{name}' does not exist in frame state.")
        raise NotImplementedError


class CheckPoint:
    """Represents a frame's state at a certain moment."""

    __slots__ = ['changes_pointer', 'location']

    def __init__(self, changes_pointer, location=None):
        self.location = location  # TODO: record location.
        self.changes_pointer: dict[str, int] = changes_pointer
