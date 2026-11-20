# SQL lesson 1: from "how many?" to piles

Status: first draft, 20 Nov 2026, for the owner's review. Nothing here is wired into an app. This is milestone 2 of `docs/07-roadmap.md`.

It extends Opening B from `docs/research/02-panorama-and-openings.md` into one sitting, with the early look at raw rows borrowed from Opening A (decisions R1 and R5).

| | |
|---|---|
| Strand and stage | SQL, stage 1 |
| Length | 23 steps, 16 of them typed. Aimed at fifteen to twenty minutes. Not yet measured. |
| Assumes | Nothing. This is the first lesson of the course. |
| Opening cold check | None. There is no earlier lesson. |
| Closing cold check | Step 23 |
| Classmates | Davi (step 8) and Ana (step 20) |

## How to read this

- **T:** is the teacher's line, as the learner sees it.
- A fenced block is code. In an Ask step it is the model answer the learner is expected to type. In a Give or Classmate step it is shown to the learner.
- *Italics are notes for the writer and are never shown.*
- **Narration** lists alternative lines for after a correct answer. In a step that introduces a thought, every line names that thought, at different depths. In other steps one line may be empty.
- **If they write** lists predictable answers that are not the model answer, with the leading question for rung 2 of the correction ladder and the reason the question matters.
- **Walk** is the step broken into smaller prompts, for rung 3.
- Every result quoted was produced by running the code against `data/`. See "Checks done by hand" at the end.

## Thoughts

Each has an identifier. "Import" means the learner already owns it from somewhere else and the script says so out loud.

| Identifier | The thought | Introduced |
|---|---|---|
| `count-rows` | `SELECT COUNT(*)` asks how many rows. | Step 1 |
| `from-table` | The table being asked goes after `FROM`. | Step 2 |
| `star` | The star means everything. `SELECT *` shows the rows themselves. | Step 3 |
| `table-out` | A table goes in, a table comes out. | Step 5 |
| `keep-rows` | A yes-or-no question is asked of every row and only the yes rows go on. It is written `WHERE` and comes after the table. | Step 6 |
| `compare-signs` | Import from maths: `>`, `<` and `=`. | Step 6 |
| `text-quotes` | A word we are looking for wears quotes. A bare word is read as a column's name. | Step 8 |
| `summary-column` | A summary about a column wraps the column: `AVG(subtotal)`. | Step 11 |
| `piles` | `GROUP BY` sorts the rows into piles by a column, and the summary is said of each pile. | Step 15 |
| `one-row-per-pile` | One row comes out per pile. | Step 16 |
| `pile-name` | The pile's name has to be asked for, or the numbers come out unlabelled. | Step 17 |
| `commas` | Import from English: a comma between two things in a list. | Step 17 |
| `summary-per-pile` | What is said about each pile can be any summary, not only a count. | Step 19 |
| `keep-before-piles` | After the table, the sentence runs in the order things happen: keep rows, then make piles. | Step 21 |

## The script

### Step 1. Give. New thought: `count-rows`

**T:** Nearly everything you will be asked about data is a question about a table: how many, how much on average, which ones. We'll answer those from the first minute. There is a table called orders, with one row for every food delivery order. To ask how many rows it has, we say:

```sql
SELECT COUNT(*) FROM orders
```

**T:** Give me the count, from orders. Run it.

**T (after the run):** 6,000 orders. SELECT is how SQL says "give me". Type the brackets and the star just as they are for now. They get their reason in a minute.

*The first thing the learner sees is an answer to a question. The star and brackets are used before they are explained (rule B3), and the promise is kept in steps 3 and 11.*

### Step 2. Ask. New thought: `from-table`

**T:** There is another table, called restaurants. How many restaurants are there? Stop and think it out before you type. Nothing here is timed.

```sql
SELECT COUNT(*) FROM restaurants
```

Result: 60.

- **Requires:** `count-rows`, `from-table`
- **Narration:**
  - 60. The table's name went after FROM and everything else stayed as it was.
  - The same question, asked of a different table. Whichever table you are asking goes after FROM. 60 restaurants.
  - 60. FROM is where you say which table.
- **If they write:**
  - `SELECT COUNT(*) restaurants`. It runs and answers 1. *Leading question:* "One restaurant? Read yours aloud: give me the count... from where?" *Why it matters:* without FROM there is no table, and SQL quietly counts nothing in particular.
  - `SELECT COUNT(restaurants)`. Error: no such column. *Leading question:* "In the first sentence, where did the table's name sit?" *Why it matters:* the brackets are not where the table goes.
- **Walk:** (1) Type again the sentence that counted the orders. (2) Which word in it says which table? Put restaurants there.
- *First typed sentence, and the first rule of engagement, at the moment it matters. Only the table changes from step 1, on purpose: it fixes where the table goes. This is the one place where a one-slot change is wanted.*

