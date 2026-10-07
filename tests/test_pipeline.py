import tempfile
from pathlib import Path

from procure_stat.domain.models import Procurement
from procure_stat.services.pipeline import (
    PipelineStats,
    batched,
    collect,
    deduplicate,
    load_procurements,
    parse_all,
)


def test_invalid_rows_are_counted() -> None:
    """Перевіряє, що некоректні рядки відсіюються та збільшують лічильник stats.invalid."""
    rows = [
        # Валідний запис
        {
            "id": "1",
            "title": "Закупівля ПК",
            "company": "ТОВ Тест",
            "amount": "1000",
            "category": "Комп'ютерне обладнання",
        },
        # Невалідний запис (відсутній title)
        {
            "id": "2",
            "title": "",
            "company": "ТОВ Тест 2",
            "amount": "2000",
            "category": "Комп'ютерне обладнання",
        },
    ]
    stats = PipelineStats()
    result = list(parse_all(rows, stats))
    assert len(result) == 1
    assert stats.read == 2
    assert stats.invalid == 1


def test_deduplicate_removes_duplicates() -> None:
    """Перевіряє фільтрацію дублікатів за id."""
    items = [
        Procurement(id="1", title="Закупівля ПК", company="ТОВ Альфа", amount=1000, category="ІТ"),
        Procurement(
            id="1", title="Закупівля ПК", company="ТОВ Альфа", amount=5000, category="ІТ"
        ),  # Дублікат за id
        Procurement(
            id="2", title="Ремонт", company="ТОВ Бета", amount=2000, category="Будівництво"
        ),
    ]
    stats = PipelineStats()
    result = list(deduplicate(items, stats))
    assert len(result) == 2
    assert stats.duplicates == 1


def test_collect_calculates_analytics() -> None:
    """Перевіряє правильність збору аналітики та категорій."""
    items = [
        Procurement(id="1", title="Закупівля ПК", company="ТОВ А", amount=1000, category="ІТ"),
        Procurement(id="2", title="Сервер", company="ТОВ Б", amount=3000, category="ІТ"),
    ]
    stats = PipelineStats()
    collect(items, stats)
    assert stats.kept == 2
    assert stats.by_category["ІТ"] == 2
    assert stats.amount_sum == 4000
    assert stats.amount_min == 1000
    assert stats.amount_max == 3000
    assert stats.amount_avg == 2000.0


def test_batched_splits_tail() -> None:
    """Перевіряє, що batched коректно розбиває потік та правильно залишає залишок."""
    result = [len(b) for b in batched(range(7), 3)]
    assert result == [3, 3, 1]


def test_full_process_pipeline_on_temp_file() -> None:
    """Інтеграційний тест для перевірки повного конвеєра process_pipeline на тимчасовому файлі."""
    jsonl_content = (
        '{"id": "1", "title": "Тендер 1", "company": "Компанія A", "amount": 100, "category": "Паливо"}\n'
        '{"id": "1", "title": "Тендер 1", "company": "Компанія A", "amount": 100, "category": "Паливо"}\n'
        '{"id": "2", "title": "", "company": "Компанія B", "amount": 200, "category": "Паливо"}\n'
    )
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl", encoding="utf-8") as tmp:
        tmp.write(jsonl_content)
    tmp_path = Path(tmp.name)
    try:
        stats = PipelineStats()
        result = load_procurements(tmp_path, stats)

        assert len(result) == 1
        assert stats.read == 3
        assert stats.invalid == 1
        assert stats.duplicates == 1
        assert stats.kept == 1
    finally:
        tmp_path.unlink()
