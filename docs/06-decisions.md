# Decisions

What is settled, what is recommended but not yet confirmed by the owner, and what is open. Add to this file as decisions are made, with the date.

## Confirmed by the owner (19 to 20 Nov 2026)

| # | Decision |
|---|---|
| C1 | The real barrier is the blank page: reading is fine, writing is where it stops. |
| C2 | The method is Michel Thomas, as refined by the Thinking Method. Responsibility sits with the method, the learner does not try to remember, and the aim is a low barrier and early production, not fluency. |
| C3 | SQL comes first, with pandas as a second dialect of the same grammar. |
| C4 | "Speaking a bit" means being able to write some simple, everyday data science code, so that it never looks as if no functional code can be written. |
| C5 | The course also teaches basic Python (lists, dicts and so on), so the learner can quickly write simple scripts. |
| C6 | The coding round is a generic gate that comes before role placement. The target is therefore the full pass bar, and all three stages are in scope. |
| C7 | This repository starts with documents only. No code until the work moves to Claude Code. |

## Recommended, not yet confirmed

The owner has seen each of these and has not objected, but has not said yes either. Confirm before relying on them.

| # | Recommendation | Reason |
|---|---|---|
| R1 | Use Opening B for SQL: start from "how many orders?" | Every sentence answers a question, piles arrive within ten minutes, and the rule about selecting the pile's name is discovered. |
| R2 | Order the strands SQL, Python, pandas | pandas syntax is Python syntax. This refines C3, where Python had not yet been added. |
| R3 | One app with three strands, not three apps | The strands refer back to each other constantly. |
| R4 | Three stages: foundation, interview level, speed and exams | The method gives acquisition, and the rounds also demand speed. |
| R5 | Borrow one thing from Opening A: an early look at raw rows | So the table is not abstract. |

## Open

| # | Question | Notes |
|---|---|---|
| O1 | Architecture: one browser file, or a small local app like the gym? | The original request was for a small single-file app. Adding Python and pandas changes the cost of that. See the comparison in `05-app-requirements.md`. Decide first. |
| O2 | Is the last step of Opening B too big a stretch for a first sitting? | It combines keep rows and piles, unrehearsed. Only trying it will tell. |
| O3 | Should the learner type a one-line plan in English before the code, or is thinking it enough? | The method wants the thought separated from the sentence. Typing a plan makes that visible and costs time. |
| O4 | How many classmate mistakes per ten minutes? | The drafts have one each. |
| O5 | How should the pause before typing work? | A forced delay could irritate. A simple request could be ignored. |
| O6 | Is stage 3 built here or handed to `live-coding-gym`? | The gym already has timed work and mock rounds. |
| O7 | Should lessons be in Portuguese, or include a phrase bank for talking through code in Portuguese? | Interviews are usually in Portuguese. The owner's Portuguese is good. |
| O8 | Which SQL dialect do the target platforms use? | The examples run on SQLite. Date functions and a few window details differ between dialects. |
| O9 | Should PySpark be covered? | Two candidate reports mention it as an alternative to pandas. |
| O10 | Do the owner's workflow tools from the gym apply here unchanged? | See `CLAUDE.md`. |

## Changed along the way

- **20 Nov 2026.** The plan to contrast the SQL equals sign with the pandas double equals was dropped. With Python between them, the double equals is met where it has its real reason and pandas inherits it.
- **20 Nov 2026.** The scope grew from a small first course to the full pass bar after C6.
- **19 Nov 2026.** Problem decomposition, first set aside for a later version, came back into stage 1 in a light form after reading the guidebook's section on separating thought from language.
