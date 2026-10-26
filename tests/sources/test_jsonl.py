import logging
from pathlib import Path

import pytest

from procure_stat.sources.jsonl import JsonlSource


def test_jsonl_source_success(tmp_path: Path) -> None:
    # Перевіряємо успішне читання та ігнорування порожніх рядків
    file_path = tmp_path / "something.jsonl"
    file_path.write_text('{"id": "1"}\n\n{"id": "2"}\n', encoding="utf-8")

    source = JsonlSource(file_path)
    rows = list(source.read())
    assert len(rows) == 2
    assert rows[0]["id"] == "1"
    assert rows[1]["id"] == "2"


def test_malformed_line_is_skipped_and_logged(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Перевіряє, що битий рядок у JSONL пропускається, логується, а валідні дані зчитуються."""
    path = tmp_path / "broken.jsonl"
    path.write_text('{"title": "Ремонт"}\n{not json}\n{"title": "Будівництво"}\n', encoding="utf-8")

    caplog.set_level(logging.DEBUG, logger="procure_stat.sources.jsonl")
    rows = list(JsonlSource(path).read())

    assert len(rows) == 2
    assert "skip malformed line 2" in caplog.text
