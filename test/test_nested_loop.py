from cyberbrain import Binding, Symbol, JumpBackToLoopStart, Loop
from utils import get_value


def test_nested_loop(tracer, rpc_stub):
    tracer.start_tracing()

    for i in range(2):
        for j in range(2):
            a = i + j

    tracer.stop_tracing()

    assert tracer.event_sequence == [
        Binding(lineno=8, target=Symbol("i"), value=0),
        Binding(lineno=9, target=Symbol("j"), value=0),
        Binding(
            lineno=10, target=Symbol("a"), value=0, sources={Symbol("i"), Symbol("j")}
        ),
        JumpBackToLoopStart(lineno=10, jump_target=get_value({"py38": 28, "py37": 32})),
        Binding(lineno=9, target=Symbol("j"), value=1),
        Binding(
            lineno=10, target=Symbol("a"), value=1, sources={Symbol("i"), Symbol("j")}
        ),
        JumpBackToLoopStart(lineno=10, jump_target=get_value({"py38": 28, "py37": 32})),
        JumpBackToLoopStart(lineno=10, jump_target=get_value({"py38": 16, "py37": 18})),
        Binding(lineno=8, target=Symbol("i"), value=1),
        Binding(lineno=9, target=Symbol("j"), value=0),
        Binding(
            lineno=10, target=Symbol("a"), value=1, sources={Symbol("i"), Symbol("j")}
        ),
        JumpBackToLoopStart(lineno=10, jump_target=get_value({"py38": 28, "py37": 32})),
        Binding(lineno=9, target=Symbol("j"), value=1),
        Binding(
            lineno=10, target=Symbol("a"), value=2, sources={Symbol("i"), Symbol("j")}
        ),
        JumpBackToLoopStart(lineno=10, jump_target=get_value({"py38": 28, "py37": 32})),
        JumpBackToLoopStart(lineno=10, jump_target=get_value({"py38": 16, "py37": 18})),
    ]
    assert tracer.loops == [
        Loop(
            start_offset=get_value({"py38": 28, "py37": 32}),
            end_offset=get_value({"py38": 40, "py37": 44}),
        ),
        Loop(
            start_offset=get_value({"py38": 16, "py37": 18}),
            end_offset=get_value({"py38": 42, "py37": 48}),
        ),
    ]
