import logging
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from itertools import islice
from pathlib import Path
from typing import Any
from typing import TypeVar

from pydantic import ValidationError

from ..domain.models import Procurement
from ..sources.json_file import read_rows
from ..sources.schemas import ProcurementIn

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass(slots=True)
class PipelineStats:
    read: int = 0
    invalid: int = 0
    duplicates: int = 0
    kept: int = 0
    by_category: Counter[str] = field(default_factory=Counter)

    # Статистика сум закупівель для тестів
    amount_sum: int = 0
    amount_min: int | None = None
    amount_max: int | None = None
    amount_avg: float = 0.0

    @property
    def valid(self) -> int:
        return self.read - self.invalid


def parse_all(
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


def deduplicate(
    items: Iterable[Procurement],
    stats: PipelineStats,
) -> Iterator[Procurement]:
    """Видаляє дублікати закупівель та фіксує їх у статистиці."""
    seen: set[str] = set()
    for procurement in items:
        if procurement.key in seen:
            stats.duplicates += 1
            continue
        seen.add(procurement.key)
        yield procurement


def count_by_category(items: Iterable[Procurement]) -> Counter[str]:
    """Підраховує кількість закупівель за категоріями."""
    return Counter(procurement.category for procurement in items)


def batched(iterable: Iterable[T], n: int) -> Iterator[tuple[T, ...]]:
    """Розбиває ітератор на батчі фіксованого розміру."""
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def collect(items: Iterable[Procurement], stats: PipelineStats) -> list[Procurement]:
    """Агрегує список закупівель та розраховує фінансову статистику."""
    result = list(items)
    stats.kept = len(result)
    stats.by_category = count_by_category(result)

    amounts = [p.amount for p in result if p.amount is not None]
    if amounts:
        stats.amount_sum = sum(amounts)
        stats.amount_min = min(amounts)
        stats.amount_max = max(amounts)
        stats.amount_avg = stats.amount_sum / len(amounts)

    return result


def process_pipeline(rows: Iterable[dict[str, Any]], stats: PipelineStats) -> list[Procurement]:
    """Повний конвеєр обробки сирих даних."""
    parsed = parse_all(rows, stats)
    deduped = deduplicate(parsed, stats)
    return collect(deduped, stats)


def load_procurements(path: Path, stats: PipelineStats | None = None) -> list[Procurement]:
    """Головний сценарій завантаження, валідації та дедуплікації."""
    if stats is None:
        stats = PipelineStats()

    rows = read_rows(path)
    return process_pipeline(rows, stats)
