# Module Quizzes — 60 questions

Five questions per module. Answers at the end of the file — mark yourself honestly; a wrong answer here
is cheaper than a wrong number in a client report.

---

## Module 1 — Getting started

1. What is the difference between Power BI **Desktop** and the Power BI **Service**?
2. Why should auto date/time be **off** in a finance model?
3. In which view do you inspect imported rows column by column?
4. A client asks for "a dashboard". Name two things you must clarify before accepting the request.
5. What does publishing to the Service actually copy — the data, the report, or both?

## Module 2 — Power Query

6. What is the practical difference between editing data in Excel and cleaning it in Power Query?
7. Why must account codes be stored as **text**, never as whole numbers?
8. A client's date column contains `03/04/2021`. What must you set before converting it, and why?
9. What is the correct handling for duplicate rows in a forensic engagement?
10. You need to budget across 12 monthly columns. Which transformation gets the data into a usable shape?

## Module 3 — Data modelling

11. State the grain of `FactGLJournal` and of `FactTrialBalance`.
12. Why can a single flat table not serve a budget-vs-actual report properly?
13. `FactGLJournal` has `PreparedBy` and `ApprovedBy`. Name two ways of handling this in the model.
14. What must be true about `DimDate` before `TOTALYTD()` works correctly?
15. The orphan-key test returns 42. What does that mean and what do you do?

## Module 4 — DAX fundamentals

16. When do you use a calculated column instead of a measure?
17. Explain filter context in one sentence, using a matrix as the example.
18. Revenue is stored as a credit balance (negative). Why is `Gross Profit = Revenue + CostOfSales`
    correct on signed amounts?
19. Why is `DIVIDE()` preferred to the `/` operator in client reports?
20. What does `CALCULATE` do to an existing filter on the column you filter?

## Module 5 — Advanced DAX

21. Classify each as additive, semi-additive or non-additive: revenue, accounts receivable balance,
    gross margin %.
22. Write the pattern for a closing balance that respects the period selected in the visual.
23. Why is `Revenue Same Period LY` preferable to a plain prior-year comparison in a part-month close?
24. What is context transition, and where does it bite in a duplicate-detection measure?
25. Your model has 13,929 GL lines; a client's has 5 million. Which two habits keep measures fast?

## Module 6 — Financial statement design

26. Why should statement line order, sign and subtotals live in a table rather than in 40 measures?
27. `Assets − (Liabilities + Equity)` equals the current year's result. Is that an error? Explain.
28. What is the correct sign convention for the model and for presentation, and where do they differ?
29. Describe how you would reconcile a cash flow statement built in Power BI to the movement in cash.
30. Name four control checks that belong on the close-pack page.

## Module 7 — Visualisation and design

31. State the rule that decides whether a visual belongs on a page.
32. What should the title of a chart contain, and why?
33. When is a gauge acceptable, and what should you use instead in most cases?
34. What is drillthrough, and why do auditors value it more than any other feature?
35. Name three accessibility requirements for a client report.

## Module 8 — Analytics and KPIs

36. What is the difference between descriptive and diagnostic analytics? Give an example of each.
37. Why must gross margin % never be computed as the average of monthly percentages?
38. What does a Pareto chart of vendor spend tell you, and what does it not tell you?
39. A journal line has a Z-score of 4.2. What have you found — and what have you not found?
40. Write the three lines of a recommendation block and state which one carries the fee.

## Module 9 — Forensic analytics

41. Name the five elements of a test design.
42. Why is removing duplicates in Power Query the wrong first step in a forensic engagement?
43. How would you test for a ghost vendor, and what evidence converts suspicion into a finding?
44. What does a spike in payments just below a $10,000 approval limit indicate?
45. State two circumstances where Benford's Law must **not** be applied, and why.

## Module 10 — Investigation

46. What must be recorded before any file is analysed, and why?
47. Distinguish "total value", "value at risk" and "estimated loss" for a duplicate-payment finding.
48. Why must a report separate fact, inference and opinion?
49. A client asks you to name the employee you suspect. What do you say?
50. Name three elements of a remediation plan that make it credible.

