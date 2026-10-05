import json

from procure_stat.domain.models import Procurement  # type: ignore
from procure_stat.services.pipeline import load_procurements  # type: ignore


def test_load_procurements_behavior(tmp_path):
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

    file_path = tmp_path / "test_prozorro.json"
    file_path.write_text(json.dumps(test_data, ensure_ascii=False), encoding="utf-8")

    result = load_procurements(str(file_path))

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
