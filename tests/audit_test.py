import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.db.session import get_db
from app.entities.audit import AuditLog
from app.core.auth import create_access_token
from datetime import datetime, timezone


# Fixture برای توکن admin (فرض می‌کنیم admin همیشه مجازه)
@pytest.fixture
async def admin_token():
    return create_access_token(user_id=1, roles=["admin"])


# تست: وقتی admin محصول رو حذف می‌کنه → باید لاگ بشه (چون delete_product حساسه)
@pytest.mark.asyncio
async def test_audit_log_created_for_sensitive_allowed_action(
    client: AsyncClient,
    db: AsyncSession,
    admin_token: str,
):
    # مرحله ۱: قبل از درخواست، تعداد لاگ‌ها رو بشمار
    before_count = await db.scalar(
        "SELECT COUNT(*) FROM audit_logs WHERE action = 'delete_product'"
    )

    # مرحله ۲: درخواست حذف محصول (فرض: محصول با id=1 وجود داره)
    response = await client.delete(
        "/api/v1/tests/delete-product/1",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    # مرحله ۳: مطمئن شویم درخواست موفق بوده
    assert response.status_code == 200

    # مرحله ۴: بعد از درخواست، دوباره بشمار
    after_count = await db.scalar(
        "SELECT COUNT(*) FROM audit_logs WHERE action = 'delete_product'"
    )

    # مرحله ۵: تعداد باید یکی افزایش پیدا کرده باشه
    assert after_count == before_count + 1

    # مرحله ۶ (اختیاری): بررسی جزئیات آخرین لاگ
    latest_log = await db.execute(
        "SELECT * FROM audit_logs WHERE action = 'delete_product' ORDER BY created_at DESC LIMIT 1"
    )
    log = latest_log.fetchone()
    assert log is not None
    assert log.policy_result is True
    assert log.reason == "user_is_admin"
    assert log.user_id == 1
