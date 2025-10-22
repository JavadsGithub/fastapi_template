# app/schema/audit_logger.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class AuditLogCreate(BaseModel):
    user_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    policy_name: Optional[str] = None
    policy_result: bool
    reason: str


class AuditLogResponse(AuditLogCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
