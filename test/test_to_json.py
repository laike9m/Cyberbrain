import msgpack
import re


def test_repr(tracer, check_golden_file):
    class A:
        pass

    tracer.start()
    match = re.match("foo", "foobar")
    a = A()
    tracer.stop()

    frame_data = msgpack.unpackb(check_golden_file.calls[0].request.body)
    binding_match_event = frame_data["events"][0]

    assert binding_match_event["repr"] == "<re.Match object; span=(0, 3), match='foo'>"
    assert (
        binding_match_event["value"]
        == '{"repr": "<re.Match object; span=(0, 3), match=\'foo\'>"}'
    )

    binding_a_event = frame_data["events"][2]
    assert binding_a_event["repr"] == "<test_to_json.test_repr.<locals>.A object>"
    assert binding_a_event["value"] == "{}"
