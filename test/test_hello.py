from cyberbrain import Creation, Mutation


def test_hello(tracer, rpc_stub):
    tracer.init()
    x = "hello world"  # LOAD_CONST, STORE_FAST
    y = x  # LOAD_FAST, STORE_FAST
    x, y = y, x  # ROT_TWO or BUILD_TUPLE. I don't know how Python compiler decides it.
    tracer.register()

    assert tracer.events == {
        "x": [
            Creation(target="x", value="hello world", lineno=6),
            Mutation(target="x", value="hello world", sources={"y"}, lineno=8),
        ],
        "y": [
            Creation(target="y", value="hello world", sources={"x"}, lineno=7),
            Mutation(target="y", value="hello world", sources={"x"}, lineno=8),
        ],
    }

    from utils import assert_GetFrame

    assert_GetFrame(rpc_stub, "test_hello")
