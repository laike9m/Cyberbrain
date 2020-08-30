from cyberbrain import Binding, Symbol, JumpBackToLoopStart, Loop
from utils import get_value


def test_for_loop(tracer, rpc_stub):
    tracer.start_tracing()

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

    tracer.stop_tracing()

    from cyberbrain import pprint

    pprint(tracer.events)

    expected_events = [
        Binding(target=Symbol("i"), value=0, lineno=8),
        Binding(target=Symbol("a"), value=0, lineno=9, sources={Symbol("i")}),
        JumpBackToLoopStart(jump_target=get_value({"py38": 16, "py37": 18}), lineno=9),
        Binding(target=Symbol("i"), value=1, lineno=8),
        Binding(target=Symbol("a"), value=1, lineno=9, sources={Symbol("i")}),
        JumpBackToLoopStart(jump_target=get_value({"py38": 16, "py37": 18}), lineno=9),
        Binding(target=Symbol("i"), value=0, lineno=11),
        Binding(target=Symbol("i"), value=0, lineno=15),
        JumpBackToLoopStart(jump_target=get_value({"py38": 56, "py37": 64}), lineno=16),
        Binding(target=Symbol("i"), value=0, lineno=19),
        JumpBackToLoopStart(jump_target=get_value({"py38": 76, "py37": 88}), lineno=21),
        Binding(target=Symbol("i"), value=1, lineno=19),
        JumpBackToLoopStart(jump_target=get_value({"py38": 76, "py37": 88}), lineno=20),
        Binding(target=Symbol("i"), value=0, lineno=23),
        JumpBackToLoopStart(
            jump_target=get_value({"py38": 100, "py37": 116}), lineno=24
        ),
        Binding(target=Symbol("i"), value=1, lineno=23),
        Binding(target=Symbol("i"), value=0, lineno=27),
        Binding(target=Symbol("i"), value=0, lineno=32),
        JumpBackToLoopStart(
            jump_target=get_value({"py38": 148, "py37": 168}), lineno=33
        ),
        Binding(target=Symbol("a"), value=1, lineno=35),
    ]
    for index, event in enumerate(tracer.events):
        assert event == expected_events[index], f"{event} {expected_events[index]}"
    print(tracer.loops)
    assert tracer.loops == [
        Loop(
            start_offset=get_value({"py38": 16, "py37": 18}),
            end_offset=get_value({"py38": 24, "py37": 26}),
        ),
        Loop(
            start_offset=get_value({"py38": 56, "py37": 64}),
            end_offset=get_value({"py38": 60, "py37": 68}),
        ),
        Loop(
            start_offset=get_value({"py38": 76, "py37": 88}),
            end_offset=get_value({"py38": 88, "py37": 100}),
        ),
        Loop(
            start_offset=get_value({"py38": 100, "py37": 116}),
            end_offset=get_value({"py38": 110, "py37": 126}),
        ),
        Loop(
            start_offset=get_value({"py38": 148, "py37": 168}),
            end_offset=get_value({"py38": 152, "py37": 172}),
        ),
    ]
