from __future__ import annotations

import dis
from copy import deepcopy
from dis import Instruction
from types import FrameType

from crayons import yellow, cyan
from deepdiff import DeepDiff, Delta

from . import value_stack
from .basis import Mutation, Creation, InitialValue
from .frame_state import FrameState
from .utils import pprint
from .value_stack import EvaluationMode, AFTER_INSTR_EXECUTION, BEFORE_INSTR_EXECUTION

_implicit_jump_ops = {"BREAK_LOOP", "RAISE_VARARGS", "END_FINALLY"}


class Frame:
    """A call frame."""

    def __init__(self, frame, debug_mode=False):
        self.instructions = {
            instr.offset: instr for instr in dis.get_instructions(frame.f_code)
        }

        # tracer.init() contains the following instructions:
        #               0 LOAD_FAST                0 (tracer)
        #               2 LOAD_METHOD              0 (init)
        #               4 CALL_METHOD              0
        #               6 POP_TOP
        # However logger is initialized before executing CALL_METHOD, last_i is already
        # at 4. This will make value stack don't have enough elements. So we need to
        # move the instr_pointer back to LOAD_FAST, and make sure LOAD_FAST and
        # LOAD_METHOD are scanned, so that value stack can be in correct state.
        self.instr_pointer = frame.f_lasti - 4
        self.value_stack = value_stack.create_value_stack()
        self.frame_state: FrameState = FrameState()
        self.debug_mode = debug_mode
        del frame

    def update(self, frame: FrameType):
        """Prints names whose values changed since this function is called last time.

        This function scans through instructions in the frame the logger belongs to,
        starting from the last_i recorded last time, and stops before the current
        last_i. It looks for instructions that are intended to mutate a variable,
        like "STORE_NAME" and "STORE_ATTR", and prints them.
        """
        last_i = frame.f_lasti
        print(f"last_i is {last_i}")

        # Why do we care about jump?
        #
        # Because we only want to handle the instructions that were actually executed.
        # In most cases where there is no jump, scanning from instr_pointer to last_i
        # is enough. Before instr_pointer hits last_i, the instruction scanned is the
        # the instruction executed.
        #
        # Things get more complicated when jump is involved. Generally speaking, jump
        # instructions complicate instruction scanning in two ways:
        #   - Instructions jumped over are between [instr_pointer, last_i], but were
        #     not executed, thus should be ignored;
        #   - If there was a jump backward (like `continue`), last_i will be smaller
        #     than instr_pointer.
        #
        # To solve the above issues, we rely on this fact (observation, to be exact):
        # frame.last_i is always updated after a jump (explicit or implicit, explained
        # later), and points to the destination of the jump.
        #
        # It is important to know that, due to the PREDICT(op) optimization, sometimes
        # last_i is not updated in time. So if last_i is p when this function is called,
        # next time it could be i+4 instead of i+2. However, this situation won't
        # happen:
        #   p:      jump instruction    <---- last_i
        #   p + 2:  other instruction
        #   p + 4:                      <---- new last_i
        # Because we know if a jump occurred, last_i will be updated in time, and this
        # function will be called. This can happen:
        #   p:      other instruction   <---- last_i
        #   p + 2:  jump instruction
        #   p + 4:                      <---- new last_i
        #
        # Now back the the solution. We still iterate from instr_pointer to last_i,
        # but we also check whether the scanned instruction is a jump that *happened*.
        # This is important, cause not all jump instruction lead to a jump, it's
        # conditional sometimes (e.g. POP_JUMP_IF_FALSE). Luckily, we know if a jump
        # just happened, last_i points to the jump destination. So we compare the jump
        # destination calculated from current instruction with last_i. If they match,
        # we know a jump has just happened, then we set instr_pointer to last_i.
        #
        # The solution is simple and easy to understand. However there are two cases
        # we need to consider.
        #
        # First is the aforementioned "jump backwards". We solve this by using a while
        # loop in stead of range(instr_pointer, last_i), and break the loop when
        # instr_pointer >= last_i. In this way, scanning can take place, and when a jump
        # backwards sets instr_pointer to last_i, the loop can break.
        #
        # Second is what I call "implicit jump". These instructions are not included in
        # `dis.hasjrel` or `dis.hasjabs`, but can change bytecode counter, including
        # "BREAK_LOOP", "RAISE_VARARGS", "END_FINALLY". Regardless of jump happened or
        # not, we set instr_pointer to last_i, because last_i == (instr_pointer + 2)
        # if jump didn't happen.

        while True:
            instr = self.instructions[self.instr_pointer]
            jumped = False

            if self._jump_occurred(instr, last_i):
                jumped = True
                self.instr_pointer = last_i
            else:
                self.instr_pointer += 2

            self._log_events(frame, instr, AFTER_INSTR_EXECUTION, jumped)
            if self.instr_pointer >= last_i:
                break

        # This is important. We need to log mutation/creation events before it actually
        # happens so that an identifier's original value is kept.
        self._log_events(frame, self.instructions[last_i], BEFORE_INSTR_EXECUTION)
        del frame

    def _log_events(
        self,
        frame: FrameType,
        instr: Instruction,
        evaluation_mode: EvaluationMode,
        jumped: bool = False,
    ):
        """Logs changed values by the given instruction, if any."""
        self._debug_log(
            f"{cyan('Executed instruction')} at line {frame.f_lineno}:",
            instr,
            condition=evaluation_mode is AFTER_INSTR_EXECUTION,
        )

        change = self.value_stack.emit_event_and_update_stack(
            instr=instr, frame=frame, evaluation_mode=evaluation_mode, jumped=jumped
        )
        if change:
            target = change.target
            if evaluation_mode is BEFORE_INSTR_EXECUTION:
                if self._name_exist_in_frame(change.target, frame):
                    self.frame_state.add_new_event(
                        InitialValue(
                            target=change.target,
                            value=self._deepcopy_value_from_frame(target, frame),
                        )
                    )

            if evaluation_mode is AFTER_INSTR_EXECUTION:
                if isinstance(change, Mutation):
                    if self.frame_state.knows(target):
                        # TODO: If event is a mutation, compare new value with old value
                        #  , discard event if target's value hasn't change.
                        #
                        # TODO: Use DeepDiff.to_delta_dump when possible. If an object
                        #  can't be pickled, and it should fall back to non-pickling.

                        # Note that we deepcopy the DeepDiff object, because DeepDiff
                        # object references the original object, which is stored in the
                        # Delta object. If we don't deepcopy, Delta is subject to change
                        # when the stored object is mutated from outside. But we want
                        # Delta object to be immutable, thus deepcopy is necessary.
                        #
                        # An alternative is to deepcopy the object sent to DeepDiff.
                        # However this usually comes with greater cost, because we need
                        # to copy the entire object, instead of the diff result, which
                        # is usually smaller.
                        change.delta = Delta(
                            diff=deepcopy(DeepDiff(
                                self.frame_state.latest_value_of(target),
                                self._get_value_from_frame(target, frame),
                            ))
                        )
                    else:
                        change = Creation(
                            target=target,
                            value=self._deepcopy_value_from_frame(target, frame),
                            sources=change.sources,
                        )
                        # TODO: Records the InitialValue of sources that frame state
                        #  don't know of.

                print(cyan(str(change)))
                self.frame_state.add_new_event(change)

        self._debug_log(
            f"{yellow('Current stack:')}",
            self.value_stack.stack,
            condition=evaluation_mode is AFTER_INSTR_EXECUTION,
        )
        del frame

    def _jump_occurred(self, instr: Instruction, last_i):
        if not any(
            [
                instr.opcode in dis.hasjrel,
                instr.opcode in dis.hasjabs,
                instr.opname in _implicit_jump_ops,
            ]
        ):
            return False

        jump_location = last_i  # For implicit_jump_ops, we assume it's last_i.
        if instr.opcode in dis.hasjrel:
            jump_location = instr.offset + 2 + instr.arg
        elif instr.opcode in dis.hasjabs:
            jump_location = instr.arg

        if jump_location == last_i:
            self._debug_log(f"Jumped to instruction at offset: {jump_location}")
            return True

    @classmethod
    def _deepcopy_value_from_frame(cls, name: str, frame):
        """Given a frame and a name(identifier) saw in this frame, returns its value.

        The value has to be deep copied to avoid being changed by code coming later.

        I'm not 100% sure if this will always return the correct value. If we find a
        case where it returns the wrong value due to name collisions, we can modify
        code and store names with their scopes, like (a, local), (b, global).

        Once we have a frame class, we might move this method there.
        """
        value = cls._get_value_from_frame(name, frame)
        del frame

        # There are certain things you can't copy, like module.
        try:
            return deepcopy(value)
        except TypeError:
            return repr(value)

    @classmethod
    def _get_value_from_frame(cls, name: str, frame):
        assert cls._name_exist_in_frame(name, frame)
        if name in frame.f_locals:
            value = frame.f_locals[name]
        elif name in frame.f_globals:
            value = frame.f_globals[name]
        else:
            value = frame.f_builtins[name]
        del frame
        return value

    @staticmethod
    def _name_exist_in_frame(name: str, frame) -> bool:
        return any(
            [name in frame.f_locals, name in frame.f_globals, name in frame.f_builtins]
        )

    def _debug_log(self, *msg, condition=True):
        if self.debug_mode and condition:
            pprint(*msg)
