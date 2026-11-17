"""Централізоване перетворення помилок домену на HTTP-відповіді.

Користувач отримує зрозуміле повідомлення без stack trace і технічних
подробностей; технічні деталі лишаються в журналі сервера.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from fridgy.domain.errors import (
    DomainError,
    InvalidProviderResponseError,
    ProviderNotConfiguredError,
    ProviderQuotaExceededError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

logger = logging.getLogger("fridgy")

DEFAULT_RESPONSE = (
    502,
    "Не вдалося створити рецепти через AI. Перевірте журнал сервера.",
)

_RESPONSES = [
    (
        ProviderNotConfiguredError,
        503,
        "AI ще не налаштований. Додайте GEMINI_API_KEY у файл backend/.env.",
    ),
    (
        ProviderUnavailableError,
        503,
        "Gemini тимчасово перевантажений. Спробуйте трохи пізніше.",
    ),
    (
        ProviderQuotaExceededError,
        429,
        "Перевищено ліміт запитів Gemini. Спробуйте пізніше.",
    ),
    (ProviderTimeoutError, 504, "AI довго не відповідає. Спробуйте ще раз."),
    (InvalidProviderResponseError, *DEFAULT_RESPONSE),
]


def describe(exc: Exception) -> tuple[int, str]:
    """Повертає (HTTP-статус, повідомлення) для помилки."""
    for error_type, status, detail in _RESPONSES:
        if isinstance(exc, error_type):
            return status, detail
    return DEFAULT_RESPONSE


async def domain_error_handler(request: Request, exc: Exception) -> JSONResponse:
    status, detail = describe(exc)
    logger.error("Recipe generation failed: %s", type(exc).__name__, exc_info=exc)
    return JSONResponse(status_code=status, content={"detail": detail})


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    status, detail = DEFAULT_RESPONSE
    logger.error("Unexpected error: %s", type(exc).__name__, exc_info=exc)
    return JSONResponse(status_code=status, content={"detail": detail})


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(Exception, unexpected_error_handler)
