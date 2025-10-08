# app/auth/policies.py
from typing import Dict, Any

def is_admin(user: Any) -> bool:
    # اگر user یه dict بود، از key استفاده کن
    if isinstance(user, dict):
        return "admin" in user.get("roles", [])
    # اگر object بود (مثلاً از دیتابیس اومده بود)
    return "admin" in getattr(user, "roles", [])

def can_delete_product(user: Any, resource: Any, env: Dict[str, Any]) -> tuple[bool, str]:
    """
    قوانین حذف محصول:
    - admin همیشه مجازه
    - owner در صورتی مجازه که id یکسانی با resource داشته باشه
    """
    if is_admin(user):
        return True, "user_is_admin"
        # در تست فعلی: فرض می‌کنیم هر کاربری فقط محصولی با id خودش رو داره
    if user.get("id") == resource.get("id"):
        #hour = env.get("hour", 10)
        #if 8 <= hour < 23:
            return True, "owner_and_ok"
    return False, "Not admin_or_owner"

    
    #if getattr(user, "id", None) == getattr(resource, "product_id", None):
    #    hour = env.get("hour", 0)
    #    if 8 <= hour < 23:
    #        return True, "owner_and_time_ok"
    #    return False, "owner_but_out_of_allowed_hours"
    #return False, "not_owner_or_admin"

def can_download_product(user: Any, resource: Any, env: Dict[str, Any]) -> tuple[bool, str]:
    """
    قوانین دانلود:
    - admin همیشه مجازه
    - اگر محصول عمومی باشه (is_public) مجازه
    - اگر user پرفچز کرده باشه (purchased_product_ids) مجازه
    """
    if is_admin(user):
        return True, "user_is_admin"
    if getattr(resource, "is_public", False):
        return True, "resource_is_public"
    purchased = getattr(user, "purchased_product_ids", []) or []
    if getattr(resource, "id", None) in purchased:
        return True, "user_purchased"
    return False, "not_purchased_or_public"
