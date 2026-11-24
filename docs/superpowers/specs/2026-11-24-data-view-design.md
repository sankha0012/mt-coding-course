# The Data tab: see the tables without scrolling

Status: draft for the owner's review, 24 Nov 2026. Decision C24 (below) records it once approved.

## Goal

A question about a column name or a value often needs a look at the dataset. Today the learner scrolls up through the transcript to find a result that shows it. The right pane gets a Data tab that always shows the tables of the step now waiting.

## Rules it must respect

- Rule 6 (no reference panel, cheat sheet or notes): the tab shows the material the learner works on, as the course's own data. It carries no lesson text, no syntax, no earlier prompts and no earlier answers.
- Rule 3 (nothing is asked before its parts are given): unaffected. Rows of a table give no method.
- Rule 5 (no pressure): no timer, count or score. A row count of a table is a fact about the data, not about the learner.
- Rule 4: the tab never touches the engine, the ladder, the returns queue or the `events` table.
- Rule 10: the tab's few labels ("Data", "empty") are interface words, not lesson text. They live in the page, as the other pane labels do.

## Decisions taken with the owner (24 Nov 2026)

1. Show data only: tables, columns and rows. Not the prompt, not the last code, not earlier answers.
2. It lives as a **Data** tab in the existing right pane, beside **Try**.
3. Each table shows its column names, its row count and its **first 10 rows**. No paging.

## Design

### The pane

The pane header holds two tabs, **Try** and **Data**, and the close button. The Try view is exactly as today (SQL and Python tabs, editor, Run, output). The Data view is new. When the pane is closed, two buttons sit at the top right edge: **Data** and **Try your own code**. Each opens the pane on its own view. The last view used is remembered in the browser (`play-view`). Width, gutter, open state and the narrow-window stacking are unchanged.

### The Data view

- One chip per table. SQL steps label a chip with the table name (`orders`), Python steps with the file name (`orders.csv`), because that is what the learner's code reads.
- Under the chips: "6,000 rows, first 10 shown" and a grid of the first 10 rows. The grid scrolls sideways in a narrow pane. An empty cell shows a faint "empty", which is the word the lessons use.
- It follows the step. When the waiting step uses a different data folder (for example the real Olist tables), the view redraws. When the dataset is the same it stays as it is, including the chosen chip, so it does not jump while the learner types, asks or answers.
- It reloads only while the Data view is on screen. A closed pane makes no request.

### The route

`GET /api/data` returns `{"data": "<folder name of the step now waiting>", "tables": [{"name", "columns", "rows", "total"}]}`.

- The server picks the folder from the current step. The client never sends a folder name, so no path can be requested.
- Rows come from the CSV files of that folder with the standard `csv` module, for SQL and Python steps alike. Files in sub folders and files that are not CSV are ignored. Empty cells go out as JSON `null`.
- The first read of a folder counts its rows and keeps the result in memory, so the nine Olist files are read once (about 2 seconds the first time, the largest file has a million rows). The read happens outside the player's lock.
- Read only. Nothing is written to the progress file.

### What is not included

Earlier code, the step prompt, paging, filtering, sorting, editing, column types. The Ask tab's context is unchanged.

## Files

| Unit | Does |
|---|---|
| `player/tables.py` (new) | `sample(folder, ext=False, limit=10)`: tables of a folder, as above |
| `player/app.py` | `Player.data()` and `GET /api/data`; a per-folder cache |
| `player/web/app.js`, `style.css` | Try / Data tabs, two edge buttons, chips, grid, redraw on a new dataset |
| `docs/06-decisions.md`, `docs/05-app-requirements.md`, `README.md` | C24, R31, one README line |

## Testing

Test first for the server. The browser has no test harness, so it is checked live.

- `sample`: columns and the first 10 rows, a true total when a quoted cell holds a line break, empty cells as `None`, sub folders and non-CSV files ignored, file names with the extension when asked.
- `/api/data` on a SQL step returns the root tables with names without extension; on a Python step it returns file names; on a step with `data: sub` it returns that folder's tables and `data == "sub"`.
- Reading data changes nothing: the run view and the `events` and `questions` tables are the same before and after.
- Browser: both opener buttons, the tab remembered after a reload, chips switch tables, the grid scrolls in a narrow pane, the view redraws when the dataset changes and stays put when it does not, and the pane resize still works.

## Decision to add to `docs/06-decisions.md` once approved

C24. The right pane has a Data tab showing the tables of the waiting step: columns, row count and the first 10 rows. It shows the material and nothing of the lesson, so it is not a reference panel in the sense of rule 6. Reason: the learner kept scrolling up to find a column name or a value.
