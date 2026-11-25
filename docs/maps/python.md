# Python strand map

Status: approved by the owner on 24 Nov 2026, with the answers recorded at the end. Read `docs/maps/sql.md` first for how a map is laid out.

Ten lessons. PY-1 to PY-6 are the foundation in pass 1, after SQL-4. PY-7 to PY-10 are the interview layer in pass 2, after SQL-9.

The strand's idea: **give a thing a name, then do something with it.** Nearly every thought here is an SQL thought done by hand, and the lessons say so each time: a loop is `FROM`, an `if` is `WHERE`, a dict of running results is `GROUP BY`.

The lessons use short lists typed into the code, with values taken from `data/`, until PY-6 brings in rows. Answers are judged by what the code produces, never by its text.

## Pass 1: foundation

### PY-1. Name a thing, then do something with it

Assumes: SQL-1 to SQL-4. Opens with: no cold check. The owner removed it on 25 Nov 2026 so that a new language does not open with an SQL question.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `name-a-value` | One `=` gives a value a name. It asks nothing. | Core |
| 2 | `list` | Several values in order, in square brackets, with commas. | Core |
| 3 | `how-many` | `len(fees)`: the list goes inside the brackets, as a column went inside `AVG`. | Core |
| 4 | `total` | `sum(fees)`. | Core |
| 5 | `build-average` | There is no average word for a list. It is the total divided by how many. | Core |
| 6 | `text-in-list` | Words wear quotes here too. | Core |
| 7 | `for-each` | `for fee in fees:` does the same thing for each item, and gives the item a name for the moment. | Core |
| 8 | `block` | The colon opens a block, and the lines pushed in are inside it. | Core |
| 9 | `show` | `print` means "show me". | Core |
| 10 | `if-question` | `if` asks a yes-or-no question. The lines inside run only on yes. | Core |
| 11 | `equals-asks` | Two equals signs ask, because one is taken for naming. | Core |
| 12 | `running-result` | A result starts before the loop, is updated inside it, and is ready after it. | Core |

Closes with: count the delivered orders by hand. This is the learner's first SQL question, written out.

```python
statuses = ['delivered', 'cancelled', 'delivered']
count = 0
for status in statuses:
    if status == 'delivered':
        count = count + 1
print(count)
```

Output: 2.

Note: this is the draft opening C1 to C13 from `docs/research/02-panorama-and-openings.md`, extended to a full sitting. Twelve thoughts is the most any lesson has, the same as SQL-1. Most are imports from SQL, which is what makes it bearable. The owner decided on 24 Nov 2026 to keep all twelve in one lesson. A classmate writes `if status = 'delivered':` before the learner can.

### PY-2. Lists that grow

Assumes: PY-1. Opens with: a cold check from PY-1.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `position` | `fees[0]` takes one item by its position. Positions count from 0. That one just is. | Core |
| 2 | `last` | `fees[-1]` is the last one. | Core |
| 3 | `add-to-end` | `fees.append(4.99)` adds one to the end. | Core |
| 4 | `new-list-in-loop` | Start with an empty list and add to it inside a loop. That is keep rows, by hand. | Core |
| 5 | `and-or` | Two questions joined with `and` or `or`, as in SQL. | Core |
| 6 | `otherwise` | `else:` holds what happens on a no. | Core |
| 7 | `sorted` | `sorted(fees)` gives a sorted copy. | Core |
| 8 | `reverse` | `reverse=True` inside the brackets turns the order round. | Core |
| 9 | `first-few` | `[:3]` takes the first three. That is `LIMIT`. | Core |

Closes with: the three biggest subtotals above 50.

```python
subtotals = [81.1, 18.85, 84.23, 91.11, 31.3]
kept = []
for s in subtotals:
    if s > 50:
        kept.append(s)
print(sorted(kept, reverse=True)[:3])
```

Output: `[91.11, 84.23, 81.1]`.

Note: the approved plan had "the three biggest delivered subtotals". That needs a status beside each subtotal, which is a row, and rows arrive in PY-6. The closing sentence was changed to keep the lesson honest.

