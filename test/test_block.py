"""Test instructions that create blocks."""

from cyberbrain import Binding, Symbol


# Loops can generate blocks too, they are tested in test_loop.py


def test_basic_try_except(tracer, check_golden_file):
    tracer.start()

    try:  # SETUP_EXCEPT (3.7), SETUP_FINALLY (3.8)
        raise IndexError("error")  # RAISE_VARARGS
        a = 1  # POP_BLOCK
    except IndexError:
        pass  # POP_EXCEPT, END_FINALLY

    tracer.stop()


def test_nested_try_except(tracer, check_golden_file):
    tracer.start()

    try:
        try:
            raise IndexError
        finally:
            a = 1
    except IndexError:
        pass

    tracer.stop()


def test_try_except_finally(tracer, check_golden_file):
    tracer.start()

    try:  # SETUP_EXCEPT + SETUP_FINALLY (3.7), SETUP_FINALLY (3.8)
        raise IndexError("error")  # RAISE_VARARGS
    except IndexError:
        pass  # POP_EXCEPT
    finally:  # BEGIN_FINALLY (3.8)
        b = 1  # END_FINALLY

    tracer.stop()


def test_break_in_finally(tracer, check_golden_file):
    tracer.start()

    for x in range(2):
        try:
            pass
        finally:
            break  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.stop()


def test_break_in_finally_with_exception(tracer, check_golden_file):
    """Tests POP_FINALLY when tos is an exception."""

    tracer.start()

    # If the finally clause executes a return, break or continue statement, the saved
    # exception is discarded.
    for x in range(2):
        try:
            raise IndexError
        finally:
            break  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.stop()