## Module 11 — Machine learning and AI

51. What is the first thing you build and report before any model? Why?
52. Define feature leakage and give one example from an accounting dataset.
53. In a forensic screening model, would you prioritise precision or recall? Explain.
54. Why does a model report need a version, a training date and its accuracy?
55. Name three governance rules for using generative AI with client data.

## Module 12 — Advisory practice

56. What distinguishes a productised service from a general offer?
57. Why should every build proposal carry a retainer line?
58. Name the three pricing models and the situation each suits best.
59. What must an engagement letter say about client data, and why does it protect both parties?
60. What are the three questions every client asks, and how do you answer them?

---

## Answer guide

1. Desktop builds models and reports offline; the Service publishes, shares, schedules refresh and
   supports apps/dashboards. Desktop is where you work; the Service is where the client consumes.
2. It creates a hidden date table per date column, bloating the model and competing with your proper
   date table, which breaks time intelligence subtly.
3. **Table view** (and DAX query view for queries).
4. Whether they mean a report or a pinned dashboard, and who will consume it (licence/sharing model).
5. Both — a copy of the model (dataset) and the report is uploaded to your workspace.

6. Power Query records a repeatable, auditable recipe (M code); Excel edits are manual and
   non-reproducible — and in forensic work, non-reproducible means inadmissible.
7. Leading zeros, alphanumeric codes and long codes are lost or corrupted when converted to numbers,
   and joins to text-keyed fact tables silently fail.
8. The **locale** (e.g. en-GB vs en-US) — the same string means March 4 or April 3 depending on the
   source convention.
9. Do not remove them: flag them. Duplicates are the evidence; removals change the population and
   destroy traceability.
10. **Unpivot** the month columns (Unpivot Other Columns), giving one row per month.

11. `FactGLJournal` — one row per ledger line; `FactTrialBalance` — one row per account per month.
12. It cannot hold two different grains (transactions and budget), cannot carry hierarchies, and
    repeats attribute data, so comparisons and slicing break or mis-state.
13. (a) One active + one inactive relationship with `USERELATIONSHIP`, or (b) a duplicated
    `DimUser_Approver` dimension — preferred on client work.
14. It must be contiguous, complete (no gaps), marked as a date table, and on the one side of the
    relationship; auto date/time off.
15. 42 GL lines have account codes that do not exist in `DimAccount`; they will not appear in
    statement analysis. Investigate, correct or escalate before reporting anything.

16. When the value must be used on an axis, a slicer, a sort, or in a relationship (measures otherwise).
17. The set of rows that are visible for a measure's evaluation, determined by the visual's rows,
    columns, slicers and page filters.
18. Because expenses are stored as positive debits and revenue as negative credits; adding the negative
    cost of sales reduces revenue correctly.
19. It returns blank rather than an error when the denominator is zero — a client-facing report must
    never show `#DIV/0!`.
20. It **replaces** the existing filter on that column (rather than adding to it).

21. Revenue — additive; AR balance — semi-additive; gross margin % — non-additive.
22. `VAR LastDate = MAX ( DimDate[Date] ) RETURN CALCULATE ( [GL Amount Signed], DimDate[Date] <= LastDate )`.
23. Because a partial month is compared with a full month last year, overstating or understating the
    variance; restrict the prior period to the same day cut-off.
24. Row context becoming filter context when wrapped in `CALCULATE`/iterators; it is what makes
    "count rows matching this row's vendor and amount" work — and what makes it O(n²) if misused.
25. Aggregate before iterating, and filter columns/dimensions rather than scanning fact tables.

26. Because the structure (order, subtotals, signs, formatting) becomes data — one change updates every
    statement, and the model stays readable and reviewable.
27. No error: the ledger closes prior-year results to retained earnings but the current year's result is
    still in the P&L, so the check equals the current-year result. Show it as "retained earnings
    including current year result" and the check goes to zero.
28. Ledger convention internally (debits +, credits −); presentation measures flip signs so a human
    reads revenue and expenses as positive magnitudes.
