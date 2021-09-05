from enum import Enum
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.constants import SortOrder
from src.models.film import Film
from src.services.film import FilmService, get_film_service
from src.utils import cached

router = APIRouter(
    prefix="/films",
)


class SortFieldFilm(str, Enum):
    ID = "id"
    TITLE = "title"
    IMDB_RATING = "imdb_rating"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@router.get(
    "/",
    response_model=list[Film],
    summary="Получение списка произведений",
    response_description="Список произведений",
)
@cached(decoder=Film, many=True)
async def film_list(
    search_query: Optional[str] = "",
    sort_order: SortOrder = SortOrder.ASC,
    sort: SortFieldFilm = SortFieldFilm.ID,
    page: int = 1,
    limit: int = 50,
    film_service: FilmService = Depends(get_film_service),  # noqa B008
) -> list[Film]:
    sort_value = sort.value
    if sort_value == SortFieldFilm.TITLE.value:
        sort_value = f"{SortFieldFilm.TITLE.value}.raw"

    es_query = {
        "size": limit,
        "from": (page - 1) * limit,
        "sort": [f"{sort_value}:{sort_order.value}"],
        "_source": [
            "id",
            "title",
            "rating",
            "description",
            "creation_date",
            "type",
            "uuid",
            "genres",
            "people",
            "certificate",
            "file_path",
        ],
    }

    if search_query:
        es_query["query"] = {
            "query": {
                "multi_match": {
                    "query": search_query,
                    "fuzziness": 1,
                    "fields": [
                        "title^5",
                        "description^4",
                        "genre^3",
                        "actors_names^3",
                        "writers_names^2",
                        "director",
                    ],
                }
            }
        }

    return await film_service.list(es_query)


@router.get(
    "/{film_id}",
    response_model=Film,
    summary="Получение информации о конкретном произведении",
    response_description="Информация о конкретном произведении",
)
@cached(decoder=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:  # noqa B008
    film = await film_service.get(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return film
