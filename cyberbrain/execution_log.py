from __future__ import annotations

import dis
from copy import deepcopy
from dis import Instruction
from types import FrameType
from typing import Union

from crayons import yellow, cyan

from .basis import Mutation, Deletion, _dummy
from .utils import pprint
from .value_stack import ValueStack


class Logger:
    """Execution logger."""

    def __init__(self, frame, debug_mode=False):
        self.instructions = {
            instr.offset: instr for instr in dis.get_instructions(frame.f_code)
        }
        # Skips CALL_METHOD and POP_TOP so that scanning starts after tracer.init().
        self.execution_start_index = frame.f_lasti + 4
        self.next_jump_location = None
        self.value_stack = ValueStack()
        self.changes: list[Union[Mutation, Deletion]] = []
        self.debug_mode = debug_mode

    def detect_changes(self, frame: FrameType):
        """Prints names whose values changed since this function is called last time.

        This function scans through instructions in the frame the logger belongs to,
        starting from the last_i recorded last time, and stops before the current
        last_i. It looks for instructions that are intended to mutate a variable,
        like "STORE_NAME" and "STORE_ATTR", and prints them.
        """
        last_i = frame.f_lasti

        # Why do we care about jump?
        #
        # Because you don't want to scan the instructions that were *not* executed.
        # So if the next instruction can potentially lead to a jump, we record the
        # jump target(bytecode offset). Now, next instruction comes, if the offset
        # matches the jump target, we know a jump just happened, and we move the
        # execution_start_index to where it should be, which is the jump target.
        # No need to scan instructions and find changes in this case, because jump
        # instruction won't cause any mutation.
        #
        # Note that jump instruction can also update the value stack, so we need to call
        # _log_changed_value to keep the stack in correct state. We do this when we
        # found the coming instruction matches the recorded jump location, because at
        # this point we know that previous instruction must be the instruction that
        # leads to the jump. Here by "previous" we mean the instruction at previous
        # "execution_start_index".
        #
        # Example
        #
        #   if a:
        #       x = 1
        #
        # Instructions
        #
        # 1           0 LOAD_NAME                0 (a)
        #             2 POP_JUMP_IF_FALSE        8      <----- ⓵
        #
        # 2           4 LOAD_CONST               0 (1)  <----- ⓶
        #             6 STORE_NAME               1 (x)
        #       >>    8 LOAD_CONST               1 (None) <--- ⓷
        #            10 RETURN_VALUE
        #
        # ⓵: last_i is 2, we assign last_i to execution_start_index, so it's also 2.
        #     instr.opcode `POP_JUMP_IF_FALSE` is in dis.hasjabs, so we record
        #     next_jump_location = 8
        #
        # ⓶: If `a` evaluates to true, code comes here, and we update the value stack
        #     with POP_JUMP_IF_FALSE.
        #
        # ⓷: If `a` evaluates to false, code comes here. Since
        #    last_i == next_jump_location == 8, we enter the if clause.
        #    The first thing we do in the if clause is to call _log_changed_value with
        #    the instruction at execution_start_index. The value is 2, and points to
        #    POP_JUMP_IF_FALSE, so we update the value stack with POP_JUMP_IF_FALSE.
        #    Next, we update execution_start_index normally.
        #
        # As explained above, with jump handling:
        # - The stack change caused by jump instruction is always taken care of.
        # - Skipped instructions are skipped (in this case, LOAD_CONST and STORE_NAME).
        if last_i == self.next_jump_location:
            self._log_changed_value(
                frame, self.instructions[self.execution_start_index], jumped=True
            )
            self.execution_start_index = last_i
            self._record_jump_location_if_exists(self.instructions[last_i])
            return

        for i in range(self.execution_start_index, last_i, 2):
            self._log_changed_value(frame, self.instructions[i])

        self._record_jump_location_if_exists(self.instructions[last_i])
        self.execution_start_index = last_i

    def _log_changed_value(self, frame: FrameType, instr: Instruction, jumped=False):
        """Logs changed values by the given instruction, if any."""
        # print(instr)
        # For now I'll deepcopy the mutated value, I don't know if there's a better way.
        # Maybe... https://github.com/seperman/deepdiff/issues/44
        change = self.value_stack.emit_change_and_update_stack(instr, jumped)
        if change:
            if isinstance(change, Mutation):
                change.value = self._deepcopy_from_frame(frame, change.target)
            self.changes.append(change)

        if self.debug_mode:
            pprint(
                f"{cyan('Executed instruction')} at line {frame.f_lineno}:",
                instr,
                f"{yellow('Current stack:')}",
                self.value_stack.stack,
            )

    def _record_jump_location_if_exists(self, instr: Instruction):
        if instr.opcode in dis.hasjrel:
            self.next_jump_location = instr.offset + 2 + instr.arg
        elif instr.opcode in dis.hasjabs:
            self.next_jump_location = instr.arg
        else:
            self.next_jump_location = None

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

        # There are certain things you can't copy, like module.
        try:
            return deepcopy(value)
        except TypeError:
            return repr(value)
