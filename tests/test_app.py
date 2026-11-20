from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from player.app import make_app

ROOT = Path(__file__).parent.parent


@pytest.fixture
def make_client(data_dir, tmp_path):
    def make():
        return TestClient(make_app(ROOT / "content" / "sql", data_dir, tmp_path))
    return make


def test_the_first_view_is_the_first_step(make_client):
    r = make_client().get("/api/run")
    assert r.status_code == 200
    body = r.json()
    assert body["items"][0]["type"] == "teacher"
    assert body["pending"] == {"mode": "run", "sql": "SELECT COUNT(*) FROM orders"}


def test_running_the_shown_sentence_adds_the_result(make_client):
    c = make_client()
    c.get("/api/run")
    body = c.post("/api/next").json()
    assert [i["type"] for i in body["items"][-3:]] == ["learner", "result", "teacher"]
    assert body["items"][-2]["rows"] == [[6000]]
    assert body["pending"] == {"mode": "continue"}


def test_an_answer_out_of_turn_is_refused(make_client):
    c = make_client()
    c.get("/api/run")
    assert c.post("/api/answer", json={"sql": "SELECT 1"}).status_code == 409


def test_an_empty_answer_is_refused(make_client):
    c = make_client()
    c.get("/api/run")
    assert c.post("/api/answer", json={"sql": "   "}).status_code == 400


def test_continuing_while_an_answer_is_due_is_refused(make_client):
    c = make_client()
    body = c.get("/api/run").json()
    while body["pending"]["mode"] != "answer":
        body = c.post("/api/next").json()
    assert c.post("/api/next").status_code == 409


def test_a_new_run_is_refused_before_the_end(make_client):
    c = make_client()
    c.get("/api/run")
    assert c.post("/api/run/new").status_code == 409


def test_an_answer_is_judged_and_a_miss_is_calm(make_client):
    c = make_client()
    body = c.get("/api/run").json()
    while body["pending"]["mode"] != "answer":
        body = c.post("/api/next").json()
    body = c.post("/api/answer", json={"sql": "SELECT 1"}).json()
    assert body["pending"]["mode"] == "answer"
    assert body["items"][-2]["type"] in ("teacher", "result")
    assert "wrong" not in str(body["items"][-3:]).lower()


def test_progress_is_resumed_after_the_app_is_rebuilt(make_client):
    c = make_client()
    c.get("/api/run")
    before = c.post("/api/next").json()
    again = make_client().get("/api/run").json()
    assert again["run_id"] == before["run_id"]
    assert again["items"] == before["items"]
    assert again["pending"] == before["pending"]


def test_the_page_and_its_files_are_served(make_client):
    c = make_client()
    assert "<html" in c.get("/").text.lower()
    assert c.get("/static/app.js").status_code == 200
    assert c.get("/static/style.css").status_code == 200
