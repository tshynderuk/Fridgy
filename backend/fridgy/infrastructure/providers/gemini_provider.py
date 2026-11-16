"""Адаптер до Google Gemini.

Єдине місце в проєкті, де використовується AI SDK (google-genai).
Типи SDK не виходять за межі цього файлу: назовні повертаються доменні
Recipe або помилки з fridgy.domain.errors.
"""
import logging
from typing import List

from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError

from fridgy.domain.errors import (
    DomainError,
    InvalidProviderResponseError,
    ProviderError,
    ProviderNotConfiguredError,
    ProviderQuotaExceededError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from fridgy.domain.models import Recipe, RecipeQuery

logger = logging.getLogger("fridgy")

SOURCE = "gemini"


class _GeneratedRecipe(BaseModel):
    """Схема, яку Gemini заповнює (специфічна для SDK, тому приватна)."""

    recipe_name: str = Field(description="Коротка зрозуміла назва страви українською.")
    cooking_time_minutes: int = Field(description="Загальний час приготування у хвилинах.")
    ingredients: List[str] = Field(description="Список інгредієнтів із приблизною кількістю.")
    instructions: List[str] = Field(description="Від 3 до 10 послідовних кроків приготування.")


class _GeneratedRecipes(BaseModel):
    recipes: List[_GeneratedRecipe] = Field(
        description="Список рівно з трьох різних рецептів."
    )


def build_prompt(query: RecipeQuery) -> str:
    ingredient_list = "\n".join(f"- {item}" for item in query.ingredients)
    max_time_minutes = query.max_time_minutes

    return f"""
Ти — кулінарний AI-помічник мобільного застосунку Fridgy.

Створи РІВНО ТРИ різні, реалістичні та смачні рецепти українською мовою.

Продукти, які користувач має:
{ingredient_list}

Максимальний час приготування для КОЖНОЇ страви:
{max_time_minutes} хвилин.

Кількість порцій: 1–2.

Обов'язкові правила:

1. Створи рівно три різні страви.
2. Рецепти повинні відрізнятися за назвою та способом приготування.
3. Використовуй надані продукти як основу кожного рецепта.
4. Не вимагай інших основних продуктів, яких немає у списку.
5. Сіль, перець, вода та олія можуть бути необов'язковими базовими продуктами.
6. Не вигадуй, що користувач має інші продукти.
7. Час приготування КОЖНОГО рецепта не повинен перевищувати {max_time_minutes} хвилин.
8. Вкажи приблизну кількість кожного інгредієнта.
9. Для кожного рецепта дай від 3 до 7 послідовних кроків.
10. Для м'яса, птиці, риби та яєць забезпечуй достатню термічну обробку.
11. Не повторюй одну страву під різними назвами.
12. Поверни лише дані відповідно до JSON-схеми.

Усі текстові значення мають бути українською мовою.
"""


def _translate_error(exc: Exception) -> DomainError:
    """Перетворює технічну помилку SDK на категорію помилки домену."""
    if isinstance(exc, DomainError):
        return exc
    if isinstance(exc, TimeoutError):
        return ProviderTimeoutError(str(exc))

    text = str(exc).upper()
    if "503" in text or "UNAVAILABLE" in text:
        return ProviderUnavailableError(str(exc))
    if "429" in text or "RESOURCE_EXHAUSTED" in text:
        return ProviderQuotaExceededError(str(exc))
    return ProviderError(str(exc))


def _parse_response(response) -> list[Recipe]:
    parsed = getattr(response, "parsed", None)

    try:
        if parsed is not None:
            result = _GeneratedRecipes.model_validate(parsed)
        else:
            text = getattr(response, "text", None)
            if not text:
                raise InvalidProviderResponseError("AI повернув порожню відповідь.")
            result = _GeneratedRecipes.model_validate_json(text)
    except ValidationError as exc:
        raise InvalidProviderResponseError(
            "Некоректна структура відповіді AI."
        ) from exc

    return [
        Recipe(
            name=item.recipe_name,
            cooking_time_minutes=item.cooking_time_minutes,
            ingredients=list(item.ingredients),
            instructions=list(item.instructions),
            source=SOURCE,
        )
        for item in result.recipes
    ]


class GeminiProvider:
    """Реалізація RecipeProvider на основі Google Gemini."""

    def __init__(self, api_key: str, model: str, timeout_s: float, client=None):
        self._model = model
        if client is not None:
            # Можна передати готовий (наприклад, підроблений) клієнт для тестів.
            self._client = client
        elif api_key:
            self._client = genai.Client(
                api_key=api_key,
                http_options=types.HttpOptions(timeout=int(timeout_s * 1000)),
            )
        else:
            self._client = None

    async def generate(self, query: RecipeQuery) -> list[Recipe]:
        if self._client is None:
            raise ProviderNotConfiguredError("GEMINI_API_KEY is not configured.")

        logger.info("Sending 3 recipes request to Gemini model %s", self._model)

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=build_prompt(query),
                config=types.GenerateContentConfig(
                    max_output_tokens=2400,
                    response_mime_type="application/json",
                    response_schema=_GeneratedRecipes,
                    thinking_config=types.ThinkingConfig(thinking_level="low"),
                ),
            )
        except Exception as exc:  # SDK піднімає різні типи помилок
            raise _translate_error(exc) from exc

        return _parse_response(response)

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aio.aclose()
            self._client.close()
