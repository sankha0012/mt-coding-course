# Lesson format and content checker: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn SQL lesson 1 into a YAML lesson file and build the checker that enforces the seven script checks, so it passes on lesson 1 and fails with clear messages on a broken copy.

**Architecture:** A small Python package `checker/` with three responsibilities: `data.py` builds a read-only in-memory SQLite database from `data/*.csv` and compares result sets, `lesson.py` reads a strand folder, `checks.py` holds one function per check and `check_all`. `__main__.py` is the command line. Lesson content lives in `content/sql/` and never in `checker/`.

**Tech Stack:** Python 3.12, `uv`, `pyyaml`, `pytest`, stdlib `sqlite3`, `csv`, `difflib`.

**Spec:** `docs/superpowers/specs/2026-11-20-lesson-format-and-checker-design.md`. Read it first: it defines every YAML field and every message.

## Global Constraints

- Python 3.12 and `uv`. Dependencies: `pyyaml` only at runtime, `pytest` in the dev group. No other packages.
- No code reads or writes anything under `data/`. The database is in memory and set to `PRAGMA query_only = ON` after loading.
- Empty CSV cells load as `NULL`. A column loads as `INTEGER` if every non-empty cell is a whole number, else `REAL` if every one is a number, else `TEXT`.
- Result sets compare as multisets of rows, column names ignored, floats rounded to six places (two places for the `result` field).
- Every failure message starts `FAIL <lesson> step <n>:` where `<n>` is the step's position counting from 1. Warnings start `WARN`.
- Checks 5 and 7 print reports and never fail the run. Exit code is 1 if any `FAIL`, 2 if files cannot be read, else 0.
- Lesson text never appears in `checker/`.
- Commit messages are normal English prose and end with the attribution line the session gives for commits.
- Work on a branch named `milestone-3-checker`. Do not merge or push without the owner's yes.
- The owner asked for permission before code. This plan, once approved, is that permission for the files named here and no others.

## File structure

| File | Responsibility |
|---|---|
| `pyproject.toml` | Project metadata, dependencies, pytest config |
| `.gitignore` | Add `.venv/`, `__pycache__/`, `.pytest_cache/` |
| `checker/__init__.py` | Empty |
| `checker/data.py` | `load_db`, `run`, `canon`, `same_rows` |
| `checker/lesson.py` | `load_strand` |
| `checker/checks.py` | `check_sql`, `check_narration`, `check_audit`, `check_new_limit`, `check_shapes`, `report_spacing`, `report_load`, `check_all` |
| `checker/__main__.py` | `main(argv)` command line |
| `content/sql/thoughts.yaml` | The 14 thoughts of lesson 1 |
| `content/sql/lesson-01.yaml` | Lesson 1, 23 steps |
| `tests/conftest.py` | Shared fixtures |
| `tests/test_data.py` | Tests for `data.py` |
| `tests/test_lesson.py` | Tests for `lesson.py` |
| `tests/test_checks.py` | Tests for every check |
| `tests/test_cli.py` | Tests for `main` |
| `tests/test_gate.py` | The two milestone gates on the real lesson |

---

### Task 1: Project scaffold and `data.py`

**Files:**
- Create: `pyproject.toml`, `checker/__init__.py`, `checker/data.py`, `tests/conftest.py`, `tests/test_data.py`
- Modify: `.gitignore`

**Interfaces:**
- Produces: `load_db(data_dir) -> sqlite3.Connection`, `run(conn, sql) -> list[tuple]`, `canon(rows, any_column_order=False, ordered=False, ndigits=6) -> list[tuple]`, `same_rows(a, b, **flags) -> bool`. Fixtures `data_dir` and `conn`.

- [ ] **Step 1: Create the branch, commit the spec and plan, add the scaffold**

```bash
git switch -c milestone-3-checker
git add docs/superpowers
git commit -m "Add design spec and plan for the lesson format and checker"
```

Write `pyproject.toml`:

```toml
[project]
name = "mt-coding-course"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["pyyaml"]

[dependency-groups]
dev = ["pytest"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

Replace `.gitignore` with:

```
.DS_Store
.venv/
__pycache__/
.pytest_cache/
```

Create an empty `checker/__init__.py`, then run:

```bash
uv sync
```

Expected: creates `.venv` and `uv.lock`, installs `pyyaml` and `pytest`.

- [ ] **Step 2: Write the failing tests**

`tests/conftest.py`:

```python
from pathlib import Path

import pytest

from checker.data import load_db

ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def data_dir():
    return ROOT / "data"


@pytest.fixture(scope="session")
def conn(data_dir):
    return load_db(data_dir)
```

`tests/test_data.py`:

```python
import sqlite3

import pytest

from checker.data import run, same_rows


def test_tables_load_with_expected_sizes(conn):
    assert run(conn, "SELECT COUNT(*) FROM orders") == [(6000,)]
    assert run(conn, "SELECT COUNT(*) FROM restaurants") == [(60,)]
    assert run(conn, "SELECT COUNT(*) FROM couriers") == [(200,)]


def test_empty_cells_are_null_and_numbers_are_numbers(conn):
    assert run(conn, "SELECT COUNT(*) FROM orders WHERE subtotal IS NULL") == [(25,)]
    assert run(conn, "SELECT typeof(subtotal) FROM orders WHERE subtotal IS NOT NULL LIMIT 1") == [("real",)]
    assert run(conn, "SELECT typeof(order_id) FROM orders LIMIT 1") == [("integer",)]
    assert run(conn, "SELECT typeof(city) FROM restaurants LIMIT 1") == [("text",)]


def test_database_is_read_only(conn):
    with pytest.raises(sqlite3.OperationalError):
        conn.execute("DELETE FROM orders")


def test_row_order_is_ignored_unless_ordered():
    assert same_rows([(1,), (2,)], [(2,), (1,)])
    assert not same_rows([(1,), (2,)], [(2,), (1,)], ordered=True)


def test_floats_compare_after_rounding():
    assert same_rows([(0.1 + 0.2,)], [(0.3,)])
    assert same_rows([(60.3992,)], [(60.4,)], ndigits=2)
    assert not same_rows([(60.3992,)], [(60.4,)])


def test_column_order_matters_unless_any_column_order():
    assert not same_rows([("a", 1)], [(1, "a")])
    assert same_rows([("a", 1)], [(1, "a")], any_column_order=True)
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest tests/test_data.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'checker.data'`.

- [ ] **Step 4: Write the implementation**

`checker/data.py`:

```python
import csv
import sqlite3
from pathlib import Path


