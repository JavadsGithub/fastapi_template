from fastapi_pagination import Params
from sqlalchemy.ext.asyncio import AsyncSession

from ..repo.item import ItemsRepo, ItemCreate, ItemUpdate


class ItemsService:
    def __init__(self, db: AsyncSession):
        self.repo = ItemsRepo(db)

    async def create_item(self, payload: ItemCreate):
        return await self.repo.create(payload)

    async def get_item(self, item_id: int):
        return await self.repo.get(item_id)

    async def list_items(self, params: Params):
        return await self.repo.list(params)

    async def update_item(self, item_id: int, payload: ItemUpdate):
        db_obj = await self.repo.get(item_id)
        if not db_obj:
            return None
        return await self.repo.update(db_obj, payload)
