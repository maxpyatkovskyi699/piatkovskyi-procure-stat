from collections.abc import Iterator
from typing import Any, Protocol


class Source(Protocol):
    """Будь-що, що віддає сирі записи для конвеєра."""

    name: str

    def read(self) -> Iterator[dict[str, Any]]: ...
