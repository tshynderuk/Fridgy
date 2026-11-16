"""Підроблений провайдер: працює без мережі, ключа та Gemini.

Режими:
- успіх (за замовчуванням) повертає три тестові рецепти, що вкладаються в ліміт часу;
- помилка: передайте error=..., і generate кине цю помилку домену.
"""
from fridgy.domain.errors import DomainError
from fridgy.domain.models import Recipe, RecipeQuery

SOURCE = "mock"


def _default_recipes(query: RecipeQuery) -> list[Recipe]:
    main = query.ingredients[0] if query.ingredients else "продукти"
    base_times = [15, 20, 25]

    return [
        Recipe(
            name=f"Тестова страва №{index}: {main}",
            cooking_time_minutes=min(minutes, query.max_time_minutes),
            ingredients=[f"{item} — 100 г" for item in query.ingredients]
            or ["Вода — 200 мл"],
            instructions=[
                "Підготуйте продукти.",
                "Приготуйте їх до готовності.",
                "Подайте страву.",
            ],
            source=SOURCE,
        )
        for index, minutes in enumerate(base_times, start=1)
    ]


class MockProvider:
    """Реалізація RecipeProvider для тестів і демонстрації без AI."""

    def __init__(
        self,
        error: DomainError | None = None,
        recipes: list[Recipe] | None = None,
    ):
        self._error = error
        self._recipes = recipes
        self.calls: list[RecipeQuery] = []

    async def generate(self, query: RecipeQuery) -> list[Recipe]:
        self.calls.append(query)

        if self._error is not None:
            raise self._error

        if self._recipes is not None:
            return list(self._recipes)

        return _default_recipes(query)

    async def aclose(self) -> None:
        return None
