from cyberbrain import Binding, Symbol, JumpBackToLoopStart, Loop, InitialValue, Return
from utils import get_value


def test_while_loop(tracer, check_golden_file):
    tracer.start()

    i = 0
    while i < 2:
        a = i
        i += 1

    i = 0
    while i < 2:
        break  # BREAK_LOOP (3.7), JUMP_ABSOLUTE (>=3.8)

    i = 0
    while i < 1:
        i += 1
        continue  # CONTINUE_LOOP (3.7), JUMP_ABSOLUTE (>=3.8)

    i = 0
    while i < 2:
        i += 1
        if i == 1:  # This jumps to the end of the iteration, not out of loop.
            continue

    i = 0
    while i < 2:
        i += 1
        if i == 1:
            break

    while True:
        break
    else:
        a = 1

    while False:
        pass
    else:
        a = 1

    tracer.stop()

    assert tracer.loops == [
        Loop(
            start_offset=get_value({"default": 12, "py37": 14}),
            end_offset=get_value({"default": 32, "py37": 34}),
            start_lineno=9,
        ),
        Loop(
            start_offset=get_value({"default": 54, "py37": 64}),
            end_offset=get_value({"default": 70, "py37": 80}),
            start_lineno=18,
        ),
        Loop(
            start_offset=get_value({"default": 78, "py37": 92}),
            end_offset=get_value({"default": 102, "py37": 116}),
            start_lineno=23,
        ),
    ]


def test_while_jump_to_zero(trace, check_golden_file):
    @trace
    def while_jump_to_zero(count):
        while count > 0:
            count -= 1

    while_jump_to_zero(2)
