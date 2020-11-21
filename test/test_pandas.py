import pandas as pd

from cyberbrain import Binding, Symbol  # noqa


def test_pandas(tracer, test_server):
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

    from utils import get_value, get_os_type

    eol = get_value({"windows": r"\r\n", "linux": r"\n", "mac": "\\n"})

    assert tracer.events == [
        Binding(
            lineno=get_value({"py37": 13, "default": 8}),
            target=Symbol("baby_data_set"),
            value='[["Bob",968],["Jessica",155],["Mary",77],["John",578],["Mel",973]]',
            repr="[('Bob',968),('Jessica',155),('Mary',77),('John',578),('Mel',973)]",
            sources=set(),
        ),
        Binding(
            lineno=15,
            target=Symbol("df"),
            value=f'{{"values":"Names,Births{eol}Bob,968{eol}Jessica,155{eol}Mary,77{eol}John,578{eol}Mel,973{eol}"'
            + ',"txt":true,"meta":{"dtypes":{"Names":"object","Births":"int64"},"index":"{\\"py/object\\":\\"pandas.core.indexes.range.RangeIndex\\",\\"values\\":\\"[0,1,2,3,4]\\",\\"txt\\":true,\\"meta\\":{\\"dtype\\":\\"int64\\",\\"name\\":null}}"}}',
            repr="     Names  Births\n0      Bob     968\n1  Jessica     155\n2     Mary      77\n3     John     578\n4      Mel     973",
            sources={Symbol("baby_data_set")},
        ),
    ]

    if get_os_type() != "windows":
        test_server.assert_frame_sent("test_pandas")


# Follow https://bitbucket.org/hrojas/learn-pandas/src/master/ to add more tests.
