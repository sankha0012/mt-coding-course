# Ask the teacher: side questions answered by an AI

Status: draft for the owner's review, 24 Nov 2026. Decision C22 (below) records it once approved.

## Goal

The learner can ask a question in words while sitting a lesson. The lesson steps aside, the question is answered, and when the learner confirms, the lesson resumes exactly where it was.

## Rules it must respect

- Rule 1 (the learner types the answer): the AI explains and never supplies the answer to the step being asked.
- Rule 4 (nothing is marked wrong): a side thread never moves the ladder, queues a return, or logs a miss.
- Rule 5 (no pressure): no timer or counter of questions is shown to the learner.
- Rule 6 (no reference panel): this is a conversation about the step in front of the learner, in the teacher's voice, tied back to the lesson. It is not a glossary, notes page or cheat sheet. The AI is told to answer in terms of the thoughts met so far and to hand the learner back to the step.
- Rule 10 (lesson text never in app code): the teacher persona prompt lives in `content/ui.yaml`, not in Python.

## Design

### The answer window

Two tabs above the input: **Code** (the current editor, SQL or Python as the step needs) and **Ask** (a plain text box and an Ask button). Code is the default. Ask is available on every step type, including give steps and the done screen.

### The detour

Sending a question opens a **side thread** in the transcript: indented, tinted, labelled "Side question". The learner's question and the reply appear inside it. Follow-ups join the same thread. While a thread is open the engine is untouched.

**"Got it, back to the lesson"** closes the thread. The teacher then re-shows the pending step ("Where we were:" and the prompt), and the code the learner had half typed is still in the editor. Only the learner ends a thread. The AI never decides the lesson has resumed.

Side threads are not replayed after a page reload. They are in the progress file (see Records) but the transcript is rebuilt from the engine's events as today.

### What the model sees

One system message and the thread:

- the teacher persona and the rules above, from `content/ui.yaml`;
- the text of every thought introduced so far, in order (the learner's vocabulary);
- the lesson's teacher lines so far, and the current step's prompt;
- the learner's last typed code and its result, if any;
- table and column names of the step's dataset. No data rows.

It never receives `model`, `wrong`, `walk`, `return` or any expected output. It cannot leak what it never saw.

### The guard

A reply may contain code blocks. Each block in the step's language is run on the step's data with the existing `Runner`. If its result equals the step's expected result, the reply is replaced by a short teacher line: that is the answer to this step, so try it. Code that errors, or gives a different result, passes. This covers the case where the model deduces the answer from the prompt alone.

The guard does not apply to give and aside steps, which expect nothing.

### Scope of questions

Any question about SQL, Python, pandas or machine learning is fine, in or out of the lesson. The persona keeps replies short (a few sentences, one small example), uses names from the lesson's own data where it can, and ends by pointing back to the step.

### Providers and keys

Gemini and Groq. Both offer an OpenAI-style chat endpoint, so one small function, `chat(messages) -> text`, serves both, using only `urllib` from the standard library. No SDK, no new dependency.

- Order: Gemini first, Groq as fallback when Gemini answers with a rate limit or a server error. The order is one line of configuration.
- Settings live in the environment or in a git-ignored `.env` at the repository root: `GEMINI_API_KEY`, `GROQ_API_KEY`, and optional `GEMINI_MODEL`, `GROQ_MODEL`, `AI_ORDER`. The desktop launcher does not load the shell environment, so `.env` is what makes it work from there.
- Model names are checked against each provider's model list on the first live call, then written as defaults. They change often, so they are configuration and not code.
- The key is read on the server only. It never appears in a response, a log line or the progress file.
- With no key, or both providers failing, the Ask tab says so in one calm line and the lesson is unaffected.
- Replies are not streamed. A short "thinking" line shows until the reply arrives. Streaming can be added later if the wait bothers the learner.
- Privacy: the question, the lesson text so far and the learner's typed code are sent to the provider. Data rows are not. Gemini's free tier may use prompts to improve Google products. A paid key avoids that.

### Records

A new table `questions(id, run_id, step, asked_at, question, reply, provider, guarded)`, additive only, like the rest of the progress store. `player.report` gains a "most-asked steps" list beside the miss list. It tells the writer where a step confuses learners. It is never shown to the learner as a count or a score.

### Components

| Unit | Does | Depends on |
|---|---|---|
| `player/ai.py` | builds the context, calls `chat`, applies the guard, returns the reply | `Runner`, the engine's read-only view of the current step, `content/ui.yaml` |
| `player/llm.py` | `chat(messages)` over `urllib`, provider order, fallback, `.env` loading | standard library |
| `player/store.py` | `questions` table, `add_question`, `questions_by_step` | sqlite |
| `player/app.py` | `POST /api/ask` (`{question, thread}` returns `{reply}`), and `POST /api/thread/close` returns the pending step view | the above |
| `player/web/app.js`, `style.css` | tabs, side-thread blocks, the back button | the routes |

The engine itself gains one read-only method that returns what the model may see for the current step. It gains no new state.

## Testing

Test first, with a fake `chat`:

- the payload never contains the step's `model`, `wrong`, `walk`, `return` or expected output (checked on every step of every lesson);
- the guard replaces a reply whose code gives the expected result, and passes one that does not;
- a thread opened and closed leaves the engine's step, ladder rung, returns queue and the miss log exactly as they were;
- `questions` rows are written, and the key is absent from every response and every stored row;
- provider fallback: Gemini failing with a rate limit moves to Groq; both failing gives the calm message;
- no key: the route answers with the calm message and no network call is made.

A live check with the owner's keys, in a scratch progress folder, ends the work. The browser check covers the tabs, a thread, and the return to the step.

## Open for the owner

1. Provider order: Gemini first (assumed) or Groq first.
2. Whether the learner wants the reply streamed from the start.

## Decision to add to `docs/06-decisions.md` once approved

C22. The learner may ask questions in words. The lesson pauses, a side thread answers, and the learner confirms to resume. The model never sees expected answers, a guard blocks a reply that solves the step, and nothing is scored or counted for the learner. Reason: the owner wants to ask about thoughts the script has not yet explained, and the questions, kept in the progress file, show where the script is thin.
