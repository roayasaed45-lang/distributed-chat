import socket
import threading

from models.message import Message
from protocol import decode_message, encode_message


class ChatClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.username = input("Enter your username: ")


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

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        self.client_socket.send(
            self.username.encode("utf-8")
        )
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

    