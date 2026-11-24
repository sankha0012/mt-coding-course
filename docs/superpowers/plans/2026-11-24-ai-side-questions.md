# Ask the teacher: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The learner can ask a question in words during a lesson. A side thread answers it, the lesson stays frozen, and the learner confirms to go back.

**Architecture:** A small `player/llm.py` calls Gemini first and Groq as fallback over their OpenAI-style endpoints with `urllib`. `player/ai.py` builds what the model sees (never a step's model answer) and finds code in a reply. The engine gains one read-only method, `solves`, so a reply that would solve the step is replaced. `Player.ask` ties these together without touching lesson state. The screen gets Code and Ask tabs and a tinted side thread.

**Tech Stack:** Python 3.12, FastAPI, SQLite, stdlib `urllib`, plain JavaScript. No new dependency.

**Spec:** `docs/superpowers/specs/2026-11-24-ai-side-questions-design.md`

## Global Constraints

- The model never receives a step's `model`, `wrong`, `walk`, `return`, `accepts` or any expected output.
- A side question never changes engine state, the ladder, the returns queue, or the `events` table.
- No timer, score, streak or count of questions is shown to the learner. The word "wrong" is never shown.
- The teacher persona and the calm lines live in `content/ui.yaml`, not in Python (rule 10).
- Keys come from the environment or a git-ignored `.env`. A key never appears in a response, a log line, the progress file, a test fixture or a commit.
- No em dashes in docs, lessons or `ui.yaml`.
- `progress/progress.db` is never deleted or overwritten. Tests use a temporary folder. The schema change is additive (`CREATE TABLE IF NOT EXISTS`).
- No new dependency. Standard library only for HTTP.
- Provider order: Gemini first, Groq as fallback. Replies are not streamed.
- Run `uv run pytest` and `uv run python -m checker content` before finishing. Do not edit lessons.

---

### Task 0: Commit the pending pane and cache fixes

The working tree holds earlier, finished changes: the side-by-side "Try your own code" pane and the no-cache header. Commit them on their own so this feature starts from a clean tree.

**Files:**
- Modify (already edited): `player/app.py`, `player/web/app.js`, `player/web/index.html`, `player/web/style.css`, `tests/test_app.py`

- [ ] **Step 1: Check the tree holds only those files**

Run: `git status --short`
Expected: exactly the five files above, as ` M`. Anything else: stop and ask.

- [ ] **Step 2: Run the app tests**

Run: `uv run pytest -q tests/test_app.py`
Expected: all pass.

- [ ] **Step 3: Commit**

```bash
git add player/app.py player/web tests/test_app.py
git commit -m "Open the try-it panel to the right with a draggable divider, and never cache the page

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 1: The model call (`player/llm.py`)

**Files:**
- Create: `player/llm.py`
- Create: `tests/test_llm.py`
- Modify: `.gitignore` (add `.env`)
- Create: `.env.example`

**Interfaces:**
- Produces:
  - `class Unavailable(Exception)`, raised when no provider answered. Its message lists provider names or "no key set", never a key.
  - `settings(env=None, env_file=ENV_FILE) -> dict[str, str]`: the `.env` file under the given mapping (or `os.environ` when `env` is None). The environment wins.
  - `chat(messages, cfg=None, urlopen=urllib.request.urlopen, timeout=30) -> tuple[str, str]`: `(reply text, provider name)`. `messages` is `[{"role": "system"|"user"|"assistant", "content": str}]`. Tries `cfg["AI_ORDER"]` (default `"gemini,groq"`), skipping providers without a key.
  - `PROVIDERS`: dict of `gemini` and `groq` with `url`, `key`, `model`, `default`.

- [ ] **Step 1: Write the failing tests**

`tests/test_llm.py`:

```python
import json
import urllib.error

import pytest

from player import llm


class Reply:
    def __init__(self, text):
        self.body = json.dumps({"choices": [{"message": {"content": text}}]}).encode()

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def fake(*outcomes):
    """Each call takes the next outcome: a string is a reply, an exception is raised."""
    calls = []

    def urlopen(req, timeout=None):
        calls.append(req)
        out = outcomes[len(calls) - 1]
        if isinstance(out, Exception):
            raise out
        return Reply(out)
    urlopen.calls = calls
    return urlopen


MSGS = [{"role": "user", "content": "hi"}]
BOTH = {"GEMINI_API_KEY": "gem-key", "GROQ_API_KEY": "groq-key"}


def too_many():
    return urllib.error.HTTPError("https://x", 429, "Too Many Requests", {}, None)


def test_gemini_is_asked_first():
    u = fake("from gemini")
    assert llm.chat(MSGS, BOTH, u) == ("from gemini", "gemini")
    assert "generativelanguage" in u.calls[0].full_url


def test_the_request_carries_the_key_the_model_and_the_messages():
    u = fake("ok")
    llm.chat(MSGS, {**BOTH, "GEMINI_MODEL": "my-model"}, u)
    req = u.calls[0]
    assert req.get_header("Authorization") == "Bearer gem-key"
    body = json.loads(req.data)
    assert body["model"] == "my-model" and body["messages"] == MSGS
    assert "gem-key" not in req.data.decode()


def test_a_failing_gemini_falls_back_to_groq():
    u = fake(too_many(), "from groq")
    assert llm.chat(MSGS, BOTH, u) == ("from groq", "groq")
    assert "groq.com" in u.calls[1].full_url


def test_an_empty_reply_counts_as_a_failure():
    u = fake("  ", "from groq")
    assert llm.chat(MSGS, BOTH, u)[1] == "groq"


def test_both_failing_raises_without_naming_a_key():
    u = fake(too_many(), OSError("down"))
    with pytest.raises(llm.Unavailable) as e:
        llm.chat(MSGS, BOTH, u)
    assert "gem-key" not in str(e.value) and "groq-key" not in str(e.value)


def test_no_key_makes_no_call():
    u = fake()
    with pytest.raises(llm.Unavailable, match="no key set"):
        llm.chat(MSGS, {}, u)
    assert u.calls == []


def test_a_provider_without_a_key_is_skipped():
    u = fake("from groq")
    assert llm.chat(MSGS, {"GROQ_API_KEY": "groq-key"}, u)[1] == "groq"


def test_the_order_can_be_changed():
    u = fake("from groq")
    assert llm.chat(MSGS, {**BOTH, "AI_ORDER": "groq,gemini"}, u)[1] == "groq"


def test_settings_read_the_env_file_and_the_environment_wins(tmp_path):
    f = tmp_path / ".env"
    f.write_text("# comment\nGEMINI_API_KEY=from-file\nexport GROQ_API_KEY='quoted'\n\nAI_ORDER = groq\n")
    cfg = llm.settings({"GEMINI_API_KEY": "from-env"}, f)
    assert cfg["GEMINI_API_KEY"] == "from-env"
    assert cfg["GROQ_API_KEY"] == "quoted" and cfg["AI_ORDER"] == "groq"


def test_settings_without_a_file(tmp_path):
    assert llm.settings({"A": "1"}, tmp_path / "missing") == {"A": "1"}
```

- [ ] **Step 2: Run to see them fail**

Run: `uv run pytest -q tests/test_llm.py`
Expected: FAIL at import (`cannot import name 'llm'`).

- [ ] **Step 3: Write `player/llm.py`**

```python
"""One call to a chat model, over the OpenAI-style endpoints that Gemini and Groq both offer."""
import json
import os
import urllib.request
from pathlib import Path

ENV_FILE = Path(__file__).parent.parent / ".env"

# The default model names change often. They are set in .env as GEMINI_MODEL and GROQ_MODEL.
PROVIDERS = {
    "gemini": {"url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
               "key": "GEMINI_API_KEY", "model": "GEMINI_MODEL", "default": "gemini-2.5-flash"},
    "groq": {"url": "https://api.groq.com/openai/v1/chat/completions",
             "key": "GROQ_API_KEY", "model": "GROQ_MODEL", "default": "llama-3.3-70b-versatile"},
}


class Unavailable(Exception):
    """No provider answered. The message names providers, never a key."""


def settings(env=None, env_file=ENV_FILE):
    """The .env file (KEY=VALUE lines, # comments) under the environment, which wins."""
    cfg = {}
    if env_file and Path(env_file).is_file():
        for line in Path(env_file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                cfg[key.removeprefix("export ").strip()] = value.strip().strip("\"'")
    cfg.update(os.environ if env is None else env)
    return cfg


def chat(messages, cfg=None, urlopen=urllib.request.urlopen, timeout=30):
    """Returns (reply, provider). Tries the providers of AI_ORDER (default gemini, groq) that have a key,
    and moves on to the next after any failure or an empty reply."""
    cfg = settings() if cfg is None else cfg
    order = [n.strip() for n in cfg.get("AI_ORDER", "gemini,groq").split(",") if n.strip() in PROVIDERS]
    tried = []
    for name in order:
        p, key = PROVIDERS[name], cfg.get(PROVIDERS[name]["key"])
        if not key:
            continue
        tried.append(name)
        body = json.dumps({"model": cfg.get(p["model"]) or p["default"], "messages": messages,
                           "temperature": 0.3, "max_tokens": 1500}).encode()
        req = urllib.request.Request(p["url"], body, {
            "Content-Type": "application/json", "Authorization": f"Bearer {key}",
            "User-Agent": "mt-coding-course"})
        try:
            with urlopen(req, timeout=timeout) as r:
                text = json.load(r)["choices"][0]["message"]["content"]
        except (OSError, ValueError, KeyError, IndexError, TypeError):
            continue
        if text and text.strip():
            return text.strip(), name
    raise Unavailable(", ".join(tried) if tried else "no key set")
```

- [ ] **Step 4: Keep secrets out of git**

Append `.env` to `.gitignore` (its own line). Create `.env.example`:

```
# Copy to .env and fill in. .env is never committed.
GEMINI_API_KEY=
GROQ_API_KEY=
# Optional. Gemini is tried first. Change the order or the models here.
# AI_ORDER=gemini,groq
# GEMINI_MODEL=
# GROQ_MODEL=
```

- [ ] **Step 5: Run the tests**

Run: `uv run pytest -q tests/test_llm.py`
Expected: 10 passed.

- [ ] **Step 6: Commit**

```bash
git add player/llm.py tests/test_llm.py .gitignore .env.example
git commit -m "Add the model call: Gemini first, Groq as fallback, over urllib

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 2: What the model sees, the guard, and `Engine.solves`

**Files:**
- Create: `player/ai.py`
- Create: `tests/test_ai.py`
- Modify: `player/engine.py` (add `solves` after `answer`)
- Modify: `tests/test_engine.py` (add one test at the end; read the file's imports first and reuse its fixtures)

**Interfaces:**
- Produces:
  - `ai.thought_lines(thoughts: dict, ids: list[str]) -> list[str]`: the text of each id in order. A thought is a string or `{"text": ...}`. Unknown ids are skipped.
  - `ai.schema_lines(folder) -> list[str]`: one `"name: col, col"` line per `*.csv` in the folder. No rows.
  - `ai.attempt_text(items: list[dict]) -> str`: the last learner item's code and what it gave (an error, printed text, or the column names and first five rows). Empty string when there is none.
  - `ai.build_messages(ui, thoughts, teacher_lines, prompt, attempt, schema, thread, question) -> list[dict]`: system message first, then up to 10 thread messages (`{"role": "user"|"teacher", "text"}` become `user`/`assistant`), then the question as a user message. `ui` needs the key `ask_persona`.
  - `ai.code_candidates(reply: str, limit=10) -> list[str]`: fenced blocks first, then inline code spans, stripped, non-empty.
  - `Engine.solves(st, code) -> bool`: true only when `st["phase"] == "answer"` and the code would be accepted as the answer to the step waiting (main or return variant).
- Consumes: `Engine._cur`, `Engine._correct`, `Runner.run`.

- [ ] **Step 1: Write the failing tests for `ai`**

`tests/test_ai.py`:

```python
from player import ai

UI = {"ask_persona": "PERSONA. Never write the answer."}


def test_thought_lines_keep_order_and_skip_unknown():
    thoughts = {"a": "Count rows.", "b": {"text": "Sort rows.", "grade": "shape"}}
    assert ai.thought_lines(thoughts, ["b", "zzz", "a"]) == ["Sort rows.", "Count rows."]


def test_schema_lines_name_files_and_columns_only(tmp_path):
    (tmp_path / "orders.csv").write_text("order_id,subtotal\n1,9.5\n2,7\n")
    (tmp_path / "notes.txt").write_text("ignored")
    assert ai.schema_lines(tmp_path) == ["orders: order_id, subtotal"]


def test_attempt_text_for_sql_and_for_python():
    sql = [{"type": "teacher", "text": "t"}, {"type": "learner", "sql": "SELECT 1", "lang": "sql"},
           {"type": "result", "columns": ["x"], "rows": [[1]], "total": 1}]
    text = ai.attempt_text(sql)
    assert "SELECT 1" in text and "x" in text and "1" in text
    py = [{"type": "learner", "sql": "print(1)", "lang": "python"},
          {"type": "result", "lang": "python", "text": "1\n", "error": None}]
    assert "print(1)" in ai.attempt_text(py) and "1" in ai.attempt_text(py)
    err = [{"type": "learner", "sql": "SELECT", "lang": "sql"},
           {"type": "result", "error": "no such column", "columns": [], "rows": [], "total": 0}]
    assert "no such column" in ai.attempt_text(err)
    assert ai.attempt_text([{"type": "teacher", "text": "t"}]) == ""


def test_the_messages_carry_the_context_in_the_system_message():
    msgs = ai.build_messages(UI, ["Count rows."], ["Welcome.", "How many?"], "How many couriers?",
                             "SELECT 1", ["couriers: city"], [], "what is count?")
    system = msgs[0]["content"]
    assert msgs[0]["role"] == "system"
    for part in ("PERSONA", "Count rows.", "Welcome.", "How many couriers?", "SELECT 1", "couriers: city"):
        assert part in system
    assert msgs[-1] == {"role": "user", "content": "what is count?"}


def test_the_thread_comes_between_the_system_message_and_the_question():
    thread = [{"role": "user", "text": "q1"}, {"role": "teacher", "text": "a1"}]
    msgs = ai.build_messages(UI, [], [], "p", "", [], thread, "q2")
    assert [m["role"] for m in msgs] == ["system", "user", "assistant", "user"]
    assert [m["content"] for m in msgs[1:]] == ["q1", "a1", "q2"]


def test_no_attempt_leaves_that_part_out():
    msgs = ai.build_messages(UI, [], [], "p", "", [], [], "q")
    assert "attempt" not in msgs[0]["content"]


def test_code_candidates_find_fences_and_inline_spans():
    reply = "Try this:\n```sql\nSELECT 1\n```\nor `SELECT 2` too. Also ```SELECT 3```."
    assert ai.code_candidates(reply)[:2] == ["SELECT 1", "SELECT 2"]
    assert "SELECT 3" in ai.code_candidates(reply)
    assert ai.code_candidates("no code here") == []
```

- [ ] **Step 2: Run to see them fail**

Run: `uv run pytest -q tests/test_ai.py`
Expected: FAIL at import (`cannot import name 'ai'`).

- [ ] **Step 3: Write `player/ai.py`**

```python
"""What the teacher tells the model, and the pieces of the guard. Nothing here ever receives a step's
model answer, wrong answers, walk or return: the caller passes only what the learner has already seen."""
import csv
import re
from pathlib import Path

FENCE = re.compile(r"```[^\n]*\n(.*?)```", re.S)
INLINE = re.compile(r"`([^`\n]+)`")


def thought_lines(thoughts, ids):
    out = []
    for i in ids:
        t = thoughts.get(i)
        text = t.get("text") if isinstance(t, dict) else t
        if text:
            out.append(text)
    return out


def schema_lines(folder):
    lines = []
    for f in sorted(Path(folder).glob("*.csv")):
        with open(f, newline="", encoding="utf-8") as h:
            header = next(csv.reader(h), [])
        lines.append(f"{f.stem}: {', '.join(header)}")
    return lines


def attempt_text(items):
    """The last thing the learner typed, and what it gave."""
    at = next((i for i in range(len(items) - 1, -1, -1) if items[i]["type"] == "learner"), None)
    if at is None:
        return ""
    out = f"Typed:\n{items[at]['sql']}"
    res = items[at + 1] if at + 1 < len(items) and items[at + 1]["type"] == "result" else None
    if res is None:
        return out
    if res.get("error"):
        return out + f"\nGave an error: {res['error']}"
    if res.get("lang") == "python":
        return out + f"\nPrinted:\n{res.get('text') or '(nothing)'}"
    rows = "\n".join(", ".join(str(v) for v in r) for r in res["rows"][:5])
    return out + f"\nGave columns {', '.join(res['columns'])} and rows:\n{rows}"


def build_messages(ui, thoughts, teacher_lines, prompt, attempt, schema, thread, question):
    parts = [ui["ask_persona"].strip(),
             "Thoughts the learner has met, in order:\n" + "\n".join("- " + t for t in thoughts),
             "The lesson so far:\n" + "\n".join(line[:1500] for line in teacher_lines[-12:]),
             "The step now waiting:\n" + prompt[:1500],
             "Tables and columns:\n" + "\n".join(schema)]
    if attempt:
        parts.append("The learner's last attempt at this step:\n" + attempt[:1500])
    earlier = [{"role": "user" if m["role"] == "user" else "assistant", "content": m["text"]}
               for m in thread[-10:]]
    return [{"role": "system", "content": "\n\n".join(parts)}, *earlier,
            {"role": "user", "content": question}]


def code_candidates(reply, limit=10):
    blocks = [b.strip() for b in FENCE.findall(reply)]
    spans = [s.strip() for s in INLINE.findall(FENCE.sub(" ", reply))]
    return [c for c in blocks + spans if c][:limit]
```

- [ ] **Step 4: Run the `ai` tests**

Run: `uv run pytest -q tests/test_ai.py`
Expected: 7 passed.

- [ ] **Step 5: Write the failing test for `Engine.solves`**

Read the top of `tests/test_engine.py` for its imports, then add at the end:

```python
def test_solves_is_true_only_for_code_the_step_would_accept(make_engine, reach):
    e = make_engine()
    st = reach(e, 2)
    assert e.solves(st, "SELECT COUNT(*) FROM restaurants") is True
    assert e.solves(st, "select count(*)  from restaurants;") is True
    assert e.solves(st, "SELECT COUNT(*) FROM couriers") is False
    assert e.solves(st, "SELECT") is False
    assert e.solves(e.start()[0], "SELECT COUNT(*) FROM restaurants") is False  # not waiting for an answer


def test_solves_does_not_change_the_state(make_engine, reach):
    import copy
    e = make_engine()
    st = reach(e, 2)
    before = copy.deepcopy(st)
    e.solves(st, "SELECT COUNT(*) FROM restaurants")
    assert st == before
```

- [ ] **Step 6: Run to see the engine tests fail**

Run: `uv run pytest -q tests/test_engine.py -k solves`
Expected: FAIL with `AttributeError: 'Engine' object has no attribute 'solves'`.

- [ ] **Step 7: Add `solves` to `player/engine.py`**

Insert after the `answer` method (before `# ---- moving through the lesson`):

```python
    def solves(self, st, code):
        """Would this code be taken as the answer to the step now waiting? Read-only. The guard on side
        questions uses it, so a reply that gives the answer away can be replaced."""
        if st["phase"] != "answer":
            return False
        cur = self._cur(st)
        return self._correct(cur, self.runner.run(cur, code))
```

- [ ] **Step 8: Run both test files**

Run: `uv run pytest -q tests/test_ai.py tests/test_engine.py`
Expected: all pass.

- [ ] **Step 9: Commit**

```bash
git add player/ai.py player/engine.py tests/test_ai.py tests/test_engine.py
git commit -m "Build what the model sees, find code in a reply, and let the engine say whether code solves the step

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 3: Keep the questions, and report them

**Files:**
- Modify: `player/store.py` (schema, `add_question`, `questions`)
- Modify: `player/report.py` (`build_question_report`, `main`)
- Create: `tests/test_questions.py`

**Interfaces:**
- Produces:
  - `Store.add_question(run_id: int, step: int, question: str, reply: str, provider: str, guarded: bool) -> None`. `step` is 1-based, like `events.step`.
  - `Store.questions() -> list[dict]`: keys `id, run_id, lesson, step, asked_at, question, reply, provider, guarded`, oldest first.
  - `report.build_question_report(questions: list[dict]) -> list[str]`: one line per lesson and step, most questions first: `"sql-02 step 5: 2 questions; latest: what is a pile?"`.

- [ ] **Step 1: Write the failing tests**

`tests/test_questions.py`:

```python
from player.report import build_question_report
from player.store import Store


def make_run(store):
    return store.new_run("sql-02", {"phase": "continue"}, [{"type": "teacher", "text": "x"}])


def test_a_question_is_stored_with_its_lesson(tmp_path):
    s = Store(tmp_path)
    run = make_run(s)
    s.add_question(run, 5, "what is a pile?", "A group of rows.", "gemini", False)
    [q] = s.questions()
    assert (q["lesson"], q["step"], q["question"], q["provider"], q["guarded"]) == (
        "sql-02", 5, "what is a pile?", "gemini", 0)
    assert q["reply"] == "A group of rows."


def test_questions_do_not_touch_runs_items_or_events(tmp_path):
    s = Store(tmp_path)
    run = make_run(s)
    before = (s.latest_any(), s.items(run), s.events())
    s.add_question(run, 1, "q", "a", "groq", True)
    assert (s.latest_any(), s.items(run), s.events()) == before


def test_an_old_progress_file_gets_the_table(tmp_path):
    import sqlite3
    db = sqlite3.connect(tmp_path / "progress.db")
    db.executescript("CREATE TABLE runs (id INTEGER PRIMARY KEY, lesson TEXT, started_at TEXT, "
                     "finished_at TEXT, state_json TEXT); INSERT INTO runs VALUES (1, 'sql-01', 't', NULL, '{}');")
    db.commit()
    db.close()
    s = Store(tmp_path)
    s.add_question(1, 2, "q", "a", "gemini", False)
    assert len(s.questions()) == 1
    assert s.conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 1


def test_the_report_ranks_steps_by_questions_asked():
    qs = [{"lesson": "sql-02", "step": 5, "question": "a"}, {"lesson": "sql-01", "step": 9, "question": "b"},
          {"lesson": "sql-02", "step": 5, "question": "c"}]
    assert build_question_report(qs) == [
        "sql-02 step 5: 2 questions; latest: c", "sql-01 step 9: 1 question; latest: b"]
    assert build_question_report([]) == []
```

- [ ] **Step 2: Run to see them fail**

Run: `uv run pytest -q tests/test_questions.py`
Expected: FAIL (`AttributeError ... add_question` and an import error for `build_question_report`).

- [ ] **Step 3: Add the table and methods to `player/store.py`**

Append to `SCHEMA` (inside the triple-quoted string, after the `events` table):

```sql
CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY, run_id INTEGER, step INTEGER, asked_at TEXT,
  question TEXT, reply TEXT, provider TEXT, guarded INTEGER);
```

Add to `Store`:

```python
    def add_question(self, run_id, step, question, reply, provider, guarded):
        with self.conn:
            self.conn.execute(
                "INSERT INTO questions (run_id, step, asked_at, question, reply, provider, guarded) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (run_id, step, _now(), question, reply, provider, int(guarded)))

    def questions(self):
        cur = self.conn.execute(
            "SELECT q.id, q.run_id, r.lesson, q.step, q.asked_at, q.question, q.reply, q.provider, q.guarded "
            "FROM questions q JOIN runs r ON r.id = q.run_id ORDER BY q.id")
        names = [d[0] for d in cur.description]
        return [dict(zip(names, r)) for r in cur.fetchall()]
```

- [ ] **Step 4: Add the report to `player/report.py`**

Add above `main`:

```python
def build_question_report(questions):
    """The steps the learner asked about most, each with the latest question. For the writer, never a score."""
    groups = {}
    for q in questions:
        groups.setdefault((q["lesson"], q["step"]), []).append(q)
    ranked = sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    return [f"{lesson} step {step}: {len(qs)} question{'s' if len(qs) != 1 else ''}; latest: {qs[-1]['question']}"
            for (lesson, step), qs in ranked]
```

In `main`, replace the print with:

```python
    store = Store(args.progress)
    _, lessons = load_content(args.content)
    print("\n".join(build_report(store.events(), lessons)))
    asked = build_question_report(store.questions())
    if asked:
        print("\nQuestions asked:\n" + "\n".join(asked))
    return 0
```

(Remove the old `_, lessons = ...` and `print(...)` lines in `main` so they are not duplicated.)

- [ ] **Step 5: Run the tests**

Run: `uv run pytest -q tests/test_questions.py tests/test_store.py tests/test_report.py`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add player/store.py player/report.py tests/test_questions.py
git commit -m "Keep the questions in the progress file and list the most-asked steps in the report

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 4: `Player.ask` and the route

**Files:**
- Modify: `content/ui.yaml` (three new keys)
- Modify: `player/app.py`
- Create: `tests/test_ask.py`

**Interfaces:**
- Consumes: `llm.chat`, `llm.Unavailable`, `ai.*`, `Engine.solves`, `Store.add_question`, `Store.items`.
- Produces:
  - `make_app(content_dir, data_dir, progress_dir, rng=None, chat=None)`: `chat(messages) -> (reply, provider)` defaults to `llm.chat`.
  - `Player.ask(question: str, thread: list[dict]) -> dict`: `{"reply": str, "ok": True, "guarded": bool}`, or `{"reply": <ask_unavailable line>, "ok": False}` when `chat` raises `llm.Unavailable`. Never changes the run state.
  - `POST /api/ask` with body `{"question": str, "thread": [{"role": "user"|"teacher", "text": str}]}`. 400 for an empty question or one over 2000 characters.
  - `content/ui.yaml` keys: `ask_persona` (text), `ask_unavailable` (line), `ask_guarded` (line).

- [ ] **Step 1: Add the lines to `content/ui.yaml`**

Append:

```yaml
ask_persona: |
  You are the teacher in a short, spoken-style course in SQL, Python, pandas and machine learning. The learner is preparing for data science interviews and has stopped in the middle of a lesson to ask you a question. Answer in plain text, warmly, in at most six short sentences, with at most one small example. Use backticks for code, and no headings, lists or bold.
  Use only the thoughts the learner has met, listed below, and the tables named below. If the question needs something they have not met, say so, and give the one idea they need, briefly.
  Never write the answer to the step that is waiting, and never write any sentence that would solve it. If the question is about that step, explain the idea with a different example, on a different table or column, and let the learner build their own answer.
  Never invent a memory trick. Give the real reason, or say that this just is.
  End by pointing the learner back to the step they are on.
ask_unavailable: "I cannot reach the question service just now. The lesson is waiting where you left it."
ask_guarded: "That would be the answer to the step you are on, and it is yours to type. Ask me about any piece of it instead."
```

- [ ] **Step 2: Write the failing tests**

`tests/test_ask.py`:

```python
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
    """A one-lesson course waiting at a typed step. Returns make(chat) -> (client, progress folder)."""
    content = tmp_path / "content"
    (content / "sql").mkdir(parents=True)
    (content / "ui.yaml").write_text((ROOT / "content" / "ui.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    (content / "sql" / "thoughts.yaml").write_text(
        yaml.safe_dump({"thoughts": {"count-rows": "Count the rows of a table."}}), encoding="utf-8")
    (content / "sql" / "lesson-01.yaml").write_text(yaml.safe_dump({"lesson": "t-01", "steps": [
        {"kind": "give", "new": ["count-rows"], "text": "We count rows.", "shows": ["SELECT COUNT(*) FROM orders"]},
        {"kind": "ask", "requires": ["count-rows"], "text": "How many restaurants?", "model": MODEL,
         "narration": ["a", "b"]}]}), encoding="utf-8")

    def build(chat):
        c = TestClient(make_app(content / "sql", data_dir, tmp_path / "progress", chat=chat))
        c.get("/api/run")
        c.post("/api/next")
        c.post("/api/next")
        assert c.get("/api/run").json()["pending"]["mode"] == "answer"
        return c, tmp_path / "progress"
    return build


def fake_chat(reply="Counting is simple.", provider="gemini"):
    calls = []

    def chat(messages):
        calls.append(messages)
        return reply, provider
    chat.calls = calls
    return chat


def unavailable(messages):
    raise llm.Unavailable("no key set")


def test_the_persona_lines_exist_and_have_no_em_dash():
    for key in ("ask_persona", "ask_unavailable", "ask_guarded"):
        assert UI[key].strip() and "—" not in UI[key]


def test_a_question_gets_a_reply_and_is_kept(make):
    chat = fake_chat("A count is a number of rows.")
    c, progress = make(chat)
    r = c.post("/api/ask", json={"question": "what is count?", "thread": []}).json()
    assert r == {"reply": "A count is a number of rows.", "ok": True, "guarded": False}
    [row] = sqlite3.connect(progress / "progress.db").execute(
        "SELECT step, question, reply, provider, guarded FROM questions").fetchall()
    assert row == (2, "what is count?", "A count is a number of rows.", "gemini", 0)


def test_the_model_answer_never_reaches_the_model(make):
    chat = fake_chat()
    c, _ = make(chat)
    c.post("/api/ask", json={"question": "help", "thread": []})
    system = chat.calls[0][0]["content"]
    assert MODEL not in json.dumps(chat.calls[0])
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
    assert [m["role"] for m in chat.calls[0]] == ["system", "user", "assistant", "user"]


def test_a_miss_adds_the_attempt_to_the_context(make):
    chat = fake_chat()
    c, _ = make(chat)
    c.post("/api/answer", json={"sql": "SELECT COUNT(*) FROM couriers"})
    c.post("/api/ask", json={"question": "why not?", "thread": []})
    assert "SELECT COUNT(*) FROM couriers" in chat.calls[0][0]["content"]


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

    def chat(messages):
        return llm.chat(messages, {"GEMINI_API_KEY": key}, urlopen)
    c, progress = make(chat)
    r = c.post("/api/ask", json={"question": "what is count?", "thread": []})
    assert r.status_code == 200 and key not in r.text
    assert key not in sent[0].data.decode()
    dump = "\n".join(sqlite3.connect(progress / "progress.db").iterdump())
    assert key not in dump
```

- [ ] **Step 3: Run to see them fail**

Run: `uv run pytest -q tests/test_ask.py`
Expected: FAIL (`make_app() got an unexpected keyword argument 'chat'`).

- [ ] **Step 4: Implement in `player/app.py`**

Imports: change `from .engine import Engine` block to:

```python
from . import ai, llm
from .engine import Engine
```

In `Player.__init__`, change the signature and store the extras:

```python
    def __init__(self, content_dir, data_dir, progress_dir, rng=None, chat=None):
        content = Path(content_dir)
        self.thoughts, lessons = load_content(content)
        ui = yaml.safe_load(ui_path(content).read_text(encoding="utf-8"))
        self.ui, self.chat = ui, chat or llm.chat
```

(keep the rest of `__init__` as it is.)

Add these methods to `Player` (after `play`):

```python
    def _met(self, name, st):
        """Ids of the thoughts introduced up to the step now playing, in course order."""
        ids = []
        for lesson, steps in self.lessons:
            upto = st["playing"]["step"] + 1 if lesson == name else len(steps)
            ids += [t for s in steps[:upto] for t in s.get("new", [])]
            if lesson == name:
                break
        return list(dict.fromkeys(ids))

    def ask(self, question, thread):
        """A side question. The lesson is not touched: no state, no ladder, no event. Only the question
        and its reply are kept. The model sees only what the learner has already seen."""
        with self.lock:
            run_id, name, st = self._current()
            eng = self.engines[name]
            step = eng.steps[st["playing"]["step"]]
            items = self.store.items(run_id)
            teacher = [i["text"] for i in items if i["type"] == "teacher"]
            messages = ai.build_messages(
                self.ui, ai.thought_lines(self.thoughts, self._met(name, st)), teacher,
                teacher[-1] if teacher else "",
                ai.attempt_text(items) if st["phase"] == "answer" and st["misses"] else "",
                ai.schema_lines(self.runner.path(step.get("data", ""))), thread, question)
        try:  # the lock is free while the model thinks
            reply, provider = self.chat(messages)
        except llm.Unavailable:
            return {"reply": self.ui["ask_unavailable"], "ok": False}
        with self.lock:
            # st is the step that was asked about, even if the learner has moved on since
            guarded = any(eng.solves(st, code) for code in ai.code_candidates(reply))
            if guarded:
                reply = self.ui["ask_guarded"]
            self.store.add_question(run_id, st["playing"]["step"] + 1, question, reply, provider, guarded)
        return {"reply": reply, "ok": True, "guarded": guarded}
```

Add the request model next to `Play`:

```python
class Ask(BaseModel):
    question: str
    thread: list[dict] = []
```

Change `make_app`'s signature and first line, and add the route after `/api/play`:

```python
def make_app(content_dir, data_dir, progress_dir, rng=None, chat=None):
    player = Player(content_dir, data_dir, progress_dir, rng, chat)
```

```python
    @app.post("/api/ask")
    def post_ask(a: Ask):
        question = a.question.strip()
        if not question or len(question) > 2000:
            raise HTTPException(400, "empty or too long")
        thread = [{"role": str(m.get("role")), "text": str(m.get("text", ""))[:2000]} for m in a.thread[-10:]]
        return player.ask(question, thread)
```

- [ ] **Step 5: Run the new tests, then the app tests**

Run: `uv run pytest -q tests/test_ask.py tests/test_app.py`
Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add content/ui.yaml player/app.py tests/test_ask.py
git commit -m "Answer side questions without touching the lesson, and replace a reply that solves the step

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 5: The screen: Code and Ask tabs, the side thread, the way back

No automated test (the project has no browser tests). Verify in the browser with a stub model.

**Files:**
- Modify: `player/web/app.js`
- Modify: `player/web/style.css`

**Interfaces:**
- Consumes: `POST /api/ask` (Task 4) returning `{reply, ok, guarded}`.
- Behaviour: Code is the default tab. Asking opens a tinted "Side question" block at the end of the transcript. "Got it, back to the lesson" closes it, appends a "Where we were:" copy of the waiting prompt inside the block, switches to Code, and restores focus. A re-render (answering a step, continuing) closes any open thread and keeps closed threads in place. A new sitting clears them.

- [ ] **Step 1: Let `renderText` accept untagged code fences**

In `player/web/app.js`, in `renderText`, change the split pattern and the code-block condition:

```js
  const parts = text.split(/```(\w*)\n([\s\S]*?)\n?```/);
  for (let i = 0; i < parts.length; i += 3) {
    parts[i].split(/\n\s*\n/).filter(p => p.trim()).forEach(p => {
      const para = el('p'); para.appendChild(lineNodes(p.trim(), lang)); box.appendChild(para);
    });
    if (i + 2 < parts.length) box.appendChild(codeBlock(parts[i + 2], null, parts[i + 1] || lang));
  }
```

- [ ] **Step 2: Add the thread state and drawing above `render`**

Insert before `function render(view)`:

```js
// ---- side questions: a thread opens in the transcript, the lesson waits, the learner says when to go back

const threads = [];       // each: { at: item count when it began, lang, messages, thinking, back, node }
let lastTeacher = null;   // the prompt now waiting, for "Where we were"

function threadNode(t) {
  const box = el('div', 'side');
  box.appendChild(el('div', 'label', 'Side question'));
  t.messages.forEach(m => box.appendChild(m.role === 'user' ? el('p', 'you', m.text) : renderText(m.text, 'reply', t.lang)));
  if (t.thinking) box.appendChild(el('p', 'hint', 'Thinking it over.'));
  if (t.back && t.back.text) {
    box.appendChild(el('div', 'label', 'Back to the lesson'));
    box.appendChild(renderText('Where we were:\n\n' + t.back.text, 'reply', t.back.lang));
  }
  return box;
}

function makeAsk(lang) {
  const pane = el('div', 'ask');
  const box = el('textarea');
  box.rows = 3;
  box.placeholder = 'Ask the teacher about this step, or about SQL, Python, pandas or machine learning.';
  ['autocomplete', 'autocapitalize', 'autocorrect'].forEach(a => box.setAttribute(a, 'off'));
  box.setAttribute('spellcheck', 'false');
  const hint = el('p', 'hint');
  const self = { pane, box, onBack: () => {} };
  let thread = null;
  const paint = () => {
    const node = threadNode(thread);
    if (thread.node) thread.node.replaceWith(node); else itemsEl.appendChild(node);
    thread.node = node;
    node.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
  };
  const ask = async () => {
    const question = box.value.trim();
    if (!question) { hint.textContent = 'Type a question first.'; return; }
    if (!thread) { thread = { at: shown, lang, messages: [], thinking: false, back: null, node: null }; threads.push(thread); }
    const earlier = thread.messages.map(m => ({ role: m.role, text: m.text }));
    thread.messages.push({ role: 'user', text: question });
    thread.thinking = true; box.value = ''; hint.textContent = ''; back.hidden = true;
    paint();
    try {
      const r = await api('/api/ask', { question, thread: earlier });
      thread.messages.push({ role: 'teacher', text: r.reply });
    } catch (e) { hint.textContent = 'That did not go through.'; }
    thread.thinking = false;
    paint();
    back.hidden = false;
  };
  const back = button('Got it, back to the lesson', () => {
    thread.back = lastTeacher || { text: '' };
    paint();
    thread = null; back.hidden = true;
    self.onBack();
    inputEl.scrollIntoView({ block: 'end', behavior: 'smooth' });
  }, 'primary small');
  back.hidden = true;
  box.addEventListener('input', () => { hint.textContent = ''; });
  box.addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); ask(); } });
  pane.append(box, button('Ask', ask, 'primary small'), ' ', back, hint);
  return self;
}
```

- [ ] **Step 3: Rewrite `renderInput` to hold the two tabs**

Replace the whole `renderInput` function with:

```js
function renderInput(pending) {
  inputEl.replaceChildren();
  const lang = pending.lang || 'sql';
  const codePane = el('div'), tabs = el('div', 'tabs'), ask = makeAsk(lang);
  let focusCode = () => {};
  const tab = {};
  const show = which => {
    codePane.hidden = which !== 'code'; ask.pane.hidden = which !== 'ask';
    tab.code.classList.toggle('on', which === 'code'); tab.ask.classList.toggle('on', which === 'ask');
    if (which === 'ask') ask.box.focus(); else focusCode();
  };
  tab.code = button('Code', () => show('code'), 'tab');
  tab.ask = button('Ask', () => show('ask'), 'tab');
  tabs.append(tab.code, tab.ask);
  ask.onBack = () => show('code');

  if (pending.mode === 'continue') {
    codePane.appendChild(button('Continue', () => send('/api/next')));
  } else if (pending.mode === 'run') {
    codePane.appendChild(codeBlock(pending.sql, null, lang));
    codePane.appendChild(button('Run', () => send('/api/next')));
  } else if (pending.mode === 'answer') {
    const { wrap, box, sync } = makeEditor(lang);
    const hint = el('p', 'hint');
    const run = () => {
      if (!box.value.trim()) { hint.textContent = 'Type an answer first.'; return; }
      send('/api/answer', { sql: box.value });
    };
    box.addEventListener('input', () => { hint.textContent = ''; });
    box.addEventListener('keydown', e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run(); } });
    codePane.append(wrap, button('Run', run), hint);
    focusCode = () => { sync(); box.focus(); };
  } else if (pending.mode === 'done') {
    if (pending.next) codePane.appendChild(button('Next lesson', () => send('/api/run/new', { next: true })));
    codePane.appendChild(button('Sit this lesson again', () => send('/api/run/new')));
  }
  inputEl.append(tabs, codePane, ask.pane);
  show('code');
}
```

- [ ] **Step 4: Keep threads across re-renders**

Replace `render` with:

```js
function render(view) {
  if (view.items.length < shown) { shown = 0; threads.length = 0; }  // a new sitting starts clean
  itemsEl.replaceChildren();
  const lastTeacherAt = view.items.map(i => i.type).lastIndexOf('teacher');
  view.items.forEach((item, i) => {
    const node = renderItem(item);
    if (i < lastTeacherAt) node.classList.add('old');
    if (shown && i >= shown) node.classList.add('rise');
    itemsEl.appendChild(node);
    threads.filter(t => t.at === i + 1).forEach(t => { t.thinking = false; t.node = threadNode(t); itemsEl.appendChild(t.node); });
  });
  shown = view.items.length;
  const t = lastTeacherAt >= 0 ? view.items[lastTeacherAt] : null;
  lastTeacher = t ? { text: t.text, lang: t.lang || 'sql' } : null;
  renderInput(view.pending);
  inputEl.scrollIntoView({ block: 'end', behavior: 'smooth' });
}
```

- [ ] **Step 5: Style the thread**

In `player/web/style.css`, add `--side: rgba(47, 111, 159, 0.08);` to the light `:root` block and `--side: rgba(130, 182, 228, 0.1);` to the dark one. Append at the end:

```css
.side { margin: 1rem 0 1rem 1.2rem; padding: 0.4rem 1rem 0.5rem; background: var(--side); border-left: 3px solid var(--fn); border-radius: 4px 12px 12px 4px; }
.side .you { margin: 0.6rem 0 0.2rem; font: 0.92rem/1.5 system-ui, sans-serif; color: var(--muted); white-space: pre-wrap; }
.side .teacher.reply { margin: 0.3rem 0 0.4rem; font-size: 1.02rem; }
.ask textarea { display: block; width: 100%; min-height: 5rem; padding: 0.7rem 0.9rem; font: 0.95rem/1.5 system-ui, sans-serif;
  color: var(--ink); background: var(--card); border: 1px solid var(--line); border-radius: 12px; resize: vertical; outline: none; }
