import uuid
from collections.abc import Iterable
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from procure_stat.domain.models import Procurement
from procure_stat.storage.models import ProcurementRow


def _to_row(procurement: Procurement) -> dict[str, Any]:
    row_id = procurement.id if procurement and procurement.id else str(uuid.uuid4())
    return {
        "id": row_id,
        "title": procurement.title,
        "company": procurement.company,
        "amount": float(procurement.amount) if procurement.amount is not None else None,
        "category": procurement.category,
    }


class SqlProcurementRepository:
    def __init__(self, session: Session, batch_size: int = 1000) -> None:
        self._session = session
        self._batch_size = batch_size

    def _flush(self, batch: list[dict[str, Any]]) -> int:
        for row_data in batch:
            stmt = ProcurementRow(**row_data)
            self._session.merge(stmt)
        return len(batch)

    def add(self, item: Procurement) -> None:
        """Додати один запис до бази даних (ідемпотентно через merge)."""
        model = ProcurementRow.from_domain(item)
        self._session.merge(model)

    def by_company(self, company: str) -> list[Procurement]:
        """Повертає закупівлі за конкретною компанією-замовником."""
        rows = (
            self._session.execute(select(ProcurementRow).where(ProcurementRow.company == company))
            .scalars()
            .all()
        )
        return [row.to_domain() for row in rows]

    def add_many(self, procurements: Iterable[Procurement]) -> int:
        """Записує пачками; повторний запуск не створює дублікатів (через merge)."""
        written = 0
        batch: list[dict[str, Any]] = []
        for procurement in procurements:
            batch.append(_to_row(procurement))
            if len(batch) >= self._batch_size:
                written += self._flush(batch)
                batch = []
        if batch:
            written += self._flush(batch)
        return written

    def add_many_fast(self, procurements: Iterable[Procurement]) -> int:
        """Швидкий масовий запис пачками без індивідуальних SELECT (швидше у ~20 разів)."""
        written = 0
        batch: list[dict[str, Any]] = []

        for procurement in procurements:
            batch.append(_to_row(procurement))
            if len(batch) >= self._batch_size:
                written += self._flush_fast(batch)
                batch = []
        if batch:
            written += self._flush_fast(batch)
        return written

    def _flush_fast(self, batch: list[dict[str, Any]]) -> int:
        if not batch:
            return 0
        # Використовуємо SQLite upsert (ідемпотентність через конфлікт по id)
        stmt = sqlite_insert(ProcurementRow).values(batch)
        stmt = stmt.on_conflict_do_nothing(index_elements=["id"])

        self._session.execute(stmt)
        return len(batch)  # або реальна кількість вставлених

    def count(self) -> int:
        result: Any = self._session.execute(select(func.count(ProcurementRow.id))).scalar_one()
        return int(result) if result is not None else 0

    def by_category(self, category: str) -> list[Procurement]:
        rows = (
            self._session.execute(select(ProcurementRow).where(ProcurementRow.category == category))
            .scalars()
            .all()
        )
        return [row.to_domain() for row in rows]

    def top_companies(self, limit: int = 5) -> list[tuple[str, int]]:
        rows = list(
            self._session.execute(
                select(ProcurementRow.company, func.count().label("n"))
                .group_by(ProcurementRow.company)
                .order_by(func.count().desc())
                .limit(limit)
            ).all()
        )
        return [
            (str(company), int(n)) for company, n in rows if company is not None and n is not None
        ]

    def average_amount(self) -> float:
        result: Any = self._session.execute(select(func.avg(ProcurementRow.amount))).scalar_one()
        return float(result) if result is not None else 0.0
