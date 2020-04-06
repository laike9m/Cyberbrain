import dis
import inspect

from dis import Instruction
from types import FrameType

from pampy import match, _

from .basis import Mutation
from .value_stack import ValueStack


class Logger:
    """Execution logger."""

    def __init__(self, frame):
        self.instructions = {
            instr.offset: instr
            for instr in dis.get_instructions(inspect.getsource(frame))
        }
        # Skips CALL_METHOD and POP_TOP so that scanning starts after tracer.init().
        self.execution_start_index = frame.f_lasti + 4
        self.next_jump_location = None
        self.value_stack = ValueStack()
        self.mutations = []  # TODO: record mutations, like set 'a' to xxx.

    def detect_chanages(self, frame: FrameType):
        """Prints names whose values changed since this function is called last time.

        This function scans through instructions in the frame the logger belongs to,
        starting from the last_i recorded last time, and stops before the current
        last_i. It looks for instructions that are intended to mutate a variable,
        like "STORE_NAME" and "STORE_ATTR", and prints them.
        """
        last_i = frame.f_lasti
        # print(f"detect_chanages, last i is {last_i}")

        # Why do we care about jump?
        #
        # Because you don't want to scan the instructions that were *not* executed.
        # So if the next instruction can potentially lead to a jump, we record the
        # jump target(bytecode offset). Now, next instruction comes, if the offset
        # matches the jump target, we know a jump just happened, and we move the
        # execution_start_index to what it should be, which is the jump target.
        # No scanning happens in this case, because jump instruction doesn't change
        # any var's value.
        if last_i == self.next_jump_location:
            self.execution_start_index = last_i
            self._record_jump_location_if_exists(self.instructions[last_i])
            return

        for i in range(self.execution_start_index, last_i, 2):
            self._log_changed_value(frame, self.instructions[i])

        self._record_jump_location_if_exists(self.instructions[last_i])
        self.execution_start_index = last_i

    def _log_changed_value(self, frame: FrameType, instr: Instruction):
        """Logs changed values by the given instruction, if any."""
        # fmt: off
        match(
            instr.opname,
            "STORE_NAME", lambda _:
                self.mutations.append(
                    Mutation(target=instr.argval, value=frame.f_locals[instr.argval])),
            _, lambda x: _
        )
        self.value_stack.handle_instruction(instr)
        # fmt: on
        # For STORE_ATTR, we can look at previous instructions to find
        # LOAD_NAME and LOAD_ATTR.
        # loop backward, find the first instr that's not LOAD_ATTR,

    def _record_jump_location_if_exists(self, instr: Instruction):
        if instr.opcode in dis.hasjrel:
            self.next_jump_location = instr.offset + 2 + instr.arg
        elif instr.opcode in dis.hasjabs:
            self.next_jump_location = instr.arg
        else:
            self.next_jump_location = None


def create_logger(frame):
    # Right now there's only a single frame(global). We should create an logger for each
    # frame.
    return Logger(frame=frame)
