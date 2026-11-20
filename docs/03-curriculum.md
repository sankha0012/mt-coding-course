# Curriculum

Three stages, and inside the first two, three strands. This is an outline of thoughts and their order. It is not yet a script. The detailed panorama for stage 1, with code checked against the data, is in `docs/research/02-panorama-and-openings.md`.

## The overarching ideas

One per strand. Each is the first thing the learner meets and the thing everything else hangs from.

| Strand | Idea |
|---|---|
| SQL | A table goes in, a table comes out. |
| Python | Give a thing a name, then do something with it. |
| pandas | The same movements as SQL, written in thinking order, in Python. |

Two observations tie the strands together and should be exploited throughout:

- **SQL is written answer-first and thought table-first.** The thinking order is: from the table, keep rows, make piles, summarise, keep piles, sort, cut. pandas is written in exactly that order. SQL prompts phrased in thinking order from the start make pandas nearly free later.
- **Python re-uses the SQL thoughts by hand.** A loop is "from". An `if` is "where". A dict of running results is "group by". A running total is a summary.

## Order of the strands

SQL, then Python, then pandas.

- SQL first, because it is nearly English and carries the five core thoughts with almost no syntax.
- Python second, because it re-uses those thoughts and supplies the syntax pandas is made of.
- pandas last, because by then brackets, quoted names, methods and `==` are all familiar.

## Stage 1. Foundation

Goal: the learner can always write something that runs. No timer.

### SQL strand

Movements, in panorama order (teaching order is woven, see below):

1. Name the table.
2. Choose columns.
3. Keep rows: a yes-or-no question asked of every row. Numbers, then text in quotes.
4. Summarise to one number: count, average, total, biggest, smallest.
5. Make piles: one row per pile, a summary of each, the pile's name shown.
6. Keep piles.
7. Sort and take the top.
8. Look things up in another table.

Recommended opening: start from "how many orders?" so that every sentence answers a question, reach piles within about ten minutes, and let the learner discover why the pile's name must be selected by first seeing unlabelled numbers. This is Opening B in the research document. Opening A, which starts from looking at the table, is the alternative.

Woven around at the start: joins (the orders table has no city, which lives in restaurants), missing values, two conditions at once, dates.

### Python strand

1. Name a value. Numbers, text, yes and no.
2. A list: make, take one by position, add to the end.
3. Summaries already known from SQL: how many, total, biggest, sorted, first few. Build an average from total and count.
4. Go through each one. The colon opens a block and indented lines are inside it.
5. Ask a question inside the loop. Asking is two equals signs because one is taken for naming.
6. Keep a running result: start before, update inside, ready after.
7. A dict: look up by name, add or change, ask whether a name is there.
8. Piles by hand: a dict with one running result per pile.
9. Wrap steps as a function: what goes in, what comes out.
10. A table by hand: a row is a dict, a table is a list of rows.

A draft opening for this strand is in the research document. It ends with the learner writing a complete script that counts delivered orders, which is their first SQL question done by hand.

Woven around at the start: counting loops with `range`, positions beyond the first and last, shorthand operators, imports.

### pandas strand

Not yet designed in detail. In outline, each SQL movement returns in pandas form, in thinking order:

1. A table is a DataFrame. Read one from a file.
2. One column, then several. A column name is text, so it wears quotes.
3. Keep rows: write the question out in full, then hand the yes and no answers to the brackets.
4. Summaries follow the column.
5. Piles, with the pile names appearing on the left.
6. Keep piles, which needs no new word: the piles are a table, so keep rows applies again.
7. Sort and take the top.
8. Look things up in another table.

Decisions already taken to keep debris down: always brackets and quotes for a column, never the dot form; single quotes everywhere; no `reset_index`, `as_index` or dictionary aggregation in stage 1.

### Pairs to keep apart, then contrast

| Pair | Plan |
|---|---|
| One equals sign and two | One is long settled as naming before two arrives with the first text comparison in Python. pandas inherits it. |
| Keep rows and keep piles in SQL | Keep piles arrives well after piles are comfortable, as the same question asked of piles. |
| Lists and dicts | Lists fully comfortable first. |
| Position and name | Contrasted when dicts arrive. |
| Showing a value and returning one | Showing is only "show me" early. Returning arrives with functions, then the two are contrasted. |
| One column and a list of columns in pandas | One column for a long stretch. The list comes with its real reason. |

## Stage 2. Interview level

Goal: the remaining thoughts the pass bar needs, in the same method. No timer. This stage is outlined only.

| Strand | Thought | Note |
|---|---|---|
| SQL | A query's result can be queried again | Subqueries and named sub-results. This is the overarching idea applied twice, so it should cost little. |
| SQL | A number about the pile, written beside each row, without collapsing the rows | Window functions. The one truly new thought, and the centrepiece of this stage. It unlocks top N per group, latest row per customer, the previous row, and running totals: four of the six SQL pass-bar tasks. |
| SQL | Rows with no match | A second thought inside "look things up". |
| SQL | Dates, and buckets with conditional logic | Vocabulary on existing movements. |
| Python | Sorting by a rule, with ties | Small. |
| Python | Text as a list of pieces | Split, join, slices. Re-uses lists. |
| Python | A loop that carries state from one item to the next | Extends the running result. Sessions, merged intervals. |
| Python | Two positions moving through sorted data | Merging sorted lists, searching. |
| Python | Sets, pairs, one-line list building | Vocabulary. |
| Python | Writing your own tests and stating the cost | Habits. Cue them from stage 1 where it is free to do so. |
| pandas | Missing values, new columns, ranking within piles | Vocabulary on SQL thoughts. |
| pandas and ML | The fit, predict, evaluate routine | One fixed shape. |
| pandas and ML | One thing by hand | Cross-validation and a metric. The learner knows the maths, so only the code is new. |

## Stage 3. Speed and exams

Goal: clear the pass bar under real conditions.

- The seventeen pass-bar tasks from `docs/01-scope.md` as timed drills, in many variations.
- Writing against tables that cannot be seen, with exact output required, because auto-graded tests give no partial credit.
- Explaining aloud while writing.
- Practice on the real platforms' interfaces. One candidate in the research failed only because the interface was unfamiliar.

The sibling `live-coding-gym` and the owner's existing mock tests already do much of this. Whether stage 3 is built here or handed to the gym is an open decision.

## Coverage of the pass bar

| Pass-bar task | Stage where it becomes possible |
|---|---|
| 1, 2 | Stage 1, SQL |
| 3, 4, 5, 6 | Stage 2, SQL |
| 7, 8 | Stage 1 for the core, stage 2 for sorting with ties |
| 9, 10, 11, 12 | Stage 2, Python |
| 14 | Stage 1 for the basics, stage 2 in full |
| 13, 15, 16, 17 | Stage 2, pandas and ML |

## Size

Unknown. A rough guess is two hours of learner time for stage 1 SQL, two to three for Python and one for pandas, with stage 2 at least as large again. Nothing supports these numbers yet. The first written lesson will give the first real measurement.
