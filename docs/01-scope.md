# Scope

## The learner

One person. PhD-level mathematics, working knowledge of statistics and ML, years of building with AI assistants. Reads code comfortably. The barrier is the blank page: asked to write a query or a small script by hand, with someone watching and no assistant, they freeze.

The suspected cause, from the research, is that code was learned as templates to recognise and edit. Templates work until the question changes shape. The course installs a constructive process in their place.

## The situation

Brazilian companies are sending this person into a coding round before deciding which role to offer. The round is a generic gate. It is not tied to a role and it cannot be avoided by aiming at less technical positions.

Because the round is generic, expect its generic forms: a timed online test on a HackerRank-style platform, and a live session in SQL and Python. See `docs/research/03-brazil-coding-rounds.md`.

## The goal

**Pass the coding part of a Brazilian data science hiring process, without an AI assistant, explaining the work aloud.**

A nearer goal comes first, in the owner's words: to be able to write "at least some simple DS related code that people have to write every day", so that it never seems they "can't write any functional code at all".

## The pass bar

Seventeen tasks. Someone who can do these from a blank page clears most of the rounds found in the research. Times are for a live round.

**SQL, about 10 minutes each**

1. Count and average per group, keeping only groups above a threshold.
2. Join two tables and aggregate by a column from the second.
3. Find rows in one table with no match in the other.
4. Top three per group.
5. Each customer's most recent order.
6. Month-by-month totals with the change from the previous month.

**Plain Python, about 15 minutes each**

7. Top-k most common items, ties broken alphabetically.
8. Average per key, ignoring missing values.
9. Split a sentence into bigrams and count them.
10. Merge two sorted lists.
11. Group timestamps into sessions.
12. Write three tests for any of the above and state its cost in Big-O terms.

**pandas and ML, about 15 to 20 minutes each**

13. Load a table, clean missing values, add two engineered columns.
14. Group and merge to answer a business question.
15. Fit a model with scikit-learn, predict, and report a sensible metric.
16. Write k-fold cross-validation by hand.
17. Write one metric by hand, such as AUC or KS.

## How the course gets there

Three stages. Details are in `docs/03-curriculum.md`.

1. **Foundation.** The learner can always write something that runs. No timer.
2. **Interview level.** The remaining thoughts the pass bar needs, in the same method. No timer.
3. **Speed and exams.** The seventeen tasks as timed drills, and practice against tables that cannot be seen.

## What the method does and does not cover

It covers acquisition: getting a correct sentence out, reliably, by thinking. It deliberately does not train speed, and the research warns that it can produce a feeling of competence that outruns the real thing. Stage 3 and the cold checks in `docs/05-app-requirements.md` exist to guard against that.

## Out of scope

- Maths, statistics and ML theory. The learner has them.
- Robust production code, system design, and using an AI assistant under observation. The sibling `live-coding-gym` covers those.
- Multiple learners, accounts, hosting, payments, a mobile layout.
- PySpark. It appeared in two candidate reports as an alternative to pandas. Revisit if a specific process asks for it.
- Classes beyond a simple one, recursion, and data structures beyond lists, dicts, sets and tuples. One company lists trees and graphs, and no report shows them asked of a data scientist.

## Language

The lessons are in English. Interviews in Brazil are usually in Portuguese. Whether the teacher's lines should be in Portuguese, or whether a short phrase bank for talking through code in Portuguese should be added, is an open question in `docs/06-decisions.md`.
