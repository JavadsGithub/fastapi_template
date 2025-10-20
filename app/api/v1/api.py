from fastapi import APIRouter
from app.controller.item import router as item_router
from app.controller.auth import router as auth_router
from app.controller.tests import router as tests_router
from app.controller.seed import router as seed_router

router = APIRouter()
router.include_router(item_router, prefix="/items", tags=["items"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(tests_router, prefix="/tests", tags=["tests"])
router.include_router(seed_router, prefix="/seed", tags=["seed"])
