# app/service/audit_logger_serv.py
import logging
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.audit_logger_repo import AuditRepository
from app.schema.audit_logger import AuditLogCreate

logger = logging.getLogger(__name__)


class AuditService:
    def __init__(self, db: AsyncSession):
        self.repo = AuditRepository(db)

    async def log_from_abac_context(
        self,
        context: Dict[str, Any],
        request: Any = None,
    ) -> None:
        """
        Accepts a flexible ABAC-style context dict and writes a compact audit record.
        This function is defensive: اگر کلیدی در context وجود نداشت، None قرار می‌دهد
        و از بالا آمدن KeyError جلوگیری می‌کند.
        """
        try:
            user = context.get("user") or {}
            resource = context.get("resource") or {}
            action = context.get("action")
            policy_name = context.get("policy_name")
            policy_result = context.get("policy_result")
            reason = context.get("reason")  # may be None
            extra = context.get("extra") or context.get("env") or {}

            # user may be entity or dict
            if isinstance(user, dict):
                user_id = user.get("id")
                username = user.get("username")
            else:
                user_id = getattr(user, "id", None)
                username = getattr(user, "username", None)

            audit_in = AuditLogCreate(
                user_id=user_id,
                username=username,
                resource_type=resource.get("type"),
                resource_id=resource.get("id"),
                action=action,
                policy=policy_name,
                allowed=bool(policy_result) if policy_result is not None else None,
                reason=reason,
                metadata=extra,
            )

            # repository method may be named create or insert — try create first
            try:
                await self.repo.create(audit_in)
            except AttributeError:
                # fallback if repo API differs
                await self.repo.insert(audit_in)  # type: ignore
        except Exception:
            logger.exception("failed to write audit log from context")
