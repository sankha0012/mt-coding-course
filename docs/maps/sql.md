# SQL strand map

Status: approved by the owner on 24 Nov 2026, with the answers recorded at the end. A map says which thoughts each lesson introduces, in order, and the sentence the lesson builds to. It is not a script. Each lesson is written as YAML after this map is approved, and is then reviewed by sitting it (decision C13).

Nine lessons. SQL-1 exists. SQL-2 to SQL-4 finish the foundation in pass 1. SQL-5 to SQL-9 are the interview layer in pass 2, after the Python and pandas foundations.

## How to read a lesson

- **Thoughts** are listed in teaching order. Each has an identifier for the audit.
- **Grade** follows decision C10. *Core* is typed from memory and comes back spaced. *Shape* means the teacher's line supplies the spelling every time. *Name only* is one aside and is never asked.
- **Closes with** is the surprise sentence. Its model answer was run against `data/` and the result is quoted.
- **Opens with** is the cold check that starts the sitting.

## Pass 1: foundation

### SQL-1. From "how many?" to piles (written, `content/sql/lesson-01.yaml`)

Thoughts: `count-rows`, `from-table`, `star`, `table-out`, `keep-rows`, `compare-signs`, `text-quotes`, `summary-column`, `piles`, `one-row-per-pile`, `pile-name`, `commas`, `summary-per-pile`, `keep-before-piles`.

Closes with: the average subtotal of each restaurant, delivered orders only.

Owed to later lessons: `star` has not returned since step 10. `summary-per-pile` and `keep-before-piles` have had one return each. SQL-2 pays these early.

### SQL-2. Sort and cut (written, `content/sql/lesson-02.yaml`)

Assumes: SQL-1. Opens with: a cold check from SQL-1.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `choose-columns` | Name the columns you want, with commas, where the star was. | Core |
| 2 | `more-summaries` | Total, biggest and smallest (`SUM`, `MAX`, `MIN`) sit where `AVG` sits. | Core |
| 3 | `two-questions` | Two questions about a row are joined with `AND` or `OR`. | Core |
| 4 | `sort` | `ORDER BY` sorts the table that comes out. It is written after the piles, because sorting happens after them. | Core |
| 5 | `sort-direction` | `DESC` puts the biggest first. With nothing said, the smallest comes first. | Core |
| 6 | `cut` | `LIMIT` keeps the first rows of what is left. It comes last, because it happens last. | Core |
| 7 | `sort-by-summary` | After piles, the sort can use a summary: `ORDER BY COUNT(*) DESC`. Added when the lesson was written: the closing sentence needs it. | Core |
| 8 | `name-a-result` | `AS` gives a column that comes out a name of your own, and the sort can use that name. | Core |

Closes with: the five restaurants with the most delivered orders.

```sql
SELECT restaurant_id, COUNT(*) FROM orders WHERE status = 'delivered'
GROUP BY restaurant_id ORDER BY COUNT(*) DESC LIMIT 5
```

Result: restaurant 2 with 113, then 24 with 112, then 59 and 3 with 109, then 22 with 108.

Note: `sort` and `cut` extend "after the table, the sentence runs in the order things happen" from SQL-1. No new rule is needed.

As written: 25 steps, 15 typed, 13 returns, 8 new thoughts. It opens with a cold check from SQL-1 and closes with one on sorted, cut piles. `star` and `summary-per-pile`, which SQL-1 left owed, both return. Two limits found while writing:

- **`AS` cannot be checked by result.** Column names are ignored in comparison, so a learner who forgets to name the count still gets the right rows. The step says so, and the narration names `AS` either way.
- **Ties.** A step that is judged by row order uses a column with no ties, or compares a set. The one tie left, two restaurants sharing a signup date, is noted in step 13.

### SQL-3. Keep piles, and empty cells

Assumes: SQL-2. Opens with: a cold check from SQL-2.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `text-is-exact` | Inside quotes it is your data, and data is matched letter for letter, capitals included. | Core |
| 2 | `empty-cells` | A cell can be empty. Nothing equals an empty cell, so the question is written `IS NULL`. | Core |
| 3 | `summaries-skip-empties` | An average skips empty cells. A count of rows does not. | Core |
| 4 | `how-many-different` | `COUNT(DISTINCT customer_id)` counts each customer once. | Core |
| 5 | `keep-piles` | `HAVING` is the keep-rows question, asked of piles. It is written after the piles are made. | Core |
| 6 | `rows-or-piles` | A question about a row goes in `WHERE`. A question about a pile goes in `HAVING`. | Core |

Closes with: restaurants with more than 100 delivered orders, with their count and average subtotal (pass-bar task 1).

```sql
SELECT restaurant_id, COUNT(*), AVG(subtotal) FROM orders WHERE status = 'delivered'
GROUP BY restaurant_id HAVING COUNT(*) > 100
```

Result: 16 restaurants.

