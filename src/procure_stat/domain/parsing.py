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
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def to_procurement(row: dict) -> Procurement | None:
    # Отримуємо ID (якщо є в JSON), інакше приводимо до str будь-яке числове/рядкове значення
    tender_id = str(row.get("id") or row.get("tenderID") or "").strip()
    title = str(row.get("title") or "").strip().lower()
    company = str(row.get("company") or "").strip()
    category = str(row.get("category") or "").strip()

    # Обов'язкові поля для валідності
    if not tender_id or not title or not company:
        return None

    amount = parse_amount(row.get("amount"))

    return Procurement(
        id=tender_id,
        title=title,
        company=company,
        amount=amount,
        category=category,
    )
