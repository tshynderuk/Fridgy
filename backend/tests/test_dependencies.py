"""Тести composition root: вибір реалізації провайдера за налаштуваннями."""
import pytest

from fridgy.api.dependencies import build_provider
from fridgy.core.config import Settings
from fridgy.domain.errors import ProviderNotConfiguredError
from fridgy.infrastructure.providers.gemini_provider import GeminiProvider
from fridgy.infrastructure.providers.mock_provider import MockProvider


def test_mock_setting_builds_mock_provider():
    assert isinstance(build_provider(Settings(provider="mock")), MockProvider)


def test_gemini_setting_builds_gemini_provider_without_network():
    provider = build_provider(Settings(provider="gemini", gemini_api_key=""))

    assert isinstance(provider, GeminiProvider)


def test_unknown_provider_is_reported_as_not_configured():
    with pytest.raises(ProviderNotConfiguredError):
        build_provider(Settings(provider="something-else"))
