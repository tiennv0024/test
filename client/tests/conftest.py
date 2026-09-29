import sys
from pathlib import Path

for module_name in list(sys.modules):
    if module_name == "app" or module_name.startswith("app."):
        del sys.modules[module_name]

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app.db.database import get_connection, init_db


@pytest.fixture
def conn(tmp_path):
    connection = get_connection(tmp_path / "library.db")
    init_db(connection)
    try:
        yield connection
    finally:
        connection.close()
