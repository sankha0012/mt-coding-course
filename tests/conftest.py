from pathlib import Path

import pytest

from checker.data import load_db

ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def data_dir():
    return ROOT / "data"


@pytest.fixture(scope="session")
def conn(data_dir):
    return load_db(data_dir)
