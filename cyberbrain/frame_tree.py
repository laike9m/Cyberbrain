from __future__ import annotations

from .frame import Frame
from .generated.communication_pb2 import CursorPosition


class FrameTree:
    """A tree to store all frames. For now it's a fake implementation.

    Each node in the tree represents a frame that ever exists during program execution.
    Caller and callee frames are connected. Call order is preserved among callee frames
    of the same caller frame.

    Nodes are also indexed by frames' physical location (file name, line range).

    TODO:
        - Add indexes.
        - Implement frame search.
    """

    # Keyed by frame ID.
    frames: dict[str, Frame] = dict()

    @classmethod
    def add_frame(cls, frame_id, frame: Frame):
        cls.frames[frame_id] = frame
        print(frame_id, frame)

    @classmethod
    def find_frames(cls, position: CursorPosition) -> list[Frame]:
        """
        Right now it's a fake implementation, where we return the only existing frame.
        """
        assert cls.frames
        return [next(iter(cls.frames.values()))]

    @classmethod
    def get_frame(cls, frame_id) -> Frame:
        assert cls.frames
        return cls.frames[frame_id]
