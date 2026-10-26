from typing import Any

import pytest

from procure_stat.domain.parsing import normalize_title, parse_amount, to_procurement


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("  Закупівля   Бензину  ", "закупівля бензину"),
        ("Test Title", "test title"),
        ("", None),
        (None, None),
        ("   ", None),
    ],
)
def test_normalize_title(raw: str | None, expected: str | None) -> None:
    assert normalize_title(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        (100, 100),
        (100.5, 100),
        ("1500", 1500),
        (b"200", 200),
        ("invalid", None),
        (None, None),
        ([1, 2], None),  # Непідтримуваний тип
    ],
)
def test_parse_amount(raw: object, expected: int | None) -> None:
    assert parse_amount(raw) == expected


def test_to_procurement_valid() -> None:
    row = {
        "id": "12345",
        "title": "  Тестова закупівля  ",
        "company": "ТОВ Рога і Копита",
        "amount": "5000",
        "category": "Обладнання",
    }
    proc = to_procurement(row)
    assert proc is not None
    assert proc.id == "12345"
    assert proc.title == "тестова закупівля"
    assert proc.company == "ТОВ Рога і Копита"
    assert proc.amount == 5000
    assert proc.category == "Обладнання"


def test_to_procurement_with_tender_id_alias() -> None:
    # Перевірка альтернативного ключа tenderID
    row = {
        "tenderID": "UA-2026-01",
        "title": "Закупівля паперу",
        "company": "ФОП Василь",
        "category": "Канцтовари",
    }
    proc = to_procurement(row)
    assert proc is not None
    assert proc.id == "UA-2026-01"


@pytest.mark.parametrize(
    "row",
    [
        {},  # Порожній словник
        {"title": "Тест", "company": "Компанія"},  # Відсутній id
        {"id": "1", "company": "Компанія"},  # Відсутній title
        {"id": "1", "title": "Тест"},  # Відсутня компанія
    ],
)
def test_to_procurement_missing_required_fields(row: dict[str, Any] | dict[str, str]) -> None:
    assert to_procurement(row) is None
