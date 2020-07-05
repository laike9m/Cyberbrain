"""
Server that serves requests from UI (VSC as of now).
"""
from concurrent import futures

import grpc

# TODO: Eventually we want to use relative import.
import communication_pb2_grpc
import communication_pb2


class CyberbrainCommunicationServer(communication_pb2_grpc.CommunicationServicer):
    def SyncState(self, request, context):
        print(f"request come: {request} \n {context}")
        return communication_pb2.State(status="server good")


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
