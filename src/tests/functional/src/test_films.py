from asyncio import sleep
from http import HTTPStatus

import pytest
from elasticsearch import NotFoundError
from httpx import AsyncClient

from src.models.film import Film, MovieType
from src.tests.functional.constants import FILM_LIST_URL

# All test coroutines will be treated as marked.
pytestmark = pytest.mark.asyncio


async def test_film_list(client: AsyncClient):
    await sleep(0.5)
    # Fetch data from elastic
    response = await client.get(FILM_LIST_URL)
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json != []
    assert all(isinstance(Film.parse_obj(film), Film) for film in resp_json)

    # Fetch data from cache
    response = await client.get(FILM_LIST_URL)
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json != []
    assert all(isinstance(Film.parse_obj(film), Film) for film in resp_json)


async def test_film_details(client: AsyncClient):
    film_details_url = "/films/1"
    # Fetch data from elastic
    response = await client.get(film_details_url)
    film: Film = Film.parse_obj(response.json())

    assert response.status_code == HTTPStatus.OK
    assert film.title == "Beirut"
    assert film.type == MovieType.TV_SHOW
    assert isinstance(film, Film)

    # Fetch data from cache
    response = await client.get(film_details_url)
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp_json != []
    assert isinstance(Film.parse_obj(resp_json), Film)


async def test_film_details_404(client: AsyncClient):
    film_details_url = "/films/-1"
    with pytest.raises(NotFoundError):
        response = await client.get(film_details_url)
        assert response.status_code == HTTPStatus.NOT_FOUND


async def test_film_list_wrong_sort_field(client: AsyncClient):
    response = await client.get(f"{FILM_LIST_URL}?sort=None")
    resp_json = response.json()
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "value is not a valid enumeration member" in resp_json["detail"][0]["msg"]


async def test_film_list_wrong_order_field(client: AsyncClient):
    response = await client.get(f"{FILM_LIST_URL}?sort_order=None")
    resp_json = response.json()
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "value is not a valid enumeration member" in resp_json["detail"][0]["msg"]


async def test_film_list_limit(client: AsyncClient):
    await sleep(0.5)
    response = await client.get(f"{FILM_LIST_URL}?page=1&limit=2")
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(resp_json) == 2
    assert resp_json[1]["title"] == "2046"

    response = await client.get(f"{FILM_LIST_URL}?page=2&limit=2")
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(resp_json) == 2
    assert resp_json[0]["title"] == "From Paris with Love"


async def test_film_list_search(client: AsyncClient):
    response = await client.get(f"{FILM_LIST_URL}?search_query=From%20Paris%20with%20Love")
    resp_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert any("From Paris with Love" in film["title"] for film in resp_json)
