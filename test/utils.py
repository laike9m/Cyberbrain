from google.protobuf import text_format

from cyberbrain.generated import communication_pb2, communication_pb2_grpc


def assert_GetFrame(
    rpc_stub: communication_pb2_grpc.CommunicationStub, frame_name: str
):
    print(rpc_stub.GetFrame(communication_pb2.FrameLocater(frame_name=frame_name)))

    # Assuming run in root directory.
    with open(f"test/data/{frame_name}.pbtext", "rt") as f:
        response_text = f.read()

    assert rpc_stub.GetFrame(
        communication_pb2.FrameLocater(frame_name=frame_name)
    ) == text_format.Parse(response_text, communication_pb2.Frame())
