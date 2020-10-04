from __future__ import annotations

from collections import defaultdict
from dis import Instruction
from types import FrameType
from typing import Any

from deepdiff import DeepDiff, Delta

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
                value=value,  # TODO: deepcopy
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
            value, value_repr = utils.deepcopy_value_from_frame(target, frame)
            self._add_new_event(
                InitialValue(
                    target=Symbol(target),
                    repr=value_repr,
                    value=value,
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

        # TODO: For mutation, add the mutated object as a source.
        if event_info.type is EventType.Mutation:
            value = utils.get_value_from_frame(target.name, frame)
            diff = DeepDiff(self._latest_value_of(target), value)
            if diff != {}:
                # noinspection PyArgumentList
                self._add_new_event(
                    Mutation(
                        target=target,
                        repr=utils.get_repr(value),
                        filename=self.filename,
                        lineno=self.offset_to_lineno[instr.offset],
                        delta=Delta(diff=diff),
                        sources=event_info.sources,
                        offset=instr.offset,
                    )
                )
        elif event_info.type is EventType.Binding:
            value, value_repr = utils.deepcopy_value_from_frame(target.name, frame)
            self._add_new_event(
                Binding(
                    target=target,
                    value=value,
                    repr=value_repr,
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

    def _latest_value_of(self, symbol: Symbol) -> Any:
        """Returns the latest value of an identifier.

        This method is *only* used during the logging process.
        """
        name = symbol.name
        if name not in self.identifier_to_events:
            raise AttributeError(f"'{name}' does not exist in frame.")

        relevant_events = self.identifier_to_events[name]
        assert type(relevant_events[0]) in {InitialValue, Binding}

        if isinstance(relevant_events[-1], Binding):
            return relevant_events[-1].value

        value = relevant_events[0].value  # initial value
        for event in relevant_events[1:]:
            assert type(event) in {Binding, Mutation}, repr(event)
            if isinstance(event, Binding):
                value = event.value
            elif isinstance(event, Mutation):
                value += event.delta

        return value

    @property
    def accumulated_events(self) -> list[Event]:
        """
        It modifies the original events, but should be fine.

        Now that FrameState only stores delta for Mutation event, if we need to know
        the value after a certain Mutation event (like in tests), the value has to be
        re-calculated. This method serves this purpose. Other events are kept unchanged.

        e.g.

        raw events:
            Binding(value=[]), Mutation(delta="append 1")

        Returned accumulated events:
            Binding(value=[]), Mutation(delta="append 1", value=[1])

        TODO: If this method was called before, return self.events directly.
        """
        latest_events: dict[Identifier, Event] = {}
        for event in self.events:
            if not hasattr(event, "target"):
                continue
            if isinstance(event, Mutation):
                event.value = latest_events[event.target.name].value + event.delta
            latest_events[event.target.name] = event

        return self.events


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
