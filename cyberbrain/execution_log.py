import dis
import inspect

from copy import deepcopy
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
        self.mutations = []

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
        # print(instr)
        # fmt: off
        # For now I'll deepcopy mutated value, I don't know if there's a better way...
        # https://github.com/seperman/deepdiff/issues/183
        match(
            instr.opname,
            "STORE_NAME", lambda _:
                self.mutations.append(
                    Mutation(instr.argval, deepcopy(frame.f_locals[instr.argval]))),
            "STORE_ATTR", lambda _:
                self.mutations.append(
                    Mutation(self._tos, deepcopy(
                        self._get_value_in_frame(frame, self._tos)))),
            _, lambda x: _
        )
        self.value_stack.handle_instruction(instr)
        # fmt: on

    def _record_jump_location_if_exists(self, instr: Instruction):
        if instr.opcode in dis.hasjrel:
            self.next_jump_location = instr.offset + 2 + instr.arg
        elif instr.opcode in dis.hasjabs:
            self.next_jump_location = instr.arg
        else:
            self.next_jump_location = None

    @staticmethod
    def _get_value_in_frame(frame, name):
        """Given a frame and a name(identifier) saw in this frame, returns its value.

        I'm not 100% sure if this will always return the correct value. If we find a
        case where it returns the wrong value due to name collisions, we can modify
        code and store names with their scopes, like (a, local), (b, global).

        Once we have a frame class, we might move this method there.
        """
        if name in frame.f_locals:
            return frame.f_locals[name]
        elif name in frame.f_globals:
            return frame.f_globals[name]

        return frame.f_builtins[name]

    @property
    def _tos(self):
        return self.value_stack.tos()


def create_logger(frame):
    # Right now there's only a single frame(global). We should create an logger for each
    # frame.
    return Logger(frame=frame)
