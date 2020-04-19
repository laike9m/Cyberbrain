class BlockStack:
    """Class that simulates a frame's block stack.

    Why do we need a block stack? Because we need to do block unwinding. An example:

    for y in range(2):
        break  # BREAK_LOOP (3.7)

      1           0 SETUP_LOOP              18 (to 20)
                  2 LOAD_NAME                0 (range)
                  4 LOAD_CONST               0 (2)
                  6 CALL_FUNCTION            1
                  8 GET_ITER
            >>   10 FOR_ITER                 6 (to 18)
                 12 STORE_NAME               1 (y)

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

    def push(self, b_level):
        self.stack.append(_Block(b_level))

    def pop(self):
        return self.stack.pop()


class _Block:
    def __init__(self, b_level):
        self.b_level = b_level
