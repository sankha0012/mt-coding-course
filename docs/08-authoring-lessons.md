# Authoring a lesson

How to write a lesson file that passes the checker and reads right. Read `docs/02-pedagogy-rules.md` and `docs/04-script-format.md` first. The plan for each lesson is in `docs/maps/`. Two finished lessons show the shape: `content/sql/lesson-01.yaml` (the voice) and `content/sql/lesson-02.yaml` (the full recipe, with returns).

A lesson is one YAML file, `content/<strand>/lesson-NN.yaml`. Write it as data with `tools/lessongen.py`, which formats the YAML the same way every time and keeps code readable. The YAML is the source of truth. The script that generated it is thrown away.

## The recipe

About 20 to 26 steps, 8 to 15 of them typed.

1. **Open with a cold check** (kind `cold-check`): one blank-page prompt from an older lesson, on a combination never practised. It has `after_run` ("That is where we stopped last time. On we go.") and no narration, wrong answers, walk or return.
2. **Give, then ask.** A new thought arrives in a `give` step that already shows it in use, with a sentence the learner can run (`shows`) and an `after_run` that gives the one-line reason. Then one or two `ask` steps use it, then it comes back inside later sentences.
3. **One new thought per step** (`new: [id]`, one id at most). Imports from earlier strands go in `imports`, and the teacher says out loud what is being imported.
4. **Weave.** Never ask for something the lesson has not given the means to build. Do not teach topic by topic.
5. **Shape the load.** After a climb, an easy recombination, an `aside` (real and interesting, never a mnemonic) or a `recap`.
6. **Friction.** Once or twice, a step that is deliberately not broken down (`friction: true`).
7. **A classmate** (Ana or Davi) makes one predictable mistake just before the learner could, with the database's or Python's own message as the real reason. The learner may repair it (a `classmate` step with a `model`).
8. **Close** with a surprise sentence that builds on everything, then a `recap` that says the lesson is acquisition and not speed and tells the learner not to revise, then a closing cold check with `after_run: "That's the sitting. We pick up from here next time."`.

## What every typed step carries

`text` (the prompt, warm and short, in changing wording), `thinking_order` (optional, same request table first), `model`, the expected result (`rows` and `result` for SQL, `output` for Python), `requires` (every thought the answer needs), `narration` (two or three lines saying what the learner just did, at varying depth, one may be `""`), `wrong` (the predictable mistakes, each with `ask`, a leading question that does not give the answer, and `why`, the real reason, or a `tell` when there is nothing to ask), `walk` (the step in two or three smaller prompts), `note` (why the step is here, never shown), and `return`.

A **return** is a different sentence on the same thoughts, played when the step was missed. It has `text`, `model`, the expected result, and two or more narration lines. It must use only thoughts the step requires, differ from the step's sentence, and give a different result. Where the step is judged by order, so is its return.

Every typed step except a cold check has a return.

## Python steps

Add `lang: python` to every step, including `give` steps. Python is judged by what it prints.

- A step whose answer prints nothing itself, such as one that asks for a function, needs `check`: code that is run after the learner's code and printed. Give the expected printed text as `output`. A return needs its own `check` if its step has one.
- Spelling is not forgiven. There is no slip view in Python.
- A wrong answer uses `code`, not `sql` (`w(code, ask=..., lang="python")`).
- Every pandas script starts by reading its own files, typed each time: `orders = pd.read_csv('orders.csv')`. The files are in the working folder under their own names.
- Use `random_state=0` anywhere a model or a split is random. A step's answer must print the same thing every time.
- Output is compared by its words and numbers, whatever the spacing, with numbers to six places. Print rounded numbers when the lesson is about a result, so the learner is not judged on the 12th digit.
- Multi-line `model`, `check` and `shows` strings are fine. They are written as readable blocks.

## Things the checker will catch, and why

- **Every sentence must run** against `data/`. Run your whole lesson through the checker often.
- **A wrong answer must differ from the model.** A sentence that gives the same rows or the same output is not wrong. The checker fails it. SQL column names are ignored, so a missing `AS` cannot be a wrong answer.
- **No shape repeat.** Two consecutive typed steps must differ in more than one slot. For SQL a slot is a clause (`SELECT`, `FROM`, `WHERE`, `GROUP BY`, `ORDER BY`, `LIMIT`). For Python it is a run of tokens. Changing the table and adding a `WHERE` is two slots.
- **Order and ties.** When a step is judged by row order (`ordered: true`), sort by a column with no ties, or the answer is ambiguous. Check with a query. When ties are unavoidable, compare as a set and say so in the `note`.
- **The audit.** Every `requires` id must be introduced by an earlier step in the course, in this or an earlier lesson, or by this step. Define the thoughts your lesson introduces in the lesson file, under `thoughts:`. A thought is a string, or `{text: ..., grade: shape}` for a spelling the teacher always supplies. A step that requires a shape thought lists `supplies`, each spelling written exactly as it appears in the step's `text`.
- **At most one new thought per step**, and narration of at least two non-empty lines on every typed step except a cold check.
- **The load warning** (three steps in a row each introducing a thought) is allowed once or twice, on purpose, in the first steps of a lesson. It is only a warning.

## Writing well

- The teacher speaks to one person, warmly, in short sentences. No em dashes. No lists in the teacher's lines.
- Wording keeps changing. The same instruction is never phrased the same way twice. Narration varies in depth.
- A leading question points at the cause without giving the fix. Its `why` is stated after the learner gets it right.
- Name only what the learner has met. A column or table the lesson has not shown is named in the prompt.
- No invented mnemonics. "This just is" is a perfectly good reason when there is no other.
- No timer, score or word "wrong" anywhere the learner can see it. (The key `wrong` in the file is not shown.)
- Do not write a lesson that is not in an approved map. If the map is wrong, say so in the `note` of the step and in your report. Do not silently change it.

## Checking

```bash
uv run python -m checker content/<strand>      # one strand
uv run python -m checker content               # the whole course, once course.yaml lists your lessons
```

A single strand cannot see thoughts from other strands. Failures that say `unknown thought` or `which no earlier step introduces` about an id from another strand are expected until the course is put together. Everything else must be fixed.

Do not edit `content/course.yaml`, other lessons, or any code.
