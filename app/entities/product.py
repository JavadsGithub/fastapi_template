# app/entities/product.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(precision=10, scale=2), nullable=False)
    file_type = Column(String, nullable=False)
    format = Column(String)
    writer = Column(String)
    release_date = Column(DateTime)
    status = Column(String, default="active")
    download_count = Column(Integer, default=0)
    rating_average = Column(Numeric(precision=3, scale=2), default=0.0)
    rating_count = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    owner = relationship("User", back_populates="owned_products")
