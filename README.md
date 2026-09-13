## Нормалізація назв (Title Normalization)

Для приведення текстових назв до єдиного стандарту використовується функція `normalize_title`:

- Видаляє зайві пробіли на початку, наприкінці та між словами.
- Приводить увесь текст до нижнього регістру.

**Приклад використання:**

```python
from procure_stat.domain.text import normalize_title

raw_input = "  Привіт   Світ  "
result = normalize_title(raw_input)
# Результат: "привіт світ"
```
