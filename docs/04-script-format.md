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
| Check | How an answer is judged. Normally by running it and comparing the result with the model answer's result. |
| New thought | At most one identifier, or none for a recombination step. |
| Required thoughts | Every thought the answer needs. The audit checks each was introduced earlier. |
| Narration | Several alternative lines the teacher can say after a correct answer, describing what the learner did. At varying depth. One may be empty. |
| Known wrong answers | Predictable mistakes, each with a leading question and the reason the question matters. |
| Step-by-step walk | The prompt split into smaller prompts, used on the third rung of the correction ladder. |
| Friction | A flag for steps that are deliberately not broken down. |
| Note for the writer | Why the step is here. Never shown to the learner. |

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

## Writing guidance

- Write the panorama for the lesson's area before the lesson.
- Draft, then rewrite many times. Expect the rewriting to take far longer than the draft.
- Read each prompt as a learner who has seen only the steps above it.
- When a step leaves a rule to remember, do not add a hint. Reorder until the rule becomes a discovery, as the pile-name step does in Opening B.
- Keep one classmate mistake or so per ten minutes, placed just before the learner would make the same mistake.
- The teacher speaks to one person, warmly, in short sentences.
