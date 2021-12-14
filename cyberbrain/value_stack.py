# encoding: utf-8

"""A self maintained value stack."""

from __future__ import annotations

import dataclasses
import enum
from copy import copy
from dis import Instruction

import functools
import inspect
import sys
from types import FrameType
from typing import Optional

try:
    from typing import TYPE_CHECKING, Literal
except ImportError:
    from typing_extensions import Literal

from . import basis, utils
from .basis import (
    Symbol,
    Binding,
    Mutation,
    Deletion,
    JumpBackToLoopStart,
    ExceptionInfo,
)
from .block_stack import BlockStack, BlockType, Block

if TYPE_CHECKING:
    from .frame import Snapshot


class ValueStackException(Exception):
    pass


class _NullClass:
    def __repr__(self):
        return "NULL"


# The NULL value pushed by BEGIN_FINALLY, WITH_CLEANUP_FINISH, LOAD_METHOD.
NULL = _NullClass()


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


@dataclasses.dataclass
class EventInfo:
    type: Literal[Binding, Mutation, Deletion, JumpBackToLoopStart]
    target: Symbol = None
    sources: set[Symbol] = dataclasses.field(default_factory=set)
    jump_target: int = None
    lineno: int = -1


class Why(enum.Enum):
    UNINITIALIZED = 0
    NOT = 1  # No error
    EXCEPTION = 2  # Exception occurred
    RETURN = 3  # 'return' statement
    BREAK = 4  # 'break' statement
    CONTINUE = 5  # 'continue' statement
    YIELD = 6  # 'yield' operator
    SILENCED = 8  # Exception silenced by 'with'


class SymbolStackItem:
    """Class representing an item on the value stack to be tracked by Cyberbrain.

    Attributes:
        start_lineno: The starting lineno of the item.
        sources: A list of symbols that are the sources of the item.
    """

    def __init__(
        self,
        start_lineno: int,
        sources: List[Symbol],
    ):
        self.start_lineno = start_lineno
        self.sources = sources

    def __repr__(self) -> str:
        return "{" + repr(self.start_lineno) + " " + repr(self.sources) + "}"

    def get_top_source(self) -> Symbol:
        # This happens when variables (e.g. globals) that we don't care about are mutated.
        if len(self.sources) == 0:
            return None
        return self.sources[0]

    def copy(self) -> SymbolStackItem:
        return SymbolStackItem(self.start_lineno, [copy(sym) for sym in self.sources])


class CustomValueStackItem:
    """Class representing a custom value (Exceptions, Why's, anything not tracked by Cyberbrain) on the value stack

    Attributes:
        custom_value: The value of the custom item.
    """

    def __init__(
        self,
        custom_value: any = None,
    ):
        self.custom_value = custom_value

    def __repr__(self) -> str:
        return repr(self.custom_value)

    def copy(self) -> CustomValueStackItem:
        return CustomValueStackItem(self.custom_value)


class SymbolWithCustomValueStackItem(SymbolStackItem, CustomValueStackItem):
    """Class representing a both a symbol and a custom value on the value stack

    Some types like None's and Exceptions can be pushed onto the stack as either
    a normal SymbolStackItem or a CustomValueStackItem used for exceptions.
    Therefore, this class inherits from both SymbolStackItem and CustomValueStackItem for flexibility.
    """

    def __init__(self, start_lineno: int, sources: List[Symbol], custom_value=None):
        SymbolStackItem.__init__(self, start_lineno, sources)
        CustomValueStackItem.__init__(self, custom_value)

    def copy(self) -> SymbolWithCustomValueStackItem:
        return SymbolWithCustomValueStackItem(
            self.start_lineno, self.sources, self.custom_value
        )

    def __repr__(self) -> str:
        return "SymbolWithCustomValueStackItem{" + repr(self.custom_value) + "}"


# Placeholder for the items on the stack that we don't care about.
# This could be from a LOAD_CONST but since we can get the value later,
# we don't care about the value pushed on the stack
_placeholder = SymbolStackItem(-1, [])


# Placeholder for a None on the stack
# Could be a None that is stored in a variable or a None used by exception handling.
_none_placeholder = SymbolWithCustomValueStackItem(-1, [], None)


