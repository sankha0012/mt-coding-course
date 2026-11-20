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

## 5. Learn from the first use

Read the miss log with the owner. Revise lesson 1. Settle O2, O3, O4 and O5 from what actually happened. Measure how long the sitting took, which gives the first real estimate of the course's size.

Done when: lesson 1 has been revised once and the open questions it could answer are closed.

## 6. Finish the SQL foundation

Panorama movements 1 to 8, woven, with cold checks between sittings.

Done when: the owner can do pass-bar tasks 1 and 2 from a blank page, untimed.

## 7. SQL at interview level

Queries on query results, window functions, rows with no match, dates, conditional buckets. Write the panorama for this layer first, since it does not exist yet.

Done when: the owner can do pass-bar tasks 3 to 6, untimed.

## 8. Python foundation

Add Python execution and result checking to the player. Write the strand from the draft opening onward.

Done when: the owner can write a small complete script from a blank page, and can do the core of pass-bar tasks 7 and 8.

## 9. Python at interview level

Sorting by a rule, text as pieces, loops that carry state, two positions through sorted data, tests and cost.

Done when: pass-bar tasks 7 to 12, untimed.

## 10. pandas and ML code

Write the pandas panorama, then the strand, then the fit, predict and evaluate routine and the two by-hand pieces.

Done when: pass-bar tasks 13 to 17, untimed.

## 11. Speed and exams

Either build stage 3 here or hand it to the gym, per O6.

Done when: the owner completes all seventeen tasks inside their time limits, without an assistant, explaining aloud.

## A note on order

SQL at interview level (milestone 7) is placed before Python on purpose. Medium SQL with window functions is the part of the pass bar that appears in almost every source and is most often auto-graded, so it is the highest-value thing to reach early. If an interview with a known format arrives, reorder to suit it.