### Step 3. Give, with a run. New thought: `star`

**T:** Before we count anything else, look at what you have been counting. In place of the count, put just a star:

```sql
SELECT * FROM orders
```

**T:** Run it.

**T (after the run):** There they are, one row per order. The star is how SQL writes "everything": every row, every column. That one just is. You had typed it already, inside COUNT(*), where it said: count everything, every row.

**T:** Look along the top. Subtotal, delivery_fee, status: we'll use those. A few cells are empty. Leave them for another day.

*The raw look borrowed from Opening A. It pays the debt on the star from step 1 and puts the column names in front of the learner before any prompt uses them. The app shows the first rows of the 6,000. The remark about empty cells is marked as something to set aside (rule D4).*

### Step 4. Ask. No new thought

**T:** There is a third table, couriers: the people who carry the orders. Show me all of it.

```sql
SELECT * FROM couriers
```

Result: 200 rows, with columns courier_id, vehicle, city.

- **Requires:** `star`, `from-table`
- **Narration:**
  - Everything, from couriers. Each courier has a vehicle and a city.
  - 200 couriers, three columns.
  - (empty)
- **If they write:**
  - `SELECT COUNT(*) FROM couriers`. Answers 200. *Leading question:* "That tells me how many there are. I asked to see them. What did we put in place of the count?" *Why it matters:* "how many" and "show me" are different requests, and each has its own word.
- **Walk:** (1) Type the sentence that showed all of orders. (2) Now the same for couriers.
- *"Show me" replaces "give me". The star returns one step after it arrived. The vehicle column is seen here, five steps before it is needed.*

### Step 5. Give, nothing to type. New thought: `table-out`

**T:** Notice what every sentence so far has done. A table went in and a table came out. With the star, the whole table came out. With the count, a very small one came out: one row, one column. A table goes in, a table comes out. Everything in SQL is that.

**T:** That picture is the one thing worth holding on to. The rest, let go. Don't try to memorise anything and don't take notes. If something slips, it will come back, and making it come back is my job, not yours.

*The overarching idea, marked as essential. The second rule of engagement arrives beside it, just before the first real climb, and uses it: one picture to keep, everything else to release (rules A3 and A5).*

### Step 6. Ask. New thought: `keep-rows`. Import named: `compare-signs`

**T:** Usually we don't want every row. To keep only some, we ask each row a question, and each row answers yes or no. Only the yes rows go on. The question is written with the signs you know from maths: >, < and =. For the big orders it reads `WHERE subtotal > 100`, and it comes straight after the table.

**T:** So: from orders, keeping the rows where the subtotal is above 100, show me everything.

```sql
SELECT * FROM orders WHERE subtotal > 100
```

Result: 632 rows.

- **Requires:** `star`, `from-table`, `keep-rows`, `compare-signs`
- **Narration:**
  - Look down the subtotal column: every one is above 100. Each row was asked the question and only the yes rows came out.
  - 6,000 rows went in, each one answered yes or no, and 632 came out.
  - The question went after the table, and the rows that answered no are gone.
- **If they write:**
  - `SELECT subtotal > 100 FROM orders`. It runs and gives 6,000 rows of 0 and 1. *Leading question:* "Every row gave its answer, written as 1 for yes and 0 for no. But all 6,000 rows are still here. Which word does the keeping?" *Why it matters:* the question alone only gets answered. WHERE is what drops the no rows.
  - `SELECT * WHERE subtotal > 100 FROM orders`. Syntax error. *Leading question:* "The question is asked of each row of a table. When SQL reaches your question, has it been told which table?" *Why it matters:* the table comes first because that is where the rows come from.
  - `SELECT * FROM orders subtotal > 100`. Syntax error. *Leading question:* "Which word opens the question?"
- **Walk:** (1) Show me everything from orders. (2) Now add the question after the table: WHERE, then the column, the sign, the number.
- *The prompt is in thinking order: table, keep, then what to show. Keep-rows is introduced with the star and not with the count, so that the learner can see the surviving rows. This differs from Opening B, where it arrived inside a count. "Comes straight after the table" is chosen over "goes at the end", which would become false at step 21.*

### Step 7. Ask. No new thought

**T:** How many orders had a delivery fee under 5?

*Thinking-order version:* From orders, keeping the ones where the delivery fee is under 5, how many?

```sql
SELECT COUNT(*) FROM orders WHERE delivery_fee < 5
```

Result: 3,033.

- **Requires:** `count-rows`, `from-table`, `keep-rows`, `compare-signs`
- **Narration:**
  - 3,033. You kept the rows first and counted what was left, even though the count is written first.
  - From orders, keep the cheap deliveries, count them. That is the order it happens in.
  - 3,033.
