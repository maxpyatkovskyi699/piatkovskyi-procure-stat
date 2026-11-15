from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, cast

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker


def make_engine(path: Path, echo: bool = False) -> Engine:
    engine = create_engine(f"sqlite:///{path}", echo=echo, future=True)

    def _enable_foreign_keys(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    listener = cast(Any, event.listens_for(engine, "connect"))
    listener(_enable_foreign_keys)

    return engine


def make_session_maker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


@contextmanager
def session_scope(session_maker: sessionmaker[Session]) -> Iterator[Session]:
    """Контекстний менеджер для безпечного керування сесією (commit / rollback)."""
    session = session_maker()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
