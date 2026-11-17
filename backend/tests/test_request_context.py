"""Тести request_id без FastAPI: допоміжні функції та фільтр журналу."""
import logging
import re

import pytest

from fridgy.core.request_context import (
    RequestIdFilter,
    configure_logging,
    request_id_var,
    resolve_request_id,
)

GENERATED = re.compile(r"^[0-9a-f]{32}$")


def test_valid_incoming_id_is_kept():
    assert resolve_request_id("abc-123_X.9") == "abc-123_X.9"


@pytest.mark.parametrize(
    "incoming",
    [None, "", "has spaces", "x" * 65, "new\nline", "<script>"],
)
def test_missing_or_unsafe_id_is_replaced_with_generated_one(incoming):
    result = resolve_request_id(incoming)

    assert GENERATED.match(result)


def test_generated_ids_are_unique():
    assert resolve_request_id(None) != resolve_request_id(None)


def test_filter_adds_current_request_id_to_log_records():
    token = request_id_var.set("req-42")
    try:
        record = logging.LogRecord("t", logging.INFO, "f", 1, "msg", None, None)

        assert RequestIdFilter().filter(record) is True
        assert record.request_id == "req-42"
    finally:
        request_id_var.reset(token)


def test_filter_uses_dash_when_no_request_is_active():
    record = logging.LogRecord("t", logging.INFO, "f", 1, "msg", None, None)

    RequestIdFilter().filter(record)

    assert record.request_id == "-"


def test_configure_logging_is_idempotent():
    root = logging.getLogger()
    before = list(root.handlers)

    configure_logging()
    configure_logging()

    added = [h for h in root.handlers if h not in before]
    try:
        assert len(added) <= 1
    finally:
        for handler in added:
            root.removeHandler(handler)