- **If they write:**
  - `... WHERE delivery fee < 5`. Syntax error. *Leading question:* "Look at the top of the orders table. How is that column's name written?" *Why it matters:* a column's name is one word, so the table joins it with an underscore.
  - `SELECT COUNT(delivery_fee < 5) FROM orders`. Answers 6,000. *Leading question:* "That counted every row. Where does the question go, so that rows are dropped before the counting?" *Why it matters:* keeping happens before summarising, and has its own place after the table.
- **Walk:** (1) How many orders are there? (2) Keep only the rows where the delivery fee is under 5: add the question after the table.
- *The wording drops to ordinary English, so the learner finds the thinking order alone. The narration starts to say that things happen in a different order from the one they are written in. That is the background for step 21.*

### Step 8. Classmate (Davi), with a run. New thought: `text-quotes`

**T:** The status column holds a word: delivered or cancelled. Davi wanted to know how many orders were cancelled, and wrote:

```sql
SELECT COUNT(*) FROM orders WHERE status = cancelled
```

**T:** SQL answered: no such column: cancelled. Davi, is cancelled a column in our table, or a word we are looking for? ... A word. SQL reads a bare word as the name of a column. A word we are looking for wears quotes:

```sql
SELECT COUNT(*) FROM orders WHERE status = 'cancelled'
```

**T:** Run it.

**T (after the run):** 399 orders were cancelled.

*Davi makes the mistake before the learner can (rule E6), and the database's own message supplies the real reason. This is also the first use of the equals sign, which arrived as an import in step 6.*

### Step 9. Ask. No new thought

**T:** The couriers ride a bike, a moto or a carro. How many of them ride a bike?

```sql
SELECT COUNT(*) FROM couriers WHERE vehicle = 'bike'
```

Result: 73.

- **Requires:** `count-rows`, `from-table`, `keep-rows`, `compare-signs`, `text-quotes`
- **Narration:**
  - 73. Bike is a word you were looking for, so it wore quotes. Vehicle is a column's name, so it did not.
  - From couriers, keep the bikes, count them. 73.
  - 73 on bikes.
- **If they write:**
  - `... WHERE vehicle = bike`. Error: no such column: bike. *Leading question:* "Is bike a column in couriers, or a word we are looking for?" *Why it matters:* a bare word is read as a column's name.
  - `... WHERE vehicle = 'Bike'`. Answers 0. *Leading question:* "Zero. Look at how the table writes it. Is yours written the same way?" *Why it matters:* inside quotes it is data, and data is matched exactly. This is not taught as a thought in this lesson. It is only caught if it happens.
  - `SELECT COUNT(*) FROM orders WHERE vehicle = 'bike'`. Error: no such column: vehicle. *Leading question:* "Which table has the vehicle column?"
- **Walk:** (1) Show me all of couriers. Which column says what they ride? (2) How many couriers are there? (3) Keep only the rows where the vehicle is the word bike.
- *The three words are spelled out in the prompt exactly as the table has them. The table and the question both change from Davi's sentence.*

### Step 10. Ask. No new thought

**T:** Back to the restaurants. Each one has a cuisine: pizza, japonesa, hamburguer and a few more. Show me the pizza places, the whole row for each.

```sql
SELECT * FROM restaurants WHERE cuisine = 'pizza'
```

Result: 8 rows.

- **Requires:** `star`, `from-table`, `keep-rows`, `compare-signs`, `text-quotes`
- **Narration:**
  - Eight pizza places. While you are here, look at the city column: São Paulo, Curitiba. We'll come back to cities.
  - The star gave you whole rows and the question kept only the pizza ones.
  - Eight rows. Each restaurant sits in a city, and that will matter soon.
- **If they write:**
  - `SELECT COUNT(*) FROM restaurants WHERE cuisine = 'pizza'`. Answers 8. *Leading question:* "Eight of them, yes. I asked to see them. What shows the rows themselves?"
  - `... WHERE cuisine = pizza`. Error: no such column: pizza. *Leading question:* "SQL went looking for a column called pizza. What tells it that pizza is a word?"
- **Walk:** (1) Show me everything from restaurants. (2) Keep only the rows where the cuisine is the word pizza.
- *The last return of the star in this lesson. Its real job is to let the learner see the restaurants table and its city column six steps before piles need it (rule C4).*

### Step 11. Ask. New thought: `summary-column`

**T:** Counting is one thing we can say about a set of rows. An average is another. The word is AVG. An average has to be the average of something, so the column goes inside its brackets: `AVG(subtotal)`. The count took a star there, because it counts whole rows.

**T:** From orders, the average subtotal?

```sql
SELECT AVG(subtotal) FROM orders
```

Result: 60.399...

- **Requires:** `from-table`, `summary-column`
- **Narration:**
  - About 60.40. AVG sat where COUNT sat, with the column it is about inside the brackets.
  - Many rows in, one number out, as with the count. This time the number is about one column.
  - About 60.40: the average, of the subtotal, from orders.
