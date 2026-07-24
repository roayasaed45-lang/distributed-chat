import sys
import socket
import threading


from models.client_session import ClientSession
from models.message import Message
from protocol import decode_message, encode_message
from services.state_manager import StateManager
from services.zookeeper_manager import ZooKeeperManager
from services.leader_election import LeaderElection
from services.replication import ReplicationService



class ChatServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        self.zookeeper_manager = ZooKeeperManager(
            server_id=f"server-{port}"
        )

        self.leader_election = LeaderElection(
            self.zookeeper_manager.client,
            f"server-{port}"
        )

        self.state_manager = StateManager()
        self.replication_service = ReplicationService(
            server_id=f"server-{port}",
            zookeeper_manager=self.zookeeper_manager
        )



        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

    def broadcast_message(self, message: Message):
        clients = self.state_manager.get_clients()
        encoded_message = encode_message(message)

        for client in clients:
            try:
                client.client_socket.send(encoded_message)

            except OSError:
                self.state_manager.remove_client(
                    client.client_socket
                )

    def handle_client(self, client_socket, address):
        print(f"New connection from {address}")

        username_data = client_socket.recv(1024)

        if not username_data:
            client_socket.close()
            return

        connection_type = username_data.decode("utf-8")

        if connection_type == "__SERVER__":
            client_socket.sendall(b"ACK")
            replication_data = client_socket.recv(4096)

            if not replication_data:
                client_socket.close()
                return

            replication_message = decode_message(replication_data)

            self.state_manager.add_message(replication_message)

            print(
                f"Replicated message received from leader: "
                f"{replication_message.content}"
            )

            print(
                f"Total messages: "
                f"{len(self.state_manager.get_messages())}"
            )

            client_socket.close()
            return

        username = connection_type

        client_session = ClientSession(
            client_socket=client_socket,
            username=username,
            address=address
        )

        self.state_manager.add_client(client_session)

        try:
            while True:
                data = client_socket.recv(1024)

                if not data:
                    break

                message = decode_message(data)

                self.state_manager.add_message(message)
                self.replication_service.replicate_message(message)

                print(f"Received message: {message.content}")
                print(
                    f"Total messages: "
                    f"{len(self.state_manager.get_messages())}"
                )

                self.broadcast_message(message)

        except ConnectionResetError:
            print(f"Connection lost: {address}")

        finally:
            self.state_manager.remove_client(client_socket)
            client_socket.close()
            print(f"Client disconnected: {address}")

    def start(self):
        self.zookeeper_manager.connect()
        self.leader_election.join_election()
        self.leader_election.elect_leader()
        self.leader_election.watch_election()
        

        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"Server started on {self.host}:{self.port}")

        while True:
            client_socket, address = self.server_socket.accept()

            thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, address),
                daemon=True
            )

            thread.start()


if __name__ == "__main__":
    port = 5001

    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    server = ChatServer("127.0.0.1", port)
    server.start()

