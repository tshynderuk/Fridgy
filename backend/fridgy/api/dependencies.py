"""Composition root: єдине місце, де створюються залежності застосунку.

Заміна реалізації (справжній Gemini <-> підробка) відбувається лише тут
(через AI_PROVIDER у .env) або через app.dependency_overrides у тестах.
"""
from functools import lru_cache

from fastapi import Depends

from fridgy.core.config import Settings, load_settings
from fridgy.domain.errors import ProviderNotConfiguredError
from fridgy.domain.interfaces import RecipeProvider
from fridgy.infrastructure.providers.gemini_provider import GeminiProvider
from fridgy.infrastructure.providers.mock_provider import MockProvider
from fridgy.services.recipe_service import RecipeService

_provider: RecipeProvider | None = None


@lru_cache
def get_settings() -> Settings:
    return load_settings()


def build_provider(settings: Settings) -> RecipeProvider:
    """Створює провайдер за налаштуваннями (AI_PROVIDER)."""
    if settings.provider == "mock":
        return MockProvider()

    if settings.provider == "gemini":
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
            timeout_s=settings.ai_timeout_s,
        )

    raise ProviderNotConfiguredError(
        f"Невідоме значення AI_PROVIDER: {settings.provider!r}."
    )


def get_provider(settings: Settings = Depends(get_settings)) -> RecipeProvider:
    """Один провайдер на весь процес сервера."""
    global _provider
    if _provider is None:
        _provider = build_provider(settings)
    return _provider


def get_recipe_service(
    provider: RecipeProvider = Depends(get_provider),
    settings: Settings = Depends(get_settings),
) -> RecipeService:
    return RecipeService(provider, timeout_s=settings.ai_timeout_s)


async def close_provider() -> None:
    """Викликається під час зупинки сервера."""
    global _provider
    if _provider is not None:
        close = getattr(_provider, "aclose", None)
        if close is not None:
            await close()
        _provider = None
