from cyberbrain import Binding, InitialValue, Symbol, JumpBackToLoopStart


def test_with(tracer, check_golden_file):
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
