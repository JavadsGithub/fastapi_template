# app/repositories/user_repo.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sa_update
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.entities.user import User
from app.entities.role import Role
import logging
from datetime import timezone

logger = logging.getLogger(__name__)


class UserRepository:
    """
    لایه دسترسی به داده (Async) برای موجودیت User.
    """

    async def get_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.id == user_id, User.is_deleted.is_(False))
            .options(selectinload(User.roles))
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id_include_deleted(
        self, db: AsyncSession, user_id: int
    ) -> Optional[User]:
        """Get user regardless of is_deleted flag (for undelete)."""
        stmt = select(User).where(User.id == user_id).options(selectinload(User.roles))
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.username == username, User.is_deleted.is_(False))
            .options(selectinload(User.roles))
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.email == email, User.is_deleted.is_(False))
            .options(selectinload(User.roles))
        )
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_roles_by_titles(
        self, db: AsyncSession, role_titles: List[str]
    ) -> List[Role]:
        stmt = select(Role).where(Role.title.in_(role_titles))
        res = await db.execute(stmt)
        return res.scalars().all()

    async def get_role_by_title(
        self, db: AsyncSession, role_title: str
    ) -> Optional[Role]:
        stmt = select(Role).where(Role.title == role_title)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()
    
    async def list_users(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[User]:
        stmt = (
            select(User)
            .where(User.is_deleted.is_(False))
            .options(selectinload(User.roles))
            .offset(skip)
            .limit(limit)
        )
        res = await db.execute(stmt)
        return res.scalars().all()

    async def create(self, db: AsyncSession, user_obj: User) -> User:
        db.add(user_obj)
        # flush so that SQLAlchemy assigns PKs / relationships without committing
        await db.flush()
        await db.refresh(user_obj)
        return user_obj

    async def update(self, db: AsyncSession, user_obj: User) -> User:
        # user_obj is expected to be persistent; flush + refresh to apply changes
        await db.flush()
        await db.refresh(user_obj)
        return user_obj

    async def update_last_login(self, db: AsyncSession, user_id: int, ts):
        """
        Update last_login via core UPDATE and RETURNING the actual row so we get
        DB-side values (updated_at, etc.) as they became after the UPDATE.
        Normalize tzinfo if DB returned naive datetime.
        """
        stmt = (
            sa_update(User)
            .where(User.id == user_id)
            .values(last_login=ts)
            .returning(User)
        )
        res = await db.execute(stmt)
        await db.flush()
        user = res.scalar_one_or_none()

        # debug: log incoming ts and returned value/tzinfo
        logger.debug(
            "update_last_login: sent ts=%r returned_last_login=%r tz=%r user_id=%s",
            ts,
            getattr(user, "last_login", None),
            getattr(getattr(user, "last_login", None), "tzinfo", None),
            user_id,
        )

        # If DB returned a naive datetime, assume UTC and attach tzinfo (defensive)
        if (
            user
            and getattr(user, "last_login", None)
            and getattr(user.last_login, "tzinfo", None) is None
        ):
            try:
                user.last_login = user.last_login.replace(tzinfo=timezone.utc)
                logger.debug(
                    "update_last_login: normalized returned last_login to UTC for user_id=%s",
                    user_id,
                )
            except Exception:
                logger.exception(
                    "failed to normalize last_login tzinfo for user_id=%s", user_id
                )

        return user

    async def delete(self, db: AsyncSession, user_obj: User) -> None:
        # hard delete (existing behavior)
        await db.delete(user_obj)
        await db.flush()

    async def soft_delete(self, db: AsyncSession, user_obj: User) -> User:
        # soft-delete: set flag, flush and refresh
        user_obj.is_deleted = True
        await db.flush()
        await db.refresh(user_obj)
        return user_obj

