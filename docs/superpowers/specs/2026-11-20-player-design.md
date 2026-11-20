# The lesson player

Milestone 4 of `docs/07-roadmap.md`: the smallest player that can run SQL lesson 1. Approved in outline by the owner on 20 Nov 2026. This file fixes the details the build needs. It builds on `2026-11-20-lesson-format-and-checker-design.md` and follows `docs/05-app-requirements.md`.

## Goal

The owner opens a local page and completes SQL lesson 1 from the first line to the cold check, with the correction ladder, narration, returns, and progress that survives a restart. Nothing for Python.

Done when: the owner completes lesson 1 in the app.

## Approach

The server holds the state machine. The browser only renders what the server sends and posts what the learner does. The ladder and the returns are therefore plain Python that pytest can reach.

## Layout

```
player/__init__.py
player/__main__.py    command line: starts the server
player/sql.py         runs the learner's SQL
player/engine.py      the sitting as a state machine
player/store.py       the progress file
player/app.py         FastAPI app
player/report.py      miss report
player/web/           index.html, app.js, style.css (no build step)
content/ui.yaml       the teacher's course-wide lines
progress/             progress.db (gitignored)
tests/                test_sql.py, test_engine.py, test_store.py, test_app.py, test_play.py
```

Dependencies: `fastapi` and `uvicorn` at runtime, `httpx` in the dev group (for FastAPI's test client). Decision O1 chose the FastAPI stack.

Lesson text never lives in `player/`. The few lines the teacher says on every lesson (the ladder's first rung, the slip view, the show-the-answer line) live in `content/ui.yaml`. Button labels and other interface chrome are in `web/`.

## `content/ui.yaml`

```yaml
again:          # rung 1, first miss. One is picked at random, not the same twice in a row.
  - Again, thinking it through, not from memory.
  - ...
slip:           # shown with the two spellings side by side
  - ...
walk_intro:
  - ...
show_answer:    # rung 4
  - ...
```

Each key holds a list of variants, since the wording keeps changing (rule D1). The build writes two or three variants per key in the teacher's voice, and the owner reviews them with the plan.

## Running the learner's SQL: `sql.py`

- `run_sql(conn, text, limit=20) -> Result` with `Result(error, columns, rows, total)`. `rows` holds at most `limit` rows and `total` is the real count. A 6,000-row result never reaches the page in full.
- Before running, a word in double quotes becomes a word in single quotes (rule R11). Double quotes inside single-quoted text are left alone. The database in use has double-quoted words disabled, so without this the learner's `"bike"` would be read as a column.
- Only reads are allowed. A SQLite authorizer permits `SELECT`, `READ`, `FUNCTION` and `RECURSIVE` and denies everything else, including `ATTACH` and `PRAGMA`.
- A statement still running after 5 seconds is stopped with a progress handler. The text is "That took too long, so it was stopped." It is shown as ordinary output (rule R13).
- An SQLite error is returned as `error`, the database's own message.
- One connection, opened from `checker.data.load_db`, guarded by a lock.
- `normalise(text) -> str`: the quote fix, lower case, whitespace collapsed, one trailing semicolon dropped. Used for slips and for recognising known wrong answers.

## The state machine: `engine.py`

A `Sitting` is built from the lesson's steps, the database and a random source. Every method takes the persisted state and returns the new state, the transcript items to append, and the events to log. It touches neither the web nor the progress file.

### State

```json
{
  "pos": 0,
  "phase": "show",
  "playing": {"step": 0, "variant": "main"},
  "misses": 0,
  "why": null,
  "queue": [{"step": 1, "due": 4}],
  "returned": [1],
  "last_narration": null
}
```

`pos` is the index of the step being played. `phase` is one of `show`, `run`, `answer`, `continue` and `done`. `playing.variant` is `main` or `return`. `misses` counts misses on the current attempt chain. `why` holds the `why` of a leading question already shown, to be stated after the learner gets it right. `queue` holds returns waiting, each with the step and the position from which it may play. `returned` lists steps that have already had a return.

### Transcript items

A list the browser renders in order. Each is a small object with a `type`:

| `type` | Fields | Shown as |
|---|---|---|
| `teacher` | `text`, optional `style` (`aside`, `recap`) | The teacher's voice, in serif. `text` is paragraphs, ```` ```sql ```` fences and `inline code`. |
| `learner` | `sql` | What the learner typed or ran, in mono |
| `result` | `columns`, `rows`, `total`, `error`, optional `label` | A table, or the error as plain output |
| `compare` | `yours`, `usual` | The two spellings side by side |

### What the learner is asked to do next: `pending`

| `mode` | Meaning |
|---|---|
| `continue` | A Continue button |
| `run` | A Run button for the teacher's sentence, which is `sql` |
| `answer` | The editor, with `step` and `variant` |
| `done` | The sitting is over. A "Sit this lesson again" button. |

### Steps

- **`give`, `aside`, `recap`, and `classmate` without a `model`.** Append the `text`. If the step has `shows`, `pending` is `run` with the last `shows` sentence. Running it appends a `learner` item, a `result` item, then `after_run` as a `teacher` item. Then `continue`. With no `shows`, `continue` directly.
- **A typed step** (has a `model`, and is not a cold check). Append the `text` as the prompt and set `pending` to `answer`. On a submitted answer:
  - **Correct.** The learner's result equals the model's result, or the result of one of the step's `accepts`, under the step's `ordered` and `any_column_order`. Append `learner` and `result` items. If a leading question's `why` is waiting, append it. Then:
    - if `normalise` of the answer equals `normalise` of the model and the raw text differs, append a `compare` item and a `slip` line from `ui.yaml`;
    - else pick one `narration` line at random from the step's lines, the empty line included, never the same text as `last_narration`; append it unless it is empty.
    - A step that had one or more misses is queued for a return (below). `continue`.
  - **Miss.** Append `learner` and `result` items, add one to `misses`, and climb the ladder.
- **A cold check.** The editor, then no ladder and no narration. Append `learner`, then two `result` items labelled "Yours" and "Model", then `after_run`. `continue`, then `done`.

### The ladder

Counted by `misses` on one step in one variant, in the order of rule E3:

| Miss | What is shown |
|---|---|
| 1 | A line from `ui.yaml` `again`. If the step has `thinking_order`, it follows as a second teacher paragraph. |
| 2 | If the attempt matches a known wrong answer: its `ask`, or its `tell`. The `why` is stored in state. If no wrong answer matches: go straight to the walk. |
| 3 | A line from `ui.yaml` `walk_intro`, then the step's `walk` as numbered prompts. Then the editor again. Skipped to the next row if the step has no `walk`. |
| 4 and after | A line from `ui.yaml` `show_answer`, then the model answer in a code block. The learner types it. A typo is a miss that shows the same again. |

The ladder never says "wrong", never counts aloud, and never shows a red mark.

A **known wrong answer** matches when both the learner's answer and the `wrong` entry's `sql` run and give the same result under the step's flags, or when their `normalise` forms are equal. Matching returns the first entry in the lesson's order.

### Returns

A step resolved after one or more misses, with no return yet, is queued with `due = step index + 3` and added to `returned` when played.

Before step `j` plays, every queued return with `due <= j` plays first, in queue order. Before a cold check plays, every queued return plays. A return plays as a typed step using the step's `return.text` and `return.model`, with the return's own `narration`, `accepts`, `rows` and `result` flags. There is no leading question and no walk. A miss on a return shows an `again` line once, then the model answer to type. A return is never queued again. A step with no `return` block is played again only through its own ladder.

If a queued return remains at the end of a lesson with no cold check, it plays before `done`.

### Events

Every submitted answer logs one event: `step` (1-based), `variant`, `typed`, `outcome`, and `misses` (misses on this chain before this answer). `outcome` is `correct`, `slip`, `miss`, or `shown` for a cold check.

## Progress: `store.py`

`progress/progress.db`, or the folder named by `MT_PROGRESS_DIR`. Created if missing. Opened with `CREATE TABLE IF NOT EXISTS`. Nothing is ever dropped, overwritten, or deleted, and the app has no code path that does.

```sql
CREATE TABLE IF NOT EXISTS runs (
  id INTEGER PRIMARY KEY, lesson TEXT, started_at TEXT, finished_at TEXT, state_json TEXT);
CREATE TABLE IF NOT EXISTS items (
  run_id INTEGER, seq INTEGER, json TEXT, PRIMARY KEY (run_id, seq));
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY, run_id INTEGER, ts TEXT, step INTEGER, variant TEXT,
  typed TEXT, outcome TEXT, misses INTEGER);
```

Each action is one transaction: the new state, the new items, and the events together. Opening the app resumes the most recent run with no `finished_at`, or creates one. "Sit this lesson again" creates a new run and leaves the old one.

## Web API: `app.py`

Every response is `{"run_id", "items", "pending"}`, where `items` is the whole transcript.

| Route | Does |
|---|---|
| `GET /api/run` | Resume or start, and return the view |
| `POST /api/answer` `{"sql"}` | Submit an answer. 409 unless `pending.mode` is `answer`. |
| `POST /api/next` | Continue, or run the shown sentence when `pending.mode` is `run`. 409 otherwise. |
| `POST /api/run/new` | Start a new run. 409 unless `pending.mode` is `done`. |

`GET /` serves `web/index.html`, and `/static` serves the rest of `web/`.

## Start up: `__main__.py`

```
uv run python -m player [--port 8770] [--content content/sql] [--data data] [--progress progress]
```

Before serving, it runs `checker.checks.check_all` on the lesson folder. If any `FAIL` is found, it prints them and exits with code 1, so a lesson that fails the checker is never played. Otherwise it prints `http://127.0.0.1:8770` and serves on `127.0.0.1` only. It plays the first lesson in the folder.

## The screen: `web/`

The schematic the owner saw. One column. Earlier items fade a little and scroll. The teacher is in the serif voice, code in mono. A `result` is a table of at most 20 rows, with "N rows in all" under it when `total` is larger. An `error` is plain text. A `compare` is two code boxes side by side. The editor is a plain `<textarea>` with no autocomplete and no spell check, and an empty answer is not sent. Run and Continue are ordinary buttons. Ctrl or Command with Enter runs the answer.

Absent on purpose, by rules 5 and 6 and R17 to R20: a timer, score, streak, percentage, step counter, progress bar, notes, reference panel, glossary, multiple choice, red, and the word "wrong". There is no pause before typing (open decision O5): "stop and think" is only in the lesson text, and the first sitting decides what to add.

## The miss report: `report.py`

`uv run python -m player.report` prints, for each step and variant that has events: the number of answers, how many were right the first time, the number of misses, the most common typed text among misses, and the thoughts the step requires. Steps are listed with the most misses first (R23).

## Tests

- `test_sql.py`: the quote fix, the authorizer (`ATTACH` and `PRAGMA` refused, `SELECT` allowed), the timeout, the row cap and total, error text.
- `test_engine.py`: each rung of the ladder, a known wrong answer, a miss that matches none, the slip view, narration never the same twice in a row, a return queued and played at the right position, a return missed, a cold check, a lesson with returns waiting at the end.
- `test_store.py`: resume the latest unfinished run, a new run keeps the old, a reopened file keeps its rows, nothing is deleted.
- `test_app.py`: each route, the 409 cases, a run resumed after the app is rebuilt on the same progress file.
- `test_play.py`, the gate: walk all of lesson 1 through the API using each step's `model`, with `continue` and `run` where needed. It must reach `done` with no miss events. A second walk misses every typed step once and must reach `done`, with a return played for each step that has one.

All tests use a temporary progress folder, never `progress/`.

## Not built

A pause before typing (O5), a typed English plan (O3), Python and pandas, a report beyond the one listing, a way to edit lessons in the app, accounts, and anything for stage 3. Each is added when it is needed.
