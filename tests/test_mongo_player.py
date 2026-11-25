from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from checker import mongo
from player.app import make_app

ROOT = Path(__file__).parent.parent
needs_mongod = pytest.mark.skipif(not mongo.available(), reason="mongod is not installed here")


@pytest.fixture
def content(tmp_path):
    """One strand folder with an SQL lesson and a MongoDB lesson."""
    d = tmp_path / "content" / "sql"
    d.mkdir(parents=True)
    (tmp_path / "content" / "ui.yaml").write_text((ROOT / "content" / "ui.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    (d / "thoughts.yaml").write_text(yaml.safe_dump({"thoughts": {}}), encoding="utf-8")
    (d / "lesson-01.yaml").write_text(yaml.safe_dump({"lesson": "t-01", "steps": [
        {"kind": "recap", "text": "SQL."}]}), encoding="utf-8")
    (d / "lesson-02.yaml").write_text(yaml.safe_dump({"lesson": "t-02", "steps": [
        {"kind": "give", "lang": "mongo", "data": "mongo", "text": "Run it.", "shows": ["db.coupons.countDocuments()"]}]}),
        encoding="utf-8")
    return d


def test_a_mongo_lesson_is_left_out_where_there_is_no_mongod(content, tmp_path, data_dir, monkeypatch):
    monkeypatch.setattr(mongo, "available", lambda: False)
    from player.app import Player
    p = Player(content, data_dir, tmp_path / "progress")
    assert p.names == ["t-01"] and p.skipped == ["t-02"]


@needs_mongod
def test_a_mongo_lesson_is_played_where_there_is_one(content, tmp_path, data_dir):
    from player.app import Player
    p = Player(content, data_dir, tmp_path / "progress")
    assert p.names == ["t-01", "t-02"] and p.skipped == []


@needs_mongod
def test_the_try_panel_runs_mongo_on_the_mongo_data_whatever_step_is_showing(content, tmp_path, data_dir):
    c = TestClient(make_app(content, data_dir, tmp_path / "progress"))
    c.get("/api/run")
    item = c.post("/api/play", json={"lang": "mongo", "code": "db.coupons.countDocuments()"}).json()
    assert item["lang"] == "mongo" and item["docs"] == [4] and item["error"] is None


@needs_mongod
def test_the_try_panel_may_change_a_scratch_copy_and_never_the_course_data(content, tmp_path, data_dir):
    c = TestClient(make_app(content, data_dir, tmp_path / "progress"))
    c.get("/api/run")
    gone = c.post("/api/play", json={"lang": "mongo", "code": "db.coupons.deleteMany({})"}).json()
    assert gone["error"] is None and gone["docs"][0]["deletedCount"] == 4
    assert c.post("/api/play", json={"lang": "mongo", "code": "db.coupons.countDocuments()"}).json()["docs"] == [4]


@needs_mongod
def test_a_mongo_error_in_the_try_panel_is_calm(content, tmp_path, data_dir):
    c = TestClient(make_app(content, data_dir, tmp_path / "progress"))
    c.get("/api/run")
    item = c.post("/api/play", json={"lang": "mongo", "code": "db.orders.find({a: })"}).json()
    assert item["error"] and item["docs"] == []


@needs_mongod
def test_the_data_tab_shows_documents_on_a_mongo_step(content, tmp_path, data_dir):
    c = TestClient(make_app(content, data_dir, tmp_path / "progress"))
    c.get("/api/run")
    c.post("/api/next")
    c.post("/api/run/new", json={"next": True})
    body = c.get("/api/data").json()
    assert body["data"] == "mongo"
    names = {t["name"]: t for t in body["tables"]}
    assert set(names) == {"coupons", "couriers", "orders", "restaurants"}
    assert names["orders"]["total"] == 6000 and len(names["orders"]["docs"]) == 3
    assert isinstance(names["orders"]["docs"][0]["created_at"], str)
