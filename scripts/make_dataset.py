import json
import pathlib
import random

# Фіксуємо random seed для відтворюваності результатів
random.seed(7)

# Предметні дані для публічних закупівель
categories = [
    "Комп'ютерна техніка",
    "Транспортні послуги",
    "Медичне обладнання",
    "Будівельні роботи",
    "Канцелярські товари",
    "Електроенергія",
]

procuring_entities = [
    "ДП Медичні закупівлі України",
    "КП Київпастранс",
    "АТ Укрзалізниця",
    "Департамент освіти і науки",
    "Виконавчий комітет міської ради",
    "КНП Міська клінічна лікарня",
]

tender_templates = [
    "Закупівля комп'ютерного обладнання",
    "Послуги з ремонту та обслуговування",
    "Постачання природного газу",
    "Придбання медичних матеріалів",
    "Капітальний ремонт приміщення",
]

# Створення директорії data за потреби
path = pathlib.Path("data/large.jsonl")
path.parent.mkdir(parents=True, exist_ok=True)

prev = None

with path.open("w", encoding="utf-8") as f:
    for i in range(200_000):
        # Дублікат тендера
        if i % 10 == 3 and prev is not None:
            row = dict(prev)
        else:
            category = random.choice(categories)
            company = random.choice(procuring_entities)
            title_base = random.choice(tender_templates)

            # Рандомні суми (або "за домовленістю" / не вказано)
            amount = str(random.randint(10_000, 5_000_000)) if i % 7 else "за домовленістю"

            row = {
                "title": f"{title_base} №{i}",
                "company": company,
                "amount": amount,
                "category": category,
            }

        # Некоректний запис (порожній title) для перевірки валідації
        if i % 1000 == 0:
            row = dict(row, title="")

        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        prev = row
