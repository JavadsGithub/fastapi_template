# app/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from datetime import datetime, timezone

from app.auth.engine import ABACEngine
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.user import User
from app.entities.product import Product
from app.core.auth import (
    get_current_user,
    get_current_product,
    get_purchased_product_ids,
)


engine = ABACEngine()


def authorize(action: str, resource_type: str):
    async def dependency(
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
        allowed = engine.check_access(context)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for '{action}' on '{resource_type}'",
            )
        return True

    return dependency
