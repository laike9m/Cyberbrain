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


class CyberbrainCommunicationServer(communication_pb2_grpc.CommunicationServicer):
    # Queue that stores state to be published to VSC extension.
    state_queue = queue.Queue()

    def SyncState(self, request, context):
        print(f"request come: {type(request)} {request}")
        yield communication_pb2.State(status=communication_pb2.State.SERVER_READY)
        Timer(
            5,  # seconds
            lambda: CyberbrainCommunicationServer.state_queue.put(
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
        pass


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    communication_pb2_grpc.add_CommunicationServicer_to_server(
        CyberbrainCommunicationServer(), server
    )
    server.add_insecure_port("[::]:50051")
    print("Starting grpc server...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
