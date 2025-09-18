from fastapi import APIRouter
from app.modules.item.controller import router as item_router

router = APIRouter()
router.include_router(item_router, prefix="/items", tags=["items"])
