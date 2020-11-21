import pytest


def test_run_in_test(trace):
    @trace
    def test_raise_error():
        s = "hello world"
        assert s.split() == ["hello", "world"]
        # cb 没办法处理从 42 -> 60 的跳转，这里有 exception
        with pytest.raises(TypeError):
            s.split(2)

    test_raise_error()
