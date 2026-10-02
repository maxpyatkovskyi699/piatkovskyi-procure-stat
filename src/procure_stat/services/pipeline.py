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


# Агрегація та збір аналітики
def collect_stats(items: Iterable[Procurement], stats: PipelineStats) -> Iterator[Procurement]:
    """Підраховує категорії та фінансові метрики для збережених тендерів."""
    for procurement in items:
        stats.kept += 1

        if procurement.category:
            stats.by_category[procurement.category] += 1

        if procurement.amount is not None:
            stats.amount_count += 1
            stats.amount_sum += procurement.amount

            if stats.amount_min is None or procurement.amount < stats.amount_min:
                stats.amount_min = procurement.amount
            if stats.amount_max is None or procurement.amount > stats.amount_max:
                stats.amount_max = procurement.amount

        yield procurement


# Головний конвеєр (збір усіх даних)
def process_pipeline(path: Path) -> tuple[list[Procurement], PipelineStats]:
    """Збирає всі генератори в єдиний конвеєр обробки."""
    stats = PipelineStats()

    # Порядкове зчитування файлу
    raw_rows = read_rows_jsonl(path)

    # Послідовний запуск етапів конвеєра
    parsed = parse_all(raw_rows, stats)
    unique = deduplicate(parsed, stats)
    analyzed = collect_stats(unique, stats)

    # Матеріалізація (виконання всього конвеєра та збереження результату)
    valid_items = list(analyzed)

    return valid_items, stats
