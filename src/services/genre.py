from functools import lru_cache
from typing import Optional

from fastapi import Depends

from src.db.elastic import get_elastic
from src.models.genre import Genre
from src.services.base import BaseService
from src.services.base_storage import BaseStorage


class GenreService(BaseService):
    async def get(self, film_id: str) -> Optional[Genre]:
        if doc := await super().get(film_id):
            return Genre(**doc["_source"])
        return None

    async def list(self, es_query: Optional[dict] = None) -> list[Genre]:
        if docs := await super().list(es_query):
            return [Genre(**film["_source"]) for film in docs["hits"]["hits"]]
        return []


@lru_cache()
def get_genre_service(
    db: BaseStorage = Depends(get_elastic),  # noqa B008
) -> GenreService:
    return GenreService(db, index="genres")
