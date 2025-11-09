# app/api/v1/api.py
from fastapi import APIRouter
from app.controller.item_ctrl import router as item_router
from app.controller.auth_ctrl import router as auth_router
from app.controller.tests_ctrl import router as tests_router
from app.controller.seed_ctrl import router as seed_router
from app.controller.user_ctrl import router as user_router

router = APIRouter()
router.include_router(item_router, prefix="/items", tags=["items"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(tests_router, prefix="/tests", tags=["tests"])
router.include_router(seed_router, prefix="/seed", tags=["seed"])
router.include_router(user_router, prefix="/user", tags=["user"])
