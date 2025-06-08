import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app as api_app

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=api_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac