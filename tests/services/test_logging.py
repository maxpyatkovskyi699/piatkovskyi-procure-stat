import logging
from pathlib import Path

import pytest

from procure_stat.config import mask
from procure_stat.errors import SourceError
from procure_stat.services.pipeline import Pipeline
from procure_stat.sources.jsonl import JsonlSource
from tests.services.test_pipeline import ROW, FakeSource


def test_invalid_rows_are_logged_as_warning(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    Pipeline([FakeSource([ROW, {"title": "", "company": "B"}])]).run()
    assert "skipped 1 invalid rows" in caplog.text


def test_missing_file_raises_source_error() -> None:
    with pytest.raises(SourceError, match="cannot open"):
        list(JsonlSource(Path("data/no-such.jsonl")).read())


def test_source_error_keeps_original_cause() -> None:
    try:
        list(JsonlSource(Path("data/no-such.jsonl")).read())
    except SourceError as exc:
        assert isinstance(exc.__cause__, FileNotFoundError)
    else:
        raise AssertionError("SourceError not raised")


def test_secret_is_masked() -> None:
    assert mask("super-secret-token-4417") == "*******************4417"
    assert mask("abc") == "****"
