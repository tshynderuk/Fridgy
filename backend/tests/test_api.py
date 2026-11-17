"""Тести HTTP-шару через TestClient та dependency_overrides.

Реальний Gemini не використовується: у застосунок підставляється MockProvider.
Тести замінюють baseline-тести, написані до рефакторингу (коміт 4a59838):
перевіряються ті самі HTTP-коди та правила.
"""
import pytest
from fastapi.testclient import TestClient

from fridgy.api.dependencies import get_provider, get_settings
from fridgy.core.config import Settings
from fridgy.domain.errors import (
    InvalidProviderResponseError,
    ProviderError,
    ProviderNotConfiguredError,
    ProviderQuotaExceededError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from fridgy.domain.models import Recipe
from fridgy.infrastructure.providers.mock_provider import MockProvider
from main import app

client = TestClient(app)

VALID_BODY = {"ingredients": ["куряче філе", "рис"], "max_time_minutes": 40}


@pytest.fixture(autouse=True)
def isolated_dependencies():
    """Тести не залежать від .env: налаштування та провайдер підміняються."""
    app.dependency_overrides[get_settings] = lambda: Settings(
        provider="mock", ai_timeout_s=5
    )
    yield
    app.dependency_overrides.clear()


def use_provider(provider):
    app.dependency_overrides[get_provider] = lambda: provider
    return provider


def make_recipe(name, minutes=30, steps=3, source="gemini"):
    return Recipe(
        name=name,
        cooking_time_minutes=minutes,
        ingredients=["Інгредієнт — 100 г"],
        instructions=[f"Крок {i + 1}" for i in range(steps)],
        source=source,
    )


def three_valid():
    return [
        make_recipe("Страва А", 20),
        make_recipe("Страва Б", 25),
        make_recipe("Страва В", 30),
    ]


# --- доступність та вхідні дані ---

def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_empty_ingredients_is_422():
    response = client.post(
        "/recipe", json={"ingredients": [], "max_time_minutes": 40}
    )

    assert response.status_code == 422


@pytest.mark.parametrize("minutes", [4, 181])
def test_time_out_of_range_is_422(minutes):
    response = client.post(
        "/recipe",
        json={"ingredients": ["рис"], "max_time_minutes": minutes},
    )

    assert response.status_code == 422


# --- успішний сценарій ---

def test_success_returns_three_recipes_in_contract_format():
    use_provider(MockProvider(recipes=three_valid()))

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert [r["recipe_name"] for r in data] == ["Страва А", "Страва Б", "Страва В"]
    assert all(r["source"] == "gemini" for r in data)
    assert set(data[0]) == {
        "recipe_name",
        "cooking_time_minutes",
        "ingredients",
        "instructions",
        "source",
    }


def test_mock_provider_marks_source_as_mock():
    use_provider(MockProvider())

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == 200
    assert all(r["source"] == "mock" for r in response.json())


def test_normalized_ingredients_reach_the_provider():
    provider = use_provider(MockProvider())

    response = client.post(
        "/recipe",
        json={
            "ingredients": ["Рис", "рис ", "  курка  "],
            "max_time_minutes": 40,
        },
    )

    assert response.status_code == 200
    assert provider.calls[0].ingredients == ["Рис", "курка"]
    assert provider.calls[0].max_time_minutes == 40


# --- перетворення помилок домену на HTTP-відповіді ---

@pytest.mark.parametrize(
    "error, expected_status",
    [
        (ProviderNotConfiguredError("no key"), 503),
        (ProviderUnavailableError("busy"), 503),
        (ProviderQuotaExceededError("quota"), 429),
        (ProviderTimeoutError("slow"), 504),
        (InvalidProviderResponseError("bad json"), 502),
        (ProviderError("something broke"), 502),
    ],
)
def test_domain_errors_are_mapped_to_http_codes(error, expected_status):
    use_provider(MockProvider(error=error))

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == expected_status
    # технічний текст помилки не потрапляє до користувача
    assert str(error) not in response.json()["detail"]


def test_missing_key_message_mentions_env_setting():
    use_provider(MockProvider(error=ProviderNotConfiguredError("no key")))

    response = client.post("/recipe", json=VALID_BODY)

    assert "GEMINI_API_KEY" in response.json()["detail"]


# --- бізнес-правила, що діють через весь стек ---

def test_recipe_over_time_limit_is_rejected():
    recipes = [make_recipe("А", 30), make_recipe("Б", 30), make_recipe("В", 60)]
    use_provider(MockProvider(recipes=recipes))

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == 502


def test_duplicate_recipe_names_are_rejected():
    recipes = [make_recipe("Борщ"), make_recipe("борщ"), make_recipe("Суп")]
    use_provider(MockProvider(recipes=recipes))

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == 502


def test_recipe_with_too_few_steps_is_rejected():
    recipes = [make_recipe("А"), make_recipe("Б", steps=2), make_recipe("В")]
    use_provider(MockProvider(recipes=recipes))

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == 502