### PY-3. Look up by name

Assumes: PY-2.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `dict` | A dict holds values under names, in curly brackets: `{'pizza': 40}`. | Core |
| 2 | `get-by-name` | `prices['pizza']`. Square brackets always mean "get from inside". | Core |
| 3 | `set-by-name` | `prices['acai'] = 25` adds a name or changes it. | Core |
| 4 | `is-it-there` | `'acai' in prices` asks whether the name is there. | Core |
| 5 | `position-or-name` | A list is asked by position. A dict is asked by name. | Core |
| 6 | `go-through-dict` | `for dish in prices:` goes through the names. | Core |
| 7 | `two-names` | `for dish, price in prices.items():` names both halves at once. | Core |

Closes with: the total price of an order, from a price list.

```python
prices = {'pizza': 40, 'sushi': 60, 'acai': 25}
order = ['pizza', 'acai', 'pizza']
total = 0
for dish in order:
    total = total + prices[dish]
print(total)
```

Output: 105.

Note: lists are fully comfortable for two lessons before dicts begin, as the plan for that confusable pair requires.

### PY-4. Piles by hand

Assumes: PY-3.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `one-entry-per-pile` | A dict with one name per pile, holding that pile's running result. | Core |
| 2 | `pile-starts-at-zero` | A pile that is not there yet has to start at zero before it can grow. | Core |
| 3 | `update-the-pile` | For each item: find its pile, update that pile. | Core |
| 4 | `get-with-default` | `counts.get(dish, 0)` is "what is there, or zero". It replaces the check. | Core |
| 5 | `total-per-pile` | The same shape with a total where the count was. | Core |
| 6 | `average-from-two-dicts` | A total per pile and a count per pile give an average per pile. | Core |

Closes with: the average price per dish.

```python
sales = [['pizza', 40], ['sushi', 60], ['pizza', 50], ['acai', 25], ['sushi', 70]]
totals = {}
counts = {}
for dish, price in sales:
    totals[dish] = totals.get(dish, 0) + price
    counts[dish] = counts.get(dish, 0) + 1
for dish in totals:
    print(dish, totals[dish] / counts[dish])
```

Output: pizza 45.0, sushi 65.0, acai 25.0.

Note: this is `GROUP BY` by hand and the commonest shape in plain-Python interview tasks. `pile-starts-at-zero` is taught first with an explicit `if dish not in counts:`, so that `.get` arrives as a shorter way to say something already understood, and not as a rule.

### PY-5. Wrap it as a function

Assumes: PY-4.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `def` | `def average(values):` gives a name to some steps. | Core |
| 2 | `what-goes-in` | The names in the brackets are what goes in. | Core |
| 3 | `what-comes-out` | `return` hands the result back. | Core |
| 4 | `call-it` | `average(fees)` runs it. A function is a query: something in, something out. | Core |
| 5 | `show-or-return` | `print` shows a value to a person. `return` hands it to the code that asked. | Core |
| 6 | `nothing` | `None` is Python's empty cell. The question is written `is None`, as SQL wrote `IS NULL`. | Core |
| 7 | `empty-case` | Ask what happens when the list is empty, before someone else does. | Core |
| 8 | `check-with-assert` | `assert average([2, 4]) == 3` is a check you write yourself. Silence means it held. | Core |
| 9 | `comment` | A line starting with `#` is a note for people. | Core |

Closes with: a function, and two checks the learner wrote.

```python
def average(values):
    if len(values) == 0:
        return None
    return sum(values) / len(values)

assert average([2, 4]) == 3
assert average([]) is None
```

Output: nothing, which is the point.

Note: this is where the testing habit starts (pass-bar task 12). From here on, narration sometimes asks for a quick check.

### PY-6. A table by hand

