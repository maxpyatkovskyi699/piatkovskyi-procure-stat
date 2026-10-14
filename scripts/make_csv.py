import csv
from pathlib import Path


def main() -> None:
    output_path = Path("data/procurements.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["title", "company", "amount", "category"]

    sample_titles = [
        "Капітальний ремонт приміщення",
        "Послуги з постачання електричної енергії",
        "Придбання комп'ютерного обладнання",
        "Будівництво спортивного майданчика",
        "Закупівля медичних матеріалів",
    ]
    sample_companies = [
        "АТ Укрзалізниця",
        "КП Київтеплоенерго",
        "ДП Енергоатом",
        "ТОВ Епіцентр К",
    ]
    sample_categories = [
        "Будівництво",
        "Енергетика",
        "Комп'ютерна техніка",
        "Медицина",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        for i in range(1, 5001):
            writer.writerow(
                {
                    "title": f"{sample_titles[i % len(sample_titles)]} №{i}",
                    "company": sample_companies[i % len(sample_companies)],
                    "amount": str(10000 + (i * 123) % 1000000),
                    "category": sample_categories[i % len(sample_categories)],
                }
            )

    print(f"Успішно згенеровано 5000 рядків у файл: {output_path}")


if __name__ == "__main__":
    main()
