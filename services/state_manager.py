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

    def get_messages_after(self, message_id: int) -> list[Message]:
        with self.lock:
            return [
                message
                for message in self.messages
                if message.message_id is not None
                   and message.message_id > message_id
            ]

    def get_last_message_id(self) -> int:
        with self.lock:
            if not self.messages:
                return 0

            message_ids = [
                message.message_id
                for message in self.messages
                if message.message_id is not None
            ]

            if not message_ids:
                return 0

            return max(message_ids)



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


