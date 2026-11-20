# Michel Thomas method: research notes for a coding version

Date: 2026-11-19. Purpose: fix the pedagogy before building a small "Michel Thomas for DS interview coding" app (SQL first, pandas as a second dialect, target problem is the blank page).

## How far to trust this

- There is no controlled study of the Michel Thomas (MT) method in anything I found. Thomas was secretive and never wrote the method down.
- The main analysis is Jonathan Solity's book "The Learning Revolution". I did not read the book. I read a teacher's detailed notes on it, a 2008 Tes article, and two long critiques of it. Treat the Solity points as second-hand.
- The Language Transfer "Thinking Method" guidebook (420 pages, free) is the best primary source on the successor method. I read the ten techniques and the course-writing chapters in full and sampled the rest. See sections 6 and 7.
- The programming-education findings come from small studies, some seen only as abstracts.

## 1. The mechanics, as far as they can be reconstructed

1. **A recorded lesson with two real beginners.** The listener is the third student. The teacher gives a prompt in English, everyone thinks, the listener pauses and answers, then one student answers and the teacher gives the correct version last.
2. **One new element per step, used at once in a sentence.** Outside short revision phases, every step combines old and new material. Sentences get long fast but each step stays easy.
3. **Structure before vocabulary.** The course starts with "handles" such as "I want", "it is possible", "I can", and hangs everything on them. Vocabulary is tiny and mostly cognates.
4. **The order inside a step** (Solity's "teaching to accuracy" sequence): use the skill with no explanation, then give the rule, then more examples, then exceptions, then contrast the exception with the rule by minimal difference.
5. **Never teach by asking.** Thomas asks constantly, but only once every piece needed for the answer has been taught.
6. **Confusable items are kept apart at first** and only later contrasted. Verb forms are split and taught one at a time.
7. **Review is the teacher's job.** Old items come back inside new sentences on a schedule built into the script. One reviewer called it spaced repetition with the loop unrolled for you. Solity's phrase is "fewer items reviewed more often".
8. **Errors reflect on the teaching.** Correction is by hint, by analogy with something known, or by accepting a rough answer and shaping it. The correct answer is always echoed at the end.
9. **Rules for the learner.** Do not memorise, do not write, do not do homework, do not guess but think it out, and pause before answering.

## 2. Why it probably works

The method's own explanation is "no stress, no memorising". The cognitive explanation is different and more useful for us.

- **It is memorisation, but the method does it.** Every prompt is a retrieval attempt, old items return at growing gaps, and old and new are mixed. Retrieval practice, spacing and interleaving are among the best supported findings in learning research. The learner is told not to memorise because the script is already doing it in the most efficient way.
- **Low load per step.** One new element at a time keeps working memory free. This is the same logic as worked examples and Krashen's "i+1".
- **Production from the first minute.** The learner generates, which is what makes it active. The advice from the retrieval literature is not to look back at reference material unless stuck.
- **High-utility selection.** A Pareto choice of the few structures that generate the most sentences.
- **Generalisation is taught, not hoped for.** The same structure appears in varied contexts so the learner can build sentences never heard before.
- **Success rate is kept high,** which is the real content of the "no stress" claim. I found no evidence for relaxation itself as the active ingredient.

Solity ties all this to Engelmann's Direct Instruction. One critic disputes that, pointing out that Thomas almost never used negative examples, and frames it as Ausubel's progressive differentiation instead. For our purposes the disagreement does not change the design.

## 3. What goes wrong

- **Illusion of competence.** The strongest critique compares it to watching a plumbing video: you feel ready and are not. The method covers acquisition. In Haring and Eaton's hierarchy (acquisition, fluency, maintenance, generalisation, application) it stops well short of fluency and application.
- **No comprehension and no authentic practice.** It is "step 1" even by the publisher's own account.
- **Grammar without vocabulary** is of limited use on its own.
- **The posthumous courses failed in an instructive way.** Other teachers "mistook the tricks for the method". They overused mnemonics, edited out the students' mistakes, and lost the natural pacing. The mistakes and the pacing turn out to be load-bearing.
- **Unscripted teaching drifts.** Thomas's own later courses have organisational slips. A script can beat a teacher's judgement.
- **Language Transfer's own limit,** in its author's words: the course "parks the car and leaves the engine running", and the learner still has to take it out.

## 4. What programming-education research adds

- **Subgoal labels help code writing**, and labels given by the teacher beat labels the student invents. In our case the labels are the plain-English plan words (keep rows, make piles, summarise each pile, sort).
- **Worked example and completion problem pairs,** explicitly bundled, raise engagement and success. Support should fade: full example, partial example, then nothing.
- **Parsons problems** (arranging given lines) helped learners with low confidence when used as a scaffold before writing. Evidence that they teach writing better than writing does is thin.
- **Expertise reversal.** Someone who can already read code gains little from long worked examples and should move to production quickly.

## 5. What this changes in the design

1. **Keep "never try to remember" as the learner's rule, and put a real spacing schedule in the script.** Each element should return at steps roughly 1, 3, 8 and 20 after it is introduced, always inside a new sentence.
2. **Use first, explain second.** Each new element appears already filled in on its first use, with a one-line rule after. The first two or three prompts keep the new word visible, then it fades. (This comes from Grzega's classroom adaptation.)
3. **Step back through three levels when the learner misses:** a hint by analogy to something known, then the pieces to arrange, then the answer to copy. The same sentence returns a few steps later. Nothing is marked wrong.
4. **Keep the classmates and their mistakes.** Losing them is part of what broke the later courses.
5. **Keep confusable pairs apart, then contrast them.** WHERE and HAVING, `=` and `==`, SQL GROUP BY and pandas `groupby` each get their own stretch before a minimal-difference contrast.
6. **No reference panel and no notes.** The only help is the step-back.
7. **A fixed, scripted path** with step-back branches, not an adaptive engine.
8. **Guard against the illusion of competence.** Each session ends with one cold blank-page query on the real mock data, and each session opens with one from last time. It is unscored, and its only job is to tell the method where to restart.
9. **State the limit.** This covers acquisition. The existing mocks and the reading app are the application step.
10. **A forced "think it out" pause** before the input accepts typing, perhaps with the plan labels to tick in order.

## 6. The Thinking Method guidebook (Language Transfer)

**Coverage.** First pass: only the first 60 pages (introduction and techniques 1.1 to 1.6). Second pass, from the PDF the person supplied: 1.6 to 1.10 in full, 2.2 on performance, the introduction to the course analyses and the first five minutes of the annotated French script, 4.1 on grammar panoramas and 4.2 on starting to write. Not read: the rest of Part 2, the other five course analyses, 4.1.1 on vocabulary, 4.3 and Part 5. Section 7 holds the second pass.

Mihalis Eleftheriou says outright that Thomas's question-and-answer format is not where the quality comes from. It comes from the writing of the script. The book is about that writing.

### What the first six techniques say

1. **Inhabit the learner's mental theatre.** "Our student only knows what we tell them, when we tell it to them." The writer keeps checking each prompt against an imaginary learner who has heard only the script so far, and stops writing when that picture slips.
2. **One thought at a time, which is not one thing at a time.** What looks like one item to an expert is several thoughts to a beginner. The writer lists the separable thoughts behind a form and asks which should come first. The feeling of completeness is for the writer only. The learner should rarely feel something is missing.
3. **Manage cognitive load and tension contours.** Load should rise and fall on purpose. Too much gives "panic mode", where the learner clings to a mantra. Too little gives boredom. Relief comes from a change of subject, a masked repetition, an interesting side note, or a recap. A wrong answer is often an earlier item that has not been let go.
4. **Import knowledge.** Show the learner they already own the idea, for example that English has a subjunctive. Use deliberately literal translations ("I want that you go") to carry word order. Any rule left over for the learner to remember is "mental debris".
5. **Reframe.** Replace the textbook description with one that makes the pattern obvious, such as the German "sandwich" of two verbs. The limit is that "the target language will always have the final say".
6. **Weave.** Do not present material in a tidy, topic-by-topic order, and do not teach something early just because it is common. Common words come after the knowledge needed to understand them.

Also from the reader's notes: writing things down "creates an external loop" that becomes part of the process, so recall never forms without it. The script is "more like a route". Mistakes are feedback to the course writer about what to fix.

One limit a reader raised: the learner only ever answers the teacher's questions and never asks their own.

### What this adds to the design

1. **"One new element" becomes "one new thought".** `GROUP BY` is at least four thoughts: make piles, one output row per pile, every selected column must be the pile's name or a summary, and the summary function. The pandas filter `orders[orders.city == 'SP']` is three: name a column, the comparison gives a yes or no per row, the brackets keep the yes rows. Each gets its own step.
2. **A mental-theatre audit of the script.** Every prompt carries a list of the thoughts it needs, and a check confirms each was introduced earlier. This can be automated when we build.
3. **Imports for this learner.** Plain English for SQL, SQL for pandas, and possibly set and function notation from maths. Literal-English prompts carry the word order, for example "from orders, keeping where city is SP, give me the total".
4. **Reframes worth scripting.** HAVING is "WHERE for piles". A join is "look each row up in the other table". SQL is written in one order and thought in another, and the script should teach the thinking order.
5. **No mental debris.** If a step leaves a rule to remember, such as "don't forget `reset_index`", the step is wrong and needs redesigning or postponing.
6. **Weave, do not march through topics.** The path should not be SELECT, then WHERE, then GROUP BY as chapters. It should not start with the commonest idiom just because it is common.
7. **Shape the load.** After a heavy step, a few easy recombinations or a short aside, then the next climb.
8. **Misses are data about the script.** The app should log where you miss so the script can be revised after you use it.
9. **Typing is not "writing things down".** Typing the answer is the speaking. The ban applies to notes and cheat sheets.

### Extra sources

- https://www.languagetransfer.org/guidebook (The Thinking Method guidebook, first edition, PDF)
- https://rosano.ca/blog/language-transfer-the-thinking-method
- https://lingopie.com/blog/language-transfer-review/

## 7. The Thinking Method guidebook, second pass

The author repeats the central claim in Part 3: "the magic of the Thinking Method is not to be found in the Socratic question and answer system, but in the course content itself."

### 7.1 Masked repetition (1.7)

- Repetition is constant but should almost never be felt. Obvious repetition is boring, and worse, it invites shortcuts. "The mind is a cleverly lazy thing, and will quickly abandon the thought processes that we are installing in favour of shortcuts." The learner finds a template that produces the current answers without the thinking, and the template fails later on wider cases.
- So neither the wording nor the structure of the course may be repetitive.
- Ways to mask it: reword the same instruction a breath later; give an alternative explanation; leave a hard item and come back to it relaxed; change one small thing in the target sentence (the noun, the verb, statement to question) so the focus shifts while the old process is still required; contrast with a similar-looking form.
- Feedback is the best hiding place. After a correct answer the teacher narrates the process ("good, you removed the ending and pulled the accent back"). The narration varies: sometimes all the movements, sometimes one, sometimes none, so the learner does not tune it out.

### 7.2 Cueing (1.8)

- What the learner is asked to do: pause, think it through, answer out loud, not obsess with remembering, let go of what was just covered, and "trust that we won't let them forget". "Think slowly to learn quickly."
- Target sentences are exercises, not tests. The learner should not "produce target sentences from memory, but rather find them, time and again". The course does not aim for fluency. It sets up the framework that makes fluency follow from use.
- Bad habits to cue against: actively memorising, simplifying the teacher's rules, answering as fast as possible, building one's own summary tables.
- Kinds of information are signalled: essential, supporting, or just interesting. Without that, a side note cannot lower the load because the learner treats everything as vital.
- Implicit import: if nothing was said, assume it works as in the base language. This only holds because the course never asks for a sentence it has not given the means to build.
- Cueing for doing: instructions are worded loosely and differently each time ("get rid of the ending", "remove the final -ar", "take away the bit that means 'to'") so that what stays is the movement, not a sentence that memory can corrupt. Instructions often only make sense after the example.
- No artificial mnemonics. They blur real explanations with empty hooks, and they imply everything needs a hook. Learners must be told early that some things "just are". Otherwise they stall on "why?" or invent their own reasons.
- Give or solicit: do not ask the learner to work out something when a lucky right answer would teach a false generalisation.

### 7.3 Correction (1.9)

- Anyone can say an answer is wrong. The teacher has to know what went wrong in the learner's process.
- The ladder: ask for it again, "not from memory, but thinking it through again". If it recurs, prompt the process step by step. Where the cause is clear, ask one question that leads to self-correction ("are we using an adjective here?"), then state why that question mattered.
- A wrong answer can trigger an unplanned extra sentence that re-uses the corrected point.
- Preventative correction: discuss a likely confusion before it happens, especially two forms that look alike or a habit carried over from the base language.
- Masked correction: narrating the correct process after a right answer silently corrects the remote learners who got it wrong.
- Indirect correction: let a small slip pass and simply echo the model answer, so the current build-up of difficulty is not broken.
- The recorded student's careless slips are mostly edited out, but enough mistakes stay in to show that the student errs too. Listeners otherwise feel inferior to a "genius" student.

### 7.4 Thought and language (1.10)

- The learner is taught that the thought and the sentence are different things. The work is "to identify the different elements of the idea it represents, and think about which of those elements will come first in the target language".
- The same prompt is given in two wordings ("I'll pick him up", "I'll collect him") to show it is an idea, not a set of words.
- Awareness of the base language is raised before importing from it.
- The course names the shortcuts the learner's mind will try to take, so the learner can catch them.
- It also describes what to do when meeting something new after the course, as a bridge to real use.

### 7.5 Weaving, the rest (1.6)

- The writer keeps "vertical" reference tables but never teaches from them. Sense in a language often runs "horizontally" across those tables.
- Background for any new concept must already be familiar, so the learner is "expanding what we know (rather than what we are just learning)". This is done by pre-inserting pieces many lessons earlier. A topic's pieces can be spread across dozens of lessons, which is why the courses have no index.
- Exceptions are saved for last so the general rule is strong first.
- A late item can resolve a tension that was set up earlier by an unexplained remark.

### 7.6 Starting a course (4.1, 4.2, French analysis)

- Before writing, build panoramas: tables of everything the language does, then look across them for shared thoughts. The example is Spanish verb endings, which split into a time part and a person part, so the learner can build endings never shown.
- Start with sentences quickly. Long preambles are a mistake the author says he would fix.
- Begin with overarching concepts that apply widely: "few explanations that will have very varied applications". Hard or narrow material is woven around at the start.
- A preference for common language is only a light preference.
- Include some "artificial friction" early, a prompt not broken down for the learner, so they learn the course cannot be done on autopilot.
- Rules of engagement are taught the same way as content. The newest course drops the instructions track and mentions pausing at the moment of the first real prompt.
- The first full sentence is not pre-rehearsed in parts. The surprise of being able to build it is motivating. If the learner freezes, split the thought.
- The author spends about ten times longer rewriting than writing, and writes alternative openings as an exercise.
- Delivery matters (2.2). A script read "like a shopping list" fails. The teacher's energy is what gets the learner to drop old habits.

### 7.7 What the second pass changes in the design

1. **Vary the shape of every prompt.** The blank-page freeze may itself be the result of learning templates. Two consecutive prompts should never be answerable by editing the previous answer in the same slot.
2. **Narrate the movements after each answer,** in varied wording and varied depth. This is the app's repetition engine and its silent correction at once.
3. **A correction ladder with diagnosis.** Predictable wrong answers map to one leading question, for example a `WHERE COUNT(*) > 5` attempt gets "is that a question about rows or about piles?". Unrecognised misses get "again, thinking it through", then the step-by-step walk.
4. **Let small slips pass.** Case, spacing, quote style, a missing semicolon. Show the model answer and move on.
5. **Prompts in changing English.** "Keep", "only", "just the ones where", "filter to". This holds the movement rather than the wording, and it rehearses what interviewers do, which is phrase the same request many ways.
6. **Teach the thought separately from the code.** Before typing, the learner names the elements of the idea and which comes first. This brings some decomposition into version one after all.
7. **No instructions screen.** Each rule of engagement appears when it first matters.
8. **No invented mnemonics, and say early that some spellings just are.**
9. **Start from one overarching idea.** The candidate is "a table goes in, a table comes out", which holds for every SQL clause and every pandas step.
10. **Build the panorama before the script.** One sheet listing every thought behind filter, pile, summarise, sort and join in both dialects, then look across for shared thoughts.
11. **No timer and no speed pressure anywhere.** Speed is the application stage, which the mocks cover.
12. **The teacher's voice is warm and conversational,** not a manual.
13. **Expect to rewrite.** Log misses, revise the script, repeat.

## Sources

- https://michelthomas.com/how-it-works
- https://planspace.blogspot.com/2011/06/learning-revolution.html (notes on Solity's book)
- https://www.tes.com/news/celebrity-road-fluency
- https://www1.ku.de/SLF/EngluVglSW/ELiX/grzega-132.pdf (Grzega, Language Workout)
- https://www.omniglot.com/bloggle/?p=724
- https://linguafrankly.blogspot.com/2012/09/michel-thomas-vs-direct-instruction.html
- https://www.lesswrong.com/posts/FMpnREfJzbf3JSyfb/review-michel-thomas-french-direct-instruction
- https://mezzoguild.com/learning-about-a-language
- https://www.languagetransfer.org/about
- https://irishtechnews.ie/interview-language-transfers-mihalis-eleftheriou/
- https://www.alllanguageresources.com/language-transfer/
- https://forum.artofmemory.com/t/thoughts-on-the-thinking-method/64680
- https://par.nsf.gov/biblio/10598698-impact-connecting-worked-examples-completion-problems-introductory-programming-practice
- https://core.ac.uk/works/77773088
- https://static.raspberrypi.org/files/curriculum/quickreads/2-Pedagogy_Summary_Worked_Examples_V6_2023.pdf
- https://justinmath.com/which-cognitive-psychology-findings-are-solid-that-can-be-used-to-help-students-learn-better/
- https://par.nsf.gov/servlets/purl/10301529 (Morrison, Decker, Margulieux, ICER 2016)