.ask textarea:focus { border-color: var(--accent); box-shadow: 0 0 0 4px var(--ring); }
.ask button.primary { margin-top: 0.7rem; }
```

- [ ] **Step 6: Verify in the browser with a stub model**

Start a scratch server whose model is a stub (no key, no network):

```bash
rm -rf /tmp/askscratch && mkdir /tmp/askscratch
uv run python - <<'EOF' &
import uvicorn
from player.app import make_app
def chat(messages):
    last = messages[-1]["content"]
    if "answer" in last:
        return "Try `SELECT COUNT(*) FROM restaurants` and see.", "stub"
    return "A count is how many rows there are. For example, `SELECT COUNT(*) FROM couriers` counts couriers. Now back to your step.", "stub"
uvicorn.run(make_app("content", "data", "/tmp/askscratch", chat=chat), port=8772)
EOF
```

Open `http://localhost:8772` in the browser pane and check, in order:
1. The tabs Code and Ask show above the editor. Code is active and the editor has focus.
2. On the Ask tab, ask "what is a count?". A tinted "Side question" block appears at the end of the transcript, with your question and the stub reply, code coloured.
3. The "Got it, back to the lesson" button appears. Click it: the block gains "Where we were:" and the waiting prompt, the Code tab returns, and anything typed in the editor before is still there.
4. Ask "just give me the answer": the reply is the guarded line (applies on a typed step; the first step is a give step, so use `Run`/`Continue` first, then repeat on a typed step with a reply containing the model answer).
5. Answer the step in Code: the old thread stays in place, the new view works, the Ask tab is empty again.
6. Stop the server and ask again: the calm "cannot reach the question service" line shows once a real `llm.chat` runs without a key (check this in Task 6).

