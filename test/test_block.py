"""Test instructions that create blocks."""

from cyberbrain import Binding, Mutation


def test_loop(tracer):
    tracer.init()

    for x in range(2):  # SETUP_LOOP (3.7), GET_ITER, FOR_ITER
        pass  # POP_BLOCK (3.7)

    for y in range(2):
        break  # BREAK_LOOP (3.7), JUMP_ABSOLUTE (>=3.8)
        a = 1

    for z in range(1):
        continue  # CONTINUE_LOOP (3.7), JUMP_ABSOLUTE (>=3.8)
        a = 1

    i = 0
    while i < 1:  # SETUP_LOOP (3.7), POP_JUMP_IF_FALSE
        i += 1

    tracer.register()

    assert tracer.events == {
        "x": [
            Binding(target="x", value=0, lineno=9),
            Mutation(target="x", value=1, lineno=9),
        ],
        "y": [Binding(target="y", value=0, lineno=12)],
        "z": [Binding(target="z", value=0, lineno=16)],
        "i": [
            Binding(target="i", value=0, lineno=20),
            Mutation(target="i", value=1, sources={"i"}, lineno=22),
        ],
    }


def test_basic_try_except(tracer):
    tracer.init()

    try:  # SETUP_EXCEPT (3.7), SETUP_FINALLY (3.8)
        raise IndexError("error")  # RAISE_VARARGS
        a = 1  # POP_BLOCK
    except IndexError:
        pass  # POP_EXCEPT, END_FINALLY

    tracer.register()

    assert tracer.events == {}


def test_nested_try_except(tracer):
    tracer.init()

    try:
        try:
            raise IndexError
        finally:
            a = 1
    except IndexError:
        pass

    tracer.register()
    assert tracer.events == {"a": [Binding(target="a", value=1, lineno=61)]}


def test_try_except_finally(tracer):
    tracer.init()

    try:  # SETUP_EXCEPT + SETUP_FINALLY (3.7), SETUP_FINALLY (3.8)
        raise IndexError("error")  # RAISE_VARARGS
    except IndexError:
        pass  # POP_EXCEPT
    finally:  # BEGIN_FINALLY (3.8)
        b = 1  # END_FINALLY

    tracer.register()

    assert tracer.events == {"b": [Binding(target="b", value=1, lineno=77)]}


def test_break_in_finally(tracer):
    tracer.init()

    for x in range(2):
        try:
            pass
        finally:
            break  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.register()

    assert tracer.events == {"x": [Binding(target="x", value=0, lineno=87)]}


def test_break_in_finally_with_exception(tracer):
    """Tests POP_FINALLY when tos is an exception."""

    tracer.init()

    # If the finally clause executes a return, break or continue statement, the saved
    # exception is discarded.
    for x in range(2):
        try:
            raise IndexError
        finally:
            break  # BREAK_LOOP (3.7) POP_FINALLY (3.8)

    tracer.register()

    assert tracer.events == {"x": [Binding(target="x", value=0, lineno=105)]}
