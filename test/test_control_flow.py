from cyberbrain import Tracer

tracer = Tracer()
tracer.init()

a = []
if a:
    x = 1
else:
    x = 2

tracer.register()


def test_if():
    assert tracer.logger.mutations == [("a", []), ("x", 2)]
