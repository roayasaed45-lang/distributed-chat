import socket
import threading


class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # <-- כאן מוסיפים את הפונקציה
    def handle_client(self, client_socket, address):
        print(f"New connection from {address}")

        while True:
            data = client_socket.recv(1024)

            if not data:
                break

            message = data.decode("utf-8")
            print(f"Received message: {message}")

        client_socket.close()

    # אחריה מגיעה הפונקציה start
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        print(f"Server started on {self.host}:{self.port}")

        while True:
            client_socket, address = self.server_socket.accept()

            thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, address)
            )

            thread.start()


if __name__ == "__main__":
    server = ChatServer("127.0.0.1", 5001)
    server.start()

    