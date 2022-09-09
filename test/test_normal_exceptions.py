import pytest


def test_simple(tracer, check_golden_file):
    tracer.start()

    class CustomException(Exception):
        pass

    a = ImportError("A")
    b = CustomException("B")
    c = AssertionError()
    print(a)
    print(b)
    print(c)
    c = b
    print(c)
    d = (b, a)
    b = d[1]
    del a
    del b
    del c
    tracer.stop()


def test_throw(trace, check_golden_file):
    @trace
    def test_throw_inner():
        with pytest.raises(ZeroDivisionError):
            a = ZeroDivisionError("A")
            print(a)
            raise a

    test_throw_inner()


def test_throw_catch(tracer, check_golden_file):
    tracer.start()
    b = TypeError("B")
    try:
        try:
            a = RuntimeError("A")
            raise a
        except b.__class__ as e:
            raise e
    except Exception as e:
        b = e
    print(b)
    del b
    tracer.stop()


def test_throw_custom(trace, check_golden_file):
    class CustomException(Exception):
        pass

    @trace
    def test_throw_custom_inner():
        with pytest.raises(CustomException):
            a = CustomException("A")
            b = a
            del a
            print(b)
            raise b

    test_throw_custom_inner()


def test_throw_catch_custom(tracer, check_golden_file):
    class CustomException(Exception):
        pass

    tracer.start()
    b = CustomException("B")
    try:
        a = CustomException("A")
        raise a
    except b.__class__ as e:
        b = e
    print(b)
    del b
    tracer.stop()


def test_exceptions_with_sources(tracer, check_golden_file):
    tracer.start()
    a = "A"
    b = ImportError(a)
    c = ImportError(b)
    d = ImportError(str(b) + str(c))
    p = []
    for i in range(5):
        e = ImportError(i)
        p.append(e)
        p.append(ImportError(d))
    for i in range(5):
        del p[4 - i]
    tracer.stop()
