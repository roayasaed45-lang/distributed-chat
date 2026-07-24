import socket

from models.message import Message
from protocol import encode_message
from services.zookeeper_manager import ZooKeeperManager


class ReplicationService:
    def __init__(
        self,
        server_id: str,
        zookeeper_manager: ZooKeeperManager
    ):
        self.server_id = server_id
        self.zookeeper_manager = zookeeper_manager

    def replicate_message(self, message: Message) -> None:
        live_servers = self.zookeeper_manager.get_live_servers()

        followers = [
            server
            for server in live_servers
            if server != self.server_id
        ]

        replication_message = Message(
            message_type="replication",
            username=message.username,
            content=message.content,
            message_id=message.message_id,
            timestamp=message.timestamp
        )

        encoded_message = encode_message(replication_message)

        for follower in followers:
            port = int(follower.split("-")[1])

            try:
                with socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM
                ) as replication_socket:

                    replication_socket.connect(
                        ("127.0.0.1", port)
                    )

                    replication_socket.sendall(b"__SERVER__")

                    acknowledgement = replication_socket.recv(1024)

                    if acknowledgement != b"ACK":
                        print(f"No ACK received from {follower}")
                        continue

                    replication_socket.sendall(encoded_message)

                print(
                    f"Replicated message to "
                    f"{follower}"
                )

            except OSError as error:
                print(
                    f"Failed to replicate to "
                    f"{follower}: {error}"
                )


