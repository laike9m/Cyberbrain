import numpy as np

from cyberbrain import Binding, Symbol  # noqa


def test_numpy(tracer, check_golden_file):
    tracer.start()
    x = np.array([6, 7, 8])
    tracer.stop()

    from utils import get_value

    int_type = get_value({"windows": "int32", "linux": "int64", "mac": "int64"})


# Add more tests
# https://numpy.org/devdocs/user/quickstart.html
