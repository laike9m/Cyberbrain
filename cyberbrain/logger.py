from __future__ import annotations

import dis
from dis import Instruction
from types import FrameType
from typing import Optional

from crayons import yellow, cyan

from . import utils
from .frame import Frame
from .frame_tree import FrameTree
from .utils import pprint, computed_gotos_enabled, shorten_path

_implicit_jump_ops = {"BREAK_LOOP", "RAISE_VARARGS", "END_FINALLY"}


class FrameLogger:
    """Logger for a frame."""

    def __init__(self, frame: FrameType, debug_mode=False):
        self.frame = Frame(
            # For testing, only stores the basename so it's separator agnostic.
            shorten_path(frame.f_code.co_filename, 1 if utils.run_in_test() else 3),
            self._map_bytecode_offset_to_lineno(frame),
        )
        FrameTree.add_frame(frame.f_code.co_name, self.frame)
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
        self.jump_detector = JumpDetector(
            instructions=self.instructions, debug_mode=debug_mode
        )
        self.debug_mode = debug_mode
        del frame

    def _map_bytecode_offset_to_lineno(self, frame) -> dict[int, int]:
        """Maps bytecode offset to lineno in file.

        Note that the lineno may not be accurate for multi-line statements. If we find
        this to be blocking, we might need to use a Range to represent lineno.
        """
        mapping = dict(dis.findlinestarts(frame.f_code))
        frame_byte_count = len(frame.f_code.co_code)
        for offset, lineno in mapping.copy().items():
            while offset <= frame_byte_count:
                offset += 2
                if offset in mapping:
                    break
                mapping[offset] = lineno

        del frame
        return mapping

    def update(self, frame: FrameType):
        """Prints names whose values changed since this function is called last time.

        This function scans through instructions in the frame the logger belongs to,
        starting from the last_i recorded last time, and stops before the current
        last_i. It looks for instructions that are intended to mutate a variable,
        like "STORE_NAME" and "STORE_ATTR", and prints them.
        """
        last_i = frame.f_lasti
        # print(f"{last_i=}, {frame=}")

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
            jumped, jump_location = self.jump_detector.detects_jump(instr, last_i)
            self.instr_pointer = jump_location if jumped else self.instr_pointer + 2
            self._debug_log(
                f"{cyan('Executed instruction')} at line {frame.f_lineno}:", instr
            )
            self.frame.log_events(frame, instr, jumped)
            self._debug_log(f"{yellow('Current stack:')}", self.frame.value_stack.stack)
            if self.instr_pointer >= last_i:
                break

        # Log InitialValue events that's relevant to the line that's about to be
        # executed, this way we record the value before it's (potentially) modified.
        self.frame.log_initial_value_events(frame, self.instructions[last_i])
        del frame

    def _debug_log(self, *msg, condition=True):
        if self.debug_mode and condition:
            pprint(*msg)


class JumpDetector:
    """Detects jump behavior."""

    COMPUTED_GOTOS_ENABLED = computed_gotos_enabled()

    PREDICT_MAP = {"FOR_ITER": "POP_BLOCK"}  # TODO: Add more.

    def __init__(self, instructions: dict[int, Instruction], debug_mode):
        self.instructions = instructions
        self.debug_mode = debug_mode

    def detects_jump(self, instr: Instruction, last_i) -> (bool, Optional[int]):
        """
        Returns: (whether jump occurred, jumped-to location)
        """
        jump_location = None

        if instr.opname in _implicit_jump_ops:
            jump_location = last_i  # For implicit_jump_ops, assume it's last_i.
        elif instr.opcode in dis.hasjrel:
            jump_location = instr.offset + 2 + instr.arg
        elif instr.opcode in dis.hasjabs:
            jump_location = instr.arg
        else:
            return False, jump_location

        computed_last_i = jump_location
        if not self.COMPUTED_GOTOS_ENABLED:
            # Here we assume that PREDICT happens at most once. I'm not sure if this
            # is always true. If it's not, we can modify the code.
            # Example:
            #              16 GET_ITER
            #         >>   18 FOR_ITER                 4 (to 24)
            #              20 STORE_FAST               1 (x)
            #   5          22 JUMP_ABSOLUTE           18
            #         >>   24 POP_BLOCK
            #   7     >>   26 SETUP_LOOP              22 (to 50)
            #
            # `PREDICT(POP_BLOCK)` exists in FOR_ITER's handler.
            # With COMPUTED_GOTOS, PREDICT is a noop, last_i is 24.
            # Without COMPUTED_GOTOS, PREDICT causes last_i to not update for POP_BLOCK,
            # so last_i is 26.
            opname_next = self.instructions[jump_location].opname
            if opname_next == self.PREDICT_MAP.get(instr.opname):
                print("Found PREDICT!!")
                computed_last_i += 2

        if computed_last_i == last_i:
            self._debug_log(f"Jumped to instruction at offset: {jump_location}")
            return True, jump_location

        return False, jump_location

    # TODO: Remove duplication.
    def _debug_log(self, *msg, condition=True):
        if self.debug_mode and condition:
            pprint(*msg)
