"""Прикладний сценарій: отримати від провайдера три валідні рецепти.

Сервіс не знає ні про HTTP, ні про конкретний AI SDK: він працює з
інтерфейсом RecipeProvider і кидає помилки з fridgy.domain.errors.
"""
import asyncio
from dataclasses import replace

from fridgy.domain.errors import InvalidProviderResponseError, ProviderTimeoutError
from fridgy.domain.interfaces import RecipeProvider
from fridgy.domain.models import Recipe, RecipeQuery

RECIPES_COUNT = 3
MIN_STEPS = 3
MAX_STEPS = 10


class RecipeService:
    def __init__(self, provider: RecipeProvider, timeout_s: float):
        self._provider = provider
        self._timeout_s = timeout_s

    async def suggest(self, query: RecipeQuery) -> list[Recipe]:
        """Повертає рівно три перевірені рецепти або кидає помилку домену."""
        try:
            recipes = await asyncio.wait_for(
                self._provider.generate(query),
                timeout=self._timeout_s,
            )
        except asyncio.TimeoutError as exc:
            raise ProviderTimeoutError(
                f"Провайдер не відповів за {self._timeout_s} с."
            ) from exc

        return self._validate(recipes, query)

    @staticmethod
    def _validate(recipes: list[Recipe], query: RecipeQuery) -> list[Recipe]:
        if len(recipes) != RECIPES_COUNT:
            raise InvalidProviderResponseError("AI має повернути рівно три рецепти.")

        cleaned: list[Recipe] = []
        seen_names: set[str] = set()

        for recipe in recipes:
            name = recipe.name.strip()
            ingredients = [item.strip() for item in recipe.ingredients if item.strip()]
            instructions = [step.strip() for step in recipe.instructions if step.strip()]

            if not name:
                raise InvalidProviderResponseError("AI не повернув назву страви.")

            key = name.casefold()
            if key in seen_names:
                raise InvalidProviderResponseError("AI повернув повторювані рецепти.")
            seen_names.add(key)

            if not ingredients:
                raise InvalidProviderResponseError("AI не повернув інгредієнти.")

            if not MIN_STEPS <= len(instructions) <= MAX_STEPS:
                raise InvalidProviderResponseError(
                    "AI повернув некоректну кількість кроків."
                )

            if not 1 <= recipe.cooking_time_minutes <= query.max_time_minutes:
                raise InvalidProviderResponseError(
                    "AI повернув час, що перевищує обмеження користувача."
                )

            cleaned.append(
                replace(
                    recipe,
                    name=name,
                    ingredients=ingredients,
                    instructions=instructions,
                )
            )

        return cleaned
