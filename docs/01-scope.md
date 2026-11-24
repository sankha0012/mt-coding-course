# Scope

## The learner

One person. PhD-level mathematics, working knowledge of statistics and ML, years of building with AI assistants. Reads code comfortably. The barrier is the blank page: asked to write a query or a small script by hand, with someone watching, they freeze.

The suspected cause, from the research, is that code was learned as templates to recognise and edit. Templates work until the question changes shape. The course installs a constructive process in their place.

## The situation

Brazilian companies are sending this person into a coding round before deciding which role to offer. The round is a generic gate. It is not tied to a role and it cannot be avoided by aiming at less technical positions.

Because the round is generic, expect its generic forms: a timed online test on a HackerRank-style platform, and a live session in SQL and Python. See `docs/research/03-brazil-coding-rounds.md`.

## The goal

**Appear fluent enough in SQL, Python, pandas and basic ML code that nothing in a coding round sets off an alarm.**

Restated by the owner on 24 Nov 2026 (decision C9). Most rounds allow looking things up, and some allow an AI assistant. So the aim is not mastery and not recall of every spelling. It is that the common sentences come out by thinking, without a freeze, and that a lookup, when one happens, is the ordinary kind that every working data scientist does.

This is also what the Michel Thomas method was for. Thomas taught people who needed a basic, working fluency quickly. He never taught a language at an advanced level.

The owner's earlier words still describe the floor: to be able to write "at least some simple DS related code that people have to write every day", so that it never seems they "can't write any functional code at all".

## Three grades

Everything the course touches has one of three grades (decision C10). The test is the alarm test: would looking this up in front of an interviewer raise an eyebrow?

| Grade | Meaning | In a lesson |
|---|---|---|
| **Core** | Typed from memory | Asked, and brought back spaced |
| **Shape** | Know the structure, look up the spelling | The teacher's line supplies the spelling every time, and says that this is something one looks up |
| **Name only** | Know it exists and what it is called | One aside. Never asked. |

## The pass bar

Seventeen tasks, drawn from the research. They are the yardstick for what the course must make possible. Fifteen are core, one is shape grade and one is name only.

**SQL**

| # | Task | Grade | Lesson |
|---|---|---|---|
| 1 | Count and average per group, keeping only groups above a threshold | Core | SQL-3 |
| 2 | Join two tables and aggregate by a column from the second | Core | SQL-4 |
| 3 | Find rows in one table with no match in the other | Core | SQL-8 |
| 4 | Top three per group | Core | SQL-7 |
| 5 | Each customer's most recent order | Core | SQL-7 |
| 6 | Month-by-month totals with the change from the previous month | Core | SQL-9 |

**Plain Python**

| # | Task | Grade | Lesson |
|---|---|---|---|
| 7 | Top-k most common items, ties broken alphabetically | Core | PY-7 |
| 8 | Average per key, ignoring missing values | Core | PY-6 |
| 9 | Split a sentence into bigrams and count them | Core | PY-8 |
| 10 | Merge two sorted lists | Shape | PY-10 |
| 11 | Group timestamps into sessions | Core | PY-9 |
| 12 | Write three tests for any of the above and state its cost in Big-O terms | Core | PY-10, and as a habit from PY-5 |

**pandas and ML**

| # | Task | Grade | Lesson |
|---|---|---|---|
| 13 | Load a table, clean missing values, add two engineered columns | Core | PD-3 |
| 14 | Group and merge to answer a business question | Core | PD-4 |
| 15 | Fit a model with scikit-learn, predict, and report a sensible metric | Core | ML-1 |
| 16 | Write k-fold cross-validation by hand | Core | ML-3 |
| 17 | Write one metric by hand, such as AUC or KS | Name only | ML-3 |

## How the course gets there

About 27 lessons of about 20 minutes, roughly eight hours in all (decision C11). That is the size of a Michel Thomas foundation course. Details are in `docs/03-curriculum.md` and `docs/maps/`.

1. **Pass 1, foundation.** Fourteen lessons across all three strands. After it the learner can write something that runs in SQL, Python and pandas.
2. **Pass 2, the interview layer.** Thirteen lessons adding the thoughts the rounds ask for: window functions, sorting by a rule, a loop that remembers, fit and predict, cross-validation by hand.

The passes run breadth first (decision C12), so that no round finds the learner with nothing to say in one of the three.

## What the method does and does not cover

It covers acquisition: getting a correct sentence out, reliably, by thinking. It deliberately does not train speed, and the research warns that it can produce a feeling of competence that outruns the real thing. The cold checks in `docs/05-app-requirements.md` exist to guard against that.

Timed practice, hidden tables and exact-output grading are not built here. They belong to the sibling `live-coding-gym`, which already has timed work and mock rounds.

## Out of scope

- Maths, statistics and ML theory. The learner has them.
- Speed drills and mock exams. The gym covers those.
- Robust production code, system design, and working with an AI assistant under observation. The gym covers those too.
- Multiple learners, accounts, hosting, payments, a mobile layout.
- PySpark. It appeared in two candidate reports as an alternative to pandas. Revisit if a specific process asks for it.
- Classes, recursion, and data structures beyond lists, dicts, sets and pairs. One company lists trees and graphs, and no report shows them asked of a data scientist.

## Language

The lessons are in English. Interviews in Brazil are usually in Portuguese. A short phrase bank for talking through code in Portuguese would fit the fluency goal. It is an open question in `docs/06-decisions.md`, to be decided after pass 1.
