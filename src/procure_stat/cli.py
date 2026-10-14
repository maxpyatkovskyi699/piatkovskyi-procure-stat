import argparse
import time
import tracemalloc
from collections.abc import Callable
from pathlib import Path

from .services.pipeline import Pipeline, PipelineStats
from .services.ports import Source
from .sources.jsonl import JsonlSource
from .sources.csv_file import CsvSource

FACTORIES: dict[str, Callable[[Path], Source]] = {".jsonl": JsonlSource, ".csv": CsvSource}


def build_source(path: Path) -> Source:
    try:
        factory = FACTORIES[path.suffix.lower()]
    except KeyError:
        raise SystemExit(f"unsupported file type: {path.suffix}") from None
    return factory(path)


def main(argv: list[str] | None = None) -> None:
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
    args = parser.parse_args(argv)

    start_time = time.perf_counter()
    tracemalloc.start()

    # Створюємо джерело даних та запускаємо пайплайн
    source = build_source(args.path)
    pipeline = Pipeline([source])

    # Якщо Pipeline.run() повертає об'єкт зі статистикою та самі дані (або сутності)
    stats: PipelineStats = pipeline.run()

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

        if hasattr(stats, "by_source") and stats.by_source:
            print("\nРозподіл за джерелами:")
            for name, count in stats.by_source.items():
                print(f"  {name}: {count}")

        print(f"\nЧас: {elapsed_seconds:.2f} с, пік пам'яті: {peak_mb:.1f} МБ")
    else:
        print(f"Залишилось записів: {stats.kept}")


if __name__ == "__main__":
    main()
