"""Інтерфейси зовнішніх залежностей."""
from typing import Protocol

from fridgy.domain.models import Recipe, RecipeQuery


class RecipeProvider(Protocol):
    """Джерело рецептів (справжній AI або підробка для тестів).

    Реалізація повертає список рецептів у доменному вигляді або кидає
    помилку з fridgy.domain.errors. Бізнес-правила (кількість рецептів,
    часовий ліміт тощо) перевіряє сервіс, а не провайдер.
    """

    async def generate(self, query: RecipeQuery) -> list[Recipe]:
        ...
