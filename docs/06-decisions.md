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
| C6 | The coding round is a generic gate that comes before role placement. The target is therefore the full pass bar, and all three stages are in scope. (Narrowed by C9 to C12 on 24 Nov 2026: the pass bar is graded, and the timed stage moved to the gym.) |
| C7 | This repository starts with documents only. No code until the work moves to Claude Code. |
| C8 | The lesson screen has a colour palette (paper and teal, with a dark mode), and SQL words are coloured everywhere, including in the answer editor, as in most editors and interview platforms. Still no autocomplete and no suggestions. Decided 20 Nov 2026. Known effect: a mistyped keyword such as `FORM` does not take the keyword colour, which quietly signals a slip. |

## Confirmed by the owner (24 Nov 2026)

The goal was restated, and the rest of the lessons were planned from it.

| # | Decision | Reason |
|---|---|---|
| C9 | The goal is to appear fluent enough that nothing in a coding round sets off an alarm. Not mastery, and not recall of every spelling. | Most rounds allow looking things up and some allow an AI assistant. Michel Thomas taught basic working fluency quickly, never an advanced level. |
| C10 | Everything taught has one of three grades. Core is typed from memory. Shape means the structure is known and the teacher's line supplies the spelling every time. Name only is one aside. The alarm test decides: would looking this up in front of an interviewer raise an eyebrow? | It is what makes a short course enough, and it rehearses the honest lookup. Shape grade is not a reference panel: the spelling arrives in the teacher's line. |
| C11 | About eight hours: 27 lessons of about 20 minutes, in two passes. | The size of a Michel Thomas foundation course. |
| C12 | Breadth first: the foundation of SQL, Python and pandas, then the interview layer of each. This replaces "SQL to interview level before Python". | After a third of the course something runs in all three strands. |
| C13 | The owner approves a one-page map per strand, then reviews each lesson by sitting it. The miss log drives revisions. This replaces a full readable draft per lesson, which was done for SQL lesson 1. | Twenty-six more drafts of 600 lines each would not get read. |
| C14 | Core: window functions, the sessions loop, k-fold cross-validation by hand as the capstone, and tests and Big-O as habits woven through the Python lessons. Shape: merging two sorted lists, window frames, date functions, import lines. Name only: a metric by hand (AUC or KS). | The alarm test, applied to the seventeen tasks. |
| O6 | Stage 3 (timed drills, hidden tables, exact output) is not built here. It goes to `live-coding-gym`. | The gym already has timed work and mock rounds. |
| C15 | Synthetic data may be added to `data/`, and real public data may be used. The app is for the owner's personal use and will not be sold, so a non-commercial licence is acceptable. | The practice tables had nothing unmatched and nothing to predict. |
| C16 | PY-1 keeps its twelve thoughts in one lesson. | The owner's call. Most of the twelve are imports from SQL. |
| O11 | The ML lessons use `data/deliveries.csv`, a synthetic table added on 24 Nov 2026. | Distance, rain and the courier's load predict lateness: an AUC of about 0.70, and 0.80 with the promised time. |
| O12 | SQL-8 uses `data/coupons.csv`, a synthetic table with one coupon never used. | "Rows with no match" needs something unmatched. |
| C17 | The two cold sittings use the Olist Brazilian e-commerce dataset, real data the learner has never seen. The lessons stay on the practice tables. The files live in `data/real/olist/` and stay out of git. | A cold sitting should test thinking, not reproduction, and a round hands you a table you have not seen. The licence is CC BY-NC-SA 4.0 and this repository is public. |

## Confirmed by the owner (20 Nov 2026, first Claude Code session)

These were R1 to R5, O1 and O10. The old numbers are kept so that references elsewhere still work.

| # | Decision | Reason |
|---|---|---|
| R1 | Use Opening B for SQL: start from "how many orders?" | Every sentence answers a question, piles arrive within ten minutes, and the rule about selecting the pile's name is discovered. |
| R2 | Order the strands SQL, Python, pandas | pandas syntax is Python syntax. This refines C3, where Python had not yet been added. |
| R3 | One app with three strands, not three apps | The strands refer back to each other constantly. |
| R4 | Three stages: foundation, interview level, speed and exams | The method gives acquisition, and the rounds also demand speed. |
| R5 | Borrow one thing from Opening A: an early look at raw rows | So the table is not abstract. |
| O1 | Architecture: a small local app like the gym (Python 3.12 with `uv`, FastAPI, plain HTML and JavaScript, SQLite) | Real Python, pandas and scikit-learn with no large browser download, and the gym's runner and result comparison can be studied or reused. |
| O10 | The gym's workflow tools apply here unchanged: Ponytail, the Superpowers skills, Graphify and terse chat replies | Lesson text and documents stay in normal prose. |

The owner also asked, in the same session, to be asked for permission before any code is written.

## Open

| # | Question | Notes |
|---|---|---|
| O2 | Is the last step of Opening B too big a stretch for a first sitting? | It combines keep rows and piles, unrehearsed. Only trying it will tell. |
| O3 | Should the learner type a one-line plan in English before the code, or is thinking it enough? | The method wants the thought separated from the sentence. Typing a plan makes that visible and costs time. |
| O4 | How many classmate mistakes per ten minutes? | The drafts have one each. |
| O5 | How should the pause before typing work? | A forced delay could irritate. A simple request could be ignored. |
| O7 | Should lessons be in Portuguese, or include a phrase bank for talking through code in Portuguese? | Interviews are usually in Portuguese. The owner's Portuguese is good. A phrase bank fits the fluency goal (C9). Decide after pass 1. |
| O8 | Which SQL dialect do the target platforms use? | The examples run on SQLite. Date functions and a few window details differ between dialects. They are shape grade (C10), so this matters less than it did. |
| O9 | Should PySpark be covered? | Two candidate reports mention it as an alternative to pandas. |

## Changed along the way

- **24 Nov 2026.** The goal changed from passing every task from a blank page with no help to appearing fluent (C9). The three stages became two passes, the pass bar became graded, and the timed stage left for the gym.
- **20 Nov 2026.** The plan to contrast the SQL equals sign with the pandas double equals was dropped. With Python between them, the double equals is met where it has its real reason and pandas inherits it.
- **20 Nov 2026.** The scope grew from a small first course to the full pass bar after C6.
- **19 Nov 2026.** Problem decomposition, first set aside for a later version, came back into stage 1 in a light form after reading the guidebook's section on separating thought from language.
