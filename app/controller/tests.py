from fastapi import APIRouter, Depends

from app.entities.user import User
from app.entities.product import Product

from app.auth.dependencies import authorize


from app.core.auth import (
    get_current_user,
    get_current_product,
)


router = APIRouter()


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/get_product/{product_id}")
async def get_product(current_product: Product = Depends(get_current_product)):
    return current_product


@router.delete(
    "/delete-product/{product_id}",
    dependencies=[Depends(authorize("delete", "product"))],
)
async def delete_product(product_id: int):
    return {"message": f"Product {product_id} deleted successfully"}


@router.get(
    "/download-product/{product_id}",
    dependencies=[Depends(authorize("download", "product"))],
)
async def download_product(product_id: int):
    return {"message": "Download allowed"}
