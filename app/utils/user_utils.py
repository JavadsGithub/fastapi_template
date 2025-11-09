# app/utils/user_utils.py
from fastapi import HTTPException
from typing import Optional
from zoneinfo import ZoneInfo

from app.entities.user import User


# ======================================================
# ✅ ۱. تبدیل User Entity به Schema
# ======================================================
def user_to_schema(user: User, schema_type):
    """
    Converts a User SQLAlchemy entity to a Pydantic schema instance.
    Handles timezone normalization and role mapping.
    """
    tz_name = "Asia/Tehran"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = None

    def _to_tz(v):
        if v is None:
            return None
        if getattr(v, "tzinfo", None) is None:
            return v
        return v.astimezone(tz) if tz else v

    user_dict = {
        "id": getattr(user, "id", None),
        "username": getattr(user, "username", None),
        "email": getattr(user, "email", None),
        "first_name": getattr(user, "first_name", None),
        "last_name": getattr(user, "last_name", None),
        "is_active": getattr(user, "is_active", True),
        "created_at": _to_tz(getattr(user, "created_at", None)),
        "updated_at": _to_tz(getattr(user, "updated_at", None)),
        "last_login": _to_tz(getattr(user, "last_login", None)),
    }

    # Roles list only for admin read schemas
    if hasattr(user, "roles") and schema_type.__name__ == "UserReadByAdmin":
        user_dict["roles"] = [r.title for r in user.roles]

    return schema_type.model_validate(user_dict)


# ======================================================
# ✅ ۲. بررسی یکتایی username و email
# ======================================================
async def ensure_unique_username_email(
    repo,
    db,
    username: Optional[str],
    email: Optional[str],
    exclude_user_id: Optional[int] = None,
):
    """
    Ensures username and email are unique (used in registration and updates).
    """
    if username:
        existing = await repo.get_by_username(db, username)
        if existing and (exclude_user_id is None or existing.id != exclude_user_id):
            raise HTTPException(status_code=400, detail="username already exists")

    if email:
        existing = await repo.get_by_email(db, email)
        if existing and (exclude_user_id is None or existing.id != exclude_user_id):
            raise HTTPException(status_code=400, detail="email already exists")


# ======================================================
# ✅ ۳. فقط بررسی یکتایی email
# ======================================================
async def ensure_unique_email(
    repo, db, email: Optional[str], exclude_user_id: Optional[int] = None
):
    if email:
        existing = await repo.get_by_email(db, email)
        if existing and (exclude_user_id is None or existing.id != exclude_user_id):
            raise HTTPException(status_code=400, detail="email already exists")


# ======================================================
# ✅ ۴. فقط بررسی یکتایی username
# ======================================================
async def ensure_unique_username(
    repo, db, username: Optional[str], exclude_user_id: Optional[int] = None
):
    if username:
        existing = await repo.get_by_username(db, username)
        if existing and (exclude_user_id is None or existing.id != exclude_user_id):
            raise HTTPException(status_code=400, detail="username already exists")


# ======================================================
# ✅ ۴. گرفتن user  با استفاده از user_id
# ======================================================
async def get_user_by_id(repo, db, user_id: int):
    user = await repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
