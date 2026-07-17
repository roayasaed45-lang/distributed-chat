from dataclasses import dataclass
import socket


@dataclass
class ClientSession:
    client_socket: socket.socket
    username: str
    address: tuple

