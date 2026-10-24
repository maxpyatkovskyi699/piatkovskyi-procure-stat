from procure_stat.services.pipeline import Pipeline
from tests.conftest import FakeSource

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
    """Перевіряє, що нечислова сума не відхиляє запис, а зберігає його з обробленою сумою."""
    row = dict(ROW, amount="некоректна_сума")
    stats = Pipeline([FakeSource([row])]).run()
    assert stats.kept == 1 and stats.invalid == 0
