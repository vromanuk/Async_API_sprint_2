from http import HTTPStatus

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_smoke(client: AsyncClient):
    response = await client.get("/smoke/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"msg": "OK"}
