import logging
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from itertools import islice
from typing import Any, TypeVar

from pydantic import ValidationError

from ..domain.models import Procurement
from .ports import Source
from .schemas import ProcurementIn

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass(slots=True)
class PipelineStats:
    read: int = 0
    invalid: int = 0
    duplicates: int = 0
    kept: int = 0
    by_source: Counter[str] = field(default_factory=Counter)
    by_category: Counter[str] = field(default_factory=Counter)

    # Фінансова статистика сум закупівель
    amount_sum: int = 0
    amount_min: int | None = None
    amount_max: int | None = None
    amount_avg: float = 0.0

    @property
    def valid(self) -> int:
        return self.read - self.invalid


class Pipeline:
    def __init__(self, sources: list[Source]) -> None:
        self._sources = sources

    def run(self) -> PipelineStats:
        """Головний сценарій запуску конвеєра для всіх джерел з потоковою обробкою."""
        stats = PipelineStats()
        seen: set[str] = set()

        # Обробляємо кожне джерело по черзі
        for source in self._sources:
            parsed_items = self._parse_all(source.read(), stats)

            # Фільтруємо дублікати та рахуємо статистику «на льоту» без списків у пам'яті
            for procurement in self._deduplicate(parsed_items, stats, seen):
                stats.kept += 1
                source_name = getattr(source, "name", source.__class__.__name__)
                stats.by_source[source_name] += 1

                # Оновлюємо фінансові метрики та категорії для кожної закупівлі
                self._process_one(procurement, stats)

        # Розраховуємо середнє значення після завершення потоку
        if stats.kept > 0 and stats.amount_sum > 0:
            stats.amount_avg = stats.amount_sum / stats.kept

        return stats

    @staticmethod
    def _parse_all(
        rows: Iterable[dict[str, Any]],
        stats: PipelineStats,
    ) -> Iterator[Procurement]:
        """Парсить сирі словники у доменні об'єкти Procurement."""
        for row in rows:
            stats.read += 1
            try:
                yield ProcurementIn.model_validate(row).to_domain()
            except ValidationError as exc:
                stats.invalid += 1
                logger.debug("skip row: %s errors", exc.error_count())
                continue

    @staticmethod
    def _deduplicate(
        items: Iterable[Procurement],
        stats: PipelineStats,
        seen: set[str],
    ) -> Iterator[Procurement]:
        """Видаляє дублікати закупівель та фіксує їх у статистиці."""
        for procurement in items:
            if procurement.key in seen:
                stats.duplicates += 1
                continue
            seen.add(procurement.key)
            yield procurement

    @staticmethod
    def _process_one(procurement: Procurement, stats: PipelineStats) -> None:
        """Оновлює статистику за категоріями та фінансовими показниками для однієї закупівлі."""
        if procurement.category:
            stats.by_category[procurement.category] += 1

        if procurement.amount is not None:
            stats.amount_min = (
                procurement.amount
                if stats.amount_min is None
                else min(stats.amount_min, procurement.amount)
            )
            stats.amount_max = (
                procurement.amount
                if stats.amount_max is None
                else max(stats.amount_max, procurement.amount)
            )
            stats.amount_sum += procurement.amount


def batched(iterable: Iterable[T], n: int) -> Iterator[tuple[T, ...]]:  # noqa: UP047
    """Розбиває ітератор на батчі фіксованого розміру."""
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch
