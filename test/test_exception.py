import pytest

from cyberbrain import Binding, InitialValue, Symbol, Mutation  # noqa


def test_implicit_exception(trace):
    @trace
    def zero_division():
        try:
            a = 1 / 0
        except ZeroDivisionError:
            print("got error")

    zero_division()


def test_assert_raise(trace):
    @trace
    def raise_error():
        s = "hello world"
        assert s.split() == ["hello", "world"]
        with pytest.raises(TypeError):
            s.split(2)

    raise_error()

    print(trace.events)
