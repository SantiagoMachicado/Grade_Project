import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_i1_get_clinics_nearby(client: AsyncClient):
    res = await client.get("/api/v1/clinics/?skip=0&limit=10")
    # I1: Endpoint /clinics (o nearby si existe) funciona y retorna lista de clínicas.
    assert res.status_code == 200
    assert isinstance(res.json(), list)