def _column_type(values):
    cells = [v for v in values if v != ""]
    for cast, sql_type in ((int, "INTEGER"), (float, "REAL")):
        try:
            for v in cells:
                cast(v)
            return cast, sql_type
        except ValueError:
            pass
    return str, "TEXT"


def load_db(data_dir):
    """Build an in-memory database from every CSV in data_dir. Empty cells become NULL."""
    conn = sqlite3.connect(":memory:")
    for path in sorted(Path(data_dir).glob("*.csv")):
        with open(path, newline="", encoding="utf-8") as f:
            header, *body = csv.reader(f)
        types = [_column_type(col) for col in zip(*body)]
        cols = ", ".join(f'"{h}" {t}' for h, (_, t) in zip(header, types))
        conn.execute(f'CREATE TABLE "{path.stem}" ({cols})')
        marks = ", ".join("?" * len(header))
        conn.executemany(
            f'INSERT INTO "{path.stem}" VALUES ({marks})',
            ([None if v == "" else cast(v) for v, (cast, _) in zip(row, types)] for row in body),
        )
    conn.execute("PRAGMA query_only = ON")
    return conn


def run(conn, sql):
    return conn.execute(sql).fetchall()


def canon(rows, any_column_order=False, ordered=False, ndigits=6):
    """Rows in a form that compares equal when the results are the same."""
    out = [tuple(round(v, ndigits) if isinstance(v, float) else v for v in row) for row in rows]
    if any_column_order:
        out = [tuple(sorted(row, key=repr)) for row in out]
    return out if ordered else sorted(out, key=repr)


def same_rows(a, b, **flags):
    return canon(a, **flags) == canon(b, **flags)
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run pytest tests/test_data.py -v`
Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml uv.lock .gitignore checker tests
git commit -m "Add project scaffold and the data loader with result comparison"
```

---

### Task 2: Strand loader and the SQL and narration checks (1, 1b, 6)

**Files:**
- Create: `checker/lesson.py`, `checker/checks.py`, `tests/test_lesson.py`, `tests/test_checks.py`
- Modify: `tests/conftest.py` (replace whole file)

**Interfaces:**
- Consumes: `run`, `same_rows` from `checker/data.py`.
- Produces: `load_strand(content_dir) -> (thoughts: dict[str, str], lessons: list[tuple[str, list[dict]]])`; `check_sql(conn, lesson, steps) -> list[str]`; `check_narration(lesson, steps) -> list[str]`. Fixtures `thoughts`, `steps`, `write_strand`.

- [ ] **Step 1: Replace `tests/conftest.py` with the full shared fixtures**

```python
from pathlib import Path

import pytest
import yaml

from checker.data import load_db

ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def data_dir():
    return ROOT / "data"


@pytest.fixture(scope="session")
def conn(data_dir):
    return load_db(data_dir)


@pytest.fixture
def thoughts():
    names = ["count-rows", "from-table", "star", "keep-rows", "compare-signs"]
    return {name: f"The thought {name}." for name in names}


@pytest.fixture
def steps():
    """A small lesson that passes every check. Tests change one thing at a time."""
    return [
        {"kind": "give", "new": ["count-rows"], "text": "t",
         "shows": ["SELECT COUNT(*) FROM orders"]},
        {"kind": "ask", "new": ["from-table"], "requires": ["count-rows", "from-table"], "text": "t",
         "model": "SELECT COUNT(*) FROM restaurants", "rows": 1, "result": [[60]],
         "narration": ["a", "b"],
         "wrong": [{"sql": "SELECT COUNT(*) restaurants", "ask": "q"}]},
        {"kind": "give", "new": ["star"], "text": "t", "shows": ["SELECT * FROM orders"]},
        {"kind": "ask", "requires": ["star", "from-table"], "text": "t",
         "model": "SELECT * FROM couriers", "rows": 200, "narration": ["a", "b"]},
    ]


@pytest.fixture
def write_strand(tmp_path, thoughts):
    """Write a thoughts file and one lesson to a temporary folder, return the folder."""
    def write(lesson_steps):
        (tmp_path / "thoughts.yaml").write_text(
            yaml.safe_dump({"thoughts": thoughts}, allow_unicode=True), encoding="utf-8")
        (tmp_path / "lesson-01.yaml").write_text(
            yaml.safe_dump({"lesson": "t-01", "steps": lesson_steps}, allow_unicode=True),
            encoding="utf-8")
        return tmp_path
    return write
```

- [ ] **Step 2: Write the failing tests**

`tests/test_lesson.py`:

```python
from checker.lesson import load_strand


def test_load_strand_returns_thoughts_and_lessons_in_order(write_strand, thoughts, steps, tmp_path):
    folder = write_strand(steps)
    (folder / "lesson-02.yaml").write_text("lesson: t-02\nsteps: []\n", encoding="utf-8")
    loaded_thoughts, lessons = load_strand(folder)
    assert loaded_thoughts == thoughts
    assert lessons == [("t-01", steps), ("t-02", [])]
```

`tests/test_checks.py`:

