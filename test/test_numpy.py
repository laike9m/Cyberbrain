import numpy as np

from cyberbrain import Binding, Symbol  # noqa


def test_numpy(tracer, rpc_stub):
    tracer.start()
    x = np.array([6, 7, 8])
    tracer.stop()

    assert tracer.events == [
        Binding(
            lineno=8,
            target=Symbol("x"),
            value='{"dtype": "int64", "values": [6, 7, 8]}',
            repr="array([6, 7, 8])",
            sources=set(),
        )
    ]

    from utils import assert_GetFrame

    assert_GetFrame(rpc_stub, "test_numpy")


# Add more tests
# https://numpy.org/devdocs/user/quickstart.html