class BaseValueStack:
    """Class that simulates the a frame's value stack.

    This class contains instr handlers that are the same across different versions.
    """

    def __init__(self):
        self.stack: List[SymbolStackItem | CustomValueStackItem] = []
        self.block_stack = BlockStack()
        self.last_exception: Optional[ExceptionInfo] = None
        self.last_starts_line = -1
        self.return_value = _placeholder
        self.handler_signature_cache: dict[str, set[str]] = {}  # keyed by opname.
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
            if isinstance(item, SymbolStackItem):
                for symbol in item.sources:
                    if symbol.name == mutated_identifier:
                        symbol.snapshot = new_snapshot

    def emit_event_and_update_stack(
        self,
        instr: Instruction,
        frame: FrameType,
        jumped: bool,
        exc_info: Optional[ExceptionInfo],
        snapshot: Snapshot,
        lineno: int,
    ) -> Optional[EventInfo]:
        """Given a instruction, emits EventInfo if any, and updates the stack.

        Args:
            instr: current instruction.
            jumped: whether jump just happened.
            frame: current frame.
            exc_info: implicitly raised exception if any, or None.
            snapshot: frame state snapshot.
        """
        self.snapshot = snapshot
        opname = instr.opname
        _placeholder.start_lineno = self.last_starts_line = lineno

        if opname.startswith("BINARY") or opname.startswith("INPLACE"):
            # Binary operations are all the same.
            handler = self._BINARY_operation_handler
        else:
            try:
                handler = getattr(self, f"_{opname}_handler")
            except AttributeError:
                raise NotImplementedError(
                    f"Bytecode {opname} not implemented.\n"
                    "Please open git.io/JYSlG to report this issue.",
                )

        # Pass arguments on demand.
        try:
            parameters = self.handler_signature_cache[opname]
        except KeyError:
            parameters = set(inspect.signature(handler).parameters)
            self.handler_signature_cache[opname] = parameters

        # noinspection PyArgumentList
        return handler(
            *[
                arg
                for param_name, arg in {
                    "instr": instr,
                    "jumped": jumped,
                    "frame": frame,
                    "exc_info": exc_info,
                }.items()
                if param_name in parameters
            ]
        )

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

    @staticmethod
    def from_stack_items(
        *stack_items: List[SymbolStackItem | CustomValueStackItem],
    ) -> SymbolStackItem | CustomValueStackItem:
        """Merges multiple SymbolStackItem into one SymbolStackItem.

        If any non-SymbolStackItem is encountered, it is returned.
        Otherwise, a new SymbolStackItem is created with the combined sources
        and the start_lineno is the minimum of all the start_lineno's.
        """
        start_lineno = -1
        sources = []
        for item in stack_items:
            if not isinstance(item, SymbolStackItem):
                return item
            if item.start_lineno != -1:
                start_lineno = (
                    min(item.start_lineno, start_lineno)
                    if start_lineno != -1
                    else item.start_lineno
                )
            sources.extend(item.sources)
        return SymbolStackItem(start_lineno, sources)

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

        StackItems are copied onto the stack
        Str (name of variable) is converted to Symbol and then wrapped into a SymbolStackItem.
        If it is none of the above, the value is stored as a custom value.
        """
        start_lineno = self.last_starts_line
        for value in values:
            sources = []
            if isinstance(value, SymbolStackItem) or isinstance(
                value, CustomValueStackItem
            ):
                newValue = value.copy()
                self.stack.append(newValue)
                continue
            elif isinstance(value, str):  # For representing identifiers.
                sources.append(Symbol(name=value, snapshot=self.snapshot))
            elif isinstance(value, Symbol):  # Already a Symbol.
                # Why copy? Because the symbols on the stack might be modified
                # later in the update_snapshot method. If we don't copy, a
                # symbol that's already been popped out of the stack will be
                # affected by the change (if it has the same name with the
                # modified symbol on the stack). A copy will make symbols
                # isolated from each other.
                sources.append(copy(value))
            else:
                # For NULL or int used by block related handlers, keep the original value.
                self.stack.append(CustomValueStackItem(value))
                continue
            self.stack.append(SymbolStackItem(start_lineno, sources))

    def _pop(self, n=1, return_list=False):
        """Pops and returns n item from stack."""
        try:
            if n == 1 and not return_list:
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
            elements.append(self._pop())
        self._push(BaseValueStack.from_stack_items(*elements))

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

    def _instruction_successfully_executed(
        self, exc_info: Optional[ExceptionInfo], opname: str
    ) -> bool:
        """Returns true if there's no exception, otherwise false."""
        if exc_info:
            sys.stdout.buffer.write(
                f"⚠️  Exception happened in {opname}\n".encode("utf-8")
            )
            self._store_exception(exc_info)
            return False
        return True

    def _NOP_handler(self):
        pass

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

    def _BINARY_operation_handler(self, exc_info):
        tos, tos1 = self._pop(2)
        if self._instruction_successfully_executed(exc_info, "BINARY op"):
            self._push(BaseValueStack.from_stack_items(tos, tos1))

    @emit_event
    def _STORE_SUBSCR_handler(self, exc_info):
        tos, tos1, tos2 = self._pop(3)
        if self._instruction_successfully_executed(exc_info, "STORE_SUBSCR"):
            # We use to `assert len(tos1) == 1`, but in certain cases, like
            # os.environ["foo"] = "2", tos1 is [].
            if tos1.get_top_source() is not None:
                return EventInfo(
                    type=Mutation,
                    target=tos1.get_top_source(),
                    sources=set(tos.sources + tos1.sources + tos2.sources),
                    lineno=tos2.start_lineno,
                )

    # noinspection DuplicatedCode
    @emit_event
    def _DELETE_SUBSCR_handler(self, exc_info):
        tos, tos1 = self._pop(2)
        assert len(tos1.sources) == 1
        if self._instruction_successfully_executed(exc_info, "DELETE_SUBSCR"):
            if tos1.get_top_source() is not None:
                return EventInfo(
                    type=Mutation,
                    target=tos1.get_top_source(),
                    sources=set(tos.sources + tos1.sources),
                    lineno=tos1.start_lineno,
                )

    def _YIELD_VALUE_handler(self):
        """
        As of now, YIELD_VALUE is not handled specially. In the future, we may add a
        Yield event and treat it specially in the trace graph.
        """
        self._pop()

        # When the __next__ method is called on a generator, and the execution resumes
        # from where yield left off, None or the argument of gen.send() is put onto
        # the value stack. YIELD_VALUE is always followed by a POP_TOP, which then pops
        # this value.
        # See https://github.com/python/cpython/blob/master/Objects/genobject.c#L197
        # and https://www.cnblogs.com/coder2012/p/4990834.html for a code walk through.
        self._push(_placeholder)

    def _YIELD_FROM_handler(self):
        self._pop()

    def _SETUP_ANNOTATIONS_handler(self):
        pass

    def _IMPORT_STAR_handler(self):
        # It's impossible to know what names are loaded, and we don't really care.
        self._pop()

    @emit_event
    def _STORE_NAME_handler(self, instr):
        binding = EventInfo(
            type=Binding,
            target=Symbol(instr.argval),
            sources=set(self.tos.sources),
            lineno=min(self.last_starts_line, self.tos.start_lineno),
        )
        self._pop()
        return binding

    @emit_event
    def _DELETE_NAME_handler(self, instr, exc_info):
        if self._instruction_successfully_executed(exc_info, "DELETE_NAME"):
            return EventInfo(
                type=Deletion,
                target=Symbol(instr.argrepr),
                lineno=self.last_starts_line,
            )

    def _UNPACK_SEQUENCE_handler(self, instr, exc_info):
        seq = self._pop()
        if self._instruction_successfully_executed(exc_info, "UNPACK_SEQUENCE"):
            for _ in range(instr.arg):
                self._push(seq)

    def _UNPACK_EX_handler(self, instr, exc_info):
        assert instr.arg <= 65535  # At most one extended arg.
        higher_byte, lower_byte = instr.arg >> 8, instr.arg & 0x00FF
        number_of_receivers = lower_byte + 1 + higher_byte
        seq = self._pop()
        if self._instruction_successfully_executed(exc_info, "UNPACK_EX"):
            for _ in range(number_of_receivers):
                self._push(seq)

    @emit_event
    def _STORE_ATTR_handler(self, exc_info):
        tos, tos1 = self._pop(2)
        assert len(tos.sources) == 1
        if self._instruction_successfully_executed(exc_info, "STORE_ATTR"):
            if tos.get_top_source() is not None:
                return EventInfo(
                    type=Mutation,
                    target=tos.get_top_source(),
                    sources=set(tos.sources + tos1.sources),
                    lineno=tos1.start_lineno,
                )

    @emit_event
    def _DELETE_ATTR_handler(self, exc_info):
        tos = self._pop()
        assert len(tos.sources) == 1
        if self._instruction_successfully_executed(exc_info, "DELETE_ATTR"):
            if tos.get_top_source() is not None:
                return EventInfo(
                    type=Mutation,
                    target=tos.get_top_source(),
                    sources=set(tos.sources),
                    lineno=tos.start_lineno,
                )

    @emit_event
    def _STORE_GLOBAL_handler(self, instr):
        return self._STORE_NAME_handler(instr)

    @emit_event
    def _DELETE_GLOBAL_handler(self, instr, exc_info):
        if self._instruction_successfully_executed(exc_info, "DELETE_GLOBAL"):
            return EventInfo(
                type=Deletion,
                target=Symbol(instr.argrepr),
                lineno=self.last_starts_line,
            )

    def _BUILD_TUPLE_handler(self, instr):
        self._pop_n_push_one(instr.arg)

    def _BUILD_LIST_handler(self, instr):
        self._BUILD_TUPLE_handler(instr)

    def _BUILD_SET_handler(self, instr, exc_info):
        items = self._pop(instr.arg, return_list=True)
        if self._instruction_successfully_executed(exc_info, "BUILD_SET"):
            self._push(BaseValueStack.from_stack_items(*items))

    def _BUILD_MAP_handler(self, instr, exc_info):
        items = self._pop(instr.arg * 2)
        if self._instruction_successfully_executed(exc_info, "BUILD_MAP"):
            self._push(BaseValueStack.from_stack_items(*items))

    def _BUILD_CONST_KEY_MAP_handler(self, instr):
        self._pop_n_push_one(instr.arg + 1)

    def _BUILD_STRING_handler(self, instr):
        self._pop_n_push_one(instr.arg)

    def _BUILD_TUPLE_UNPACK_handler(self, instr, exc_info):
        items = self._pop(instr.arg, return_list=True)
        if self._instruction_successfully_executed(exc_info, "BUILD_TUPLE_UNPACK"):
            self._push(BaseValueStack.from_stack_items(*items))

    def _BUILD_TUPLE_UNPACK_WITH_CALL_handler(self, instr, exc_info):
        items = self._pop(instr.arg, return_list=True)
        if self._instruction_successfully_executed(
            exc_info, "BUILD_TUPLE_UNPACK_WITH_CALL"
        ):
            self._push(BaseValueStack.from_stack_items(*items))

    def _BUILD_LIST_UNPACK_handler(self, instr, exc_info):
        items = self._pop(instr.arg, return_list=True)
        if self._instruction_successfully_executed(exc_info, "BUILD_LIST_UNPACK"):
            self._push(BaseValueStack.from_stack_items(*items))

    def _BUILD_SET_UNPACK_handler(self, instr, exc_info):
        items = self._pop(instr.arg, return_list=True)
        if self._instruction_successfully_executed(exc_info, "BUILD_SET_UNPACK"):
            self._push(BaseValueStack.from_stack_items(*items))

    def _BUILD_MAP_UNPACK_handler(self, instr, exc_info):
        items = self._pop(instr.arg, return_list=True)
        if self._instruction_successfully_executed(exc_info, "BUILD_MAP_UNPACK"):
            self._push(BaseValueStack.from_stack_items(*items))

    def _BUILD_MAP_UNPACK_WITH_CALL_handler(self, instr, exc_info):
        items = self._pop(instr.arg, return_list=True)
        if self._instruction_successfully_executed(
            exc_info, "BUILD_MAP_UNPACK_WITH_CALL"
        ):
            self._push(BaseValueStack.from_stack_items(*items))

    def _LOAD_ATTR_handler(self, exc_info):
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
        self._instruction_successfully_executed(exc_info, "LOAD_ATTR")

    def _COMPARE_OP_handler(self, exc_info):
        return self._BINARY_operation_handler(exc_info)

    def _IMPORT_NAME_handler(self, exc_info):
        self._pop(2)
        if self._instruction_successfully_executed(exc_info, "IMPORT_NAME"):
            self._push(_placeholder)

    def _IMPORT_FROM_handler(self, exc_info):
        if self._instruction_successfully_executed(exc_info, "IMPORT_FROM"):
            self._push(_placeholder)

    def _LOAD_CONST_handler(self, instr):
        if instr.argrepr == "None":
            self._push(_none_placeholder)
        else:
            self._push(_placeholder)

    def _LOAD_NAME_handler(self, instr, frame, exc_info):
        if self._instruction_successfully_executed(exc_info, "LOAD_NAME"):
            self._push(self._fetch_value_for_load_instruction(instr.argrepr, frame))

    def _LOAD_GLOBAL_handler(self, instr, frame, exc_info):
        if self._instruction_successfully_executed(exc_info, "LOAD_GLOBAL"):
            self._push(self._fetch_value_for_load_instruction(instr.argrepr, frame))

    def _LOAD_FAST_handler(self, instr, frame, exc_info):
        if self._instruction_successfully_executed(exc_info, "LOAD_FAST"):
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
            return _placeholder

        return name

    @emit_event
    def _STORE_FAST_handler(self, instr):
        return self._STORE_NAME_handler(instr)

    def _LOAD_CLOSURE_handler(self, instr, frame, exc_info):
        if self._instruction_successfully_executed(exc_info, "LOAD_CLOSURE"):
            # It is possible that the name does not exist in the frame. Example:
            #
            # class Bar(Foo):  # LOAD_CLOSURE, but the name `Bar` does exist in frame.
            #     def __init__(self):
            #         super(Bar, self).__init__()
            #
            # In this case, we ignore the value cause it doesn't matter.
            try:
                value = self._fetch_value_for_load_instruction(instr.argrepr, frame)
            except AssertionError:
                value = _placeholder
            self._push(value)

    def _LOAD_DEREF_handler(self, instr, frame, exc_info):
        if self._instruction_successfully_executed(exc_info, "LOAD_DEREF"):
            self._push(self._fetch_value_for_load_instruction(instr.argrepr, frame))

    @emit_event
    def _STORE_DEREF_handler(self, instr):
        return self._STORE_NAME_handler(instr)

    @emit_event
    def _DELETE_DEREF_handler(self, instr, exc_info):
        if self._instruction_successfully_executed(exc_info, "DELETE_DEREF"):
            return EventInfo(
                type=Deletion,
                target=Symbol(instr.argrepr),
                lineno=self.last_starts_line,
            )

    @emit_event
    def _DELETE_FAST_handler(self, instr, exc_info):
        if self._instruction_successfully_executed(exc_info, "DELETE_FAST"):
            return EventInfo(
                type=Deletion,
                target=Symbol(instr.argrepr),
                lineno=self.last_starts_line,
            )

    def _LOAD_METHOD_handler(self, exc_info):
        if self._instruction_successfully_executed(exc_info, "LOAD_METHOD"):
            # NULL should be pushed if method lookup failed, but this would lead to an
            # exception anyway, and should be very rare, so ignoring it.
            # See https://docs.python.org/3/library/dis.html#opcode-LOAD_METHOD.
            self._push(self.tos)

    def _push_arguments_or_exception(self, callable_obj, args):
        if isinstance(callable_obj, SymbolStackItem):
            # Normal, return the callable and all arguments in a new symbol
            self._push(BaseValueStack.from_stack_items(callable_obj, *args))
        elif utils.is_exception_class(callable_obj.custom_value):
            # In `raise IndexError()`
            # We need to make sure the result of `IndexError()` is an exception inst,
            # so that _do_raise sees the correct value type.
            self._push(callable_obj.custom_value())
        else:
            # Non-exception custom value
            self._push(callable_obj)

    def _CALL_FUNCTION_handler(self, instr, exc_info):
        args = self._pop(instr.arg, return_list=True)
        callable_obj = self._pop()
        if self._instruction_successfully_executed(exc_info, "CALL_FUNCTION"):
            self._push_arguments_or_exception(callable_obj, args)

    def _CALL_FUNCTION_KW_handler(self, instr: Instruction, exc_info):
        args_num = instr.arg
        _ = self._pop()  # A tuple of keyword argument names.
        args = self._pop(args_num, return_list=True)
        callable_obj = self._pop()
        if self._instruction_successfully_executed(exc_info, "CALL_FUNCTION_KW"):
            self._push_arguments_or_exception(callable_obj, args)

    def _CALL_FUNCTION_EX_handler(self, instr, exc_info):
        kwargs = self._pop() if (instr.arg & 0x01) else SymbolStackItem(-1, [])
        args = self._pop()
        args = BaseValueStack.from_stack_items(args, kwargs)
        callable_obj = self._pop()
        if self._instruction_successfully_executed(exc_info, "CALL_FUNCTION_EX"):
            self._push_arguments_or_exception(callable_obj, (args,))

    @emit_event
    def _CALL_METHOD_handler(self, instr, exc_info):
        args = self._pop(instr.arg, return_list=True)
        inst_or_callable = self._pop()
        method_or_null = self._pop()  # method or NULL
        if self._instruction_successfully_executed(exc_info, "CALL_METHOD"):
            self._push(
                BaseValueStack.from_stack_items(inst_or_callable, method_or_null, *args)
            )

        # The real callable can be omitted for various reasons.
        # See the _fetch_value_for_load method.
        if inst_or_callable.get_top_source():
            # Actually, there could be multiple identifiers in inst_or_callable, but right
            # now we'll assume there's just one, and improve it as part of fine-grained
            # symbol tracing (main feature of version 3).
            return EventInfo(
                type=Mutation,
                target=inst_or_callable.get_top_source(),
                sources=set(
                    BaseValueStack.from_stack_items(inst_or_callable, *args)
                    .copy()
                    .sources
                ),
                lineno=inst_or_callable.start_lineno,
            )

    def _MAKE_FUNCTION_handler(self, instr):
        function_obj = []
        function_obj.append(self._pop())  # qualified_name
        function_obj.append(self._pop())  # code_obj

        if instr.argval & 0x08:
            function_obj.append(self._pop())  # closure
        if instr.argval & 0x04:
            function_obj.append(self._pop())  # annotations
        if instr.argval & 0x02:
            function_obj.append(self._pop())  # kwargs defaults
        if instr.argval & 0x01:
            function_obj.append(self._pop())  # args defaults

        self._push(BaseValueStack.from_stack_items(*function_obj))

    def _BUILD_SLICE_handler(self, instr):
        if instr.arg == 2:
            self._pop_n_push_one(2)
        elif instr.arg == 3:
            self._pop_n_push_one(3)

    def _EXTENDED_ARG_handler(self, instr):
        # Instruction.arg already contains the final value of arg, so this is a no op.
        pass

    def _FORMAT_VALUE_handler(self, instr, exc_info):
        # See https://git.io/JvjTg to learn what this opcode is doing.
        elements = []
        if (instr.arg & 0x04) == 0x04:
            elements.append(self._pop())
        elements.append(self._pop())

        if self._instruction_successfully_executed(exc_info, "FORMAT_VALUE"):
            self._push(BaseValueStack.from_stack_items(*elements))

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
    def _GET_ITER_handler(self, instr, exc_info):
        if self._instruction_successfully_executed(exc_info, "GET_ITER"):
            return self._return_jump_back_event_if_exists(instr)

    @emit_event
    def _GET_YIELD_FROM_ITER_handler(self, instr):
        """Since the handling of generators is ad-hoc, for now we didn't handle
        exceptions. We'll add it as part of a more well-thought-out generator
        implementation.
        """
        return self._return_jump_back_event_if_exists(instr)

    @emit_event
    def _FOR_ITER_handler(self, instr, jumped, exc_info: ExceptionInfo):
        # If it's StopIteration, we assume it's OK.
        if exc_info is None or exc_info.type is StopIteration:
            if jumped:
                self._pop()
            else:
                self._push(self.tos)
                return self._return_jump_back_event_if_exists(instr)
        else:
            self._instruction_successfully_executed(exc_info, "FOR_ITER")

    def _LOAD_BUILD_CLASS_handler(self):
        self._push(_placeholder)  # builtins.__build_class__()

    def _SETUP_WITH_handler(self, exc_info):
        if self._instruction_successfully_executed(exc_info, "SETUP_WITH"):
            enter_func = self.tos
            # We ignored the operation to replace context manager on tos with __exit__,
            # because it is a noop in our stack.
            self._push_block(BlockType.SETUP_FINALLY)
            self._push(enter_func)  # The return value of __enter__()

    def _return_jump_back_event_if_exists(self, instr):
        jump_target = utils.get_jump_target_or_none(instr)
        if jump_target is not None and jump_target < instr.offset:
            return EventInfo(
                type=JumpBackToLoopStart,
                jump_target=jump_target,
                lineno=self.last_starts_line,
            )

    def _unwind_except_handler(self, b: Block):
        assert self.stack_level >= b.b_level + 3
        while self.stack_level > b.b_level + 3:
            self._pop()
        exc_type, value, tb = (x.custom_value for x in self._pop(3))
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