29. Classify every cash movement by counterparty, build the waterfall, and reconcile its closing figure
    to the movement in the cash accounts, and to the opening plus movement = closing identity.
30. Debits = credits; BS check = 0; P&L result ties to retained earnings movement; orphan keys = 0;
    unbalanced journals = 0; suspense balance disclosed; unreconciled bank items disclosed. (Any four.)

31. It must answer a question someone actually asked — if you cannot write the question, do not build it.
32. A sentence containing the number and the comparison ("Revenue $10.54m, 12.2% below prior year") —
    so the reader gets the finding without interpreting the chart.
33. Almost never; use a KPI card or bullet chart with a target line.
34. Right-click a number and land on the transactions behind it — it converts a report into evidence.
35. Font size ≥ 10 pt; not relying on colour alone; alt text; adequate contrast. (Any three.)

36. Descriptive states what happened (revenue trend); diagnostic explains why (price/volume/mix
    decomposition of a variance).
37. It weights small months equally; margin must be computed from total gross profit ÷ total revenue.
38. It shows concentration (how few vendors drive most spend) and therefore where control and
    relationship risk sits; it does not tell you whether those vendors are legitimate or the prices fair.
39. You have found a statistical outlier worth asking about; you have not found fraud, error or intent —
    that requires corroboration.
40. Finding / Impact / Action; the **Impact** line (quantified in money, days or risk) is what carries
    the fee.

41. Population, assertion, expectation, exception, follow-up.
42. Because the duplicates are the evidence; you flag them and keep both rows so the population stays
    complete and traceable.
43. Test for vendors that are employee-linked (bank account or name match, no tax clearance, created
    shortly before first payment, single preparer); convert to a finding by obtaining company registry
    records, bank confirmation or a conflict declaration.
44. Threshold avoidance/structuring: deliberately keeping payments under the approval limit to bypass
    authorisation — corroborate by inspecting the invoices and the approvals.
45. Any two of: data with built-in boundaries (VAT multiples, fixed fees, salary bands); populations
    under ~1,000 items; assigned/sequential numbers; amounts under ~$10 or rounded to hundreds —
    Benford assumes an unconstrained, natural distribution.

46. The original files' hash values, extraction date/time, source system and provider — so the evidence
    is provably unaltered and the analysis is reproducible.
47. Total value = everything that moved; value at risk = the improper portion on conservative
    assumptions; estimated loss = the amount supported by documents (here, the duplicate half).
48. So the reader — and ultimately a court or regulator — knows what is established, what is inferred
    and what is your professional judgement; opinion dressed as fact destroys credibility.
49. You do not name anyone. You report the pattern, the evidence and the control failure, and recommend
    that the company's legal advisers or the appropriate authority take any further step.
50. Specific actions, a named owner and a date — plus the cost and the control that prevents recurrence.

51. The **baseline** (e.g. "always predict the majority class"): without it, accuracy is meaningless.
52. Using information not available at prediction time; e.g. predicting late payment using the eventual
    payment date, or churn using next year's purchases.
53. Recall — you want to catch the exceptions; false positives are acceptable because a human reviews
    each flag before action.
54. So the client can judge whether the model is current, how it performed, and when to retrain.
55. Written permission and a lawful basis for client data; no client-identifiable data in public models;
    human review of every AI-generated number before issue. (Also acceptable: disclosure of AI use,
    retention limits, vendor/dpa review.)

56. A named product with a defined scope, deliverable, price, timeline and "not included" list.
57. Because the build is a one-off project and the retainer is repeatable revenue and the client's
    ongoing value — and it is where the analytics actually change behaviour.
58. Fixed fee (defined scope), time-based (investigations, discovery), retainer (recurring reporting),
    with success/contingency only where permitted.
59. Data handling: lawful basis, access restrictions, storage, retention, destruction — it protects the
    client's data and caps your liability for misuse.
60. How long, how much, and how do I know it is right — answered with a timeline, a fee, and your
    quality-control and reconciliation process.
