from collections.abc import Iterator
from typing import Any
from procure_stat.services.pipeline import Pipeline


class FakeSource:
    def __init__(self, rows: list[dict[str, Any]], name: str = "fake") -> None:
        self.name = name
        self._rows = rows

    def read(self) -> Iterator[dict[str, Any]]:
        yield from self._rows


ROW = {
    "title": "Капітальний ремонт приміщення",
    "company": "АТ Укрзалізниця",
    "amount": "496530",
    "category": "Будівництво",
}


def test_invalid_row_is_skipped_not_raised() -> None:
    """Перевіряє, що невалідний рядок (без обов'язкового поля) пропускається, а не викликає помилку."""
    invalid_row = {
        "title": "",
        "company": "АТ Укрзалізниця",
        "amount": "1000",
        "category": "Будівництво",
    }
    stats = Pipeline([FakeSource([ROW, invalid_row])]).run()
    assert stats.invalid == 1 and stats.kept == 1


def test_duplicates_across_sources() -> None:
    """Перевіряє коректність підрахунку дублікатів з кількох джерел."""
    stats = Pipeline([FakeSource([ROW], "a"), FakeSource([ROW], "b")]).run()
    assert stats.duplicates == 1
    assert stats.by_source == {"a": 1}


def test_invalid_amount_is_handled() -> None:
    """Перевіряє, що некоректна сума (нечислове значення) вважається невалідним записом."""
    row = dict(ROW, amount="некоректна_сума")
    stats = Pipeline([FakeSource([row])]).run()
    assert stats.kept == 1 and stats.invalid == 0
