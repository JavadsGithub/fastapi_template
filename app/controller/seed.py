from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from sqlalchemy import select
from app.entities.user import User
from app.entities.product import Product
from app.entities.role import Role
from app.entities.order import Order, OrderItem

from app.core.security import get_password_hash

router = APIRouter()


@router.post("/seed", tags=["seed"])
async def seed_test_data(db: AsyncSession = Depends(get_db)):
    """
    فقط برای محیط توسعه!
    این route داده‌های تست زیر را ایجاد می‌کند:
    - نقش‌ها: admin, seller, user
    - کاربران: admin_user, seller_ali, buyer_reza
    - محصولات:
        - Private Dataset (مالک: seller_ali, is_public=False)
        - Public Book (مالک: seller_ali, is_public=True)
    - سفارش: buyer_reza محصول خصوصی را خریده است
    """

    # ---------- 1. ایجاد نقش‌ها ----------
    roles_to_create = ["admin", "seller", "user"]
    for role_title in roles_to_create:
        result = await db.execute(select(Role).where(Role.title == role_title))
        if not result.scalar_one_or_none():
            role = Role(title=role_title, description=f"{role_title} role")
            db.add(role)
    await db.commit()

    # ---------- 2. دریافت نقش‌ها به صورت object ----------
    result = await db.execute(select(Role))
    roles = {role.title: role for role in result.scalars().all()}

    # ---------- 3. ایجاد کاربران ----------
    users_data = [
        {
            "username": "admin_user",
            "email": "admin@example.com",
            "password": "123456",
            "roles": [roles["admin"]],
        },
        {
            "username": "seller_ali",
            "email": "ali@example.com",
            "password": "123456",
            "roles": [roles["seller"]],
        },
        {
            "username": "buyer_reza",
            "email": "reza@example.com",
            "password": "123456",
            "roles": [roles["user"]],
        },
    ]

    created_users = {}
    for ud in users_data:
        result = await db.execute(select(User).where(User.username == ud["username"]))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                username=ud["username"],
                email=ud["email"],
                password_hash=get_password_hash(ud["password"]),
                first_name=ud["username"].split("_")[1].title()
                if "_" in ud["username"]
                else ud["username"],
                is_active=True,
            )
            user.roles = ud["roles"]
            db.add(user)
            await db.flush()  # دریافت id قبل از commit
        created_users[ud["username"]] = user

    await db.commit()

    # ---------- 4. ایجاد محصولات ----------
    products_data = [
        {
            "name": "Private Dataset",
            "description": "A private dataset for buyers only",
            "price": 50.00,
            "file_type": "dataset",
            "owner_id": created_users["seller_ali"].id,
            "is_public": False,
        },
        {
            "name": "Public Book",
            "description": "A free public book for everyone",
            "price": 0.00,
            "file_type": "book",
            "owner_id": created_users["seller_ali"].id,
            "is_public": True,
        },
    ]

    for pd in products_data:
        result = await db.execute(select(Product).where(Product.name == pd["name"]))
        if not result.scalar_one_or_none():
            product = Product(**pd)
            db.add(product)

    await db.commit()

    # ---------- 5. ایجاد سفارش (برای تست purchased) ----------
    result = await db.execute(select(Product).where(Product.name == "Private Dataset"))
    private_product = result.scalar_one_or_none()

    if private_product and "buyer_reza" in created_users:
        existing_order = await db.execute(
            select(Order)
            .join(OrderItem)
            .where(Order.user_id == created_users["buyer_reza"].id)
            .where(OrderItem.product_id == private_product.id)
        )
        if not existing_order.scalar_one_or_none():
            order = Order(
                user_id=created_users["buyer_reza"].id,
                total_amount=private_product.price,
                status="paid",
            )
            db.add(order)
            await db.flush()

            order_item = OrderItem(
                order_id=order.id,
                product_id=private_product.id,
                quantity=1,
                price_at_time=private_product.price,
            )
            db.add(order_item)

    await db.commit()

    # ---------- 6. واکشی نهایی برای نمایش اطلاعات ----------
    result = await db.execute(select(Product))
    all_products = result.scalars().all()

    product_list = [
        {"id": p.id, "name": p.name, "is_public": p.is_public} for p in all_products
    ]

    return {
        "message": "✅ Test data seeded successfully!",
        "users": list(created_users.keys()),
        "products": product_list,
        "note": "Use /api/v1/auth/login to get tokens and test ABAC rules.",
    }
