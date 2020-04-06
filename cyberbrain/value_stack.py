"""A self maintained value stack."""

import dis
import types

from .basis import _dummy


class ValueStackException(Exception):
    pass


class ValueStack:
    def __init__(self):
        self.stack = []

    def tos(self):
        try:
            return stack[-1]
        except IndexError:
            ValueStackException("Value stack should have tos but is empty.")

    def _push(self, value):
        self.stack.append(value)

    def _pop(self):
        try:
            return self.stack.pop()
        except IndexError:
            ValueStackException("Value stack should have tos but is empty.")

    def handle_instruction(self, instr: dis.Instruction):
        getattr(self, f"_handle_{instr.opname}")(instr)

    def _handle_LOAD_CONST(self, instr):
        # For instructions like LOAD_CONST, we just need a placeholder on the stack.
        self._push(_dummy)

    def _handle_STORE_NAME(self, instr):
        self._pop()

    def _handle_LOAD_NAME(self, instr):
        # Note that we never store the actual rvalue, just name.
        self._push(instr.argrepr)

    def _handle_RETURN_VALUE(self, instr):
        self._pop()

    def _handle_LOAD_METHOD(self, instr):
        self._pop()

    def _handle_BUILD_TUPLE(self, instr):
        self._handle_BUILD_LIST(instr)

    def _handle_BUILD_LIST(self, instr):
        for _ in range(instr.arg):
            self._pop()
        self._push(_dummy)
