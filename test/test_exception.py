from cyberbrain import Binding, InitialValue, Symbol, Mutation  # noqa


def test_implicit_exception(trace):
    @trace
    def test_zero_division():
        try:
            a = 1 / 0
        except ZeroDivisionError:
            print("got error")

    test_zero_division()
