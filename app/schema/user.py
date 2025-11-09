# app/schema/user.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict  # noqa: F401
from typing import Optional, List
from datetime import datetime


# ---------- Base ----------
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)


# ---------- Create ----------
class UserRegister(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    phone: Optional[str] = Field(None, max_length=100)
    model_config = ConfigDict(extra="forbid")


class UserCreateByAdmin(UserRegister):
    is_active: Optional[bool] = True
    roles: Optional[List[str]] = None
    # اگر roles فرستاده نشود None می‌شود؛ اگر خالی یا [] فرستاده شود در سرویس به معنی "keep default" رفتار می‌کنیم


# ---------- Update -------------
class UserUpdateSelf(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=100)


class UserUpdateByAdmin(UserUpdateSelf):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    roles: Optional[List[str]] = None
    # None -> تغییر نقش انجام نشود، [] -> نیز درخواستی برای پاک‌کردن نیست و در این پروژه به معنای "بدون تغییر" درنظر گرفته می‌شود


# -------------Read--------------
class UserReadSelf(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    phone: Optional[str] = Field(None, max_length=100)
    last_login: Optional[datetime] = None


class UserReadByAdmin(UserReadSelf):
    roles: List[str] = []
    is_active: bool


class UserListItem(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
