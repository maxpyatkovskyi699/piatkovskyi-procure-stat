import pytest

from procure_stat.services.schemas import ProcurementIn  # або твій клас схеми/парсера


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("496530", 496530),
        (496530, 496530),
        ("не вказано", None),
        (None, None),
    ],
)
def test_amount_is_parsed(raw: int | None, expected: int | None) -> None:
    """Перевіряє, що сума закупівлі коректно парситься з різних типів даних."""
    schema = ProcurementIn(
        id="UA-1",
        title="Ремонт",
        company="АТ Укрзалізниця",
        amount=raw,
        category="Будівництво",
    )
    assert schema.amount == expected
