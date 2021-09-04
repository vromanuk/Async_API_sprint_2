from http import HTTPStatus
from unittest.mock import patch

import orjson
import pytest
from elasticsearch import AsyncElasticsearch
from httpx import AsyncClient

from src.models.film import Film
from src.services.base_cache import RedisCache
from src.tests.functional.constants import FILM_LIST_URL
from src.tests.functional.factories import MovieFactory
from src.tests.functional.utils.es_helpers import populate_es_from_factory

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_film_list(client: AsyncClient, es_client: AsyncElasticsearch):
    movies = [MovieFactory.create() for _ in range(10)]
    await populate_es_from_factory(es_client=es_client, entities=movies, index="movies")
    # Fetch data from elastic
    response = await client.get(FILM_LIST_URL)
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json != []


async def test_film_details(client: AsyncClient, es_client: AsyncElasticsearch, movie: Film):
    await populate_es_from_factory(es_client=es_client, entities=[movie], index="movies")
    # Fetch data from elastic
    film_details_url = f"/films/{movie.id}"
    response = await client.get(film_details_url)
    film: Film = Film.parse_obj(response.json())

    assert response.status_code == HTTPStatus.OK
    assert film.title == movie.title
    assert film.type == movie.type


async def test_film_details_404(client: AsyncClient):
    film_details_url = "/films/-1"
    response = await client.get(film_details_url)
    assert response.status_code == HTTPStatus.NOT_FOUND


async def test_film_list_wrong_sort_field(client: AsyncClient, es_client: AsyncElasticsearch, movie: Film):
    await populate_es_from_factory(es_client=es_client, entities=[movie], index="movies")

    response = await client.get(f"{FILM_LIST_URL}?sort=None")
    resp_json = response.json()
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "value is not a valid enumeration member" in resp_json["detail"][0]["msg"]


async def test_film_list_wrong_order_field(client: AsyncClient, es_client: AsyncElasticsearch, movie: Film):
    await populate_es_from_factory(es_client=es_client, entities=[movie], index="movies")

    response = await client.get(f"{FILM_LIST_URL}?sort_order=None")
    resp_json = response.json()
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "value is not a valid enumeration member" in resp_json["detail"][0]["msg"]


async def test_film_list_limit_page_1(client: AsyncClient, es_client: AsyncElasticsearch):
    movies = sorted([MovieFactory.create() for _ in range(10)], key=lambda movie: movie.id)
    await populate_es_from_factory(es_client=es_client, entities=movies, index="movies")

    response = await client.get(f"{FILM_LIST_URL}?sort_order=asc&sort=id&page=1&limit=2")
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(resp_json) == 2
    assert resp_json[0]["title"] == movies[0].title


async def test_film_list_limit_page_2(client: AsyncClient, es_client: AsyncElasticsearch):
    movies = sorted([MovieFactory.create() for _ in range(10)], key=lambda movie: movie.id)
    await populate_es_from_factory(es_client=es_client, entities=movies, index="movies")

    response = await client.get(f"{FILM_LIST_URL}?sort_order=asc&sort=id&page=2&limit=2")
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(resp_json) == 2
    assert resp_json[0]["title"] == movies[2].title


async def test_film_list_search(client: AsyncClient, es_client: AsyncElasticsearch):
    movies = [MovieFactory.create() for _ in range(10)]
    await populate_es_from_factory(es_client=es_client, entities=movies, index="movies")

    response = await client.get(f"{FILM_LIST_URL}?search_query={movies[0].title}")
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert any(movies[0].title in film["title"] for film in resp_json)


@patch("src.services.film.get_film_service")
async def test_film_list_from_cache(mock_service, client: AsyncClient, cache_client: RedisCache):
    movies = [MovieFactory.create() for _ in range(10)]
    cache_key = ":asc:id:1:50"
    await cache_client.cache(cache_key, orjson.dumps([entity.dict() for entity in movies]))
    # Fetch data from cache
    response = await client.get(FILM_LIST_URL)
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json != []
    assert len(resp_json) == len(movies)
    mock_service.assert_not_called()


@patch("src.services.film.get_film_service")
async def test_film_details_from_cache(mock_service, client: AsyncClient, cache_client: RedisCache, movie: Film):
    film_details_url = f"/films/{movie.id}"
    cache_key = f"film:{movie.id}"
    await cache_client.cache(cache_key, movie.json())
    # Fetch data from cache
    response = await client.get(film_details_url)
    film: Film = Film.parse_obj(response.json())

    assert response.status_code == HTTPStatus.OK
    assert film.title == movie.title
    assert film.type == movie.type
    mock_service.assert_not_called()
