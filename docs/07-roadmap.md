# Roadmap

In order. Each milestone ends with something the owner can look at. The content milestones come before the build milestones on purpose: the research says the script is where the quality is, and a player built before a script exists will shape the script badly.

## 1. Settle the open decisions

Go through `06-decisions.md` with the owner. Architecture (O1) and the opening (R1) block everything else. The rest can wait until they bite.

Done when: O1 and R1 have answers recorded in the decisions file.

## 2. Write the first full SQL lesson as a readable document

Extend the chosen opening into one complete sitting of fifteen to twenty minutes, in the shape described in `04-script-format.md`: every step with its prompt, model answer, new thought, required thoughts, narration lines, known wrong answers and step-by-step walk. Include the list of thoughts with identifiers.

Run every model answer against `data/` by hand or with a throwaway check. Do the audit by hand.

Done when: the owner has read the lesson and says it reads right.

## 3. Choose the lesson file format and build the content checker

Turn the approved lesson into the chosen plain-file format. Build the checker with the seven checks. This is the first code in the repository.

Done when: the checker passes on lesson 1 and fails, with a clear message, on a deliberately broken copy.

Built 20 Nov 2026 as one YAML file per lesson plus a Python checker. See `docs/superpowers/specs/2026-11-20-lesson-format-and-checker-design.md`. Lesson 1 passes with two load warnings, both expected. Both gates are in `tests/test_gate.py`.

## 4. Build the smallest player that can run lesson 1

The core loop, the editor, result-based checking for SQL, the correction ladder, narration, progress that survives a restart, and the miss log. Nothing for Python yet.

Done when: the owner completes lesson 1 in the app.

Built 20 Nov 2026. See `docs/superpowers/specs/2026-11-20-player-design.md`. All of lesson 1 plays through the API in `tests/test_play.py`. The owner completing it in the app is still to come.

## 5. Learn from the first use

Read the miss log with the owner. Revise lesson 1. Settle O2, O3, O4 and O5 from what actually happened. Measure how long the sitting took, which gives the first real estimate of the course's size.

Done when: lesson 1 has been revised once and the open questions it could answer are closed.

The milestones below replaced the earlier 6 to 11 on 24 Nov 2026, when the goal was restated as fluency (decision C9) and the lesson map in `docs/03-curriculum.md` was agreed. Code is written only with the owner's go-ahead, one piece at a time.

## 6. Approve the strand maps

The owner reads `docs/maps/sql.md`, `docs/maps/python.md` and `docs/maps/pandas-ml.md` and answers the questions at the end of each.

Done when: the three maps are approved.

Done 24 Nov 2026 (decision C18).

## 7. The player plays a course

More than one lesson: a course order across strands, "next lesson" at the end of a sitting, and an opening cold check drawn from an earlier lesson. The lesson format and the checker gain shape grade: a step lists the spellings it supplies, and the checker confirms each appears in the step's text.

Done when: lesson 1 and a second lesson play in order, and the second opens with a cold check from the first.

## 8. Finish the SQL foundation

SQL-2, SQL-3 and SQL-4, one at a time: write the YAML, pass the checker, the owner sits it, read the miss report, revise.

Done when: the owner has sat SQL-4, and can do pass-bar tasks 1 and 2.

## 9. Python foundation

Add Python to the checker and the player: run the learner's code in a separate process with a time limit, judge it by what it produces, and indent automatically after a colon. Then PY-1 to PY-6.

Done when: the owner has sat PY-6, and can write the function behind pass-bar task 8.

## 10. pandas foundation

Add pandas to the checker and the player. Then PD-1 to PD-4, and cold sitting A. The cold sittings run on the Olist tables in `data/real/olist/` (decision C17), so the checker and the player learn to load a second dataset here, and to say so plainly when it is absent.

Done when: the owner has sat cold sitting A. Pass 1 is complete: something runs in all three strands.

## 11. The interview layer in SQL

SQL-5 to SQL-9. SQL-8 needs `data/coupons.csv`, a new small file.

Done when: the owner has sat SQL-9, and can do pass-bar tasks 3 to 6.

## 12. The interview layer in Python

PY-7 to PY-10.

Done when: the owner has sat PY-10, and can do pass-bar tasks 7, 9, 11 and 12.

## 13. Windows in pandas, and ML code

Add scikit-learn. Settle the data question first: the practice data has nothing to predict (see `docs/maps/pandas-ml.md`). Then PD-5, ML-1, ML-2, ML-3, and cold sitting B.

Done when: the owner has written k-fold cross-validation by hand in ML-3 and sat cold sitting B.

## A note on order

The order is breadth first (decision C12): the foundation of all three strands before the interview layer of any, so that no round finds the learner with nothing to say in one of them. If an interview with a known format arrives, reorder to suit it. The likeliest change is to bring milestone 11 forward, since medium SQL with window functions appears in almost every source and is the part most often auto-graded.

Speed and mock exams are not built here. They moved to `live-coding-gym` (decision O6, closed 24 Nov 2026).
