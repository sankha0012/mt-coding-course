# MT Coding Course

A course that takes one person from "can read code but freezes on a blank page" to "passes the coding round of a Brazilian data science hiring process". It teaches SQL, basic Python and pandas with the Michel Thomas method as refined by Language Transfer's Thinking Method: the method carries the burden of remembering, the learner only thinks and produces.

**Status (20 Nov 2026): design, the first lesson, a content checker and the first player are built.** SQL lesson 1 is in `content/sql/`. `uv run python -m checker content/sql` checks it and `uv run python -m player` plays it at http://127.0.0.1:8770. The rest of the course is planned as 27 lessons in two passes (`docs/03-curriculum.md`, `docs/maps/`). Next: the owner sits lesson 1 (milestone 5) and approves the strand maps (milestone 6).

## Why this exists

The owner already has the maths, statistics and ML. Companies are sending them into a coding round before deciding on a role, so the round is a gate that has to be cleared whatever job follows. A sibling project, `live-coding-gym`, trains reading, robustness and interview routine. It assumes the learner can already write some code. This course is the step before that.

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
