from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from player.app import make_app
from player.store import Store

ROOT = Path(__file__).parent.parent


def recap(text, **more):
    return {"kind": "recap", "text": text, **more}


@pytest.fixture
def make(tmp_path, data_dir):
    """A course in two strands and a cold sitting. t-01 and t-02 are the SQL foundation, t-03 is its interview
    layer and opens with a cold check that borrows a thought of t-04 (Python). t-04 needs the SQL foundation."""
    content = tmp_path / "content"
    lessons = [
        ("sql", "lesson-01", "t-01", "One", 1, [recap("One a.", new=["a"]), recap("One b.")]),
        ("sql", "lesson-02", "t-02", "Two", 1, [recap("Two a.", new=["b"]), recap("Two b.")]),
        ("py", "lesson-01", "t-04", "Four", 1, [recap("Four a.", new=["p"], requires=["b"]), recap("Four b.")]),
        ("sql", "lesson-03", "t-03", "Three", 2, [
            {"kind": "cold-check", "text": "Borrowed cold.", "model": "SELECT COUNT(*) FROM orders", "requires": ["p"]},
            recap("Three a."), recap("Three b.")]),
        ("cold", "lesson-01", "t-05", "Cold", 1, [recap("Cold a.", requires=["b"])]),
    ]
    for strand, f, lesson, title, stage, steps in lessons:
        (content / strand).mkdir(parents=True, exist_ok=True)
        (content / strand / f"{f}.yaml").write_text(yaml.safe_dump({
            "lesson": lesson, "title": title, "strand": strand, "stage": stage, "steps": steps}), encoding="utf-8")
    (content / "course.yaml").write_text(
        yaml.safe_dump({"course": [f"{s}/{f}" for s, f, *_ in lessons]}), encoding="utf-8")
    (content / "ui.yaml").write_text((ROOT / "content" / "ui.yaml").read_text(encoding="utf-8"), encoding="utf-8")

    def build():
        return TestClient(make_app(content, data_dir, tmp_path / "progress")), tmp_path / "progress"
    return build


def states(c):
    return {i["lesson"]: i["state"] for i in c.get("/api/course").json()["lessons"]}


def finish(c):
    c.post("/api/next")
    return c.post("/api/next").json()


def start(c, lesson):
    return c.post("/api/lesson/start", json={"lesson": lesson})


def finish_foundation(c):
    c.get("/api/run")
    finish(c)
    start(c, "t-02")
    finish(c)


def test_at_the_start_only_the_first_lesson_is_open(make):
    c, _ = make()
    c.get("/api/run")
    assert states(c) == {"t-01": "current", "t-02": "locked", "t-04": "locked", "t-03": "locked", "t-05": "locked"}


def test_the_outline_has_titles_strands_layers_and_names_for_the_panel(make):
    c, _ = make()
    body = c.get("/api/course").json()
    first = body["lessons"][0]
    assert (first["title"], first["strand"], first["layer"]) == ("One", "sql", "foundation")
    assert next(i for i in body["lessons"] if i["lesson"] == "t-03")["layer"] == "interview"
    assert [s["id"] for s in body["strands"]][:3] == ["sql", "py", "cold"]
    assert all(s["name"] for s in body["strands"]) and set(body["layers"]) == {"foundation", "interview"}


def test_a_finished_lesson_opens_the_next_one_in_its_strand(make):
    c, _ = make()
    c.get("/api/run")
    finish(c)
    assert states(c)["t-02"] == "open" and states(c)["t-03"] == "locked"


def test_finishing_the_foundation_opens_its_interview_layer_and_the_strands_built_on_it(make):
    c, _ = make()
    finish_foundation(c)
    assert states(c) == {"t-01": "done", "t-02": "current", "t-04": "open", "t-03": "open", "t-05": "open"}


def test_a_locked_lesson_names_what_it_waits_for(make):
    c, _ = make()
    c.get("/api/run")
    waits = {i["lesson"]: i["waits"] for i in c.get("/api/course").json()["lessons"]}
    assert waits["t-02"] == ["One"] and waits["t-04"] == ["One", "Two"] and waits["t-03"] == ["Two"]
    assert waits["t-01"] == []


def test_starting_the_next_lesson_makes_the_finished_one_sit_again(make):
    c, _ = make()
    c.get("/api/run")
    finish(c)
    body = start(c, "t-02").json()
    assert body["lesson"] == "t-02" and body["items"][0]["text"] == "Two a."
    assert states(c)["t-01"] == "done" and states(c)["t-02"] == "current"


def test_a_locked_or_unknown_lesson_cannot_be_started(make):
    c, _ = make()
    c.get("/api/run")
    assert start(c, "t-04").status_code == 409
    assert start(c, "t-02").status_code == 409
    assert start(c, "nope").status_code == 400


def test_starting_over_keeps_the_old_attempt_in_the_progress_file(make):
    c, progress = make()
    c.get("/api/run")
    c.post("/api/next")
    before = Store(progress)
    old = before.latest("t-01")[0]
    old_items = before.items(old)
    body = start(c, "t-01").json()
    assert [i["text"] for i in body["items"]] == ["One a."] and body["run_id"] != old
    after = Store(progress)
    assert after.items(old) == old_items
    assert after.latest("t-01")[0] == body["run_id"]


def test_a_finished_lesson_can_be_sat_again_after_later_ones(make):
    c, _ = make()
    finish_foundation(c)
    start(c, "t-01")
    assert states(c)["t-01"] == "current" and states(c)["t-02"] == "done" and states(c)["t-03"] == "open"


def test_the_next_lesson_is_the_first_open_one_in_course_order(make):
    c, _ = make()
    c.get("/api/run")
    finish(c)
    assert c.post("/api/run/new", json={"next": True}).json()["lesson"] == "t-02"
    finish(c)
    assert c.post("/api/run/new", json={"next": True}).json()["lesson"] == "t-04"


def test_an_opening_cold_check_borrowed_from_a_lesson_not_met_is_skipped(make):
    c, _ = make()
    finish_foundation(c)
    body = start(c, "t-03").json()
    assert body["items"][0]["text"] == "Three a."


def test_an_opening_cold_check_is_played_once_its_thoughts_are_met(make):
    c, _ = make()
    finish_foundation(c)
    start(c, "t-04")
    finish(c)
    body = start(c, "t-03").json()
    assert body["items"][0]["text"] == "Borrowed cold." and body["pending"]["mode"] == "answer"


def test_reading_the_outline_changes_nothing(make):
    c, progress = make()
    before = c.get("/api/run").json()
    c.get("/api/course")
    c.get("/api/course")
    assert c.get("/api/run").json() == before
    assert Store(progress).events() == []
