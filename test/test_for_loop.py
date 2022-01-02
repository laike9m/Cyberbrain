from cyberbrain import Binding, Symbol, JumpBackToLoopStart, Loop
from utils import get_value


def test_for_loop(tracer, check_golden_file):
    tracer.start()

    for i in range(2):  # SETUP_LOOP (3.7), GET_ITER, FOR_ITER
        a = i  # POP_BLOCK (3.7)

    for i in range(2):
        break  # BREAK_LOOP (3.7), JUMP_ABSOLUTE (>=3.8)
        a = 1

    for i in range(1):
        continue  # CONTINUE_LOOP (3.7), JUMP_ABSOLUTE (>=3.8)
        a = 1

    for i in range(2):
        if i == 0:  # This jumps directly to FOR_ITER
            continue

    for i in range(2):
        if i == 1:
            break

    for i in range(1):
        break
    else:
        a = 1

    for i in range(1):  # One iteration loop.
        pass
    else:
        a = 1

    tracer.stop()

    assert tracer.loops == [
        Loop(
            start_offset=get_value({"default": 16, "py37": 18}),
            end_offset=get_value({"default": 24, "py37": 26}),
            start_lineno=8,
            end_lineno=9,
        ),
        Loop(
            start_offset=get_value({"default": 56, "py37": 64, "py310": 48}),
            end_offset=get_value({"default": 60, "py37": 68, "py310": 52}),
            start_lineno=15,
            end_lineno=16,
        ),
        Loop(
            start_offset=get_value({"default": 76, "py37": 88, "py310": 62}),
            end_offset=get_value({"default": 88, "py37": 100, "py310": 76}),
            start_lineno=19,
            end_lineno=21,
        ),
        Loop(
            start_offset=get_value({"default": 100, "py37": 116, "py310": 86}),
            end_offset=get_value({"default": 110, "py37": 126, "py310": 102}),
            start_lineno=23,
            # TODO: Correct lineno is 25, see if we can fix this for older versions.
            end_lineno=get_value({"default": 25, "py37": 24, "py38": 24, "py39": 24}),
        ),
        Loop(
            start_offset=get_value({"default": 148, "py37": 168, "py310": 132}),
            end_offset=get_value({"default": 152, "py37": 172, "py310": 136}),
            start_lineno=32,
            end_lineno=33,
        ),
    ]
