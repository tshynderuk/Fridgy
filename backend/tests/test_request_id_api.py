"""Тести request_id через HTTP: заголовок відповіді та передача в глибину стека."""
import re

import pytest
from fastapi.testclient import TestClient

from fridgy.api.dependencies import get_provider, get_settings
from fridgy.core.config import Settings
from fridgy.core.request_context import HEADER_NAME, request_id_var
from fridgy.domain.errors import ProviderUnavailableError
from fridgy.infrastructure.providers.mock_provider import MockProvider
from main import app

client = TestClient(app)

VALID_BODY = {"ingredients": ["рис"], "max_time_minutes": 40}
GENERATED = re.compile(r"^[0-9a-f]{32}$")


@pytest.fixture(autouse=True)
def isolated_dependencies():
    app.dependency_overrides[get_settings] = lambda: Settings(
        provider="mock", ai_timeout_s=5
    )
    yield
    app.dependency_overrides.clear()


class SpyProvider(MockProvider):
    """Запам'ятовує request_id, який бачить провайдер усередині запиту."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.seen_request_id = None

    async def generate(self, query):
        self.seen_request_id = request_id_var.get()
        return await super().generate(query)


def test_response_contains_generated_request_id():
    response = client.get("/health")

    assert GENERATED.match(response.headers[HEADER_NAME])


def test_incoming_request_id_is_echoed_back():
    response = client.get("/health", headers={HEADER_NAME: "client-req-1"})

    assert response.headers[HEADER_NAME] == "client-req-1"


def test_unsafe_incoming_request_id_is_replaced():
    response = client.get("/health", headers={HEADER_NAME: "bad id!"})

    assert GENERATED.match(response.headers[HEADER_NAME])


def test_error_responses_also_carry_request_id():
    provider = MockProvider(error=ProviderUnavailableError("busy"))
    app.dependency_overrides[get_provider] = lambda: provider

    response = client.post("/recipe", json=VALID_BODY)

    assert response.status_code == 503
    assert GENERATED.match(response.headers[HEADER_NAME])


def test_request_id_reaches_the_provider_layer():
    spy = SpyProvider()
    app.dependency_overrides[get_provider] = lambda: spy

    response = client.post(
        "/recipe", json=VALID_BODY, headers={HEADER_NAME: "trace-777"}
    )

    assert response.status_code == 200
    assert response.headers[HEADER_NAME] == "trace-777"
    assert spy.seen_request_id == "trace-777"
