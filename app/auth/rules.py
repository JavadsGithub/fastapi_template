# app/auth/rules.py
from typing import Any, Dict
from .utils import utils_is_admin, get_attr


def is_admin(user: Any, resource: Any, env: Dict[str, Any]) -> bool:
    return utils_is_admin(user)


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
