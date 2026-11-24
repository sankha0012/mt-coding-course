# Curriculum

Two passes over three strands, about 27 lessons and eight hours. This file is the overview. The thoughts of each lesson, in order, with the sentence each lesson builds to, are in the strand maps:

- `docs/maps/sql.md`
- `docs/maps/python.md`
- `docs/maps/pandas-ml.md`

The earlier version of this file had three stages, the third a timed one. The goal was restated on 24 Nov 2026 (see `docs/01-scope.md`), and the timed stage moved to `live-coding-gym`.

## The overarching ideas

One per strand. Each is the first thing the learner meets and the thing everything else hangs from.

| Strand | Idea |
|---|---|
| SQL | A table goes in, a table comes out. |
| Python | Give a thing a name, then do something with it. |
| pandas | The same movements as SQL, written in thinking order, in Python. |

Two observations tie the strands together and are used throughout:

- **SQL is written answer-first and thought table-first.** The thinking order is: from the table, keep rows, make piles, summarise, keep piles, sort, cut. pandas is written in exactly that order. SQL prompts phrased in thinking order from the start make pandas nearly free later.
- **Python re-uses the SQL thoughts by hand.** A loop is "from". An `if` is "where". A dict of running results is "group by". A running total is a summary.

## Three grades

Each thought is core, shape or name only (decision C10, explained in `docs/01-scope.md`). Core is typed from memory. For shape, the teacher's line supplies the spelling every time. Name only is a single aside.

Grades are what make eight hours enough. Date functions, window frames, import lines and the rarer pandas methods are shape grade: the learner knows the thought and its name, and is told plainly that this is something everyone looks up.

## Order

Breadth first (decision C12). The foundation of all three strands comes before the interview layer of any.

### Pass 1: foundation, 14 lessons

| # | Lesson | Closes with |
|---|---|---|
| SQL-1 | From "how many?" to piles (written) | Average subtotal per restaurant, delivered only |
| SQL-2 | Sort and cut | The five restaurants with the most delivered orders |
| SQL-3 | Keep piles, and empty cells | Restaurants with more than 100 delivered orders |
| SQL-4 | Look things up in another table | Average subtotal per city |
| PY-1 | Name a thing, then do something with it | Count the delivered orders by hand |
| PY-2 | Lists that grow | The three biggest subtotals above 50 |
| PY-3 | Look up by name | The total price of an order |
| PY-4 | Piles by hand | Average price per dish |
| PY-5 | Wrap it as a function | A function with two checks of your own |
| PY-6 | A table by hand | Average per key, ignoring missing values |
| PD-1 | The same movements, in thinking order | Average subtotal of delivered orders |
| PD-2 | Piles in pandas | Top five restaurants by delivered orders |
| PD-3 | Clean and add columns | Load, clean, add two columns |
| PD-4 | Look things up in pandas | Are deliveries more often late when it rains? |

Then cold sitting A.

### Pass 2: the interview layer, 13 lessons

| # | Lesson | Closes with |
|---|---|---|
| SQL-5 | A result can be queried again | Restaurants above the average number of orders |
| SQL-6 | A number beside each row | Orders above their own restaurant's average |
| SQL-7 | Order inside the pile | Top three per restaurant, and each customer's latest order |
| SQL-8 | Rows with no match | Coupons never used |
| SQL-9 | Dates and buckets | Month totals with the change from the month before |
| PY-7 | Sort by a rule | Top-k items, ties alphabetical |
| PY-8 | Text as pieces | Count the bigrams in a sentence |
| PY-9 | A loop that remembers | Sessions from timestamps |
| PY-10 | Say it shorter, say its cost | Three checks and the cost, and merging sorted lists at shape grade |
| PD-5 | Windows in pandas | Each customer's latest order, in pandas |
| ML-1 | Fit, predict, evaluate | Predict late deliveries and report a metric |
| ML-2 | The same shape, any model | Raw table to a metric in one script |
| ML-3 | K-fold by hand | `cross_validate(model, X, y, k)` |

Then cold sitting B.

### Cold sittings

A cold sitting is about ten minutes of five or six blank-page prompts drawn from all three strands. It has no ladder, no narration and no score (rule F1). It adds no thoughts and is not counted as a lesson. Its only job is to show where the course has to go back.

The cold sittings are planned on real data the learner has never seen: the Olist Brazilian e-commerce dataset, which is the same world as the lessons with real names and real mess. The lessons themselves stay on the practice tables. See `docs/maps/pandas-ml.md`. The dataset is in `data/real/olist/`, outside git.

## How the strands stay alive across the gaps

Breadth first leaves SQL untouched for ten lessons. Three things cover the gap:

- **Every sitting opens with a cold check from an older strand**, once there is one.
- **Python and pandas ask the same business questions on the same data** as the SQL lessons and get the same numbers. The narration names the echo: "that was `GROUP BY`, by hand".
- **Pass 2 SQL imports Python thoughts by name.** `WITH` is "name a thing, then do something with it".

## Why this order of strands

- SQL first, because it is nearly English and carries the five core thoughts with almost no syntax.
- Python second, because it re-uses those thoughts and supplies the syntax pandas is made of.
- pandas last, because by then brackets, quoted names, methods and `==` are all familiar.

## Pairs to keep apart, then contrast

| Pair | Where they meet |
|---|---|
| Keep rows and keep piles in SQL | Piles in SQL-1. Keep piles in SQL-3, as the same question asked of piles. |
| One equals sign and two | One is naming from the first line of PY-1. Two arrives later in PY-1, through a classmate. pandas inherits it. |
| Lists and dicts | Lists alone in PY-1 and PY-2. Dicts from PY-3. |
| Position and name | Contrasted in PY-3. |
| Showing a value and returning one | Showing from PY-1. Returning in PY-5, where the two are contrasted. |
| One column and a list of columns in pandas | One column in PD-1 and PD-2. The list in PD-3, with its real reason. |
| Python's `and` and pandas' `&` | `and` in PY-2. `&` in PD-2, with the reason it differs. |

## Size

About 27 lessons. At 20 minutes each that is nine hours, and at 18 it is eight. Nothing supports the per-lesson figure yet. The owner's first sitting of SQL-1 gives the first real measurement, and lesson sizes are adjusted from it.

Settled on 24 Nov 2026: PY-1 keeps its twelve thoughts, and the ML lessons use `data/deliveries.csv`, a synthetic table in which distance, rain and the courier's load predict lateness.