Notes: `empty-cells` pays the debt from SQL-1 step 3 ("a few cells are empty, leave them for another day"). `keep-piles` arrives two lessons after piles, as the plan for that confusable pair requires. A classmate writes `WHERE COUNT(*) > 100` just before the learner could.

### SQL-4. Look things up in another table

Assumes: SQL-3. Opens with: a cold check from SQL-3.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `join` | `JOIN` sticks each order's restaurant on the end of its row. | Core |
| 2 | `join-on` | `ON` says which column in one table matches which column in the other. | Core |
| 3 | `whose-column` | When both tables have a column of that name, say whose it is: `orders.restaurant_id`. | Core |
| 4 | `short-names` | A table can be given a short name, and columns are then called by it: `o.subtotal`. | Core |
| 5 | `pile-by-looked-up` | Once it is on the row, a column from the other table can make the piles. | Core |

Closes with: the average subtotal per city, delivered orders only (pass-bar task 2).

```sql
SELECT r.city, AVG(o.subtotal) FROM orders o JOIN restaurants r ON o.restaurant_id = r.restaurant_id
WHERE o.status = 'delivered' GROUP BY r.city
```

Result: four cities, each close to 60.

Note: the lesson opens on the need. The learner is asked for orders per city and finds the orders table has no city.

## Pass 2: the interview layer

These follow the Python and pandas foundations, so they may import Python thoughts by name.

### SQL-5. A result can be queried again

Assumes: SQL-4, and `name-a-value` from PY-1. Opens with: a cold check from the pandas foundation.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `in-a-list` | `IN ('pizza', 'japonesa')` asks whether a cell is one of several. | Core |
| 2 | `query-a-result` | A table came out, so it can go in: a query in brackets can stand after `FROM`. | Core |
| 3 | `name-a-table` | `WITH counts AS (...)` names a result, and the sentence below uses it. Name a thing, then do something with it. | Core |
| 4 | `one-number-from-a-query` | A query that answers one number can stand where a number stands. | Core |
| 5 | `list-from-a-query` | A query that answers one column can stand where the list after `IN` stands. | Core |

Closes with: the restaurants with more orders than the average restaurant.

```sql
WITH counts AS (SELECT restaurant_id, COUNT(*) AS n FROM orders GROUP BY restaurant_id)
SELECT restaurant_id, n FROM counts WHERE n > (SELECT AVG(n) FROM counts)
```

Result: 29 restaurants.

Note: this is "a table goes in, a table comes out" used twice. It should cost little.

### SQL-6. A number beside each row

Assumes: SQL-5.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `beside-each-row` | `AVG(subtotal) OVER ()` writes the summary beside every row. The rows do not collapse. | Core |
| 2 | `piles-that-stay` | `OVER (PARTITION BY restaurant_id)` writes each pile's summary beside the rows of that pile. | Core |
| 3 | `row-against-pile` | A row can now be compared with its own pile. | Core |
| 4 | `beside-comes-late` | The number beside the row is written after the keeping is done. To keep by it, name the result and query it again. | Core |

Closes with: the orders that came to more than their own restaurant's average.

```sql
WITH o AS (SELECT order_id, restaurant_id, subtotal,
                  AVG(subtotal) OVER (PARTITION BY restaurant_id) AS rest_avg FROM orders)
SELECT order_id, restaurant_id, subtotal, rest_avg FROM o WHERE subtotal > rest_avg
```

Result: 2,588 orders.

Note: the one truly new thought of the strand. `beside-comes-late` is the order-of-events idea again, so it is a discovery and not a rule. This moved here from SQL-7, where the approved plan had it, because this lesson's closing sentence needs it.

### SQL-7. Order inside the pile

Assumes: SQL-6.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `number-the-rows` | `ROW_NUMBER() OVER (ORDER BY subtotal DESC)` numbers the rows in an order you choose. | Core |
| 2 | `number-inside-pile` | With `PARTITION BY`, the numbering starts again in each pile. | Core |
| 3 | `top-n-per-pile` | Keep the rows numbered up to N. | Core |
| 4 | `latest-is-number-one` | Number from the newest, and keep number 1. | Core |
| 5 | `ties` | `RANK` gives tied rows the same number. | Name only |

Closes with two sentences: the three biggest orders of each restaurant (task 4), and each customer's latest order (task 5).

```sql
WITH ranked AS (SELECT order_id, restaurant_id, subtotal,
                       ROW_NUMBER() OVER (PARTITION BY restaurant_id ORDER BY subtotal DESC) AS rn FROM orders)
SELECT restaurant_id, order_id, subtotal FROM ranked WHERE rn <= 3
```

```sql
WITH ranked AS (SELECT customer_id, order_id, created_at,
                       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS rn FROM orders)
SELECT customer_id, order_id, created_at FROM ranked WHERE rn = 1
```

