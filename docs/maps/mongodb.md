# MongoDB strand map

Status: **approved by the owner on 25 Nov 2026**, with the answers recorded at the end (decision C26). Read `docs/maps/sql.md` first for how a map is laid out.

**This strand is an optional extra**, like the extra recordings Michel Thomas published beside his main courses (decision C28). SQL, Python and pandas are the foundations of a data science interview, and nothing in them waits for MongoDB. See "An optional extra" below.

Six lessons. MG-1 to MG-3 are the foundation. MG-4 to MG-6 are the interview layer, which opens once MG-3 is finished (decision C27). The strand opens after the SQL foundation, because every Mongo thought is a SQL thought in a new spelling and the lessons say so aloud.

The strand's idea: **a pipeline is the thinking order, written down.** SQL is written answer-first and thought table-first: from the table, keep rows, make piles, summarise, keep piles, sort, cut. MongoDB's `aggregate` is that same thinking order as a list of stages, in the order things happen: `$match` keeps rows, `$group` makes piles, `$match` again keeps piles, `$sort`, `$limit`. A table goes in, a table comes out, at every stage.

Every lesson asks questions the learner has already answered in SQL, on the same data, and gets the same number. MG-3 ends on the closing sentence of SQL-2 and gets 113, 112, 109, 109, 108. MG-5 ends on the closing sentence of SQL-4 and gets the same four city averages to the last digit. Nothing about the movements is new. Only the spelling is, and the new thing a document brings is the shape: a value can be a list or another document.

## How to read a lesson

- **Thoughts** are listed in teaching order, each with an identifier for the audit and a grade from decision C10. *Core* is typed from memory and returns spaced. *Shape* means the teacher's line supplies the spelling every time and says so. *Name only* is one aside and is never asked.
- **Closes with** is the surprise sentence. Its model answer was run on a real `mongod` (v8.2.4, loaded from `data/mongo/`) with `mongosh`, and the result is quoted.
- **Opens with** is the cold check that starts the sitting.

## Conventions, to keep things to remember down

Decided here so that no lesson has to decide them again:

