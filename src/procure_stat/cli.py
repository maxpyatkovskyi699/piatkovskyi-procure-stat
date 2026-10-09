import argparse
import time
import tracemalloc
from pathlib import Path

from procure_stat.services.pipeline import PipelineStats

from .services.pipeline import count_by_category, load_procurements


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="procure-stat",
        description="Аналітична система моніторингу публічних закупівель Prozorro",
    )
    parser.add_argument("path", type=Path, help="файл із даними закупівель")
    parser.add_argument(
        "--stats",
        "-s",
        action="store_true",
        help="вивести детальну статистику обробки конвеєра",
    )
    args = parser.parse_args()

    # Запускаємо заміри часу та пам'яті
    start_time = time.perf_counter()
    tracemalloc.start()

    stats = PipelineStats()
    procurements = load_procurements(args.path, stats)

    # Фіксуємо показники
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed_seconds = time.perf_counter() - start_time
    peak_mb = peak_bytes / (1024 * 1024)

    if args.stats:
        print(f"Прочитано записів: {stats.read}")
        print(f"Відхилено: {stats.invalid}")
        print(f"Дублікатів: {stats.duplicates}")
        print(f"Залишилось: {stats.kept}")

        # Статистика за сумами (якщо розраховується в stats)
        if hasattr(stats, "amount_min") and stats.amount_min is not None:
            print(
                f"Сума закупівель (грн): min={stats.amount_min} "
                f"max={stats.amount_max} avg={stats.amount_avg:.0f}"
            )

        print("\nРозподіл за категоріями:")
        for category, count in count_by_category(procurements).most_common():
            print(f"  {category}: {count}")

        print(f"\nЧас: {elapsed_seconds:.2f} с, пік пам'яті: {peak_mb:.1f} МБ")
    else:
        print(f"Завантажено записів: {len(procurements)}")


if __name__ == "__main__":
    main()
