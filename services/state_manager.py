from models.client_session import ClientSession
from threading import Lock
from models.message import Message


class StateManager:
    def __init__(self):
        self.messages: list[Message] = []
        self.clients = []
        self.lock = Lock()

    def add_message(self, message: Message) -> None:
        with self.lock:
            self.messages.append(message)

    def get_messages(self) -> list[Message]:
        with self.lock:
            return self.messages.copy()

    def add_client(self, client_session: ClientSession):
        with self.lock:
            self.clients.append(client_session)

    def remove_client(self, client_socket):
        with self.lock:
            self.clients = [
                client
                for client in self.clients
                if client.client_socket != client_socket
            ]

    def get_clients(self):
        with self.lock:
            return self.clients.copy()


