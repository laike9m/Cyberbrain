from __future__ import annotations

from collections import defaultdict
from copy import copy
from typing import Any

from .basis import Event, InitialValue, Creation, Mutation, Deletion

_INITIAL_STATE = 0


class _EventsDict(defaultdict):
    def __contains__(self, name):
        events = self[name]
        if not events:
            return False

        if isinstance(events[-1], Deletion):
            # If last event is a deletion, the name should be considered non-existent.
            return False

        return True


class Frame:
    """Stores frame state events and checkpoints.

    Two major functionalities this class provide:
    1. Tells the value of an identifier given a code location.
    2. Easier back tracing.

    TODO: corner cases to be handled:
        - delete, then create again
    """

    def __init__(self):
        self.raw_events: dict[str, list[Event]] = _EventsDict(list)
        # Creates a checkpoint to represent the initial frame state, where pointer
        # points to zero for every identifier.
        self.checkpoints: list[CheckPoint] = [
            CheckPoint(events_pointer=defaultdict(lambda: _INITIAL_STATE))
        ]
        # Frame that generated this frame. Could be empty if this frame is the outermost
        # frame.
        self.parent: Optional[Frame] = None
        # Frames derived from this frame.
        self.children: list[Frame] = []

    def add_new_event(self, event: Event):
        assert event.target
        if self.raw_events[event.target] and isinstance(event, InitialValue):
            # Make sure InitialValue is added at most once.
            return
        self.raw_events[event.target].append(event)

        # Creates a new checkpoint.
        new_events_pointer = self.checkpoints[-1].events_pointer.copy()
        new_events_pointer[event.target] += 1
        self.checkpoints.append(CheckPoint(events_pointer=new_events_pointer))

    def knows(self, name: str) -> bool:
        return name in self.raw_events

    def latest_value_of(self, name: str) -> Any:
        """Returns the latest value of an identifier.

        This method is *only* used during the logging process.
        """
        if name not in self.raw_events:
            raise AttributeError(f"'{name}' does not exist in frame.")

        relevant_events = self.raw_events[name]
        assert type(relevant_events[0]) in {InitialValue, Creation}

        value = relevant_events[0].value  # initial value
        for mutation in relevant_events[1:]:
            assert type(mutation) is Mutation, repr(mutation)
            value += mutation.delta

        return value

    @property
    def accumulated_events(self):
        """Returns events with accumulated value.

        Now that FrameState only stores delta for Mutation event, if we need to know
        the value after a certain mutation (like in tests), the value has to be
        re-calculated. This method does exactly that. Other events keep unchanged.

        e.g.

        raw events:
            {'a': [Creation(value=[]), Mutation(delta="append 1")]

        Returned accumulated events:
            {'a': [Creation(value=[]), Mutation(delta="append 1", value=[1])]
        """
        result: dict[str, list[Event]] = defaultdict(list)
        for name, raw_events in self.raw_events.items():
            for raw_event in raw_events:
                if not isinstance(raw_event, Mutation):
                    result[name].append(raw_event)
                    continue
                event = copy(raw_event)
                event.value = result[name][-1].value + raw_event.delta
                result[name].append(event)

        return result


class CheckPoint:
    """Represents a frame's state at a certain moment."""

    # TODO: checkpoints should contain, but not keyed by code location, because code
    #  location can duplicate.

    __slots__ = ["events_pointer", "location"]

    def __init__(self, events_pointer, location=None):
        self.location = location
        self.events_pointer: dict[str, int] = events_pointer
