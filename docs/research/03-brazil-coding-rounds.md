# What Brazilian DS coding rounds require

Research date: 20 Nov 2026. Question: given that the maths, statistics and ML knowledge is already there, exactly what hands-on coding is needed to pass data science coding rounds in Brazil?

This builds on two earlier briefs kept in the owner's project files (a formats brief of 11 Nov and the iFood Coderbyte research). It adds company-by-company evidence and turns it into a pass bar and a gap list for the course in `02-panorama-and-openings.md`.

## How far to trust this

- **No company publishes a syllabus.** The closest thing is QuintoAndar's official Data Scientist interview guide, which names its coding topics. Everything else is candidate reports or prep sites.
- **First-hand reports are few and short.** For data scientist roles I found about a dozen usable ones across Nubank, QuintoAndar, Mercado Livre, Stone and QuantumBlack, dated 2019 to 2026. Most name the round and not the questions.
- **Prep sites disagree with each other** and often say outright that they are estimating. I use them only where they match a first-hand report.
- **Not readable from here:** Itaú's Glassdoor pages and the later pages of Nubank's. Banks are therefore a gap. The earlier brief found that most banks still run the classic round with no AI allowed.
- The question lists for iFood come from an aggregator that built them from two candidate reports.

So what follows is a pattern drawn from thin evidence. It is consistent across sources, which is the main reason to believe it.

## 1. The five kinds of coding round

| Round | What happens | Seen at |
|---|---|---|
| **Timed online test** | A HackerRank-style platform, auto-graded. Usually SQL plus one Python problem plus theory questions. | QuintoAndar (one SQL query, one Python algorithm, ML theory). Nubank ("AI test" on a platform, Apr 2026). QuantumBlack (36 multiple-choice questions in under 90 minutes on statistics, SQL and Python with sklearn and pandas, Feb 2023, or a 90 minute coding test). iFood internship (four questions). |
| **Live SQL** | You write queries while someone watches. | Nubank analytics roles ("Live programming SQL"; one candidate reports six very long questions in about 45 minutes, May 2026). QuantumBlack data engineer (one SQL and three dataframe questions, live, Mar 2026). |
| **Live Python** | A function on lists, dicts or strings, sometimes a classic algorithm. | Nubank ("live coding de algoritmo", Apr 2026). QuintoAndar ("Coding and SQL" on an online IDE). |
| **Live data or ML coding** | pandas manipulation, a model fitted on given data, or a piece of ML written by hand. | Nubank ("live coding de IA"; "code review em pandas ou pyspark"). QuintoAndar ("implement cross-validation", 2024). QuantumBlack (pandas feature engineering; "train a model and return predictions"). |
| **Take-home case, then a presentation** | Several days, then you defend it. | Mercado Livre (build a model, "not very different from a Kaggle task"). iFood. Nubank analytics (one week, about six hours of work). QuintoAndar. Luizalabs. |

A sixth kind, the rapid-fire concept round (bias and variance, bagging and boosting, imputation), is very common and needs no coding.

## 2. What each round asks you to write

### SQL

This is the part that appears in nearly every source, and it is the part most often auto-graded.

**Level.** The iFood question list has 18 SQL items: 3 easy, 11 medium, 4 hard. Other sources name the same topics. The bar is medium.

| Tier | Topic | Typical question |
|---|---|---|
| Must | Filter, group, aggregate, `HAVING` | Monthly customer report |
| Must | Joins, including rows with no match | Neighbourhoods with no users |
| Must | Top N within each group | Top three salaries per department |
| Must | "Latest row per something" | Each customer's last transaction |
| Must | Subqueries or CTEs | Second-highest salary |
| Must | Window functions for ranking and for the previous row | Rank within a group, change since last month |
| Should | Dates, grouping by month | Monthly sales growth by category |
| Should | Running totals and moving averages | Rolling bank transactions |
| Should | `CASE WHEN` for buckets and conditional counts | Comments histogram |
| Rare, hard | Streaks, overlaps, self-joins for pairs, first-touch attribution | Longest streak of daily use |

One practical point from a QuantumBlack candidate: practise SQL "without relying on visible input/output tables". On some platforms you cannot see the data.

### Plain Python

**Level.** Easy to medium. Coaches and candidates agree that heavy algorithms are unlikely for data science roles, with Nubank as the possible exception (one candidate called its algorithm round hard).

| Tier | Topic | Typical question |
|---|---|---|
| Must | Counting and grouping with a dict | Top-k items, average per customer |
| Must | Sorting with a key, and ties | Rank by count then name |
| Must | Strings: split, join, slices | Bigrams, an n-gram dictionary |
| Must | A function with edge cases handled, and a few tests you write yourself | Any of the above |
| Must | Saying the cost in Big-O terms | "This is one pass, so linear" |
| Should | Sets, tuples, list comprehensions | De-duplicate, pair things up |
| Should | A loop that carries state | Sessionise events, merge overlapping intervals |
| Should | Two pointers, binary search | Merge two sorted lists, search a rotated sorted array |
| Should | A simple class | QuintoAndar lists object-oriented design |
| Recognise | Stacks, queues, trees, graphs | QuintoAndar lists them. No report shows one being asked of a data scientist. |

