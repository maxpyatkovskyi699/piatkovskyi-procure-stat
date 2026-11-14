from sqlalchemy import Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from procure_stat.domain.models import Procurement


class Base(DeclarativeBase):
    pass


class ProcurementRow(Base):
    __tablename__ = "procurements"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)

    @classmethod
    def from_domain(cls, item: Procurement) -> "ProcurementRow":
        """Створює рядок бази даних із доменної моделі."""
        return cls(
            id=item.id,
            title=item.title,
            company=item.company,
            amount=float(item.amount) if item.amount is not None else None,
            category=item.category,
        )

    def to_domain(self) -> Procurement:
        """Перетворює рядок бази даних у доменну модель."""
        return Procurement(
            id=self.id,
            title=self.title,
            company=self.company,
            amount=int(self.amount) if self.amount is not None else 0,
            category=self.category or "",
        )
