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

    def add_client(self, client_socket) -> None:
        with self.lock:
            self.clients.append(client_socket)

    def remove_client(self, client_socket) -> None:
        with self.lock:
            if client_socket in self.clients:
                self.clients.remove(client_socket)

    def get_clients(self) -> list:
        with self.lock:
            return self.clients.copy()



