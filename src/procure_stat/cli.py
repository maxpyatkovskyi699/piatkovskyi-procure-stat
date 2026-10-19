import argparse
import logging
import time
import tracemalloc
from collections.abc import Callable
from pathlib import Path

from .config import Settings
from .errors import ProcureStatError
from .logging_setup import setup
from .services.pipeline import Pipeline, PipelineStats
from .services.ports import Source
from .sources.csv_file import CsvSource
from .sources.jsonl import JsonlSource

FACTORIES: dict[str, Callable[[Path], Source]] = {".jsonl": JsonlSource, ".csv": CsvSource}
logger = logging.getLogger(__name__)


def build_source(path: Path) -> Source:
    try:
        factory = FACTORIES[path.suffix.lower()]
    except KeyError:
        raise SystemExit(f"unsupported file type: {path.suffix}") from None
    return factory(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="procure-stat",
        description="Аналітична система моніторингу публічних закупівель Prozorro",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Шляхи до файлів з даними")
    parser.add_argument(
        "--stats",
        "-s",
        action="store_true",
        help="вивести детальну статистику обробки конвеєра",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="перекриває значення з .env і змінних середовища",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    settings = Settings()
    setup(args.log_level or settings.log_level)

    start_time = time.perf_counter()
    tracemalloc.start()

    try:
        sources = [build_source(p) for p in args.paths]
        pipeline = Pipeline(sources)
        stats: PipelineStats = pipeline.run()
    except ProcureStatError as exc:
        logger.error("%s", exc)
        raise SystemExit(1) from exc

    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed_seconds = time.perf_counter() - start_time
    peak_mb = peak_bytes / (1024 * 1024)

    print(f"Прочитано записів: {stats.read}")
    print(f"Відхилено: {stats.invalid}")
    print(f"Дублікатів: {stats.duplicates}")
    print(f"Залишилось: {stats.kept}")

    if hasattr(stats, "by_source") and stats.by_source:
        for name, count in stats.by_source.items():
            print(f"з {name}: {count}")

    if args.stats:
        if hasattr(stats, "amount_min") and stats.amount_min is not None:
            print(
                f"Сума закупівель (грн): min={stats.amount_min} "
                f"max={stats.amount_max} avg={stats.amount_avg:.0f}"
            )
        print(f"\nЧас: {elapsed_seconds:.2f} с, пік пам'яті: {peak_mb:.1f} МБ")


if __name__ == "__main__":
    main()