Then stop the stub: `pkill -f "port=8772"` and `rm -rf /tmp/askscratch`.

- [ ] **Step 7: Run the web-facing tests and commit**

Run: `uv run pytest -q tests/test_app.py tests/test_ask.py`
Expected: all pass.

```bash
git add player/web/app.js player/web/style.css
git commit -m "Add the Code and Ask tabs, the side thread and the way back to the lesson

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Docs, the live check, and the whole suite

**Files:**
- Modify: `docs/06-decisions.md` (add C22 after C21)
- Modify: `docs/05-app-requirements.md` (add R30 after R29)
- Modify: `docs/superpowers/specs/2026-11-24-ai-side-questions-design.md` (close the open items)
- Modify: `README.md` and `CLAUDE.md` (a short note on asking, and `.env`)
- Modify (if the live check shows a better name): `player/llm.py` defaults
- Needs from the owner: a `.env` file at the repository root with `GEMINI_API_KEY` and `GROQ_API_KEY`

- [ ] **Step 1: Add decision C22**

In `docs/06-decisions.md`, add a row after C21 in the same table format:

```
| C22 | The learner may ask questions in words. The lesson pauses, a side thread answers, and the learner confirms to go back. The model never sees expected answers, a guard replaces any reply that would solve the step, and nothing is scored or counted for the learner. Gemini first, Groq as fallback, keys in a git-ignored `.env`. Questions are kept in the progress file and listed in the miss report. | The owner wants to ask about thoughts the script has not yet explained. It is a conversation about the step in front of them and not a reference panel (rule 6), and they still type every answer (rule 1). The questions show where the script is thin. |
```

- [ ] **Step 2: Add requirement R30**

In `docs/05-app-requirements.md`, after R29:

```
- R30. An "Ask" tab beside the code editor (decision C22). A question opens a side thread in the transcript while the lesson waits. Only the learner ends it, with "Got it, back to the lesson", and the step is shown again with the learner's draft kept. The model never receives expected answers, a reply that solves the step is replaced, and the thread changes no lesson state, ladder or miss log.
```

- [ ] **Step 3: Close the spec's open items**

In the spec, replace the "Open for the owner" section's two items with: `1. Provider order: Gemini first (decided 24 Nov 2026).` and `2. Streaming: not at first (decided 24 Nov 2026).`

- [ ] **Step 4: README and CLAUDE.md**

In `README.md`, add a short section "Asking the teacher": copy `.env.example` to `.env`, fill in `GEMINI_API_KEY` and `GROQ_API_KEY`, restart the player, use the Ask tab. In `CLAUDE.md`, add to the state paragraph: "The Ask tab (decision C22) sends questions to Gemini or Groq. Keys live in a git-ignored `.env`. The model never sees a step's expected answer."

- [ ] **Step 5: Live check (needs the owner's `.env`)**

Confirm `.env` exists and is ignored: `git check-ignore .env` prints `.env`. List the models each provider offers (prints names only, never a key):

```bash
uv run python - <<'EOF'
import json, urllib.request
from player.llm import settings
cfg = settings()
for name, url, key in [("gemini", "https://generativelanguage.googleapis.com/v1beta/openai/models", "GEMINI_API_KEY"),
                       ("groq", "https://api.groq.com/openai/v1/models", "GROQ_API_KEY")]:
    if not cfg.get(key):
        print(name, "no key"); continue
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + cfg[key], "User-Agent": "mt-coding-course"})
    print(name, sorted(m["id"] for m in json.load(urllib.request.urlopen(req, timeout=30))["data"]))
