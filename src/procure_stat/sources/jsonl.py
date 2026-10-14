import json
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def read_rows(path: Path) -> Iterator[dict[str, Any]]:
    """Читає звичайний JSON-файл (масив об'єктів) та повертає ітератор словників."""
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        yield item
                    else:
                        logger.warning("Skipping non-dict item in JSON array in %s", path)
            else:
                logger.warning("Expected JSON array in %s, got %s", path, type(data).__name__)
    except json.JSONDecodeError as err:
        logger.warning("Invalid JSON file in %s: %s", path, err)


def read_rows_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    """Ледаче читання файлу JSON Lines (один об'єкт на рядок)."""
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as err:
                logger.warning(
                    "Skipping invalid JSON on line %d in %s: %s",
                    line_no,
                    path,
                    err,
                )
