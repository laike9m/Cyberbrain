from __future__ import annotations

from dis import Instruction
from types import FrameType
from typing import Optional

from crayons import yellow, cyan

from . import utils
from .frame import Frame
from .utils import pprint, computed_gotos_enabled

_implicit_jump_ops = {"BREAK_LOOP", "CONTINUE_LOOP", "RAISE_VARARGS", "END_FINALLY"}

PREDICT_MAP = {
    "LIST_APPEND": {"JUMP_ABSOLUTE"},
    "SET_ADD": {"JUMP_ABSOLUTE"},
    "GET_ANEXT": {"LOAD_CONST"},
    "GET_AWAITABLE": {"LOAD_CONST"},
    "MAP_ADD": {"JUMP_ABSOLUTE"},
    "COMPARE_OP": {"POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE"},
    "GET_ITER": {"FOR_ITER", "CALL_FUNCTION"},
    "GET_YIELD_FROM_ITER": {"LOAD_CONST"},
    "FOR_ITER": {"STORE_FAST", "UNPACK_SEQUENCE", "POP_BLOCK"},
    "BEFORE_ASYNC_WITH": {"GET_AWAITABLE"},
    "WITH_CLEANUP_START": {"WITH_CLEANUP_FINISH"},
    "WITH_CLEANUP_FINISH": {"END_FINALLY"},
}

COMPUTED_GOTOS_ENABLED = computed_gotos_enabled()


class FrameLogger:
    """Logger for a frame."""

    def __init__(
        self,
        instructions: dict[int, Instruction],
        initial_instr_pointer: int,
        frame: Frame,
        debug_mode=False,
    ):
        self.instructions = instructions
        self.frame = frame
        self.instr_pointer = initial_instr_pointer
        self.jump_detector = JumpDetector(
            instructions=self.instructions, debug_mode=debug_mode
        )
        self.debug_mode = debug_mode

    def update(self, frame: FrameType):
        """Prints names whose values changed since this function is called last time.

        This function scans through instructions in the frame the logger belongs to,
        starting from the last_i recorded last time, and stops before the current
        last_i. It looks for instructions that are intended to mutate a variable,
        like "STORE_NAME" and "STORE_ATTR", and prints them.
        """
        last_i = frame.f_lasti
        if last_i == 0:  # Skips when no instruction has been executed.
            # Tracks possible initial value events of symbols in the first instruction.
            self.frame.log_initial_value_events(frame, self.instructions[last_i])
            return
        # print(f"last_i={last_i}, frame={frame}")

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
            _debug_log(
                self.debug_mode,
                (
                    f"{cyan('Executed instruction')} at line "
                    f"{self.frame.offset_to_lineno[instr.offset]}"
                ),
                instr,
            )
            self.frame.log_events(frame, instr, jumped)
            _debug_log(
                self.debug_mode,
                f"{yellow('Current stack:')}",
                self.frame.value_stack.stack,
            )

            # Taking the following code as an example.
            #     for i in range(2):
            #         if i == 1:
            #             break
            #
            #          16 GET_ITER
            #     >>   18 FOR_ITER                16 (to 34)
            #          20 STORE_FAST               2 (i)
            #
            #          22 LOAD_FAST                2 (i)
            #          24 LOAD_CONST               2 (1)
            #          26 COMPARE_OP               2 (==)
            #          28 POP_JUMP_IF_FALSE       18
            #
            # Without COMPUTED_GOTOS, when last_i is 26, it will execute two
            # instructions COMPARE_OP and POP_JUMP_IF_FALSE without ever updating
            # last_i to 28, this is because PREDICT(POP_JUMP_IF_FALSE) exists in
            # COMPARE_OP's handler.
            #
            # Assuming i = 0, and POP_JUMP_IF_FALSE jumps to loop start, resulting in
            # last_i = 18. If we do nothing, since
            #
            #   self.instr_pointer (28, after increase) > last_i (18)
            #
            # the while loop would break, and POP_JUMP_IF_FALSE will never be traversed.
            # Therefore we need to identify this and make sure to call "continue", to
            # be able to process the next jump instruction .
            if not COMPUTED_GOTOS_ENABLED:
                try:
                    # Note that instr_pointer has been increased already.
                    opname_next = self.instructions[self.instr_pointer].opname
                    if opname_next in PREDICT_MAP.get(instr.opname, {}):
                        print(f"Found PREDICT!! {instr.opname} -> {opname_next}")
                        continue
                except IndexError:
                    pass

            if self.instr_pointer >= last_i:
                break

        # Log InitialValue events that's relevant to the line that's about to be
        # executed, this way we record the value before it's (potentially) modified.
        self.frame.log_initial_value_events(frame, self.instructions[last_i])


class JumpDetector:
    """Detects jump behavior."""

    def __init__(self, instructions: dict[int, Instruction], debug_mode):
        self.instructions = instructions
        self.debug_mode = debug_mode

    def detects_jump(self, instr: Instruction, last_i) -> (bool, Optional[int]):
        """
        An instruction could have both implicit_jump_target and implicit_jump_target.
        e.g. CONTINUE_LOOP, when it's inside a `with` clause, there's an implicit
        jump to the following WITH_CLEANUP_START instruction.

        From observation, implicit jump instructions don't contain PREDICT. So we only
        process PREDICT if there's explicit_jump_target.
        TODO: Verify if this is always true.

        Returns: (whether jump occurred, jumped-to location)
        """

        explicit_jump_target = utils.get_jump_target_or_none(instr)
        implicit_jump_target = last_i if instr.opname in _implicit_jump_ops else None

        if not any([implicit_jump_target, explicit_jump_target]):
            return False, None

        computed_last_i = explicit_jump_target
        if not COMPUTED_GOTOS_ENABLED and explicit_jump_target is not None:
            # Here we assume that PREDICT happens at most once. I'm not sure if this
            # is always true. If not, we can modify the code.
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
            opname_next = self.instructions[explicit_jump_target].opname
            if opname_next in PREDICT_MAP.get(instr.opname, {}):
                _debug_log(
                    self.debug_mode,
                    f"Found PREDICT!! {instr.opname} -> {opname_next}",
                )
                computed_last_i += 2

        if computed_last_i == last_i:
            _debug_log(
                self.debug_mode,
                f"Jumped to instruction at offset: {explicit_jump_target}",
            )
            return True, explicit_jump_target
        elif implicit_jump_target:
            _debug_log(
                self.debug_mode,
                f"Jumped to instruction at offset: {implicit_jump_target}",
            )
            return True, implicit_jump_target

        return False, None


def _debug_log(debug_mode, *msg, condition=True):
    if debug_mode and condition:
        pprint(*msg)
