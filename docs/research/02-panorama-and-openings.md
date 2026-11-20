# Panorama and two alternative openings

Date: 2026-11-19. This follows the research notes in `01-method-research.md`. It is a working draft for discussion, not a script to build from yet.

The course has three strands: SQL first, then basic Python, then pandas (see Part 3 for why in that order). The data is the delivery set from the mocks: `orders` (6,000 rows), `restaurants` (60) and `couriers` (200). Every line of code in a fenced block below was run against that data.

## Part 1. The panorama

A panorama is the writer's reference sheet, not the teaching order. It lists every separate thought the learner must have, so that the script can introduce them one at a time.

### 1.1 The one overarching idea

**A table goes in, a table comes out.** Every SQL query and every pandas step takes a table and hands back a table, even when the table that comes back has one row and one column. Everything else is a movement applied to a table.

### 1.2 The movements

There are eight. For each one I give the two dialects, then the separate thoughts hiding inside it.

**1. Name the table**

```sql
SELECT * FROM orders
```
```python
orders
```

- Thought: which table.
- Just is: the spelling `SELECT`, `FROM`, and `*` for "everything".

**2. Choose columns**

```sql
SELECT status, subtotal FROM orders
```
```python
orders[['status', 'subtotal']]
```

- Thought: one column.
- Thought: several, separated by commas.
- pandas only: a column name is a piece of text, so it wears quotes. The real reason is that in Python a bare word is the name of a variable.
- pandas only: one name gives a column, a list of names gives a table. This is where the double brackets come from, and it is a debris risk if taught as "remember two brackets".

**3. Keep rows**

```sql
SELECT * FROM orders WHERE status = 'delivered'
```
```python
orders[orders['status'] == 'delivered']
```

- Thought: a question is asked of every row and each row answers yes or no.
- Thought: the comparison itself (`>`, `<`, `=`).
- Thought: text wears quotes and numbers do not.
- Thought: only the yes rows come out.
- pandas only: the question is written out in full first, and the brackets then take the yes and no answers.
- pandas only: `==` asks, `=` names. Real reason: `=` was already taken for naming things.
- Later thoughts, each its own step: two questions joined with AND or OR (pandas needs `&`, `|` and a bracket round each question), and missing values (`IS NULL`, `.isna()`).

**4. Summarise to one number**

```sql
SELECT AVG(subtotal) FROM orders
```
```python
orders['subtotal'].mean()
```

- Thought: many rows become one.
- Thought: which summary (how many, average, total, biggest, smallest).
- Thought: which column it is about. Counting rows needs no column.
- Position: in SQL the summary wraps the column, in pandas it follows it.
- Vocabulary differs and just is: `AVG` and `mean`, `COUNT(*)` and `len(orders)`.

**5. Make piles**

```sql
SELECT status, AVG(subtotal) FROM orders GROUP BY status
```
```python
orders.groupby('status')['subtotal'].mean()
```

- Thought: sort the rows into piles by a column.
- Thought: one row comes out per pile.
- Thought: say what you want to know about each pile, which is movement 4 again.
- Thought: the pile's name has to come out too, or the numbers are unlabelled.
- pandas: the pile names appear on the left on their own. `reset_index` is only needed when a later step wants them as a normal column, so it is postponed until then.

**6. Keep piles**

```sql
SELECT restaurant_id, COUNT(*) FROM orders GROUP BY restaurant_id HAVING COUNT(*) > 110
```
```python
counts = orders.groupby('restaurant_id').size()
counts[counts > 110]
```

- Thought: this is movement 3 again, asked of piles and not of rows.
- SQL needs a second word for it, `HAVING`. pandas does not, because the piles are already a table and "keep rows" simply applies again.

**7. Sort and take the top**

```sql
SELECT * FROM orders ORDER BY subtotal DESC LIMIT 5
```
```python
orders.sort_values('subtotal', ascending=False).head(5)
```

- Thought: sort by which column.
- Thought: which direction.
- Thought: how many to keep.

**8. Look things up in another table**

```sql
SELECT * FROM orders JOIN restaurants ON orders.restaurant_id = restaurants.restaurant_id
```
```python
orders.merge(restaurants, on='restaurant_id')
```

- Thought: every order row gets its restaurant's columns stuck on the end.
- Thought: which column says which restaurant.
- Thought: when both tables have a column of the same name, say whose it is.
- Later thought: what happens to rows with no match.

Two more movements exist and are left out of the first course: making a new column from others, and anything with dates.

