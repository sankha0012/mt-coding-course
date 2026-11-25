# Lesson script format

This describes what a lesson script contains. It does not fix a file format. Choose one that keeps lesson text out of app code and is easy for a person to read and edit. The sibling `live-coding-gym` uses plain files in a `content/` folder and that has worked.

Two worked examples of scripts written to this shape are in `docs/research/02-panorama-and-openings.md` (Opening B for SQL and the Python opening). Read those before writing a new lesson.

## A lesson

A lesson is one sitting of roughly ten to twenty minutes. It is an ordered list of steps, plus:

- The strand and stage it belongs to.
- The thoughts it introduces, by identifier.
- The thoughts it assumes from earlier lessons.
- An opening cold check drawn from the previous lesson, and a closing cold check from this one.

## Kinds of step

| Kind | What the learner sees | What the learner does |
|---|---|---|
| **Give** | The teacher introduces something and shows it in use | Reads. May be asked to run it. |
| **Ask** | A prompt in plain language | Types the answer |
| **Classmate** | Another learner's attempt with a typical mistake, and the teacher's leading question | Reads, or is asked what the classmate should change |
| **Aside** | Something interesting but not essential, clearly marked as such | Reads |
| **Recap** | A short summary after a climb | Reads |
| **Cold check** | A blank-page prompt with no build-up | Types the answer. Never scored. |

## What an Ask step carries

| Field | Meaning |
|---|---|
| Prompt | The teacher's line. Plain language. Its wording should differ from the last prompt that used the same movement. |
| Thinking-order version | Optional. The same request phrased table first, for early lessons and for the correction ladder. |
| Model answer | One answer that runs against the data. |
| Start | Optional, Python only. Text the editor opens with, usually the data the prompt gives, such as `subtotals = [28.04, 57.72]`. The model answer must begin with it. Use it where typing the data is not the thought being practised. Keep it typed in the steps that introduce or return to a list, a dict or a name. |
| Check | How an answer is judged. Normally by running it and comparing the result with the model answer's result. |
| New thought | At most one identifier, or none for a recombination step. |
| Required thoughts | Every thought the answer needs. The audit checks each was introduced earlier. |
| Narration | Several alternative lines the teacher can say after a correct answer, describing what the learner did. At varying depth. One may be empty. |
| Known wrong answers | Predictable mistakes, each with a leading question and the reason the question matters. |
| Step-by-step walk | The prompt split into smaller prompts, used on the third rung of the correction ladder. |
| Friction | A flag for steps that are deliberately not broken down. |
| Note for the writer | Why the step is here. Never shown to the learner. |

## Grades

Every thought is core, shape or name only (decision C10, explained in `docs/01-scope.md`).

- A **core** thought is asked for and comes back spaced.
- A **shape** thought is asked for only in steps whose teacher's line carries the spelling. The line also says plainly that this is something people look up, for example: "This one you would look up. The thought is: cut a date down to its month. Here it is spelled `strftime('%Y-%m', created_at)`." A shape step lists the spellings it supplies, and the checker confirms each appears in the step's text. This is not a reference panel: the spelling arrives in the teacher's voice, at the moment it is needed.
- A **name only** thought appears in one Aside and in no prompt.

In `thoughts.yaml` a core thought is a plain string. A shape or name-only thought is written `{text: ..., grade: shape}` or `{text: ..., grade: name-only}`. A step that supplies spellings lists them in `supplies`, each exactly as it appears in the step's `text`. Check 9 enforces it: a step that requires a shape thought must have `supplies`, every `supplies` entry must appear in the step's text, and no step may require a name-only thought.

## Languages and data

A step is SQL unless it says `lang: python`. Python covers plain Python, pandas and scikit-learn. A step may name its data folder with `data`, relative to `data/`. A lesson whose folder is missing is left out.