- **If they write:**
  - `SELECT AVG(*) FROM orders`. Error: wrong number of arguments. *Leading question:* "The average of what? Which column?" *Why it matters:* a count can be about whole rows, and an average cannot.
  - `SELECT AVERAGE(subtotal) FROM orders`. Error: no such function. *Leading question:* none. The teacher says: "The word is shorter, AVG. That spelling just is."
  - `SELECT AVG subtotal FROM orders`. Error: no such column: AVG. *Leading question:* "Where does the column go, so that AVG knows it is the one to average?"
- **Walk:** (1) How many orders are there? (2) The same sentence, but in place of the count: AVG, with subtotal inside its brackets.
- *This pays the second half of the debt from step 1: brackets hold what the summary is about. For the writer only: 25 orders have an empty subtotal and AVG skips them. Missing values are a later thought and nothing is said here.*

### Step 12. Ask. No new thought. Friction

**T:** This one I won't break down for you. What was the typical delivery fee on the big orders, the ones above 100?

```sql
SELECT AVG(delivery_fee) FROM orders WHERE subtotal > 100
```

Result: 5.32.

- **Requires:** `from-table`, `summary-column`, `keep-rows`, `compare-signs`
- **Narration:**
  - 5.32. Two different columns: one inside the question, to choose the rows, and another inside AVG, to say what the average is about.
  - From orders, keep the big ones, average their delivery fee. You found that order yourself.
  - Typical meant average, big meant above 100, and you did the translating.
- **If they write:**
  - `SELECT AVG(subtotal) FROM orders WHERE subtotal > 100`. Answers 123.00. *Leading question:* "That is the average size of a big order. Which column did I ask the average of?"
  - `SELECT AVG(delivery_fee) FROM orders WHERE delivery_fee > 100`. Answers nothing. *Leading question:* "No delivery fee is above 100, so no rows were left. What is it that is above 100?"
- **Walk:** (1) From orders, show me the rows where the subtotal is above 100. (2) Not the rows this time, one number about them: the average delivery fee.
- *Deliberate friction (rule C9). "Typical" for average, "big" for above 100, and the column inside AVG is not the column in the question.*

### Step 13. Aside. Nothing to type

**T:** Something that is only interesting, with nothing in it to keep. SQL was designed at IBM in the early 1970s, so that people who were not programmers could put questions to a database. Its first name was SEQUEL, for Structured English Query Language, which is why many people still say "sequel". That is where "give me the count, from orders" comes from: it was meant to read like a sentence. It is also why the sentence opens with what you want, even though, as you have noticed, things happen starting from the table.

*Relief after the climb of steps 11 and 12 and before the steepest part of the lesson (rule C8). A real origin, not a mnemonic. It quietly restates the thinking-order observation.*

### Step 14. Ask. No new thought

**T:** On the delivered orders, what was the average subtotal?

*Thinking-order version:* From orders, keeping the delivered ones, the average subtotal.

```sql
SELECT AVG(subtotal) FROM orders WHERE status = 'delivered'
```

Result: 60.43.

- **Requires:** `from-table`, `summary-column`, `keep-rows`, `compare-signs`, `text-quotes`
- **Narration:**
  - 60.43. Keep the delivered rows, then average what is left.
  - A word in quotes inside the question, a column inside AVG.
  - (empty)
- **If they write:**
  - `... WHERE status = delivered`. Error: no such column: delivered. *Leading question:* "Is delivered a column, or a word?"
  - `SELECT COUNT(*) FROM orders WHERE status = 'delivered'`. Answers 5,601. *Leading question:* "That is how many were delivered. What did I ask about them?"
- **Walk:** (1) From orders, the average subtotal. (2) Keep only the delivered rows first.
- *An easy recombination, and a planted one. Step 21 is this sentence with piles added, so the hardest step of the lesson expands something the learner has already written.*

### Step 15. Give, with a run. New thought: `piles`

**T:** Now the idea you will use more than any other. Earlier you counted the couriers on bikes: 73. To know about the motos and the carros you could ask twice more, changing the word each time. Or you can ask once. Think of sorting the couriers into piles, one pile per vehicle, and counting each pile:

```sql
SELECT COUNT(*) FROM couriers GROUP BY vehicle
```

**T:** Run it.

**T (after the run):** 73, 17 and 110. There is your 73. GROUP BY vehicle says: group the rows by what is in their vehicle column. One sentence did the work of three.

*Marked as essential. Piles arrive as the answer to a need: the learner already has one of the three numbers and can see what it would cost to get the others. The numbers are unlabelled, and nothing is said about that yet.*

### Step 16. Ask. New thought: `one-row-per-pile`

**T:** The restaurants are spread over four cities. Count the restaurants in each city, the same way: one pile per city. Before you run it, decide how many rows will come back.

```sql
SELECT COUNT(*) FROM restaurants GROUP BY city
```

