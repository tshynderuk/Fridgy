"""Тести провайдерів без мережі та API-ключа (ЛР5)."""
import asyncio
import json
from types import SimpleNamespace

import pytest

from fridgy.domain.errors import (
    InvalidProviderResponseError,
    ProviderError,
    ProviderNotConfiguredError,
    ProviderQuotaExceededError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from fridgy.domain.models import RecipeQuery
from fridgy.infrastructure.providers.gemini_provider import GeminiProvider
from fridgy.infrastructure.providers.mock_provider import MockProvider

QUERY = RecipeQuery(ingredients=["рис", "курка"], max_time_minutes=40)

VALID_JSON = json.dumps(
    {
        "recipes": [
            {
                "recipe_name": name,
                "cooking_time_minutes": 20,
                "ingredients": ["Рис — 100 г"],
                "instructions": ["Крок 1", "Крок 2", "Крок 3"],
            }
            for name in ("Страва А", "Страва Б", "Страва В")
        ]
    },
    ensure_ascii=False,
)


class FakeClient:
    """Підміна genai.Client: повертає задану відповідь або кидає помилку."""

    def __init__(self, response=None, error=None):
        self.last_kwargs = None
        outer = self

        class _Models:
            async def generate_content(self, **kwargs):
                outer.last_kwargs = kwargs
                if error is not None:
                    raise error
                return response

        self.aio = SimpleNamespace(models=_Models())


def make_provider(client):
    return GeminiProvider(
        api_key="test-key-not-real", model="test-model", timeout_s=5, client=client
    )


# --- MockProvider ---

def test_mock_provider_returns_three_distinct_recipes():
    recipes = asyncio.run(MockProvider().generate(QUERY))

    assert len(recipes) == 3
    assert len({r.name for r in recipes}) == 3
    assert all(r.source == "mock" for r in recipes)


def test_mock_provider_respects_time_limit():
    query = RecipeQuery(ingredients=["яйця"], max_time_minutes=10)

    recipes = asyncio.run(MockProvider().generate(query))

    assert all(1 <= r.cooking_time_minutes <= 10 for r in recipes)


def test_mock_provider_error_mode_raises():
    provider = MockProvider(error=ProviderUnavailableError("busy"))

    with pytest.raises(ProviderUnavailableError):
        asyncio.run(provider.generate(QUERY))


# --- GeminiProvider (з підробленим клієнтом) ---

def test_gemini_provider_without_key_raises_not_configured():
    provider = GeminiProvider(api_key="", model="m", timeout_s=5)

    with pytest.raises(ProviderNotConfiguredError):
        asyncio.run(provider.generate(QUERY))


@pytest.mark.parametrize(
    "error, expected",
    [
        (Exception("503 UNAVAILABLE: busy"), ProviderUnavailableError),
        (Exception("429 RESOURCE_EXHAUSTED: quota"), ProviderQuotaExceededError),
        (TimeoutError(), ProviderTimeoutError),
        (Exception("something unexpected"), ProviderError),
    ],
)
def test_gemini_provider_translates_sdk_errors(error, expected):
    provider = make_provider(FakeClient(error=error))

    with pytest.raises(expected):
        asyncio.run(provider.generate(QUERY))


def test_gemini_provider_parses_json_text():
    client = FakeClient(response=SimpleNamespace(parsed=None, text=VALID_JSON))

    recipes = asyncio.run(make_provider(client).generate(QUERY))

    assert [r.name for r in recipes] == ["Страва А", "Страва Б", "Страва В"]
    assert all(r.source == "gemini" for r in recipes)


def test_gemini_provider_accepts_parsed_object():
    client = FakeClient(
        response=SimpleNamespace(parsed=json.loads(VALID_JSON), text=None)
    )

    recipes = asyncio.run(make_provider(client).generate(QUERY))

    assert len(recipes) == 3


@pytest.mark.parametrize("text", [None, "", "not a json", '{"recipes": "oops"}'])
def test_gemini_provider_rejects_broken_response(text):
    client = FakeClient(response=SimpleNamespace(parsed=None, text=text))

    with pytest.raises(InvalidProviderResponseError):
        asyncio.run(make_provider(client).generate(QUERY))


def test_gemini_provider_sends_ingredients_limit_and_model():
    client = FakeClient(response=SimpleNamespace(parsed=None, text=VALID_JSON))

    asyncio.run(make_provider(client).generate(QUERY))

    assert client.last_kwargs["model"] == "test-model"
    prompt = client.last_kwargs["contents"]
    assert "- рис\n- курка" in prompt
    assert "40 хвилин" in prompt
