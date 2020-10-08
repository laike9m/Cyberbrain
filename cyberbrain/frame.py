from __future__ import annotations

from collections import defaultdict
from dis import Instruction
from types import FrameType
from typing import Any

from . import value_stack, utils
from .basis import (
    Event,
    InitialValue,
    Binding,
    Mutation,
    Deletion,
    Return,
    EventType,
    Symbol,
    Loop,
    JumpBackToLoopStart,
)

_INITIAL_STATE = -1

Identifier = str  # Just a type alias to make annotations more expressive.


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

    Whether we still need identifier_to_events is yet to be decided.
    """

    def __init__(self, filename, frame_name, offset_to_lineno):
        # ################### Frame attribute ####################
        self.filename = filename
        self.frame_name = frame_name
        # For now, use frame name as frame id. Eventually this should be a unique uuid.
        self.frame_id = frame_name
        self.offset_to_lineno = offset_to_lineno

        self.value_stack = value_stack.create_value_stack()

        # ################### Frame state ####################
        self.events: list[Event] = []
        self.identifier_to_events: dict[Identifier, list[Event]] = _EventsDict(list)
        self.snapshots: list[Snapshot] = [
            # The initial state, where pointer points to zero for every identifier.
            Snapshot(events_pointer=defaultdict(lambda: _INITIAL_STATE))
        ]
        self._latest_snapshot = self.snapshots[0]
        self.loops: dict[int, Loop] = {}  # Maps loop start to loop.

        # ################### Relevant frames ####################
        # Frame that generated this frame. Could be empty if this frame is the outermost
        # frame.
        self.parent: Optional[Frame] = None
        # Frames derived from this frame.
        self.children: list[Frame] = []

    @property
    def latest_snapshot(self):
        return self._latest_snapshot

    def log_return_event(self, frame: FrameType, value: Any):
        # There should be one and only one item left on the stack before return.
        assert self.value_stack.stack_level == 1
        returned_obj = self.value_stack._pop()
        self.events.append(
            Return(
                value=utils.to_json(value),
                repr=utils.get_repr(value),
                lineno=self.offset_to_lineno[frame.f_lasti],
                filename=self.filename,
                offset=frame.f_lasti,
                sources=set(utils.flatten(returned_obj)),
                index=len(self.events),
            )
        )

    def log_initial_value_events(self, frame: FrameType, instr: Instruction):
        # We must use instr.argrepr instead of instr.argval. Example:
        # x = "hello"
        # Instruction(opname='LOAD_CONST', argval='hello', argrepr="'hello'")
        # Note argval is 'hello', which can collide with identifier names in frame.
        target: str = instr.argrepr
        try:
            value = utils.get_value_from_frame(target, frame)
        except AssertionError:
            # The target name may not yet exist in the frame.
            value = None

        if utils.should_ignore_event(target=target, value=value, frame=frame):
            return

        # Logs InitialValue event if it hasn't been recorded yet.
        if utils.name_exist_in_frame(target, frame) and not self._knows(target):
            value = utils.get_value_from_frame(target, frame)
            self._add_new_event(
                InitialValue(
                    target=Symbol(target),
                    value=utils.to_json(value),
                    repr=utils.get_repr(value),
                    lineno=self.offset_to_lineno[instr.offset],
                    filename=self.filename,
                    offset=instr.offset,
                )
            )

    def log_events(self, frame: FrameType, instr: Instruction, jumped: bool = False):
        """Logs changed values by the given instruction, if any."""
        event_info = self.value_stack.emit_event_and_update_stack(
            instr=instr, frame=frame, jumped=jumped, snapshot=self.latest_snapshot
        )
        if not event_info:
            return

        target: Symbol = event_info.target

        if target and target == Symbol("random"):
            print(event_info)

        if event_info.type is EventType.Mutation:
            value = utils.get_value_from_frame(target.name, frame)
            json = utils.to_json(value)
            if self._latest_value_of(target.name) == json:
                return

            self._add_new_event(
                Mutation(
                    target=target,
                    value=json,
                    repr=utils.get_repr(value),
                    filename=self.filename,
                    lineno=self.offset_to_lineno[instr.offset],
                    sources=event_info.sources,
                    offset=instr.offset,
                )
            )
        elif event_info.type is EventType.Binding:
            value = utils.get_value_from_frame(target.name, frame)
            self._add_new_event(
                Binding(
                    target=target,
                    value=utils.to_json(value),
                    repr=utils.get_repr(value),
                    sources=event_info.sources,
                    filename=self.filename,
                    lineno=self.offset_to_lineno[instr.offset],
                    offset=instr.offset,
                )
            )
        elif event_info.type is EventType.Deletion:
            self._add_new_event(
                Deletion(
                    target=target,
                    filename=self.filename,
                    lineno=self.offset_to_lineno[instr.offset],
                    offset=instr.offset,
                )
            )
        elif event_info.type is EventType.JumpBackToLoopStart:
            loop_start = event_info.jump_target
            self.events.append(
                JumpBackToLoopStart(
                    filename=self.filename,
                    lineno=self.offset_to_lineno[instr.offset],
                    offset=instr.offset,
                    index=len(self.events),
                    jump_target=loop_start,
                )
            )
            if loop_start in self.loops:
                self.loops[loop_start].end_offset = max(
                    self.loops[loop_start].end_offset, instr.offset
                )
            else:
                self.loops[loop_start] = Loop(
                    start_offset=loop_start,
                    end_offset=instr.offset,
                    start_lineno=self.offset_to_lineno[loop_start],
                )

    def _add_new_event(self, event: Event):
        target = event.target.name
        assert not (
            self.identifier_to_events[target] and isinstance(event, InitialValue)
        ), "InitialValue shouldn't be added twice"
        self.identifier_to_events[target].append(event)
        event.index = len(self.events)
        self.events.append(event)

        # Creates a new snapshot by incrementing the target index.
        new_events_pointer = self.snapshots[-1].events_pointer.copy()
        new_events_pointer[target] += 1
        new_snapshot = Snapshot(events_pointer=new_events_pointer)
        self._latest_snapshot = new_snapshot
        self.snapshots.append(new_snapshot)

        # If event is a mutation, updates relevant snapshots in value stack.
        if isinstance(event, Mutation):
            self.value_stack.update_snapshot(event.target.name, self.latest_snapshot)

    def _knows(self, name: str) -> bool:
        return name in self.identifier_to_events

    def _latest_value_of(self, name: str) -> Any:
        """Returns the latest value of an identifier.

        This method is *only* used during the logging process.
        TODO: What if the last event is a Deletion?
        """
        if not self._knows(name):
            raise AttributeError(f"'{name}' does not exist in frame.")

        return self.identifier_to_events[name][-1].value


class Snapshot:
    """Represents a frame's state at a certain moment.

    Given an event, Snapshot can help you find other variable's value at the same
    point of program execution.
    e.g. What's `b`'s value when `a` is set to 1
    """

    # TODO: Snapshot should contain, but not keyed by code location, because code
    #  location can duplicate.

    __slots__ = ["events_pointer", "location"]

    def __init__(self, events_pointer, location=None):
        self.location = location
        self.events_pointer: dict[str, int] = events_pointer

    def __repr__(self):
        return repr(self.events_pointer)
