from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from itertools import islice

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


# Парсинг сирих рядків у об'єкти Procurement
def parse_all(rows: Iterable[dict], stats: PipelineStats) -> Iterator[Procurement]:
    """Парсить сирі словники з JSON, оновлюючи лічильники read та invalid."""
    for row in rows:
        stats.read += 1
        procurement = to_procurement(row)
        if procurement is None:
            stats.invalid += 1
            continue
        yield procurement


# Видалення дублікатів
def deduplicate(items: Iterable[Procurement], stats: PipelineStats) -> Iterator[Procurement]:
    """Фільтрує дублікати за допомогою ключів (title, company), фіксуючи їх у stats."""
    seen: set[tuple[str, str]] = set()
    for procurement in items:
        # У множину зберігаємо лише легкий кортеж-ключ, а не весь об'єкт
        key = (procurement.title, procurement.company)
        if key in seen:
            stats.duplicates += 1
            continue
        seen.add(key)
        yield procurement


# Агрегація та збір аналітики (споживає конвеєр)
def collect(items: Iterable[Procurement], stats: PipelineStats) -> None:
    """Підраховує категорії та фінансові метрики, споживаючи увесь потік."""
    for procurement in items:
        stats.kept += 1

        if procurement.category:
            stats.by_category[procurement.category] += 1

        amount = procurement.amount
        if amount is None:
            continue

        stats.amount_count += 1
        stats.amount_sum += amount

        if stats.amount_min is None or amount < stats.amount_min:
            stats.amount_min = amount
        if stats.amount_max is None or amount > stats.amount_max:
            stats.amount_max = amount


# Головний конвеєр (обробка за один прохід без завантаження списку в RAM)
def process_pipeline(path: Path) -> PipelineStats:
    """Збирає всі генератори та споживає потік даних за один прохід."""
    stats = PipelineStats()

    raw_rows = read_rows_jsonl(path)
    parsed = parse_all(raw_rows, stats)
    unique = deduplicate(parsed, stats)

    # Проганяє всі дані через генератори та заповнює stats
    collect(unique, stats)

    return stats


def batched(items: Iterable[Procurement], size: int) -> Iterator[tuple[Procurement, ...]]:
    """Розбиває потік елементів на пачки (пакети) заданого розміру."""
    iterator = iter(items)
    while batch := tuple(islice(iterator, size)):  # := замінює if not batch: break
        yield batch
