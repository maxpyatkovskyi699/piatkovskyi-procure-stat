import json
from pathlib import Path

from procure_stat.domain.models import Procurement  # type: ignore
from procure_stat.services.pipeline import PipelineStats, deduplicate, parse_all  # type: ignore
from procure_stat.sources.json_file import read_rows_jsonl  # type: ignore


def test_procurements_output_is_stable(tmp_path: Path) -> None:
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
            "title": "",  # Невалідний запис
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

    file_path = tmp_path / "test_prozorro.jsonl"
    file_path.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in test_data),
        encoding="utf-8",
    )

    stats = PipelineStats()
    result = list(deduplicate(parse_all(read_rows_jsonl(file_path), stats), stats))

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
