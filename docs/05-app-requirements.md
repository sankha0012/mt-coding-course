# App requirements

What the app must do. No implementation is chosen here. The architecture is an open decision in `docs/06-decisions.md`.

## The core loop

1. The teacher's line appears.
2. For an Ask step, the learner types an answer in a plain editor and submits.
3. The app runs the answer and compares its result with the model answer's result.
4. On a match, the teacher narrates what the learner did, choosing a narration line different from the last one used, and the next step appears.
5. On a miss, the app moves down the correction ladder. It never shows the word "wrong", a red mark, or a count of mistakes.

## Requirements

### Lesson player

- R1. Present steps one at a time, in order. Earlier steps stay visible above as a conversation the learner can scroll back through.
- R2. Support the six kinds of step in `docs/04-script-format.md`.
- R3. Resume exactly where the learner stopped.
- R4. Open each sitting with a cold check from the previous lesson and close with one from the current lesson.

### Answering

- R5. A plain editor. No autocomplete and no suggestions, so that it behaves like an interview editor. SQL syntax colours are allowed, as in interview editors (decision C8).
- R6. In Python, indent automatically after a line ending in a colon. Indentation cannot be forgiven by the checker, so the editor must make it easy.
- R7. Make room for thinking before typing. One option is a short quiet moment before the editor accepts input, with the request to think it out. This needs trying with the learner before it is fixed.
- R8. Show the result of the learner's code, as a table for SQL and pandas and as output for Python, so they see what they made.

### Checking

- R9. Judge an answer by what it produces, not by its text. Python admits too many correct forms for text comparison.
- R10. For SQL, compare result sets with the model answer's. Row order matters only when the step says so. Column names do not matter unless the step says so.
- R11. Forgive letter case in keywords, spacing, quote style and a missing final semicolon.
- R12. Recognise the known wrong answers listed in a step, by result or by pattern, so the matching leading question can be asked.
- R13. A crash or an endless loop in the learner's code is reported calmly as output, never as an app error. Stop runaway code after a time limit.

### After a miss

- R14. The correction ladder: ask again thinking it through; then a leading question where one is known; then the step-by-step walk; then, as a last resort, pieces to arrange and finally the answer to copy.
- R15. A missed step is brought back a few steps later inside a different sentence.
- R16. Small slips do not trigger the ladder. Show the model answer beside the learner's and move on.

### What must be absent

- R17. No timer, score, streak, percentage or leaderboard in stages 1 and 2.
- R18. No reference panel, cheat sheet, glossary or notes feature. The only help is the ladder.
- R19. No instructions screen before the first lesson. Rules of engagement appear in the lesson text when they first matter.
- R20. No multiple choice.

### Records

- R21. Keep progress on the learner's machine and never lose it. An update to the app must not reset it.
- R22. Keep a miss log: which step, what was typed, which rung of the ladder resolved it. This is for revising the script, and the learner never sees it as a score.
- R23. Give the writer a simple report from the miss log: the steps most often missed and the thoughts they required.

### Content

- R24. Lessons are plain files, separate from app code.
- R25. A content checker implements the seven checks in `docs/04-script-format.md` and runs before any lesson is shipped.

### Stage 3 only

- R26. Timed drills on the pass-bar tasks, with the timer visible.
- R27. A mode where the tables cannot be seen and only a description of their columns is given.
- R28. Exact-output grading with hidden test cases, as the online platforms do.

## Qualities

- One learner, one machine. Starting it should take one command or one double-click.
- Works offline once set up.
- Rough visual finish is fine. The teacher's text must be comfortable to read, because the lesson is a conversation.
- The teacher's voice is warm. Nothing in the interface should feel like an exam before stage 3.

## Running the learner's code

The app has to execute SQL and Python, including pandas and later scikit-learn. Two broad routes exist, and choosing between them is the first architecture decision.

| Route | For | Against |
|---|---|---|
| Everything in the browser, as one file | Nothing to install, easy to share | Python with pandas in the browser means a download of several megabytes on first load, and scikit-learn adds more |
| A small local app, as the sibling gym is | Real Python and SQLite, the gym's runner and result comparison can be studied or reused, the owner already runs this setup | Needs a local server |

The only code that ever runs is the learner's own, on their own machine.

## Not required now

- Review of answers by an AI model. The gym uses one. Here the correction ladder and the known wrong answers do that job. It could be added later for free-form explanations.
- Voice, even though the original method is spoken. Reading aloud is a possible later experiment.
- More than one learner.
