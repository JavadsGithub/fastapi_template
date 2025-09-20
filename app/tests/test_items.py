import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app

@pytest.mark.asyncio #changed:@pytest.mark.anyio
async def test_root_returns_200():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac: #changed
        r = await ac.get("/")
        assert r.status_code == 200
        assert r.json()["message"] == "Hello World"

