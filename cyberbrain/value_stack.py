"""A self maintained value stack."""

import dis
import types

from .basis import _dummy


class ValueStackException(Exception):
    pass


class ValueStack:
    """This class simulates the intepreter's value stack."""

    def __init__(self):
        self.stack = []

    def tos(self):
        try:
            return self.stack[-1]
        except IndexError:
            ValueStackException("Value stack should have tos but is empty.")

    def _push(self, value):
        self.stack.append(value)

    def _pop(self):
        try:
            return self.stack.pop()
        except IndexError:
            ValueStackException("Value stack should have tos but is empty.")

    def _replace_tos(self, new_value):
        self._pop()
        self._push(new_value)

    def handle_instruction(self, instr: dis.Instruction):
        getattr(self, f"_{instr.opname}_handler")(instr)

    def _LOAD_CONST_handler(self, instr):
        # For instructions like LOAD_CONST, we just need a placeholder on the stack.
        self._push(_dummy)

    def _STORE_NAME_handler(self, instr):
        self._pop()

    def _LOAD_NAME_handler(self, instr):
        # Note that we never store the actual rvalue, just name.
        self._push(instr.argrepr)

    def _RETURN_VALUE_handler(self, instr):
        self._pop()

    def _LOAD_METHOD_handler(self, instr):
        self._pop()

    def _BUILD_TUPLE_handler(self, instr):
        self._handle_BUILD_LIST(instr)

    def _BUILD_LIST_handler(self, instr):
        for _ in range(instr.arg):
            self._pop()
        self._push(_dummy)

    def _LOAD_ATTR_handler(self, instr):
        """Change the behavior of LOAD_ATTR.

        The effect of LOAD_ATTR is: Replaces TOS with getattr(TOS, co_names[namei]).
        However, this will make backtracing hard, because it eliminates the information
        about the source object, where the attribute originates from.

        Example: a = b.x
              0 LOAD_NAME                0 (b)
              2 LOAD_ATTR                1 (x)
              4 STORE_NAME               2 (a)
              6 LOAD_CONST               0 (None)
              8 RETURN_VALUE

        Tos was 'b' (in our customized version of LOAD_NAME), then LOAD_ATTR replaces it
        with the value of `b.x`. This caused 'a' to lost from the value stack, but we
        need it to know that b caused a to change.

        Example: a.x.y = 1
              0 LOAD_CONST               0 (1)
              2 LOAD_NAME                0 (a)
              4 LOAD_ATTR                1 (x)
              6 STORE_ATTR               2 (y)
              8 LOAD_CONST               1 (None)
             10 RETURN_VALUE

        Tos was 'a', then LOAD_ATTR replaces it with the value of `a.x`. This caused 'a'
        to lost from the value stack, but we need it to know that a's value has changed.

        In both examples, we can see what the value of the attribute doesn't mean much
        to us, so it's fine if we don't store it. But the "name" of the source object is
        vital, so we need to keep it. Thus, the handler just does nothing.
        """
        pass

    def _STORE_ATTR_handler(self, instr):
        return self.tos()

    def _CALL_METHOD_handler(self, instr):
        """
        For now we assume no argument is passed, so tos is replaced with return value,
        thus a noop.
        TODO: Implement full behaviors of CALL_METHOD.
        """
        pass

    def _POP_TOP_handler(self, instr):
        self._pop()
