from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Procurement:
    id: str
    title: str
    company: str
    amount: int | None
    category: str

    @property
    def key(self) -> str:
        return self.id
