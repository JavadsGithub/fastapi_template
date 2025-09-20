# app/modules/items/items_service.py
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.items.items_repo import ItemsRepository
from app.modules.items.items_schema import ItemCreate, ItemUpdate

class ItemsService:
    def __init__(self, db: AsyncSession):
        self.repo = ItemsRepository(db)

    async def create_item(self, payload: ItemCreate):
        return await self.repo.create(payload)

    async def get_item(self, item_id: int):
        return await self.repo.get(item_id)

    async def list_items(self, limit: int = 100):
        return await self.repo.list(limit)

    async def update_item(self, item_id: int, payload: ItemUpdate):
        db_obj = await self.repo.get(item_id)
        if not db_obj:
            return None
        return await self.repo.update(db_obj, payload)
