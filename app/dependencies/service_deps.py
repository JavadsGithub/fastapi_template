# app/dependencies/sevice_deps.py
from typing import AsyncGenerator
from fastapi import Depends
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.item_serv import ItemsService
from app.service.user_serv import UserService
from app.service.auth_serv import AuthService


""""
تزریق وابستگی سرویس به API

"""


async def get_items_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[ItemsService, None]:
    yield ItemsService(db)


async def get_user_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[UserService, None]:
    yield UserService(db)


async def get_auth_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[AuthService, None]:
    yield AuthService(db)