```python
from checker.checks import check_narration, check_sql


def has(fails, text):
    return any(text in f for f in fails)


def sql(conn, steps):
    return check_sql(conn, "t-01", steps)


def test_good_lesson_passes_sql_checks(conn, steps):
    assert sql(conn, steps) == []


def test_model_that_does_not_run(conn, steps):
    steps[1]["model"] = "SELECT COUNT(*) FROM restaurant"
    assert has(sql(conn, steps), "FAIL t-01 step 2: model answer does not run: no such table")


def test_model_that_returns_no_rows(conn, steps):
    steps[1]["model"] = "SELECT * FROM restaurants WHERE city = 'Nowhere'"
    del steps[1]["rows"], steps[1]["result"]
    assert has(sql(conn, steps), "step 2: model answer returns no rows")


def test_rows_must_match(conn, steps):
    steps[1]["rows"] = 2
    assert has(sql(conn, steps), "step 2: model answer returns 1 rows, expected 2")


def test_result_must_match(conn, steps):
    steps[1]["result"] = [[61]]
    assert has(sql(conn, steps), "step 2: model result")


def test_shown_sentence_must_run(conn, steps):
    steps[0]["shows"] = ["SELECT COUNT(*) FROM nowhere"]
    assert has(sql(conn, steps), "step 1: shown sentence does not run")


def test_broken_sentence_must_fail(conn, steps):
    steps[0]["broken"] = "SELECT COUNT(*) FROM orders"
    assert has(sql(conn, steps), "step 1: broken sentence runs without error")


def test_accepted_answer_must_run_and_return_rows(conn, steps):
    steps[1]["accepts"] = ["SELECT * FROM nowhere"]
    assert has(sql(conn, steps), "step 2: accepted answer")


def test_wrong_answer_that_matches_model_fails(conn, steps):
    steps[1]["wrong"] = [{"sql": "SELECT COUNT(*) FROM restaurants", "ask": "q"}]
    assert has(sql(conn, steps), "step 2: wrong answer gives the model result")


def test_wrong_answer_that_errors_is_fine(conn, steps):
    steps[1]["wrong"] = [{"sql": "SELECT COUNT(restaurants)", "ask": "q"}]
    assert sql(conn, steps) == []


def test_wrong_answer_needs_ask_or_tell_and_sql(conn, steps):
    steps[1]["wrong"] = [{"sql": "SELECT 1"}, {"ask": "q"}]
    fails = sql(conn, steps)
    assert has(fails, "step 2: wrong answer needs ask or tell: SELECT 1")
    assert has(fails, "step 2: wrong answer has no sql")


def test_any_column_order_applies_to_wrong_answers(conn, steps):
    steps[1].update(model="SELECT city, COUNT(*) FROM restaurants GROUP BY city", rows=4)
    del steps[1]["result"]
    steps[1]["wrong"] = [{"sql": "SELECT COUNT(*), city FROM restaurants GROUP BY city", "ask": "q"}]
    assert not has(sql(conn, steps), "gives the model result")
    steps[1]["any_column_order"] = True
    assert has(sql(conn, steps), "gives the model result")


def test_typed_step_needs_two_narration_lines(steps):
    steps[1]["narration"] = ["only one", ""]
    assert has(check_narration("t-01", steps), "FAIL t-01 step 2: needs at least two non-empty narration lines, has 1")


def test_cold_check_needs_no_narration(steps):
    steps[3]["kind"] = "cold-check"
    del steps[3]["narration"]
    assert check_narration("t-01", steps) == []
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `uv run pytest tests/test_lesson.py tests/test_checks.py -v`
Expected: FAIL, `ModuleNotFoundError: No module named 'checker.lesson'`.

- [ ] **Step 4: Write the implementation**

`checker/lesson.py`:

```python
from pathlib import Path

import yaml


