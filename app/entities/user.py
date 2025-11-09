# app/entities/user.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.db.base import Base
from .associations import user_role


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    last_login = Column(TIMESTAMP(timezone=True))
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        # onupdate=lambda: datetime.now(timezone.utc),
    )

    roles = relationship("Role", secondary=user_role, back_populates="users")
    owned_products = relationship("Product", back_populates="owner")
    orders = relationship("Order", back_populates="user")
