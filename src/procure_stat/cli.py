import argparse
from pathlib import Path

from .services.pipeline import count_by_category, load_procurements


def main() -> None:
    parser = argparse.ArgumentParser(prog="procure-stat")
    parser.add_argument("path", type=Path, help="файл із даними закупівель")
    args = parser.parse_args()

    procurements = load_procurements(args.path)

    print(f"Завантажено записів: {len(procurements)}")
    for category, count in count_by_category(procurements).most_common():
        print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