Result: 15, 6, 14, 25.

- **Requires:** `count-rows`, `from-table`, `piles`, `one-row-per-pile`
- **Check:** also accept `SELECT city, COUNT(*) FROM restaurants GROUP BY city`. A learner who writes that is one step ahead and gets the fourth narration line.
- **Narration:**
  - Four cities, four piles, four rows. One row comes out per pile, however many rows went in.
  - 60 rows went in and four came out: one for each pile.
  - One pile per city, so one row per city: four.
  - (only if the city was selected too) Four rows, one per pile. And you put the city in front so we can tell them apart. That is the next step, and you are already there.
- **If they write:**
  - `SELECT COUNT(*) FROM restaurants`. Answers 60. *Leading question:* "That is all the restaurants in one pile. What makes the piles?"
  - `... GROUP city`. Syntax error. *Leading question:* "Group the rows... by what? Two words make the piles."
- **Walk:** (1) How many restaurants are there? (2) Sort them into piles by city before counting: add the piling part after the table.
- *The new thought is exercised as a prediction, then confirmed by the result. The learner types the unlabelled form once, on purpose, and sees four anonymous numbers of their own making. Opening B gave this sentence instead of asking for it. See the questions for the owner.*

### Step 17. Ask. New thought: `pile-name`. Import named: `commas`

**T:** Look at the two answers you have: 73, 17, 110 for the vehicles, and 15, 6, 14, 25 for the cities. Which city has the 25? We can't tell. We asked only for the count, so the count is all that came out.

**T:** So we ask for the pile's name as well, in front of the count, with a comma between them, as you would write a list in English. The vehicle, and how many couriers, for each vehicle?

```sql
SELECT vehicle, COUNT(*) FROM couriers GROUP BY vehicle
```

Result: bike 73, carro 17, moto 110.

- **Requires:** `count-rows`, `from-table`, `piles`, `one-row-per-pile`, `pile-name`, `commas`
- **Check:** the two columns may come in either order.
- **Narration:**
  - Now each number has its name beside it: bike 73, carro 17, moto 110. You asked for two things, the pile's name and the count, so two columns came out.
  - The name in front, the count beside it, one row per pile. Nothing comes out that you did not ask for, and that includes the name.
  - A table with two columns came out, because you asked for two things: the pile's name and its count.
- **If they write:**
  - `SELECT vehicle COUNT(*) FROM couriers GROUP BY vehicle`. Syntax error. *Leading question:* "Two things in a list. What goes between them in English?"
  - `SELECT vehicle FROM couriers GROUP BY vehicle`. Answers bike, carro, moto. *Leading question:* "Now we have the names and have lost the numbers. How do we ask for both?"
  - `SELECT vehicle, COUNT(*) FROM couriers`. It runs and answers one row: bike, 200. *Leading question:* "One row came back. How many piles did we want? What makes the piles?" *Why it matters:* this database answers without complaint, and the answer is nonsense. Most others refuse. Either way the piling part is missing.
- **Walk:** (1) Count the couriers in each vehicle pile, as the teacher did. (2) Now ask for the pile's name too: vehicle, then a comma, in front of the count.
- *The tension from steps 15 and 16 resolves. "Select the column you grouped by" is never stated as a rule. It answers a need the learner has just felt twice.*

### Step 18. Ask. No new thought

**T:** And the cities. How many restaurants per city?

```sql
SELECT city, COUNT(*) FROM restaurants GROUP BY city
```

Result: Belo Horizonte 15, Curitiba 6, Rio de Janeiro 14, São Paulo 25.

- **Requires:** `count-rows`, `from-table`, `piles`, `one-row-per-pile`, `pile-name`, `commas`
- **Check:** the two columns may come in either order.
- **Narration:**
  - São Paulo has the 25. "Per city" was your signal: when a question says per, it wants piles.
  - One pile per city, its name in front, its count beside it.
  - There are the four numbers again, this time with their names.
- **If they write:**
  - `SELECT COUNT(*) FROM restaurants GROUP BY city`. Answers four bare numbers. *Leading question:* "Which city is which?"
- **Walk:** (1) Sort the restaurants into piles by city and count each pile. (2) Put the pile's name in front.
- *Relief after three new thoughts in a row. "Per" appears for the first time as the word that signals piles. The second open question, which city has the 25, is answered.*

### Step 19. Ask. New thought: `summary-per-pile`

**T:** Back to orders. What we say about each pile does not have to be a count. Any summary will do. Average subtotal by status.

```sql
SELECT status, AVG(subtotal) FROM orders GROUP BY status
```

Result: cancelled 59.99, delivered 60.43.

