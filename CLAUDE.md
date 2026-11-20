# MT Coding Course: working rules

A course that teaches SQL, basic Python and pandas to one learner by the Michel Thomas / Thinking Method. Start with `README.md`, then `docs/01` to `docs/07` in order. Everything in `docs/research/` is evidence and background, to be consulted when a rule needs its reason.

## State of the repository

Design, one full lesson script (`content/sql/`), and a content checker. The checker is the only code. Run it with `uv run python -m checker content/sql` and the tests with `uv run pytest`. There is no player yet. Do not build one without the owner's go-ahead: `docs/07-roadmap.md` puts the player at milestone 4, after the owner has read the checked lesson, because the research is clear that the quality lives in the script and not in the question-and-answer mechanism.

## What must not be broken

These come from `docs/02-pedagogy-rules.md`. A feature or a lesson that violates one is wrong even if it works.

1. The learner always produces the answer by typing it. No multiple choice, and no arranging of given pieces except as a step-back after a miss.
2. One new thought per step. If a step needs two, split it.
3. Never ask for anything the script has not already given the means to build.
4. Nothing is ever marked wrong. A miss moves the learner down the correction ladder and brings the sentence back later.
5. No timer, score, streak or speed pressure anywhere in stages 1 and 2.
6. No reference panel, cheat sheet or notes feature.
7. Two consecutive prompts must not be answerable by editing one slot of the previous answer.
8. A step must leave nothing behind for the learner to remember as an arbitrary rule. If it does, redesign or postpone the step.
9. No invented mnemonics. Real reasons only, and "this just is" where there is no reason.
10. Lesson text never lives in app code.

## Working conventions

- **Content and code stay apart.** Lessons are plain files. The app reads them.
- **Every expected answer must run.** No lesson ships if its own model answers fail against the data in `data/`. The checker does this. Run it after every content change.
- **Every prompt must pass the audit.** Each step lists the thoughts it requires, and a check confirms each was introduced in an earlier step. See `docs/04-script-format.md`.
- **Write for the owner's review.** A lesson script is reviewed and approved in readable form before it is wired into the app.
- **Verify before claiming.** Run the thing and read the output before saying it works.
- **Single user, local.** Rough visual finish is acceptable. Sloppy lesson content is not.
- **Keep the owner's data safe.** Never delete or overwrite a progress file. Test against a scratch copy.

## Workflow tools

The sibling repository `live-coding-gym` (same owner, same machine) requires a set of workflow tools in its own `CLAUDE.md`: Ponytail for minimal code, the Superpowers skills for brainstorming, planning, test-first development, debugging and verification, Graphify for code questions, and terse chat replies. Those are the owner's standing preferences there. Assume they apply here too, and confirm with the owner at the start of the first session.

## Sibling project

`../live-coding-gym` is a finished local app (Python 3.12 with `uv`, FastAPI, plain HTML and JavaScript, SQLite, content in plain files, a content checker). It is a good source of patterns for running learner code safely and comparing SQL results. Its dataset in `content/_shared` is similar to, but not the same as, the one in this repository's `data/`. The examples in these docs were checked against `data/` here.

## First session checklist

1. Read the docs in order.
2. Confirm the open decisions in `docs/06-decisions.md` with the owner, architecture first.
3. Follow `docs/07-roadmap.md` from milestone 1.
