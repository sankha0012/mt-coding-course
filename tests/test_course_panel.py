from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from player.app import make_app
from player.store import Store

ROOT = Path(__file__).parent.parent


@pytest.fixture
def make(tmp_path, data_dir):
    """A four-lesson course: two SQL lessons, a cold sitting, and a Python lesson after it."""
    content = tmp_path / "content"
    plan = [("sql", "lesson-01", "t-01", "One"), ("sql", "lesson-02", "t-02", "Two"),
            ("cold", "lesson-01", "t-03", "Cold"), ("py", "lesson-01", "t-04", "Four")]
    for strand, f, lesson, title in plan:
        (content / strand).mkdir(parents=True, exist_ok=True)
        (content / strand / f"{f}.yaml").write_text(yaml.safe_dump({
            "lesson": lesson, "title": title, "strand": strand, "steps": [
                {"kind": "recap", "text": f"{title} a."}, {"kind": "recap", "text": f"{title} b."}]}),
            encoding="utf-8")
    (content / "course.yaml").write_text(
        yaml.safe_dump({"course": [f"{s}/{f}" for s, f, _, _ in plan]}), encoding="utf-8")
    (content / "ui.yaml").write_text((ROOT / "content" / "ui.yaml").read_text(encoding="utf-8"), encoding="utf-8")

    def build():
        return TestClient(make_app(content, data_dir, tmp_path / "progress")), tmp_path / "progress"
    return build


def states(c):
    return [(i["lesson"], i["state"], i["finished"]) for i in c.get("/api/course").json()["lessons"]]


def finish(c):
    c.post("/api/next")
    return c.post("/api/next").json()


def test_at_the_start_only_the_first_lesson_is_open(make):
    c, _ = make()
    c.get("/api/run")
    assert states(c) == [("t-01", "current", False), ("t-02", "locked", False),
                         ("t-03", "locked", False), ("t-04", "locked", False)]


def test_the_outline_has_titles_strands_and_passes(make):
    c, _ = make()
    body = c.get("/api/course").json()
    first = body["lessons"][0]
    assert first["title"] == "One" and first["strand"] == "sql" and first["pass"] == 0
    assert [i["pass"] for i in body["lessons"]] == [0, 0, 0, 1]
    assert len(body["passes"]) == 2 and all(isinstance(p, str) for p in body["passes"])


def test_a_finished_lesson_opens_the_next_one(make):
    c, _ = make()
    c.get("/api/run")
    finish(c)
    assert states(c)[:2] == [("t-01", "current", True), ("t-02", "next", False)]
    assert states(c)[2][1] == "locked"


def test_starting_the_next_lesson_makes_the_finished_one_sit_again(make):
    c, _ = make()
    c.get("/api/run")
    finish(c)
    body = c.post("/api/lesson/start", json={"lesson": "t-02"}).json()
    assert body["lesson"] == "t-02" and body["items"][0]["text"] == "Two a."
    assert states(c)[:2] == [("t-01", "done", True), ("t-02", "current", False)]


def test_a_locked_or_unknown_lesson_cannot_be_started(make):
    c, _ = make()
    c.get("/api/run")
    assert c.post("/api/lesson/start", json={"lesson": "t-04"}).status_code == 409
    assert c.post("/api/lesson/start", json={"lesson": "t-02"}).status_code == 409
    assert c.post("/api/lesson/start", json={"lesson": "nope"}).status_code == 400


def test_starting_over_keeps_the_old_attempt_in_the_progress_file(make):
    c, progress = make()
    c.get("/api/run")
    c.post("/api/next")
    before = Store(progress)
    old = before.latest("t-01")[0]
    old_items = before.items(old)
    body = c.post("/api/lesson/start", json={"lesson": "t-01"}).json()
    assert [i["text"] for i in body["items"]] == ["One a."] and body["run_id"] != old
    after = Store(progress)
    assert after.items(old) == old_items
    assert after.latest("t-01")[0] == body["run_id"]


def test_a_finished_lesson_can_be_sat_again_after_later_ones(make):
    c, _ = make()
    c.get("/api/run")
    finish(c)
    c.post("/api/lesson/start", json={"lesson": "t-02"})
    c.post("/api/lesson/start", json={"lesson": "t-01"})
    assert states(c)[:3] == [("t-01", "current", True), ("t-02", "next", False), ("t-03", "locked", False)]


def test_reading_the_outline_changes_nothing(make):
    c, progress = make()
    before = c.get("/api/run").json()
    c.get("/api/course")
    c.get("/api/course")
    assert c.get("/api/run").json() == before
    assert Store(progress).events() == []
