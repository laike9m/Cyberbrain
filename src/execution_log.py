import dis
import inspect

from dis import Instruction


class Logger:
    """Execution logger."""

    def __init__(self, frame):
        self.instructions = {
            instr.offset: instr
            for instr in dis.get_instructions(inspect.getsource(frame))
        }
        self.execution_start_index = 0
        self.next_jump_location = None

    def record_jump_location_if_exists(self, instr: Instruction):
        if instr.opcode in dis.hasjrel:
            self.next_jump_location = instr.offset + 2 + instr.arg
        elif instr.opcode in dis.hasjabs:
            self.next_jump_location = instr.arg
        else:
            self.next_jump_location = None

    def detect_chanages(self, last_i: int):
        """Print names whose values are changed by the given series of bytecode."""

        print(f"Ops Executed, last i is {last_i}")

        if last_i == self.next_jump_location:
            # Jump instruction doesn't change any var's value, so we can skip.
            self.execution_start_index = last_i
            self.record_jump_location_if_exists(self.instructions[last_i])
            return

        for i in range(self.execution_start_index, last_i, 2):
            instr = self.instructions[i]
            if instr.opname.startswith("STORE") or instr.opname.startswith("LOAD_CONST"):
                # For STORE_ATTR, we can look at previous instructions and find
                # LOAD_NAME and LOAD_ATTR.
                print(self.instructions[i])
                print("\n")

        self.record_jump_location_if_exists(self.instructions[last_i])
        self.execution_start_index = last_i
