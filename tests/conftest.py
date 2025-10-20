# tests/conftest.py

import pytest
import pytest_asyncio
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport

from app.db.base import Base
from app.core.security import get_password_hash
from app.entities.user import User
from app.entities.role import Role
from app.entities.product import Product
from app.entities.order import Order, OrderItem  # ✅ مدل سفارش را import کن
from app.main import app
from app.db.session import get_db


# استفاده از SQLite in-memory برای تست
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestingSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with TestingSessionLocal() as session:
        yield session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def test_data(db: AsyncSession):
    # نقش‌ها
    roles = {
        "admin": Role(title="admin", description="Admin role"),
        "seller": Role(title="seller", description="Seller role"),
        "user": Role(title="user", description="User role"),
    }
    db.add_all(roles.values())
    await db.commit()
    for r in roles.values():
        await db.refresh(r)

    # کاربران
    users = {
        "admin_user": User(
            username="admin_user",
            email="admin@example.com",
            password_hash=get_password_hash("123456"),
            is_active=True,
        ),
        "seller_ali": User(
            username="seller_ali",
            email="ali@example.com",
            password_hash=get_password_hash("123456"),
            is_active=True,
        ),
        "buyer_reza": User(
            username="buyer_reza",
            email="reza@example.com",
            password_hash=get_password_hash("123456"),
            is_active=True,
        ),
    }
    for user in users.values():
        user.roles = [
            roles["admin"]
            if user.username == "admin_user"
            else roles["seller"]
            if user.username == "seller_ali"
            else roles["user"]
        ]
    db.add_all(users.values())
    await db.commit()
    for u in users.values():
        await db.refresh(u)

    # محصولات
    products = {
        "private": Product(
            name="Private Dataset",
            description="A private dataset for buyers only",
            price=50.00,
            file_type="dataset",
            owner_id=users["seller_ali"].id,
            is_public=False,
        ),
        "public": Product(
            name="Public Book",
            description="A free public book for everyone",
            price=0.00,
            file_type="book",
            owner_id=users["seller_ali"].id,
            is_public=True,
        ),
    }
    db.add_all(products.values())
    await db.commit()
    for p in products.values():
        await db.refresh(p)

    # ✅ سفارش پرداخت‌شده برای buyer_reza
    order = Order(
        user_id=users["buyer_reza"].id,
        total_amount=products["private"].price,
        status="paid",  # ⚠️ باید "paid" باشد
        shipping_address="Test Address",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    order_item = OrderItem(
        order_id=order.id,
        product_id=products["private"].id,
        quantity=1,
        price_at_time=products["private"].price,
    )
    db.add(order_item)
    await db.commit()

    return {
        "users": users,
        "products": products,
    }


@pytest.fixture
def get_token():
    from app.core.auth import create_access_token

    def _get_token(username: str):
        return create_access_token(claims={"sub": username})

    return _get_token


@pytest.fixture(scope="function")
def override_get_db(db: AsyncSession):
    async def _override():
        yield db

    return _override


@pytest.fixture(scope="function")
def test_client(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    yield AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    app.dependency_overrides.clear()