Assumes: PY-5.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `row-is-dict` | A row is a dict: column names and that row's values. | Core |
| 2 | `table-is-list-of-rows` | A table is a list of rows. | Core |
| 3 | `cell` | `row['status']` is one cell. | Core |
| 4 | `missing-is-none` | An empty cell arrives as `None`. | Core |
| 5 | `skip-the-missing` | `if row['subtotal'] is not None:` leaves the empty ones out, which is what `AVG` did for you. | Core |
| 6 | `read-a-file` | `csv.DictReader` turns a file into rows like these. | Shape |
| 7 | `text-to-number` | Cells from a file are text, so `float(...)` turns one into a number. Added when written, because the closing function needs it. | Core |

Closes with: the average of one column per value of another, ignoring missing values (pass-bar task 8).

```python
def average_by(rows, key, value):
    totals = {}
    counts = {}
    for row in rows:
        if row[value] is not None:
            totals[row[key]] = totals.get(row[key], 0) + row[value]
            counts[row[key]] = counts.get(row[key], 0) + 1
    result = {}
    for name in totals:
        result[name] = totals[name] / counts[name]
    return result
```

With four sample rows, one of them missing its subtotal, it returns `{'delivered': 50.0, 'cancelled': 31.3}`.

Note: the capstone of the Python foundation, and the doorway to pandas. Nothing in the closing function is new. It is PY-4, PY-5 and this lesson's rows, recombined.

## Pass 2: the interview layer

### PY-7. Sort by a rule

Assumes: PY-6. Opens with: a cold check from SQL-9.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `pair` | `('pizza', 3)` is a pair: two values that travel together. | Core |
| 2 | `dict-as-pairs` | `counts.items()` hands a dict over as pairs. | Core |
| 3 | `key-function` | `sorted(pairs, key=f)`: the function says what to sort by. | Core |
| 4 | `lambda` | `lambda pair: pair[1]` is a small function written where it is used. | Core |
| 5 | `tie-rule` | A key that returns a pair sorts by the first part, then the second. A minus sign turns a number's order round. | Core |

Closes with: the k most common items, ties in alphabetical order (pass-bar task 7).

```python
def top_k(items, k):
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    ranked = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return ranked[:k]
```

With six dishes where coca and pizza both appear twice, `top_k(dishes, 2)` returns `[('coca', 2), ('pizza', 2)]`.

### PY-8. Text as pieces

Assumes: PY-7.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `split` | `sentence.split()` cuts text into a list of words. | Core |
| 2 | `join-words` | `' '.join(words)` puts a list back together. Renamed from `join` when written, because `join` is already SQL-4's `JOIN`. | Core |
| 3 | `tidy` | `.lower()` and `.strip()` clean text before it is compared. | Core |
| 4 | `positions` | `range(len(words))` gives the positions themselves, for when you need to look at a neighbour. | Core |
| 5 | `neighbours` | `words[i]` and `words[i + 1]`, stopping one short of the end. | Core |
| 6 | `pair-as-key` | A pair can be a name in a dict. | Core |

Closes with: count the bigrams in a sentence (pass-bar task 9).

```python
def bigrams(sentence):
    words = sentence.lower().split()
    counts = {}
    for i in range(len(words) - 1):
        pair = (words[i], words[i + 1])
        counts[pair] = counts.get(pair, 0) + 1
    return counts
```

On "the order was late and the order was cold" it counts `('the', 'order')` and `('order', 'was')` twice each.

Note: `range` waits until here because this is its real reason. Earlier loops never needed a position.

### PY-9. A loop that remembers

Assumes: PY-8.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `remember-previous` | Keep the last item under a name, and update it at the end of each turn. | Core |
| 2 | `compare-with-previous` | Each item is judged against the one before it. | Core |
| 3 | `list-of-lists` | The result is a list of groups, and each group is a list. | Core |
| 4 | `start-new-group` | When the gap is too big, put the current group away and start an empty one. | Core |
| 5 | `close-last-group` | After the loop, the last group is still in your hands. Put it away too. | Core |

Closes with: group times into sessions (pass-bar task 11).

```python
def sessions(times, gap):
    groups = []
    current = []
    previous = None
    for t in times:
        if previous is not None and t - previous > gap:
            groups.append(current)
            current = []
        current.append(t)
        previous = t
    if len(current) > 0:
        groups.append(current)
    return groups
```

