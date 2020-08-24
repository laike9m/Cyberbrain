"""Test instructions that create blocks."""

from cyberbrain import Binding, Symbol
from utils import assert_GetFrame

# Loops can generate blocks too, they are tested in test_loop.py


def test_basic_try_except(tracer, rpc_stub):
    tracer.start_tracing()

    try:  # SETUP_EXCEPT (3.7), SETUP_FINALLY (3.8)
        raise IndexError("error")  # RAISE_VARARGS
        a = 1  # POP_BLOCK
    except IndexError:
        pass  # POP_EXCEPT, END_FINALLY

    tracer.stop_tracing()

    assert tracer.events == {}

    assert_GetFrame(rpc_stub, "test_basic_try_except")


def test_nested_try_except(tracer, rpc_stub):
    tracer.start_tracing()

    try:
        try:
            raise IndexError
        finally:
            a = 1
    except IndexError:
        pass

    tracer.stop_tracing()
    assert tracer.events == {"a": [Binding(target=Symbol("a"), value=1, lineno=32)]}

    assert_GetFrame(rpc_stub, "test_nested_try_except")


def test_try_except_finally(tracer, rpc_stub):
    tracer.start_tracing()

    try:  # SETUP_EXCEPT + SETUP_FINALLY (3.7), SETUP_FINALLY (3.8)
        raise IndexError("error")  # RAISE_VARARGS
    except IndexError:
        pass  # POP_EXCEPT
    finally:  # BEGIN_FINALLY (3.8)
        b = 1  # END_FINALLY

    tracer.stop_tracing()

    assert tracer.events == {"b": [Binding(target=Symbol("b"), value=1, lineno=50)]}

    assert_GetFrame(rpc_stub, "test_try_except_finally")


def test_break_in_finally(tracer, rpc_stub):
    tracer.start_tracing()

    for x in range(2):
        try:
            pass
        finally:
            break  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.stop_tracing()

    assert tracer.events == {"x": [Binding(target=Symbol("x"), value=0, lineno=62)]}

    assert_GetFrame(rpc_stub, "test_break_in_finally")


def test_break_in_finally_with_exception(tracer, rpc_stub):
    """Tests POP_FINALLY when tos is an exception."""

    tracer.start_tracing()

    # If the finally clause executes a return, break or continue statement, the saved
    # exception is discarded.
    for x in range(2):
        try:
            raise IndexError
        finally:
            break  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.stop_tracing()

    assert tracer.events == {"x": [Binding(target=Symbol("x"), value=0, lineno=82)]}

    assert_GetFrame(rpc_stub, "test_break_in_finally_with_exception")
