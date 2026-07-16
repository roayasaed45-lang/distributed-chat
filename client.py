import socket


class ChatClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

        self.client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server {self.host}:{self.port}")
        print("Type 'exit' to disconnect.")

        try:
            while True:
                message = input("Enter message: ")

                if message.lower() == "exit":
                    break

                self.client_socket.send(
                    message.encode("utf-8")
                )

        except ConnectionResetError:
            print("Connection to the server was lost.")

        finally:
            self.client_socket.close()
            print("Disconnected from server.")


if __name__ == "__main__":
    client = ChatClient("127.0.0.1", 5001)
    client.connect()

    