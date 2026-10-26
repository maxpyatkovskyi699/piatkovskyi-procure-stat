from procure_stat.domain.text import normalize_title


def test_normalize_title() -> None:
    """Перевіряє коректність нормалізації назви закупівлі (очищення зайвих пробілів тощо)."""
    assert normalize_title("  Капітальний   ремонт  ") == "Капітальний ремонт"
    assert normalize_title("Укрзалізниця") == "Укрзалізниця"
    assert normalize_title("   ") == ""
