from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import configure_logging
from app.api.v1.api import router as api_v1_router
from app.db.session import engine
from app.db.base import Base


configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ایجاد جدول‌ها
    async with engine.begin() as conn:
       
        await conn.run_sync(Base.metadata.drop_all) #delete all tables
        await conn.run_sync(Base.metadata.create_all) #build all tables
    yield
    # Shutdown: اگر نیاز به پاک‌سازی یا بستن منابع داری، اینجا بنویس
    # مثلاً await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan  # ← lifespam added too app
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router, prefix="/api/v1")

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    @app.get("/health/liveness")
    async def liveness():
        return {"status": "ok"}

    return app

app = create_app()