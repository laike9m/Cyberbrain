"""A self maintained value stack."""

import dis
import inspect
from typing import Optional

from .basis import Mutation, Deletion


class ValueStackException(Exception):
    pass


# Sometimes we need to put a _placeholder on TOS because we don't care about its value,
# like LOAD_CONST. We convert it to [] when putting it on the stack.
_placeholder = None


class JumpHandler:
    """Class that handles jump related instructions.

    The difference is, for jump instructions, we may need to use runtime information to
    decide what to do with the stack.
    """

    def emit_change_and_update_stack(
            self, instr, jumped=False, *args
    ) -> Optional[Mutation]:
        try:
            return getattr(JumpHandler, f"_{instr.opname}_handler")(self, instr, jumped)
        except AttributeError:
            return super().emit_change_and_update_stack(instr, *args)

    def _POP_BLOCK_handler(self, instr, jumped):
        pass

    def _JUMP_FORWARD_handler(self, instr, jumped):
        pass

    def _POP_JUMP_IF_TRUE_handler(self, instr, jumped):
        self._pop()

    def _POP_JUMP_IF_FALSE_handler(self, instr, jumped):
        self._pop()

    def _JUMP_IF_TRUE_OR_POP_handler(self, instr, jumped):
        if not jumped:
            self._pop()

    def _JUMP_IF_FALSE_OR_POP_handler(self, instr, jumped):
        if not jumped:
            self._pop()

    def _JUMP_ABSOLUTE_handler(self, instr, jumped):
        pass

    def _FOR_ITER_handler(self, instr, jumped):
        if jumped:
            self._pop()
        else:
            self._push(self.tos)


