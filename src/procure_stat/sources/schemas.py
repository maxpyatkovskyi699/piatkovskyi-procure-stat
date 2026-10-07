from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..domain.models import Procurement


class ProcurementIn(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
    )

    id: str = Field(min_length=1, alias="procurement_id")
    title: str = Field(min_length=1, max_length=500)
    company: str = Field(min_length=1, alias="buyer_company")
    amount: int | None = Field(default=None, gt=0)
    category: str = Field(min_length=1, default="Загальне")

    @field_validator("amount", mode="before")
    @classmethod
    def unknown_amount(cls, value: object) -> object:
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return None  # «за домовленістю» / порожній сума перетворюється на None
        return value

    @field_validator("title", "company", "category")
    @classmethod
    def strip_spaces(cls, value: str) -> str:
        return " ".join(value.split())

    @field_validator("title")
    @classmethod
    def lowercase_title(cls, value: str) -> str:
        return value.lower()

    def to_domain(self) -> Procurement:
        return Procurement(
            id=self.id,
            title=self.title,
            company=self.company,
            amount=self.amount,
            category=self.category,
        )