Results: 180 rows, and 1,475 rows. No restaurant has a tie between its third and fourth order, and no customer has two orders at the same moment, so both answers are stable.

### SQL-8. Rows with no match

Assumes: SQL-7, and `empty-cells` from SQL-3.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `keep-all-of-first` | `LEFT JOIN` keeps every row of the first table, matched or not. | Core |
| 2 | `empty-side` | Where there was no match, the other table's columns are empty. | Core |
| 3 | `keep-the-empties` | So "no match" is a question you already know: `IS NULL`. | Core |
| 4 | `count-matches` | `COUNT(o.order_id)` counts matches, because summaries skip empties. A row with no match counts zero. | Core |

Closes with: the coupons nobody has used (pass-bar task 3).

```sql
SELECT c.coupon_code FROM coupons c LEFT JOIN orders o ON c.coupon_code = o.coupon_code
WHERE o.order_id IS NULL
```

Result: one coupon, `VOLTA15`.

A second sentence for the same thought, on another table: the orders that never had a delivery.

```sql
SELECT COUNT(*) FROM orders o LEFT JOIN deliveries d ON o.order_id = d.order_id WHERE d.order_id IS NULL
```

Result: 399, which is the number of cancelled orders that SQL-1 found in step 8.

Note: every restaurant and every courier has orders, so the three original tables had nothing unmatched. The owner allowed synthetic data on 24 Nov 2026, and `data/coupons.csv` and `data/deliveries.csv` were added. Both sentences were run against them.

### SQL-9. Dates and buckets

Assumes: SQL-8.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `date-to-month` | Cut a date down to its month. Here it is spelled `strftime('%Y-%m', created_at)`, and every database spells it differently. | Shape |
| 2 | `pile-by-computed` | You can pile by something you worked out, once it has a name. | Core |
| 3 | `previous-row` | `LAG(total) OVER (ORDER BY month)` writes the previous row's value beside this row. | Core |
| 4 | `column-arithmetic` | Columns can be added and subtracted, cell by cell. | Core |
| 5 | `buckets` | `CASE WHEN ... THEN ... ELSE ... END` writes a label on each row. | Core |
| 6 | `conditional-count` | `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` counts only some of the rows in each pile. | Core |
| 7 | `running-total` | `SUM(total) OVER (ORDER BY month)` adds up as it goes. | Shape |

Closes with: month totals, with the change from the month before (pass-bar task 6).

```sql
WITH monthly AS (SELECT strftime('%Y-%m', created_at) AS month, SUM(subtotal) AS total FROM orders GROUP BY month)
SELECT month, total, total - LAG(total) OVER (ORDER BY month) AS change FROM monthly
```

Result: three months, August to October 2026. The change is empty for August, minus 6,750.00 for September and plus 1,846.34 for October.

## Checks done on this map

- **Every closing sentence runs** against `data/`, loaded with empty cells as missing.
- **Prerequisites.** Each lesson assumes only thoughts from earlier lessons. The two cross-strand imports are marked: SQL-5 leans on naming from PY-1.
- **Size.** No lesson has more than seven new thoughts. SQL-1 has twelve and remains the largest.
- **Pass bar.** Tasks 1 to 6 are all core: SQL-3, SQL-4, SQL-8, SQL-7, SQL-7 and SQL-9.

## Answered on 24 Nov 2026

1. **The threshold in SQL-3.** The owner left this to me and I chose 100 delivered orders, which leaves 16 restaurants. The reason is that a closing answer of two rows (at 110) shows too little of what `HAVING` does, and 16 rows shows that it keeps some piles and drops others.
2. **`short-names` in SQL-4.** Taught, as a core thought. Interview answers nearly always write `o` and `r`.

## As written, 24 Nov 2026

All nine lessons are in `content/sql/`. Changes from this map, each said by the writer in the lesson's notes:

- **SQL-3** keeps the threshold of 100 and its 16 restaurants. Davi's `'Pizza'` introduces `text-is-exact`, and Ana's `WHERE COUNT(*)` introduces `rows-or-piles`, with SQLite's own message.
- **SQL-4** opens on the need (orders per city) as a give, since the question cannot be answered yet. A 360,000-row cross join shows why `ON` is needed. An aside plants the dropped rows that SQL-8 uses: orders joined to couriers gives 5,601 rows, not 6,000.
- **SQL-5** lists `name-a-value` under `requires`, not `imports`, because an id may be introduced once. The teacher still says aloud that it is the Python idea.
- **SQL-6** compares with `>` in the `SELECT`, giving 1 or 0, so that `row-against-pile` needs no subtraction. Subtraction belongs to SQL-9.
- **SQL-8** gives `keep-the-empties` first on orders with no courier (399), before the coupons.
- **SQL-7** gives the name-only `ties` a `new` on its aside, because otherwise the checker reports it as never introduced.
- Wrong answers that gave the model result were dropped where SQLite's scan order made a "no ORDER BY" slip give identical rows.