- **Requires:** `from-table`, `summary-column`, `piles`, `one-row-per-pile`, `pile-name`, `commas`, `summary-per-pile`
- **Check:** the two columns may come in either order.
- **Narration:**
  - Two piles, cancelled and delivered, and an average for each. The average took the count's place and the piles stayed as they were.
  - "By status" is "per status": one pile per status. Then you say what you want to know about each pile, and this time it was an average.
  - Any summary can be said of a pile. Here, the average: cancelled orders and delivered ones both come to about 60.
- **If they write:**
  - `SELECT AVG(subtotal) FROM orders GROUP BY status`. Answers two bare numbers. *Leading question:* "Which one is the cancelled orders?"
  - `SELECT status, AVG(subtotal) FROM orders GROUP BY subtotal`. Answers thousands of rows. *Leading question:* "How many piles did you expect? What are we piling by?"
- **Walk:** (1) From orders, the average subtotal. (2) Sort the orders into piles by status first, so that the average is said of each pile. (3) Put the pile's name in front.
- *"By" joins "per". The summary changes as well as the table and the pile, so step 18 cannot be edited into this.*

### Step 20. Classmate (Ana), and the learner repairs it. No new thought

**T:** Ana was asked how many orders each restaurant got. She wrote:

```sql
SELECT COUNT(*) FROM orders GROUP BY restaurant_id
```

**T:** Sixty numbers came back: 107, 119, 114, 82 and on. Ana, which restaurant got the 119? ... She can't say. What should she have written?

```sql
SELECT restaurant_id, COUNT(*) FROM orders GROUP BY restaurant_id
```

Result: 60 rows. Restaurant 2 has 119.

- **Requires:** `count-rows`, `from-table`, `piles`, `one-row-per-pile`, `pile-name`, `commas`
- **Check:** the two columns may come in either order.
- **Narration:**
  - Restaurant 2 got the 119. Each number has its restaurant beside it now.
  - Sixty piles, sixty rows, and each one named.
  - The pile's name in front, as before. In the orders table a restaurant is only a number, and that number is the pile.
- **Walk:** (1) What did we add when we could not tell which city had the 25? (2) Do the same for Ana, with the column she piled by.
- *Ana makes the slip the learner is most likely to make in step 21, one step before it (rule E6). It also shows restaurant_id as something to pile by, and "each" as a third word for piles after "per" and "by". The repair is a one-slot change to a sentence on screen. That is accepted here because the slot is the point.*

### Step 21. Ask. New thought: `keep-before-piles`. Friction

**T:** The last one, and I won't break it down. For the delivered orders only, the average subtotal of each restaurant. Think about what happens first, keeping rows or making piles. Then write them in that order.

```sql
SELECT restaurant_id, AVG(subtotal) FROM orders WHERE status = 'delivered' GROUP BY restaurant_id
```

Result: 60 rows. Restaurant 1 has 65.45.

- **Requires:** `from-table`, `summary-column`, `keep-rows`, `compare-signs`, `text-quotes`, `piles`, `one-row-per-pile`, `pile-name`, `commas`, `summary-per-pile`, `keep-before-piles`
- **Check:** the two columns may come in either order.
- **Narration:**
  - That is the shape of a real interview question, and you built it by thinking: from orders, keep the delivered ones, pile them by restaurant, average each pile. After the table, the sentence runs in the order things happen.
  - Keep first, pile second, and that is the order you wrote them in. Only the first part, what you want out, is written ahead of its turn.
  - Sixty restaurants, one average each, over delivered orders only. After FROM, the order of the sentence is the order of events: keep, then pile.
- **If they write:**
  - `... FROM orders GROUP BY restaurant_id WHERE status = 'delivered'`. Syntax error near WHERE. *Leading question:* "Which happens first: keeping rows, or making piles? Write them in that order." *Why it matters:* after the table, the sentence follows the order of events.
  - `SELECT AVG(subtotal) FROM orders WHERE status = 'delivered' GROUP BY restaurant_id`. Answers 60 bare numbers. *Leading question:* "Which restaurant is the first number?"
  - `SELECT restaurant_id, AVG(subtotal) FROM orders GROUP BY restaurant_id`. Answers slightly different averages. *Leading question:* "Those averages include the cancelled orders. Where do we drop them?"
- **Walk:** (1) On the delivered orders, the average subtotal. (2) Now sort what is left into piles by restaurant: the piling goes after the keeping. (3) Put the pile's name in front.
- *The surprise sentence. The learner is asked to work the clause order out, not told it (rule B4): a wrong guess produces an error, not a false belief, and the reason is real. The first rung of the walk is step 14 again. Open decision O2 asks whether this step is too big for a first sitting. It is better prepared here than in the ten-minute opening, and only a real attempt will settle it.*

### Step 22. Recap. Nothing to type

**T:** Stop there. In one sitting you went from nothing to this: from a table, keep the rows you want, sort them into piles, and say something about each pile. A count or an average, one table or another. Most questions you will be asked about data are that sentence with different words in it.