### 1.3 Looking across the panorama

These are the "horizontal" observations, which is where the method says the teachable sense lives.

1. **"Keep rows" appears three times.** `WHERE`, `HAVING` and the pandas brackets are one thought. Taught that way, `HAVING` is not a new idea, and its absence in pandas becomes obvious instead of puzzling.
2. **pandas is SQL in thinking order.** SQL is written answer-first (`SELECT` at the front) but thought table-first: from the table, keep rows, make piles, summarise, keep piles, sort, cut. pandas is written in exactly that thinking order, left to right. If the SQL prompts are phrased in thinking order from the start ("from orders, keeping the delivered ones, how many?"), pandas later costs almost nothing.
3. **Summaries are the same words in a different position.** Wrap in SQL, follow in pandas.
4. **Quotes mean text in both dialects.** pandas just has more text, because column names count.
5. **Piles are the centre of gravity.** Most interview questions contain "per" or "by". Movements 3 and 4 are the background that piles need.

### 1.4 Decisions that remove things to remember

- pandas always uses brackets and quotes for a column. The dot form (`orders.status`) is never shown, so there is one way to say it.
- Single quotes everywhere, in both dialects.
- The checker accepts any letter case, spacing and quote style.
- No `reset_index`, no `as_index`, no `.agg` with dictionaries in the first course.

### 1.5 What the opening must weave around

- **Joins.** `orders` has no city. City lives in `restaurants`. So early prompts about orders use status, subtotal, delivery fee and restaurant id, and "per city" questions are asked of the `restaurants` table until joins arrive.
- **Missing values.** `coupon_code` is empty on most rows and `courier_id` is empty on cancelled orders. Both stay out of early prompts.
- **Two conditions at once**, because of the pandas brackets.
- **Dates.**

### 1.6 Pairs to keep apart, then contrast

| Pair | Plan |
|---|---|
| `=` in SQL and `==` in pandas | SQL `=` is long settled before pandas begins. Contrast on the first pandas filter. |
| `WHERE` and `HAVING` | `HAVING` arrives well after piles are comfortable, as "the same question, asked of piles". |
| `COUNT(*)` and `COUNT(column)` | Only `COUNT(*)` in the first course. |
| One column and a list of columns in pandas | One column for a long stretch. The list comes with its real reason. |

## Part 2. Two openings

Both cover roughly the first ten minutes. Both follow the same rules from the research: no instructions screen, sentences straight away, one new thought per step, prompts whose wording keeps changing, feedback that narrates what the learner did, and a classmate who makes the instructive mistakes. The classmates are Ana and Davi.

Notation: **T** is the teacher's line on screen. The fenced block is the answer the learner is expected to type. *Italics are commentary for us and never appear in the app.*

### Opening A: look at the table, then narrow it

The handle is `SELECT ... FROM orders`. The learner starts by looking at data and narrows it step by step.

**A1.** **T:** We'll start straight away. You already speak some SQL, because it was designed to read like English. There is a table called orders, with one row for every food delivery order. To look at all of it, we say:

```sql
SELECT * FROM orders
```

**T:** Select everything, from orders. The star is just how SQL writes "everything".

*Given, not asked. The star is labelled as something that just is, which cues early that not everything gets a reason.*

**A2.** **T:** One of the columns is called subtotal. To see only that column, its name goes where the star was. So how would you say: show me the subtotal, from orders? Stop and think it out before you type. Nothing here is timed. Then compare with Ana.

```sql
SELECT subtotal FROM orders
```

*First solicited sentence, and the first rule of engagement, given at the moment it matters.*

**A3.** **T:** Good, you put the column's name in the star's place. Another column is called status. Give me the status of every order.

```sql
SELECT status FROM orders
```

*Masked repetition: the noun changes and the wording changes from "show me" to "give me".*

**A4.** **T:** If you want two columns, you list them the way you would in English, with a comma. The status and the subtotal?

```sql
SELECT status, subtotal FROM orders
```

**A5.** **T:** So far a table went in and the whole table came out. To keep only some rows, we add a question that each row has to answer yes to. For the big orders: `WHERE subtotal > 100`. Try the whole thing: everything from orders, but only where the subtotal is above 100.

```sql
SELECT * FROM orders WHERE subtotal > 100
```

*New thought: a question asked of each row. The overarching idea is named here for the first time.*

**A6.** **T:** Nice. The question went at the end, after the table. Now just the status, for the orders whose delivery fee was under 5.

