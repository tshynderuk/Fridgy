"""Наскрізний request_id: контекстна змінна, фільтр журналу та налаштування логів.

Номер запиту зберігається в contextvar, тому автоматично доступний на всіх
рівнях (роутер, сервіс, провайдер) без передавання параметрів.
"""
import logging
import re
import uuid
from contextvars import ContextVar

HEADER_NAME = "X-Request-ID"

# Дозволені символи вхідного заголовка (захист від спотворення журналу)
_VALID_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


def resolve_request_id(incoming: str | None) -> str:
    """Повертає вхідний id, якщо він безпечний, інакше створює новий."""
    if incoming is not None and _VALID_ID.match(incoming.strip()):
        return incoming.strip()
    return uuid.uuid4().hex


class RequestIdFilter(logging.Filter):
    """Додає поточний request_id до кожного запису журналу."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def configure_logging() -> None:
    """Єдиний обробник журналу з request_id. Повторний виклик нічого не дублює."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    if any(getattr(h, "_fridgy_handler", False) for h in root.handlers):
        return

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(levelname)s:%(name)s:[%(request_id)s] %(message)s")
    )
    handler.addFilter(RequestIdFilter())
    handler._fridgy_handler = True  # позначка для перевірки повторного виклику
    root.addHandler(handler)
