from typing import Optional
from fastapi_pagination import Page, Params
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi_pagination.ext.sqlalchemy import paginate
from ..schema.item import ItemCreate, ItemUpdate
from ..entities.item import Item


class ItemsRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, item_id: int) -> Optional[Item]:
        q = await self.db.execute(select(Item).where(Item.id == item_id))
        return q.scalars().first()

    async def list(self, params: Params) -> Page[Item]:
        q = select(Item).order_by(Item.id)
        return await paginate(self.db, q, params)

    async def create(self, payload: ItemCreate) -> Item:
        db_obj = Item(**payload.model_dump())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: Item, payload: ItemUpdate) -> Item:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Item) -> None:
        await self.db.delete(db_obj)
        await self.db.commit()
