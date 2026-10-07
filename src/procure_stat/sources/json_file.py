import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


def read_rows(path: Path) -> Iterator[dict[str, Any]]:
    """Читає JSONL файл построково та повертає ітератор словників."""
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def read_rows_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Ледаче читання файлу JSON Lines (один об'єкт на рядок)."""
    # Any виправданий: json.loads повертає тип Any до перевірки в доменному шарі
    path = Path(path)
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)
