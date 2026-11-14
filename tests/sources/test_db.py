from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from procure_stat.domain.models import Procurement
from procure_stat.storage.db import make_engine, make_session_maker, session_scope
from procure_stat.storage.models import Base
from procure_stat.storage.repository import SqlProcurementRepository


def test_empty_repository(session: Session) -> None:
    """Перевірка щойно створеного сховища: порожньо, нуль записів."""
    repo = SqlProcurementRepository(session)
    assert repo.count() == 0
    assert repo.average_amount() == 0.0
    assert repo.top_companies() == []


def test_add_and_idempotency(session: Session) -> None:
    """Запис закупівель та повторний запис (ідемпотентність: нуль нових рядків)."""
    repo = SqlProcurementRepository(session)

    item = Procurement(
        id="proc-1",
        title="Закупівля паперу",
        company="ТОВ Офіс-Сервіс",
        amount=1500.0,
        category="Канцтовари",
    )

    # Перший запис
    written_first = repo.add_many([item])
    assert written_first == 1
    assert repo.count() == 1

    # Повторний запис того ж елемента (через merge у репозиторії)
    written_second = repo.add_many([item])
    assert written_second == 1
    assert repo.count() == 1  # генерація нових рядків не відбулась, оскільки ID співпав


def test_duplicate_within_same_batch(session: Session) -> None:
    """Дублікат ідентифікатора всередині однієї пачки."""
    repo = SqlProcurementRepository(session)

    items = [
        Procurement(id="proc-1", title="Перший", company="А", amount=100.0, category="Х"),
        Procurement(id="proc-1", title="Дубль", company="А", amount=100.0, category="Х"),
    ]

    repo.add_many(items)
    # Метод merge обробить їх послідовно в межах однієї транзакції без падіння
    assert repo.count() == 1


def test_same_title_different_company(session: Session) -> None:
    """Однакова назва закупівлі в іншій компанії – це окремі унікальні записи."""
    repo = SqlProcurementRepository(session)

    items = [
        Procurement(
            id="proc-1",
            title="Ремонт доріг",
            company="Компанія А",
            amount=50000.0,
            category="Будівництво",
        ),
        Procurement(
            id="proc-2",
            title="Ремонт доріг",
            company="Компанія Б",
            amount=70000.0,
            category="Будівництво",
        ),
    ]

    repo.add_many(items)
    assert repo.count() == 2


def test_aggregates_with_null_amounts(session: Session) -> None:
    """Середня сума з урахуванням можливих NULL (None) значень."""
    repo = SqlProcurementRepository(session)

    items = [
        Procurement(id="proc-1", title="А", company="Компанія А", amount=100.0, category="Х"),
        Procurement(
            id="proc-2", title="Б", company="Компанія Б", amount=None, category="Х"
        ),  # amount як None
        Procurement(id="proc-3", title="В", company="Компанія А", amount=300.0, category="Х"),
    ]

    repo.add_many(items)
    assert repo.count() == 3
    # Середнє вираховується лише з тих, де amount не NULL: (100 + 300) / 2 = 200.0
    assert repo.average_amount() == 200.0


def test_failed_transaction_rolls_everything_back(tmp_path: Path) -> None:
    """Помилка в середині транзакції не має лишити половину записів (відкат)."""
    db_file = tmp_path / "rollback.db"
    engine = make_engine(db_file)
    Base.metadata.create_all(engine)
    factory = make_session_maker(engine)

    item = Procurement(
        id="proc-rollback", title="Тест", company="Тест", amount=500.0, category="Тест"
    )

    # Симулюємо помилку під час транзакції
    with pytest.raises(RuntimeError, match="щось пішло не так"), session_scope(factory) as session:
        repo = SqlProcurementRepository(session)
        repo.add_many([item])
        raise RuntimeError("щось пішло не так уже після запису")

    # Перевіряємо, що після відкату транзакції база залишилася абсолютно порожньою
    with session_scope(factory) as session:
        repo = SqlProcurementRepository(session)
        assert repo.count() == 0

    engine.dispose()
