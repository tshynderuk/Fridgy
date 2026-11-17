"""Точка входу Fridgy API: збирає застосунок із готових частин.

Запуск (без змін): python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
Уся логіка винесена в пакет fridgy/ (api, services, domain, infrastructure, core).
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from fridgy.api.dependencies import close_provider, get_settings
from fridgy.api.error_handlers import register_error_handlers
from fridgy.api.middleware import register_request_id_middleware
from fridgy.api.routes import router
from fridgy.core.request_context import configure_logging

configure_logging()
logger = logging.getLogger("fridgy")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(
        "Fridgy backend ready. Gemini model=%s, thinking_level=low, timeout=%ss, provider=%s",
        settings.gemini_model,
        settings.ai_timeout_s,
        settings.provider,
    )
    yield
    await close_provider()


app = FastAPI(
    title="Fridgy API",
    description="AI-підбір рецептів за продуктами користувача",
    version="2.3.0",
    lifespan=lifespan,
)

register_error_handlers(app)
register_request_id_middleware(app)
app.include_router(router)