### pandas and ML code

| Tier | Topic | Typical question |
|---|---|---|
| Must | `groupby` with aggregation, `merge`, sorting, new columns | Feature engineering on a business table |
| Must | Missing values | Find, drop, fill, and say why |
| Must | Fit, predict and evaluate with sklearn | "Train a model and return predictions" |
| Should | Something written by hand | Cross-validation, a metric such as AUC, a train and test split |
| Should | Building a training dataset with SQL | QuintoAndar: "query data using best practices to build a training dataset" |
| Should | Reading and criticising someone else's pandas | Nubank's code review round |
| Should | A function that applies a model to a business rule or formats LLM output | QuintoAndar names both |

## 3. Rules of the room

- **AI assistants.** It varies, and the differences are large.
  - QuintoAndar's published policy: not allowed in live technical interviews, allowed with caution on take-home cases provided you "fully understand, explain, and defend your solution".
  - iFood, in your own round: an outside assistant was allowed and the prompt itself was evaluated.
  - A QuantumBlack candidate: Googling allowed, with the screen shared.
  - Most banks: no AI, per the earlier brief.
- **What is graded in live rounds.** Reasoning aloud, clear structure, trade-offs, "solve, then optimize" (QuintoAndar), and testing your own code. One Brazilian guide puts it this way: getting it wrong does not eliminate you, freezing without trying does.
- **What is graded in online tests.** Only whether the hidden test cases pass. Reasoning earns nothing there, and the clock is tight.
- **Time pressure is real in the tests.** 36 questions in 90 minutes, or six long SQL questions in 45. One QuantumBlack candidate failed simply by running out of time and advised practising the platform's interface first.
- **Language.** Python and SQL throughout. PySpark shows up at Nubank and QuantumBlack as an alternative to pandas, and one São Paulo candidate was told SQL and got Spark and pandas.

## 4. The pass bar

If you can do these from a blank page, without AI, explaining as you go, you can pass the coding part of most of the rounds above. Times are for a live round.

**SQL, about 10 minutes each**

1. Count and average per group, keeping only groups above a threshold.
2. Join two tables and aggregate by a column from the second one.
3. Find rows in one table with no match in the other.
4. Top three per group.
5. Each customer's most recent order.
6. Month-by-month totals with the change from the previous month.

**Plain Python, about 15 minutes each**

7. Top-k most common items, ties broken alphabetically.
8. Average per key, ignoring missing values.
9. Split a sentence into bigrams and count them.
10. Merge two sorted lists.
11. Group timestamps into sessions.
12. Write three tests for any of the above and state its Big-O.

**pandas and ML, about 15 to 20 minutes each**

13. Load a table, clean missing values, add two engineered columns.
14. `groupby` and `merge` to answer a business question.
15. Fit a model with sklearn, predict, and report a sensible metric.
16. Write k-fold cross-validation by hand.
17. Write one metric by hand (AUC or KS, which suits your credit background).

Your existing mocks already contain versions of 7, 8, 11 and several of the pandas and ML items.

## 5. What this means for the course

The course as designed so far (`02-panorama-and-openings.md`) gets you to the foot of this bar. It does not get you over it.

**Already covered by the first course:** items 1 and 2 in SQL, the dict-counting core of 7 and 8 in Python, and the pandas basics behind 14.

**Missing, and needed to pass:**

| Strand | Missing thought | How it fits the method |
|---|---|---|
| SQL | A query's result can be queried again (subqueries, CTEs) | This is "a table goes in, a table comes out" used a second time. It should cost very little. |
| SQL | A number about the pile, written next to each row, without collapsing the rows (window functions) | The one truly new thought. It unlocks top N per group, latest per customer, previous row and running totals, which is four of the six SQL pass-bar items. |
| SQL | Rows with no match | A second thought inside "look things up in another table". |
| SQL | Dates and `CASE WHEN` | Vocabulary on top of existing movements. |
| Python | Sorting with a key | Small. |
| Python | Strings as lists of pieces | Small, and it re-uses lists. |
| Python | A loop that carries state from one item to the next | An extension of "keep a running result". |
| Python | Writing your own tests and saying the cost | Habits, cued from the start. |
| pandas and ML | Everything beyond the basics | Mostly vocabulary on top of SQL thoughts, plus the sklearn fit and predict routine. |

**Two things the method does not provide and the rounds demand:**

