import json
from models.message import Message


def encode_message(message: Message) -> bytes:
    """
    Converts a Message object into bytes for sending over a socket.
    """
    message_dict = message.to_dict()
    message_json = json.dumps(message_dict)
    return message_json.encode("utf-8")


def decode_message(data: bytes) -> Message:
    """
    Converts bytes received from a socket back into a Message object.
    """
    message_json = data.decode("utf-8")
    message_dict = json.loads(message_json)
    return Message.from_dict(message_dict)

