# ProcureStat — Система моніторингу публічних закупівель Prozorro

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Mypy](https://img.shields.io/badge/Mypy-checked-blue)](https://mypy.readthedocs.io/)
[![CodeFactor](https://www.codefactor.io/repository/github/maxpyatkovskyi699/piatkovskyi-procure-stat/badge)](https://www.codefactor.io/repository/github/maxpyatkovskyi699/piatkovskyi-procure-stat)

## Про проєкт

**ProcureStat** — Python-застосунок для збору, обробки та аналізу даних про публічні закупівлі в Україні. Проєкт використовує відкритий API системи Prozorro та дозволяє отримувати інформацію про закупівлі, обробляти її й зберігати в базі даних.

Основна мета проєкту — спростити роботу з даними про публічні закупівлі та створити основу для їх подальшого аналізу.

## Технології

- **Python 3.12+** — основна мова розробки.
- **SQLAlchemy 2.0** — робота з базою даних.
- **SQLite / PostgreSQL** — підтримувані системи зберігання даних.
- **Alembic** — керування міграціями бази даних.
- **Pytest** — автоматизоване тестування.
- **Ruff** — перевірка стилю та якості коду.
- **Mypy** — статична перевірка типів.

Для організації роботи з даними використовується Repository pattern, який відокремлює логіку роботи застосунку від конкретної реалізації сховища.

## Встановлення

### 1. Клонування репозиторію

```bash
git clone https://github.com/maxpyatkovsky1699/piatkovskyi-procure-stat.git
cd piatkovskyi-procure-stat
```

### 2. Створення віртуального середовища

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Встановлення залежностей

```bash
python -m pip install --upgrade pip
pip install -e .
```

## Використання

Для запуску застосунку використовується командний інтерфейс CLI.

Приклад запуску обробки JSONL-файлу зі збереженням результатів у базу даних:

```bash
procure-stat data/large.jsonl --db data/procure_stat.db
```

Під час виконання програма обробляє записи, перевіряє їхню коректність, виявляє дублікати та зберігає відповідні дані.

## Міграції бази даних

Для застосування доступних міграцій Alembic використовується команда:

```bash
alembic upgrade head
```

## Перевірка якості та тестування

Запуск тестів:

```bash
pytest --ignore=tests/test_storage_benchmarks.py
```

Запуск тестів продуктивності:

```bash
pytest tests/test_storage_benchmarks.py -s --no-cov
```

Перевірка типізації:

```bash
mypy src tests
```

Перевірка стилю коду:

```bash
ruff check .
```

## Автор

**Максим Пятковський**

GitHub: [maxpyatkovskyi699](https://github.com/maxpyatkovskyi699)
