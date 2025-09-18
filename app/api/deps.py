from typing import AsyncGenerator
from fastapi import Depends
from app.db.session import get_db
from app.modules.item.service import ItemsService
from sqlalchemy.ext.asyncio import AsyncSession


async def get_items_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ItemsService, None]:
    yield ItemsService(db)
