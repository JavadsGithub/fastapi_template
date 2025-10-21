# app/repo/audit_logger.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.entities.audit import AuditLog
from app.schema.audit_logger import AuditLogCreate


class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, log_data: AuditLogCreate) -> AuditLog:
        """ذخیره یک رویداد امنیتی در دیتابیس."""
        db_log = AuditLog(**log_data.model_dump())
        self.db.add(db_log)
        await self.db.flush()
        await self.db.refresh(db_log)
        await self.db.commit()
        return db_log
