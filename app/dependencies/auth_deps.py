# app/dependencies/auth_deps.py
from fastapi import Depends, HTTPException, status, Request
from datetime import datetime, timezone
from typing import Callable, Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.authorization.engine import ABACEngine
from app.db.session import get_db
from app.entities.user import User
from app.entities.product import Product
from app.service.audit_logger_serv import AuditService
from app.repositories.user_repo import UserRepository

from app.core.auth import (
    get_current_user,
    get_purchased_product_ids,
    get_current_product,
    get_current_user_resource,
)

# ⚙️ موتور ABAC
engine = ABACEngine()

# ⚙️ Repositoryها
user_repo = UserRepository()


# wrapper loaderها با یک امضاء یکسان: (request, db, resource_id)
async def load_user(request: Request, db: AsyncSession, resource_id: Optional[int]):
    # get_current_user_resource خودش موقع نبودن user_id را هندل می‌کند (مثلاً register/create)
    return await get_current_user_resource(request, db)


async def load_product(request: Request, db: AsyncSession, resource_id: Optional[int]):
    if not resource_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing product_id in path.",
        )
    return await get_current_product(product_id=int(resource_id), db=db)


# ⚙️ مپ لودرها: برای هر resource_type مشخص می‌کند چطور از DB لود شود
RESOURCE_LOADERS: Dict[str, Callable[[Request, AsyncSession, Optional[int]], Any]] = {
    "user": load_user,
    "product": load_product,
}


# ==============================
# تابع authorize نهایی
# ==============================
def authorize(action: str, resource_type: str):
    async def dependency(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ) -> bool:
        """
        بررسی دسترسی به صورت ABAC.
        """

        # ===============================
        # 1️⃣ شناسایی resource_id از path
        # ===============================
        resource_id_key = f"{resource_type}_id"
        resource_id = request.path_params.get(resource_id_key)

        # فقط اگر مسیر نیاز به resource دارد
        resource: Optional[Any] = None
        if resource_type in RESOURCE_LOADERS:
            loader = RESOURCE_LOADERS[resource_type]
            # loaderها یک امضاء یکسان دارند: (request, db, resource_id)
            resource = await loader(request, db, resource_id)
            if not resource:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{resource_type.capitalize()} not found.",
                )

        # ===============================
        # 2️⃣ ساخت context
        # ===============================
        purchased_ids = await get_purchased_product_ids(db, current_user.id)

        # ساخت context مخصوص هر منبع
        resource_context = {}
        if resource_type == "product" and isinstance(resource, Product):
            resource_context = {
                "id": resource.id,
                "owner_id": resource.owner_id,
                "is_public": resource.is_public,
                "type": "product",
            }
        elif resource_type == "user" and isinstance(resource, User):
            resource_context = {
                "id": resource.id,
                "username": resource.username,
                "type": "user",
            }
        else:
            resource_context = {
                "id": getattr(resource, "id", None),
                "type": resource_type,
            }

        # context نهایی برای ABAC
        context = {
            "user": current_user,
            "resource": resource_context,
            "action": action,
            "env": {
                "hour": datetime.now(timezone.utc).hour,
                "purchased_ids": purchased_ids,
            },
        }

        # ===============================
        # 3️⃣ بررسی سیاست‌ها
        # ===============================
        allowed, reason = engine.check_access(context)

        # ===============================
        # 4️⃣ ثبت در Audit Log
        # ===============================
        audit_service = AuditService(db)
        await audit_service.log_from_abac_context(
            {
                "user": current_user,
                "resource": resource_context,
                "action": action,
                "policy_name": f"{action}_{resource_type}",
                "policy_result": allowed,
                "reason": reason,
            },
            request,
        )

        # ===============================
        # 5️⃣ نتیجه نهایی
        # ===============================
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied for '{action}' on '{resource_type}': {reason}",
            )

        return True

    return dependency
