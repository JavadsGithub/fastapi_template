# app/core/auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status, Path
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.security import verify_password
from app.db.session import get_db
from app.entities.user import User
from app.entities.product import Product
from app.entities.order import Order, OrderItem
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=True)


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


# TODO: use JWTClaims instead of dict
def create_access_token(claims: dict, expires_delta: Optional[timedelta] = None) -> str:
    claims_to_encode = claims.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
        claims_to_encode.update({"exp": expire})
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        claims_to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        claims_to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    stmt = (
        select(User).where(User.username == username).options(selectinload(User.roles))
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_current_product(
    product_id: int = Path(...), db: AsyncSession = Depends(get_db)
) -> Product:
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def get_purchased_product_ids(db: AsyncSession, user_id: int) -> set[int]:
    stmt = (
        select(OrderItem.product_id)
        .join(Order)
        .where(Order.user_id == user_id)
        .where(Order.status == "paid")
    )
    result = await db.scalars(stmt)
    return set(result.all())
