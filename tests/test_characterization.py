import json
from pathlib import Path

from procure_stat.services.pipeline import PipelineStats, deduplicate, parse_all  # type: ignore
from procure_stat.sources.json_file import read_rows_jsonl  # type: ignore


def test_procurements_output_is_stable(tmp_path: Path) -> None:
    test_data = [
        {
            "id": "1",
            "title": " Закупівля комп'ютерного обладнання ",
            "company": "ДП Медичні закупівлі",
            "amount": "150000",
            "category": "Комп'ютерна техніка",
        },
        {
            "id": "1",  # Дублікат за id
            "title": "Закупівля комп'ютерного обладнання",
            "company": "ДП Медичні закупівлі",
            "amount": "150000",
            "category": "Комп'ютерна техніка",
        },
        {
            "id": "2",
            "title": "Ремонт доріг",
            "company": "КП Київпастранс",
            "amount": "за домовленістю",
            "category": "Будівництво",
        },
    ]

    file_path = tmp_path / "test_prozorro.jsonl"
    file_path.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in test_data),
        encoding="utf-8",
    )

    stats = PipelineStats()
    rows = list(deduplicate(parse_all(read_rows_jsonl(file_path), stats), stats))

    assert len(rows) == 2
    assert rows[0].id == "1"
    assert rows[0].title == "закупівля комп'ютерного обладнання"
    assert rows[0].amount == 150000
    assert any(row.amount is None for row in rows)
