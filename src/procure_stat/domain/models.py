from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Procurement:
    title: str
    company: str
    amount: int
    category: str


@property
def key(self) -> tuple[str, str]:
    return self.title, self.company
