import sys
import time
import tracemalloc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from procure_stat.domain.parsing import to_procurement  # type: ignore
from procure_stat.services.pipeline import (  # type: ignore
    PipelineStats,
    collect,
    deduplicate,
    parse_all,
)
from procure_stat.sources.json_file import read_rows_jsonl  # type: ignore

PATH = Path("data/large.jsonl")


def lazy() -> int:
    """Ледачий генераторний конвеєр (O(1) пам'яті)."""
    stats = PipelineStats()
    collect(deduplicate(parse_all(read_rows_jsonl(PATH), stats), stats), stats)
    return stats.kept


def greedy() -> int:
    """Жадібна обробка через матеріалізацію проміжних списків."""
    rows = list(read_rows_jsonl(PATH))  # Всі сирі JSON-рядки в RAM
    parsed = [to_procurement(r) for r in rows]
    valid = [p for p in parsed if p is not None]

    seen = set()
    unique = []
    for p in valid:
        key = (p.title, p.company)
        if key not in seen:
            seen.add(key)
            unique.append(p)

    return len(unique)


def main() -> None:
    if not PATH.exists():
        print(f"Помилка: Файл {PATH} не знайдено.")
        return

    print(f"{'Підхід':<25} {'Записів':<12} {'Час (с)':<10} {'Пікова пам\'ять (МБ)':<20}")
    print("-" * 70)

    for name, fn in (("генераторний конвеєр", lazy), ("проміжні списки", greedy)):
        tracemalloc.start()
        t0 = time.perf_counter()
        n = fn()
        elapsed = time.perf_counter() - t0
        peak = tracemalloc.get_traced_memory()[1] / 1024 / 1024
        tracemalloc.stop()

        print(f"{name:<25} {n:<12} {elapsed:<10.2f} {peak:<20.1f}")


if __name__ == "__main__":
    main()
