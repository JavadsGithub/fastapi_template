import pytest
from httpx import AsyncClient
from app.main import create_app


@pytest.mark.anyio
async def test_root_returns_200():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/")
        assert r.status_code == 200
        assert r.json()["message"] == "Hello World"
