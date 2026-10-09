import sys
import time
import tracemalloc
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from procure_stat.services.pipeline import (
    PipelineStats,
    collect,
    deduplicate,
    parse_all,
)
from procure_stat.sources.json_file import read_rows_jsonl

PATH = Path("data/large.jsonl")


def lazy() -> int:
    """Ледачий генераторний конвеєр (потокова обробка)."""
    stats = PipelineStats()
    collect(deduplicate(parse_all(read_rows_jsonl(PATH), stats), stats), stats)
    return stats.kept


def greedy() -> int:
    """Жадібна обробка через матеріалізацію (list) НА КОЖНОМУ ЕТАПІ того самого конвеєра."""
    stats = PipelineStats()

    # Використовуємо ті самі функції, але з матеріалізацією проміжних результатів у RAM
    rows = list(read_rows_jsonl(PATH))
    parsed = list(parse_all(rows, stats))
    unique = list(deduplicate(parsed, stats))
    collect(unique, stats)

    return stats.kept


def main() -> None:
    if not PATH.exists():
        print(f"Помилка: Файл {PATH} не знайдено.")
        return

    print(f"{'Підхід':<25} {'Записів':<12} {'Час (с)':<10} {"Пікова пам'ять (МБ)":<20}")
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
