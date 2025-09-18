from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .schema import ItemCreate, ItemUpdate
from .entity import Item


class ItemsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, item_id: int) -> Optional[Item]:
        q = await self.db.execute(select(Item).where(Item.id == item_id))
        return q.scalars().first()

    async def list(self, limit: int = 100) -> List[Item]:
        q = await self.db.execute(select(Item).limit(limit))
        return q.scalars().all()

    async def create(self, payload: ItemCreate) -> Item:
        db_obj = Item(**payload.dict())
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: Item, payload: ItemUpdate) -> Item:
        for field, value in payload.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: Item) -> None:
        await self.db.delete(db_obj)
        await self.db.commit()
