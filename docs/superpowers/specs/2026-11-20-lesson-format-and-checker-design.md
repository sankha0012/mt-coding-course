# Lesson file format and content checker

Milestone 3 of `docs/07-roadmap.md`. Approved in outline by the owner on 20 Nov 2026 (one YAML file per lesson, a Python checker). This file fixes the details the build needs.

## Goal

Turn the approved SQL lesson 1 (`docs/lessons/sql-01-draft.md`) into plain files, and build the checker that enforces the seven checks of `docs/04-script-format.md`.

Done when: the checker passes on lesson 1, and fails with a clear message on a deliberately broken copy of it.

This is the first code in the repository. It reads lesson files and runs SQL. It is not the player.

## Layout

```
content/sql/thoughts.yaml     every thought of the SQL strand
content/sql/lesson-01.yaml    lesson 1
checker/                      the checker (Python package)
tests/                        pytest
pyproject.toml                Python 3.12, uv; pyyaml, pytest
```

Lessons of a strand are read in filename order. A thought introduced in an earlier lesson counts as introduced for a later one. Lesson text never lives in `checker/`.

## `thoughts.yaml`

```yaml
thoughts:
  count-rows: SELECT COUNT(*) asks how many rows.
  from-table: The table being asked goes after FROM.
```

Identifier, then the one-line description. Order does not matter.

## Lesson file

```yaml
lesson: sql-01
title: From "how many?" to piles
strand: sql
stage: 1
steps:
  - kind: give
    new: [count-rows]
    text: |
      ...teacher's lines, Markdown, code in fences...
    shows: ["SELECT COUNT(*) FROM orders"]
    note: Why this step is here. Never shown.
```

Steps are a list. A step's number is its position, counting from 1. Messages use that number.

### Fields common to every step

| Field | Meaning |
|---|---|
| `kind` | `give`, `ask`, `classmate`, `aside`, `recap` or `cold-check` |
| `text` | Teacher's lines, Markdown. For a typed step this is the prompt. |
| `new` | List of thought ids introduced here. Omit if none. |
| `imports` | List of thought ids the learner already owns and the step names out loud. They count as introduced here but not towards the limit of one new thought. |
| `requires` | List of thought ids the step's answer needs. Omit for steps with no `model`. |
| `friction` | `true` for a step deliberately not broken down. |
| `note` | Writer's note. Never shown. |

### Shown sentences

`shows` is a list of SQL sentences the learner sees in a `give` or `classmate` step. Each must run. `broken` is one SQL sentence a classmate wrote that must fail with an error.

### Typed steps

A step with a `model` is typed. It has these fields as well:

| Field | Meaning |
|---|---|
| `model` | One SQL answer that runs against `data/`. |
| `thinking_order` | Optional. The same prompt phrased table first. |
| `rows` | Optional. Number of rows the model's result has. |
| `result` | Optional. The full result for a small answer, as a list of lists. Floats are compared to two decimals and row order is ignored. |
| `ordered` | `true` if row order matters. Default `false`. |
| `any_column_order` | `true` if the columns may come in either order. Default `false`. |
| `accepts` | Optional list of other SQL answers also treated as correct. Each must run and return rows. They need not match the model's result. |
| `narration` | List of strings the teacher may say after a correct answer. An empty string is a silent option. |
| `narration_ahead` | Optional. A line for a learner who wrote an `accepts` answer. |
| `wrong` | List of known wrong answers. See below. |
| `walk` | List of smaller prompts for rung 3 of the ladder. |

`kind: classmate` may carry a `model` when the learner repairs the classmate's sentence. `kind: cold-check` has a `model` and none of `narration`, `wrong` or `walk`: nothing is laddered or narrated.

### Known wrong answers

```yaml
wrong:
  - sql: SELECT COUNT(*) restaurants
    ask: One restaurant? Read yours aloud...
    why: Without FROM there is no table.
  - sql: SELECT AVERAGE(subtotal) FROM orders
    tell: The word is shorter, AVG. That spelling just is.
```

`sql` is a full sentence. `ask` is the leading question for rung 2, `why` is the reason it matters, and `tell` is a plain statement used where there is nothing to ask. Each entry needs `ask` or `tell`.

## How SQL is run

A scratch in-memory SQLite database is built from `data/orders.csv`, `restaurants.csv` and `couriers.csv` each time the checker runs. The files are never modified.

- An empty cell becomes `NULL`.
- A column whose non-empty cells all read as whole numbers becomes `INTEGER`, then all as numbers `REAL`, otherwise `TEXT`.

Results compare as multisets of rows. Column names are ignored. Floats round to six places. With `any_column_order`, the values inside each row are sorted before comparing. With `ordered`, row order matters.

## The checks

Each check names the lesson and step in its message, for example `FAIL sql-01 step 7: model answer does not run: no such column: delivry_fee`.

| # | Check | Outcome |
|---|---|---|
| 1 | Every `model`, `accepts` entry and `shows` entry runs. A `model` returns at least one row, and matches `rows` and `result` where given. A `broken` entry fails with an error. | fail |
| 1b | Every `wrong` entry gives an error or a result that differs from the model's, under the step's comparison rules. | fail |
| 2 | Audit. Every id in `new`, `imports` and `requires` exists in `thoughts.yaml`. Every `requires` id was introduced in an earlier step, in this lesson or an earlier one, or in this step. No thought is introduced twice. | fail |
| 3 | At most one id in `new` per step. | fail |
| 4 | No shape repeat. For each pair of consecutive typed steps, tokenise both models (case ignored, quoted text as one token) and compare them. If they differ in one contiguous run of tokens, the pair is a shape repeat. | fail |
| 5 | Spacing. For each thought, list the steps that require it after its introduction and the gaps between them. | report |
| 6 | Every typed step except `cold-check` has at least two non-empty `narration` lines. | fail |
| 7 | Load shape. List the steps that introduce a thought. Warn when three or more steps in a row do. | report, with warnings |

Checks 5 and 7 print text and never fail the run. Lesson 1 has two runs of three new thoughts (steps 1 to 3 and 15 to 17) on purpose, so the warning is expected there and the writer reads it.

## Command and output

```
uv run python -m checker content/sql
```

Options: `--data data` (default `data`). Prints `FAIL` lines, then the two reports, then a one-line summary. Exit code 1 if any `FAIL`, else 0.

## Tests

Pytest. A small good lesson is built in each test and mutated to break one check at a time, so every check has a test that fails it and a message that is asserted. Two further tests use the real files:

- `content/sql` passes with no `FAIL`.
- A copy of lesson 1 with a typo in one model answer, a repeated shape, and a thought used before it is introduced fails with the three expected messages. The copy lives in a temporary directory and is not committed.

## Conversion of lesson 1

Teacher text moves over verbatim. The draft's list of thoughts becomes `thoughts.yaml`. Every typed step gets `rows` or `result` from the results quoted in the draft. Every "If they write" entry becomes a `wrong` entry with its full SQL sentence, since the draft elided parts with `...`. `docs/lessons/sql-01-draft.md` stays as the frozen copy the owner approved. From then on the YAML is the source and edits go there.

## Not built

A step-by-step walk check, a player, a report from the miss log, other strands, Portuguese, a Markdown renderer for review. Each is added when it is needed.
