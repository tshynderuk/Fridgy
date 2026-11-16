"""Помилки прикладного рівня (domain errors).

Вони нічого не знають про HTTP-коди та конкретний AI SDK.
Перетворення на HTTP-відповіді виконується централізовано в api/error_handlers.py.
"""


class DomainError(Exception):
    """Базовий тип контрольованих помилок застосунку."""


class ProviderNotConfiguredError(DomainError):
    """AI-провайдер не налаштований (наприклад, відсутній API-ключ)."""


class ProviderUnavailableError(DomainError):
    """AI-провайдер тимчасово недоступний або перевантажений."""


class ProviderQuotaExceededError(DomainError):
    """Вичерпано ліміт запитів до AI-провайдера."""


class ProviderTimeoutError(DomainError):
    """AI-провайдер не відповів у відведений час."""


class InvalidProviderResponseError(DomainError):
    """Відповідь AI не пройшла перевірку (структура або бізнес-правила)."""


class ProviderError(DomainError):
    """Будь-яка інша помилка AI-провайдера."""
