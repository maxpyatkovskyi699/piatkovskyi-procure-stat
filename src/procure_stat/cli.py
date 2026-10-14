import argparse
import time
import tracemalloc
from pathlib import Path

from procure_stat.sources.jsonl import read_rows, read_rows_jsonl
from procure_stat.services.pipeline import process_pipeline, PipelineStats, count_by_category
from procure_stat.domain.models import Procurement


def load_procurements_orchestrator(
    path: Path, stats: PipelineStats | None = None
) -> list[Procurement]:
    """Визначає формат файлу, читає його та передає дані у конвеєр."""
    path = Path(path)
    active_stats = stats if stats is not None else PipelineStats()

    if path.suffix.lower() == ".jsonl":
        rows = read_rows_jsonl(path)
    else:
        rows = read_rows(path)

    return process_pipeline(rows, active_stats)


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

    start_time = time.perf_counter()
    tracemalloc.start()

    stats = PipelineStats()
    procurements = load_procurements_orchestrator(args.path, stats)

    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed_seconds = time.perf_counter() - start_time
    peak_mb = peak_bytes / (1024 * 1024)

    if args.stats:
        print(f"Прочитано записів: {stats.read}")
        print(f"Відхилено: {stats.invalid}")
        print(f"Дублікатів: {stats.duplicates}")
        print(f"Залишилось: {stats.kept}")

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
