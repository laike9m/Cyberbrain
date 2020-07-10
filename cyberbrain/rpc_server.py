"""
Server that serves requests from UI (VSC as of now).
"""
import queue
from concurrent import futures
from threading import Timer

import grpc

from generated import communication_pb2
from generated import communication_pb2_grpc


class CyberbrainCommunicationServer(communication_pb2_grpc.CommunicationServicer):
    # Queue that stores state to be published to VSC extension.
    state_queue = queue.Queue()

    def SyncState(self, request, context):
        print(f"request come: {request} \n {context}")
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
