# MT Coding Course

A course that takes one person from "can read code but freezes on a blank page" to "passes the coding round of a Brazilian data science hiring process". It teaches SQL, basic Python and pandas with the Michel Thomas method as refined by Language Transfer's Thinking Method: the method carries the burden of remembering, the learner only thinks and produces.

**Status (24 Nov 2026): the whole course is written.** 27 lessons in two passes, in SQL, Python, pandas and scikit-learn, and two cold sittings on real data, are in `content/` (`docs/03-curriculum.md`, `docs/maps/`). `uv run python -m checker content` checks them and `uv run python -m player` plays them at http://127.0.0.1:8770. No lesson has been sat by the owner yet. Next: the owner sits lesson 1 and reads the miss log (milestone 5).

## Why this exists

The owner already has the maths, statistics and ML. Companies are sending them into a coding round before deciding on a role, so the round is a gate that has to be cleared whatever job follows. A sibling project, `live-coding-gym`, trains reading, robustness and interview routine. It assumes the learner can already write some code. This course is the step before that.

## Asking the teacher

The Ask tab beside the code editor sends a question to Gemini or Groq, as you choose from its menu. The lesson waits, a side thread answers, and "Got it, back to the lesson" returns you to the step (decision C22). The model never sees a step's expected answer. To set it up, copy `.env.example` to `.env`, put in `GEMINI_API_KEY` and `GROQ_API_KEY` (and optionally `GEMINI_MODEL`, `GROQ_MODEL`), and restart the player. `.env` is git-ignored. Your questions are kept in `progress/progress.db`, and `uv run python -m player.report` lists the steps you asked about most.

## Seeing the data

The pane on the right has a Data tab. It shows the tables of the step you are on, with their columns and the first 10 rows, so you need not scroll up to find a column name.

## The course panel

The Course button at the top left opens a map of the whole course. Finished lessons can be sat again, later ones are locked, and "Start over" begins the current lesson from the beginning. Your earlier attempts stay in the progress file.

## Read in this order

| File | What it gives you |
|---|---|
| `CLAUDE.md` | Working rules for whoever builds this |
| `docs/01-scope.md` | The learner, the goal, the pass bar, what is out of scope |
| `docs/02-pedagogy-rules.md` | The teaching rules every lesson and every feature must obey |
| `docs/03-curriculum.md` | Two passes, three strands, the lessons in order |
| `docs/04-script-format.md` | What a lesson script contains, step by step |
| `docs/05-app-requirements.md` | What the app must do, with no implementation chosen |
| `docs/06-decisions.md` | What is decided, what is only recommended, what is open |
| `docs/07-roadmap.md` | Milestones, in order |
| `docs/maps/` | The thoughts of every lesson, strand by strand |
| `docs/research/` | The evidence behind all of the above |
| `data/` | The practice dataset every example was checked against |

## The idea in five lines

1. Every prompt is a small translation from a plain question into code. The learner always produces and never picks from options.
2. One new thought per step, immediately recombined with everything earlier.
3. The learner is told not to memorise. The script does the spaced repetition, hidden inside new sentences.
4. A miss is information about the script. The app steps back to a smaller piece and never marks anything wrong.
5. Acquisition has no timer. Speed is trained afterwards, in the sibling gym.