**T:** You are not fast at it yet, and you are not meant to be. Speed is trained separately, later. For now the only aim is that you can think a sentence out.

**T:** Don't go over any of this before next time. One more question, cold, and then we stop.

*States the limit (rule F2) and repeats, in other words, that the learner is not to revise.*

### Step 23. Cold check

**T:** Counting only the couriers on bikes, how many are there in each city?

```sql
SELECT city, COUNT(*) FROM couriers WHERE vehicle = 'bike' GROUP BY city
```

Result: Belo Horizonte 9, Curitiba 13, Rio de Janeiro 18, São Paulo 33.

- **Requires:** `count-rows`, `from-table`, `keep-rows`, `compare-signs`, `text-quotes`, `piles`, `one-row-per-pile`, `pile-name`, `commas`, `keep-before-piles`
- **No ladder and no narration.** Whatever is typed, the app shows its result beside the model answer and its result, records what was typed, and the teacher closes with the same line either way: "That's the sitting. We pick up from here next time."
- **What a miss tells the script:** which of keeping, quotes, piles, the pile's name, or the order of keeping and piling was absent. Lesson 2 opens by rebuilding from that point.
- *Every thought of the lesson that an answer can show, on a combination of table, question and pile that was never practised. It is never scored (rule F1).*

## Checks done by hand

These are the seven checks from `docs/04-script-format.md`, done without a checker. The checker of milestone 3 should reproduce them.

### 1. Every model answer runs

All 16 typed answers and all 6 shown sentences were run with SQLite 3.45 against the three files in `data/`, loaded with numeric columns as numbers and empty cells as missing. Each result quoted above is what came back. Every "If they write" entry was run too, and the error or result quoted is the real one.

### 2. Audit

| Step | Kind | New | Requires, beyond `from-table` | All introduced earlier? |
|---|---|---|---|---|
| 1 | Give | `count-rows` | | |
| 2 | Ask | `from-table` | `count-rows` | Yes |
| 3 | Give | `star` | | |
| 4 | Ask | | `star` | Yes |
| 5 | Give | `table-out` | | |
| 6 | Ask | `keep-rows` | `star`, `compare-signs` (named in this step) | Yes |
| 7 | Ask | | `count-rows`, `keep-rows`, `compare-signs` | Yes |
| 8 | Classmate | `text-quotes` | | |
| 9 | Ask | | `count-rows`, `keep-rows`, `compare-signs`, `text-quotes` | Yes |
| 10 | Ask | | `star`, `keep-rows`, `compare-signs`, `text-quotes` | Yes |
| 11 | Ask | `summary-column` | | Yes |
| 12 | Ask | | `summary-column`, `keep-rows`, `compare-signs` | Yes |
| 13 | Aside | | | |
| 14 | Ask | | `summary-column`, `keep-rows`, `compare-signs`, `text-quotes` | Yes |
| 15 | Give | `piles` | | |
| 16 | Ask | `one-row-per-pile` | `count-rows`, `piles` | Yes |
| 17 | Ask | `pile-name` | `count-rows`, `piles`, `one-row-per-pile`, `commas` (named in this step) | Yes |
| 18 | Ask | | `count-rows`, `piles`, `one-row-per-pile`, `pile-name`, `commas` | Yes |
| 19 | Ask | `summary-per-pile` | `summary-column`, `piles`, `one-row-per-pile`, `pile-name`, `commas` | Yes |
| 20 | Classmate | | `count-rows`, `piles`, `one-row-per-pile`, `pile-name`, `commas` | Yes |
| 21 | Ask | `keep-before-piles` | everything except `count-rows`, `star` and `table-out` | Yes |
| 22 | Recap | | | |
| 23 | Cold check | | everything except `star`, `table-out`, `summary-column` and `summary-per-pile` | Yes |

Column names are not thoughts, but each must have been seen before it is asked for. Subtotal, delivery_fee and status are seen in step 3. Vehicle is seen in step 4. Cuisine is given in the prompt of step 10, where city is then seen. Restaurant_id is seen in step 3 and shown in use in step 20.

### 3. One new thought at most per step

Holds. Steps 6 and 17 each also name an import (`compare-signs` from maths, `commas` from English), which the format allows.

### 4. No shape repeats

Consecutive typed answers, with the parts that change between them:

| From | To | What changes |
|---|---|---|
| 2 | 4 | what is selected, table |
| 4 | 6 | table, question added |
| 6 | 7 | what is selected, question |
| 7 | 9 | table, question |
| 9 | 10 | what is selected, table, question |
| 10 | 11 | what is selected, table, question removed |
| 11 | 12 | column inside AVG, question added |
| 12 | 14 | column inside AVG, question |
| 14 | 16 | what is selected, table, question removed, piles added |
| 16 | 17 | name added, table, pile column |
| 17 | 18 | name, table, pile column |
| 18 | 19 | name, summary, table, pile column |
| 19 | 20 | name, summary, pile column |
| 20 | 21 | summary, question added |
| 21 | 23 | name, summary, table, question, pile column |

