# app/core/logging.py
import logging
import sys


def configure_logging(log_level: str = "INFO") -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    root_logger.setLevel(logging.DEBUG)

    try:
        level = getattr(logging, log_level.upper())
    except AttributeError:
        level = logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(name)-25s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)

    # کم‌صدا کردن لاگ‌های پرسر و صدا
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    # logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    # logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
