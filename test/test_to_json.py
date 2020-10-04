import re


def test_repr(tracer, rpc_stub):
    tracer.start()
    match = re.match("foo", "foobar")
    tracer.stop()

    from utils import return_GetFrame

    frame_proto = return_GetFrame(rpc_stub, "test_repr")
    binding_match_event = frame_proto.events[0]

    assert (
        binding_match_event.binding.repr
        == "<re.Match object; span=(0, 3), match='foo'>"
    )
    assert (
        binding_match_event.binding.value
        == '{"repr": "<re.Match object; span=(0, 3), match=\'foo\'>"}'
    )
