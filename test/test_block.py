"""Test instructions that create blocks."""

from cyberbrain import Binding, Symbol


# Loops can generate blocks too, they are tested in test_loop.py


def test_basic_try_except(tracer, mocked_responses):
    tracer.start()

    try:  # SETUP_EXCEPT (3.7), SETUP_FINALLY (3.8)
        raise IndexError("error")  # RAISE_VARARGS
        a = 1  # POP_BLOCK
    except IndexError:
        pass  # POP_EXCEPT, END_FINALLY

    tracer.stop()

    assert tracer.events == []


def test_nested_try_except(tracer, mocked_responses):
    tracer.start()

    try:
        try:
            raise IndexError
        finally:
            a = 1
    except IndexError:
        pass

    tracer.stop()
    assert tracer.events == [Binding(target=Symbol("a"), value="1", lineno=30)]


def test_try_except_finally(tracer, mocked_responses):
    tracer.start()

    try:  # SETUP_EXCEPT + SETUP_FINALLY (3.7), SETUP_FINALLY (3.8)
        raise IndexError("error")  # RAISE_VARARGS
    except IndexError:
        pass  # POP_EXCEPT
    finally:  # BEGIN_FINALLY (3.8)
        b = 1  # END_FINALLY

    tracer.stop()

    assert tracer.events == [Binding(target=Symbol("b"), value="1", lineno=46)]


def test_break_in_finally(tracer, mocked_responses):
    tracer.start()

    for _ in range(2):
        try:
            pass
        finally:
            break  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.stop()

    assert tracer.events == [Binding(target=Symbol("x"), value="0", lineno=56)]


def test_break_in_finally_with_exception(tracer, mocked_responses):
    """Tests POP_FINALLY when tos is an exception."""

    tracer.start()

    # If the finally clause executes a return, break or continue statement, the saved
    # exception is discarded.
    for _ in range(2):
        try:
            raise IndexError
        finally:
            break  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.stop()

    assert tracer.events == [Binding(target=Symbol("x"), value="0", lineno=74)]
