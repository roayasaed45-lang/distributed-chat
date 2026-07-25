import socket
import threading

from models.message import Message
from protocol import decode_message, encode_message
from services.client_discovery import ClientDiscovery



class ChatClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.username = input("Enter your username: ")
        self.discovery = ClientDiscovery()
        self.discovery.connect()



        self.client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)

                if not data:
                    break

                message = decode_message(data)

                print(
                    f"\n{message.username}: {message.content}"
                )


            except OSError:
                break

    def connect_to_server(self):
        self.client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.client_socket.connect(
            (self.host, self.port)
        )

        self.client_socket.send(
            self.username.encode("utf-8")
        )
        acknowledgement = self.client_socket.recv(1024)

        if acknowledgement != b"ACK":
            raise ConnectionError(
                "Server did not acknowledge the connection"
            )
        

        print(
            f"Connected to server "
            f"{self.host}:{self.port}"
        )

    def reconnect_to_leader(self):
        leader_server = self.discovery.get_leader_server()

        if leader_server is None:
            print("No leader available")
            return False

        self.port = int(leader_server.split("-")[1])

        self.host = "127.0.0.1"

        self.connect_to_server()

        return True



    def connect(self):
        self.connect_to_server()

        receive_thread = threading.Thread(
            target=self.receive_messages,
            daemon=True
        )

        receive_thread.start()
        print(f"Connected to server {self.host}:{self.port}")
        print("Type 'exit' to disconnect.")

        try:
            while True:
                message = input("Enter message: ")

                if message.lower() == "exit":
                    break

                chat_message = Message(
                    message_type="CHAT",
                    username=self.username,
                    content=message
                )

                try:
                    self.client_socket.send(
                        encode_message(chat_message)
                    )

                except (BrokenPipeError, ConnectionResetError, OSError):
                    print("Connection lost. Trying to reconnect...")

                    reconnected = self.reconnect_to_leader()

                    if not reconnected:
                        print("Could not reconnect to a leader")
                        break

                    receive_thread = threading.Thread(
                        target=self.receive_messages,
                        daemon=True
                    )

                    receive_thread.start()


                    self.client_socket.send(
                        encode_message(chat_message)
                    )



        except ConnectionResetError:
            print("Connection to the server was lost.")

        finally:
            self.client_socket.close()
            print("Disconnected from server.")


if __name__ == "__main__":
    client = ChatClient("127.0.0.1", 5001)
    client.connect()

    