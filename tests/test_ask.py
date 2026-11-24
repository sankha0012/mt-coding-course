import json
import sqlite3
from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from player import llm
from player.app import make_app

ROOT = Path(__file__).parent.parent
UI = yaml.safe_load((ROOT / "content" / "ui.yaml").read_text(encoding="utf-8"))
MODEL = "SELECT COUNT(*) FROM restaurants"


@pytest.fixture
def make(tmp_path, data_dir):
    """A one-lesson course waiting at a typed step. Returns build(chat) -> (client, progress folder)."""
    content = tmp_path / "content"
    (content / "sql").mkdir(parents=True)
    (content / "ui.yaml").write_text((ROOT / "content" / "ui.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    (content / "sql" / "thoughts.yaml").write_text(
        yaml.safe_dump({"thoughts": {"count-rows": "Count the rows of a table."}}), encoding="utf-8")
    (content / "sql" / "lesson-01.yaml").write_text(yaml.safe_dump({"lesson": "t-01", "steps": [
        {"kind": "give", "new": ["count-rows"], "text": "We count rows.", "shows": ["SELECT COUNT(*) FROM orders"]},
        {"kind": "ask", "requires": ["count-rows"], "text": "How many restaurants?", "model": MODEL,
         "narration": ["a", "b"]}]}), encoding="utf-8")

    def build(chat, providers=lambda: ["gemini", "groq"]):
        c = TestClient(make_app(content / "sql", data_dir, tmp_path / "progress", chat=chat, providers=providers))
        c.get("/api/run")
        c.post("/api/next")
        c.post("/api/next")
        assert c.get("/api/run").json()["pending"]["mode"] == "answer"
        return c, tmp_path / "progress"
    return build


def fake_chat(reply="Counting is simple.", provider="gemini"):
    calls = []

    def chat(messages, provider=None):
        calls.append((messages, provider))
        return reply, provider or "gemini"
    chat.calls = calls
    return chat


def unavailable(messages, provider=None):
    raise llm.Unavailable("no key set")


def test_the_persona_lines_exist_and_have_no_em_dash():
    for key in ("ask_persona", "ask_unavailable", "ask_guarded"):
        assert UI[key].strip() and "—" not in UI[key]


def test_the_menu_lists_the_providers_that_have_a_key(make):
    c, _ = make(fake_chat(), providers=lambda: ["groq"])
    assert c.get("/api/providers").json() == {"providers": ["groq"]}


def test_a_question_gets_a_reply_and_is_kept(make):
    c, progress = make(fake_chat("A count is a number of rows."))
    r = c.post("/api/ask", json={"question": "what is count?", "thread": []}).json()
    assert r == {"reply": "A count is a number of rows.", "ok": True, "guarded": False}
    [row] = sqlite3.connect(progress / "progress.db").execute(
        "SELECT step, question, reply, provider, guarded FROM questions").fetchall()
    assert row == (2, "what is count?", "A count is a number of rows.", "gemini", 0)


def test_the_chosen_provider_reaches_the_model_call(make):
    chat = fake_chat()
    c, progress = make(chat)
    c.post("/api/ask", json={"question": "q", "thread": [], "provider": "groq"})
    assert chat.calls[0][1] == "groq"
    assert sqlite3.connect(progress / "progress.db").execute("SELECT provider FROM questions").fetchone() == ("groq",)


def test_an_unknown_provider_is_refused(make):
    c, _ = make(fake_chat())
    assert c.post("/api/ask", json={"question": "q", "thread": [], "provider": "bing"}).status_code == 400


def test_the_model_answer_never_reaches_the_model(make):
    chat = fake_chat()
    c, _ = make(chat)
    c.post("/api/ask", json={"question": "help", "thread": []})
    messages = chat.calls[0][0]
    system = messages[0]["content"]
    assert MODEL not in json.dumps(messages)
    for part in ("Count the rows of a table.", "We count rows.", "How many restaurants?", "restaurants: "):
        assert part in system


def test_a_reply_that_solves_the_step_is_replaced(make):
    c, progress = make(fake_chat(f"Try `{MODEL}` and see."))
    r = c.post("/api/ask", json={"question": "just tell me", "thread": []}).json()
    assert r["guarded"] is True and r["reply"] == UI["ask_guarded"]
    stored = sqlite3.connect(progress / "progress.db").execute("SELECT reply, guarded FROM questions").fetchone()
    assert stored == (UI["ask_guarded"], 1)


def test_a_reply_with_other_code_passes(make):
    c, _ = make(fake_chat("For example `SELECT COUNT(*) FROM couriers` counts couriers."))
    r = c.post("/api/ask", json={"question": "example?", "thread": []}).json()
    assert r["guarded"] is False and "couriers" in r["reply"]


def test_a_question_leaves_the_lesson_alone(make):
    c, progress = make(fake_chat())
    db = sqlite3.connect(progress / "progress.db")

    def snapshot():
        return (c.get("/api/run").json(), db.execute("SELECT state_json FROM runs").fetchall(),
                db.execute("SELECT COUNT(*) FROM events").fetchone())
    before = snapshot()
    c.post("/api/ask", json={"question": "why?", "thread": []})
    c.post("/api/ask", json={"question": "and?", "thread": []})
    assert snapshot() == before


def test_no_provider_gives_a_calm_line_and_stores_nothing(make):
    c, progress = make(unavailable)
    r = c.post("/api/ask", json={"question": "hello", "thread": []}).json()
    assert r == {"reply": UI["ask_unavailable"], "ok": False}
    assert sqlite3.connect(progress / "progress.db").execute("SELECT COUNT(*) FROM questions").fetchone()[0] == 0


def test_the_thread_is_passed_on(make):
    chat = fake_chat()
    c, _ = make(chat)
    thread = [{"role": "user", "text": "q1"}, {"role": "teacher", "text": "a1"}]
    c.post("/api/ask", json={"question": "q2", "thread": thread})
    assert [m["role"] for m in chat.calls[0][0]] == ["system", "user", "assistant", "user"]


def test_a_miss_adds_the_attempt_to_the_context(make):
    chat = fake_chat()
    c, _ = make(chat)
    c.post("/api/answer", json={"sql": "SELECT COUNT(*) FROM couriers"})
    c.post("/api/ask", json={"question": "why not?", "thread": []})
    assert "SELECT COUNT(*) FROM couriers" in chat.calls[0][0][0]["content"]


def test_empty_and_huge_questions_are_refused(make):
    c, _ = make(fake_chat())
    assert c.post("/api/ask", json={"question": "  ", "thread": []}).status_code == 400
    assert c.post("/api/ask", json={"question": "x" * 2001, "thread": []}).status_code == 400


def test_the_key_never_leaves_the_server(make):
    key = "SECRET-KEY-123"
    sent = []

    class Reply:
        def read(self):
            return json.dumps({"choices": [{"message": {"content": "A count."}}]}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def urlopen(req, timeout=None):
        sent.append(req)
        return Reply()

    def chat(messages, provider=None):
        return llm.chat(messages, {"GEMINI_API_KEY": key}, urlopen, provider=provider)
    c, progress = make(chat)
    r = c.post("/api/ask", json={"question": "what is count?", "thread": []})
    assert r.status_code == 200 and key not in r.text
    assert key not in sent[0].data.decode()
    assert key not in "\n".join(sqlite3.connect(progress / "progress.db").iterdump())
    assert key not in c.get("/api/providers").text
