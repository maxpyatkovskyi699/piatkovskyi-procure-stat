from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from procure_stat.domain.models import Procurement


def make(**overrides: Any) -> Procurement:
    """Будує валідну закупівлю, замінюючи лише потрібні поля."""
    data: dict[str, Any] = {
        "id": "UA-100",
        "title": "Капітальний ремонт приміщення",
        "company": "АТ Укрзалізниця",
        "amount": 496530,
        "category": "Будівництво",
    }
    data.update(overrides)
    return Procurement(**data)


@pytest.mark.parametrize(
    "overrides",
    [
        {"id": " "},
        {"title": " "},
        {"company": ""},
        {"category": "   "},
        {"amount": 0},
        {"amount": -500},
    ],
)
def test_invalid_procurement_rejected(overrides: dict[str, Any]) -> None:
    """Перевіряє, що невалідні параметри закупівлі відхиляються."""
    with pytest.raises(ValueError):
        make(**overrides)


def test_frozen_model_is_hashable() -> None:
    a = Procurement("UA-1", "Ноутбуки", "ТОВ Вектор", 100, "IT")
    b = Procurement("UA-1", "Ноутбуки", "ТОВ Вектор", 100, "IT")

    # Перевірка хешованості та порівняння однакових об'єктів у set
    assert len({a, b}) == 1


def test_valid_procurement_creation() -> None:
    """Перевіряє коректність створення валідного об'єкта та роботу його властивостей."""
    p = make(id="UA-100")
    assert p.key == "UA-100"


def test_frozen_model_is_immutable() -> None:
    """Перевіряє, що модель є незмінною (frozen), і спроба зміни поля викликає помилку."""
    p = make()
    with pytest.raises(FrozenInstanceError):
        p.title = "Нова назва"  # type: ignore[misc]


def test_procurement_set_deduplication() -> None:
    """Перевіряє, що дві ідентичні закупівлі зливаються в множині (працює дедублікація)."""
    a = make()
    b = make()
    assert len({a, b}) == 1


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (None, False),
        (500_000, False),
        (999_999, False),
        (1_000_000, True),
        (5_000_000, True),
    ],
)
def test_is_high_value(amount: int | None, expected: bool) -> None:
    """Перевіряє бізнес-логіку визначення великих закупівель."""
    assert make(amount=amount).is_high_value is expected
