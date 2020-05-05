from __future__ import annotations

from collections import defaultdict

from .basis import Event, InitialValue

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
            CheckPoint(events_pointer=defaultdict(lambda: _INITIAL_STATE))
        ]

    def knows(self, name) -> bool:
        return name in self.events

    def add_new_event(self, event: Event):
        assert event.target
        if self.events[event.target] and isinstance(event, InitialValue):
            # Make sure InitialValue is added at most once.
            return
        self.events[event.target].append(event)

        # Creates a new checkpoint.
        new_events_pointer = self.checkpoints[-1].events_pointer.copy()
        new_events_pointer[event.target] += 1
        self.checkpoints.append(CheckPoint(events_pointer=new_events_pointer))

    def latest_value_of(self, name):
        """Returns the latest value of an identifier."""
        if name not in events:
            raise AttributeError(f"'{name}' does not exist in frame state.")
        raise NotImplementedError


class CheckPoint:
    """Represents a frame's state at a certain moment."""

    __slots__ = ["events_pointer", "location"]

    def __init__(self, events_pointer, location=None):
        self.location = location  # TODO: record location.
        self.events_pointer: dict[str, int] = events_pointer
