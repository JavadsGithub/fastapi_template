from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.api.v1.api import router as api_v1_router
from app.core.config import settings
from app.core.logging import configure_logging

from .utils.error import register_error_handlers

configure_logging()


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