def load_strand(content_dir):
    """Read thoughts.yaml and every lesson-*.yaml in filename order."""
    d = Path(content_dir)
    thoughts = yaml.safe_load((d / "thoughts.yaml").read_text(encoding="utf-8"))["thoughts"]
    lessons = []
    for path in sorted(d.glob("lesson-*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        lessons.append((data["lesson"], data["steps"]))
    return thoughts, lessons
```

`checker/checks.py`:

```python
import sqlite3

from .data import run, same_rows


def _flags(step):
    return {"ordered": step.get("ordered", False),
            "any_column_order": step.get("any_column_order", False)}


def _try(conn, sql):
    """Return (rows, None), or (None, error message) if the sentence fails."""
    try:
        return run(conn, sql), None
    except sqlite3.Error as e:
        return None, str(e)


def check_sql(conn, lesson, steps):
    """Checks 1 and 1b: every SQL sentence in the lesson runs, or fails, as the step says."""
    fails = []

    def fail(n, msg):
        fails.append(f"FAIL {lesson} step {n}: {msg}")

    for n, s in enumerate(steps, 1):
        for sql in s.get("shows", []):
            _, err = _try(conn, sql)
            if err:
                fail(n, f"shown sentence does not run: {err}: {sql}")
        if "broken" in s and _try(conn, s["broken"])[1] is None:
            fail(n, f"broken sentence runs without error: {s['broken']}")
        if "model" not in s:
            continue
        rows, err = _try(conn, s["model"])
        if err:
            fail(n, f"model answer does not run: {err}")
            continue
        if not rows:
            fail(n, "model answer returns no rows")
        if "rows" in s and len(rows) != s["rows"]:
            fail(n, f"model answer returns {len(rows)} rows, expected {s['rows']}")
        if "result" in s and not same_rows(rows, s["result"], ndigits=2, **_flags(s)):
            fail(n, f"model result {rows[:4]} differs from expected result {s['result']}")
        for sql in s.get("accepts", []):
            got, err = _try(conn, sql)
            if err or not got:
                fail(n, f"accepted answer does not run or returns no rows ({err or 'no rows'}): {sql}")
        for w in s.get("wrong", []):
            if "ask" not in w and "tell" not in w:
                fail(n, f"wrong answer needs ask or tell: {w.get('sql')}")
            if "sql" not in w:
                fail(n, "wrong answer has no sql")
                continue
            got, err = _try(conn, w["sql"])
            if err is None and same_rows(got, rows, **_flags(s)):
                fail(n, f"wrong answer gives the model result: {w['sql']}")
    return fails


def check_narration(lesson, steps):
    """Check 6: a typed step, except a cold check, has two non-empty narration lines."""
    fails = []
    for n, s in enumerate(steps, 1):
        if "model" in s and s.get("kind") != "cold-check":
            lines = [x for x in s.get("narration", []) if x.strip()]
            if len(lines) < 2:
                fails.append(f"FAIL {lesson} step {n}: needs at least two non-empty narration lines, has {len(lines)}")
    return fails
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `uv run pytest tests -v`
Expected: all tests in `test_data.py`, `test_lesson.py` and `test_checks.py` pass. If `test_result_must_match` fails because the message text differs, fix the implementation to match the test, not the reverse.

- [ ] **Step 6: Commit**

```bash
git add checker tests
git commit -m "Add the strand loader and the SQL and narration checks"
```

---

### Task 3: Audit and new-thought limit (checks 2 and 3)

**Files:**
- Modify: `checker/checks.py` (append), `tests/test_checks.py` (append, and update the import line)

**Interfaces:**
- Consumes: the `(lesson_name, steps)` tuples from Task 2.
- Produces: `check_audit(thoughts, lessons) -> list[str]`, `check_new_limit(lessons) -> list[str]`.

- [ ] **Step 1: Write the failing tests**

Change the import line at the top of `tests/test_checks.py` to:

```python
from checker.checks import check_audit, check_narration, check_new_limit, check_sql
```

Append to `tests/test_checks.py`:

```python
def audit(thoughts, steps):
    return check_audit(thoughts, [("t-01", steps)])


def test_good_lesson_passes_audit(thoughts, steps):
    assert audit(thoughts, steps) == []


def test_requiring_a_thought_never_introduced(thoughts, steps):
    steps[3]["requires"] = ["star", "keep-rows"]
    assert has(audit(thoughts, steps), "FAIL t-01 step 4: requires 'keep-rows', which no earlier step introduces")


def test_requiring_a_thought_introduced_later(thoughts, steps):
    steps[1]["requires"] = ["count-rows", "from-table", "star"]
    assert has(audit(thoughts, steps), "step 2: requires 'star'")


def test_unknown_thought_id(thoughts, steps):
    steps[3]["requires"] = ["nonsense"]
    assert has(audit(thoughts, steps), "step 4: unknown thought 'nonsense'")


def test_thought_introduced_twice(thoughts, steps):
    steps[2]["new"] = ["count-rows"]
    assert has(audit(thoughts, steps), "step 3: thought 'count-rows' already introduced at t-01 step 1")


def test_an_import_counts_as_introduced(thoughts, steps):
    steps[0]["imports"] = ["compare-signs"]
    steps[3]["requires"] = ["star", "compare-signs"]
    assert audit(thoughts, steps) == []


def test_a_thought_from_an_earlier_lesson_counts(thoughts, steps):
    later = [{"kind": "ask", "requires": ["star"], "text": "t", "model": "SELECT * FROM couriers",
              "narration": ["a", "b"]}]
    assert check_audit(thoughts, [("t-01", steps), ("t-02", later)]) == []


def test_at_most_one_new_thought_per_step(steps):
    steps[2]["new"] = ["star", "keep-rows"]
    assert has(check_new_limit([("t-01", steps)]),
               "FAIL t-01 step 3: introduces 2 new thoughts (star, keep-rows), at most one allowed")


def test_imports_do_not_count_towards_the_limit(steps):
    steps[2]["imports"] = ["compare-signs", "keep-rows"]
    assert check_new_limit([("t-01", steps)]) == []
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_checks.py -v`
Expected: FAIL, `ImportError: cannot import name 'check_audit'`.

- [ ] **Step 3: Write the implementation**

Append to `checker/checks.py`:

```python
def check_audit(thoughts, lessons):
    """Check 2: every required thought was introduced earlier, and every id exists."""
    fails, seen = [], {}
    for lesson, steps in lessons:
        for n, s in enumerate(steps, 1):
            where = f"{lesson} step {n}"
            here = {}
            for t in s.get("new", []) + s.get("imports", []):
                if t not in thoughts:
                    fails.append(f"FAIL {where}: unknown thought '{t}'")
                elif t in seen:
                    fails.append(f"FAIL {where}: thought '{t}' already introduced at {seen[t]}")
                else:
                    here[t] = where
            for t in s.get("requires", []):
                if t not in thoughts:
                    fails.append(f"FAIL {where}: unknown thought '{t}'")
                elif t not in seen and t not in here:
                    fails.append(f"FAIL {where}: requires '{t}', which no earlier step introduces")
            seen.update(here)
    return fails


def check_new_limit(lessons):
    """Check 3: at most one new thought per step. Imports do not count."""
    return [
        f"FAIL {lesson} step {n}: introduces {len(s['new'])} new thoughts ({', '.join(s['new'])}), at most one allowed"
        for lesson, steps in lessons
        for n, s in enumerate(steps, 1)
        if len(s.get("new", [])) > 1
    ]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add checker tests
git commit -m "Add the audit and new-thought limit checks"
```

---

### Task 4: Shape repeat (check 4)

**Files:**
- Modify: `checker/checks.py` (append), `tests/test_checks.py` (append, update import)

**Interfaces:**
- Produces: `check_shapes(lessons) -> list[str]`.

- [ ] **Step 1: Write the failing tests**

Change the import line at the top of `tests/test_checks.py` to:

```python
from checker.checks import check_audit, check_narration, check_new_limit, check_shapes, check_sql
```

Append:

```python
def shapes(steps):
    return check_shapes([("t-01", steps)])


def test_good_lesson_has_no_shape_repeat(steps):
    assert shapes(steps) == []


def test_answers_differing_in_one_place_repeat_a_shape(steps):
    steps[3]["model"] = "SELECT COUNT(*) FROM orders"
    assert has(shapes(steps), "FAIL t-01 step 4: same shape as step 2")


def test_identical_answers_repeat_a_shape(steps):
    steps[3]["model"] = steps[1]["model"]
    assert has(shapes(steps), "step 4: same shape as step 2")


def test_case_and_spacing_are_ignored(steps):
    steps[3]["model"] = "select  count(*)  from restaurants"
    assert has(shapes(steps), "step 4: same shape as step 2")


def test_two_changes_are_not_a_repeat(steps):
    steps[3]["model"] = "SELECT * FROM restaurants WHERE city = 'Curitiba'"
    assert shapes(steps) == []


def test_steps_without_a_model_are_skipped(steps):
    steps.insert(2, {"kind": "aside", "text": "t"})
    assert shapes(steps) == []
    steps[4]["model"] = "SELECT COUNT(*) FROM orders"
    assert has(shapes(steps), "step 5: same shape as step 2")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_checks.py -v`
Expected: FAIL, `ImportError: cannot import name 'check_shapes'`.

- [ ] **Step 3: Write the implementation**

Add `import re` and `from difflib import SequenceMatcher` at the top of `checker/checks.py`, above `import sqlite3`:

```python
import re
import sqlite3
from difflib import SequenceMatcher
```

Append:

```python
def _tokens(sql):
    return re.findall(r"'[^']*'|\w+|[^\s\w]", sql.lower())


def _changed_runs(a, b):
    """How many separate runs of tokens differ between two SQL sentences."""
    ops = SequenceMatcher(None, _tokens(a), _tokens(b), autojunk=False).get_opcodes()
    return sum(1 for tag, *_ in ops if tag != "equal")


def check_shapes(lessons):
    """Check 4: two consecutive typed steps must not differ in one place only."""
    fails = []
    for lesson, steps in lessons:
        typed = [(n, s) for n, s in enumerate(steps, 1) if "model" in s]
        for (n1, a), (n2, b) in zip(typed, typed[1:]):
            if _changed_runs(a["model"], b["model"]) <= 1:
                fails.append(f"FAIL {lesson} step {n2}: same shape as step {n1}; the answers differ in one place only")
    return fails
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add checker tests
git commit -m "Add the shape repeat check"
```

---

### Task 5: Reports, `check_all` and the command line (checks 5 and 7)

**Files:**
- Modify: `checker/checks.py` (append), `tests/test_checks.py` (append, update import)
- Create: `checker/__main__.py`, `tests/test_cli.py`

**Interfaces:**
- Produces: `report_spacing(thoughts, lessons) -> list[str]`, `report_load(lessons) -> (list[str], list[str])` returning report lines and warnings, `check_all(conn, thoughts, lessons) -> (fails, warns, spacing_lines, load_lines)`, `main(argv=None) -> int`.

- [ ] **Step 1: Write the failing tests**

Change the import line at the top of `tests/test_checks.py` to:

```python
from checker.checks import (check_all, check_audit, check_narration, check_new_limit,
                            check_shapes, check_sql, report_load, report_spacing)
```

Append to `tests/test_checks.py`:

```python
def test_spacing_report_lists_returns_and_gaps(thoughts, steps):
    lines = report_spacing(thoughts, [("t-01", steps)])
    assert "star: introduced t-01:3; needed at t-01:4; gaps 1" in lines
    assert "count-rows: introduced t-01:1; needed at t-01:2; gaps 1" in lines
    assert "keep-rows: never introduced" in lines


def test_spacing_report_says_when_a_thought_is_never_needed_again(thoughts, steps):
    steps[3]["requires"] = ["from-table"]
    lines = report_spacing(thoughts, [("t-01", steps)])
    assert "star: introduced t-01:3; never needed again" in lines


def test_load_report_warns_on_three_new_thoughts_in_a_row(steps):
    lines, warns = report_load([("t-01", steps)])
    assert lines == ["t-01: new thoughts at steps 1, 2, 3 (3 in 4)"]
    assert warns == ["WARN t-01 steps 1 to 3: a new thought in each of 3 steps in a row"]


def test_load_report_has_no_warning_when_relief_comes(steps):
    steps[2].pop("new")
    steps[2]["imports"] = ["star"]
    _, warns = report_load([("t-01", steps)])
    assert warns == []


def test_check_all_returns_failures_warnings_and_reports(conn, thoughts, steps):
    fails, warns, spacing, load = check_all(conn, thoughts, [("t-01", steps)])
    assert fails == []
    assert len(warns) == 1
    assert spacing and load
    steps[1]["narration"] = ["one"]
    steps[3]["requires"] = ["keep-rows"]
    fails, *_ = check_all(conn, thoughts, [("t-01", steps)])
    assert has(fails, "step 2: needs at least two") and has(fails, "step 4: requires 'keep-rows'")
```

`tests/test_cli.py`:

```python
from checker.__main__ import main


def test_clean_lesson_exits_zero_and_prints_reports(write_strand, data_dir, steps, capsys):
    folder = write_strand(steps)
    assert main([str(folder), "--data", str(data_dir)]) == 0
    out = capsys.readouterr().out
    assert "Spacing" in out and "Load" in out and "0 failures, 1 warnings" in out


def test_broken_lesson_exits_one_and_names_the_step(write_strand, data_dir, steps, capsys):
    steps[1]["model"] = "SELECT COUNT(*) FROM restaurant"
    folder = write_strand(steps)
    assert main([str(folder), "--data", str(data_dir)]) == 1
    assert "FAIL t-01 step 2: model answer does not run" in capsys.readouterr().out


def test_missing_files_exit_two(tmp_path, data_dir, capsys):
    assert main([str(tmp_path), "--data", str(data_dir)]) == 2
    assert "ERROR" in capsys.readouterr().out
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests -v`
Expected: FAIL, `ImportError: cannot import name 'check_all'` and `No module named 'checker.__main__'`.

- [ ] **Step 3: Write the implementation**

Append to `checker/checks.py`:

```python
def report_spacing(thoughts, lessons):
    """Check 5: for each thought, where it is needed again after its introduction."""
    flat = [(f"{lesson}:{n}", s) for lesson, steps in lessons for n, s in enumerate(steps, 1)]
    intro, needed = {}, {}
    for i, (_, s) in enumerate(flat):
        for t in s.get("new", []) + s.get("imports", []):
            intro.setdefault(t, i)
        for t in s.get("requires", []):
            needed.setdefault(t, []).append(i)
    lines = []
    for t in sorted(thoughts, key=lambda t: intro.get(t, len(flat))):
        if t not in intro:
            lines.append(f"{t}: never introduced")
            continue
        later = [j for j in needed.get(t, []) if j > intro[t]]
        if not later:
            lines.append(f"{t}: introduced {flat[intro[t]][0]}; never needed again")
            continue
        gaps = [b - a for a, b in zip([intro[t]] + later, later)]
        lines.append(f"{t}: introduced {flat[intro[t]][0]}; needed at "
                     f"{', '.join(flat[j][0] for j in later)}; gaps {', '.join(map(str, gaps))}")
    return lines


def report_load(lessons):
    """Check 7: where new thoughts fall. Warn on three or more steps in a row."""
    lines, warns = [], []
    for lesson, steps in lessons:
        new = [n for n, s in enumerate(steps, 1) if s.get("new")]
        lines.append(f"{lesson}: new thoughts at steps {', '.join(map(str, new))} ({len(new)} in {len(steps)})")
        streak = []
        for n in new + [None]:
            if streak and (n is None or n != streak[-1] + 1):
                if len(streak) >= 3:
                    warns.append(f"WARN {lesson} steps {streak[0]} to {streak[-1]}: "
                                 f"a new thought in each of {len(streak)} steps in a row")
                streak = []
            if n is not None:
                streak.append(n)
    return lines, warns


def check_all(conn, thoughts, lessons):
    fails = []
    for lesson, steps in lessons:
        fails += check_sql(conn, lesson, steps) + check_narration(lesson, steps)
    fails += check_audit(thoughts, lessons) + check_new_limit(lessons) + check_shapes(lessons)
    load, warns = report_load(lessons)
    return fails, warns, report_spacing(thoughts, lessons), load
```

`checker/__main__.py`:

```python
import argparse
import sys

import yaml

from .checks import check_all
from .data import load_db
from .lesson import load_strand


def main(argv=None):
    p = argparse.ArgumentParser(prog="checker", description="Check a strand of lesson files.")
    p.add_argument("content", help="folder holding thoughts.yaml and lesson-*.yaml")
    p.add_argument("--data", default="data", help="folder holding the CSV files")
    args = p.parse_args(argv)
    try:
        thoughts, lessons = load_strand(args.content)
        conn = load_db(args.data)
    except (OSError, KeyError, yaml.YAMLError) as e:
        print(f"ERROR cannot read the lesson files: {e!r}")
        return 2
    fails, warns, spacing, load = check_all(conn, thoughts, lessons)
    for line in fails + warns:
        print(line)
    print("\nSpacing")
    for line in spacing:
        print("  " + line)
    print("\nLoad")
    for line in load:
        print("  " + line)
    print(f"\n{len(fails)} failures, {len(warns)} warnings")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests -v`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add checker tests
git commit -m "Add the spacing and load reports, check_all and the command line"
```

---

### Task 6: Convert lesson 1 to YAML and pass the first gate

**Files:**
- Create: `content/sql/thoughts.yaml`, `content/sql/lesson-01.yaml`, `tests/test_gate.py`
- Modify: `docs/superpowers/specs/2026-11-20-lesson-format-and-checker-design.md` (add `after_run`)

**Interfaces:**
- Consumes: `main` from `checker/__main__.py`.
- Produces: the real lesson that Task 7's gate and the future player read.

**Source:** `docs/lessons/sql-01-draft.md`. Every teacher line, narration line, leading question, reason, walk item and note moves over word for word. Nothing is reworded, shortened or "improved". The owner approved that text.

- [ ] **Step 1: Add `after_run` to the spec**

In the spec's table "Fields common to every step", add this row after `text`:

```
| `after_run` | Optional. Teacher's lines shown after the learner has run a sentence in a `give` or `classmate` step. |
```

- [ ] **Step 2: Write the gate test**

`tests/test_gate.py`:

```python
from pathlib import Path

from checker.__main__ import main

ROOT = Path(__file__).parent.parent


def test_lesson_1_passes(capsys):
    code = main([str(ROOT / "content" / "sql"), "--data", str(ROOT / "data")])
    out = capsys.readouterr().out
    assert code == 0, out
    assert "0 failures, 2 warnings" in out
```

- [ ] **Step 3: Run it to verify it fails**

Run: `uv run pytest tests/test_gate.py -v`
Expected: FAIL, exit code 2 (`ERROR cannot read the lesson files`), because `content/sql` does not exist yet.

- [ ] **Step 4: Write `content/sql/thoughts.yaml`**

Copy the 14 rows of the draft's "Thoughts" table. Identifier first, description second, descriptions verbatim:

```yaml
thoughts:
  count-rows: "`SELECT COUNT(*)` asks how many rows."
  from-table: The table being asked goes after `FROM`.
  star: The star means everything. `SELECT *` shows the rows themselves.
  table-out: A table goes in, a table comes out.
  keep-rows: A yes-or-no question is asked of every row and only the yes rows go on. It is written `WHERE` and comes after the table.
  compare-signs: "Import from maths: `>`, `<` and `=`."
  text-quotes: A word we are looking for wears quotes. A bare word is read as a column's name.
  summary-column: "A summary about a column wraps the column: `AVG(subtotal)`."
  piles: "`GROUP BY` sorts the rows into piles by a column, and the summary is said of each pile."
  one-row-per-pile: One row comes out per pile.
  pile-name: The pile's name has to be asked for, or the numbers come out unlabelled.
  commas: "Import from English: a comma between two things in a list."
  summary-per-pile: What is said about each pile can be any summary, not only a count.
  keep-before-piles: "After the table, the sentence runs in the order things happen: keep rows, then make piles."
```

- [ ] **Step 5: Write `content/sql/lesson-01.yaml` header and steps 1 to 3**

Use these three steps as the template for all 23. Block scalars (`|`) hold teacher text, one paragraph per blank-line-separated block, code in ```sql fences. Short single-line values are plain scalars; quote any that contain `: `, start with a symbol, or contain ` #`.

```yaml
lesson: sql-01
title: From "how many?" to piles
strand: sql
stage: 1
steps:
  - kind: give
    new: [count-rows]
    text: |
      Nearly everything you will be asked about data is a question about a table: how many, how much on average, which ones. We'll answer those from the first minute. There is a table called orders, with one row for every food delivery order. To ask how many rows it has, we say:

      ```sql
      SELECT COUNT(*) FROM orders
      ```

      Give me the count, from orders. Run it.
    shows: ["SELECT COUNT(*) FROM orders"]
    after_run: |
      6,000 orders. SELECT is how SQL says "give me". Type the brackets and the star just as they are for now. They get their reason in a minute.
    note: The first thing the learner sees is an answer to a question. The star and brackets are used before they are explained (rule B3), and the promise is kept in steps 3 and 11.

  - kind: ask
    new: [from-table]
    requires: [count-rows, from-table]
    text: |
      There is another table, called restaurants. How many restaurants are there? Stop and think it out before you type. Nothing here is timed.
    model: SELECT COUNT(*) FROM restaurants
    rows: 1
    result: [[60]]
    narration:
      - 60. The table's name went after FROM and everything else stayed as it was.
      - The same question, asked of a different table. Whichever table you are asking goes after FROM. 60 restaurants.
      - 60. FROM is where you say which table.
    wrong:
      - sql: SELECT COUNT(*) restaurants
        ask: "One restaurant? Read yours aloud: give me the count... from where?"
        why: Without FROM there is no table, and SQL quietly counts nothing in particular.
      - sql: SELECT COUNT(restaurants)
        ask: In the first sentence, where did the table's name sit?
        why: The brackets are not where the table goes.
    walk:
      - Type again the sentence that counted the orders.
      - Which word in it says which table? Put restaurants there.
    note: First typed sentence, and the first rule of engagement, at the moment it matters. Only the table changes from step 1, on purpose, to fix where the table goes.

  - kind: give
    new: [star]
    text: |
      Before we count anything else, look at what you have been counting. In place of the count, put just a star:

      ```sql
      SELECT * FROM orders
      ```

      Run it.
    shows: ["SELECT * FROM orders"]
    after_run: |
      There they are, one row per order. The star is how SQL writes "everything": every row, every column. That one just is. You had typed it already, inside COUNT(*), where it said: count everything, every row.

      Look along the top. Subtotal, delivery_fee, status: we'll use those. A few cells are empty. Leave them for another day.
    note: The raw look borrowed from Opening A. It pays the debt on the star from step 1 and puts the column names in front of the learner before any prompt uses them. The app shows the first rows of the 6,000. The remark about empty cells is marked as something to set aside (rule D4).
```

The template shows the structure. If its wording differs from the draft anywhere, the draft wins.

Then convert steps 4 to 23 the same way, using this table for every field that is not teacher text:

| Step | kind | new | imports | requires | other fields |
|---|---|---|---|---|---|
| 4 | ask | | | star, from-table | model `SELECT * FROM couriers`; rows 200 |
| 5 | give | table-out | | | |
| 6 | ask | keep-rows | compare-signs | star, from-table, keep-rows, compare-signs | model `SELECT * FROM orders WHERE subtotal > 100`; rows 632 |
| 7 | ask | | | count-rows, from-table, keep-rows, compare-signs | `thinking_order`; model `SELECT COUNT(*) FROM orders WHERE delivery_fee < 5`; rows 1; result `[[3033]]` |
| 8 | classmate | text-quotes | | | `broken: SELECT COUNT(*) FROM orders WHERE status = cancelled`; `shows: ["SELECT COUNT(*) FROM orders WHERE status = 'cancelled'"]`; `after_run` |
| 9 | ask | | | count-rows, from-table, keep-rows, compare-signs, text-quotes | model `SELECT COUNT(*) FROM couriers WHERE vehicle = 'bike'`; rows 1; result `[[73]]` |
| 10 | ask | | | star, from-table, keep-rows, compare-signs, text-quotes | model `SELECT * FROM restaurants WHERE cuisine = 'pizza'`; rows 8 |
| 11 | ask | summary-column | | from-table, summary-column | model `SELECT AVG(subtotal) FROM orders`; rows 1; result `[[60.4]]` |
| 12 | ask | | | from-table, summary-column, keep-rows, compare-signs | `friction: true`; model `SELECT AVG(delivery_fee) FROM orders WHERE subtotal > 100`; rows 1; result `[[5.32]]` |
| 13 | aside | | | | |
| 14 | ask | | | from-table, summary-column, keep-rows, compare-signs, text-quotes | `thinking_order`; model `SELECT AVG(subtotal) FROM orders WHERE status = 'delivered'`; rows 1; result `[[60.43]]` |
| 15 | give | piles | | | `shows: ["SELECT COUNT(*) FROM couriers GROUP BY vehicle"]`; `after_run` |
| 16 | ask | one-row-per-pile | | count-rows, from-table, piles, one-row-per-pile | model `SELECT COUNT(*) FROM restaurants GROUP BY city`; rows 4; result `[[15],[6],[14],[25]]`; `accepts: ["SELECT city, COUNT(*) FROM restaurants GROUP BY city"]`; `narration_ahead` is the draft's fourth narration line |
| 17 | ask | pile-name | commas | count-rows, from-table, piles, one-row-per-pile, pile-name, commas | `any_column_order: true`; model `SELECT vehicle, COUNT(*) FROM couriers GROUP BY vehicle`; rows 3; result `[["bike",73],["carro",17],["moto",110]]` |
| 18 | ask | | | count-rows, from-table, piles, one-row-per-pile, pile-name, commas | `any_column_order: true`; model `SELECT city, COUNT(*) FROM restaurants GROUP BY city`; rows 4; result `[["Belo Horizonte",15],["Curitiba",6],["Rio de Janeiro",14],["São Paulo",25]]` |
| 19 | ask | summary-per-pile | | from-table, summary-column, piles, one-row-per-pile, pile-name, commas, summary-per-pile | `any_column_order: true`; model `SELECT status, AVG(subtotal) FROM orders GROUP BY status`; rows 2; result `[["cancelled",59.99],["delivered",60.43]]` |
| 20 | classmate | | | count-rows, from-table, piles, one-row-per-pile, pile-name, commas | `shows: ["SELECT COUNT(*) FROM orders GROUP BY restaurant_id"]`; `any_column_order: true`; model `SELECT restaurant_id, COUNT(*) FROM orders GROUP BY restaurant_id`; rows 60 |
| 21 | ask | keep-before-piles | | from-table, summary-column, keep-rows, compare-signs, text-quotes, piles, one-row-per-pile, pile-name, commas, summary-per-pile, keep-before-piles | `friction: true`; `any_column_order: true`; model `SELECT restaurant_id, AVG(subtotal) FROM orders WHERE status = 'delivered' GROUP BY restaurant_id`; rows 60 |
| 22 | recap | | | | |
| 23 | cold-check | | | count-rows, from-table, keep-rows, compare-signs, text-quotes, piles, one-row-per-pile, pile-name, commas, keep-before-piles | `any_column_order: true`; model `SELECT city, COUNT(*) FROM couriers WHERE vehicle = 'bike' GROUP BY city`; rows 4; result `[["Belo Horizonte",9],["Curitiba",13],["Rio de Janeiro",18],["São Paulo",33]]`; no `narration`, `wrong` or `walk` |

Rules for the rest:

1. **Steps 3, 5 and others:** `new` and `requires` come from the table above, not from the draft's prose.
2. **Typed steps** also copy `narration` (every line, including empty ones as `""`), `wrong` and `walk` from the draft's "Narration", "If they write" and "Walk" bullets.
3. **`wrong` entries:** each needs a full SQL sentence. The draft wrote some with `...`. Write them in full:

| Step | Draft wrote | Write |
|---|---|---|
| 7 | `... WHERE delivery fee < 5` | `SELECT COUNT(*) FROM orders WHERE delivery fee < 5` |
| 9 | `... WHERE vehicle = bike` | `SELECT COUNT(*) FROM couriers WHERE vehicle = bike` |
| 9 | `... WHERE vehicle = 'Bike'` | `SELECT COUNT(*) FROM couriers WHERE vehicle = 'Bike'` |
| 10 | `... WHERE cuisine = pizza` | `SELECT * FROM restaurants WHERE cuisine = pizza` |
| 14 | `... WHERE status = delivered` | `SELECT AVG(subtotal) FROM orders WHERE status = delivered` |
| 16 | `... GROUP city` | `SELECT COUNT(*) FROM restaurants GROUP city` |
| 21 | `... FROM orders GROUP BY restaurant_id WHERE status = 'delivered'` | `SELECT restaurant_id, AVG(subtotal) FROM orders GROUP BY restaurant_id WHERE status = 'delivered'` |

4. **A `wrong` entry with no leading question** (the draft's `AVERAGE` case in step 11) uses `tell:` with the teacher's sentence and no `ask:`.
5. **The draft's italic writer's notes** become `note:`.
6. **The draft's "Check", "Requires" and "Result" lines** are not copied as text. They became the fields in the table.
7. **The draft's "No ladder and no narration" bullet in step 23** becomes the absence of `narration`, `wrong` and `walk`.
8. **Step 20:** the learner sees Ana's sentence and the teacher's remarks (`text`), then types the repair (`model`).
9. **Step 21's prompt, step 12's prompt and every `thinking_order`:** copy the draft's "Thinking-order version" text into `thinking_order`.

- [ ] **Step 6: Check that teacher text was copied word for word**

Run this one-off check from the repository root. It is not committed:

```bash
uv run python - <<'EOF'
import yaml
draft = open("docs/lessons/sql-01-draft.md", encoding="utf-8").read()
lesson = yaml.safe_load(open("content/sql/lesson-01.yaml", encoding="utf-8"))
skip = {"kind", "new", "imports", "requires", "model", "sql", "shows", "broken", "accepts",
        "rows", "result", "lesson", "strand", "stage", "title", "friction", "any_column_order"}
bad = []
def walk(x, n):
    if isinstance(x, dict):
        for k, v in x.items():
            if k not in skip:
                walk(v, n)
    elif isinstance(x, list):
        for v in x:
            walk(v, n)
    elif isinstance(x, str):
        for line in x.splitlines():
            line = line.strip()
            if line and not line.startswith("```") and line not in draft:
                bad.append((n, line[:90]))
for n, step in enumerate(lesson["steps"], 1):
    walk(step, n)
print(len(lesson["steps"]), "steps")
for b in bad:
    print("NOT IN DRAFT:", b)
EOF
```

Expected: `23 steps` and no `NOT IN DRAFT` lines. A listed line is either a copy mistake, to be fixed, or a line the draft wraps differently (for example a `thinking_order` the draft writes after an italic label), which is fine once checked by eye against the draft.

- [ ] **Step 7: Run the checker on the real lesson**

Run: `uv run python -m checker content/sql`
Expected: no `FAIL` lines, two `WARN` lines (`steps 1 to 3` and `steps 15 to 17`), the spacing report matching the draft's table, and `0 failures, 2 warnings`.

If a `FAIL` appears, read it: it is either a copy mistake in the YAML, or a real fault in the lesson the hand checks in the draft missed. In the second case stop and tell the owner before changing teacher text. If the shape check flags a pair the draft's hand table cleared, show the owner the two answers.

- [ ] **Step 8: Run the gate test**

Run: `uv run pytest tests/test_gate.py -v`
Expected: PASS.

- [ ] **Step 9: Commit**

```bash
git add content tests/test_gate.py docs/superpowers/specs
git commit -m "Convert SQL lesson 1 to YAML and pass the checker on it"
```

---

### Task 7: Broken-copy gate, docs and finish

**Files:**
- Modify: `tests/test_gate.py` (append), `README.md`, `CLAUDE.md`, `docs/07-roadmap.md`

**Interfaces:**
- Consumes: the real `content/sql` from Task 6.

- [ ] **Step 1: Write the second gate test**

Replace the import block of `tests/test_gate.py` and append the test, so the whole file reads:

```python
import shutil
from pathlib import Path

import yaml

from checker.__main__ import main

ROOT = Path(__file__).parent.parent


def test_lesson_1_passes(capsys):
    code = main([str(ROOT / "content" / "sql"), "--data", str(ROOT / "data")])
    out = capsys.readouterr().out
    assert code == 0, out
    assert "0 failures, 2 warnings" in out


def test_broken_copy_of_lesson_1_fails_with_clear_messages(tmp_path, capsys):
    shutil.copytree(ROOT / "content" / "sql", tmp_path / "sql")
    path = tmp_path / "sql" / "lesson-01.yaml"
    lesson = yaml.safe_load(path.read_text(encoding="utf-8"))
    steps = lesson["steps"]
    steps[6]["model"] = "SELECT COUNT(*) FROM orders WHERE delivry_fee < 5"
    steps[17]["model"] = steps[16]["model"]
    steps[3]["requires"].append("keep-rows")
    path.write_text(yaml.safe_dump(lesson, allow_unicode=True), encoding="utf-8")

    code = main([str(tmp_path / "sql"), "--data", str(ROOT / "data")])
    out = capsys.readouterr().out

    assert code == 1
    assert "FAIL sql-01 step 7: model answer does not run: no such column: delivry_fee" in out
    assert "FAIL sql-01 step 18: same shape as step 17" in out
    assert "FAIL sql-01 step 4: requires 'keep-rows', which no earlier step introduces" in out
```

- [ ] **Step 2: Run the whole suite**

Run: `uv run pytest -v`
Expected: all pass, including both gate tests.

- [ ] **Step 3: Update the docs that say there is no code**

In `README.md`, replace the status paragraph's first sentence `**Status (20 Nov 2026): design only. There is no code in this repository yet.**` with:

```
**Status (20 Nov 2026): design and the first lesson are done. The only code is the content checker.** Lesson 1 of the SQL strand is in `content/sql/` and `uv run python -m checker content/sql` checks it. There is no player yet.
```

and change the sentence after it so it says: `The next step is to build the smallest player that can run lesson 1.`

In `CLAUDE.md`, replace the "State of the repository" paragraph with:

```
Design, one full lesson script, and a content checker. The checker is the only code. Run it with `uv run python -m checker content/sql`, and run the tests with `uv run pytest`. There is no player yet. Do not build one without the owner's go-ahead: `docs/07-roadmap.md` puts the player at milestone 4, after the owner has read the checked lesson.
```

and in the "Working conventions" list change the line `**Every expected answer must run.** ... Build this check early and run it after every content change.` by appending: ` The checker does this. Run it after every content change.`

In `docs/07-roadmap.md`, under milestone 3 add one line after "Done when": `Done 20 Nov 2026: the checker passes on lesson 1 and fails on a broken copy. See `docs/superpowers/specs/2026-11-20-lesson-format-and-checker-design.md`.`

- [ ] **Step 4: Run the checker and the suite one last time**

Run: `uv run python -m checker content/sql && uv run pytest -q`
Expected: `0 failures, 2 warnings`, then all tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_gate.py README.md CLAUDE.md docs/07-roadmap.md
git commit -m "Add the broken-copy gate and update the docs for milestone 3"
```

- [ ] **Step 6: Hand back to the owner**

Do not merge. Report: the branch name, the checker output on lesson 1, the two warnings, and the passing broken-copy test. Ask whether to merge `milestone-3-checker` into `main`.
