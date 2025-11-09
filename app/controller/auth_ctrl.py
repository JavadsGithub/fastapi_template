# app/controller/auth_ctrl.py
from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.service.auth_serv import AuthService
from app.service.user_serv import UserService
from app.dependencies.service_deps import get_user_service, get_auth_service

from app.schema.response import success

from app.schema.user import (
    UserRegister,
    UserReadSelf,
)

router = APIRouter()


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    request: Request = None,
):
    token = await auth_service.login(
        form_data.username, form_data.password, request=request
    )
    return success(token, flat=True)


# ۱. ثبت‌نام عمومی (self register) -> POST /users
@router.post("/users", response_model=UserReadSelf, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    request: Request,
    service: UserService = Depends(get_user_service),
):
    return await service.register_user(user_in=user_data, request=request)
