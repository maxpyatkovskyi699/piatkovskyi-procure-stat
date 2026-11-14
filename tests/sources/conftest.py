from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from procure_stat.storage.db import make_engine, make_session_maker
from procure_stat.storage.models import Base


@pytest.fixture
def session(tmp_path: Path) -> Iterator[Session]:
    """Порожня база на один тест – у тимчасовому каталозі, не в проєкті."""
    db_file = tmp_path / "test.db"
    engine = make_engine(db_file)
    Base.metadata.create_all(engine)
    session_maker = make_session_maker(engine)

    db = session_maker()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
