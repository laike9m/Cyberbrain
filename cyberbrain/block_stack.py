from enum import Enum


class BlockType(Enum):
    SETUP_FINALLY = 1
    SETUP_EXCEPT = 2
    SETUP_LOOP = 3
    EXCEPT_HANDLER = 4


class Block:
    opname_to_b_type = {
        "BREAK_LOOP": {BlockType.SETUP_LOOP},
        "POP_BLOCK": {BlockType.SETUP_LOOP, BlockType.SETUP_FINALLY},
        "POP_EXCEPT": {BlockType.SETUP_EXCEPT, BlockType.SETUP_FINALLY},
        "END_FINALLY": {BlockType.SETUP_FINALLY},
    }

    def __init__(self, b_level: int, b_type: BlockType, start: int, end: int):
        """
        Args:
            b_level: The # of elements that were on the value stack when this block was
            created.
            b_type: The type of block.
            start: Start bytecode offset of this block.
            end: End bytecode offset of this block, inclusive.
        """
        self.b_level = b_level
        self.b_type = b_type
        self.start = start
        self.end = end


class BlockStack:
    """Class that simulates a frame's block stack.
    Why do we need a block stack? Because we need to do block unwinding. An example:
    for x in range(2):
        break  # BREAK_LOOP (3.7)
      1           0 SETUP_LOOP              18 (to 20)
                  2 LOAD_NAME                0 (range)
                  4 LOAD_CONST               0 (2)
                  6 CALL_FUNCTION            1
                  8 GET_ITER
            >>   10 FOR_ITER                 6 (to 18)
                 12 STORE_NAME               1 (x)
      2          14 BREAK_LOOP
                 16 JUMP_ABSOLUTE           10
            >>   18 POP_BLOCK
            >>   20 LOAD_CONST               1 (None)
                 22 RETURN_VALUE
    GET_ITER pushes an iterator to TOS, which is kept during the loop. Normally, when
    the iterator is exhausted, it is popped from value stack. However, when we break
    the loop and jump to the next line, the iterator is left on the stack. CPython uses
    block unwinding(https://git.io/JfU3I) to clean up the stack and keep it in correct
    state. We need to do the same, which requires recording the created block stack and
    its b_level. b_level is a bad name, it actually means how many elements were on the
    value stack when this block was created. We need to clean up elements that are on
    top of b_level.
    """

    def __init__(self):
        self.stack = []

    def push(self, block: Block):
        self.stack.append(block)

    def pop(self):
        return self.stack.pop()

    @property
    def tos(self) -> Block:
        return self.stack[-1]

    def is_empty(self):
        return len(self.stack) == 0