EOF
```

Pick a current fast model for each, set it in `.env` as `GEMINI_MODEL` and `GROQ_MODEL`, and if the built-in default names are no longer listed, update `PROVIDERS` in `player/llm.py`. Then one real call per provider:

```bash
uv run python - <<'EOF'
from player.llm import chat, settings
cfg = settings()
for order in ("gemini", "groq"):
    reply, provider = chat([{"role": "user", "content": "In one sentence, what does SQL COUNT(*) do?"}], {**cfg, "AI_ORDER": order})
    print(provider, "->", reply)
EOF
```

Expected: one sentence from each. If Gemini returns an empty reply (its reasoning can use up `max_tokens`), raise `max_tokens` in `player/llm.py` and rerun. Then start the player on a scratch progress folder (`uv run python -m player --skip-check --port 8773 --progress /tmp/askscratch`), ask a real question on a typed step in the browser, ask for the answer outright, and check that the guard line or an explanation comes back and "back to the lesson" works. Stop the server and remove `/tmp/askscratch`. Confirm `git status` does not list `.env`.

- [ ] **Step 6: Run everything**

Run: `uv run pytest -q` and `uv run python -m checker content | tail -1`
Expected: all tests pass (about 235) and `0 failures, 4 warnings`.

- [ ] **Step 7: Commit**

```bash
git add docs README.md CLAUDE.md player/llm.py
git commit -m "Record decision C22 and the Ask requirement, and document the keys

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"
```

---

## Self-review

**Spec coverage.** Answer window tabs: Task 5. Detour and back button, draft kept, only the learner ends a thread: Task 5 (Steps 2 to 4). What the model sees and never sees: Tasks 2 and 4, with `test_the_model_answer_never_reaches_the_model`. Guard: `Engine.solves` (Task 2), `Player.ask` (Task 4), tested. Scope of questions, persona: `ui.yaml` (Task 4). Providers, `.env`, fallback, calm no-key line, no streaming, keys never leaking: Tasks 1 and 4, tested. Records and "most-asked steps": Task 3. Privacy: stated in the spec, no code. Tests listed in the spec: payload (Task 4), guard (Task 4), lesson unchanged (Task 4), rows written and key absent (Tasks 3 and 4), fallback (Task 1), no key (Tasks 1 and 4). Docs C22 and R30: Task 6. Side threads not replayed on reload: by construction, they live in JavaScript only.

**Placeholders.** None. The one deliberate gap is the default model names in `PROVIDERS`, which Task 6 Step 5 checks against each provider's live list.

**Type consistency.** `chat(messages) -> (reply, provider)` in Task 1, passed as `chat=` and called that way in Task 4 and in the tests. `Store.add_question(run_id, step, question, reply, provider, guarded)` in Task 3 matches the call in Task 4. `ai.build_messages` argument order in Task 2 matches the call in Task 4: `(ui, thoughts, teacher_lines, prompt, attempt, schema, thread, question)`. `/api/ask` returns `{reply, ok, guarded}`; Task 5 reads `r.reply`. `Engine.solves(st, code)` matches its call. UI keys `ask_persona`, `ask_unavailable`, `ask_guarded` are used consistently.

**Known limits, accepted.** The guard catches an answer that runs to the expected result. A reply that explains the answer in words only is held back by the persona prompt alone. The persona prompt is the only guard for Python steps judged through hidden `check` code beyond the same `solves` run. Gemini's free tier may keep prompts.
