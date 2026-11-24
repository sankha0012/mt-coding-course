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


def test_the_page_files_are_never_served_from_a_stale_browser_cache(make_client):
    c = make_client()
    for path in ("/", "/static/app.js", "/static/style.css"):
        assert c.get(path).headers["cache-control"] == "no-cache"


@pytest.fixture
def course(tmp_path, data_dir):
    """A two-lesson course in a temporary folder. Returns a function that builds a client on it."""
    import yaml
    content = tmp_path / "content"
    (content / "sql").mkdir(parents=True)
    (content / "ui.yaml").write_text((ROOT / "content" / "ui.yaml").read_text())
    (content / "sql" / "thoughts.yaml").write_text("thoughts: {}\n")
    (content / "sql" / "lesson-01.yaml").write_text(yaml.safe_dump({"lesson": "t-01", "steps": [
        {"kind": "recap", "text": "One."}]}))
    (content / "sql" / "lesson-02.yaml").write_text(yaml.safe_dump({"lesson": "t-02", "steps": [
        {"kind": "cold-check", "text": "Cold.", "model": "SELECT COUNT(*) FROM orders"},
        {"kind": "recap", "text": "Two."}]}))

    def make():
        return TestClient(make_app(content / "sql", data_dir, tmp_path / "progress"))
    return make


def test_the_view_names_its_lesson(course):
    assert course().get("/api/run").json()["lesson"] == "t-01"


def test_a_finished_lesson_offers_the_next_one(course):
    c = course()
    c.get("/api/run")
    body = c.post("/api/next").json()
    assert body["pending"] == {"mode": "done", "next": True}


def test_the_next_lesson_starts_after_the_first(course):
    c = course()
    c.get("/api/run")
    c.post("/api/next")
    body = c.post("/api/run/new", json={"next": True}).json()
    assert body["lesson"] == "t-02"
    assert body["items"][0]["text"] == "Cold."
    assert body["pending"] == {"mode": "answer", "step": 1, "variant": "main"}


def test_sitting_again_stays_on_the_same_lesson(course):
    c = course()
    c.get("/api/run")
    c.post("/api/next")
    body = c.post("/api/run/new").json()
    assert body["lesson"] == "t-01" and len(body["items"]) == 1


def test_the_last_lesson_has_no_next(course):
    c = course()
    c.get("/api/run")
    c.post("/api/next")
    c.post("/api/run/new", json={"next": True})
    c.post("/api/answer", json={"sql": "SELECT 1"})
    c.post("/api/next")
    body = c.post("/api/next").json()
    assert body["pending"] == {"mode": "done", "next": False}
    assert c.post("/api/run/new", json={"next": True}).status_code == 409


def test_the_course_resumes_in_the_lesson_it_was_in(course):
    c = course()
    c.get("/api/run")
    c.post("/api/next")
    c.post("/api/run/new", json={"next": True})
    again = course().get("/api/run").json()
    assert again["lesson"] == "t-02"


def test_the_try_it_panel_runs_sql_and_shows_the_result(make_client):
    c = make_client()
    c.get("/api/run")
    item = c.post("/api/play", json={"lang": "sql", "code": "SELECT COUNT(*) FROM couriers"}).json()
    assert item["type"] == "result" and item["rows"] == [[200]]


def test_the_try_it_panel_runs_python(make_client):
    c = make_client()
    c.get("/api/run")
    item = c.post("/api/play", json={"lang": "python", "code": "print(sum([1, 2, 3]))"}).json()
    assert item["lang"] == "python" and item["text"] == "6\n"


def test_the_try_it_panel_cannot_change_the_core_data(make_client, data_dir):
    c = make_client()
    c.get("/api/run")
    before = {f.name: f.read_bytes() for f in data_dir.glob("*.csv")}
    assert c.post("/api/play", json={"lang": "sql", "code": "DROP TABLE orders"}).json()["error"]
    assert c.post("/api/play", json={"lang": "python", "code": "open('orders.csv', 'w').write('x')"}).json()["error"]
    assert {f.name: f.read_bytes() for f in data_dir.glob("*.csv")} == before
    assert c.post("/api/play", json={"lang": "sql", "code": "SELECT COUNT(*) FROM orders"}).json()["rows"] == [[6000]]


def test_playing_changes_nothing_in_the_sitting(make_client, tmp_path):
    from player.store import Store
    c = make_client()
    before = c.get("/api/run").json()
    c.post("/api/play", json={"lang": "sql", "code": "SELECT 1"})
    after = c.get("/api/run").json()
    assert after == before
    assert Store(tmp_path).events() == []


def test_the_try_it_panel_refuses_empty_code_and_unknown_languages(make_client):
    c = make_client()
    c.get("/api/run")
    assert c.post("/api/play", json={"lang": "sql", "code": "  "}).status_code == 400
    assert c.post("/api/play", json={"lang": "ruby", "code": "puts 1"}).status_code == 400
