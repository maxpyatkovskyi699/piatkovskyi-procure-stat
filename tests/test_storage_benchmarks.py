import time
from pathlib import Path

from sqlalchemy import text

from procure_stat.domain.models import Procurement
from procure_stat.storage.db import make_engine, make_session_maker, session_scope
from procure_stat.storage.models import Base
from procure_stat.storage.repository import SqlProcurementRepository


def test_experiment_1_indexes_and_selectivity(tmp_path: Path) -> None:
    """Дослід 1: Вплив індексу та вибірковості (company vs category)."""
    db_file = tmp_path / "benchmark_index.db"
    engine = make_engine(db_file)
    Base.metadata.create_all(engine)
    factory = make_session_maker(engine)

    # 1. Заповнюємо базу тестовими даними (amount > 0 для уникнення ValueError)
    with session_scope(factory) as session:
        repo = SqlProcurementRepository(session)
        items = [
            Procurement(
                id=f"proc-{i}",
                title=f"Закупівля №{i}",
                company=f"Компанія {i % 50}",  # Висока вибірковість (50 унікальних)
                amount=float((i + 1) * 10),  # Сума гарантовано > 0
                category="Будівництво"
                if i % 2 == 0
                else "Медицина",  # Низька вибірковість (2 значення)
            )
            for i in range(5000)
        ]
        repo.add_many(items)

    print("\n--- ЕКСПЕРИМЕНТ 1: Вплив індексу ---")

    with factory() as session:
        # А. Тест високої вибірковості (company) БЕЗ індексу
        start = time.perf_counter()
        session.execute(
            text("SELECT * FROM procurements WHERE company = :val"), {"val": "Компанія 10"}
        ).fetchall()
        duration_no_idx = (time.perf_counter() - start) * 1000

        plan_no_idx = session.execute(
            text("EXPLAIN QUERY PLAN SELECT * FROM procurements WHERE company = :val"),
            {"val": "Компанія 10"},
        ).fetchall()

        print(
            f"[Company БЕЗ індексу] Час: {duration_no_idx:.3f} мс | Plan: {plan_no_idx[0].detail}"
        )

        # Створюємо індекс для високої вибірковості
        session.execute(text("CREATE INDEX idx_company ON procurements(company);"))
        session.commit()

        # Б. Тест високої вибірковості (company) З індексом
        start = time.perf_counter()
        session.execute(
            text("SELECT * FROM procurements WHERE company = :val"), {"val": "Компанія 10"}
        ).fetchall()
        duration_idx = (time.perf_counter() - start) * 1000

        plan_idx = session.execute(
            text("EXPLAIN QUERY PLAN SELECT * FROM procurements WHERE company = :val"),
            {"val": "Компанія 10"},
        ).fetchall()

        print(f"[Company З ІНДЕКСОМ] Час: {duration_idx:.3f} мс | Plan: {plan_idx[0].detail}")

    engine.dispose()


def test_experiment_2_transaction_boundaries(tmp_path: Path) -> None:
    """Дослід 2: Вплив межі транзакцій (коміт після кожного рядка vs один коміт наприкінці)."""
    db_file = tmp_path / "benchmark_tx.db"
    engine = make_engine(db_file)
    Base.metadata.create_all(engine)
    factory = make_session_maker(engine)

    items = [
        Procurement(
            id=f"tx-{i}",
            title=f"Тест транзакцій {i}",
            company="Тест ТОВ",
            amount=100.0,
            category="Тест",
        )
        for i in range(1000)
    ]

    print("\n--- ЕКСПЕРИМЕНТ 2: Вплив межі транзакцій (1000 записів) ---")

    # А. Зберігаємо по одному рядку з комітом для кожного
    start = time.perf_counter()
    for item in items:
        with session_scope(factory) as session:
            repo = SqlProcurementRepository(session)
            repo.add_many([item])
    duration_each = time.perf_counter() - start
    print(f"З комітом ПІСЛЯ КОЖНОГО рядка: {duration_each:.3f} сек")

    # Очищаємо таблицю для чистоти експерименту
    with factory() as session:
        session.execute(text("DELETE FROM procurements;"))
        session.commit()

    # Б. Зберігаємо всі рядки в одній транзакції (як робить наш репозиторій)
    start = time.perf_counter()
    with session_scope(factory) as session:
        repo = SqlProcurementRepository(session)
        repo.add_many(items)
    duration_batch = time.perf_counter() - start
    print(f"З ОДНИМ КОМІТОМ наприкінці пакета: {duration_batch:.3f} сек")
    print(f"Різниця у швиддкості: у {duration_each / duration_batch:.1f} разів швидше!")

    engine.dispose()
