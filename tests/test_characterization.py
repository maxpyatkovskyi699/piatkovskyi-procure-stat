from procure_stat.services.pipeline import load_procurements  # type: ignore


def test_procurements_output_is_stable():
    rows = load_procurements("data/prozorro.json")

    # Перевіряємо, що після дедуплікації та очищення залишилися очікувані записи
    assert len(rows) == 6  # Кількість унікальних закупівель у датасеті

    # Перший запис: назва очищена від пробілів і приведена до нижнього регістру, сума — число
    assert rows[0].title == "закупівля комп'ютерного обладнання"
    assert rows[0].amount == 150000

    # Запис із нечисловою сумою ("за домовленістю" або "невідомо") перетворюється на None
    assert any(row.amount is None for row in rows)  # Перевірка, що некоректна сума стала 0
