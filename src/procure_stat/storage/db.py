from pathlib import Path
from typing import Any, Callable, cast

from sqlalchemy import Engine, create_engine, event


def make_engine(path: Path, echo: bool = False) -> Engine:
    engine = create_engine(f"sqlite:///{path}", echo=echo, future=True)

    def enable_foreign_keys(
        dbapi_connection: Any,
        connection_record: Any,
    ) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    listener = cast(Callable[..., Any], event.listens_for(engine, "connect"))
    listener(enable_foreign_keys)

    return engine
