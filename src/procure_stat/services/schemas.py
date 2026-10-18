from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..domain.models import Procurement


class ProcurementIn(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    id: str | None = Field(default=None, min_length=1, alias="procurement_id")
    title: str = Field(min_length=1, max_length=500)
    company: str = Field(min_length=1)  # Без аліасу, у JSONL колюч називається "company"
    amount: int | None = Field(default=None, gt=0)
    category: str = Field(default="Загальне", min_length=1)

    @field_validator("amount", mode="before")
    @classmethod
    def unknown_amount(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return int(value) if value > 0 else None
        if isinstance(value, str):
            cleaned = value.replace(" ", "").replace(",", ".").strip()
            try:
                val = float(cleaned)
                return int(val) if val > 0 else None
            except ValueError:
                return None  # «за домовленістю» / некоректні рядки
        return None

    @field_validator("company", "category")
    @classmethod
    def strip_spaces(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("title")
    @classmethod
    def process_title(cls, value: str) -> str:
        cleaned = " ".join(value.split()).lower()
        if not cleaned:
            raise ValueError("Title cannot be empty after stripping")
        return cleaned

    def to_domain(self) -> Procurement:
        return Procurement(
            id=self.id,
            title=self.title,
            company=self.company,
            amount=self.amount,
            category=self.category,
        )
