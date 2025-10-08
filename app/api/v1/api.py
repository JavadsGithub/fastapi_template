from fastapi import APIRouter
from app.controller.item import router as item_router
from app.controller.auth import router as auth_router
#from app.controller.abac_test import router as abac_test

router = APIRouter()
router.include_router(item_router, prefix="/items", tags=["items"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
#router.include_router(abac_test, prefix="/abac-test", tags=["ABAC Test"])