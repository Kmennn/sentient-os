from enum import StrEnum, auto
from dataclasses import dataclass
import time
import uuid

class ClientType(StrEnum):
    UI = auto()
    CLI = auto()
    OTHER = auto()

@dataclass
class ClientIdentity:
    client_id: str
    client_type: ClientType
    ip_address: str
    connected_at: float
    user_agent: str = "Unknown"
    
    @staticmethod
    def create(client_type: ClientType, ip_address: str, user_agent: str = "Unknown"):
        return ClientIdentity(
            client_id=str(uuid.uuid4()),
            client_type=client_type,
            ip_address=ip_address,
            connected_at=time.time(),
            user_agent=user_agent
        )
