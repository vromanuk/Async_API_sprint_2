from abc import ABC
from typing import Optional

from src.services.base_storage import BaseStorage


class BaseService(ABC):
    def __init__(self, storage: BaseStorage, index: str):
        self.storage = storage
        self.index = index

    async def get(self, entity_id: str):
        return await self.storage.get_scalar(entity_id, self.index)

    async def list(self, query: Optional[dict] = None):
        return await self.storage.get_all(query, self.index)
