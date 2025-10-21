from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repo.audit_logger import AuditRepository
from app.schema.audit_logger import AuditLogCreate
from app.auth.utils import get_attr
import logging

logger = logging.getLogger(__name__)


class AuditService:
    def __init__(self, db: AsyncSession):
        self.repo = AuditRepository(db)

    async def log_from_abac_context(
        self,
        context: dict,
        request: Any = None,
    ) -> None:
        """
        ثبت رویداد ABAC فقط با یک context و request.
        context باید شامل: user, resource, action, policy_result, reason
        """
        # استخراج اطلاعات از context
        user = context["user"]
        resource = context["resource"]
        action = context["action"]
        policy_result = context["policy_result"]
        reason = context["reason"]
        policy_name = context["policy_name"]

        # استخراج IP و User-Agent از request
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        # تصمیم‌گیری برای لاگ‌گیری
        sensitive_actions = {"delete_product"}
        should_log = (not policy_result) or (
            policy_result and policy_name in sensitive_actions
        )
        # should_log = True
        if not should_log:
            return

        # ساخت داده لاگ
        log_data = AuditLogCreate(
            user_id=get_attr(user, "id"),
            action=action,
            entity_type=get_attr(resource, "type", "product"),
            entity_id=get_attr(resource, "id"),
            ip_address=ip_address,
            user_agent=user_agent,
            policy_name=policy_name,
            policy_result=policy_result,
            reason=reason,
        )

        try:
            await self.repo.create(log_data)
        except Exception as e:
            logger.error(f"Audit log failed: {e}", exc_info=True)
