import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

import orjson
from pydantic import BaseModel

from src.models.genre import Genre
from src.models.person import Person
from src.utils import orjson_dumps


class MovieType(str, Enum):
    MOVIE = "movie"
    TV_SHOW = "tv_show"


class Film(BaseModel):
    id: str
    title: str
    description: str
    creation_date: datetime.datetime
    rating: float
    type: MovieType
    uuid: UUID
    certificate: Optional[str] = None
    file_path: Optional[str] = None
    genres: list[Genre]
    people: list[Person]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
