from fastapi import APIRouter
from app.modules.items import items_controller

router = APIRouter()
router.include_router(items_controller.router, prefix="/items", tags=["items"])
