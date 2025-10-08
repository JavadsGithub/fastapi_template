from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.exceptions import ValidationException
from fastapi.security import OAuth2PasswordRequestForm
from app.auth.dependencies import get_current_user2
from pydantic import BaseModel
from app.auth.dependencies import authorize

from app.core.auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.core.config import settings
from app.schema.response import success

router = APIRouter()

from app.auth.engine import ABACEngine


engine = ABACEngine()

# Mock user DB (replace with real DB in production)
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": get_password_hash("secret"),
    }
}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


@router.post(
    "/login",
)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        claims={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return success({"access_token": access_token, "token_type": "bearer"})


@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['username']}, you are authenticated!"}


@router.delete("/delete-product2/{product_id}", dependencies=[Depends(authorize("delete", "product"))],)
def delete_product2(product_id: int, 
                    current_user: dict = Depends(get_current_user2),
                    ):
    """
    Route تستی برای بررسی سیاست‌های ABAC.
    """
    return {"message": f"✅ User {current_user['username']} authorized to delete product {product_id}"}


""""
@router.get("/delete-product")
def delete_product(product_id: int, current_user: dict = Depends(get_current_user2)):
    
    #Route تستی برای بررسی سیاست‌های ABAC.
    
    context = {
        "user": current_user,
        "resource": {"type": "product", "id": product_id},
        "action": "delete",
        "env": {"hour": 10},
    }

    allowed = engine.check_access(context)

    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied")

    return {"message": f"User {current_user['username']} is allowed to delete product {product_id}"}
"""


