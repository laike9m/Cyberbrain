from cyberbrain import Binding, Symbol, JumpBackToLoopStart, Loop
from utils import get_value, assert_GetFrame


def test_while_loop(tracer, rpc_stub):
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

    assert tracer.events == [
        Binding(lineno=8, target=Symbol("i"), value=0),
        Binding(lineno=10, target=Symbol("a"), value=0, sources={Symbol("i")}),
        Binding(lineno=11, target=Symbol("i"), value=1, sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=11, jump_target=get_value({"py38": 12, "py37": 14})),
        Binding(lineno=10, target=Symbol("a"), value=1, sources={Symbol("i")}),
        Binding(lineno=11, target=Symbol("i"), value=2, sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=11, jump_target=get_value({"py38": 12, "py37": 14})),
        ##
        Binding(lineno=13, target=Symbol("i"), value=0),
        Binding(lineno=17, target=Symbol("i"), value=0),
        Binding(lineno=19, target=Symbol("i"), value=1, sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=20, jump_target=get_value({"py38": 54, "py37": 64})),
        ##
        Binding(lineno=22, target=Symbol("i"), value=0),
        Binding(lineno=24, target=Symbol("i"), value=1, sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=26, jump_target=get_value({"py38": 78, "py37": 92})),
        Binding(lineno=24, target=Symbol("i"), value=2, sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=25, jump_target=get_value({"py38": 78, "py37": 92})),
        ##
        Binding(lineno=28, target=Symbol("i"), value=0),
        Binding(lineno=30, target=Symbol("i"), value=1, sources={Symbol("i")}),
        Binding(lineno=42, target=Symbol("a"), value=1),
    ]
    assert tracer.loops == [
        Loop(
            start_offset=get_value({"py38": 12, "py37": 14}),
            end_offset=get_value({"py38": 32, "py37": 34}),
        ),
        Loop(
            start_offset=get_value({"py38": 54, "py37": 64}),
            end_offset=get_value({"py38": 70, "py37": 80}),
        ),
        Loop(
            start_offset=get_value({"py38": 78, "py37": 92}),
            end_offset=get_value({"py38": 102, "py37": 116}),
        ),
    ]
    assert_GetFrame(rpc_stub, "test_while_loop")
