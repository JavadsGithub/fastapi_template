# app/controller/user_ctrl.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.core.auth import get_current_user
from app.entities.user import User

from app.service.user_serv import UserService
from app.dependencies.service_deps import get_user_service

from app.schema.user import (
    UserCreateByAdmin,
    UserUpdateSelf,
    UserUpdateByAdmin,
    UserReadSelf,
    UserReadByAdmin,
    UserListItem,
)

from app.dependencies.auth_deps import authorize  # ABAC dependency

router = APIRouter()


# 1. ایجاد کاربر توسط admin -> POST /admin/users
@router.post(
    "/admin/users",
    response_model=UserReadByAdmin,
    dependencies=[Depends(authorize("create", "user"))],
)
async def create_user_by_admin(
    user_data: UserCreateByAdmin,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return await service.create_user_by_admin(
        current_user=current_user, user_in=user_data, request=request
    )


# 2. دریافت اطلاعات خود کاربر -> GET /users/me
@router.get("/users/me", response_model=UserReadSelf)
async def read_self(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    user = None
    if getattr(current_user, "id", None) is not None:
        user = await service.get_user_by_id(current_user.id)
    user = user or current_user
    return service.user_to_schema(user, UserReadSelf)


# 3. دریافت کاربر خاص (admin) -> GET /admin/users/{user_id}
@router.get(
    "/admin/users/{user_id}",
    response_model=UserReadByAdmin,
    dependencies=[Depends(authorize("read", "user"))],
)
async def read_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return service.user_to_schema(user, UserReadByAdmin)


# 4. لیست کاربران (admin) -> GET /admin/users
@router.get(
    "/admin/users",
    response_model=List[UserListItem],
    dependencies=[Depends(authorize("list", "user"))],
)
async def list_users(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return await service.list_users(current_user=current_user)


# 5. ویرایش توسط خود کاربر -> PUT /users/me
@router.put("/users/me", response_model=UserReadSelf)
async def update_self(
    user_data: UserUpdateSelf,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return await service.update_user_self(
        current_user=current_user,
        user_id=current_user.id,
        update_data=user_data,
        request=request,
    )


# 6. ویرایش توسط admin -> PUT /admin/users/{user_id}
@router.put(
    "/admin/users/{user_id}",
    response_model=UserReadByAdmin,
    dependencies=[Depends(authorize("update", "user"))],
)
async def update_user_by_admin(
    user_id: int,
    user_data: UserUpdateByAdmin,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return await service.update_user_by_admin(
        current_user=current_user,
        user_id=user_id,
        update_data=user_data,
        request=request,
    )


# 7. حذف سخت (hard) توسط admin -> DELETE /admin/users/{user_id}/hard
@router.delete(
    "/admin/users/{user_id}/hard",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(authorize("delete", "user"))],
)
async def hard_delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    deleted = await service.delete_user(
        current_user=current_user, user_id=user_id, request=request
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return None


# 8a. حذف نرم (soft-delete) توسط admin -> DELETE /admin/users/{user_id}
@router.delete(
    "/admin/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(authorize("soft_delete", "user"))],
)
async def soft_delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    deleted = await service.soft_delete_user(
        current_user=current_user, user_id=user_id, request=request
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return None


# 8b. بازیابی (undelete) توسط admin -> POST /admin/users/{user_id}/restore
@router.post(
    "/admin/users/{user_id}/restore",
    response_model=UserReadByAdmin,
    dependencies=[Depends(authorize("undelete", "user"))],
)
async def undelete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    user_schema = await service.undelete_user(
        current_user=current_user, user_id=user_id, request=request
    )
    if not user_schema:
        raise HTTPException(
            status_code=404, detail="User not found or not soft-deleted"
        )
    return user_schema
