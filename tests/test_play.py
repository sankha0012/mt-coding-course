from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from checker.lesson import load_strand
from player.app import make_app
from player.store import Store

ROOT = Path(__file__).parent.parent
CONTENT = ROOT / "content" / "sql"


@pytest.fixture
def lesson():
    return load_strand(CONTENT)[1][0][1]


def play(client, lesson, miss_first):
    """Play the whole lesson through the API. Returns the final view."""
    body = client.get("/api/run").json()
    for _ in range(2000):
        pending = body["pending"]
        if pending["mode"] == "done":
            return body
        if pending["mode"] in ("run", "continue"):
            body = client.post("/api/next").json()
            continue
        step = lesson[pending["step"] - 1]
        model = (step["return"] if pending["variant"] == "return" else step)["model"]
        if miss_first and step.get("kind") != "cold-check":
            body = client.post("/api/answer", json={"sql": "SELECT 1"}).json()
            assert body["pending"]["mode"] == "answer"
        body = client.post("/api/answer", json={"sql": model}).json()
    raise AssertionError("the lesson never finished")


def test_all_of_lesson_1_can_be_played_with_the_model_answers(data_dir, tmp_path, lesson):
    client = TestClient(make_app(CONTENT, data_dir, tmp_path))
    body = play(client, lesson, miss_first=False)
    assert body["pending"] == {"mode": "done"}
    events = Store(tmp_path).events()
    assert events and all(e["outcome"] in ("correct", "shown") for e in events)
    assert all(e["variant"] == "main" for e in events)


def test_lesson_1_can_be_played_missing_every_step_once(data_dir, tmp_path, lesson):
    client = TestClient(make_app(CONTENT, data_dir, tmp_path))
    body = play(client, lesson, miss_first=True)
    assert body["pending"] == {"mode": "done"}
    events = Store(tmp_path).events()
    returns = [e for e in events if e["variant"] == "return" and e["outcome"] == "correct"]
    with_return = [s for s in lesson if "return" in s]
    assert len(returns) == len(with_return) == 15
    assert not any("wrong" in str(i).lower() for i in body["items"] if i["type"] == "teacher")


def test_sitting_again_starts_a_new_run_and_keeps_the_old(data_dir, tmp_path, lesson):
    client = TestClient(make_app(CONTENT, data_dir, tmp_path))
    first = play(client, lesson, miss_first=False)
    second = client.post("/api/run/new").json()
    assert second["run_id"] > first["run_id"]
    assert second["pending"]["mode"] == "run"
    assert Store(tmp_path).items(first["run_id"]) == first["items"]
