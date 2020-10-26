from cyberbrain import Binding, InitialValue, Symbol, JumpBackToLoopStart


def test_with(tracer, rpc_stub):
    class ContextManagerNoReturn:
        def __enter__(self):
            pass

        def __exit__(self, *unused):
            pass

    class ContextManagerWithReturn:
        def __enter__(self):
            return 2

        def __exit__(self, *unused):
            pass

    tracer.start()

    with ContextManagerNoReturn():  # SETUP_WITH,WITH_CLEANUP_START,WITH_CLEANUP_FINISH
        a = 1

    with ContextManagerWithReturn() as b:
        pass

    with ContextManagerWithReturn() as c, ContextManagerNoReturn() as d:
        pass

    with ContextManagerWithReturn() as e:
        with ContextManagerWithReturn() as f:
            pass

    with ContextManagerNoReturn():
        try:
            g = 1
            raise RuntimeError
        except RuntimeError:
            pass

    for i in range(1):
        with ContextManagerNoReturn():
            continue

    tracer.stop()

    expected_events = [
        InitialValue(
            lineno=21,
            target=Symbol("ContextManagerNoReturn"),
            value='{"py/type": "test_with.test_with.<locals>.ContextManagerNoReturn"}',
        ),
        Binding(lineno=22, target=Symbol("a"), value="1", sources=set()),
        InitialValue(
            lineno=24,
            target=Symbol("ContextManagerWithReturn"),
            value='{"py/type": "test_with.test_with.<locals>.ContextManagerWithReturn"}',
        ),
        Binding(
            lineno=24,
            target=Symbol("b"),
            value="2",
            sources={Symbol("ContextManagerWithReturn")},
        ),
        Binding(
            lineno=27,
            target=Symbol("c"),
            value="2",
            sources={Symbol("ContextManagerWithReturn")},
        ),
        Binding(
            lineno=27,
            target=Symbol("d"),
            value="null",
            sources={Symbol("ContextManagerNoReturn")},
        ),
        Binding(
            lineno=30,
            target=Symbol("e"),
            value="2",
            sources={Symbol("ContextManagerWithReturn")},
        ),
        Binding(
            lineno=31,
            target=Symbol("f"),
            value="2",
            sources={Symbol("ContextManagerWithReturn")},
        ),
        Binding(lineno=36, target=Symbol("g"), value="1", sources=set()),
        Binding(lineno=41, target=Symbol("i"), value="0", sources=set()),
    ]

    from utils import python_version, get_value

    if python_version >= "py38":
        expected_events.append(
            JumpBackToLoopStart(
                lineno=43, jump_target=get_value({"py38": 208, "default": 352})
            )
        )

    assert tracer.events == expected_events

    from utils import assert_GetFrame

    assert_GetFrame(rpc_stub, "test_with")