```sql
SELECT status FROM orders WHERE delivery_fee < 5
```

*Recombination. Two things change at once (the column and the question), which stops the learner from editing one slot of the previous answer.*

**A7.** **T:** The status column holds a word: delivered or cancelled. When we look for a word, the word wears quotes, so SQL knows it is text and not the name of a column. Everything from the delivered orders?

```sql
SELECT * FROM orders WHERE status = 'delivered'
```

**T:** Davi wrote `WHERE status = delivered`. Davi, is delivered a column in our table, or a word we are looking for? ... A word, so it wears quotes.

*New thought: text wears quotes. The classmate makes the predictable error and gets a leading question, not a red mark.*

**A8.** **T:** The subtotal and the delivery fee of the cancelled orders.

```sql
SELECT subtotal, delivery_fee FROM orders WHERE status = 'cancelled'
```

*Artificial friction. Nothing is new, but nothing is broken down either. This tells the learner the course cannot be done on autopilot.*

**A9.** **T:** Often we don't want to look at rows at all. We want one number about them. To ask how many rows there are, we select a count:

```sql
SELECT COUNT(*) FROM orders
```

**T:** Many rows went in and one row came out.

*New thought: many rows become one. Given, not asked. "One number about them" is pre-inserted for piles.*

**A10.** **T:** How many orders were cancelled?

```sql
SELECT COUNT(*) FROM orders WHERE status = 'cancelled'
```

**T:** That is a real question with a real answer, 399, and you wrote it from nothing.

*The surprise sentence. Not rehearsed in parts. If the learner freezes, the app splits it: first "how many orders", then "only the cancelled ones".*

**A11.** **T:** Count the orders that came to more than 100.

```sql
SELECT COUNT(*) FROM orders WHERE subtotal > 100
```

**A12.** **T:** For an average, the word is AVG, and it needs to know which column, so the column goes inside its brackets: `AVG(subtotal)`. What was the average subtotal of the delivered orders?

```sql
SELECT AVG(subtotal) FROM orders WHERE status = 'delivered'
```

*Ends the opening. Covered: movements 1 to 4. Piles have not started.*

### Opening B: answer a question from the first sentence

The handle is `SELECT COUNT(*) FROM ...`. Every sentence the learner writes answers a question, and the prompts are phrased in thinking order.

**B1.** **T:** Nearly everything you get asked about data is a question about a table: how many, how much on average, which ones. We'll answer those from the first minute. There is a table called orders, with one row for every food delivery order. To ask how many rows it has, we say:

```sql
SELECT COUNT(*) FROM orders
```

**T:** Give me the count, from orders. It answers 6,000.

*Given. The first thing the learner sees is an answer to a question, and "one number comes out" is there from the start.*

**B2.** **T:** There is another table called restaurants. How many restaurants are there? Stop and think it out before you type. Nothing here is timed. Then compare with Ana.

```sql
SELECT COUNT(*) FROM restaurants
```

*First solicited sentence. Only the table changes, which fixes where the table goes.*

**B3.** **T:** Good. The table's name went after FROM. A table goes in and a table comes out, even if what comes out is a single number. Now, to count only some of the rows, we add a question that each row has to answer yes to. From orders, keeping the ones where the subtotal is above 100, how many? The keeping part is written `WHERE subtotal > 100` and goes at the end.

```sql
SELECT COUNT(*) FROM orders WHERE subtotal > 100
```

*New thought: a question asked of each row. The prompt is in thinking order: table, keep, then the summary.*

**B4.** **T:** You kept the rows first and counted what was left. How many orders had a delivery fee under 5?

```sql
SELECT COUNT(*) FROM orders WHERE delivery_fee < 5
```

*The wording drops back to ordinary English, so the learner has to find the thinking order alone.*

**B5.** **T:** The status column holds a word: delivered or cancelled. When we look for a word, it wears quotes, so SQL knows it is text and not a column's name. How many orders were cancelled?

```sql
SELECT COUNT(*) FROM orders WHERE status = 'cancelled'
```

**T:** Davi wrote `WHERE status = cancelled`. Davi, is cancelled a column in our table, or a word we are looking for? ... A word, so it wears quotes.

**B6.** **T:** Counting is one thing we can say about a set of rows. An average is another. The word is AVG, and it needs to know which column, so the column goes inside its brackets. From orders, the average subtotal?

```sql
SELECT AVG(subtotal) FROM orders
```

*New thought: a summary about a column.*

**B7.** **T:** What was the typical delivery fee on the big orders, the ones above 100?

