from cyberbrain import Binding, Symbol


def test_list_comprehension(tracer, mocked_responses):
    tracer.start()

    n = 2
    x = [i for i in range(n)]  # MAKE_FUNCTION,GET_ITER,CALL_FUNCTION
    lst = ["foo", "bar"]
    x = [e for e in lst]

    tracer.stop()

    assert tracer.events == [
        Binding(target=Symbol("n"), value="2", lineno=7),
        Binding(target=Symbol("x"), value="[0,1]", lineno=8, sources={Symbol("n")}),
        Binding(target=Symbol("lst"), value='["foo","bar"]', lineno=9),
        Binding(
            target=Symbol("x"),
            value='["foo","bar"]',
            lineno=10,
            sources={Symbol("lst")},
        ),
    ]
