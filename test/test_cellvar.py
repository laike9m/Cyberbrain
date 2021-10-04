from cyberbrain import Binding, InitialValue, Symbol, Deletion


def test_deref(tracer, check_golden_file):

    a = 1

    def test_deref_func():
        tracer.start()
        nonlocal a
        print(a)  # LOAD_DEREF
        a = 2  # STORE_DEREF
        del a  # DELETE_DEREF
        tracer.stop()

    test_deref_func()


def test_closure(tracer, check_golden_file):
    tracer.start()

    a = 1  # LOAD_CLASSDEREF

    class Foo:
        print(a)  # LOAD_CLOSURE

    class Bar(Foo):  # LOAD_CLOSURE. If we remove super(Bar, self) it becomes LOAD_CONST
        def __init__(self):
            super(Bar, self).__init__()

    tracer.stop()
