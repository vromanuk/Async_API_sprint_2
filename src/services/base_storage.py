from abc import ABC, abstractmethod
from typing import Optional


class BaseStorage(ABC):
    def __init__(self, db):
        self.db = db

    @abstractmethod
    async def get_all(self, query: Optional[dict] = None, index: Optional[str] = None):
        pass

    @abstractmethod
    async def get_scalar(self, entity_id: str, index: Optional[str] = None):
        pass


class ElasticsearchStorage(BaseStorage):
    async def get_all(self, query: Optional[dict] = None, index: Optional[str] = None):
        return await self.db.search(
            index=index,
            body=query.get("query"),
            sort=query["sort"],
            size=query["size"],
            from_=query["from"],
            _source=query["_source"],
        )

    async def get_scalar(self, entity_id: str, index: Optional[str] = None):
        return await self.db.get(index, entity_id)

