from cyberbrain import Binding, Symbol, JumpBackToLoopStart, Loop


def test_for_loop(tracer, rpc_stub):
    tracer.start_tracing()

    for i in range(2):
        for j in range(2):
            a = i + j

    tracer.stop_tracing()

    assert tracer.event_sequence == [
        Binding(lineno=7, target=Symbol("i"), value=0),
        Binding(lineno=8, target=Symbol("j"), value=0),
        Binding(
            lineno=9, target=Symbol("a"), value=0, sources={Symbol("i"), Symbol("j")}
        ),
        JumpBackToLoopStart(lineno=9, jump_target=28),
        Binding(lineno=8, target=Symbol("j"), value=1),
        Binding(
            lineno=9, target=Symbol("a"), value=1, sources={Symbol("i"), Symbol("j")}
        ),
        JumpBackToLoopStart(lineno=9, jump_target=28),
        JumpBackToLoopStart(lineno=9, jump_target=16),
        Binding(lineno=7, target=Symbol("i"), value=1),
        Binding(lineno=8, target=Symbol("j"), value=0),
        Binding(
            lineno=9, target=Symbol("a"), value=1, sources={Symbol("i"), Symbol("j")}
        ),
        JumpBackToLoopStart(lineno=9, jump_target=28),
        Binding(lineno=8, target=Symbol("j"), value=1),
        Binding(
            lineno=9, target=Symbol("a"), value=2, sources={Symbol("i"), Symbol("j")}
        ),
        JumpBackToLoopStart(lineno=9, jump_target=28),
        JumpBackToLoopStart(lineno=9, jump_target=16),
    ]
    assert tracer.loops == [
        Loop(start_offset=28, end_offset=40),
        Loop(start_offset=16, end_offset=42),
    ]
