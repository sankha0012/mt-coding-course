from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from checker.lesson import load_content
from player.app import make_app
from player.store import Store

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content"


@pytest.fixture
def lessons():
    return dict(load_content(CONTENT)[1])


def play(client, lessons, miss_first):
    """Play the whole course through the API, lesson after lesson. Returns the final view."""
    body = client.get("/api/run").json()
    for _ in range(20000):
        pending = body["pending"]
        if pending["mode"] == "done":
            if not pending["next"]:
                return body
            body = client.post("/api/run/new", json={"next": True}).json()
        elif pending["mode"] in ("run", "continue"):
            body = client.post("/api/next").json()
        else:
            step = lessons[body["lesson"]][pending["step"] - 1]
            model = (step["return"] if pending["variant"] == "return" else step)["model"]
            if miss_first and step.get("kind") != "cold-check":
                body = client.post("/api/answer", json={"sql": "SELECT 1"}).json()
                assert body["pending"]["mode"] == "answer"
            body = client.post("/api/answer", json={"sql": model}).json()
    raise AssertionError("the course never finished")


def test_the_whole_course_can_be_played_with_the_model_answers(data_dir, tmp_path, lessons):
    client = TestClient(make_app(CONTENT, data_dir, tmp_path))
    body = play(client, lessons, miss_first=False)
    assert body["pending"] == {"mode": "done", "next": False}
    events = Store(tmp_path).events()
    assert events and all(e["outcome"] in ("correct", "shown") for e in events)
    assert all(e["variant"] == "main" for e in events)
    played = {e["lesson"] for e in events}
    assert played <= set(lessons) and len(played) >= 2


def test_the_whole_course_can_be_played_missing_every_step_once(data_dir, tmp_path, lessons):
    client = TestClient(make_app(CONTENT, data_dir, tmp_path))
    body = play(client, lessons, miss_first=True)
    assert body["pending"] == {"mode": "done", "next": False}
    events = Store(tmp_path).events()
    returns = [e for e in events if e["variant"] == "return" and e["outcome"] == "correct"]
    played = {e["lesson"] for e in events}
    with_return = [s for name, steps in lessons.items() if name in played for s in steps if "return" in s]
    assert len(returns) == len(with_return) > 0
    assert not any("wrong" in str(i).lower() for i in body["items"] if i["type"] == "teacher")


def test_sitting_again_starts_a_new_run_and_keeps_the_old(data_dir, tmp_path, lessons):
    client = TestClient(make_app(CONTENT, data_dir, tmp_path))
    first = play(client, lessons, miss_first=False)
    second = client.post("/api/run/new").json()
    assert second["run_id"] > first["run_id"]
    assert second["lesson"] == first["lesson"]
    assert second["pending"]["mode"] in ("run", "answer", "continue")
    assert Store(tmp_path).items(first["run_id"]) == first["items"]
