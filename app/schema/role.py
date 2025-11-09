from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ---------- Base ----------
class RoleBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None


# ---------- Create ----------
# وقتی ادمین نقش جدید می‌سازد
class RoleCreate(RoleBase):
    permissions: Optional[List[str]] = []  # در آینده با policy system یکی می‌شود


# ---------- Update ----------
# ادمین می‌خواهد نقش را تغییر دهد
class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


# ---------- Read ----------
# برای نمایش نقش به کاربر یا ادمین
class RoleRead(RoleBase):
    id: int
    permissions: List[str] = []
    created_at: datetime

    class Config:
        orm_mode = True