1. **Speed.** The method deliberately has no timer. The online tests are races. Speed has to come afterwards, from timed practice, which is what the existing mocks and the live coding gym are for.
2. **Working blind.** Auto-graded tests give no partial credit, and some hide the data. A final stage should include writing against tables you cannot see and getting exact output right.

**Suggested shape, in three stages:**

1. **Foundation.** The course as designed: SQL, Python, pandas basics. Goal: you can always write something that runs.
2. **Interview level.** A second layer woven on top, in the same method, covering the "missing" table above. Window functions are the centrepiece.
3. **Speed and exams.** The 17 pass-bar tasks as timed drills, in the gym you already have.

**Where to put effort first.** Medium SQL with window functions. It appears in almost every source, it is the most likely thing to be auto-graded, and it is the shortest distance from where the first course ends.

## 6. Which roles this applies to

Clarified by the person on 20 Nov 2026: companies are saying "we don't know where to place you yet, so take the coding round first and we'll figure it out later". The coding round is therefore a generic gate that comes before any decision about the role, including for strategy and AI product positions. It cannot be skipped by aiming at less technical roles.

Consequences for the course:

- The target is the full pass bar in section 4, not just the foundation.
- Because the round is not tied to a role, expect the generic versions: a timed online test and a live round in SQL and Python. Role-specific rounds such as iFood's ML systems round are the exception.
- All three stages in section 5 are in scope.

## Sources

Official
- [QuintoAndar: Data Scientist interview guide](https://carreiras.quintoandar.com.br/x/data-scientist/?lang=en)
- [QuintoAndar: using AI in the recruiting process](https://carreiras.quintoandar.com.br/a-guide-to-using-ai-in-the-recruiting-process/?lang=en)
- [QuintoAndar: selection process](https://carreiras.quintoandar.com.br/nosso-processo-seletivo-en/?lang=en)

First-hand candidate reports (Glassdoor)
- [Nubank Data Scientist](https://www.glassdoor.com/Interview/Nubank-Data-Scientist-Interview-Questions-EI_IE827975.0,6_KO7,21.htm)
- [Nubank Analytics Engineer](https://www.glassdoor.com/Interview/Nubank-Analytics-Engineer-Interview-Questions-EI_IE827975.0,6_KO7,25.htm)
- [QuintoAndar Cientista de Dados](https://www.glassdoor.co.in/Interview/QuintoAndar-Interview-E1161693-RVW48876918.htm)
- [Mercado Livre Data Scientist](https://www.glassdoor.co.in/Interview/Mercado-Livre-Interview-E2372230-RVW96292108.htm)
- [Stone Cientista de Dados](https://www.glassdoor.ca/Interview/Stone-Interview-E1093539-RVW87839561.htm)
- [QuantumBlack Data Engineer](https://www.glassdoor.co.in/Interview/QuantumBlack-Interview-E1508182-RVW78738122.htm), [Principal Data Scientist](https://www.glassdoor.ca/Interview/QuantumBlack-Interview-E1508182-RVW67569594.htm), [Data Science Intern](https://www.glassdoor.co.nz/Interview/QuantumBlack-Interview-E1508182-RVW61598830.htm)

Aggregators, prep sites and blogs (lower confidence)
- [Interview Query: iFood data scientist](https://www.interviewquery.com/interview-guides/ifoodds-data-scientist)
- [PrepLounge: QuantumBlack HackerRank thread (Mar 2026)](https://www.preplounge.com/consulting-forum/quantumblack-data-science-hackerrank-assessment-24580)
- [Hacking the Case Interview: QuantumBlack](https://www.hackingthecaseinterview.com/pages/mckinsey-quantumblack-interview)
- [CleverPrep: McKinsey data scientist](https://www.cleverprep.com/companies/mckinsey/data-scientist)
- [JobRise: entrevista de data scientist (Aug 2026)](https://jobrise.io/pt/blog/entrevista-data-scientist-perguntas-respostas-2026/)
- [JobRise: PicPay processo seletivo](https://jobrise.io/pt/blog/picpay-vagas-tech-2026-processo-seletivo/)
- [Serasa Experian: como se preparar para entrevista técnica](https://www.serasaexperian.com.br/carreiras/blog-carreiras/como-se-preparar-para-entrevista-tecnica/)
- [Somos Tera: como conquistar vaga de cientista de dados (2021)](https://somostera.com/blog/como-conquistar-vaga-de-cientista-de-dados)
- [Dataford: Stefanini Brasil data analyst](https://dataford.io/interview-guides/stefanini-brasil/data-analyst)
- [Revarta: Nubank data scientist](https://www.revarta.com/interview/companies/nubank/roles/data-scientist), [OphyAI: Nubank](https://ophyai.com/blog/company-guides/nubank-interview-guide), [OphyAI: Mercado Libre](https://ophyai.com/blog/company-guides/mercado-libre-interview-guide)

Could not be read: Itaú Unibanco's Glassdoor interview pages and the later pages of Nubank's.
