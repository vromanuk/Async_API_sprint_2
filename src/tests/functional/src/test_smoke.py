import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_smoke(client: AsyncClient):
    response = await client.get("/smoke/")

    assert response.status_code == 200
    assert response.json() == {"msg": "OK"}
