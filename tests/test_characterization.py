import json
from pathlib import Path

from procure_stat.services.pipeline import Pipeline
from procure_stat.sources.jsonl import JsonlSource


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

    source = JsonlSource(file_path)
    pipeline = Pipeline([source])

    # run() повертає статистику, а самі дані обробляються всередині.
    stats = pipeline.run()

    assert stats.read == 3
    assert stats.duplicates == 1
    assert stats.kept == 2
