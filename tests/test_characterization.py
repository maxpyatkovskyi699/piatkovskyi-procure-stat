import json
from pathlib import Path
from collections.abc import Iterator


def read_rows_jsonl(path: Path) -> Iterator[dict]:
    """Зчитує JSONL або стандартний JSON-файл порядково/елемент за елементом."""
    with open(path, "r", encoding="utf-8") as f:
        # Перевіряємо перші символи файлу
        first_char = f.read(1)
        f.seek(0)

        # Якщо файл починається з '[', це стандартний JSON-масив
        if first_char == "[":
            data = json.load(f)
            for row in data:
                if isinstance(row, dict):
                    yield row
        else:
            # Інакше читаємо як JSONL (порядково)
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
