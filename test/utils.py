from __future__ import annotations

import os
import sys

from google.protobuf import text_format

from cyberbrain.generated import communication_pb2, communication_pb2_grpc


def get_value(value_dict: dict[str, any]):
    """Accept an argument like {'py37': 1, 'py38': 2}.

    Used for version-dependent tests.
    """

    if sys.version_info[:2] == (3, 7):
        return value_dict["py37"]
    if sys.version_info[:2] == (3, 8):
        return value_dict["py38"]
    else:
        raise Exception(
            f"please modify the get_value function to support version {sys.version}"
        )


def assert_GetFrame(
    rpc_stub: communication_pb2_grpc.CommunicationStub, frame_name: str
):
    # print(rpc_stub.GetFrame(communication_pb2.FrameLocater(frame_name=frame_name)))
    golden_filepath = f"test/data/{frame_name}.pbtext"

    # Generates golden data.
    if not os.path.exists(golden_filepath):
        with open(golden_filepath, "wt") as f:
            f.write("# proto-file: communication.proto\n# proto-message: Frame\n\n")
            f.write(
                str(
                    rpc_stub.GetFrame(
                        communication_pb2.FrameLocater(frame_name=frame_name)
                    )
                )
            )
        return

    # Assuming run in root directory.
    with open(golden_filepath, "rt") as f:
        response_text = f.read()

    assert rpc_stub.GetFrame(
        communication_pb2.FrameLocater(frame_name=frame_name)
    ) == text_format.Parse(response_text, communication_pb2.Frame())
