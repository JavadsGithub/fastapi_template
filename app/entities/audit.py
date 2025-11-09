# app/entities/audit.py
from sqlalchemy import Column, Integer, String, Text, Boolean, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String, nullable=False)
    entity_type = Column(String, nullable=True)
    entity_id = Column(Integer, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    policy_name = Column(String, nullable=True)
    policy_result = Column(Boolean, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
