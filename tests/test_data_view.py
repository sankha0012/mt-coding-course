from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from player.app import make_app
from player.store import Store

ROOT = Path(__file__).parent.parent


@pytest.fixture
def make(tmp_path, data_dir):
    """A course whose steps use the root data, a Python step, and a step with its own folder."""
    data = tmp_path / "data"
    data.mkdir()
    for f in data_dir.glob("*.csv"):
        (data / f.name).write_bytes(f.read_bytes())
    (data / "sub").mkdir()
    (data / "sub" / "pets.csv").write_text("name,age\nRex,3\nTom,\n", encoding="utf-8")
    content = tmp_path / "content"
    (content / "sql").mkdir(parents=True)
    (content / "ui.yaml").write_text((ROOT / "content" / "ui.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    (content / "sql" / "thoughts.yaml").write_text(yaml.safe_dump({"thoughts": {}}), encoding="utf-8")
    (content / "sql" / "lesson-01.yaml").write_text(yaml.safe_dump({"lesson": "t-01", "steps": [
        {"kind": "recap", "text": "One."},
        {"kind": "recap", "text": "Two.", "lang": "python"},
        {"kind": "recap", "text": "Three.", "data": "sub"}]}), encoding="utf-8")

    def build():
        return TestClient(make_app(content / "sql", data, tmp_path / "progress")), tmp_path / "progress"
    return build


def test_a_sql_step_gets_the_root_tables_by_table_name(make):
    c, _ = make()
    body = c.get("/api/data").json()
    assert body["data"] == ""
    orders = next(t for t in body["tables"] if t["name"] == "orders")
    assert orders["total"] == 6000 and len(orders["rows"]) == 10 and orders["columns"][0] == "order_id"
    assert "sub" not in [t["name"] for t in body["tables"]]


def test_a_python_step_gets_file_names(make):
    c, _ = make()
    c.get("/api/run")
    c.post("/api/next")
    assert "orders.csv" in [t["name"] for t in c.get("/api/data").json()["tables"]]


def test_a_step_with_its_own_folder_gets_that_folder(make):
    c, _ = make()
    c.get("/api/run")
    c.post("/api/next")
    c.post("/api/next")
    body = c.get("/api/data").json()
    assert body["data"] == "sub"
    assert body["tables"] == [{"name": "pets", "columns": ["name", "age"],
                               "rows": [["Rex", "3"], ["Tom", None]], "total": 2}]


def test_reading_the_data_changes_nothing(make):
    c, progress = make()
    before = c.get("/api/run").json()
    c.get("/api/data")
    c.get("/api/data")
    assert c.get("/api/run").json() == before
    s = Store(progress)
    assert s.events() == [] and s.questions() == []
