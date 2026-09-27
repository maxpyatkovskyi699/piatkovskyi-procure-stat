import json
from collections.abc import Iterator
from pathlib import Path


def read_rows(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8") as f:
        yield from json.load(f)