- **One spelling for text:** double quotes, as the MongoDB documentation writes them (the owner's decision, 25 Nov 2026). A learner who types single quotes is not wrong. The checker judges by result, and the engine reads both.
- **Field names are bare words** (`status`, `subtotal`), except a dotted name, which must wear quotes (`"delivery.rain"`) because a dot is not part of a word. That is the only quoting rule for names, and its reason is real.
- **Every operator starts with a dollar sign.** `$gt`, `$match`, `$sum`. A dollar sign in front of a field name inside quotes (`"$restaurant_id"`) means the value of that field. These are two different jobs for one character, and the lesson that meets the second one says so (MG-3, `field-value`).
- **The shell words stay out.** No `.pretty()`, no variables, no `let`, no loops. One sentence is one `db.<collection>.<method>(...)`, possibly with `.sort(...)` and `.limit(...)` chained. This is also what the runner reads (see "Running an answer" in the plan).
- **A document is judged by its values.** Field order and the name of a computed field do not matter, as column names do not in SQL. `_id` matters when it is a pile's name, and when a step shows ids.
- **The data is the course data in `data/mongo/`.** Collections `orders`, `restaurants`, `couriers`, `coupons`. A primary key is `_id`, not `order_id`, and a reference to another collection is a plain field (`restaurant_id`). Every prompt names the collection and its fields, as the clarity rule in `docs/08-authoring-lessons.md` requires.
- **No lesson requires a thought from the SQL interview layer.** Where an interview-layer SQL idea is echoed (top of each pile, rows with no match), the teacher says it aloud and the Mongo thought is introduced afresh, so that MG-4 to MG-6 open when MG-3 is finished and not later.

## Foundation

### MG-1. Documents in, documents out

Assumes: SQL-1 to SQL-4. Opens with: a cold check from SQL-3.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `collection` | A collection is the table: `db.orders` is the table named orders. | Core |
| 2 | `find-all` | `db.orders.find()` shows every document. A document is one row, written as names with values in braces. | Core |
| 3 | `count-documents` | `db.orders.countDocuments()` counts them, where `COUNT(*)` counted rows. | Core |
| 4 | `question-is-a-document` | The question is a document too: `find({status: "delivered"})`. A name, a colon, the value it must have. There is no `WHERE`. Words wear quotes, numbers do not, as in SQL. | Core |
| 5 | `two-names-both-hold` | Two names in one question must both hold: `{status: "delivered", promised_minutes: 30}`. A comma is `AND`. | Core |
| 6 | `choose-fields` | A second document picks the fields to show: `find({...}, {subtotal: 1})`. A `1` means show it. | Core |
| 7 | `id-comes-unless-off` | `_id` comes along unless it is turned off with `_id: 0`. This just is. | Core |

Imports aloud: `from-table`, `keep-rows`, `text-quotes`, `count-rows`, `choose-columns`, `two-questions` (all from SQL-1 and SQL-2).

Closes with: the cancelled orders that were promised in 50 minutes, each one's id and subtotal.

```js
db.orders.find({status: "cancelled", promised_minutes: 50}, {subtotal: 1})
```

Result: 142 documents, each an `_id` and a `subtotal`. The first three are 100009 (42.27), 100003 (50.56) and 100039 (38.24). Judged as a set.

Note: a document is the lesson's first surprise, because `_id` arrives unasked. It is set up in step 2 (`find()` shows it) and the lesson closes on the sentence that has it in the result. Seven new thoughts, all small.

### MG-2. Sharper questions, and looking inside

Assumes: MG-1. Opens with: a cold check from MG-1.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `operator-documents` | A question of more than or less than is a document with a dollar word in it: `{subtotal: {$gt: 100}}`. `$gt`, `$gte`, `$lt`, `$lte` are the signs you know. | Core |
| 2 | `one-of` | `{cuisine: {$in: ["pizza", "japonesa"]}}` asks whether a value is one of a list. SQL has `IN` too. | Core |
| 3 | `or-takes-a-list` | `$or` takes a list of questions, and a row stays if any of them holds. | Core |
| 4 | `document-inside-document` | A value can itself be a document. An order holds its `delivery` inside it: `{distance_km: 4.2, rain: false, bag_size: 1}`. | Core |
| 5 | `dotted-name` | To ask about a field inside a field, join the names with a dot, in quotes: `"delivery.rain": true`. | Core |
| 6 | `absent-field` | A field can be absent. `{coupon_code: {$exists: false}}` asks for the orders with no coupon. This is the empty cell of SQL-3. | Core |
| 7 | `sort-spelling` | `.sort({subtotal: -1})` sorts what came out. `-1` puts the biggest first, `1` the smallest. | Core |
| 8 | `limit-spelling` | `.limit(5)` keeps the first few of what is left. | Core |

Imports aloud: `compare-signs`, `two-questions`, `empty-cells`, `sort`, `sort-direction`, `cut`.

Closes with: the five biggest delivered orders that were delivered in the rain, each one's id and subtotal.

```js
db.orders.find({status: "delivered", "delivery.rain": true}, {subtotal: 1}).sort({subtotal: -1}).limit(5)
```

Result: orders 104550 (193.68), 102720 (173.98), 103319 (173.26), 100777 (168.78) and 101339 (165.80). No tie at the cut: the sixth is 162.82. Judged in order.

Notes:

- `{coupon_code: null}` also finds the absent field, and gives the same 4,116 orders as `$exists: false`. The lesson teaches `$exists` and does not mention `null`, so that nothing is left to remember (rule B5). 25 orders have no `subtotal`, as in SQL-3.
- `.limit(5).sort(...)` sorts first all the same, as does `.sort(...).limit(5)`. The order of the two chained words does not matter in the shell. The lesson writes them in thinking order and never asks the learner to choose. The *stages* of MG-3 do depend on their order, and the lesson that meets that says so.

### MG-3. The pipeline

Assumes: MG-2. Opens with: a cold check from MG-2.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `pipeline-of-stages` | `aggregate` takes a list of stages. Each stage takes the table the one before it made. A table goes in, a table comes out. | Core |
| 2 | `match-stage` | `{$match: {status: "delivered"}}` keeps rows. It is the same question document as in `find`. | Core |
| 3 | `group-pile-name` | `{$group: {_id: "$restaurant_id", ...}}` makes the piles. Whatever follows `_id` is the pile's name. | Core |
| 4 | `field-value` | `"$restaurant_id"` in quotes means the value of that field in each document. Without the dollar it is only the word. | Core |
| 5 | `group-summaries` | What to say about each pile is written beside `_id`: `n: {$sum: 1}` counts, `avg: {$avg: "$subtotal"}` averages, `big: {$max: "$subtotal"}`. | Core |
| 6 | `sort-and-limit-stages` | `{$sort: {n: -1}}` and `{$limit: 5}` are stages too, in the same words. The order of the stages is the order things happen. | Core |
| 7 | `match-after-group` | A `$match` after a `$group` asks the piles, not the rows. This is `HAVING`, and it is the same word as `WHERE` in a different place. | Core |

Imports aloud: `piles`, `one-row-per-pile`, `pile-name`, `summary-per-pile`, `keep-before-piles`, `keep-piles`, `rows-or-piles`, `sort-by-summary`.

Closes with: the five restaurants with the most delivered orders, with how many each had (the closing sentence of SQL-2).

```js
db.orders.aggregate([
  {$match: {status: "delivered"}},
  {$group: {_id: "$restaurant_id", n: {$sum: 1}}},
  {$sort: {n: -1}},
  {$limit: 5}
])
```

Result: restaurant 2 with 113, then 24 with 112, then 3 and 59 with 109, then 22 with 108. The sixth is 35 with 105. The same numbers as SQL-2.

Notes:

- `field-value` is the one place a character does two jobs, and the only candidate for a debt of arbitrary rules (rule B5). The step that meets it runs `{$group: {_id: "restaurant_id"}}` first and shows one pile named with the plain word, then the dollar sign, so that the reason is seen and not told.
- A classmate puts `$match` for the piles before the `$group`, as Ana did with `WHERE COUNT(*)` in SQL-3, and gets an empty result.

## Interview layer (opens after MG-3)

### MG-4. Lists inside documents

Assumes: MG-3. Opens with: a cold check from MG-3.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `list-inside-document` | A value can be a list. Each order holds the dishes it was made of: `items: [{name, qty, price}, ...]`. | Core |
| 2 | `dotted-through-list` | `{"items.name": "Margherita"}` finds the orders where any dish is Margherita. The dot reaches through the list. | Core |
| 3 | `size-of-list` | `{items: {$size: 3}}` finds the orders with exactly three dishes. | Core |
| 4 | `elem-match` | `{items: {$elemMatch: {name: "Margherita", qty: 2}}}` asks of one dish at a time. With two dotted names, the two questions may be answered by two different dishes. | Core |
| 5 | `unwind-stage` | `{$unwind: "$items"}` makes one document of each dish, the rest of the order copied beside it. A list comes out as rows. | Core |
| 6 | `group-after-unwind` | After an unwind, a pile counts dishes, not orders. 6,000 orders became 12,700 dishes. | Core |
| 7 | `computed-value` | A value can be worked out from fields: `{$multiply: ["$items.qty", "$items.price"]}`. | Shape |

Imports aloud: `join`, the fan-out of SQL-4's cross join (360,000 rows); `piles`.

Closes with: the five dishes sold in the greatest quantity, with the quantity and what they earned.

```js
db.orders.aggregate([
  {$unwind: "$items"},
  {$group: {_id: "$items.name", qty: {$sum: "$items.qty"},
            earned: {$sum: {$multiply: ["$items.qty", "$items.price"]}}}},
  {$sort: {qty: -1}},
  {$limit: 5}
])
```

Result: Clássico 753 (20,833.41), Batata frita 748 (12,239.23), Milkshake 744 (13,755.87), Cheese bacon 723 (23,296.24) and Refrigerante 695 (5,411.34). The sixth, Pastel, has 565, so there is no tie at the cut.

Notes:

- The classmate for `elem-match` is Davi, who asks for orders with a Margherita of quantity 2 using two dotted names and gets 105 orders. The right sentence gives 50. One of them is a question about two dishes, and the other about one.
- `computed-value` is shape grade: the teacher supplies the spelling every time and says it is a thing you would look up (decision C10). What is core is the idea that a value can be worked out and put where a field name stood.
- Money is floating point in the data, as in the CSVs. Totals are compared to six places, so the order a sum is added in cannot fail an answer.

### MG-5. Look things up in another collection

Assumes: MG-4. Opens with: a cold check from MG-4.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `lookup-stage` | `$lookup` sticks the matching documents of another collection onto each document. It takes four names: `from`, `localField`, `foreignField`, `as`. | Shape |
| 2 | `lookup-gives-a-list` | What it sticks on is always a list, even when only one document matches. Unwind it to get a plain document. | Core |
| 3 | `mongo-pile-by-looked-up` | Once it is on the document, a field of the looked-up one can name the piles: `"$restaurant.city"`. | Core |
| 4 | `lookup-keeps-unmatched` | A document with no match keeps an empty list, and `$unwind` throws that document away. The rows with no match are the rows `LEFT JOIN` kept. | Core |
| 5 | `why-items-inside` | Dishes sit inside the order because they belong to it alone. Restaurants live outside because many orders point to one. | Name only |

Imports aloud: `join`, `join-on`, `pile-by-looked-up`, the dropped rows of SQL-4 (5,601, not 6,000), and the idea of SQL-8. None is required as a thought.

Closes with: two sentences.

First, the average subtotal in each city, delivered orders only (the closing sentence of SQL-4).

```js
db.orders.aggregate([
  {$match: {status: "delivered"}},
  {$lookup: {from: "restaurants", localField: "restaurant_id", foreignField: "_id", as: "restaurant"}},
  {$unwind: "$restaurant"},
  {$group: {_id: "$restaurant.city", avg: {$avg: "$subtotal"}}}
])
```

Result: Belo Horizonte 59.8310, Curitiba 61.3740, Rio de Janeiro 60.9755, São Paulo 60.2494. The same four numbers as SQL-4, to the last digit.

Second, the coupons that nobody has used (the sentence of SQL-8).

```js
db.coupons.aggregate([
  {$lookup: {from: "orders", localField: "_id", foreignField: "coupon_code", as: "used"}},
  {$match: {used: {$size: 0}}},
  {$project: {discount_pct: 1}}
])
```

Result: one coupon, `VOLTA15`, with a discount of 15.

Notes:

- `lookup-keeps-unmatched` is taught by a classmate. Ana joins orders to coupons and unwinds, and 6,000 orders become 1,884, since only the orders that used a coupon survive. The lookup alone keeps all 6,000, with an empty list on 4,116 of them. This is the SQL-4 aside (6,000 became 5,601) again, and the word for the fix, `preserveNullAndEmptyArrays`, is not taught. It is named once as something to look up.
- `$lookup` is shape grade: four names to supply, and the teacher supplies them every time and says it is one to look up. `lookup-gives-a-list` is the part to know.
- The reference is to `_id` of the other collection, because that is how the data is stored. The prompt says so in words ("the restaurant's `_id`").

### MG-6. Top of each pile, dates, and changing things

Assumes: MG-5. Opens with: a cold check from MG-5.

| # | Identifier | The thought | Grade |
|---|---|---|---|
| 1 | `first-in-pile` | Sort first, then group, and `$first` takes each pile's first document: the newest, the biggest. The sort stage comes before the piles are made. | Core |
| 2 | `mongo-top-n-per-pile` | `$topN` keeps the best few of each pile, in one stage: `{$topN: {n: 2, sortBy: {subtotal: -1}, output: "$subtotal"}}`. | Shape |
| 3 | `mongo-date-to-month` | A date cut down to its month: `{$dateToString: {format: "%Y-%m", date: "$created_at"}}`. This one you would look up. | Shape |
| 4 | `comparison-in-a-stage` | Inside a stage, a comparison is written as a list: `{$gt: ["$actual_minutes", "$promised_minutes"]}` gives true or false for each document. | Core |
| 5 | `conditional-sum` | `{$cond: [question, 1, 0]}` gives 1 or 0, and summing it counts. `$sum` of that is the conditional count of SQL-9. | Core |
| 6 | `update-one` | `updateOne({_id: 7}, {$set: {status: "cancelled"}})` changes a field of one document and reports how many it found and changed. | Shape |
| 7 | `upsert-index-explain` | Names only: an `upsert` inserts when nothing matches, an index makes a question faster, and `explain` shows how a question was answered. | Name only |

Imports aloud: `keep-before-piles`, the idea of SQL-7 (the first row of each pile), and `date-to-month`, `conditional-count` of SQL-9. None is required as a thought.

Closes with: two sentences.

First, each customer's latest order, with the customer, the order id and the time (the sentence of SQL-7).

```js
db.orders.aggregate([
  {$sort: {created_at: -1}},
  {$group: {_id: "$customer_id", order: {$first: "$_id"}, at: {$first: "$created_at"}}}
])
```

Result: 1,475 documents, one for each customer. Customer 1's latest order is 100766, on 24 October 2026 at 17:41. No customer has two orders at the same minute, so no tie.

Second, for each month of the delivered orders, how many orders there were and how many were late: actual minutes above the promised minutes.

```js
db.orders.aggregate([
  {$match: {status: "delivered"}},
  {$group: {_id: {$dateToString: {format: "%Y-%m", date: "$created_at"}},
            n: {$sum: 1},
            late: {$sum: {$cond: [{$gt: ["$actual_minutes", "$promised_minutes"]}, 1, 0]}}}},
  {$sort: {_id: 1}}
])
```

Result: 2026-08 with 1,929 orders, 802 late. 2026-09 with 1,813 and 776. 2026-10 with 1,859 and 808.

Notes:

- **Updates run on a scratch copy, so the course data never changes.** `update-one` is the only step that changes anything. Before the sentence runs, the runner clones the course data into a scratch database. The sentence runs against the clone, and the clone is dropped afterwards. The course database itself is opened read-only for every other sentence and is never written, so after the lessons end the original data is exactly as it was (the owner's requirement, 25 Nov 2026). Each sentence gets its own scratch copy, so a later `find` cannot see the change. The answer is judged by what `updateOne` reports (one found, one changed), and the teacher says in words what the change did.
- `mongo-top-n-per-pile` is shape grade and appears once, as the one-stage way to say what `first-in-pile` says in two. The core thought is `first-in-pile`. On the 60 restaurants, the top two subtotals of restaurant 1 are 158.13 and 154.34.
- The classmate for `first-in-pile` groups without sorting first. The learner gets some order's id and time for each customer, and cannot say which. The same trap as `LIMIT` without `ORDER BY` in SQL-7.
- `upsert-index-explain` is an aside. Nothing in it is asked and it adds no thought to remember.

## An optional extra

The owner's rule (25 Nov 2026): a learner must be able to finish SQL, Python and pandas without being tied up by MongoDB. So:

- **Nothing in the core course requires a Mongo thought,** and no core lesson, cold sitting A or cold sitting B asks a Mongo prompt. This was already true of the prerequisite graph (decision C27) and is now a rule.
- **It sits apart in the course.** `content/course.yaml` lists the six lessons, and cold sitting C, under a separate `extras` list after the core. The Course panel shows them under their own heading, "Extra: MongoDB", with a line saying they are optional and open after the SQL foundation.
- **The course never leads into it.** The "next lesson" after a finished core lesson is always the next core lesson. Only when the whole core is finished does the done screen offer the extras. A learner who is mid-course is never pointed at MongoDB.
- **Finishing it is not a goal.** The panel shows no count and no "extras remaining". A learner may start MG-1 as soon as the SQL foundation is done, and may stop after any lesson.
- **The time goal is unchanged.** About eight hours for the core, and about two more for the extra.

## The cold sitting for this strand

Cold sitting C (`content/cold/lesson-03.yaml`) closes the extra on the real Nobel Prize data, as the SQL cold sittings use Olist (decision C17). It is optional like the rest of the strand. It is written after the Nobel data has been fetched and its fields confirmed, and it has its own short map. It is not part of this map.

## Checks done on this map

- **Every closing sentence runs** on a real `mongod` v8.2.4 loaded from `data/mongo/`, with `mongosh`, and the results quoted above are what it returned. The eight sentences are in the blocks above, exactly as they will be typed.
- **The two SQL echoes are exact.** The five restaurants of MG-3 equal the closing result of SQL-2. The four city averages of MG-5 equal the SQL result on the CSV tables, to 15 digits. The 1,475 customers of MG-6 equal the number of distinct customers in `orders.csv`.
- **Facts the thoughts depend on were measured, not assumed:** `$exists: false` and `null` both give 4,116. `.limit().sort()` sorts first. Two dotted names give 105 orders where `$elemMatch` gives 50. A lookup keeps 6,000 orders, and an unwind keeps 1,884. `$first` after a sort and `$topN` agree (158.13 for restaurant 1). A `updateOne` on a scratch collection reports `matchedCount: 1, modifiedCount: 1`.
- **Prerequisites.** MG-1 to MG-3 assume only SQL-1 to SQL-4 and earlier Mongo lessons. MG-4 to MG-6 assume only earlier Mongo lessons. No lesson requires a thought from the SQL interview layer, the Python or pandas strands. The prerequisite rule of decision C27 therefore gives: MG-1 opens after the SQL foundation, MG-4 after MG-3.
- **Size.** No lesson has more than eight new thoughts. MG-2 has eight, MG-1, MG-3, MG-4 and MG-6 have seven, MG-5 has five.
- **Grades.** Core 34, shape 5 (`computed-value`, `lookup-stage`, `mongo-top-n-per-pile`, `mongo-date-to-month`, `update-one`), name only 2 (`why-items-inside`, `upsert-index-explain`).
- **The ids** `mongo-pile-by-looked-up`, `mongo-top-n-per-pile` and `mongo-date-to-month` carry a prefix because `pile-by-looked-up`, `top-n-per-pile` and `date-to-month` already exist in the SQL and pandas strands, and an id may be introduced once.

## Answered by the owner on 25 Nov 2026

1. **Quotes.** Double quotes, as MongoDB's own documentation writes them.
2. **Updates.** `update-one` stays in MG-6. All writes happen on a scratch copy cloned from the course data for the sentence, so the original data does not change after the lessons end.
3. **Order.** Recommended by concept: foundation, then interview layer. But the strand is an optional extra, kept apart from the core so that SQL, Python and pandas, the foundations of the interview, are never tied up by it (decision C28).

## As written, 25 Nov 2026

All six lessons are in `content/mongo/` and listed under `extras` in `content/course.yaml`. They pass the checker (0 failures), and a test sits each one through the real engine twice: once typing every model answer, and once missing every typed step first, so that every ladder, walk and return is played. **The owner has not yet sat any of them.** Changes from this map, each said by the writer in the lesson's notes:

- **MG-1** has two classmates: Davi (words without quotes, `{status = ...}`) and Ana (the field choice written first, which gives 0 documents and brings in the empty question `{}`). `collection` and `find-all` arrive in one give and one ask, and two gives follow before the first typed count, because the checker treats collection plus method as one slot. A short ask on coupons shows an `_id` that is a code.
- **MG-2** has the absent-field give name `$exists: true` as well as `false`, so that returns can use it. The classmate is Davi writing `delivery.rain` without quotes, with the runner's own "expected `:`" line.
- **MG-3** shows `group-pile-name` first with a constant pile name (`_id: "all orders"`), so that the dollar sign is not used before `field-value`, and shows `pipeline-of-stages` with an empty pipeline. The closing sentence is judged as a set because 3 and 59 tie at 109. A wrong answer that put `$limit` before `$sort` was dropped, because an unsorted `$group` sometimes gave the right five by luck.
- **MG-4** introduces `elem-match` inside Davi's step: he runs his two-dotted-names slip (105 orders) and a worked `$elemMatch` (Pastel, quantity 1), then types the question for Margherita, quantity 2 (50 orders). The lesson uses `$sum: "$items.qty"`, a field value where MG-3 taught `$sum: 1`, and says so, citing SQL's `SUM`. 25 orders have no `items` and vanish at `$unwind`. The lesson says so twice.
- **MG-5** leaves `$project` out of the second closing sentence, because no lesson teaches it. The result is the whole `VOLTA15` document, with `used` an empty list. A second classmate (Davi) forgets the unwind, and the piles come out named by lists. A give shows the lookup running from `coupons` to `orders`. Ana counts the orders by status after the unwind: delivered 1,769 and cancelled 115, which add up to 1,884 against 6,000. The lookup alone keeps 5,601 delivered and 399 cancelled. Step 19 has no `result`, only `rows: 1`, because the checker compares a nested empty list `[]` in `result` with a tuple and fails it.
- **MG-6** follows the correction above: `update-one` is judged by the report `[true, 1, 1, 0]`, with no follow-up `find`. The classmate asks for each customer's biggest order, not the latest, so that the closing sentence is not a one-slot edit of it. Extra steps recombine `first-in-pile` with the month, `$topN`, a conditional count by rain, and a lookup with a late count by cuisine.

Found while writing, and fixed in the runtime: an update without a `$` operator raised an uncaught `ValueError` and now gives the driver's own words as an error. An unsorted `$group` has no fixed order, so a wrong answer that depends on it can pass by luck: such answers were replaced by a sort the wrong way round.

