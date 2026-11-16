"""Доменні моделі. Не залежать від Pydantic, FastAPI чи AI SDK."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RecipeQuery:
    """Що просить користувач: продукти та максимальний час приготування."""

    ingredients: list[str]
    max_time_minutes: int


@dataclass(frozen=True)
class Recipe:
    """Один рецепт у доменному вигляді."""

    name: str
    cooking_time_minutes: int
    ingredients: list[str]
    instructions: list[str]
