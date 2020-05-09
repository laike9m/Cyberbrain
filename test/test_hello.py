from cyberbrain import Creation, Mutation


def test_hello(tracer):
    tracer.init()
    x = "hello world"  # LOAD_CONST, STORE_FAST
    y = x  # LOAD_FAST, STORE_FAST
    x, y = y, x  # ROT_TWO
    tracer.register()

    assert tracer.events == {
        "x": [
            Creation(target="x", value="hello world"),
            Mutation(target="x", value="hello world", sources={"y"}),
        ],
        "y": [
            Creation(target="y", value="hello world", sources={"x"}),
            Mutation(target="y", value="hello world", sources={"x"}),
        ],
    }
