from collections.abc import Iterable, Iterator
from typing import Any, Protocol

from procure_stat.domain.models import Procurement


class Source(Protocol):
    """Будь-що, що віддає сирі записи для конвеєра."""

    name: str

    def read(self) -> Iterator[dict[str, Any]]: ...


class ProcurementRepository(Protocol):
    def add(self, item: Procurement) -> None: ...

    def add_many(self, procurements: Iterable[Procurement]) -> int:
        """Записує пачками; повторний запуск не створює дублікатів."""
        ...

    def count(self) -> int:
        """Повертає загальну кількість записів."""
        ...

    def by_company(self, company: str) -> list[Procurement]:
        """Повертає закупівлі за конкретною компанією-замовником."""
        ...

    def top_companies(self, limit: int = 5) -> list[tuple[str, int]]:
        """Повертає топ компаній за кількістю закупівель."""
        ...

    def average_amount(self) -> float:
        """Повертає середню суму закупівлі."""
        ...