class Py37ValueStack(BaseValueStack):
    """Value stack for Python 3.7."""

    def __init__(self):
        self.why = Why.UNINITIALIZED
        super().__init__()

    def _store_exception(self, exc_info: ExceptionInfo):
        """When an exception is raised implicitly (aka not by calling `raise`), use
        This method to propagate it as self.last_exception.
        """
        self.last_exception = exc_info
        self.why = Why.EXCEPTION
        self._fast_block_end()

    def _WITH_CLEANUP_FINISH_handler(self):
        # For __exit__, returning a true value from this method will cause the with
        # statement to suppress the exception and continue execution with the statement
        # immediately following the with statement. Otherwise the exception continues
        # propagating after this method has finished executing.
        #
        # res represents the return value, but there's no way CB can know its value.
        # So we just assume res is true whenever there is an exception, because CB does
        # not support unhandled exception, so it's safe to assume that if there's an
        # exception raised in `with`, it is properly handled. e.g.
        #         with pytest.raises(TypeError)
        res = self._pop()
        exc = self._pop().custom_value
        if res and utils.is_exception(exc):
            self._push(Why.SILENCED)

    def _RETURN_VALUE_handler(self):
        self.return_value = self._pop().custom_value
        self.why = Why.RETURN
        self._fast_block_end()

    def _YIELD_VALUE_handler(self):
        super()._YIELD_VALUE_handler()
        self.why = Why.YIELD

    def _YIELD_FROM_handler(self):
        super()._YIELD_FROM_handler()
        self.why = Why.YIELD

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
        # Since in FrameLogger.handle_exception, we excluded implicit exceptions raised
        # by executing RAISE_VARARGS and RERAISE, Cyberbrain can't handle exceptions
        # caused by `raise 1` (TypeError). But since this should be super rare, it
        # should be fine.

        cause = exc = None
        if instr.arg == 2:
            cause, exc = (x.custom_value for x in self._pop(2))
        elif instr.arg == 1:
            exc = self._pop().custom_value

        # In CPython's source code, it uses the result of _do_raise to decide whether to
        # raise an exception, then execute exception_unwind. Our value stack doesn't
        # need to actually raise an exception. If _do_raise returns false, it breaks
        # out of the switch clause, then jumps to label "error", which is above
        # _fast_block_end. So _fast_block_end will be executed anyway.
        self._do_raise(exc, cause)
        self.why = Why.EXCEPTION
        self._fast_block_end()

    # noinspection DuplicatedCode
    def _WITH_CLEANUP_START_handler(self, exc_info):
        exc = self.tos.custom_value
        exit_func: any
        if exc is None:
            exit_func = self.stack.pop(-2)
        elif isinstance(exc, Why):
            if exc in {Why.RETURN, Why.CONTINUE}:
                exit_func = self.stack.pop(-2).custom_value  # why, ret_val, __exit__
            else:
                exit_func = self.stack.pop(-1).custom_value  # why, __exit__
        elif utils.is_exception_class(exc):
            w, v, u = (x.custom_value for x in self._pop(3))
            tp2, exc2, tb2 = (x.custom_value for x in self._pop(3))
            exit_func = self._pop()
            self._push(tp2, exc2, tb2)
            self._push(None)
            self._push(w, v, u)
            block = self.block_stack.tos
            assert block.b_type == BlockType.EXCEPT_HANDLER
            block.b_level -= 1
        else:
            assert False, f"Unrecognized type: {exc}"

        if self._instruction_successfully_executed(exc_info, "WITH_CLEANUP_START"):
            self._push(exc)
            self._push(exit_func)

    def _END_FINALLY_handler(self, instr):
        status = self._pop().custom_value
        if isinstance(status, Why):
            self.why = status
            assert self.why not in {Why.YIELD, Why.EXCEPTION}
            if self.why in {Why.RETURN, Why.CONTINUE}:
                self.return_value = self._pop()
            if self.why is Why.SILENCED:
                block = self._pop_block()
                assert block.b_type is BlockType.EXCEPT_HANDLER
                self._unwind_except_handler(block)
                self.why = Why.NOT
                return
            self._fast_block_end()
        elif utils.is_exception_class(status):
            exc_type = status
            value, tb = (x.custom_value for x in self._pop(2))
            self.last_exception = ExceptionInfo(
                type=exc_type, value=value, traceback=tb
            )
            self.why = Why.EXCEPTION
            self._fast_block_end()
        else:
            assert status is None

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


