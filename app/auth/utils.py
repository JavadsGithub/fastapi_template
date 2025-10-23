# app/auth/utils.py

from typing import Any


def get_attr(obj, attr: str, default=None):
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def utils_is_admin(user: Any) -> bool:
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
