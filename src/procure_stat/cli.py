import argparse
from itertools import islice
from pathlib import Path

from .services.pipeline import (
    PipelineStats,
    deduplicate,
    parse_all,
    process_pipeline,
)
from .sources.json_file import read_rows_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="procure-stat", description="ProcureStat Data Pipeline CLI"
    )
    parser.add_argument("path", type=Path, help="файл із даними закупівель")
    parser.add_argument(
        "--preview",
        type=int,
        metavar="N",
        help="Показати перші N записів без повної обробки датасету",
    )
    args = parser.parse_args()

    # Прев'ю перших N записів (Ледаче виконання)
    if args.preview:
        stats = PipelineStats()
        raw_rows = read_rows_jsonl(args.path)
        parsed = parse_all(raw_rows, stats)
        pipeline = deduplicate(parsed, stats)

        for procurement in islice(pipeline, args.preview):
            print(procurement)

        # Перевірка ледачості: зчитано має бути лише кілька рядків (5-10), а не увесь файл
        print(f"\n[DEBUG] Зчитано рядків з файлу для прев'ю: {stats.read}")
        return

    # Повний розрахунок статистики конвеєра
    stats = process_pipeline(args.path)

    print(f"Прочитано рядків: {stats.read}")
    print(f"Невалідних: {stats.invalid}")
    print(f"Дублікатів: {stats.duplicates}")
    print(f"Збережено записів: {stats.kept}")

    if stats.amount_count:
        print(f"Середня сума: {stats.amount_avg:.2f}")
        print(f"Мінімальна сума: {stats.amount_min}")
        print(f"Максимальна сума: {stats.amount_max}")

    print("\nКатегорії:")
    for category, count in stats.by_category.most_common():
        print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
