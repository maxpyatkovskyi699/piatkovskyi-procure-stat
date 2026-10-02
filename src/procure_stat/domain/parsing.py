from .models import Procurement


def normalize_title(raw: str | None) -> str | None:
    """Чиста функція нормалізації назви закупівлі."""
    if not raw:
        return None
    normalized = " ".join(raw.strip().lower().split())
    return normalized if normalized else None


def parse_amount(raw: object) -> int | None:
    """Чиста функція парсингу суми закупівлі.
    Повертає None, якщо сума відсутня або не є числом."""
    if raw is None:
        return None
    try:
        # Спочатку перетворюємо на float (на випадок рядків із крапкою "150.0"), потім у int
        return int(float(str(raw).strip()))
    except (TypeError, ValueError):
        return None


def to_procurement(row: dict) -> Procurement | None:
    """Чиста функція перетворення сирого словника в об'єкт Procurement."""
    title = normalize_title(row.get("title"))
    if not title:
        return None

    return Procurement(
        title=title,
        company=row.get("company", ""),
        amount=parse_amount(row.get("amount")),
        category=row.get("category", ""),
    )
