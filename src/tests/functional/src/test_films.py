from http import HTTPStatus

import pytest
from elasticsearch import AsyncElasticsearch, NotFoundError
from httpx import AsyncClient

from src.models.film import Film
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
    assert all(isinstance(Film.parse_obj(film), Film) for film in resp_json)


async def test_film_details(client: AsyncClient, es_client: AsyncElasticsearch, movie: Film):
    await populate_es_from_factory(es_client=es_client, entities=[movie], index="movies")
    # Fetch data from elastic
    film_details_url = f"/films/{movie.id}"
    response = await client.get(film_details_url)
    film: Film = Film.parse_obj(response.json())

    assert response.status_code == HTTPStatus.OK
    assert film.title == movie.title
    assert film.type == movie.type
    assert isinstance(film, Film)


async def test_film_details_404(client: AsyncClient, es_client: AsyncElasticsearch, movie: Film):
    await populate_es_from_factory(es_client=es_client, entities=[movie], index="movies")

    film_details_url = "/films/-1"
    with pytest.raises(NotFoundError):
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


async def test_film_list_limit(client: AsyncClient, es_client: AsyncElasticsearch):
    movies = sorted([MovieFactory.create() for _ in range(10)], key=lambda movie: movie.id)
    await populate_es_from_factory(es_client=es_client, entities=movies, index="movies")

    response = await client.get(f"{FILM_LIST_URL}?page=1&limit=2")
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(resp_json) == 2
    assert resp_json[0]["title"] == movies[0].title

    response = await client.get(f"{FILM_LIST_URL}?page=2&limit=2")
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
