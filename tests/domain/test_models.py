import pytest

from procure_stat.domain.models import Procurement


@pytest.mark.parametrize(
    "procurement_id, title, company, amount, category",
    [
        (" ", "Ноутбуки", "ТОВ Вектор", 100, "IT"),  # порожній id
        ("UA-1", " ", "ТОВ Вектор", 100, "IT"),  # порожній заголовок
        ("UA-1", "Ноутбуки", "", 100, "IT"),  # порожня компанія
        ("UA-1", "Ноутбуки", "ТОВ Вектор", 100, "   "),  # порожня категорія
        ("UA-1", "Ноутбуки", "ТОВ Вектор", -500, "IT"),  # від'ємна сума
        ("UA-1", "Ноутбуки", "ТОВ Вектор", 0, "IT"),  # нульова сума
    ],
)
def test_invalid_procurement_rejected(
    procurement_id: str,
    title: str,
    company: str,
    amount: int | None,
    category: str,
) -> None:
    with pytest.raises(ValueError):
        Procurement(procurement_id, title, company, amount, category)


def test_frozen_model_is_hashable() -> None:
    a = Procurement("UA-1", "Ноутбуки", "ТОВ Вектор", 100, "IT")
    b = Procurement("UA-1", "Ноутбуки", "ТОВ Вектор", 100, "IT")

    # Перевірка хешованості та порівняння однакових об'єктів у set
    assert len({a, b}) == 1


def test_valid_procurement_creation() -> None:
    p = Procurement("UA-100", "Папір A4", "ТОВ Офіс", 5000, "Канцтовари")
    assert p.key == "UA-100"
    assert p.is_high_value is False