`sessions([1, 5, 9, 50, 55, 120], 30)` returns `[[1, 5, 9], [50, 55], [120]]`, and an empty list gives an empty list.

Note: times are plain minutes, so no date library is needed. A classmate forgets `close-last-group` and loses the final session, which is the classic slip.

### PY-10. Say it shorter, say its cost

Assumes: PY-9.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `one-line-list` | `[s for s in subtotals if s > 50]` is the loop, the question and the adding, in one line. | Core |
| 2 | `each-thing-once` | `set(items)` keeps each thing once. | Core |
| 3 | `cost-in-words` | One pass is linear. A loop inside a loop is quadratic. Looking a name up in a dict costs the same however big it is. Sorting costs a little more than one pass. | Core |
| 4 | `three-checks` | The ordinary case, the empty case, and the awkward case. | Core |
| 5 | `while-loop` | `while` repeats for as long as its question says yes. | Shape |
| 6 | `two-positions` | Two positions move through two sorted lists, and the smaller item is taken each time. | Shape |

Closes with: three checks on `top_k` and its cost in a comment (pass-bar task 12).

```python
# one pass to count, then a sort of the different items
assert top_k(['a', 'b', 'a'], 1) == [('a', 2)]
assert top_k([], 3) == []
assert top_k(['b', 'a'], 2) == [('a', 1), ('b', 1)]
```

Merging two sorted lists (pass-bar task 10) is shape grade. The teacher walks through it once and the learner types it with the walk in view. It is not brought back cold.

```python
def merge(a, b):
    result = []
    i = 0
    j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i = i + 1
        else:
            result.append(b[j])
            j = j + 1
    return result + a[i:] + b[j:]
```

`merge([1, 4, 9], [2, 3, 10, 11])` returns `[1, 2, 3, 4, 9, 10, 11]`.

## Checks done on this map

- **Every closing program runs** and gives the output quoted. They were run in a scratch folder, and nothing was installed into the project.
- **Prerequisites.** Each lesson assumes only thoughts from earlier lessons. `two-names` from PY-3 is what lets PY-4 go through a list of pairs. `nothing` from PY-5 is what PY-6 and PY-9 need for `is None`.
- **Confusable pairs.** One and two equals signs meet in PY-1 through a classmate. Lists have PY-1 and PY-2 to themselves before dicts. Showing and returning are contrasted in PY-5.
- **Size.** PY-1 has twelve thoughts, the same as SQL-1. PY-2 and PY-5 have nine. The rest have five to seven.
- **Pass bar.** Tasks 7, 8, 9, 11 and 12 are core: PY-7, PY-6, PY-8, PY-9 and PY-10. Task 10 is shape grade in PY-10.

## Answered by the owner on 24 Nov 2026

1. **`lambda`** stays core, typed from memory in PY-7.
2. **Merging sorted lists** stays shape grade. The teacher walks through it once, and it is not brought back cold.

## As written, 24 Nov 2026

All ten lessons are in `content/py/`. Changes from this map, each said by the writer in the lesson's notes:

- **PY-1** teaches `show` second, before `list`, because Python prints only when told to and a program that shows nothing cannot be judged.
- **PY-2** closes with "above 50 and under 100" on an eight-value list. With the map's list, "above 50" removed nothing, so a learner could skip the filter and still pass.
- **PY-4** has a classmate whose `.get(dish)` shows `None` before PY-5 teaches it. It is the real reason for the default.
- **PY-5** closes by also printing an average, and a hidden `check` confirms the function returns and does not print. `comment` and the learner's own `assert` lines cannot be verified from output, so a learner who leaves them out still passes.
- **PY-6** closes on real subtotals: delivered 69.41 and cancelled 31.3, not the 50.0 of the map's sample rows.
- **PY-10** judges `three-checks` weakly, since the learner's own asserts only show that they hold on their own function. `cost-in-words` is shown by counting steps. There are no infinite-loop wrong answers for `while`, because the checker would wait on them.