class Py38ValueStack(Py37ValueStack):
    """Value stack for Python 3.8.

    Note that the this class inherits from Py37ValueStack, and not GeneralValueStack.
    This allows us to only override the methods that have changed in 3.8
    """

    def _store_exception(self, exc_info: ExceptionInfo):
        """When an exception is raised implicitly (aka not by calling `raise`), use
        This method to propagate it as self.last_exception.

        TODO: Every instruction handler that may raise exceptions should call this
            method.
        """
        self.last_exception = exc_info
        self._exception_unwind()

    def _WITH_CLEANUP_FINISH_handler(self):
        # For __exit__, returning a true value from this method will cause the with
        # statement to suppress the exception and continue execution with the statement
        # immediately following the with statement. Otherwise the exception continues
        # propagating after this method has finished executing.
        #
        # res represents the return value, but there's no way CB can know its value.
        # So we just assume res is true whenever there is an exception, because CB does
        # not support unhandled exception, so it's safe to assume that if there's an
        # exception raised in `with`, it is properly handled. e.g.
        #         with pytest.raises(TypeError)
        res = self._pop()
        exc = self._pop().custom_value
        if res and utils.is_exception(exc):
            block = self.block_stack.pop()
            assert block.b_type == BlockType.EXCEPT_HANDLER
            self._unwind_except_handler(block)
            self._push(NULL)

    def _RETURN_VALUE_handler(self):
        self.return_value = self._pop().custom_value
        # TODO: add exit_returning

    def _SETUP_FINALLY_handler(self):
        self._push_block(b_type=BlockType.SETUP_FINALLY)

    def _RAISE_VARARGS_handler(self, instr):
        cause = exc = None
        if instr.arg == 2:
            cause, exc = (x.custom_value for x in self._pop(2))
        elif instr.arg == 1:
            exc = self._pop().custom_value

        # In CPython's source code, it uses the result of _do_raise to decide whether to
        # raise an exception, then execute exception_unwind. Our value stack doesn't
        # need to actually raise an exception. If _do_raise returns false, it breaks
        # out of the switch clause, then jumps to label "error", which is above
        # _exception_unwind. So _exception_unwind will be executed anyway.
        self._do_raise(exc, cause)
        self._exception_unwind()

    def _POP_EXCEPT_handler(self):
        block = self._pop_block()
        assert block.b_type == BlockType.EXCEPT_HANDLER
        assert block.b_level + 3 <= self.stack_level <= block.b_level + 4
        exc_type, value, tb = (x.custom_value for x in self._pop(3))
        self.last_exception = ExceptionInfo(
            type=exc_type,
            value=value,
            traceback=tb,
        )

    def _POP_FINALLY_handler(self, instr):
        preserve_tos = instr.arg
        if preserve_tos:
            res = self._pop()

        if self.tos.custom_value is NULL or isinstance(self.tos.custom_value, int):
            _ = self._pop()
        else:
            _, _, _ = self._pop(3)
            block = self._pop_block()
            assert block.b_type is BlockType.EXCEPT_HANDLER
            assert self.stack_level == block.b_level + 3
            exc_type, value, tb = (x.custom_value for x in self._pop(3))
            self.last_exception = ExceptionInfo(
                type=exc_type,
                value=value,
                traceback=tb,
            )

        if preserve_tos:
            self._push(res)

    def _POP_BLOCK_handler(self):
        self._pop_block()

    def _BEGIN_FINALLY_handler(self):
        self._push(NULL)

    def _END_FINALLY_handler(self, instr):
        if self.tos.custom_value is NULL or isinstance(self.tos.custom_value, int):
            self._pop()
        elif utils.is_exception_class(self.tos.custom_value):
            exc_type, value, tb = (x.custom_value for x in self._pop(3))
            self.last_exception = ExceptionInfo(
                type=exc_type,
                value=value,
                traceback=tb,
            )
            self._exception_unwind()
        else:
            raise ValueStackException(f"TOS has wrong value: {self.tos}")

    def _WITH_CLEANUP_START_handler(self, exc_info):
        exc = self.tos.custom_value
        if self.tos.custom_value == NULL:  # Pushed by BEGIN_FINALLY
            exit_func = self.stack.pop(-2)
        else:
            w, v, u = (x.custom_value for x in self._pop(3))
            tp2, exc2, tb2 = (x.custom_value for x in self._pop(3))
            exit_func = self._pop()
            self._push(tp2, exc2, tb2)
            self._push(None)
            self._push(w, v, u)
            block = self.block_stack.tos
            assert block.b_type == BlockType.EXCEPT_HANDLER
            block.b_level -= 1

        if self._instruction_successfully_executed(exc_info, "WITH_CLEANUP_START"):
            self._push(exc)
            self._push(exit_func)

    def _exception_unwind(self):
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


