"""Ієрархія винятків застосунку: один корінь, кілька конкретних нащадків."""


class ProcureStatError(Exception):
    """Базовий виняток застосунку."""


class SourceError(ProcureStatError):
    """Проблема з джерелом даних: файл, мережа, формат."""


class ParseError(SourceError):
    """Запис не вдалося розібрати."""


class ConfigError(ProcureStatError):
    """Некоректна конфігурація застосунку."""
