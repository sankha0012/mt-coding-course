# Handover, 25 Nov 2026

For a fresh agent that starts when the owner sits lessons. Read `CLAUDE.md` first, then this file. Everything below is on `main` and pushed (last commit `6334636`).

## State

The course is built and every lesson is written. The owner has sat **SQL lesson 1 only**. Nothing else has met a real learner.

| Part | State |
|---|---|
| Core course (`content/course.yaml`, `course:`) | 27 lessons and two cold sittings: SQL 1 to 9, Python 1 to 10, pandas 1 to 5, ML 1 to 3, cold A and B. Written, checker clean, SQL 1 sat. |
| Optional MongoDB extra (`extras:`) | MG-1 to MG-6 and cold sitting C (`content/mongo/lesson-01..07.yaml`). Written, checker clean, played through the engine in tests, **not sat**. |
| Player | FastAPI app. Course panel, Try pane (SQL, Python, MongoDB), Data tab, Ask tab (Gemini or Groq), restart a lesson. |
| Tests | 441 pass (about 3 minutes). `uv run python -m checker content`: 0 failures, 5 warnings. |

Decisions are in `docs/06-decisions.md` (C1 to C29). Recent ones: C22 Ask tab, C23 slips accepted silently, C24 Data tab, C25 Course panel, C26 and C28 MongoDB as an optional extra, C27 lessons open by prerequisites, C29 cold sitting C on Nobel data.

## How to run

```bash
uv run python -m player --skip-check          # the player on port 8770 (the desktop launcher does this)
uv run python -m player.report                # miss report and the questions asked (reads progress/progress.db)
uv run python -m checker content              # about 30 seconds, needs mongod for the MongoDB lessons
uv run pytest -q                              # about 3 minutes
```

Keys for the Ask tab are in the git-ignored `.env` (`GEMINI_API_KEY`, `GROQ_API_KEY`, `GEMINI_MODEL`, `GROQ_MODEL`). The player must be restarted after any code or content change, and the page hard-refreshed (Cmd+Shift+R).

**Never delete, overwrite or reset `progress/progress.db`.** To read it for a report, copy it to a scratch folder first and pass `--progress <folder>` to `player.report`. Test the player only with `--progress` pointing at a scratch folder.

MongoDB needs `mongod` installed (it is at `/opt/homebrew/bin/mongod`, v8.2.4). The program starts it privately on a spare port in a temporary folder and stops it on exit, even if killed (a watcher process cleans up). Without `mongod` the MongoDB lessons are left out and named at start up. `mongod --fork` does not work on macOS, so it is started as a background process.

## What to do when the owner sits

The owner reports a problem with a step number and what they typed. The workflow that has worked all session:

1. Copy `progress/progress.db` to a scratch folder and run `player.report` on the copy. It lists the steps most missed, the most common miss, and the questions asked in the Ask tab. A step with many misses or questions is a step to revise.
2. Reproduce with the real engine before changing anything. Replay the owner's exact inputs (an `Engine` with a `Runner`, or the app through `TestClient` on a scratch progress folder).
3. Fix the cause, test first, and keep to the rules in `CLAUDE.md` (1 to 10) and `docs/08-authoring-lessons.md`, above all **the clarity rule**: a typed prompt names the collection or table, the fields, the rows to keep and what to show. The owner has complained twice that conversational tone made prompts ambiguous.
4. Run the full suite and the checker. Commit when asked, push when asked. **The owner asks for each push explicitly ("Push main").** Commit messages end with the attribution line the harness gives.

Lesson revisions are driven by the miss log. Do not rewrite lessons the owner has not sat, except to apply the clarity rule.

## Known gaps (none blocks sitting)

- **Real MongoDB lessons have not been clicked through in a browser.** The screen was checked with a stub lesson, and the six real lessons plus cold sitting C are played through the real engine by `tests/test_mongo_lessons.py` (every model answer typed, and again missing every typed step once). Check the first real Mongo sitting in the browser.
- **Ask tab on a MongoDB step** gives the model the collections and their field paths (`ai.schema_lines`, tested), but was not tried live against Gemini or Groq.
- **The "this piece differs" hint** after a repeated miss (`Engine._differs`) exists for SQL only. A Python or MongoDB learner who keeps mistyping the shown answer just sees it again. Extend it if a sitting shows that loop.
- **The Data tab follows the lesson's language,** not the Try pane's tab. In a SQL lesson it shows the SQL tables even if the learner is trying MongoDB.
- **Checker limit:** a step's expected `result` cannot hold a nested empty list (`[]`). MG-5 step 19 gives only `rows: 1` for that reason.
- **Unsorted `$group` has no fixed order.** A wrong answer that depends on it can pass by luck, and an `ordered: true` step with a tie fails a correct answer now and then. `docs/08-authoring-lessons.md` has the rule. Check any new sorted step for ties.
- Two cosmetic things noticed and left: with both the Course panel and the Try pane open the lesson column is narrow on a 1024 px window, and the Course panel stacks above the lesson on a narrow window.

## Where things are

- Lessons: `content/<strand>/lesson-NN.yaml` (YAML is the source of truth; `tools/lessongen.py` formats them). The order and the extras: `content/course.yaml`. Maps: `docs/maps/` (`sql.md`, `python.md`, `pandas-ml.md`, `mongodb.md`).
- Player: `player/` (`app.py`, `engine.py`, `runner.py`, `store.py`, `ai.py`, `llm.py`, `tables.py`, `report.py`, `web/`). Engines and runners shared with the checker: `checker/` (`checks.py`, `pyrun.py`, `mongo.py`, `mongoparse.py`, `lesson.py`).
- Data: `data/*.csv` (SQL, Python, pandas), `data/mongo/*.jsonl` (built by `tools/build_mongo_data.py`), `data/real/olist/` (git-ignored, CC BY-NC-SA, cold sittings A and B), `data/real/nobel/` (committed, CC0, cold sitting C; `tools/fetch_nobel.py`).
- Specs and plans of the larger features: `docs/superpowers/specs/` and `docs/superpowers/plans/`.
- Owner preferences: terse replies, questions through the question tool, no em dashes in docs, keys only in `.env`, the owner reviews by sitting. The sibling repository `../live-coding-gym` holds timed practice and mock rounds, which this course sends the learner to.