No pair differs in one part. Two things to judge by eye:

- Steps 17 and 18 are the same sentence about a different table. Three parts change, but they change together. Opening B did the same in B9 and B10.
- Step 2 is a one-part change from the given sentence of step 1, and step 20 is a one-part repair of Ana's sentence. Both are deliberate.

### 5. Spacing

Steps at which each thought is needed again after it is introduced, and the gaps between them. The target is a return after roughly 1, 3, 8 and 20 steps.

| Thought | Introduced | Needed again at | Gaps |
|---|---|---|---|
| `count-rows` | 1 | 2, 7, 9, 16, 17, 18, 20, 23 | 1, 5, 2, 7, 1, 1, 2, 3 |
| `from-table` | 2 | every typed step | |
| `star` | 3 | 4, 6, 10 | 1, 2, 4 |
| `keep-rows` | 6 | 7, 9, 10, 12, 14, 21, 23 | 1, 2, 1, 2, 2, 7, 2 |
| `text-quotes` | 8 | 9, 10, 14, 21, 23 | 1, 1, 4, 7, 2 |
| `summary-column` | 11 | 12, 14, 19, 21 | 1, 2, 5, 2 |
| `piles` | 15 | 16, 17, 18, 19, 20, 21, 23 | 1 each, then 2 |
| `one-row-per-pile` | 16 | 17 to 21, 23 | 1 each, then 2 |
| `pile-name` | 17 | 18, 19, 20, 21, 23 | 1 each, then 2 |
| `summary-per-pile` | 19 | 21 | 2 |
| `keep-before-piles` | 21 | 23 | 2 |

What this shows:

- The star is not used after step 10. It is due again near the start of lesson 2.
- `summary-per-pile` and `keep-before-piles` arrive at the end and have had one return each. Lesson 2 owes them early returns.
- The pile thoughts come back at every step from 16 to 21. That is a pile-up by the schedule, and it is intended: the four pile thoughts are only usable together. Lesson 2 should space them out.
- `table-out` is never required by an answer. It is spoken in step 5 and echoed in the narration of steps 11, 16 and 17.

### 6. Narration variety

Every typed step except the cold check has three lines. Step 16 has a fourth for the learner who is a step ahead. Steps 4 and 14 have one empty line each.

### 7. Load shape

New thoughts fall at steps 1, 2, 3, 5, 6, 8, 11, 15, 16, 17, 19 and 21. That is twelve in 23 steps.

- Steps 1 to 3 are three in a row. They are the handle sentence, its table and the star, and each is small. Step 4 is relief.
- Steps 15 to 17 are three in a row and they are the steep part of the lesson. Step 13 (an aside) and step 14 (an easy recombination) come before the climb. Step 18 is relief after it.
- Steps 12 and 21 are the two friction steps. Step 20 is a breather before the second.

## Notes for the build

Not part of the lesson. Things the draft found that the checker and player will need.

- **Empty cells must load as missing, not as empty text.** Loaded as empty text, `AVG(subtotal)` and comparisons on subtotal give different answers.
- **`subtotal` is empty on 25 orders.** `data/README.md` did not list it and now does. The lesson still uses subtotal, as both openings did. AVG skips the 25 and no prompt depends on them.
- **Double quotes.** `WHERE vehicle = "bike"` fails in the SQLite used here with "no such column: bike". Requirement R11 forgives quote style, so the checker has to treat double-quoted words as text before running.
- **Either column order** is accepted in steps 17 to 21 and 23.
- **Step 16 accepts two answers**, with or without the pile's name.
- **SQLite answers some sentences that other databases refuse**, such as step 17's `SELECT vehicle, COUNT(*) FROM couriers`. Known wrong answers have to be recognised by their result, not by an error.

## Questions for the owner

1. **Step 16 has the learner type the unlabelled pile sentence.** Opening B gave it and went straight to the fix. Typing it makes the missing name something the learner runs into, but it is one production of a form they will not use again. Keep it, or give it as before?
2. **Keep-rows arrives with the star (step 6), not with a count.** The learner sees the surviving rows. The cost is three "show me" sentences in the first ten steps of an opening whose point was that every sentence answers a question. Acceptable?
3. **Step 20 asks the learner to repair Ana's sentence** and not only to read about it. Is that the right use of a classmate?
4. **Narration convention.** In a step that introduces a thought, every narration line names it. Otherwise one line may be empty. Is that how you want it?
5. **Twelve new thoughts in one sitting.** Opening B had eight in ten minutes, so the rate is about the same. If the sitting runs long, the natural place to cut it in two is after step 14.
6. **O2 remains open:** whether step 21 is too big a stretch. This draft prepares it more than the opening did. Only your attempt will tell.
