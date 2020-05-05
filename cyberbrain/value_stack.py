"""A self maintained value stack."""

import enum
import inspect
import sys
from dataclasses import dataclass
from dis import Instruction
from types import FrameType
from typing import Optional

from . import utils
from .basis import Mutation, Deletion, Event
from .block_stack import BlockStack, BlockType, Block


class ValueStackException(Exception):
    pass


# Sometimes we need to put a _placeholder on TOS because we don't care about its value,
# like LOAD_CONST. We convert it to [] when putting it on the stack.
_placeholder = None


class _NullClass:
    def __repr__(self):
        return "NULL"


# The NULL value pushed by BEGIN_FINALLY, WITH_CLEANUP_FINISH, LOAD_METHOD.
NULL = _NullClass()


@dataclass
class ExceptionInfo:
    type: type
    value: Exception
    traceback: any


class EvaluationMode(enum.Enum):
    """Whether instruction evaluation happens before or after its execution."""

    BEFORE_INSTR_EXECUTION = 1
    AFTER_INSTR_EXECUTION = 2


BEFORE_INSTR_EXECUTION = EvaluationMode.BEFORE_INSTR_EXECUTION
AFTER_INSTR_EXECUTION = EvaluationMode.AFTER_INSTR_EXECUTION


class GeneralValueStack:
    """Class that simulates the a frame's value stack.

    This class handles instructions that don't require special processing.
    """

    def __init__(self):
        self.stack = []
        self.block_stack = BlockStack()

    def emit_event_and_update_stack(
        self,
        instr: Instruction,
        frame: FrameType,
        evaluation_mode: EvaluationMode,
        jumped: bool,
    ) -> Optional[Event]:
        """Given a instruction, emits mutation(s) if any, and updates the stack.

        Args:
            instr: current instruction.
            jumped: whether jump just happened.
            frame: current frame.
            evaluation_mode: If instruction evaluation happens before it's been
                             executed, don't modify stack, only emits events.
        """

        if instr.opname.startswith("BINARY") or instr.opname.startswith("INPLACE"):
            # Binary operations are all the same.
            handler = self._BINARY_operation_handler
        else:
            try:
                handler = getattr(self, f"_{instr.opname}_handler")
            except AttributeError:
                del frame
                raise AttributeError(
                    f"Please add\ndef _{instr.opname}_handler(self, instr):"
                )

        arg_spec = inspect.getfullargspec(handler).args
        if (
            evaluation_mode is BEFORE_INSTR_EXECUTION
            and "evaluation_mode" not in arg_spec
        ):
            # When a handler does not have evaluation_mode parameter, it is
            # guaranteed to not emit any event.
            return None

        # Pass arguments on demand.
        args = []
        if "instr" in arg_spec:
            args.append(instr)
        if "jumped" in arg_spec:
            args.append(jumped)
        if "frame" in arg_spec:
            args.append(frame)
        if "evaluation_mode" in arg_spec:
            args.append(evaluation_mode)
        del frame
        return handler(*args)

    @property
    def stack_level(self):
        return len(self.stack)

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
            raise ValueStackException(
                f"Value stack should at least have {-index} elements",
                f", but only has {len(self.stack)}.",
            )

    def _push(self, *values):
        """Pushes values onto the simulated value stack.

        This method will automatically convert single value to a list. _placeholder will
        be converted to an empty list, so that it never exists on the value stack.
        """
        for value in values:
            if value is _placeholder:
                value = []
            elif isinstance(value, str):  # For representing identifiers.
                value = [value]
            # For NULL or int used by block related handlers, keep the original value.
            self.stack.append(value)

    def _pop(self, n=1):
        """Pops and returns n item from stack."""
        try:
            if n == 1:
                return self.stack.pop()
            return [self.stack.pop() for _ in range(n)]
        except IndexError:
            raise ValueStackException("Value stack should have tos but is empty.")

    def _pop_n_push_one(self, n):
        """Pops n elements from TOS, and pushes one to TOS.

        The pushed element is expected to originates from the popped elements.
        """
        elements = []
        for _ in range(n):
            tos = self._pop()
            if isinstance(tos, list):
                # Flattens identifiers in TOS, leave out others (NULL, int).
                elements.extend(tos)
        self._push(elements)

    def _pop_one_push_n(self, n):
        """Pops one elements from TOS, and pushes n elements to TOS.

        The pushed elements are expected to originates from the popped element.
        """
        tos = self._pop()
        for _ in range(n):
            self._push(tos)

    def _push_block(self, instr, b_type: BlockType):
        self.block_stack.push(Block(b_level=self.stack_level, b_type=b_type))

    def _POP_TOP_handler(self):
        self._pop()

    def _ROT_TWO_handler(self):
        tos, tos1 = self._pop(2)
        self._push(tos)
        self._push(tos1)

    def _DUP_TOP_handler(self):
        self._push(self.tos)

    def _DUP_TOP_TWO_handler(self):
        tos1, tos = self.tos1, self.tos
        self._push(tos1)
        self._push(tos)

    def _ROT_THREE_handler(self):
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

    def _BINARY_operation_handler(self):
        self._pop_n_push_one(2)

    def _STORE_SUBSCR_handler(self, evaluation_mode):
        if evaluation_mode is BEFORE_INSTR_EXECUTION:
            return Mutation(target=self.tos1[0], sources=set(self.tos + self.tos2))

        if evaluation_mode is AFTER_INSTR_EXECUTION:
            tos, tos1, tos2 = self._pop(3)
            assert len(tos1) == 1
            return Mutation(target=tos1[0], sources=set(tos + tos2))

    # noinspection DuplicatedCode
    def _DELETE_SUBSCR_handler(self, evaluation_mode):
        if evaluation_mode is BEFORE_INSTR_EXECUTION:
            return Mutation(target=self.tos1[0], sources=set(self.tos))

        if evaluation_mode is AFTER_INSTR_EXECUTION:
            tos, tos1 = self._pop(2)
            assert len(tos1) == 1
            return Mutation(target=tos1[0], sources=set(tos))

    def _RETURN_VALUE_handler(self):
        self._pop()

    def _SETUP_ANNOTATIONS_handler(self):
        pass

    def _IMPORT_STAR_handler(self):
        # It's impossible to know what names are loaded, and we don't really care.
        self._pop()

    def _STORE_NAME_handler(self, instr, evaluation_mode):
        mutation = Mutation(target=instr.argval, sources=set(self.tos))
        if evaluation_mode is AFTER_INSTR_EXECUTION:
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

    # noinspection DuplicatedCode
    def _STORE_ATTR_handler(self, evaluation_mode):
        if evaluation_mode is BEFORE_INSTR_EXECUTION:
            return Mutation(target=self.tos[0], sources=set(self.tos1))

        if evaluation_mode is AFTER_INSTR_EXECUTION:
            tos, tos1 = self._pop(2)
            assert len(tos) == 1
            return Mutation(target=tos[0], sources=set(tos1))

    def _DELETE_ATTR_handler(self, evaluation_mode):
        if evaluation_mode is BEFORE_INSTR_EXECUTION:
            return Mutation(target=self.tos[0])

        if evaluation_mode is AFTER_INSTR_EXECUTION:
            tos = self._pop()
            assert len(tos) == 1
            return Mutation(target=tos[0])

    def _STORE_GLOBAL_handler(self, instr, evaluation_mode):
        return self._STORE_NAME_handler(instr, evaluation_mode)

    def _DELETE_GLOBAL_handler(self, instr):
        return Deletion(instr.argrepr)

    def _LOAD_CONST_handler(self):
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
        """Event the behavior of LOAD_ATTR.

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

    def _COMPARE_OP_handler(self):
        return self._BINARY_operation_handler()

    def _IMPORT_NAME_handler(self):
        self._pop_n_push_one(2)

    def _IMPORT_FROM_handler(self):
        self._push(_placeholder)

    def _LOAD_GLOBAL_handler(self, instr, frame):
        # Exclude builtin types like "range" so they don't become a source of mutations.
        # TODO: this method (and other LOAD_XXX methods) seriously need rewriting.
        # Because in the end we need to handle values based on their type.
        val = _placeholder

        if instr.argval in frame.f_builtins:
            val = frame.f_builtins[instr.argval]
            if not utils.is_exception(val):
                # Keeps exceptions so that they can be identified.
                val = []
        else:
            val = instr.argrepr

        self._push(val)
        del frame

    def _LOAD_FAST_handler(self, instr):
        self._push(instr.argrepr)

    def _STORE_FAST_handler(self, instr, evaluation_mode):
        return self._STORE_NAME_handler(instr, evaluation_mode)

    def _DELETE_FAST_handler(self, instr):
        return Deletion(target=instr.argrepr)

    def _LOAD_METHOD_handler(self):
        # TODO: Implement full behaviors.
        self._push(self.tos)

    def _CALL_FUNCTION_handler(self, instr):
        # TODO: Deal with callsite.
        args = self._pop(instr.arg)
        callable_obj = self._pop()
        if utils.is_exception_class(callable_obj):
            # In `raise IndexError()`
            # We need to make sure the result of `IndexError()` is an exception inst,
            # so that _do_raise sees the correct value type.
            self._push(callable_obj())
        else:
            elements = []
            for arg in args:
                if isinstance(arg, list):
                    elements.extend(tos)
            self._push(elements)

    def _CALL_METHOD_handler(self, instr):
        # TODO: Deal with callsite.
        self._pop_n_push_one(instr.arg + 2)

    def _BUILD_SLICE_handler(self, instr):
        if instr.arg == 2:
            self._pop_n_push_one(2)
        elif instr.arg == 3:
            self._pop_n_push_one(3)

    def _EXTENDED_ARG_handler(self, instr):
        # Instruction.arg already contains the final value of arg, so this is a no op.
        pass

    def _FORMAT_VALUE_handler(self, instr):
        # See https://git.io/JvjTg to learn what this opcode is doing.
        elements = []
        if (instr.arg & 0x04) == 0x04:
            elements.extend(self._pop())
        elements.extend(self._pop())
        self._push(elements)

    def _JUMP_FORWARD_handler(self, instr, jumped):
        pass

    def _POP_JUMP_IF_TRUE_handler(self):
        self._pop()

    def _POP_JUMP_IF_FALSE_handler(self):
        self._pop()

    def _JUMP_IF_TRUE_OR_POP_handler(self, jumped):
        if not jumped:
            self._pop()

    def _JUMP_IF_FALSE_OR_POP_handler(self, jumped):
        if not jumped:
            self._pop()

    def _JUMP_ABSOLUTE_handler(self, instr, jumped):
        pass

    def _FOR_ITER_handler(self, jumped):
        if jumped:
            self._pop()
        else:
            self._push(self.tos)


class Py37ValueStack(GeneralValueStack):
    """Value stack for Python 3.7."""

    def _SETUP_LOOP_handler(self):
        raise NotImplementedError

    def _BREAK_LOOP_handler(self):
        raise NotImplementedError

    def _CONTINUE_LOOP_handler(self, instr):
        raise NotImplementedError

    def _SETUP_EXCEPT_handler(self):
        raise NotImplementedError


class Py38ValueStack(GeneralValueStack):
    """Value stack for Python 3.8."""

    last_exception: Optional[ExceptionInfo] = None

    def _do_raise(self, exc, cause) -> bool:
        # See https://github.com/nedbat/byterun/blob/master/byterun/pyvm2.py#L806
        if exc is None:  # reraise
            exc_type, val, tb = (
                self.last_exception.type,
                self.last_exception.value,
                self.last_exception.traceback,
            )
            return exc_type is not None
        elif type(exc) == type:
            # As in `raise ValueError`
            exc_type = exc
            val = exc()  # Make an instance.
        elif isinstance(exc, BaseException):
            # As in `raise ValueError('foo')`
            val = exc
            exc_type = type(exc)
        else:
            return False  # error

        # If you reach this point, you're guaranteed that
        # val is a valid exception instance and exc_type is its class.
        # Now do a similar thing for the cause, if present.
        if cause:
            if type(cause) == type:
                cause = cause()
            elif not isinstance(cause, BaseException):
                return False

            val.__cause__ = cause

        self.last_exception = ExceptionInfo(
            type=exc_type, value=val, traceback=val.__traceback__
        )
        return False

    def _unwind_except_handler(self, b: Block):
        assert self.stack_level >= b.b_level + 3
        while self.stack_level > b.b_level + 3:
            self._pop()
        exc_type = self._pop()
        value = self._pop()
        tb = self._pop()
        self.last_exception = ExceptionInfo(type=exc_type, value=value, traceback=tb)

    def _unwind_block(self, b: Block):
        while self.stack_level > b.b_level:
            self._pop()

    def _exception_unwind(self, instr):
        print("inside _exception_unwind")
        while not self.block_stack.is_empty():
            block = self.block_stack.pop()

            if block.b_type is BlockType.EXCEPT_HANDLER:
                self._unwind_except_handler(block)
                continue

            self._unwind_block(block)

            if block.b_type is BlockType.SETUP_FINALLY:
                self._push_block(instr, b_type=BlockType.EXCEPT_HANDLER)
                exc_type, value, tb = (
                    self.last_exception.type,
                    self.last_exception.value,
                    self.last_exception.traceback,
                )
                self._push(tb, value, exc_type)
                self._push(tb, value, exc_type)
                break  # goto main_loop.

    def _pop_block(self):
        return self.block_stack.pop()

    def _SETUP_FINALLY_handler(self, instr):
        self._push_block(instr, b_type=BlockType.SETUP_FINALLY)

    def _RAISE_VARARGS_handler(self, instr):
        cause = exc = None
        if instr.arg == 2:
            cause, exc = self._pop(2)
        elif instr.arg == 1:
            exc = self._pop()

        # In CPython's source code, it uses the result of _do_raise to decide whether to
        # raise an exception, then execute exception_unwind. Our value stack doesn't
        # need to actually raise an exception.
        self._do_raise(exc, cause)
        self._exception_unwind(instr)

    def _POP_EXCEPT_handler(self):
        block = self._pop_block()
        assert block.b_type == BlockType.EXCEPT_HANDLER
        assert block.b_level + 3 <= self.stack_level <= block.b_level + 4
        exc_type = self._pop()
        value = self._pop()
        tb = self._pop()
        self.last_exception = ExceptionInfo(type=exc_type, value=value, traceback=tb)

    def _POP_FINALLY_handler(self, instr):
        preserve_tos = instr.arg
        if preserve_tos:
            res = self._pop()

        if self.tos is NULL or isinstance(self.tos, int):
            exc = self._pop()
        else:
            _, _, _ = self._pop(3)
            block = self._pop_block()
            assert block.b_type is BlockType.EXCEPT_HANDLER
            assert self.stack_level == block.b_level + 3
            exc_type, value, tb = self._pop(3)
            self.last_exception = ExceptionInfo(
                type=exc_type, value=value, traceback=tb
            )

        if preserve_tos:
            self._push(res)

    def _POP_BLOCK_handler(self):
        self._pop_block()

    def _BEGIN_FINALLY_handler(self):
        self._push(NULL)

    def _END_FINALLY_handler(self, instr):
        if self.tos is NULL or isinstance(self.tos, int):
            self._pop()
        elif utils.is_exception_class(self.tos):
            exc_type = self._pop()
            value = self._pop()
            tb = self._pop()
            self.last_exception = ExceptionInfo(
                type=exc_type, value=value, traceback=tb
            )
            self._exception_unwind(instr)
        else:
            raise ValueStackException(f"TOS has wrong value: {self.tos}")


def create_value_stack():
    if sys.version_info[:2] == (3, 7):
        return Py37ValueStack()
    elif sys.version_info[:2] == (3, 8):
        return Py38ValueStack()
    else:
        raise Exception(f"Unsupported Python version: {sys.version}")