```sql
SELECT AVG(delivery_fee) FROM orders WHERE subtotal > 100
```

*Artificial friction. "Typical" for average, "big" for above 100, and the column inside AVG differs from the column in the question. Not broken down.*

**B8.** **T:** Now the idea you will use more than any other. Think of sorting the rows into piles. The restaurants table has a city column. If we make one pile per city and count each pile, we get one number per pile:

```sql
SELECT COUNT(*) FROM restaurants GROUP BY city
```

**T:** It answers 15, 6, 14 and 25. Which city is which?

*Given. The answer really is four unlabelled numbers. This is a deliberate tension: the learner feels that something is missing before being handed the fix.*

**B9.** **T:** We can't tell, because we only asked for the count. So we ask for the pile's name as well, in front, with a comma. How would you say: the city, and how many restaurants, for each city?

```sql
SELECT city, COUNT(*) FROM restaurants GROUP BY city
```

*The tension resolves. The rule "select the column you grouped by" is never stated as a rule. It arrives as the answer to a need the learner just felt.*

**B10.** **T:** One pile per city, the name in front, the count beside it. Now the couriers table has a vehicle column. How many couriers per vehicle?

```sql
SELECT vehicle, COUNT(*) FROM couriers GROUP BY vehicle
```

*Both the table and the pile column change. "Per" appears for the first time as the word that signals piles.*

**B11.** **T:** Back to orders. Average subtotal by status.

```sql
SELECT status, AVG(subtotal) FROM orders GROUP BY status
```

*"By" joins "per". The summary changes from count to average.*

**B12.** **T:** For the delivered orders only, the average subtotal of each restaurant. Think about what happens first: keeping rows, or making piles.

```sql
SELECT restaurant_id, AVG(subtotal) FROM orders WHERE status = 'delivered' GROUP BY restaurant_id
```

**T:** That is the shape of a real interview question, and you built it by thinking: from orders, keep the delivered ones, pile them by restaurant, average each pile.

*The surprise sentence, and the end of the opening. Covered: movements 1, 3, 4 and 5. Choosing columns for their own sake has not been taught at all.*

### How the two compare

| | Opening A | Opening B |
|---|---|---|
| First sentence the learner writes | Shows a column | Answers "how many?" |
| First real business answer | Step 10 | Step 2 |
| Reaches piles in ten minutes | No | Yes |
| Load | Gentle and even | Climbs faster, with one steep step at B8 to B9 |
| Why `SELECT` lists columns | Explained at once | Left as "give me" until B9, where it is discovered |
| Prepares pandas | Neutral | Prompts already run in pandas order |
| Risk | Feels like a tutorial, and the payoff is late | B12 may be one step too far for a first sitting |

**My recommendation is B.** The research says to open with the most widely applicable idea and get to real sentences fast, and piles are the idea that interview questions turn on. B also makes the awkward `GROUP BY` rule something you discover. I would borrow one thing from A: a short look at raw rows (`SELECT * FROM orders`) early on, so the table is not abstract.

## Part 3. Basic Python

Added after the person asked that the course also teach basic Python (lists, dicts and so on), so that someone finishing it can quickly write simple scripts.

### 3.1 Where it fits

**Recommended order: SQL, then Python, then pandas.**

- SQL comes first because it is nearly English and it installs the five thoughts (go through a table, keep, pile, summarise, sort) with almost no syntax.
- Python comes second and re-uses those thoughts by hand. A loop is "from". An `if` is "where". A dict of running totals is "group by". Nothing conceptually new arrives, only the hand-cranked form.
- pandas comes last because every piece of pandas syntax is Python syntax: square brackets, quoted names, methods after a dot, `==`. Taught before Python, each of those is a rule to remember. Taught after, each is already familiar.

This reverses one earlier decision. I had planned to contrast SQL `=` with pandas `==`. With Python in the middle, `==` is met where it has its real reason, and pandas inherits it for free.

### 3.2 The overarching idea

**Give a thing a name, then do something with it.** A script is a list of steps read from top to bottom. Each step either names a value or does something with one. A function is the same idea as a query: something goes in, something comes out.

### 3.3 The movements

**P1. Name a value**

```python
fee = 8.99
```

- Thought: `=` gives a name. It does not ask anything.
- Kinds of value: numbers, text in quotes (imported from SQL), and yes or no (`True`, `False`), which is the answer a row gave to a `WHERE` question.

**P2. A list**

```python
fees = [8.99, 6.99, 0]
fees[0]
fees.append(4.99)
```

