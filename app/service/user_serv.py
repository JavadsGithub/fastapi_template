# app/service/user_serv.py
from typing import Optional, List
from datetime import datetime
import logging

from fastapi import HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from zoneinfo import ZoneInfo

from app.service.audit_logger_serv import AuditService
from app.repositories.user_repo import UserRepository
from app.entities.user import User
from app.core.security import get_password_hash

from app.schema.user import (
    UserRegister,
    UserCreateByAdmin,
    UserUpdateSelf,
    UserUpdateByAdmin,
    UserReadByAdmin,
    UserListItem,
    UserReadSelf,
)

from app.authorization.engine import ABACEngine

engine = ABACEngine()


class UserService:
    """
    UserService — لایه منطق تجاری کاربران
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository()
        self.abac = engine
        self.logger = logging.getLogger(__name__)
        self.audit = AuditService(db)

    # -------------------------
    # Helpers: تبدیل User Entity به Schema با roles
    # -------------------------
    def user_to_schema(self, user: User, schema_type):
        """
        Build a dict from User entity, convert datetimes for presentation and
        return the appropriate Pydantic schema instance.
        """
        # پایه‌ای‌ترین فیلدها
        user_dict = {
            "id": getattr(user, "id", None),
            "username": getattr(user, "username", None),
            "email": getattr(user, "email", None),
            "first_name": getattr(user, "first_name", None),
            "last_name": getattr(user, "last_name", None),
            "phone": getattr(user, "phone", None),
            "is_active": getattr(user, "is_active", True),
            "created_at": getattr(user, "created_at", None),
            "updated_at": getattr(user, "updated_at", None),
        }

        # roles -> list[str]
        roles_list = []
        try:
            roles_attr = getattr(user, "roles", None)
            if roles_attr:
                roles_list = [r.title for r in roles_attr]
        except Exception:
            roles_list = []

        # convert tz-aware datetimes to desired TZ for presentation (optional)
        tz_name = "Asia/Tehran"  # میتوانی از settings بگیری
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = None

        def _to_tz(v):
            if v is None:
                return None
            # only convert tz-aware datetimes; leave naive as-is
            if getattr(v, "tzinfo", None) is None:
                return v
            return v.astimezone(tz) if tz else v

        user_dict["created_at"] = _to_tz(user_dict.get("created_at"))
        user_dict["updated_at"] = _to_tz(user_dict.get("updated_at"))
        user_dict["last_login"] = _to_tz(getattr(user, "last_login", None))

        # اضافه کردن roles فقط در صورت وجود در schema
        if getattr(schema_type, "__name__", "") == "UserReadByAdmin":
            user_dict["roles"] = roles_list

        # همیشه از schema_type واقعی برای validate استفاده کن
        return schema_type.model_validate(user_dict)

    # -------------------------
    # Helpers: اطمینان از unigue بودن username و ایمیل
    # -------------------------
    async def _ensure_unique_username_email(
        self,
        username: Optional[str],
        email: Optional[str],
        exclude_user_id: Optional[int] = None,
    ):
        if username:
            existing = await self.repo.get_by_username(self.db, username)
            if existing and (exclude_user_id is None or existing.id != exclude_user_id):
                raise HTTPException(status_code=400, detail="username already exists")
        if email:
            existing = await self.repo.get_by_email(self.db, email)
            if existing and (exclude_user_id is None or existing.id != exclude_user_id):
                raise HTTPException(status_code=400, detail="email already exists")

    async def _ensure_unique_email(
        self,
        email: Optional[str],
        exclude_user_id: Optional[int] = None,
    ):
        if email:
            existing = await self.repo.get_by_email(self.db, email)
            if existing and (exclude_user_id is None or existing.id != exclude_user_id):
                raise HTTPException(status_code=400, detail="email already exists")

    async def _ensure_unique_username(
        self,
        username: Optional[str],
        exclude_user_id: Optional[int] = None,
    ):
        if username:
            existing = await self.repo.get_by_username(self.db, username)
            if existing and (exclude_user_id is None or existing.id != exclude_user_id):
                raise HTTPException(status_code=400, detail="username already exists")

    # -------------------------
    # ۱. ثبت‌نام کاربر توسط خودش
    # -------------------------
    async def register_user(
        self, user_in: UserRegister, request: Optional[Request] = None
    ):
        await self._ensure_unique_username_email(user_in.username, user_in.email)
        hashed_pwd = get_password_hash(user_in.password)

        db_user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=hashed_pwd,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            is_active=True,
        )

        # نقش پیش‌فرض
        default_role = await self.repo.get_role_by_title(self.db, "user")
        if default_role:
            db_user.roles.append(default_role)

        created_user = await self.repo.create(self.db, db_user)
        return self.user_to_schema(created_user, UserReadSelf)

    # -------------------------
    # ۲. ایجاد کاربر توسط ادمین
    # -------------------------
    async def create_user_by_admin(
        self,
        current_user: User,
        user_in: UserCreateByAdmin,
        request: Optional[Request] = None,
    ):
        # intended roles from request; None or [] -> treat as default below
        intended_roles = list(user_in.roles) if getattr(user_in, "roles", None) else []
        # If empty, default to ["user"]
        roles_input = intended_roles or ["user"]

        # Safety: never allow creating a user with 'admin' role here (defense-in-depth)
        if any(r.lower() == "admin" for r in roles_input):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Assigning 'admin' role is not allowed.",
            )

        # ABAC check: include intended roles in resource context
        resource_context = {"type": "user", "intended_roles": roles_input}
        ctx = {
            "user": current_user,
            "resource": resource_context,
            "action": "create",
            "env": {},
        }
        allowed, reason = self.abac.check_access(ctx)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {reason or 'not allowed'}",
            )

        await self._ensure_unique_username_email(user_in.username, user_in.email)

        hashed = get_password_hash(user_in.password)
        new_user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=hashed,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            is_active=bool(user_in.is_active),
            created_at=datetime.utcnow(),
        )

        # fetch Role objects
        role_objs = await self.repo.get_roles_by_titles(self.db, roles_input)
        found = {r.title.lower() for r in role_objs}
        missing = set(r.lower() for r in roles_input) - found
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Roles not found: {', '.join(sorted(missing))}",
            )

        new_user.roles = role_objs

        created_user = await self.repo.create(self.db, new_user)
        return self.user_to_schema(created_user, UserReadByAdmin)

    # -------------------------
    # ۳ & ۴. گرفتن کاربر بر اساس id
    # -------------------------
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self.repo.get_by_id(self.db, user_id)

    # -------------------------
    # ۵. لیست کاربران
    # -------------------------
    async def list_users(
        self, current_user: User, skip=0, limit=100, request: Optional[Request] = None
    ) -> List[UserListItem]:
        users_list = await self.repo.list_users(self.db, skip=skip, limit=limit)
        return [self.user_to_schema(user, UserListItem) for user in users_list]

    # -------------------------
    # ۶. ویرایش توسط خود کاربر
    # -------------------------
    async def update_user_self(
        self,
        current_user: User,
        user_id: int,
        update_data: UserUpdateSelf,
        request: Optional[Request] = None,
    ) -> UserReadSelf:
        if current_user.id != user_id:
            raise HTTPException(
                status_code=403, detail="Cannot update another user's profile"
            )

        target_user = await self.repo.get_by_id(self.db, user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if key == "password" and value:
                setattr(target_user, "password_hash", get_password_hash(value))
            elif hasattr(target_user, key):
                setattr(target_user, key, value)

        updated_user = await self.repo.update(self.db, target_user)
        return self.user_to_schema(updated_user, UserReadSelf)

    # -------------------------
    # ۷. ویرایش توسط admin
    # -------------------------
    async def update_user_by_admin(
        self,
        current_user: User,
        user_id: int,
        update_data: UserUpdateByAdmin,
        request: Optional[Request] = None,
    ) -> UserReadByAdmin:
        target_user = await self.repo.get_by_id(self.db, user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Determine if target is admin already
        target_roles = [
            r.title.lower() for r in getattr(target_user, "roles", [])
        ] or []
        target_is_admin = "admin" in target_roles

        # Roles handling:
        # - None => no change
        # - [] => treated as "no change" (per requirement)
        roles_input = None
        if (
            getattr(update_data, "roles", None) is not None
            and len(update_data.roles) > 0
        ):
            roles_input = list(update_data.roles)

        # If target is already admin, disallow any role changes
        if target_is_admin and roles_input is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot change roles of an admin user",
            )

        # If roles are to be changed, run ABAC check and validate roles
        if roles_input is not None:
            resource_context = {"type": "user", "intended_roles": roles_input}
            ctx = {
                "user": current_user,
                "resource": resource_context,
                "action": "update",
                "env": {},
            }
            allowed, reason = self.abac.check_access(ctx)
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied to assign roles: {reason or 'not allowed'}",
                )

            # Validate roles existence and forbid assigning "admin"
            role_objs = await self.repo.get_roles_by_titles(self.db, roles_input)
            found = {r.title.lower() for r in role_objs}
            missing = set(r.lower() for r in roles_input) - found
            if missing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Roles not found: {', '.join(sorted(missing))}",
                )

            if "admin" in {r.title.lower() for r in role_objs}:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Assigning 'admin' role is not allowed",
                )

            target_user.roles = role_objs

        # Apply other fields: preserve existing values when a field is not provided OR provided as None or empty string
        update_dict = update_data.model_dump(exclude_unset=True)
        # validate email uniqueness only if email is provided in the update (exclude current user)
        new_email = update_dict.get("email")
        if new_email is not None:
            await self._ensure_unique_email(new_email, exclude_user_id=user_id)
        # remove roles from update_dict since handled above
        update_dict.pop("roles", None)

        for key, value in update_dict.items():
            # skip None or empty string values (preserve existing)
            if value is None:
                continue
            if isinstance(value, str) and value.strip() == "":
                continue
            if hasattr(target_user, key):
                setattr(target_user, key, value)

        updated = await self.repo.update(self.db, target_user)
        return self.user_to_schema(updated, UserReadByAdmin)

    # -------------------------
    # ۸. حذف کاربر
    # -------------------------
    async def delete_user(
        self, current_user: User, user_id: int, request: Optional[Request] = None
    ) -> bool:
        target_user = await self.repo.get_by_id(self.db, user_id)
        if not target_user:
            return False
        await self.repo.delete(self.db, target_user)
        return True

    # -------------------------
    # ۸. حذف کاربر به صورت نرم‌افزاری
    # -------------------------
    async def soft_delete_user(
        self,
        current_user: User,
        user_id: int,
        request: Optional[Request] = None,
    ) -> bool:
        target_user = await self.repo.get_by_id(self.db, user_id)
        if not target_user:
            return False
        if current_user.id == target_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself"
            )
        await self.repo.soft_delete(self.db, target_user)
        try:
            audit = AuditService(self.db)
            await audit.log_from_abac_context(
                {
                    "user": current_user,
                    "resource": {"type": "user", "id": user_id},
                    "action": "soft_delete",
                    "policy_name": "delete_user",
                    "policy_result": True,
                },
                request,
            )
        except Exception:
            pass
        return True

    # -------------------------
    # ۹. بازیابی کاربر حذف‌شده
    # -------------------------
    async def undelete_user(
        self,
        current_user: User,
        user_id: int,
        request: Optional[Request] = None,
    ) -> UserReadByAdmin | None:
        """
        Restore a soft-deleted user (set is_deleted=False) and return the user schema.
        Only admins can call the route (controller enforces authorize dependency).
        """
        target_user = await self.repo.get_by_id_include_deleted(self.db, user_id)
        if not target_user:
            return None

        # if not deleted, nothing to do
        if not getattr(target_user, "is_deleted", False):
            return None

        # optional: prevent undeleting self? keep normal behavior (admin can undelete others)
        target_user.is_deleted = False
        updated = await self.repo.update(self.db, target_user)

        # audit
        try:
            audit = AuditService(self.db)
            await audit.log_from_abac_context(
                {
                    "user": current_user,
                    "resource": {"type": "user", "id": user_id},
                    "action": "undelete",
                    "policy_name": "undelete_user",
                    "policy_result": True,
                },
                request,
            )
        except Exception:
            pass

        return self.user_to_schema(updated, UserReadByAdmin)
