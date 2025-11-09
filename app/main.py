# app/main.py
from app.core.logging import configure_logging

from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination


from app.api.v1.api import router as api_v1_router
from app.config.base_config import settings
from .utils.error import register_error_handlers

import app.entities  # ✅ این خط مطمئن می‌کنه همه مدل‌ها load شدن
from app.events import (
    user_events,  # noqa: F401
)  # 👈 import این باعث فعال شدن event میشه


configure_logging(log_level="DEBUG")


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)
    add_pagination(app)

    register_error_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router, prefix="/api/v1")

    @app.get("/ping")
    async def ping():
        return "pong"

    @app.get("/error")
    async def error():
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    return app


app = create_app()
