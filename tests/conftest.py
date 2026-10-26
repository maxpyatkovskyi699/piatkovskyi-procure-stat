import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

ROW = {
    "title": "Капітальний ремонт приміщення",
    "company": "АТ Укрзалізниця",
    "amount": "496530",
    "category": "Будівництво",
}


class FakeSource:
    def __init__(self, rows: list[dict[str, Any]], name: str = "fake") -> None:
        self.name = name
        self._rows = rows

    def read(self) -> Iterator[dict[str, Any]]:
        yield from self._rows


@pytest.fixture
def row() -> dict[str, Any]:
    """Один коректний сирий запис закупівлі."""
    return {
        "id": "1",
        "title": "Капітальний ремонт приміщення",
        "company": "АТ Укрзалізниця",
        "amount": "496530",
        "category": "Будівництво",
    }


@pytest.fixture
def rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Містить: 1 валідний, 1 дублікат, 1 битий (без назви), 1 з некоректною сумою."""
    return [
        row,
        {
            "id": "1",
            "title": "Капітальний ремонт приміщення",
            "company": "АТ Укрзалізниця",
            "amount": "496530",
            "category": "Будівництво",
        },  # Дублікат (такий самий ідентифікатор/дані)
        {
            "id": "2",
            "title": "",
            "company": "АТ Укрзалізниця",
            "amount": "100000",
            "category": "Будівництво",
        },  # Битий рядок (порожня назва викличе помилку валідації)
        {
            "id": "3",
            "title": "Послуги зв'язку",
            "company": "АТ Укрзалізниця",
            "amount": "некоректна_сума",
            "category": "ІТ",
        },  # Запис із нечисловою сумою
    ]


@pytest.fixture
def jsonl_file(tmp_path: Path, rows: list[dict[str, Any]]) -> Path:
    """Тимчасовий .jsonl файл із закупівлями — зникає разом із tmp_path."""
    path = tmp_path / "procurements.jsonl"
    body = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
    path.write_text(body + "\n", encoding="utf-8")
    return path
