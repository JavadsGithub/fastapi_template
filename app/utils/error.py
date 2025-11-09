# app/utils/error.py
from http import HTTPStatus
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schema.response import StandardResponse


def register_error_handlers(app):
    """Register custom error handlers with the FastAPI app."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content=StandardResponse(
                success=False, message=exc.detail, payload=None
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content=StandardResponse(
                success=False,
                message="Validation error",
                payload={"errors": exc.errors()},
            ).model_dump(),
        )
