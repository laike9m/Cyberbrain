import re


def test_repr(tracer, test_server):
    class A:
        pass

    tracer.start()
    match = re.match("foo", "foobar")
    a = A()
    tracer.stop()

    test_server.assert_frame_sent("test_repr")
    frame_proto = test_server.received_frames["test_repr"]
    binding_match_event = frame_proto.events[0]

    assert (
        binding_match_event.binding.repr
        == "<re.Match object; span=(0, 3), match='foo'>"
    )
    assert (
        binding_match_event.binding.value
        == '{"repr": "<re.Match object; span=(0, 3), match=\'foo\'>"}'
    )

    binding_a_event = frame_proto.events[2]
    assert binding_a_event.binding.repr == "<test_to_json.test_repr.<locals>.A object>"
    assert binding_a_event.binding.value == "{}"