class Py39ValueStack(Py38ValueStack):
    def _JUMP_IF_NOT_EXC_MATCH_handler(self):
        self._pop(2)

    def _CONTAINS_OP_handler(self, exc_info):
        self._BINARY_operation_handler(exc_info)

    def _IS_OP_handler(self, exc_info):
        self._BINARY_operation_handler(exc_info)

    def _LOAD_ASSERTION_ERROR_handler(self):
        self._push(AssertionError())

    def _LIST_TO_TUPLE_handler(self, instr):
        pass

    def _LIST_EXTEND_handler(self, exc_info):
        # list.extend(TOS1[-i], TOS), which essentially merges tos and tos1.
        items = self._pop(2)
        if self._instruction_successfully_executed(exc_info, "LIST_EXTEND"):
            self._push(BaseValueStack.from_stack_items(*items))

    def _SET_UPDATE_handler(self, exc_info):
        # list.extend(TOS1[-i], TOS), which essentially merges tos and tos1.
        items = self._pop(2)
        if self._instruction_successfully_executed(exc_info, "SET_UPDATE"):
            self._push(BaseValueStack.from_stack_items(*items))

    def _DICT_UPDATE_handler(self, exc_info):
        # dict.extend(TOS1[-i], TOS), which essentially merges tos and tos1.
        items = self._pop(2)
        if self._instruction_successfully_executed(exc_info, "DICT_UPDATE"):
            self._push(BaseValueStack.from_stack_items(*items))

    def _DICT_MERGE_handler(self, exc_info):
        items = self._pop(2)
        if self._instruction_successfully_executed(exc_info, "DICT_MERGE"):
            self._push(BaseValueStack.from_stack_items(*items))

    def _RERAISE_handler(self):
        exc_type, value, tb = (x.custom_value for x in self._pop(3))
        assert utils.is_exception_class(exc_type)
        self.last_exception = ExceptionInfo(
            type=exc_type,
            value=value,
            traceback=tb,
        )
        self._exception_unwind()

    def _WITH_EXCEPT_START_handler(self):
        exit_func = self.stack[-7]
        self._push(exit_func)


class Py310ValueStack(Py39ValueStack):
    def _GEN_START_handler(self):
        """Left unhandled for now."""


def create_value_stack():
    version_info = basis.VERSION_INFO
    if version_info == (3, 7):
        return Py37ValueStack()
    elif version_info == (3, 8):
        return Py38ValueStack()
    elif version_info == (3, 9):
        return Py39ValueStack()
    elif version_info == (3, 10):
        return Py310ValueStack()
    else:
        raise Exception(f"Unsupported Python version: {version_info}")
