import socket
import threading

from models.message import Message
from services.state_manager import StateManager


class ChatServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        self.state_manager = StateManager()
        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

    def handle_client(self, client_socket, address):
        print(f"New connection from {address}")
        self.state_manager.add_client(client_socket)

        try:
            while True:
                data = client_socket.recv(1024)

                if not data:
                    break

                text = data.decode("utf-8")

                message = Message(
                    message_type="CHAT",
                    username=str(address),
                    content=text
                )

                self.state_manager.add_message(message)

                print(f"Received message: {text}")
                print(
                    f"Total messages: "
                    f"{len(self.state_manager.get_messages())}"
                )

        except ConnectionResetError:
            print(f"Connection lost: {address}")

        finally:
            self.state_manager.remove_client(client_socket)
            client_socket.close()
            print(f"Client disconnected: {address}")

    def start(self):
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
    server = ChatServer("127.0.0.1", 5001)
    server.start()

