from legacy.loader import process_procurements


def test_procurements_output_is_stable():
    rows = process_procurements("data/prozorro.json")

    # Перевіряємо, що після дедуплікації та очищення залишилися очікувані записи
    assert len(rows) == 6  # Кількість унікальних закупівель у датасеті

    # Перший запис: назва очищена від пробілів і приведена до нижнього регістру, сума — число
    assert rows[0][0] == "закупівля комп'ютерного обладнання"
    assert rows[0][2] == 150000

    # Запис із нечисловою сумою ("за домовленістю" або "невідомо") перетворюється на 0
    assert any(row[2] == 0 for row in rows)  # Перевірка, що некоректна сума стала 0
