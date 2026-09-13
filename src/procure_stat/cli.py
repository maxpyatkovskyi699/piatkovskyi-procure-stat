from procure_stat.domain.text import normalize_title


def main():
    # Приклад використання функції
    raw_title = "   Один   Два  "
    clean_title = normalize_title(raw_title)

    print(f"Normalized title: {clean_title}")


if __name__ == "__main__":
    main()
