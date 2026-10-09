from dataclasses import dataclass

HIGH_VALUE_THRESHOLD = 1_000_000


@dataclass(frozen=True, slots=True)
class Procurement:
    id: str | None
    title: str
    company: str
    amount: int | None
    category: str

    def __post_init__(self) -> None:
        if self.id is not None and not self.id.strip():
            raise ValueError("id must not be empty string if provided")
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if not self.company.strip():
            raise ValueError("company must not be empty")
        if not self.category.strip():
            raise ValueError("category must not be empty")
        if self.amount is not None and self.amount <= 0:
            raise ValueError("amount must be positive")

    @property
    def key(self) -> str:
        # Якщо є id — використовуємо його, інакше дедуплікуємо за сукупністю полів
        if self.id:
            return self.id
        return f"{self.title}:{self.company}"

    @property
    def is_high_value(self) -> bool:
        return self.amount is not None and self.amount >= HIGH_VALUE_THRESHOLD