- **Python answers are judged by what they print.** A step that asks for a function, or any program that prints nothing itself, carries `check`: hidden code that is run after the learner's code and printed. The learner sees only what their own code printed. A step with no output and no `check` is a fault, and the checker says so.
- A return in a Python step is played in the same language and on the same data. If its step has a `check`, the return needs its own.
- `output` is the expected printed text of a Python model answer, in place of `rows` and `result`.
- In `wrong`, a Python entry uses `code` where an SQL entry uses `sql`.
- Output is compared by its words and numbers, whatever the spacing, with numbers rounded to six places.
- Python has no slip view. Its ladder ends in a Python code block.
- The learner's code runs in a long-lived worker process that imports pandas and scikit-learn once, in a temporary folder whose CSV files are read-only links to private copies. A program that runs for too long is stopped.

## MongoDB steps

A step is a MongoDB step when it says `lang: mongo`, and it names its data folder with `data: mongo` (the course documents in `data/mongo/`). The lessons are in the optional MongoDB extra (decision C28).

- **One sentence per answer**, in the mongosh shell's spelling: `db.<collection>.<method>(...)`, with `.sort()`, `.limit()` and `.skip()` chained after a `find`. No JavaScript is run. The runner reads the sentence, so anything it does not read, such as a variable, gets a calm line.
- **Answers are judged by the values of the documents.** A computed field may be called anything, and the order of fields inside a document is free. Row order matters only with `ordered: true`.
- `rows` is the number of documents, and `result` lists the expected values of each document, as for SQL.
- A step that writes (`updateOne` and the like) says `scratch: true`. It runs on a copy of the data that is made for that sentence and dropped afterwards, so the course data never changes.
- Text is written in double quotes. A learner may type single quotes.
- The learner's sentence is run on a real `mongod`, which the program starts privately. Where there is none, the MongoDB lessons are left out and named at start up.

## Several lessons

A strand folder holds `lesson-01.yaml`, `lesson-02.yaml` and so on, and its own `thoughts.yaml`. `content/course.yaml` lists the lessons as `strand/lesson-01`, in the order they are played, which interleaves the strands. An id may be defined in one strand's `thoughts.yaml` only, and any lesson may require any earlier thought, whichever strand it came from. The checker takes either a course folder or a single strand folder. A lesson opens with a cold check from an earlier lesson by starting with a step of kind `cold-check`. The audit lets it require any thought from any earlier lesson. When a lesson ends, the player offers the next one, or to sit the same lesson again.

## Cold sittings

A cold sitting is a short lesson file made only of Cold check steps, drawn from every strand taught so far. It has no ladder, no narration and no score. Two exist, one after each pass (see `docs/03-curriculum.md`).

## What a Give step carries

The teacher's text, the example in use, the one-line reason or the statement that this just is, the new thought's identifier, and whether what is imported is being named (for example "commas, as in English").

## Thoughts

Every thought in the curriculum has an identifier and a one-line description, kept in one list. For example: "a question asked of each row", "text wears quotes", "one row comes out per pile". The list is what makes the audit possible and what the spacing schedule counts.

## The checks a script must pass

These should be automated early. They are the equivalent of the gym's content checker.

1. **Every model answer runs** against the data in `data/` and returns a non-empty, sensible result.
2. **The audit passes.** Every required thought of every step was introduced by an earlier step, in this lesson or a previous one.
3. **One new thought at most** per step.
4. **No shape repeats.** Flag any two consecutive Ask steps whose model answers differ in only one slot.
5. **Spacing.** For each thought, report the steps at which it is required after its introduction, so gaps and pile-ups are visible. The target is a return at roughly 1, 3, 8 and 20 steps.
6. **Narration variety.** Flag an Ask step with fewer than two narration lines.
7. **Load shape.** Report where new thoughts fall, so that three in a row without relief stands out.
8. **Start text.** A `start` is for a Python step, and the model answer begins with it.

## Writing guidance

- Write the panorama for the lesson's area before the lesson.
- Draft, then rewrite many times. Expect the rewriting to take far longer than the draft.
- Read each prompt as a learner who has seen only the steps above it.
- When a step leaves a rule to remember, do not add a hint. Reorder until the rule becomes a discovery, as the pile-name step does in Opening B.
- Keep one classmate mistake or so per ten minutes, placed just before the learner would make the same mistake.
- The teacher speaks to one person, warmly, in short sentences.
