import argparse
import logging
import time
import tracemalloc
from collections.abc import Callable
from pathlib import Path

from .config import Settings
from .errors import ProcureStatError, UnsupportedFormatError
from .logging_setup import setup
from .services.pipeline import Pipeline, PipelineStats
from .services.ports import Source
from .sources.csv_file import CsvSource
from .sources.jsonl import JsonlSource
from .storage.db import make_engine, make_session_maker
from .storage.models import Base
from .storage.repository import SqlProcurementRepository

FACTORIES: dict[str, Callable[[Path], Source]] = {".jsonl": JsonlSource, ".csv": CsvSource}
logger = logging.getLogger(__name__)


def run_with_storage(sources: list[Source], db_path: Path) -> PipelineStats:
    """Створює схему, якщо її немає, і пише потік закупівель у базу."""
    engine = make_engine(db_path)
    Base.metadata.create_all(engine)

    # Створюємо фабрику сесій (sessionmaker)
    session_maker = make_session_maker(engine)

    # Відкриваємо сесію та запускаємо конвеєр у сховище
    with session_maker() as session:
        repository = SqlProcurementRepository(session)
        return Pipeline(sources).run_into(repository)


def build_source(path: Path) -> Source:
    try:
        factory = FACTORIES[path.suffix.lower()]
    except KeyError:
        raise UnsupportedFormatError(path.suffix) from None
    return factory(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="procure-stat",
        description="Аналітична система моніторингу публічних закупівель Prozorro",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Шляхи до файлів з даними")
    parser.add_argument(
        "--db",
        type=Path,
        default=None,
        help="Шлях до файлу SQLite бази даних (якщо вказано, дані зберігаються у БД)",
    )
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
        if args.db:
            stats = run_with_storage(sources, args.db)
        else:
            pipeline = Pipeline(sources)
            stats = pipeline.run()
    except ProcureStatError as exc:
        logger.error("%s", exc)
        raise SystemExit(1) from exc

    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    elapsed_seconds = time.perf_counter() - start_time
    peak_mb = peak_bytes / (1024 * 1024)

    if args.db:
        print(f"Збережено у базу даних: {args.db}")

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
