from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.entities.user import User
from app.entities.product import Product

from app.auth.dependencies import authorize
from app.auth.engine import ABACEngine
from app.core.config import settings
from app.schema.response import success


from app.core.auth import (
    create_access_token,
    get_current_user,
    authenticate_user,
    get_current_product,
)


router = APIRouter()
engine = ABACEngine()

"""
# Mock user DB (replace with real DB in production)
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": get_password_hash("secret"),
    }
}
"""


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


@router.post(
    "/login",
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        claims={"sub": form_data.username}, expires_delta=access_token_expires
    )

    return success(
        {"access_token": access_token, "token_type": "bearer"},
        flat=True,
    )
