# app/constants/error_const.py
from enum import Enum


class ErrorMsg(Enum):
    INTERNAL_SERVER_ERROR = 0
    UNIQUE_CONSTRAINT_VIOLATION = 1
