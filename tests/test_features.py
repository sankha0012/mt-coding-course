from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from checker import mongo
from player.app import make_app

ROOT = Path(__file__).parent.parent


@pytest.fixture
def client(tmp_path, data_dir):
    return TestClient(make_app(ROOT / "content" / "sql", data_dir, tmp_path))


def test_the_page_is_told_whether_mongodb_is_available(client, monkeypatch):
    monkeypatch.setattr(mongo, "available", lambda: True)
    assert client.get("/api/features").json() == {"mongo": True}
    monkeypatch.setattr(mongo, "available", lambda: False)
    assert client.get("/api/features").json() == {"mongo": False}
