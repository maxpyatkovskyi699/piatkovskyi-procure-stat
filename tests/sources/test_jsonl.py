import logging
from pathlib import Path

import pytest

from procure_stat.sources.jsonl import JsonlSource


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
