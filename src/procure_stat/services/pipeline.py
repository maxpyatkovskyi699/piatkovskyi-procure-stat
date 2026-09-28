from collections import Counter
from collections.abc import Iterable, Iterator
from pathlib import Path

from ..domain.models import Procurement
from ..domain.parsing import to_procurement
from ..sources.json_file import read_rows


def deduplicate(items: Iterable[Procurement]) -> Iterator[Procurement]:
    seen: set[tuple[str, str]] = set()
    for procurement in items:
        key = (procurement.title, procurement.company)
        if key not in seen:
            seen.add(key)
            yield procurement


def count_by_category(items: Iterable[Procurement]) -> Counter[str]:
    return Counter(procurement.category for procurement in items)


def load_procurements(path: Path) -> list[Procurement]:
    """Сценарій завантаження та обробки закупівель.

    Усі проміжні етапи виконуються «ледаче» (через генератори).
    Дані матеріалізуються в пам'ять лише під час виклику list().
    """
    rows = read_rows(path)
    parsed = (to_procurement(row) for row in rows)
    valid = (p for p in parsed if p is not None)
    return list(deduplicate(valid))
