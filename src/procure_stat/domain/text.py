# Зміна A: перша нова функція (реверс слова)
def reverse_text(raw: str) -> str:
    return raw[::-1]


def normalize_title(raw: str) -> str:
    return " ".join(raw.split()).lower()


# Зміна B: друга нова функція (перша літера велика)
def capitalize_text(raw: str) -> str:
    return raw.capitalize()
