from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from ..domain.models import Procurement
from ..domain.parsing import to_procurement
from ..sources.json_file import read_rows_jsonl


@dataclass(slots=True)
class PipelineStats:
    read: int = 0
    invalid: int = 0
    duplicates: int = 0
    kept: int = 0
    by_category: Counter[str] = field(default_factory=Counter)
    amount_count: int = 0
    amount_sum: int = 0
    amount_min: int | None = None
    amount_max: int | None = None

    @property
    def amount_avg(self) -> float | None:
        if not self.amount_count:
            return None
        return self.amount_sum / self.amount_count


def deduplicate(items: Iterable[Procurement]) -> Iterator[Procurement]:
    seen: set[tuple[str, str]] = set()
    for procurement in items:
        key = (procurement.title, procurement.company)
        if key not in seen:
            seen.add(key)
            yield procurement


def count_by_category(items: Iterable[Procurement]) -> Counter[str]:
    return Counter(procurement.category for procurement in items)


def process_pipeline(path: Path) -> tuple[list[Procurement], PipelineStats]:
    """Проганяє дані через конвеєр та підраховує статистику PipelineStats."""
    stats = PipelineStats()
    valid_items: list[Procurement] = []
    seen: set[tuple[str, str]] = set()

    for row in read_rows_jsonl(path):
        stats.read += 1

        procurement = to_procurement(row)
        if procurement is None:
            stats.invalid += 1
            continue

        key = (procurement.title, procurement.company)
        if key in seen:
            stats.duplicates += 1
            continue

        seen.add(key)
        stats.kept += 1
        valid_items.append(procurement)

        # Збір статистики по категоріях
        if procurement.category:
            stats.by_category[procurement.category] += 1

        # Збір статистики по сумах тендерів (якщо сума вказана числом)
        if procurement.amount is not None:
            stats.amount_count += 1
            stats.amount_sum += procurement.amount

            if stats.amount_min is None or procurement.amount < stats.amount_min:
                stats.amount_min = procurement.amount
            if stats.amount_max is None or procurement.amount > stats.amount_max:
                stats.amount_max = procurement.amount

    return valid_items, stats
