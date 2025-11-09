# app/service/auth_serv.py
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.service.audit_logger_serv import AuditService
from app.core.security import verify_password
from app.core.auth import create_access_token
from app.config.base_config import settings

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository()
        self.audit = AuditService(db)
        self.logger = logger

    async def login(
        self, username: str, password: str, request: Optional[object] = None
    ) -> dict:
        user = await self.repo.get_by_username(self.db, username)
        if not user or not verify_password(
            password, getattr(user, "password_hash", "")
        ):
            # failed login audit
            try:
                await self.audit.log_from_abac_context(
                    {
                        "user": {"username": username},
                        "resource": {"type": "auth"},
                        "action": "login_failed",
                        "policy_name": "auth",
                        "policy_result": False,
                    },
                    request,
                )
            except Exception:
                self.logger.exception("failed to write audit (login_failed)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials"
            )

        # update last_login using core UPDATE so updated_at is NOT modified
        try:
            user = await self.repo.update_last_login(
                self.db, user.id, datetime.now(timezone.utc)
            )
        except Exception:
            self.logger.exception("failed to persist last_login")

        # create token
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            claims={"sub": user.username}, expires_delta=expires
        )

        # success audit
        try:
            await self.audit.log_from_abac_context(
                {
                    "user": {"id": user.id, "username": user.username},
                    "resource": {"type": "auth"},
                    "action": "login_success",
                    "policy_name": "auth",
                    "policy_result": True,
                },
                request,
            )
        except Exception:
            self.logger.exception("failed to write audit (login_success)")

        self.logger.info("login success user_id=%s username=%s", user.id, user.username)
        return {"access_token": token, "token_type": "bearer"}
