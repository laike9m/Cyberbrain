from cyberbrain import Binding, Symbol, JumpBackToLoopStart, Loop, InitialValue, Return
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
        Binding(lineno=8, target=Symbol("i"), value="0"),
        Binding(lineno=10, target=Symbol("a"), value="0", sources={Symbol("i")}),
        Binding(lineno=11, target=Symbol("i"), value="1", sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=11, jump_target=get_value({"py38": 12, "py37": 14})),
        Binding(lineno=10, target=Symbol("a"), value="1", sources={Symbol("i")}),
        Binding(lineno=11, target=Symbol("i"), value="2", sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=11, jump_target=get_value({"py38": 12, "py37": 14})),
        ##
        Binding(lineno=13, target=Symbol("i"), value="0"),
        Binding(lineno=17, target=Symbol("i"), value="0"),
        Binding(lineno=19, target=Symbol("i"), value="1", sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=20, jump_target=get_value({"py38": 54, "py37": 64})),
        ##
        Binding(lineno=22, target=Symbol("i"), value="0"),
        Binding(lineno=24, target=Symbol("i"), value="1", sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=26, jump_target=get_value({"py38": 78, "py37": 92})),
        Binding(lineno=24, target=Symbol("i"), value="2", sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=25, jump_target=get_value({"py38": 78, "py37": 92})),
        ##
        Binding(lineno=28, target=Symbol("i"), value="0"),
        Binding(lineno=30, target=Symbol("i"), value="1", sources={Symbol("i")}),
        Binding(lineno=42, target=Symbol("a"), value="1"),
    ]
    assert tracer.loops == [
        Loop(
            start_offset=get_value({"py38": 12, "py37": 14}),
            end_offset=get_value({"py38": 32, "py37": 34}),
            start_lineno=9,
        ),
        Loop(
            start_offset=get_value({"py38": 54, "py37": 64}),
            end_offset=get_value({"py38": 70, "py37": 80}),
            start_lineno=18,
        ),
        Loop(
            start_offset=get_value({"py38": 78, "py37": 92}),
            end_offset=get_value({"py38": 102, "py37": 116}),
            start_lineno=23,
        ),
    ]
    assert_GetFrame(rpc_stub, "test_while_loop")


def test_while_jump_to_zero(trace):
    @trace
    def while_jump_to_zero(count):
        while count > 0:
            count -= 1

    while_jump_to_zero(2)

    assert trace.events == [
        InitialValue(
            lineno=93,
            target=Symbol("count"),
            value="2",
            repr="2",
        ),
        Binding(
            lineno=94,
            target=Symbol("count"),
            value="1",
            repr="1",
            sources={Symbol("count")},
        ),
        JumpBackToLoopStart(lineno=94, jump_target=0),
        Binding(
            lineno=94,
            target=Symbol("count"),
            value="0",
            repr="0",
            sources={Symbol("count")},
        ),
        JumpBackToLoopStart(lineno=94, jump_target=0),
        Return(
            lineno=94,
            value="null",
            repr="None",
            sources=set(),
        ),
    ]
