from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Message:
    message_type: str
    username: str
    content: str
    message_id: Optional[int] = None
    timestamp: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(
            message_type=data["message_type"],
            username=data["username"],
            content=data["content"],
            message_id=data.get("message_id"),
            timestamp=data.get("timestamp"),
        )
