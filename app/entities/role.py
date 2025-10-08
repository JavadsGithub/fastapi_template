from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from .associations import user_role  # ✅ ایمپورت جدول ارتباطی

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    description = Column(Text)

    users = relationship("User", secondary=user_role, back_populates="roles")