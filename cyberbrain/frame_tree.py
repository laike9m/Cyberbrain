from __future__ import annotations

from .frame import Frame
from .generated.communication_pb2 import CursorPosition


class FrameTree:
    """A tree to store all frames. For now it's a fake implementation.

    Each node in the tree represents a frame that ever exists during program execution.
    Caller and callee frames are connected. Call order is preserved among callee frames
    of the same caller frame.

    Nodes are also indexed by frames' physical location (file name, line range).

    TODO: add indexes.
    """

    @classmethod
    def find_frames(cls, position: CursorPosition) -> list[Frame]:
        pass

    @classmethod
    def get_frame(cls, frame_id: int) -> Frame:
        pass
