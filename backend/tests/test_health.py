import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "tensor-console"


@pytest.mark.asyncio
async def test_health_endpoint_with_trailing_slash(client: AsyncClient):
    response = await client.get("/api/v1/health/", follow_redirects=True)
    assert response.status_code == 200