from collections import Counter
from collections.abc import Iterable, Iterator

from ..domain.models import Procurement


def deduplicate(items: Iterable[Procurement]) -> Iterator[Procurement]:
    seen: set[tuple[str, str]] = set()
    for procurement in items:
        key = (procurement.title, procurement.company)
        if key not in seen:
            seen.add(key)
            yield procurement


def count_by_category(items: Iterable[Procurement]) -> Counter[str]:
    return Counter(procurement.category for procurement in items)
