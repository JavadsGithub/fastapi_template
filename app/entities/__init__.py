# entities
from app.db.base import Base
from .item import Item
from .user import User
from .role import Role
from .audit import AuditLog
# این کار باعث می‌شود هنگام ایمپورت Base، مدل‌ها ثبت شوند