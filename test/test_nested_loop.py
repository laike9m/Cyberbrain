from cyberbrain import Binding, Symbol, JumpBackToLoopStart, Loop
from utils import get_value


def test_nested_loop(tracer, check_golden_file):
    tracer.start()

    for i in range(2):
        for j in range(2):
            a = i + j

    tracer.stop()

    assert tracer.loops == [
        Loop(
            start_offset=get_value({"default": 28, "py37": 32}),
            end_offset=get_value({"default": 40, "py37": 44}),
            start_lineno=9,
        ),
        Loop(
            start_offset=get_value({"default": 16, "py37": 18}),
            end_offset=get_value({"default": 42, "py37": 48}),
            start_lineno=8,
        ),
    ]
