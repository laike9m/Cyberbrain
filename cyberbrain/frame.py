from __future__ import annotations

import dis
from copy import deepcopy
from dis import Instruction
from types import FrameType
from typing import Union

from crayons import yellow, cyan

from . import value_stack
from .basis import Mutation, Deletion, _dummy
from .utils import pprint

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
        self.changes: list[Union[Mutation, Deletion]] = []
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

            self._get_change(frame, instr, jumped)
            if self.instr_pointer >= last_i:
                del frame
                break

    def _debug_log(self, *msg):
        if self.debug_mode:
            pprint(*msg)

    def _get_change(self, frame: FrameType, instr: Instruction, jumped=False):
        """Logs changed values by the given instruction, if any."""
        self._debug_log(
            f"{cyan('Executed instruction')} at line {frame.f_lineno}:", instr
        )

        change = self.value_stack.emit_change_and_update_stack(instr, jumped, frame)
        if change:
            if isinstance(change, Mutation):
                # For now I'll deepcopy the mutated value, will replace it with
                # https://github.com/seperman/deepdiff/issues/44 once it's implemented.
                print(cyan(str(change)))
                change.value = self._deepcopy_from_frame(frame, change.target)
            self.changes.append(change)

        self._debug_log(f"{yellow('Current stack:')}", self.value_stack.stack)
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

    @staticmethod
    def _deepcopy_from_frame(frame, name: str):
        """Given a frame and a name(identifier) saw in this frame, returns its value.

        The value has to be deep copied to avoid being changed by code coming later.

        I'm not 100% sure if this will always return the correct value. If we find a
        case where it returns the wrong value due to name collisions, we can modify
        code and store names with their scopes, like (a, local), (b, global).

        Once we have a frame class, we might move this method there.
        """
        value = _dummy
        if name in frame.f_locals:
            value = frame.f_locals[name]
        elif name in frame.f_globals:
            value = frame.f_globals[name]
        else:
            value = frame.f_builtins[name]

        assert value is not _dummy
        del frame

        # There are certain things you can't copy, like module.
        try:
            return deepcopy(value)
        except TypeError:
            return repr(value)
