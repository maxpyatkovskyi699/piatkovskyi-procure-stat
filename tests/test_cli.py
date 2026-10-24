from pathlib import Path

import pytest

from procure_stat.cli import main


def test_missing_file_exits_with_code_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Перевіряє, що у разі відсутності вхідного файлу CLI завершується з кодом 1."""
    monkeypatch.setattr("sys.argv", ["procure-stat", str(tmp_path / "no.jsonl")])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 1


def test_flag_beats_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Пріоритет: аргумент командного рядка > змінна середовища."""
    jsonl_file = tmp_path / "data.jsonl"
    jsonl_file.write_text(
        '{"id": "1", "title": "Ремонт", "company": "АТ Укрзалізниця", "amount": 1000, "category": "Будівництво"}\n',
        encoding="utf-8",
    )

    levels: list[str] = []
    monkeypatch.setattr("procure_stat.cli.setup", levels.append)
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    monkeypatch.setattr("sys.argv", ["procure-stat", str(jsonl_file), "--log-level", "DEBUG"])

    main()

    assert levels == ["DEBUG"]


def test_environment_beats_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Пріоритет: змінна середовища > значення за замовчуванням."""
    jsonl_file = tmp_path / "data.jsonl"
    jsonl_file.write_text(
        '{"id": "1", "title": "Ремонт", "company": "АТ Укрзалізниця", "amount": 1000, "category": "Будівництво"}\n',
        encoding="utf-8",
    )

    levels: list[str] = []
    monkeypatch.setattr("procure_stat.cli.setup", levels.append)
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setattr("sys.argv", ["procure-stat", str(jsonl_file)])

    main()

    assert levels == ["WARNING"]