- Thought: several values in order, inside square brackets, with commas.
- Thought: take one out by its position.
- Just is, with a real reason available later: positions count from 0.
- Thought: add one to the end.

**P3. Summaries you already know**

```python
len(fees)
sum(fees)
max(fees)
sorted(fees, reverse=True)[:2]
```

- Imported from SQL: how many, total, biggest, smallest, sorted, and "the first few".
- No average word in plain Python. The learner builds it from `sum` and `len`.

**P4. Go through each one**

```python
for fee in fees:
    print(fee)
```

- Thought: do the same thing for each item.
- Thought: the item gets a temporary name.
- Thought: the colon opens a block and the indented lines are inside it. This one idea covers `for`, `if` and `def`.

**P5. Ask a question**

```python
for fee in fees:
    if fee > 5:
        print(fee)
```

- Thought: `if` asks a yes or no question, and the lines inside run only on yes.
- `==` asks whether two things are equal, because `=` is already taken for naming.
- Later: `else`, and joining questions with `and`, `or`.

**P6. Keep a running result**

```python
total = 0
for fee in fees:
    total = total + fee
```

- Thought: start the result before the loop.
- Thought: update it inside the loop.
- Thought: it is ready after the loop.
- This is "summarise" by hand. The same shape builds a count, a total, a biggest so far, or a new list.

**P7. A dict**

```python
price = {'pizza': 40, 'sushi': 60}
price['pizza']
price['acai'] = 25
'acai' in price
```

- Thought: look things up by name, not by position.
- Thought: read one, add or change one, ask whether a name is there.
- Curly brackets to make it, square brackets to get from it. Square brackets always mean "get from inside".

**P8. Piles by hand**

```python
dishes = ['pizza', 'coca', 'pizza', 'sushi', 'coca', 'pizza']
counts = {}
for dish in dishes:
    counts[dish] = counts.get(dish, 0) + 1
```

- Thought: the dict holds one entry per pile.
- Thought: for each item, find its pile and update that pile's running result.
- Thought: a pile that does not exist yet starts at 0.
- This is `GROUP BY` with `COUNT(*)`, by hand. It is also the single most common shape in plain-Python interview tasks. Two of the five tasks in the existing mock 3 are this.

**P9. Wrap it as a function**

```python
def average(values):
    return sum(values) / len(values)

average(fees)
```

- Thought: give a name to some steps.
- Thought: what goes in.
- Thought: what comes out, with `return`.

**P10. A table by hand**

```python
rows = [
    {'status': 'delivered', 'subtotal': 81.1},
    {'status': 'cancelled', 'subtotal': 31.3},
    {'status': 'delivered', 'subtotal': 18.85},
]
total = 0
for row in rows:
    if row['status'] == 'delivered':
        total = total + row['subtotal']
```

- Thought: a row is a dict and a table is a list of rows.
- This joins the Python strand back to the SQL strand, and it is the doorway to pandas.

Left for a second course: list comprehensions, tuples and unpacking, sets, `Counter` and `defaultdict`, sorting with a key, string methods, reading files, error handling. Classes are left out altogether.

### 3.4 Looking across

1. **The five SQL thoughts reappear by hand.** Loop, `if`, dict of piles, running result, `sorted`. The plain-Python strand is mostly old thoughts in new clothes.
2. **Square brackets always mean "get from inside".** A position in a list, a name in a dict, a column in pandas, the yes rows in pandas.
3. **Quotes always mean text.**
4. **`=` names and `==` asks.** One explanation serves Python and pandas.
5. **Colon and indent are one idea** for loops, questions and functions.
6. **Something in, something out** describes a query, a pandas step and a function.

### 3.5 Pairs to keep apart, and things to weave around

| Pair | Plan |
|---|---|
| `=` and `==` | `=` for a good while first. `==` arrives with the first `if` on text, with a classmate's mistake. |
| `[]` list and `{}` dict | Lists are fully comfortable before dicts begin. |
| Position and name | Same separation. Contrast when dicts arrive. |
| `print` and `return` | `print` is only "show me" early on. `return` arrives with functions, then the two are contrasted. |

Woven around at the start: `range` and counting loops, positions beyond `[0]` and `[-1]`, `+=`, and anything that needs an import.

### 3.6 A Python opening

This starts after the SQL strand, so the learner already owns quotes, commas, counting, averages and "keep the ones where".

**C1.** **T:** Now the same thoughts in Python, where you do the work by hand. In Python we give things names, using `=`. Here is a list of three delivery fees, and its name is fees:

