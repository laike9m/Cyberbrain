"""
Server that serves requests from UI (VSC as of now).
"""
import queue
from concurrent import futures
from threading import Timer

import grpc

from .frame_tree import FrameTree
from .generated import communication_pb2
from .generated import communication_pb2_grpc


class CyberbrainCommunicationServicer(communication_pb2_grpc.CommunicationServicer):
    # Queue that stores state to be published to VSC extension.
    state_queue = queue.Queue()

    def SyncState(self, request, context):
        print(f"request come: {type(request)} {request}")
        yield communication_pb2.State(status=communication_pb2.State.SERVER_READY)
        Timer(
            5,  # seconds
            lambda: CyberbrainCommunicationServicer.state_queue.put(
                # Simulates when program hits cyberbrain.register().
                communication_pb2.State(
                    status=communication_pb2.State.EXECUTION_COMPLETE
                )
            ),
        ).start()
        while True:
            yield self.state_queue.get()  # block forever.

    def FindFrames(self, request, context):
        frames = FrameTree.find_frames(request)
        raise NotImplementedError

    def GetFrame(self, request, context) -> communication_pb2.Frame:
        # TODO: return accumulated_events + tracing result.
        #  1. Get a frame from frame tree.
        #  2. Get accumulated_events + tracing result.
        #  3. Transforms to Frame proto.
        pass


class Server:
    def __init__(self):
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        communication_pb2_grpc.add_CommunicationServicer_to_server(
            CyberbrainCommunicationServicer(), self._server
        )

    def serve(self, block: bool, port: int = 50051):
        print("Starting grpc server...")
        self._server.add_insecure_port(f"[::]:{port}")
        self._server.start()
        if block:
            self._server.wait_for_termination()

    def stop(self):
        self._server.stop(grace=None)  # Abort all active RPCs immediately.


if __name__ == "__main__":
    server = Server()
    server.serve(block=True)
