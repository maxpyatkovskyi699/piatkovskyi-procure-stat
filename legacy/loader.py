import json
from os import PathLike
from dataclasses import dataclass
from collections import Counter
from typing import Iterator, Iterable, Any


@dataclass(frozen=True)
class Procurement:
    title: str
    company: str
    amount: int
    category: str

    def to_list(self) -> list[Any]:
        return [self.title, self.company, self.amount, self.category]


def _normalize_title(raw_title: str | None) -> str | None:
    if not raw_title:
        return None
    normalized = " ".join(raw_title.strip().lower().split())
    return normalized if normalized else None


def _parse_amount(raw_amount: Any) -> int:
    try:
        return int(raw_amount)
    except (ValueError, TypeError):
        return 0


def read_procurements(file_path: str | PathLike) -> Iterator[dict[str, Any]]:
    """Ледаче читання записів із JSON-файлу Prozorro."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        yield from data


def transform_procurements(raw_items: Iterable[dict[str, Any]]) -> Iterator[Procurement]:
    """Генераторний конвеєр для нормалізації та очищення даних."""
    for item in raw_items:
        title = _normalize_title(item.get("title"))
        if not title:
            continue

        yield Procurement(
            title=title,
            company=item.get("company", ""),
            amount=_parse_amount(item.get("salary")),
            category=item.get("city", ""),
        )


def deduplicate_procurements(items: Iterable[Procurement]) -> list[Procurement]:
    """Дедуплікація за O(N) за допомогою set."""
    seen: set[tuple[str, str]] = set()
    unique_items: list[Procurement] = []

    for item in items:
        key = (item.title, item.company)
        if key not in seen:
            seen.add(key)
            unique_items.append(item)

    return unique_items


def count_by_category(items: Iterable[Procurement]) -> Counter[str]:
    """Підраховує кількість закупівель за категоріями."""
    return Counter(item.category for item in items)


def process_procurements(file_path: str | PathLike) -> list[list[Any]]:
    """Головна функція-конвеєр."""
    raw_data = read_procurements(file_path)
    cleaned_data = transform_procurements(raw_data)
    unique_data = deduplicate_procurements(cleaned_data)

    stats = count_by_category(unique_data)
    print(dict(stats))  # Розподіл закупівель за категоріями

    return [item.to_list() for item in unique_data]


if __name__ == "__main__":
    process_procurements("data/prozorro.json")
