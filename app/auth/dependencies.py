# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status, Request
from datetime import datetime, timezone

from app.auth.engine import ABACEngine
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.user import User
from app.entities.product import Product

from app.service.audit_logger import AuditService
from app.core.auth import (
    get_current_user,
    get_current_product,
    get_purchased_product_ids,
)


engine = ABACEngine()


def authorize(action: str, resource_type: str):
    async def dependency(
        request: Request,
        current_product: Product = Depends(get_current_product),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        purchased_ids = await get_purchased_product_ids(db, current_user.id)

        context = {
            "user": current_user,
            "resource": {
                "id": current_product.id,
                "owner_id": current_product.owner_id,
                "is_public": current_product.is_public,
                "type": "product",
            },
            "action": action,
            "env": {
                "hour": datetime.now(timezone.utc).hour,
                "purchased_ids": purchased_ids,
            },
        }
        policy_name = f"{action}_{resource_type}"

        allowed, reason = engine.check_access(context)

        # ✅ ساخت context کامل برای audit

        audit_context = {
            "user": current_user,
            "resource": context["resource"],
            "action": action,
            "policy_name": policy_name,
            "policy_result": allowed,
            "reason": reason,
        }

        audit_service = AuditService(db)
        await audit_service.log_from_abac_context(audit_context, request)

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for '{action}' on '{resource_type}'",
            )
        return True

    return dependency
