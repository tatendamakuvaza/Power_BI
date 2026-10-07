# Glossary — accounting and Power BI, in one place

Written for an accountant learning Power BI. Where a term has a different meaning in the two worlds,
both are given.

---

## Accounting terms used in the course

| Term | Meaning |
|---|---|
| **Accrual** | An expense or income recognised before cash moves; must be reversed or settled in the next period |
| **Ageing bucket** | Classification of receivables/payables by days past due (Current, 1–30, 31–60, 61–90, 91–180, Over 180) |
| **Amount at risk** | The full value of transactions exhibiting an exception — not yet a proven loss |
| **Benford's Law** | The expected distribution of first digits (30.1% begin with 1, 17.6% with 2, … 4.6% with 9) in unconstrained natural data |
| **Closing balance** | Balance at the end of a period; opening + movement (semi-additive — never summed across time) |
| **Control account** | A GL account summing a sub-ledger (trade receivables, trade payables) |
| **Direct labour** | Labour applied directly to production; sits in cost of sales, not overheads |
| **DPO / DSO / DIO** | Days payable / receivable / inventory outstanding — working-capital efficiency ratios |
| **Ghost vendor** | A supplier that exists only on paper, often controlled by an employee |
| **IESBA code** | The international ethics code for professional accountants (integrity, objectivity, competence, confidentiality, professional behaviour) |
| **Journal entry testing** | Analytically testing the whole journal population for characteristics associated with fraud (manual, round, backdated, unusual users/accounts) |
| **Materiality** | The threshold above which a misstatement would change a user's decision |
| **Overhead absorption** | Recovering indirect production costs into cost of sales via a recovery rate |
| **Provisions vs accruals** | Provisions are uncertain in timing/amount; accruals are certain but unbilled |
| **Suspense account** | Holding account for unallocated amounts; a growing balance is a control failure |
| **Segregation of duties** | No single person should be able to both create and conceal a transaction (e.g. set up a vendor *and* approve its payment) |
| **Structuring / splitting** | Dividing a transaction to stay below an approval or reporting threshold |
| **Three-way match** | Purchase order ↔ goods received note ↔ supplier invoice agreement before payment |
| **Value at risk vs loss** | What could be improper vs what is supported by evidence as improper |
| **VAT input / output** | VAT paid on purchases (claimable) vs charged on sales (payable) |

## Power BI terms

| Term | Meaning | Accounting analogy |
|---|---|---|
| **Power Query (M)** | The data preparation engine; records every transformation as a reproducible recipe | Bookkeeping / coding |
| **Applied steps** | The ordered list of transformations; the audit trail of your data prep | Audit trail of edits |
| **Query folding** | Pushing transformations back to the source database as one query | Working on the ledger directly rather than exporting |
| **Data model** | Tables plus relationships | The ledger structure / trial balance |
| **Star schema** | Fact tables (transactions) surrounded by dimension tables (master data) | Journals + master files |
| **Fact table** | Transaction grain, additive numbers | Sub-ledger / journal |
| **Dimension table** | Descriptive attributes; filters the facts | Chart of accounts, vendor master |
| **Grain** | What one row represents — must be stated and never mixed | Level of detail |
| **Measure** | A DAX calculation evaluated in the filter context | A calculated column in a management pack |
| **Calculated column** | Row-by-row value stored in the table | A helper column in Excel |
| **Filter context** | The set of rows visible to a calculation in a visual | Which slice of the ledger you are reporting |
| **Row context** | The current row during iteration | The row you are on in Excel |
| **Context transition** | Row context becoming filter context inside `CALCULATE` | Turning "this row" into "all rows like this row" |
| **CALCULATE** | The function that modifies filter context | Applying a filter to a report |
| **Iterator (SUMX, AVERAGEX)** | Evaluates an expression row by row then aggregates | Summing a helper column you calculated row by row |
| **Semi-additive** | Additive across some dimensions, not time (balances) | A balance you cannot "add up" over months |
| **Time intelligence** | Functions using a marked date table (`TOTALYTD`, `SAMEPERIODLASTYEAR`) | Prior-period and to-date columns in a pack |
| **`USERELATIONSHIP`** | Activates an inactive relationship inside a measure | Choosing which user field (preparer vs approver) to analyse |
| **`TREATAS`** | Applies values from one table as a filter on another (no relationship) | Matching two lists that are not linked in the ledger |
| **RLS (row-level security)** | Restricts data by user/role | Restricting a branch manager to their branch |
| **Drillthrough** | Right-click a number to see the detail behind it | Drilling from the TB to the ledger lines |
| **Bookmark** | A saved view state | A saved report selection |
| **Field parameter** | Lets the user switch the measure/dimension on an axis | Choosing which column the pack shows |
| **Dataset (semantic model)** | The published model in the Service | The shared reporting database |
| **App** | A packaged bundle of reports for a client's team | The delivered management pack |
| **RLS / workspace roles** | Who can see what | Report distribution list |

## Analytics and ML terms

| Term | Meaning |
|---|---|
| **Baseline** | The naive prediction (e.g. majority class) that any model must beat |
| **Classification** | Predicting a category (churn / no churn) |
| **Regression** | Predicting a number (next month's sales) |
| **Feature** | An input variable used by a model |
| **Label / target** | The outcome being predicted |
| **Leakage** | Using information not available at prediction time |
| **Overfitting** | Fitting noise in the training data; performs well there, badly on new data |
| **Accuracy** | Share of predictions that are correct (misleading with unbalanced classes) |
| **Precision** | Of those flagged, the share that are real |
| **Recall (sensitivity)** | Of the real cases, the share that were flagged |
| **Specificity** | Of the negative cases, the share correctly left alone |
| **AUC / lift** | Ranking quality; how much better than random the model sorts a list |
| **Confusion matrix** | TP / TN / FP / FN counts behind the metrics |
| **Explainability** | Being able to say why the model produced a score |
| **Drift** | The data or relationship changing over time, degrading the model |
| **Anomaly detection** | Finding observations that do not fit the learned pattern |
