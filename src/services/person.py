from functools import lru_cache
from typing import Optional

from fastapi import Depends

from src.db.elastic import get_elastic
from src.models.person import Person
from src.services.base import BaseService
from src.services.base_storage import BaseStorage


class PersonService(BaseService):
    async def get(self, film_id: str) -> Optional[Person]:
        if doc := await super().get(film_id):
            return Person(**doc["_source"])
        return None

    async def list(self, es_query: Optional[dict] = None) -> list[Person]:
        if docs := await super().list(es_query):
            return [Person(**film["_source"]) for film in docs["hits"]["hits"]]
        return []


@lru_cache()
def get_person_service(
    db: BaseStorage = Depends(get_elastic),  # noqa B008
) -> PersonService:
    return PersonService(db, index="people")
