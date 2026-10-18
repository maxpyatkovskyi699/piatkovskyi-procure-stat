from collections.abc import Iterator
from typing import Any

from procure_stat.services.pipeline import Pipeline, PipelineStats


class FakeSource:
    def __init__(self, rows: list[dict[str, Any]], name: str = "empty") -> None:
        self.name = name
        self._rows = rows

    def read(self) -> Iterator[dict[str, Any]]:
        yield from self._rows


def test_empty_source_pipeline() -> None:
    """Перевіряє поведінку пайплайну з порожнім джерелом даних."""
    source = FakeSource([])
    pipeline = Pipeline([source])
    stats: PipelineStats = pipeline.run()

    assert stats.read == 0
    assert stats.invalid == 0
    assert stats.duplicates == 0
    assert stats.kept == 0
    assert stats.by_source["empty"] == 0