class GeneralValueStack:
    """Class that simulates the interpreter's value stack.

    This class handles instructions that don't require special processing.
    """

    def __init__(self):
        self.stack = []

        # Stores extended args, insertion order = order of appearances. e.g.
        #   0 EXTENDED_ARG 1
        #   2 EXTENDED_ARG 2
        # extended_args is [1, 2].
        # extended_args is cleared after it's been consumed.
        self.extended_args = []

    def emit_change_and_update_stack(self, instr, frame) -> Optional[Mutation]:
        """Given a instruction, emits mutation(s) if any, and updates the stack."""

        # Binary operations are all the same, no need to define handlers individually.
        if instr.opname.startswith("BINARY") or instr.opname.startswith("INPLACE"):
            self._BINARY_operation_handler(instr)
            return

        updated_instr_or_none = self._process_extended_arg(instr)
        if updated_instr_or_none is None:
            return

        # Emits mutation and updates value stack.
        try:
            handler = getattr(self, f"_{instr.opname}_handler")
            # For handlers that receive a frame parameter, passes in current frame.
            if "frame" in inspect.getfullargspec(handler).args:
                return handler(updated_instr_or_none, frame)
            else:
                return handler(updated_instr_or_none)
        except AttributeError:
            raise AttributeError(
                f"Please add\ndef _{instr.opname}_handler(self, instr):"
            )

    def _process_extended_arg(self, instr) -> Optional[dis.Instruction]:
        if instr.opname == "EXTENDED_ARG":
            self.extended_args.append(instr.arg)
            return

        # Calculates real arg value.
        if self.extended_args:
            assert len(self.extended_args) <= 3
            instr_attrs = instr._asdict()
            arg = instr.arg
            for i, extended_arg in enumerate(reversed(self.extended_args), 1):
                arg += extended_arg << (8 * i)
            instr_attrs["arg"] = arg
            instr = dis.Instruction(**instr_attrs)
            self.extended_args.clear()  # Important.

        return instr

    @property
    def tos(self):
        return self._tos(0)

    @property
    def tos1(self):
        return self._tos(1)

    @property
    def tos2(self):
        return self._tos(2)

    def _tos(self, n):
        """Returns the i-th element on the stack. Stack keeps unchanged."""
        index = -1 - n
        try:
            return self.stack[index]
        except IndexError:
            ValueStackException(
                f"Value stack should at least have {-index} elements",
                ", but only has {len(self.stack)}.",
            )

    def _push(self, value):
        """Pushes a value onto the simulated value stack.

        This method will automatically convert single value to a list. _placeholder will
        be converted to an empty list, so that it never exists on the value stack.
        """
        if value is _placeholder:
            value = []
        elif not isinstance(value, list):
            value = [value]
        self.stack.append(value)

    def _pop(self, n=1):
        """Pops and returns n item from stack."""
        try:
            if n == 1:
                return self.stack.pop()
            return [self.stack.pop() for _ in range(n)]
        except IndexError:
            ValueStackException("Value stack should have tos but is empty.")

    def _pop_n_push_one(self, n):
        """Pops n elements from TOS, and pushes one to TOS.

        The pushed element is expected to originates from the popped elements.
        """
        elements = []
        for _ in range(n):
            elements.extend(self._pop())  # Flattens elements in TOS.
        self._push(elements)

    def _pop_one_push_n(self, n):
        """Pops one elements from TOS, and pushes n elements to TOS.

        The pushed elements are expected to originates from the popped element.
        """
        tos = self._pop()
        for _ in range(n):
            self._push(tos)

    def _POP_TOP_handler(self, instr):
        self._pop()

    def _ROT_TWO_handler(self, instr):
        tos, tos1 = self._pop(2)
        self._push(tos)
        self._push(tos1)

    def _DUP_TOP_handler(self, instr):
        self._push(self.tos)

    def _DUP_TOP_TWO_handler(self, instr):
        tos1, tos = self.tos1, self.tos
        self._push(tos1)
        self._push(tos)

    def _ROT_THREE_handler(self, instr):
        self.stack[-3], self.stack[-2], self.stack[-1] = (
            self.tos,
            self.tos2,
            self.tos1,
        )

    def _UNARY_POSITIVE_handler(self, instr):
        pass

    def _UNARY_NEGATIVE_handler(self, instr):
        pass

    def _UNARY_NOT_handler(self, instr):
        pass

    def _UNARY_INVERT_handler(self, instr):
        pass

    def _GET_ITER_handler(self, instr):
        pass

    def _BINARY_operation_handler(self, instr):
        self._pop_n_push_one(2)

    def _STORE_SUBSCR_handler(self, instr):
        tos, tos1, tos2 = self._pop(3)
        assert len(tos1) == 1
        return Mutation(target=tos1[0], sources=set(tos + tos2))

    def _DELETE_SUBSCR_handler(self, instr):
        tos, tos1 = self._pop(2)
        assert len(tos1) == 1
        return Mutation(target=tos1[0], sources=set(tos))

    def _RETURN_VALUE_handler(self, instr):
        self._pop()

    def _SETUP_ANNOTATIONS_handler(self, instr):
        pass

    def _IMPORT_STAR_handler(self, instr):
        # It's impossible to know what names are loaded, and we don't really care.
        self._pop()

    def _STORE_NAME_handler(self, instr):
        mutation = Mutation(target=instr.argval, sources=set(self.tos))
        self._pop()
        return mutation

    def _DELETE_NAME_handler(self, instr):
        return Deletion(target=instr.argrepr)

    def _UNPACK_SEQUENCE_handler(self, instr):
        self._pop_one_push_n(instr.arg)

    def _UNPACK_EX_handler(self, instr):
        assert instr.arg <= 65535  # At most one extended arg.
        higher_byte, lower_byte = instr.arg >> 8, instr.arg & 0x00FF
        number_of_receivers = lower_byte + 1 + higher_byte
        self._pop_one_push_n(number_of_receivers)

    def _STORE_ATTR_handler(self, instr):
        assert len(self.tos) == 1
        return Mutation(target=self.tos[0], sources=set(self.tos1))

    def _DELETE_ATTR_handler(self, instr):
        assert len(self.tos) == 1
        return Mutation(target=self.tos[0])

    def _STORE_GLOBAL_handler(self, instr):
        return self._STORE_NAME_handler(instr)

    def _DELETE_GLOBAL_handler(self, instr):
        return Deletion(instr.argrepr)

    def _LOAD_CONST_handler(self, instr):
        # For instructions like LOAD_CONST, we just need a placeholder on the stack.
        self._push(_placeholder)

    def _LOAD_NAME_handler(self, instr):
        # Note that we never store the actual rvalue, just name.
        self._push(instr.argrepr)

    def _BUILD_TUPLE_handler(self, instr):
        self._pop_n_push_one(instr.arg)

    def _BUILD_LIST_handler(self, instr):
        self._BUILD_TUPLE_handler(instr)

    def _BUILD_SET_handler(self, instr):
        self._BUILD_TUPLE_handler(instr)

    def _BUILD_MAP_handler(self, instr):
        self._pop_n_push_one(instr.arg * 2)

    def _BUILD_CONST_KEY_MAP_handler(self, instr):
        self._pop_n_push_one(instr.arg + 1)

    def _BUILD_STRING_handler(self, instr):
        self._pop_n_push_one(instr.arg)

    def _BUILD_TUPLE_UNPACK_handler(self, instr):
        self._pop_n_push_one(instr.arg)

    def _BUILD_LIST_UNPACK_handler(self, instr):
        self._pop_n_push_one(instr.arg)

    def _BUILD_SET_UNPACK_handler(self, instr):
        self._pop_n_push_one(instr.arg)

    def _BUILD_MAP_UNPACK_handler(self, instr):
        self._pop_n_push_one(instr.arg)

    def _LOAD_ATTR_handler(self, instr):
        """Change the behavior of LOAD_ATTR.

        The effect of LOAD_ATTR is: Replaces TOS with getattr(TOS, co_names[namei]).
        However, this will make back tracing hard, because it eliminates the information
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

    def _COMPARE_OP_handler(self, instr):
        return self._BINARY_operation_handler(instr)

    def _IMPORT_NAME_handler(self, instr):
        self._pop_n_push_one(2)

    def _IMPORT_FROM_handler(self, instr):
        self._pop()
        self._push(_placeholder)

    def _LOAD_GLOBAL_handler(self, instr, frame):
        # Exclude builtin types like "range" so they don't become a source of mutations.
        if instr.argval in frame.f_builtins:
            self._push([])
        else:
            self._push(instr.argrepr)

    def _SETUP_LOOP_handler(self, instr):
        pass

    def _LOAD_FAST_handler(self, instr):
        self._push(instr.argrepr)

    def _STORE_FAST_handler(self, instr):
        return self._STORE_NAME_handler(instr)

    def _DELETE_FAST_handler(self, instr):
        return Deletion(target=instr.argrepr)

    def _LOAD_METHOD_handler(self, instr):
        self._pop()

    def _CALL_FUNCTION_handler(self, instr):
        # TODO: Deal with callsite.
        self._pop_n_push_one(instr.arg + 1)

    def _CALL_METHOD_handler(self, instr):
        """
        For now we assume no argument is passed, so tos is replaced with return value,
        thus a noop.
        TODO: Implement full behaviors of CALL_METHOD.
        """
        self._push(_placeholder)

    def _BUILD_SLICE_handler(self, instr):
        if instr.arg == 2:
            self._pop_n_push_one(2)
        elif instr.arg == 3:
            self._pop_n_push_one(3)

    def _FORMAT_VALUE_handler(self, instr):
        # See https://git.io/JvjTg to learn what this opcode is doing.
        elements = []
        if (instr.arg & 0x04) == 0x04:
            elements.extend(self._pop())
        elements.extend(self._pop())
        self._push(elements)

    # 3.7 Only
    def _BREAK_LOOP_handler(self, instr):
        pass


class ValueStack(JumpHandler, GeneralValueStack):
    pass
