# app/modules/items/test_items.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import create_app

@pytest.mark.asyncio #changed:@pytest.mark.anyio
async def test_create_and_read_item():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac: #changed:async with AsyncClient(app=app), base_url="http://test")
        # ایجاد یک آیتم
        payload = {"name": "Book", "price": 19.99, "is_offer": True}
        resp = await ac.post("/api/v1/items/", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Book"
        assert "id" in data

        # گرفتن همان آیتم
        item_id = data["id"]
        resp2 = await ac.get(f"/api/v1/items/{item_id}")
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["id"] == item_id
        assert data2["name"] == "Book"
