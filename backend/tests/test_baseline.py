"""Baseline-тести ЛР5: фіксують поточну поведінку backend ДО рефакторингу.

Реальний Gemini не викликається: клієнт підміняється fake-об'єктом,
тому тестам не потрібні ні мережа, ні API-ключ.
"""
import asyncio
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

import main

client = TestClient(main.app)

VALID_BODY = {"ingredients": ["куряче філе", "рис"], "max_time_minutes": 40}


def make_recipe(name, minutes=30, steps=3):
    return main.GeneratedRecipe(
        recipe_name=name,
        cooking_time_minutes=minutes,
        ingredients=["Інгредієнт — 100 г"],
        instructions=[f"Крок {i + 1}" for i in range(steps)],
    )


def make_recipes(*items):
    return main.GeneratedRecipes(recipes=list(items))


class FakeGeminiClient:
    """Підміна genai.Client: повертає заданий результат або кидає помилку."""

    def __init__(self, parsed=None, error=None):
        self.last_kwargs = None
        outer = self

        class _Models:
            async def generate_content(self, **kwargs):
                outer.last_kwargs = kwargs
                if error is not None:
                    raise error
                return SimpleNamespace(parsed=parsed, text=None)

        self.aio = SimpleNamespace(models=_Models())


def use_fake(monkeypatch, parsed=None, error=None):
    fake = FakeGeminiClient(parsed=parsed, error=error)
    monkeypatch.setattr(main, "gemini_client", fake)
    return fake


def three_valid():
    return make_recipes(
        make_recipe("Страва А", 20),
        make_recipe("Страва Б", 25),
        make_recipe("Страва В", 30),
    )


# --- перевірка доступності та вхідних даних ---

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

def test_success_returns_three_recipes_with_source_gemini(monkeypatch):
    use_fake(monkeypatch, parsed=three_valid())

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert [r["recipe_name"] for r in data] == ["Страва А", "Страва Б", "Страва В"]
    assert all(r["source"] == "gemini" for r in data)


def test_ingredients_are_normalized_in_prompt(monkeypatch):
    fake = use_fake(monkeypatch, parsed=three_valid())

    response = client.post(
        "/recipe",
        json={
            "ingredients": ["Рис", "рис ", "  курка  "],
            "max_time_minutes": 40,
        },
    )

    assert response.status_code == 200
    prompt = fake.last_kwargs["contents"]
    assert "- Рис\n- курка" in prompt
    assert "- рис" not in prompt
    assert "40 хвилин" in prompt


# --- помилки конфігурації та зовнішнього сервісу ---

def test_missing_api_key_gives_503(monkeypatch):
    monkeypatch.setattr(main, "gemini_client", None)

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]


@pytest.mark.parametrize(
    "error_text, expected_status",
    [
        ("503 UNAVAILABLE: model is busy", 503),
        ("429 RESOURCE_EXHAUSTED: quota exceeded", 429),
        ("something unexpected broke", 502),
    ],
)
def test_gemini_errors_are_mapped_to_http_codes(
    monkeypatch, error_text, expected_status
):
    use_fake(monkeypatch, error=Exception(error_text))

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == expected_status
    # технічний текст помилки не повинен потрапляти до користувача
    assert error_text not in response.json()["detail"]


def test_timeout_gives_504(monkeypatch):
    use_fake(monkeypatch, error=asyncio.TimeoutError())

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == 504


# --- бізнес-правила перевірки відповіді AI ---

def test_recipe_over_time_limit_is_rejected(monkeypatch):
    parsed = make_recipes(
        make_recipe("Страва А", 30),
        make_recipe("Страва Б", 30),
        make_recipe("Страва В", 60),  # понад ліміт 40 хвилин
    )
    use_fake(monkeypatch, parsed=parsed)

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == 502


def test_duplicate_recipe_names_are_rejected(monkeypatch):
    parsed = make_recipes(
        make_recipe("Борщ"),
        make_recipe("борщ"),  # та сама назва в іншому регістрі
        make_recipe("Суп"),
    )
    use_fake(monkeypatch, parsed=parsed)

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == 502


def test_recipe_with_too_few_steps_is_rejected(monkeypatch):
    parsed = make_recipes(
        make_recipe("Страва А"),
        make_recipe("Страва Б", steps=2),  # менше 3 кроків
        make_recipe("Страва В"),
    )
    use_fake(monkeypatch, parsed=parsed)

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == 502


def test_model_requires_exactly_three_recipes():
    with pytest.raises(ValidationError):
        make_recipes(make_recipe("Страва А"), make_recipe("Страва Б"))