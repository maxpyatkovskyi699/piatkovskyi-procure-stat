import json
from collections.abc import Iterator
from pathlib import Path


def read_rows(path: Path) -> Iterator[dict]:
    """Читання звичайного JSON-файлу (масив об'єктів)."""
    path = Path(path)
    with path.open(encoding="utf-8") as f:
        yield from json.load(f)


def read_rows_jsonl(path: Path) -> Iterator[dict]:
    """Ледаче читання файлу JSON Lines (один об'єкт на рядок).

    Биті рядки пропускаються без падіння програми.
    """
    path = Path(path)
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue
