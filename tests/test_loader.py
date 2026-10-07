import json
from pathlib import Path

from procure_stat.domain.models import Procurement
from procure_stat.services.pipeline import PipelineStats, load_procurements


def test_load_procurements_behavior(tmp_path: Path) -> None:
    test_data = [
        {
            "id": "1",
            "title": " Закупівля комп'ютерів ",
            "company": "ДП Медичні закупівлі",
            "amount": "150000",
            "category": "Комп'ютерна техніка",
        },
        {
            "id": "1",  # Дублікат за id
            "title": "закупівля комп'ютерів",
            "company": "ДП Медичні закупівлі",
            "amount": "150000",
            "category": "Комп'ютерна техніка",
        },
        {
            "id": "2",
            "title": "",  # Невалідний запис (відсутній title)
            "company": "КП Київпастранс",
            "amount": "90000",
            "category": "Транспортні послуги",
        },
        {
            "id": "3",
            "title": "Послуги з ремонту доріг",
            "company": "КП Київпастранс",
            "amount": "за домовленістю",
            "category": "Будівельні роботи",
        },
    ]

    stats = PipelineStats()

    # Створюємо файл у тимчасовій директорії pytest
    file_path = tmp_path / "sample.jsonl"

    # Записуємо рядки у форматі JSONL (кожен JSON-об'єкт з нового рядка)
    jsonl_content = "\n".join(json.dumps(item, ensure_ascii=False) for item in test_data)
    file_path.write_text(jsonl_content, encoding="utf-8")

    # Передаємо об'єкт file_path (Path) та stats у load_procurements
    result = load_procurements(file_path, stats)

    expected = [
        Procurement(
            id="1",
            title="закупівля комп'ютерів",
            company="ДП Медичні закупівлі",
            amount=150000,
            category="Комп'ютерна техніка",
        ),
        Procurement(
            id="3",
            title="послуги з ремонту доріг",
            company="КП Київпастранс",
            amount=None,
            category="Будівельні роботи",
        ),
    ]

    assert result == expected
    assert stats.read == 4
    assert stats.invalid == 1
    assert stats.duplicates == 1
    assert stats.kept == 2
