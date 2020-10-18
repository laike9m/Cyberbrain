import numpy as np

from cyberbrain import Binding, Symbol  # noqa


def test_numpy(tracer, rpc_stub):
    tracer.start()
    x = np.array([6, 7, 8])
    tracer.stop()

    from utils import get_os_type, get_value

    int_type = get_value({"windows": "int32", "linux": "int64", "mac": "int64"})

    assert tracer.events == [
        Binding(
            lineno=8,
            target=Symbol("x"),
            value=f'{{"dtype": "{int_type}", "values": [6, 7, 8]}}',
            repr="array([6, 7, 8])",
            sources=set(),
        )
    ]

    from utils import assert_GetFrame

    if get_os_type() != "windows":
        assert_GetFrame(rpc_stub, "test_numpy")


# Add more tests
# https://numpy.org/devdocs/user/quickstart.html
