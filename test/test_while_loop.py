from cyberbrain import Binding, Symbol, JumpBackToLoopStart


def test_while_loop(tracer, rpc_stub):
    tracer.start_tracing()

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

    tracer.stop_tracing()

    assert tracer.event_sequence == [
        Binding(lineno=7, target=Symbol("i"), value=0),
        Binding(lineno=9, target=Symbol("a"), value=0, sources={Symbol("i")}),
        Binding(lineno=10, target=Symbol("i"), value=1, sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=10, jump_target=12),
        Binding(lineno=9, target=Symbol("a"), value=1, sources={Symbol("i")}),
        Binding(lineno=10, target=Symbol("i"), value=2, sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=10, jump_target=12),
        ##
        Binding(lineno=12, target=Symbol("i"), value=0),
        Binding(lineno=16, target=Symbol("i"), value=0),
        Binding(lineno=18, target=Symbol("i"), value=1, sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=19, jump_target=54),
        ##
        Binding(lineno=21, target=Symbol("i"), value=0),
        Binding(lineno=23, target=Symbol("i"), value=1, sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=25, jump_target=78),
        Binding(lineno=23, target=Symbol("i"), value=2, sources={Symbol("i")}),
        JumpBackToLoopStart(lineno=25, jump_target=78),
        ##
        Binding(lineno=27, target=Symbol("i"), value=0),
        Binding(lineno=29, target=Symbol("i"), value=1, sources={Symbol("i")}),
        Binding(lineno=41, target=Symbol("a"), value=1),
    ]
    assert tracer.loops == [
        Loop(start_offset=12, end_offset=32),
        Loop(start_offset=54, end_offset=70),
        Loop(start_offset=78, end_offset=104),
    ]

    import pprint

    pprint.pprint(tracer.loops)
