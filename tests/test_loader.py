import json
from legacy.loader import process_procurements


def test_legacy_loader_behavior(tmp_path):
    test_data = [
        {
            "title": " Закупівля комп'ютерів ",
            "company": "ДП Медичні закупівлі",
            "salary": "150000",
            "city": "Комп'ютерна техніка",
        },
        {
            "title": "закупівля комп'ютерів",
            "company": "ДП Медичні закупівлі",
            "salary": "150000",
            "city": "Комп'ютерна техніка",
        },
        {
            "title": "",
            "company": "КП Київпастранс",
            "salary": "90000",
            "city": "Транспортні послуги",
        },
        {
            "title": "Послуги з ремонту доріг",
            "company": "КП Київпастранс",
            "salary": "за домовленістю",
            "city": "Будівельні роботи",
        },
    ]

    file_path = tmp_path / "test_prozorro.json"
    file_path.write_text(json.dumps(test_data, ensure_ascii=False), encoding="utf-8")

    result = process_procurements(str(file_path))

    expected = [
        ["закупівля комп'ютерів", "ДП Медичні закупівлі", 150000, "Комп'ютерна техніка"],
        ["послуги з ремонту доріг", "КП Київпастранс", 0, "Будівельні роботи"],
    ]

    assert result == expected
