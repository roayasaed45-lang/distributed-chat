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
        self.next_message_id = 1
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

        if connection_type == "__RECOVERY__":
            client_socket.sendall(b"ACK")

            last_id_data = client_socket.recv(1024)

            if not last_id_data:
                client_socket.close()
                return

            last_message_id = int(
                last_id_data.decode("utf-8")
            )

            missing_messages = (
                self.state_manager.get_messages_after(
                    last_message_id
                )
            )

            print(
                f"Recovery request after "
                f"message #{last_message_id}"
            )

            print(
                f"Sending {len(missing_messages)} "
                f"missing messages"
            )

            for message in missing_messages:
                encoded_message = encode_message(message)
                client_socket.sendall(encoded_message)


            client_socket.close()
            return



        if connection_type == "__SERVER__":
            client_socket.sendall(b"ACK")
            replication_data = client_socket.recv(4096)

            if not replication_data:
                client_socket.close()
                return

            replication_message = decode_message(replication_data)

            self.state_manager.add_message(replication_message)

            print(
                f"Replicated message "
                f"#{replication_message.message_id} "
                f"received from leader: "
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

                message.message_id = self.next_message_id
                self.next_message_id += 1

                self.state_manager.add_message(message)
                self.replication_service.replicate_message(message)

                print(
                    f"Received message #{message.message_id}: "
                    f"{message.content}"
                )

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

    def request_recovery(self) -> None:
        if self.leader_election.is_leader:
            return

        leader_server = self.leader_election.get_leader_server()

        if leader_server is None:
            print("No leader found for recovery")
            return

        leader_port = int(leader_server.split("-")[1])

        last_message_id = (
            self.state_manager.get_last_message_id()
        )

        try:
            with socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM
            ) as recovery_socket:

                recovery_socket.connect(
                    ("127.0.0.1", leader_port)
                )

                recovery_socket.sendall(b"__RECOVERY__")

                acknowledgement = recovery_socket.recv(1024)

                if acknowledgement != b"ACK":
                    print("Recovery request was not acknowledged")
                    return

                recovery_socket.sendall(
                    str(last_message_id).encode("utf-8")
                )

                received_data = b""

                while True:
                    data = recovery_socket.recv(4096)

                    if not data:
                        break

                    received_data += data

                recovered_count = 0

                for message_data in received_data.splitlines():
                    if not message_data:
                        continue

                    recovered_message = decode_message(
                        message_data
                    )

                    self.state_manager.add_message(
                        recovered_message
                    )

                    recovered_count += 1

                last_recovered_id = (
                    self.state_manager.get_last_message_id()
                )

                self.next_message_id = (
                        last_recovered_id + 1
                )

                print(
                    f"Recovery completed: "
                    f"{recovered_count} messages received"
                )

            print(
                f"Recovery requested from {leader_server} "
                f"after message #{last_message_id}"
            )

        except OSError as error:
            print(f"Recovery request failed: {error}")
            

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
        self.request_recovery()

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

