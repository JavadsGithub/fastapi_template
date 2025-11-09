# app/constants/auth_const.py
from typing import Dict, Any, Callable

from app.authorization.rules import (
    is_admin,
    is_owner,
    in_working_hours,
    is_public,
    has_purchased,
    is_self,
    anyone,
    is_admin_or_self,
)


# نگاشت نام توابع به توابع واقعی
RULE_FUNCTIONS: Dict[str, Callable[[Any, Any, Dict], bool]] = {
    "is_admin": is_admin,
    "is_owner": is_owner,
    "in_working_hours": in_working_hours,
    "is_public": is_public,
    "has_purchased": has_purchased,
    "is_self": is_self,
    "is_admin_or_self": is_admin_or_self,
    "anyone": anyone,
}