```python
fees = [8.99, 6.99, 0]
```

**T:** Square brackets hold a list, and commas separate the items, just as they separated columns.

*Given. Commas are imported from SQL. `=` is introduced as naming from its very first appearance.*

**C2.** **T:** Make a list called subtotals holding 81.1, 18.85 and 84.23. Think it out first. Nothing is timed.

```python
subtotals = [81.1, 18.85, 84.23]
```

**C3.** **T:** You already know how to ask how many. In Python the word is len, short for length, and the list goes inside its brackets, the way a column went inside AVG. How many subtotals?

```python
len(subtotals)
```

*Imports the shape of `AVG(subtotal)`. "Short for length" is a real origin, not an invented hook.*

**C4.** **T:** For the total, the word is sum. The total of the fees?

```python
sum(fees)
```

*The list changes as well as the word, so the previous answer cannot simply be edited.*

**C5.** **T:** Python has no AVG for a plain list. But you know what an average is made of. The average subtotal?

```python
sum(subtotals) / len(subtotals)
```

**T:** The total divided by how many. You didn't need a word for it.

*Artificial friction and the first small surprise: the learner builds something that was never given.*

**C6.** **T:** Give that result the name average.

```python
average = sum(subtotals) / len(subtotals)
```

*Masked repetition of C5, with naming applied to a result and not just a typed value.*

**C7.** **T:** A list can hold words too. Words wear quotes here as well. A list called statuses with delivered, cancelled, delivered.

```python
statuses = ['delivered', 'cancelled', 'delivered']
```

**C8.** **T:** In SQL the database went through the rows for you. In Python you say it yourself: for each fee in fees, do something. The colon opens the "do something", and the lines pushed in underneath are inside it. Here print just means "show me".

```python
for fee in fees:
    print(fee)
```

*Given. New thought: go through each one. `print` is labelled as vocabulary.*

**C9.** **T:** Show me each status, one at a time.

```python
for status in statuses:
    print(status)
```

**C10.** **T:** Inside the loop we can ask a question, the same kind each row answered after WHERE. The word is if, it also ends with a colon, and what should happen on a yes is pushed in again. Go through the fees and show only the ones above 5.

```python
for fee in fees:
    if fee > 5:
        print(fee)
```

**T:** That was WHERE, by hand.

*New thought: a question inside the loop. The colon and indent idea is used a second time without being re-taught.*

**C11.** **T:** Now go through the statuses and show only the delivered ones. One thing first. Ana wrote `if status = 'delivered':`. Ana, what does a single `=` do in Python? ... It gives a name. Here we are not naming, we are asking, and asking is written with two.

```python
for status in statuses:
    if status == 'delivered':
        print(status)
```

*Preventative correction. The confusable pair is met through a classmate before the learner can make the slip.*

**C12.** **T:** Showing is fine, but usually we want a number. For that we keep a running count. It starts at zero before the loop, and inside the loop we add one: `count = count + 1`. How many fees are above 5?

```python
count = 0
for fee in fees:
    if fee > 5:
        count = count + 1
print(count)
```

*New thought: a result that starts before the loop and is updated inside it. The heaviest step in this opening.*

**C13.** **T:** How many orders were delivered?

```python
count = 0
for status in statuses:
    if status == 'delivered':
        count = count + 1
print(count)
```

**T:** That is `SELECT COUNT(*) ... WHERE status = 'delivered'`, written out by hand. You named a result, went through each one, asked a question, and kept count.

*The surprise sentence. It is a complete small script, and it closes the loop back to the first SQL question the learner ever answered.*

### 3.7 What Python changes in the build

- **Answers can no longer be checked by comparing text.** There are too many correct ways to write a loop. The app will have to run the learner's code and check what it produces. Running Python in a single HTML file is possible but adds a download of several megabytes on first load.
- **Indentation cannot be forgiven** the way spacing and letter case can. The typing box needs to indent automatically after a colon.
- **The course is no longer small.** My rough guess is two hours for SQL, two to three for Python and one for pandas. That guess has nothing behind it yet.

## Open questions

1. Is B12 too much for ten minutes, or is that stretch the point?
2. Should the learner type a one-line plan in English before the code, or is thinking it enough?
3. How many classmate mistakes per ten minutes feels right? Each draft has one.
4. Is SQL, then Python, then pandas the right order for you, given which interviews are closest?
5. Should the three strands be one app, or three small ones that share a design?
