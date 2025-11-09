# app/authorization/rules.py
from typing import Any, Dict
from app.utils.auth_utils import get_attr


def is_admin(user: Any, resource: Any, env: Dict[str, Any]) -> bool:
    if isinstance(user, dict):
        roles = user.get("roles", [])
        return "admin" in roles
    else:
        # user یک object SQLAlchemy است (مثل app.entities.user.User)
        roles = getattr(user, "roles", [])
        if not roles:
            return False
        # هر role یک object با attribute 'title' است
        return any(getattr(role, "title", "") == "admin" for role in roles)


def is_owner(user: Any, resource: Any, env: Dict[str, Any]) -> bool:
    return get_attr(user, "id") == get_attr(resource, "owner_id")


def in_working_hours(user: Any, resource: Any, env: Dict[str, Any]) -> bool:
    hour = env.get("hour", 0)
    return 8 <= hour < 23


def is_public(user: Any, resource: Any, env: Dict[str, Any]) -> bool:
    return get_attr(resource, "is_public", False)


def has_purchased(user: Any, resource: Any, env: Dict[str, Any]) -> bool:
    product_id = get_attr(resource, "id")
    purchased_ids = env.get("purchased_ids", set())
    return product_id in purchased_ids


def is_self(user: Any, resource: Any, env: Dict[str, Any]) -> bool:
    """
    بررسی می‌کند که resource یک user است و آیا user در حال اعمال بر روی خودش است.
    (برای resource هایی که به صورت dict فرستاده می‌شوند هم کار می‌کند)
    """
    # resource ممکن است dict یا ORM object باشد؛ اگر dict باشد احتمالاً id موجود است
    resource_id = get_attr(resource, "id")
    return get_attr(user, "id") == resource_id


def is_admin_or_self(user: Any, resource: Any, env: Dict[str, Any]) -> bool:
    """
    ترکیبی: admin یا خودِ کاربر (owner)
    """
    return is_admin(user, resource, env) or is_self(user, resource, env)


def anyone(user: Any, resource: Any, env: Dict[str, Any]) -> bool:
    """
    همیشه True — مناسب برای register/public actions.
    توجه: اگر می‌خواهی register محدودتر باشد (مثلاً با captcha یا invite code)،
    نباید از anyone استفاده کنی و شرط‌های دیگری اضافه کن.
    """
    return True


def can_assign_roles(context: dict) -> bool:
    """
    تنها اجازهٔ تخصیص نقش‌های مجاز را می‌دهد و از تخصیص 'admin' جلوگیری می‌کند.
    انتظار می‌رود context['resource']['intended_roles'] لیستی از اسامی نقش‌ها باشد.
    """
    resource = context.get("resource") or {}
    intended = resource.get("intended_roles") or []
    if not intended:
        return True
    allowed = {"user", "seller"}
    intended_lower = {r.lower() for r in intended}
    if "admin" in intended_lower:
        return False
    return intended_lower.issubset(allowed)
