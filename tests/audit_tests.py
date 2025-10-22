# tests/audit_test.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import create_access_token
from sqlalchemy import text
from tests.conftest import TestingSessionLocal


# helper جدید: از یک session جدید برای خواندن استفاده می‌کنیم
async def count_audit_logs_with_session(
    session: AsyncSession, action: str = None
) -> int:
    if action:
        query = text("SELECT COUNT(*) FROM audit_logs WHERE action = :action")
        result = await session.execute(query, {"action": action})
    else:
        query = text("SELECT COUNT(*) FROM audit_logs")
        result = await session.execute(query)
    return result.scalar()


# کمک‌کننده برای شمارش لاگ‌ها
async def count_audit_logs(db: AsyncSession, action: str = None) -> int:
    if action:
        query = text("SELECT COUNT(*) FROM audit_logs WHERE action = :action")
        result = await db.execute(query, {"action": action})
    else:
        query = text("SELECT COUNT(*) FROM audit_logs")
        result = await db.execute(query)
    return result.scalar()


# کمک‌کننده برای دریافت آخرین لاگ
async def get_latest_audit_log(db: AsyncSession):
    query = text("SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT 1")
    result = await db.execute(query)
    return result.fetchone()


# ------------------------------------------------------------
# تست ۱: Allowed + حساس → باید لاگ بشه (admin حذف محصول)
@pytest.mark.asyncio
async def test_audit_logs_sensitive_allowed(test_client, get_token, test_data):
    token = get_token("admin_user")
    product_id = test_data["products"]["private"].id

    response = await test_client.delete(
        f"/api/v1/tests/delete-product/{product_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


# ------------------------------------------------------------
# تست ۲: Denied → باید لاگ بشه (کاربر عادی خارج از ساعت کاری)


@pytest.mark.asyncio
async def test_audit_logs_denied_access(test_client, get_token, test_data):
    token = get_token("buyer_reza")  # کاربر خریدار نمی‌تونه حذف کنه
    product_id = test_data["products"]["private"].id

    response = await test_client.delete(
        f"/api/v1/tests/delete-product/{product_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ------------------------------------------------------------
# تست ۳: Allowed + غیرحساس → نباید لاگ بشه (دانلود محصول عمومی)
# tests/audit_test.py (یا همان فایلی که تست در آن است)
# استفاده از session factory تست


@pytest.mark.asyncio
async def test_audit_does_not_log_non_sensitive_allowed(
    test_client: AsyncClient, db: AsyncSession, test_data
):
    # توکن برای کاربر buyer_reza
    token = create_access_token(claims={"sub": "buyer_reza", "roles": ["user"]})

    # ------- مقدار اولیه با session فعلی fixture -------
    before = await count_audit_logs_with_session(db, "download")

    # ------- درخواست به endpoint با یک product واقعی از test_data -------
    # استفاده از product موجود (مثلاً محصول public)
    product = test_data["products"]["public"]
    product_id = product.id

    response = await test_client.get(
        f"/api/v1/tests/download-product/{product_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, (
        f"expected 200 but got {response.status_code} - body: {response.text}"
    )

    # ------- حالا یک session تازه باز می‌کنیم تا وضعیت دیتابیس را با اطمینان بخوانیم -------
    async with TestingSessionLocal() as fresh_session:
        after = await count_audit_logs_with_session(fresh_session, "download")

    assert after == before
