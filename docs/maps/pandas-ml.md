# pandas and ML strand map

Status: approved by the owner on 24 Nov 2026, with the answers recorded at the end. Read `docs/maps/sql.md` first for how a map is laid out.

Eight lessons. PD-1 to PD-4 are the foundation in pass 1, after PY-6. PD-5 and ML-1 to ML-3 close pass 2, after PY-10.

The strand's idea: **the same movements as SQL, written in thinking order, in Python.** Every lesson asks a question the learner has already answered in SQL, on the same data, and gets the same number. Nothing about the movements is new. Only the spelling is, and the spelling is Python the learner already owns: square brackets get from inside, quotes mean text, two equals signs ask.

**Every script starts by reading its files.** From PD-1 on, each closing sentence and each cold prompt begins with its own `pd.read_csv(...)` lines, and the learner typed them every time (the owner's decision, 24 Nov 2026). From 25 Nov 2026 the editor opens with those lines already in it (`start`, `docs/04-script-format.md`) from PD-2 on, except in cold checks and where a step is about reading or importing, because retyping them cost time and taught nothing new. Reading is the first line of every real script, and it is the line a blank page most easily freezes on. It needs no thought of its own after PD-1. It simply returns in every lesson, spaced for free.

Decisions carried over from the panorama, which keep things to remember down: a column is always written with brackets and quotes and never with a dot, single quotes everywhere, and no dictionary aggregation.

## Pass 1: foundation

### PD-1. The same movements, in thinking order

Assumes: SQL-1 to SQL-4, PY-1 to PY-6. Opens with: a cold check from PY-6.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `bring-pandas-in` | `import pandas as pd` brings the library in, under a short name. | Core |
| 2 | `read-a-table` | `orders = pd.read_csv('orders.csv')` reads a file into a table and names it. | Core |
| 3 | `dataframe` | The table is called a DataFrame. A table goes in, a table comes out, as before. | Core |
| 4 | `look-at-rows` | `orders.head()` shows the first rows. | Core |
| 5 | `column` | `orders['subtotal']` gets one column by name. The name is text, so it wears quotes. | Core |
| 6 | `summary-follows` | The summary comes after the column: `.mean()`, `.sum()`, `.max()`. In SQL it wrapped the column. | Core |
| 7 | `yes-no-column` | `orders['status'] == 'delivered'` asks every row and gives a column of yes and no. | Core |
| 8 | `brackets-keep-yes` | Hand that column to the brackets and only the yes rows come out. | Core |
| 9 | `name-the-result` | Name what came out, then do something with it. | Core |

Closes with: the average subtotal of the delivered orders.

```python
orders = pd.read_csv('orders.csv')
orders[orders['status'] == 'delivered']['subtotal'].mean()
```

Result: 60.43, the number SQL-1 step 14 gave.

Note: nine thoughts, but six are Python or SQL the learner owns, said aloud as imports. The filter is taught in two steps, question first and brackets second, so the doubled `orders` is never a thing to remember.

### PD-2. Piles in pandas

Assumes: PD-1.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `groupby` | `orders.groupby('status')` makes the piles. | Core |
| 2 | `pick-then-summarise` | Then pick the column, then say the summary: thinking order. | Core |
| 3 | `pile-names-on-left` | The pile names come out on the left, by themselves. Nobody has to ask for them. | Core |
| 4 | `size` | `.size()` counts the rows of each pile. | Core |
| 5 | `value-counts` | `orders['status'].value_counts()` is piles and a count in one word, biggest first. | Core |
| 6 | `sort-values` | `.sort_values(ascending=False)` sorts, biggest first. | Core |
| 7 | `keep-piles-again` | The piles are a table, so keeping piles is keeping rows. There is no second word. | Core |
| 8 | `row-by-row-and` | Two questions are joined with `&` or `\|`, each in its own brackets. Python's `and` asks once, and these ask every row. | Core |

Closes with: the five restaurants with the most delivered orders.

```python
orders = pd.read_csv('orders.csv')
orders[orders['status'] == 'delivered'].groupby('restaurant_id').size().sort_values(ascending=False).head(5)
```

Result: restaurant 2 with 113, 24 with 112, 3 and 59 with 109, 22 with 108. The answer SQL-2 gave.

Note: `pile-names-on-left` resolves, without a word, the tension that SQL-1 built in steps 15 to 17. `keep-piles-again` is why pandas has no `HAVING`. `value-counts` was added on 24 Nov: it is the first thing most people type on a table they have never seen, and the cold sittings will use tables the learner has never seen.

### PD-3. Clean and add columns

Assumes: PD-2.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `first-look` | `orders.info()` lists the columns, their kinds, and how many cells of each are filled. | Core |
| 2 | `list-of-columns` | A list of names gets several columns. One name gives a column, a list of names gives a table, which is where the two pairs of brackets come from. | Core |
| 3 | `new-column` | `orders['total'] = ...` adds a column, the way a dict takes a new name. | Core |
| 4 | `column-sums` | Columns add and subtract, row by row. | Core |
| 5 | `yes-no-as-column` | A question can be kept as a column of its own. | Core |
| 6 | `mean-of-yes-no` | The mean of a yes-or-no column is the share of yes. | Core |
| 7 | `find-missing` | `.isna().sum()` counts the empty cells of a column. | Core |
| 8 | `fill-or-drop` | `.fillna(value)` fills them, `.dropna(subset=[...])` drops their rows. Say which you chose and why. | Core |

Closes with: load a table, clean its missing values, add two columns (pass-bar task 13).

```python
orders = pd.read_csv('orders.csv')
orders['subtotal'] = orders['subtotal'].fillna(orders['subtotal'].median())
orders['total'] = orders['subtotal'] + orders['delivery_fee']
orders['late'] = orders['actual_minutes'] > orders['promised_minutes']
```

Result: 25 empty subtotals before, none after.

Note: one column for two whole lessons before the list of columns arrives, as the plan for that pair requires. `first-look` was added on 24 Nov for the same reason as `value-counts`.

### PD-4. Look things up in pandas

Assumes: PD-3.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `merge` | `orders.merge(restaurants, on='restaurant_id')` sticks each order's restaurant on the end of its row. | Core |
| 2 | `pile-by-merged` | A column that came from the other table can make the piles. | Core |
| 3 | `only-matches-survive` | Rows with no partner drop out of a merge. Cancelled orders have no delivery, so they are gone. | Core |
| 4 | `names-back-as-column` | `.reset_index()` turns the pile names back into an ordinary column, for when the next step needs them as one. | Core |
| 5 | `several-summaries` | `.agg(['mean', 'count'])` says several things about each pile at once. | Shape |

Closes with: is a delivery more often late when it rains? (pass-bar task 14)

```python
orders = pd.read_csv('orders.csv')
deliveries = pd.read_csv('deliveries.csv')
joined = orders.merge(deliveries, on='order_id')
joined['late'] = joined['actual_minutes'] > joined['promised_minutes']
joined.groupby('rain')['late'].mean()
```

Result: 0.375 without rain and 0.638 with it.

Note: the lesson first merges restaurants and asks for the average subtotal per city, which echoes SQL-4. It then meets the new `deliveries` table. The closing sentence changed on 24 Nov from "late share per city", where all four cities sat between 0.417 and 0.438 and there was nothing to see. With rain there is a finding, which is what "answer a business question" means.

## Pass 2: the interview layer

### PD-5. Windows in pandas

Assumes: SQL-6, SQL-7, PD-4. Opens with: a cold check from PY-10.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `transform-beside` | `.transform('mean')` writes each pile's summary beside the rows of that pile. It is `OVER (PARTITION BY ...)`. | Core |
| 2 | `top-n-in-pandas` | Sort, make piles, take the first three of each. | Core |
| 3 | `latest-in-pandas` | Sort by time, make piles, take the last one of each. | Core |
| 4 | `text-to-date` | `pd.to_datetime(...)` turns text into dates, and `.dt` reaches the month. | Shape |
| 5 | `shift` | `.shift()` is the previous row's value. It is `LAG`. | Shape |

Closes with: each customer's latest order.

```python
orders = pd.read_csv('orders.csv')
orders.sort_values('created_at').groupby('customer_id').tail(1)
```

Result: 1,475 rows, the same orders SQL-7 found.

Note: almost all vocabulary on SQL thoughts. In thinking order the pandas form is shorter than the SQL.

### ML-1. Fit, predict, evaluate

Assumes: PD-5.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `features-and-target` | `X` is a table of the columns to learn from. `y` is the one column to predict. | Core |
| 2 | `hold-rows-back` | `train_test_split` holds some rows back, so the score is honest. | Core |
| 3 | `make-fit-predict` | Make a model, fit it on the training rows, predict the held-back rows. Three lines, always the same. | Core |
| 4 | `score` | A metric compares the predictions with the truth. | Core |
| 5 | `probabilities` | `predict_proba(...)[:, 1]` gives a probability for each row, which is what AUC needs. | Core |
| 6 | `ml-imports` | The import lines. Everyone looks these up. | Shape |

Closes with: predict late deliveries and report a metric (pass-bar task 15).

```python
orders = pd.read_csv('orders.csv')
deliveries = pd.read_csv('deliveries.csv')
data = orders.merge(deliveries, on='order_id').dropna(subset=['distance_km'])
X = data[['distance_km', 'rain', 'bag_size']]
y = data['actual_minutes'] > data['promised_minutes']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
model = LogisticRegression()
model.fit(X_train, y_train)
print(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]))
```

Result: an AUC of 0.697 on 5,489 deliveries.

Note: the learner knows the statistics. Only the three verbs and their order are new, and they are "name a thing, then do something with it" once more.

### ML-2. The same shape, any model

Assumes: ML-1.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `engineer-then-fit` | A better column beats a better model. Add the promised time and the score moves. | Core |
| 2 | `swap-the-model` | Change the first line and nothing else. Every model has the same three verbs. | Core |
| 3 | `fit-on-train-only` | Anything learned from the data, even a median to fill with, is learned from the training rows only. | Core |
| 4 | `pick-the-metric` | When one answer is rare, accuracy flatters. Say which metric you chose and why. | Core |
| 5 | `read-and-criticise` | Reading someone else's pandas and finding what leaks. | Core |

Closes with: from the raw tables to a metric, in one script that reads its own files, with missing distances filled from the training rows, and a gradient boosting model in place of the plain one. The `GradientBoostingClassifier` import line is shape grade.

What the data shows, each a line the teacher can use:

- Adding `promised_minutes` lifts the AUC from 0.697 to 0.805. A long distance matters less when the promise was long.
- Gradient boosting on the same columns scores 0.795, just below the plain model's 0.805. A fancier model is not a better one.
- For "more than 15 minutes late", which is 7.3 percent of deliveries, the model's accuracy is 0.938. Answering "no" every time scores 0.926.

Note: a classmate fills the missing distances with the median of the whole table before splitting. The learner is asked what the model has now seen. This is Nubank's code review round in small.

### ML-3. K-fold by hand (capstone)

Assumes: ML-2, and nearly everything before it.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `bring-numpy-in` | `import numpy as np`, for a row of numbers the length of the table. | Shape |
| 2 | `fold-number-per-row` | `np.arange(len(X)) % k` gives every row a fold number from 0 to k minus 1. | Core |
| 3 | `row-by-row-not` | `~` turns a yes-or-no column round. It belongs with `&` and `\|`. | Core |
| 4 | `this-fold-and-the-rest` | The test rows are this fold. The training rows are all the others. | Core |
| 5 | `average-the-scores` | One score per fold, kept in a list, averaged at the end. A running result. | Core |
| 6 | `metric-by-hand` | AUC and KS can be written by hand. You know what they are. | Name only |

Closes with: cross-validation, written without the library (pass-bar task 16).

```python
def cross_validate(model, X, y, k):
    fold = np.arange(len(X)) % k
    scores = []
    for i in range(k):
        test = fold == i
        model.fit(X[~test], y[~test])
        scores.append(roc_auc_score(y[test], model.predict_proba(X[test])[:, 1]))
    return sum(scores) / len(scores)
```

Result: with five folds on the four columns, after the script has read and merged its two files, it returns 0.803. The five folds score between 0.789 and 0.827, so the learner sees why one split is not enough.

Note: the capstone of the course. It has four new thoughts and uses a function, a loop, a running result, a yes-or-no column, the brackets that keep yes rows, and fit and predict. If the learner can write this, the course has done its job.

## The cold sittings use real data

Decided on 24 Nov 2026, after the owner allowed real public data and said a non-commercial licence is fine.

The lessons stay on the practice tables: every sentence in them was checked against those. The two cold sittings move to the **Olist Brazilian e-commerce dataset**: about 100,000 real orders from 2016 to 2018, with customers, sellers, items, payments, reviews, and both the promised and the actual delivery date.

- **Why.** A cold sitting asks whether the learner can think a sentence out, or only reproduce one. A table they have never seen, with real column names and real mess, is the honest test, and it is what a round hands you.
- **Why this one.** It is the same world as the lessons: orders, delivery, lateness, Brazilian cities. The sentences transfer and only the names change.
- **What it costs.** No new thoughts and no new lessons. `first-look` and `value-counts` were added to PD-3 and PD-2 so that the learner has the two words for meeting a new table.
- **Licence.** CC BY-NC-SA 4.0. This repository is public, so the files stay out of git, in a folder that is ignored. The sittings name their source.

Downloaded on 24 Nov 2026 into `data/real/olist/`, which git ignores. What a first look found, all of it useful for cold prompts:

- Nine tables. Orders has 99,441 rows and eight statuses, of which `delivered` is 96,478.
- 8.1 percent of delivered orders arrived after the estimated date. Late is rare here, so the metric question from ML-2 is real.
- 775 orders have no row in the items table. That is "rows with no match", found in the wild.
- A customer who orders twice gets two `customer_id` values and one `customer_unique_id`. Counting customers needs "how many different".
- Dates arrive as text. Two column names carry a real typo (`product_name_lenght`). Category names are in Portuguese, with a translation table to look them up in.

## Checks done on this map

- **Every closing sentence runs** against `data/` and gives the result quoted. They were run in a scratch folder with pandas and scikit-learn loaded for that run only. Nothing was installed into the project.
- **The echoes hold.** PD-1 gives 60.43 as SQL-1 did. PD-2 gives the same five restaurants as SQL-2. PD-5 gives the same 1,475 orders as SQL-7, and `transform` finds the same 2,588 orders as SQL-6.
- **Prerequisites.** Each lesson assumes only thoughts from earlier lessons. PD-5 needs SQL-6 and SQL-7, which is why it sits in pass 2.
- **Size.** PD-1 has nine thoughts. PD-2 and PD-3 have eight. The rest have five or six.
- **Pass bar.** Tasks 13, 14, 15 and 16 are core: PD-3, PD-4, ML-1 and ML-3. Task 17 is name only, in ML-3.

## Settled on 24 Nov 2026

- **Real data for the cold sittings.** The owner said yes to the Olist download. See the section above.
- **Data for the ML lessons.** The owner allowed synthetic data. `data/deliveries.csv` now gives lateness something to be predicted by: distance, rain, and how many orders the courier carried. See `data/README.md` for how it was made.

## Answered by the owner on 24 Nov 2026

1. **Reading the file.** Make the learner read it every time. Applied above and in every closing script.
2. **The second model in ML-2.** Gradient boosting. Applied above.

## As written, 24 Nov 2026

All eight lessons are in `content/pd/` and `content/ml/`. Changes from this map, each said by the writer in the lesson's notes:

- **PD-1** shows `head()` on restaurants and couriers, because the 11-column orders table gets cut with `...`.
- **PD-2** and **PD-4** opened with an SQL cold check until 25 Nov 2026; they now open with a pandas one from PD-1 and PD-3. PD-2 shows `groupby` through `len(...groupby(...))`, because printing the group object shows a memory address that changes every run. Its closing step accepts the `value_counts` route, whose output ends with `Name: count`. Restaurants 3 and 59, tied at 109, come out in the order 3, 59 in pandas and 59, 3 in SQL.
- **PD-3** gives `dropna` as a second give under `fill-or-drop`. `info()` is shown without `print`, and the lesson says why.
- **PD-4** shows `reset_index` as making the pile names askable, not as something merge needs, because pandas can merge on index names.
- **PD-5** has the latest-order-per-customer sentence as a mid-lesson ask, and closes on latest plus `transform`.
- **ML-2** keeps two worlds apart. On the `dropna` rows, as in ML-1, adding the promised time lifts the plain model from 0.697 to 0.792, and boosting scores 0.787. The figures in this map (0.805, 0.795, 0.938 and 0.926) hold on all 5,601 rows with a fill learned from the training rows only, which is where the lesson goes after `fit-on-train-only`. Typed steps fill with the mean and print it (4.4174 against 4.439), because a median fill leaks invisibly (4.3 either way).
- **ML-3** uses no `check`: the learner's script prints. `np.arange` and `% k` are split across two gives.
- **ML-1** and **ML-2** each have one ask more than the map, as extra returns on existing thoughts.
