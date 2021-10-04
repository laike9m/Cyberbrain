import pandas as pd

from cyberbrain import Binding, Symbol  # noqa


def test_pandas(tracer, check_golden_file):
    tracer.start()
    baby_data_set = [
        ("Bob", 968),
        ("Jessica", 155),
        ("Mary", 77),
        ("John", 578),
        ("Mel", 973),
    ]
    df = pd.DataFrame(data=baby_data_set, columns=["Names", "Births"])
    tracer.stop()

    from utils import get_value

    eol = get_value({"windows": r"\r\n", "linux": r"\n", "mac": "\\n"})


# Follow https://bitbucket.org/hrojas/learn-pandas/src/master/ to add more tests.
