from collections.abc import Iterator, Iterable
from typing import Any, Protocol

from procure_stat.domain.models import Procurement


class Source(Protocol):
    """Будь-що, що віддає сирі записи для конвеєра."""

    name: str

    def read(self) -> Iterator[dict[str, Any]]: ...


class ProcurementRepository(Protocol):
    def add_many(self, procurements: Iterable[Procurement]) -> int:
        """Записує пачками; повторний запуск не створює дублікатів."""
        ...

    def count(self) -> int:
        """Повертає загальну кількість записів."""
        ...

    def by_city(self, city: str) -> list[Procurement]:
        """Повертає закупівлі за конкретним містом/регіоном."""
        ...

    def top_cities(self, limit: int = 5) -> list[tuple[str, int]]:
        """Повертає топ міст за кількістю закупівель."""
        ...

    def average_amount(self) -> float:
        """Повертає середню суму закупівлі."""
        ...
