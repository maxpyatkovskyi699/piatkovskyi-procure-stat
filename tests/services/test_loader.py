from collections.abc import Iterator
from typing import Any

from procure_stat.services.pipeline import Pipeline, PipelineStats

ROW = {
    "title": "Капітальний ремонт приміщення",
    "company": "АТ Укрзалізниця",
    "amount": "496530",
    "category": "Будівництво",
}


class FakeSource:
    def __init__(self, rows: list[dict[str, Any]], name: str = "mock") -> None:
        self.name = name
        self._rows = rows

    def read(self) -> Iterator[dict[str, Any]]:
        yield from self._rows


def test_multiple_sources_aggregation() -> None:
    """Перевіряє коректну агрегацію та розподіл записів з кількох різних джерел."""
    row1 = dict(ROW, title="Закупівля 1")
    row2 = dict(ROW, title="Закупівля 2")

    source1 = FakeSource([row1], "jsonl")
    source2 = FakeSource([row2], "csv")

    pipeline = Pipeline([source1, source2])
    stats: PipelineStats = pipeline.run()

    assert stats.read == 2
    assert stats.kept == 2
    assert stats.by_source["jsonl"] == 1
    assert stats.by_source["csv"] == 1


def test_financial_metrics_calculation() -> None:
    """Перевіряє правильність розрахунку мінімальної, максимальної та загальної суми."""
    row_cheap = dict(ROW, title="Закупівля А", amount="100")
    row_expensive = dict(ROW, title="Закупівля Б", amount="300")

    source = FakeSource([row_cheap, row_expensive])
    stats: PipelineStats = Pipeline([source]).run()

    assert stats.amount_min == 100
    assert stats.amount_max == 300
    assert stats.amount_sum == 400
    assert stats.amount_avg == 200.0


def test_categories_counter() -> None:
    """Перевіряє підрахунок кількості закупівель за категоріями."""
    row_it1 = dict(ROW, title="ІТ послуги 1", category="ІТ")
    row_build = dict(ROW, title="Будівництво 1", category="Будівництво")
    row_it2 = dict(ROW, title="ІТ послуги 2", category="ІТ")

    source = FakeSource([row_it1, row_build, row_it2])
    stats: PipelineStats = Pipeline([source]).run()

    assert stats.by_category["ІТ"] == 2
    assert stats.by_category["Будівництво"] == 1
