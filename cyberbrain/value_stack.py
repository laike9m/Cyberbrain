"""A self maintained value stack."""

from __future__ import annotations

import dataclasses
import enum
import functools
import inspect
import sys
from copy import copy
from dis import Instruction
from types import FrameType
from typing import Optional

try:
    from typing import TYPE_CHECKING, Literal
except ImportError:
    from typing_extensions import Literal

from . import utils
from .basis import EventType, Symbol
from .block_stack import BlockStack, BlockType, Block

if TYPE_CHECKING:
    from .frame import Snapshot


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


@dataclasses.dataclass
class ExceptionInfo:
    type: type
    value: Exception
    traceback: any


def emit_event(f):
    """Decorator used to denote that a handler emits at least one event.

    It is used for:
        1. Documentation purposes.
        2. In case there's a need to determine whether a handler emits any event.
    """

    @functools.wraps(f)
    def inner(*args, **kwargs):
        return f(*args, **kwargs)

    inner.emit_event = True
    return inner


MutationType = EventType.Mutation
DeletionType = EventType.Deletion
BindingType = EventType.Binding
JumpBackToLoopStartType = EventType.JumpBackToLoopStart


@dataclasses.dataclass
class EventInfo:
    type: Literal[EventType.Binding, EventType.Mutation, EventType.Deletion]
    target: Symbol = None
    sources: set[Symbol] = dataclasses.field(default_factory=set)
    jump_target: int = None


