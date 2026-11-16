"""Тести RecipeService із підробленим провайдером (без мережі та ключа)."""
import asyncio

import pytest

from fridgy.domain.errors import (
    InvalidProviderResponseError,
    ProviderQuotaExceededError,
    ProviderTimeoutError,
)
from fridgy.domain.models import Recipe, RecipeQuery
from fridgy.infrastructure.providers.mock_provider import MockProvider
from fridgy.services.recipe_service import RecipeService

QUERY = RecipeQuery(ingredients=["рис", "курка"], max_time_minutes=40)


def make_recipe(name="Страва", minutes=20, steps=3, ingredients=None):
    return Recipe(
        name=name,
        cooking_time_minutes=minutes,
        ingredients=["Рис — 100 г"] if ingredients is None else ingredients,
        instructions=[f"Крок {i + 1}" for i in range(steps)],
        source="mock",
    )


def three(**overrides):
    """Три різні валідні рецепти; другий можна змінити через overrides."""
    return [
        make_recipe("Страва А"),
        make_recipe(**{"name": "Страва Б", **overrides}),
        make_recipe("Страва В"),
    ]


def suggest(recipes, timeout_s=5):
    service = RecipeService(MockProvider(recipes=recipes), timeout_s=timeout_s)
    return asyncio.run(service.suggest(QUERY))


def test_returns_three_valid_recipes():
    result = suggest(three())

    assert [r.name for r in result] == ["Страва А", "Страва Б", "Страва В"]


def test_trims_whitespace_and_drops_empty_items():
    recipes = three(
        name="  Страва Б  ",
        ingredients=["  Рис — 100 г  ", "   ", ""],
    )

    result = suggest(recipes)

    assert result[1].name == "Страва Б"
    assert result[1].ingredients == ["Рис — 100 г"]


def test_calls_provider_once_with_the_query():
    provider = MockProvider()
    service = RecipeService(provider, timeout_s=5)

    asyncio.run(service.suggest(QUERY))

    assert provider.calls == [QUERY]


@pytest.mark.parametrize("count", [2, 4])
def test_rejects_wrong_number_of_recipes(count):
    recipes = [make_recipe(f"Страва {i}") for i in range(count)]

    with pytest.raises(InvalidProviderResponseError):
        suggest(recipes)


def test_rejects_duplicate_names_ignoring_case():
    recipes = [make_recipe("Борщ"), make_recipe("борщ"), make_recipe("Суп")]

    with pytest.raises(InvalidProviderResponseError):
        suggest(recipes)


@pytest.mark.parametrize(
    "overrides",
    [
        {"name": "   "},            # порожня назва
        {"ingredients": ["  "]},    # інгредієнтів немає
        {"steps": 2},               # замало кроків
        {"steps": 11},              # забагато кроків
        {"minutes": 41},            # понад ліміт 40 хвилин
        {"minutes": 0},             # нульовий час
    ],
)
def test_rejects_invalid_recipe(overrides):
    with pytest.raises(InvalidProviderResponseError):
        suggest(three(**overrides))


def test_provider_error_is_propagated_unchanged():
    provider = MockProvider(error=ProviderQuotaExceededError("quota"))
    service = RecipeService(provider, timeout_s=5)

    with pytest.raises(ProviderQuotaExceededError):
        asyncio.run(service.suggest(QUERY))


def test_slow_provider_gives_timeout_error():
    class SlowProvider:
        async def generate(self, query):
            await asyncio.sleep(1)
            return []

    service = RecipeService(SlowProvider(), timeout_s=0.01)

    with pytest.raises(ProviderTimeoutError):
        asyncio.run(service.suggest(QUERY))
