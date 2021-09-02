from functools import lru_cache
from typing import Optional

from fastapi import Depends

from src.db.elastic import get_elastic
from src.models.film import Film
from src.services.base import BaseService
from src.services.base_storage import BaseStorage


class FilmService(BaseService):
    async def get(self, film_id: str) -> Optional[Film]:
        if doc := await super().get(film_id):
            return Film(**doc["_source"])
        return None

    async def list(self, es_query: Optional[dict] = None) -> list[Film]:
        if docs := await super().list(es_query):
            return [Film(**film["_source"]) for film in docs["hits"]["hits"]]
        return []


@lru_cache()
def get_film_service(
    db: BaseStorage = Depends(get_elastic),  # noqa B008
) -> FilmService:
    return FilmService(db, index="movies")
