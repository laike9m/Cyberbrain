from enum import Enum


class BlockType(Enum):
    SETUP_FINALLY = 1
    SETUP_EXCEPT = 2
    SETUP_LOOP = 3
    EXCEPT_HANDLER = 4


class Block:
    def __init__(self, b_level: int, b_type: BlockType):
        """
        Args:
            b_level: The # of elements that were on the value stack when this block was
            created.
            b_type: Type of this block.
        """
        self.b_level = b_level
        self.b_type = b_type

    def __repr__(self):
        return f"Block(b_level={self.b_level}, b_type={self.b_type})"


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
        print(f"Pushed block stack: {block}")
        self.stack.append(block)
        print(f"Current block stack: {self.stack}")

    def pop(self):
        print(f"Popped block stack: {self.tos}")
        print(f"Current block stack: {self.stack[:-1]}")
        return self.stack.pop()

    @property
    def tos(self) -> Block:
        return self.stack[-1]

    def is_not_empty(self):
        return len(self.stack) > 0
