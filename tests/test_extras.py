from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from checker.__main__ import main
from checker.lesson import extras_needed_by_core, is_course, lesson_titles, load_content, prerequisites
from player.app import make_app

ROOT = Path(__file__).parent.parent


def recap(text, **more):
    return {"kind": "recap", "text": text, **more}


def course(root, lessons, extras=(), core_requires_extra=False):
    """lessons and extras: (strand, file, name, stage, steps). Writes them with a manifest and returns the root."""
    entries = []
    for strand, f, name, stage, steps in [*lessons, *extras]:
        (root / strand).mkdir(parents=True, exist_ok=True)
        (root / strand / f"{f}.yaml").write_text(yaml.safe_dump({
            "lesson": name, "title": name.upper(), "strand": strand, "stage": stage, "steps": steps}), encoding="utf-8")
        entries.append(f"{strand}/{f}")
    manifest = {"course": entries[:len(lessons)]}
    if extras:
        manifest["extras"] = entries[len(lessons):]
    (root / "course.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    (root / "ui.yaml").write_text((ROOT / "content" / "ui.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    return root


CORE = [("sql", "lesson-01", "s-1", 1, [recap("S one.", new=["a"])]),
        ("sql", "lesson-02", "s-2", 1, [recap("S two.", new=["b"])]),
        ("py", "lesson-01", "p-1", 1, [recap("P one.", new=["p"], requires=["b"])])]
EXTRA = [("mg", "lesson-01", "m-1", 1, [recap("M one.", new=["m"], requires=["b"])]),
         ("mg", "lesson-02", "m-2", 1, [recap("M two.")])]


def test_extras_are_loaded_after_the_core_in_order(tmp_path):
    course(tmp_path, CORE, EXTRA)
    _, lessons = load_content(tmp_path)
    assert [n for n, _ in lessons] == ["s-1", "s-2", "p-1", "m-1", "m-2"]


def test_the_titles_say_which_lessons_are_extras(tmp_path):
    course(tmp_path, CORE, EXTRA)
    assert [(t["lesson"], t["extra"]) for t in lesson_titles(tmp_path)] == [
        ("s-1", False), ("s-2", False), ("p-1", False), ("m-1", True), ("m-2", True)]


def test_a_course_with_no_extras_loads_as_before(tmp_path):
    course(tmp_path, CORE)
    assert is_course(tmp_path) and not any(t["extra"] for t in lesson_titles(tmp_path))


def test_an_extra_opens_after_the_foundation_it_is_built_on(tmp_path):
    course(tmp_path, CORE, EXTRA)
    pre = prerequisites(tmp_path)
    assert pre["m-1"] == {"s-1", "s-2"} and pre["m-2"] == {"m-1"}


def test_a_core_lesson_may_not_need_a_thought_from_an_extra(tmp_path):
    core = [*CORE, ("pd", "lesson-01", "d-1", 1, [recap("D.", requires=["m"])])]
    course(tmp_path, core, EXTRA)
    assert extras_needed_by_core(tmp_path) == [("d-1", "m", "m-1")]


def test_the_checker_fails_a_course_whose_core_needs_an_extra(tmp_path, data_dir, capsys):
    core = [*CORE, ("pd", "lesson-01", "d-1", 1, [recap("D.", requires=["m"])])]
    course(tmp_path, core, EXTRA)
    assert main([str(tmp_path), "--data", str(data_dir)]) == 1
    assert "FAIL d-1: requires thought 'm', introduced by m-1, an optional extra" in capsys.readouterr().out


def test_a_course_whose_extras_lean_on_the_core_passes_that_check(tmp_path, data_dir, capsys):
    course(tmp_path, CORE, EXTRA)
    main([str(tmp_path), "--data", str(data_dir)])
    assert "optional extra" not in capsys.readouterr().out


@pytest.fixture
def client(tmp_path, data_dir):
    course(tmp_path / "content", CORE, EXTRA)
    return TestClient(make_app(tmp_path / "content", data_dir, tmp_path / "progress"))


def finish(c):
    body = c.get("/api/run").json()
    while body["pending"]["mode"] != "done":
        body = c.post("/api/next").json()
    return body


def start(c, lesson):
    return c.post("/api/lesson/start", json={"lesson": lesson})


def lessons(c):
    return {i["lesson"]: i for i in c.get("/api/course").json()["lessons"]}


def test_the_course_view_marks_extras_and_names_their_strand(client):
    body = client.get("/api/course").json()
    assert [i["extra"] for i in body["lessons"]] == [False, False, False, True, True]
    assert "mg" in [s["id"] for s in body["strands"]]
    assert body["extras"]["title"] and body["extras"]["note"]


def test_an_extra_can_be_started_as_soon_as_its_foundation_is_done(client):
    client.get("/api/run")
    finish(client)
    start(client, "s-2")
    finish(client)
    assert lessons(client)["m-1"]["state"] == "open"
    assert start(client, "m-1").json()["items"][0]["text"] == "M one."


def test_an_extra_is_locked_until_then(client):
    client.get("/api/run")
    assert lessons(client)["m-1"]["state"] == "locked"
    assert start(client, "m-1").status_code == 409


def test_the_next_lesson_is_never_an_extra_while_core_remains(client):
    client.get("/api/run")
    finish(client)
    start(client, "s-2")
    finish(client)
    assert client.post("/api/run/new", json={"next": True}).json()["lesson"] == "p-1"


def test_when_the_whole_core_is_finished_the_extras_are_offered(client):
    client.get("/api/run")
    finish(client)
    start(client, "s-2")
    finish(client)
    start(client, "p-1")
    done = finish(client)
    assert done["pending"] == {"mode": "done", "next": True}
    assert client.post("/api/run/new", json={"next": True}).json()["lesson"] == "m-1"


def test_after_the_last_extra_there_is_nothing_next(client):
    client.get("/api/run")
    finish(client)
    start(client, "s-2")
    finish(client)
    start(client, "p-1")
    finish(client)
    start(client, "m-1")
    finish(client)
    start(client, "m-2")
    assert finish(client)["pending"] == {"mode": "done", "next": False}
