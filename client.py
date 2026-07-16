import socket


class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server {self.host}:{self.port}")

        message = input("Enter message: ")
        self.client_socket.send(message.encode("utf-8"))

        self.client_socket.close()


if __name__ == "__main__":
    client = ChatClient("127.0.0.1", 5001)
    client.connect()

