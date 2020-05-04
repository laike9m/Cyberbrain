from __future__ import annotations

from collections import defaultdict

from .basis import Event

_INITIAL_STATE = 0


class FrameState:
    """Stores frame state events and checkpoints.

    Two major functionalities this class provide:
    1. Tells the value of an identifier given a code location.
    2. Easier back tracing.
    """

    def __init__(self):
        self.events: dict[str, list[Event]] = defaultdict(list)
        # Creates a checkpoint to represent the initial frame state, where pointer
        # points to zero for every identifier.
        self.checkpoints: list[CheckPoint] = [
            CheckPoint(events_pointer=defaultdict(lambda: _INITIAL_STATE))]

    def add_new_change(self, new_change: Event):
        # Adds new change to events, including initial state.
        assert new_change.target
        # if not self.events[new_change.target]:
        #     assert type(new_change) in {Inheritance, Creation}
        self.events[new_change.target].append(new_change)

        # Creates a new checkpoint.
        new_events_pointer = self.checkpoints[-1].events_pointer.copy()
        new_events_pointer[new_change.target] += 1
        self.checkpoints.append(CheckPoint(events_pointer=new_events_pointer))

    def latest_value_of(self, name):
        """Returns the latest value of an identifier."""
        if name not in events:
            raise AttributeError(f"'{name}' does not exist in frame state.")
        raise NotImplementedError


class CheckPoint:
    """Represents a frame's state at a certain moment."""

    __slots__ = ['events_pointer', 'location']

    def __init__(self, events_pointer, location=None):
        self.location = location  # TODO: record location.
        self.events_pointer: dict[str, int] = events_pointer
