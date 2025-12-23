from typing import Dict, List, Optional
from brain.presence.client import ClientIdentity, ClientType
import logging

logger = logging.getLogger(__name__)

class PresenceRegistry:
    def __init__(self):
        self._clients: Dict[str, ClientIdentity] = {}

    def register(self, client_type: ClientType, ip_address: str, user_agent: str = "Unknown") -> ClientIdentity:
        client = ClientIdentity.create(client_type, ip_address, user_agent)
        self._clients[client.client_id] = client
        logger.info(f"Client Registered: {client.client_id} ({client.client_type}) from {ip_address}")
        return client

    def unregister(self, client_id: str):
        if client_id in self._clients:
            client = self._clients.pop(client_id)
            logger.info(f"Client Disconnected: {client_id} ({client.client_type})")

    def get_client(self, client_id: str) -> Optional[ClientIdentity]:
        return self._clients.get(client_id)
    
    @property
    def active_clients(self) -> List[ClientIdentity]:
        return list(self._clients.values())
        
    @property
    def client_count(self) -> int:
        return len(self._clients)
        
    def get_summary(self) -> Dict[str, int]:
        summary = {t: 0 for t in ClientType}
        for c in self._clients.values():
            if c.client_type in summary: # Should be StrEnum but just in case
                summary[c.client_type] += 1
            else:
                 # fallback
                 t = str(c.client_type)
                 summary[t] = summary.get(t, 0) + 1
        return summary

presence_registry = PresenceRegistry()