class GeneralValueStack:
    """Class that simulates the a frame's value stack.

    This class handles instructions that don't require special processing.
    """

    def __init__(self):
        self.stack = []
        self.block_stack = BlockStack()
        self.last_exception: Optional[ExceptionInfo] = None
        self.return_value = _placeholder
        self.snapshot = None

    def update_snapshot(self, mutated_identifier: str, new_snapshot: Snapshot):
        """Updates snapshot after an identifier has been mutated.

        e.g. `a`'s value is pushed to value stack, then `a` is mutated. We need to
            update the snapshot bound to `a`'s symbol so that later doing tracing,
            we can get the correct predecessor event of `a`, which is the mutation
            event.

        Note that Binding event does not change the object on value stack, so no need
        to update.
        """
        for item in self.stack:
            for symbol in item:
                if symbol.name == mutated_identifier:
                    symbol.snapshot = new_snapshot

    def emit_event_and_update_stack(
        self, instr: Instruction, frame: FrameType, jumped: bool, snapshot: Snapshot
    ) -> Optional[EventInfo]:
        """Given a instruction, emits EventInfo if any, and updates the stack.

        Args:
            instr: current instruction.
            jumped: whether jump just happened.
            frame: current frame.
            snapshot: frame state snapshot.
        """
        self.snapshot = snapshot

        if instr.opname.startswith("BINARY") or instr.opname.startswith("INPLACE"):
            # Binary operations are all the same.
            handler = self._BINARY_operation_handler
        else:
            try:
                handler = getattr(self, f"_{instr.opname}_handler")
            except AttributeError:
                raise AttributeError(
                    f"Please add\ndef _{instr.opname}_handler(self, instr):"
                )

        # Pass arguments on demand.
        parameters = inspect.signature(handler).parameters
        args = []
        if "instr" in parameters:
            args.append(instr)
        if "jumped" in parameters:
            args.append(jumped)
        if "frame" in parameters:
            args.append(frame)
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

        Str is converted to Symbol.
        """
        for value in values:
            if value is _placeholder:
                value = []
            elif isinstance(value, str):  # For representing identifiers.
                value = [Symbol(name=value, snapshot=self.snapshot)]
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    if isinstance(item, str):
                        value[index] = Symbol(item, snapshot=self.snapshot)
                    else:  # Already a Symbol.
                        # Why copy? Because the symbols on the stack might be modified
                        # later in the update_snapshot method. If we don't copy, a
                        # symbol that's already been popped out of the stack will be
                        # affected by the change (if it has the same name with the
                        # modified symbol on the stack). A copy will make symbols
                        # isolated from each other.
                        value[index] = copy(value[index])
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

    def _push_block(self, b_type: BlockType):
        self.block_stack.push(Block(b_level=self.stack_level, b_type=b_type))

    def _pop_block(self):
        return self.block_stack.pop()

    def _unwind_block(self, b: Block):
        while self.stack_level > b.b_level:
            self._pop()

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

    def _BINARY_operation_handler(self):
        self._pop_n_push_one(2)

    @emit_event
    def _STORE_SUBSCR_handler(self):
        tos, tos1, tos2 = self._pop(3)
        assert len(tos1) == 1
        return EventInfo(
            type=MutationType, target=tos1[0], sources=set(tos + tos1 + tos2)
        )

    # noinspection DuplicatedCode
    @emit_event
    def _DELETE_SUBSCR_handler(self):
        tos, tos1 = self._pop(2)
        assert len(tos1) == 1
        return EventInfo(type=MutationType, target=tos1[0], sources=set(tos + tos1))

    def _SETUP_ANNOTATIONS_handler(self):
        pass

    def _IMPORT_STAR_handler(self):
        # It's impossible to know what names are loaded, and we don't really care.
        self._pop()

    @emit_event
    def _STORE_NAME_handler(self, instr):
        binding = EventInfo(
            type=BindingType, target=Symbol(instr.argval), sources=set(self.tos)
        )
        self._pop()
        return binding

    @emit_event
    def _DELETE_NAME_handler(self, instr):
        return EventInfo(type=DeletionType, target=Symbol(instr.argrepr))

    def _UNPACK_SEQUENCE_handler(self, instr):
        self._pop_one_push_n(instr.arg)

    def _UNPACK_EX_handler(self, instr):
        assert instr.arg <= 65535  # At most one extended arg.
        higher_byte, lower_byte = instr.arg >> 8, instr.arg & 0x00FF
        number_of_receivers = lower_byte + 1 + higher_byte
        self._pop_one_push_n(number_of_receivers)

    # noinspection DuplicatedCode
    @emit_event
    def _STORE_ATTR_handler(self):
        tos, tos1 = self._pop(2)
        assert len(tos) == 1
        return EventInfo(type=MutationType, target=tos[0], sources=set(tos + tos1))

    @emit_event
    def _DELETE_ATTR_handler(self):
        tos = self._pop()
        assert len(tos) == 1
        return EventInfo(type=MutationType, target=tos[0], sources=set(tos))

    @emit_event
    def _STORE_GLOBAL_handler(self, instr):
        return self._STORE_NAME_handler(instr)

    @emit_event
    def _DELETE_GLOBAL_handler(self, instr):
        return EventInfo(type=DeletionType, target=Symbol(instr.argrepr))

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

    def _BUILD_TUPLE_UNPACK_WITH_CALL_handler(self, instr):
        self._pop_n_push_one(instr.arg)

    def _BUILD_LIST_UNPACK_handler(self, instr):
        self._pop_n_push_one(instr.arg)

    def _BUILD_SET_UNPACK_handler(self, instr):
        self._pop_n_push_one(instr.arg)

    def _BUILD_MAP_UNPACK_handler(self, instr):
        self._pop_n_push_one(instr.arg)

    def _BUILD_MAP_UNPACK_WITH_CALL_handler(self, instr):
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

    ############################ LOAD instructions ############################

    def _LOAD_CONST_handler(self):
        self._push(_placeholder)

    def _LOAD_NAME_handler(self, instr, frame):
        self._push(self._fetch_value_for_load_instruction(instr.argrepr, frame))

    def _LOAD_GLOBAL_handler(self, instr, frame):
        self._push(self._fetch_value_for_load_instruction(instr.argrepr, frame))

    def _LOAD_FAST_handler(self, instr, frame):
        self._push(self._fetch_value_for_load_instruction(instr.argrepr, frame))

    def _fetch_value_for_load_instruction(self, name, frame):
        """Transforms the value to be loaded onto value stack based on their types.

        The rules are:
        1. If the value is an exception class or instance, use the real value
        2. If the value is a built-in object, or tracer, or module, ignore it and stores
           a placeholder instead.
        3. Others, most likely a variable from user's code, stores the identifier.
        """
        val = utils.get_value_from_frame(name, frame)

        if utils.is_exception(val):
            # Keeps exceptions as they are so that they can be identified.
            return val

        if utils.should_ignore_event(target=name, value=val, frame=frame):
            return []

        return name

    @emit_event
    def _STORE_FAST_handler(self, instr):
        return self._STORE_NAME_handler(instr)

    def _LOAD_CLOSURE_handler(self, instr, frame):
        self._push(self._fetch_value_for_load_instruction(instr.argrepr, frame))

    def _LOAD_DEREF_handler(self, instr, frame):
        self._push(self._fetch_value_for_load_instruction(instr.argrepr, frame))

    @emit_event
    def _STORE_DEREF_handler(self, instr):
        return self._STORE_NAME_handler(instr)

    @emit_event
    def _DELETE_DEREF_handler(self, instr):
        return EventInfo(type=DeletionType, target=Symbol(instr.argrepr))

    @emit_event
    def _DELETE_FAST_handler(self, instr):
        return EventInfo(type=DeletionType, target=Symbol(instr.argrepr))

    def _LOAD_METHOD_handler(self):
        # NULL should be pushed if method lookup failed, but this would lead to an
        # exception anyway, and should be very rare, so ignoring it.
        # See https://docs.python.org/3/library/dis.html#opcode-LOAD_METHOD.
        self._push(self.tos)

    def _push_arguments_or_exception(self, callable_obj, args):
        if utils.is_exception_class(callable_obj):
            # In `raise IndexError()`
            # We need to make sure the result of `IndexError()` is an exception inst,
            # so that _do_raise sees the correct value type.
            self._push(callable_obj())
        else:
            # Return value is a list containing the callable and all arguments
            self._push(utils.flatten(callable_obj, args))

    def _CALL_FUNCTION_handler(self, instr):
        args = self._pop(instr.arg)
        callable_obj = self._pop()
        self._push_arguments_or_exception(callable_obj, args)

    def _CALL_FUNCTION_KW_handler(self, instr: Instruction):
        args_num = instr.arg
        _ = self._pop()  # A tuple of keyword argument names.
        args = self._pop(args_num)
        callable_obj = self._pop()
        self._push_arguments_or_exception(callable_obj, args)

    def _CALL_FUNCTION_EX_handler(self, instr):
        kwargs = self._pop() if (instr.arg & 0x01) else []
        args = self._pop()
        args.extend(kwargs)
        callable_obj = self._pop()
        self._push_arguments_or_exception(callable_obj, args)

    @emit_event
    def _CALL_METHOD_handler(self, instr):
        args = self._pop(instr.arg)
        inst_or_callable = self._pop()
        method_or_null = self._pop()  # method or NULL
        self._push(utils.flatten(inst_or_callable, method_or_null, *args))

        # The real callable can be omitted for various reasons.
        # See the _fetch_value_for_load method.
        if not inst_or_callable:
            return

        # Actually, there could be multiple identifiers in inst_or_callable, but right
        # now we'll assume there's just one, and improve it as part of fine-grained
        # symbol tracing (main feature of version 3).
        return EventInfo(
            type=MutationType,
            target=inst_or_callable[0],
            sources=set(utils.flatten(args, inst_or_callable)),
        )

    def _MAKE_FUNCTION_handler(self, instr):
        function_obj = []
        function_obj.extend(self._pop())  # qualified_name
        function_obj.extend(self._pop())  # code_obj

        if instr.argval & 0x08:
            function_obj.extend(self._pop())  # closure
        if instr.argval & 0x04:
            function_obj.extend(self._pop())  # annotations
        if instr.argval & 0x02:
            function_obj.extend(self._pop())  # kwargs defaults
        if instr.argval & 0x01:
            function_obj.extend(self._pop())  # args defaults

        self._push(function_obj)

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

    @emit_event
    def _POP_JUMP_IF_TRUE_handler(self, instr, jumped):
        self._pop()
        if jumped:
            return self._return_jump_back_event_if_exists(instr)

    @emit_event
    def _POP_JUMP_IF_FALSE_handler(self, instr, jumped):
        self._pop()
        if jumped:
            return self._return_jump_back_event_if_exists(instr)

    @emit_event
    def _JUMP_IF_TRUE_OR_POP_handler(self, instr, jumped):
        if not jumped:
            self._pop()
        else:
            return self._return_jump_back_event_if_exists(instr)

    @emit_event
    def _JUMP_IF_FALSE_OR_POP_handler(self, instr, jumped):
        if not jumped:
            self._pop()
        else:
            return self._return_jump_back_event_if_exists(instr)

    @emit_event
    def _JUMP_ABSOLUTE_handler(self, instr):
        return self._return_jump_back_event_if_exists(instr)

    @emit_event
    def _GET_ITER_handler(self, instr):
        return self._return_jump_back_event_if_exists(instr)

    @emit_event
    def _FOR_ITER_handler(self, instr, jumped):
        if jumped:
            self._pop()
        else:
            self._push(self.tos)
            return self._return_jump_back_event_if_exists(instr)

    def _LOAD_BUILD_CLASS_handler(self):
        self._push(_placeholder)  # builtins.__build_class__()

    def _SETUP_WITH_handler(self):
        enter_func = self.tos
        # We ignored the operation to replace context manager on tos with __exit__,
        # because it is a noop in our stack.
        self._push_block(BlockType.SETUP_FINALLY)
        self._push(enter_func)  # The return value of __enter__()

    def _WITH_CLEANUP_FINISH_handler(self):
        self._pop(2)
        # Again, this assumes there's no unhandled exception, and ignored the handling
        # for those exceptions.

    def _return_jump_back_event_if_exists(self, instr):
        jump_target = utils.get_jump_target_or_none(instr)
        if jump_target is not None and jump_target < instr.offset:
            return EventInfo(type=JumpBackToLoopStartType, jump_target=jump_target)

    def _unwind_except_handler(self, b: Block):
        assert self.stack_level >= b.b_level + 3
        while self.stack_level > b.b_level + 3:
            self._pop()
        exc_type = self._pop()
        value = self._pop()
        tb = self._pop()
        self.last_exception = ExceptionInfo(type=exc_type, value=value, traceback=tb)

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


class Why(enum.Enum):
    UNINITIALIZED = 0
    NOT = 1  # No error
    EXCEPTION = 2  # Exception occurred
    RETURN = 3  # 'return' statement
    BREAK = 4  # 'break' statement
    CONTINUE = 5  # 'continue' statement
    YIELD = 6  # 'yield' operator
    SILENCED = 8  # Exception silenced by 'with'


class Py37ValueStack(GeneralValueStack):
    """Value stack for Python 3.7."""

    def __init__(self):
        self.why = Why.UNINITIALIZED
        super().__init__()

    def _RETURN_VALUE_handler(self):
        self.return_value = self._pop()
        self.why = Why.RETURN
        self._fast_block_end()

    def _SETUP_LOOP_handler(self):
        self._push_block(BlockType.SETUP_LOOP)

    def _SETUP_EXCEPT_handler(self):
        self._push_block(BlockType.SETUP_EXCEPT)

    def _SETUP_FINALLY_handler(self):
        self._push_block(BlockType.SETUP_FINALLY)

    def _POP_BLOCK_handler(self):
        self._unwind_block(self._pop_block())

    def _BREAK_LOOP_handler(self):
        self.why = Why.BREAK
        self._fast_block_end()

    def _CONTINUE_LOOP_handler(self, instr):
        self.return_value = instr.arg
        assert self.return_value is not NULL
        self.why = Why.CONTINUE
        self._fast_block_end()

    def _POP_EXCEPT_handler(self):
        block = self._pop_block()
        assert block.b_type is BlockType.EXCEPT_HANDLER
        self._unwind_except_handler(block)

    def _RAISE_VARARGS_handler(self, instr):
        cause = exc = None
        if instr.arg == 2:
            cause, exc = self._pop(2)
        elif instr.arg == 1:
            exc = self._pop()

        # In CPython's source code, it uses the result of _do_raise to decide whether to
        # raise an exception, then execute exception_unwind. Our value stack doesn't
        # need to actually raise an exception. If _do_raise returns false, it breaks
        # out of the switch clause, then jumps to label "error", which is above
        # _fast_block_end. So _fast_block_end will be executed anyway.
        self._do_raise(exc, cause)
        self.why = Why.EXCEPTION
        self._fast_block_end()

    def _WITH_CLEANUP_START_handler(self):
        exc = self.tos
        exit_func: any
        if not exc:  # Checks if tos is None, which in our stack, is []
            exit_func = self.stack.pop(-2)
        elif isinstance(exc, Why):
            if exc in {Why.RETURN, Why.CONTINUE}:
                exit_func = self.stack.pop(-2)  # why, ret_val, __exit__
            else:
                exit_func = self.stack.pop(-1)  # why, __exit__
        else:
            assert False, "Unhandled exception is not supported by Cyberbrain"

        self._push(_placeholder)  # exc, set to None
        self._push(exit_func)

    def _END_FINALLY_handler(self):
        status = self._pop()
        if isinstance(status, Why):
            self.why = status
            assert self.why not in {Why.YIELD, Why.EXCEPTION}
            if self.why in {Why.RETURN, Why.CONTINUE}:
                self.return_value = self._pop()
            if self.why is Why.SILENCED:
                block = self._pop_block()
                assert block.type is BlockType.EXCEPT_HANDLER
                self._unwind_except_handler(block)
                self.why = Why.NOT
            self._fast_block_end()
        elif utils.is_exception_class(status):
            exc_type = status
            value = self._pop()
            tb = self._pop()
            self.last_exception = ExceptionInfo(
                type=exc_type, value=value, traceback=tb
            )
            self.why = Why.EXCEPTION
            self._fast_block_end()

        assert status is not None

    def _fast_block_end(self):
        assert self.why is not Why.NOT

        while self.block_stack.is_not_empty():
            block = self.block_stack.tos
            assert self.why is not Why.YIELD

            if block.b_type is BlockType.SETUP_LOOP and self.why is Why.CONTINUE:
                self.why = Why.NOT
                break

            self.block_stack.pop()
            if block.b_type is BlockType.EXCEPT_HANDLER:
                self._unwind_except_handler(block)
                continue

            self._unwind_block(block)

            if block.b_type is BlockType.SETUP_LOOP and self.why is Why.BREAK:
                self.why = Why.NOT
                break

            if self.why is Why.EXCEPTION and (
                block.b_type in {BlockType.SETUP_EXCEPT, BlockType.SETUP_FINALLY}
            ):
                self._push_block(BlockType.EXCEPT_HANDLER)
                self._push(self.last_exception.traceback)
                self._push(self.last_exception.value)
                if self.last_exception.type is not NULL:
                    self._push(self.last_exception.type)
                else:
                    self._push(None)

                exc_type, value, tb = (
                    self.last_exception.type,
                    self.last_exception.value,
                    self.last_exception.traceback,
                )
                # PyErr_NormalizeException is ignored, add it if needed.
                self._push(tb, value, exc_type)
                self.why = Why.NOT
                break

            if block.b_type is BlockType.SETUP_FINALLY:
                if self.why in {Why.RETURN, Why.CONTINUE}:
                    self._push(self.return_value)
                self._push(self.why)
                self.why = Why.NOT
                break


class Py38ValueStack(GeneralValueStack):
    """Value stack for Python 3.8."""

    def _RETURN_VALUE_handler(self):
        self.return_value = self._pop()
        # TODO: add exit_returning

    def _SETUP_FINALLY_handler(self):
        self._push_block(b_type=BlockType.SETUP_FINALLY)

    def _RAISE_VARARGS_handler(self, instr):
        cause = exc = None
        if instr.arg == 2:
            cause, exc = self._pop(2)
        elif instr.arg == 1:
            exc = self._pop()

        # In CPython's source code, it uses the result of _do_raise to decide whether to
        # raise an exception, then execute exception_unwind. Our value stack doesn't
        # need to actually raise an exception. If _do_raise returns false, it breaks
        # out of the switch clause, then jumps to label "error", which is above
        # _exception_unwind. So _exception_unwind will be executed anyway.
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

    def _WITH_CLEANUP_START_handler(self):
        if self.tos == NULL:  # Pushed by BEGIN_FINALLY
            exit_func = self.stack.pop(-2)
            self._push([])  # Pushes None to the stack
            self._push(exit_func)
        else:
            # Note that in real CPython code, this clause is used to process unhandled
            # exceptions thrown inside `with`. However, since our stack is just a
            # simulation, we won't push exceptions onto the stack even if an unhandled
            # happened, which, makes it meaningless to write any code here.
            # Essentially, users shouldn't use Cyberbrain if there will ever be
            # unhandled exceptions.
            pass

    def _exception_unwind(self, instr):
        print("inside _exception_unwind")
        while self.block_stack.is_not_empty():
            block = self.block_stack.pop()

            if block.b_type is BlockType.EXCEPT_HANDLER:
                self._unwind_except_handler(block)
                continue

            self._unwind_block(block)

            if block.b_type is BlockType.SETUP_FINALLY:
                self._push_block(b_type=BlockType.EXCEPT_HANDLER)
                exc_type, value, tb = (
                    self.last_exception.type,
                    self.last_exception.value,
                    self.last_exception.traceback,
                )
                self._push(tb, value, exc_type)
                self._push(tb, value, exc_type)
                break  # goto main_loop.


def create_value_stack():
    if sys.version_info[:2] == (3, 7):
        return Py37ValueStack()
    elif sys.version_info[:2] == (3, 8):
        return Py38ValueStack()
    else:
        raise Exception(f"Unsupported Python version: {sys.version}")
