# Pedagogy rules

These are the rules every lesson script and every app feature must obey. Each has a short reason. The full evidence is in `docs/research/01-method-research.md`, which draws on Jonathan Solity's analysis of Michel Thomas, Mihalis Eleftheriou's Thinking Method guidebook, and programming-education research.

One sentence from the guidebook governs everything else: the magic "is not to be found in the Socratic question and answer system, but in the course content itself". The script is the product. The app is its delivery.

## A. What the learner does

**A1. The learner always produces.** Every prompt is a translation from a plain question into code, typed out. Recognition tasks do not train production.

**A2. Think it out, do not guess.** The learner pauses, works out the answer, then types. The app makes room for the pause.

**A3. The learner is told not to memorise.** They are asked to let go of what was just covered and trust that it will come back. This is honest only because rule C1 makes it true.

**A4. Prompts are exercises, not tests.** The learner should "find them, time and again", not recall them. Nothing is scored.

**A5. No notes.** Writing things down builds an external loop that recall then depends on. Typing the answer is not note-taking. It is the speaking.

## B. How a step is built

**B1. One new thought per step.** A thought is smaller than a feature. Grouping in SQL is at least four thoughts: make piles, one row per pile, what to say about each pile, and showing the pile's name. Each gets its own step.

**B2. Nothing is asked before its parts are given.** The writer checks every prompt against a learner who has seen only the script so far. This is called inhabiting the learner's mental theatre.

**B3. Use first, explain second.** A new element appears already in use, then gets its one-line reason. An instruction often only makes sense after its example.

**B4. Give or ask.** Ask when the learner can build the answer. Give when a lucky correct guess would teach a false generalisation.

**B5. No mental debris.** If a step leaves the learner with an arbitrary rule to remember, the step is wrong. Either find the real reason, find an order that makes the rule a discovery, or postpone it.

**B6. No invented mnemonics.** They blur real explanations with empty hooks. Real origins are fine. Where there is no reason, say so early: some things just are.

**B7. Import what the learner already owns.** English for SQL, SQL for Python, Python for pandas, and mathematics where it helps. Say explicitly what is being imported.

**B8. Reframe awkward things.** Replace the textbook description with one that makes the pattern obvious. Example: `HAVING` is the same keep-rows question, asked of piles.

## C. How the course is ordered

**C1. The script does the spaced repetition.** Each element returns inside new sentences at widening gaps, roughly 1, 3, 8 and 20 steps after it first appears.

**C2. Repetition is masked.** The learner should rarely feel a repeat. Visible repetition is boring and, worse, invites shortcuts: "the mind is a cleverly lazy thing, and will quickly abandon the thought processes that we are installing in favour of shortcuts".

**C3. No two consecutive prompts share a shape.** A prompt must not be answerable by editing one slot of the previous answer. Change two things at once, or change the kind of sentence.

**C4. Weave, do not march.** Do not teach topic by topic. Pre-insert the background for a hard idea many steps before it arrives, so the learner is expanding something familiar.

**C5. Common is only a light preference.** Do not teach something early just because it is frequent. Order serves the explanations.

**C6. Keep confusable things apart, then contrast them.** Each of a pair is comfortable alone before the two meet.

**C7. Exceptions come last,** after the general rule is strong.

**C8. Shape the load.** Difficulty rises and falls on purpose. After a climb comes relief: easy recombinations, a short aside, a recap.

**C9. Include deliberate friction.** Now and then a prompt is not broken down for the learner. It signals that the course cannot be done on autopilot.

**C10. Open with one widely applicable idea and reach full sentences fast.**

## D. How the teacher speaks

**D1. Wording keeps changing.** The same instruction is phrased differently each time, so the learner keeps the movement and not the sentence. For this course it also rehearses a real interview difficulty: the same request arrives in many phrasings.

**D2. Prompts separate the thought from the code.** The learner identifies the elements of the idea and which comes first, then writes. Early prompts are phrased in thinking order to make this visible.

**D3. Narrate after a correct answer.** The teacher says what the learner just did, varying the wording and the depth: sometimes every movement, sometimes one, sometimes nothing. This is hidden repetition and silent correction at once.

**D4. Signal the kind of information.** Essential, supporting, or just interesting. An aside can only lower the load if the learner knows it is an aside.

**D5. Rules of engagement arrive in context.** No instructions screen. "Stop and think before you type" appears at the first real prompt.

**D6. Warm and conversational.** A script read like a manual fails. The voice is a person talking to one learner.

## E. What happens after a miss

**E1. Nothing is marked wrong.** A miss reflects on the script.

**E2. Diagnose, do not just detect.** The aim is to know what went wrong in the learner's thinking.

**E3. The correction ladder.**

1. "Again, thinking it through, not from memory."
2. For a predictable error, one leading question that points at the cause. Then the teacher states why the question mattered.
3. Walk the thought step by step.
4. As a last resort, offer the pieces to arrange, then the answer to copy.

**E4. The missed sentence returns** a few steps later inside a new one.

**E5. Let small slips pass.** Letter case, spacing, quote style, a missing semicolon. Show the model answer and move on, so the current climb is not broken.

**E6. Correct in advance.** Where a confusion is predictable, a classmate makes the mistake first and is corrected, before the learner can make it.

**E7. Keep the classmates' mistakes.** The courses made after Thomas's death edited the students' errors out, and lost something that mattered.

## F. Guarding against false confidence

**F1. Cold checks.** Each sitting opens with one blank-page prompt from the previous sitting and closes with one from the current one. They are unscored. Their only job is to tell the script where to restart.

**F2. State the limit.** The course is acquisition. It does not make the learner fast.

**F3. Speed is trained elsewhere.** No timer appears in this course. Timed practice lives in `live-coding-gym` (decision O6).

## G. For the writer

**G1. Build the panorama first.** List every thought behind every movement, in every dialect, then look across the list for thoughts that recur.

**G2. Expect to rewrite.** The guidebook's author spends about ten times longer rewriting than writing.

**G3. Misses are data.** Record where the learner misses and revise the script.

**G4. Write alternative openings** and compare them before committing.
