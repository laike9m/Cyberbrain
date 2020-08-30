from cyberbrain import Binding, Symbol, JumpBackToLoopStart, Loop


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
        if i == 0:  # This jumps to the end of the iteration, not out of loop.
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

    assert tracer.event_sequence == [
        Binding(target=Symbol("i"), value=0, lineno=7),
        Binding(target=Symbol("a"), value=0, lineno=8, sources={Symbol("i")}),
        JumpBackToLoopStart(jump_target=16, lineno=8),
        Binding(target=Symbol("i"), value=1, lineno=7),
        Binding(target=Symbol("a"), value=1, lineno=8, sources={Symbol("i")}),
        JumpBackToLoopStart(jump_target=16, lineno=8),
        Binding(target=Symbol("i"), value=0, lineno=10),
        Binding(target=Symbol("i"), value=0, lineno=14),
        JumpBackToLoopStart(jump_target=56, lineno=15),
        Binding(target=Symbol("i"), value=0, lineno=18),
        JumpBackToLoopStart(jump_target=76, lineno=20),
        Binding(target=Symbol("i"), value=1, lineno=18),
        JumpBackToLoopStart(jump_target=76, lineno=20),
        Binding(target=Symbol("i"), value=0, lineno=22),
        JumpBackToLoopStart(jump_target=100, lineno=24),
        Binding(target=Symbol("i"), value=1, lineno=22),
        Binding(target=Symbol("i"), value=0, lineno=26),
        Binding(target=Symbol("i"), value=0, lineno=31),
        JumpBackToLoopStart(jump_target=148, lineno=32),
        Binding(target=Symbol("a"), value=1, lineno=34),
    ]
    assert tracer.loops == [
        Loop(start_offset=16, end_offset=24),
        Loop(start_offset=56, end_offset=60),
        Loop(start_offset=76, end_offset=90),
        Loop(start_offset=100, end_offset=116),
        Loop(start_offset=148, end_offset=152),
    ]
