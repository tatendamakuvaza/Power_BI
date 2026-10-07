# Module 3 — Data Modelling & the Star Schema

**Time:** 8 hours · **Lab:** [Lab 03](../labs/Lab_Index.md#lab-03--model-the-mhondoro-warehouse) · **Prerequisite:** Module 2

> Every frustrating Power BI problem ("my filter does nothing", "my total is wrong", "YTD doubles
> when I add a column") is a **data-model** problem, not a DAX problem. Get this module right and
> the rest of the course becomes easy.

---

## 3.1 Why accountants should care about a star schema

A star schema is just **the accounting equation applied to data**:

> One set of **facts** (transactions) captured once, described by **dimensions** (who, what, when,
> where) that are shared and consistent.

| Accounting concept | Star schema equivalent |
|---|---|
| Journal / sub-ledger | **Fact table** — one row per transaction line, numeric, additive |
| Chart of accounts | **Dimension** (`DimAccount`) |
| Cost centre list, customer master, vendor master | **Dimensions** |
| Calendar / period table | **Date dimension** |
| Control totals | **Measures** that sum facts and tie to the TB |
| Reconciliation | Relationships that must not duplicate or lose rows |

If your model duplicates revenue, you have effectively posted the same invoice twice — and your
financial statements are wrong. That is why this module is non-negotiable.

---

## 3.2 Fact vs dimension, decided in 30 seconds

Ask: **what am I counting, and can I add it up?**

| Question | Fact | Dimension |
|---|---|---|
| Is it a number I can sum (amount, units, hours)? | Yes | |
| Is it a list of attributes (name, code, category)? | | Yes |
| Does it change over time (a new transaction each month)? | Yes | |
| Is it a "master" that describes many transactions? | | Yes |
| Would it be wrong to add it up (credit limit, tax rate, exchange rate)? | Never sum → | Yes |

**The classic error:** putting `CreditLimitUSD` in a fact table and summing it. Credit limits are
dimension attributes; only `SUM` what is genuinely additive.

---

## 3.3 The Mhondoro model

```
                    DimDate
                       │
                       │ 1:*
   DimAccount ──┐      │
                │      │
   DimCostCentre ┼── FactGLJournal ──── DimVendor      (line-level detail, 13,929 rows)
   DimCustomer ──┘   (13,929 rows) ─── DimUser
                                        (PreparedBy / ApprovedBy = role-playing)
   FactTrialBalance ── DimAccount, DimDate
   FactARAgeing     ── DimCustomer, DimDate
   FactAPInvoices   ── DimVendor, DimDate
   FactSalesOrders  ── DimCustomer, DimDate
   FactBudget       ── DimAccount, DimCostCentre, DimDate
   FactBankTransactions ── DimDate (join by date or a bank-transaction type dimension)
   FactExpenseClaims ── DimEmployee, DimDate
   FactFixedAssets  ── DimCostCentre, DimDate (acquisition), DimAccount
   DimEmployee ── (used for ghost-vendor / payroll tests)
   DimFXRate ── DimDate
```

Rules this model obeys:

1. **Every fact joins to dimensions on a single key.** No fact-to-fact joins.
2. **Filters flow one way:** dimension → fact. One-to-many, single direction, by default.
3. **Grain is explicit.** `FactGLJournal` is *one row per ledger line*. `FactTrialBalance` is
   *one row per account per month*. Never mix grains in one table.
4. **Dimensions are shared.** `DimDate` filters every fact; that is what makes cross-fact comparison
   possible.

---

## 3.4 Building it: the practical steps

1. **Get Data ▸ Excel workbook** → `data/xlsx/Mhondoro_Accounting_Data.xlsx` → select all tables →
   Transform Data.
2. In Power Query, for each table:
   - Set the key column types. **Codes are text** (`AccountCode`, `CostCentreCode`, `VendorID`, `CustomerID`,
     `Period`); dates are date; amounts are decimal number.
   - Remove the answer-key column `AnomalyLabel` from `FactGLJournal` (Module 10 reveals it).
3. **Close & Apply.**
4. **Model view (⧉).** Drag `DimAccount[AccountCode]` onto `FactGLJournal[AccountCode]`.
   Power BI auto-detects one-to-many. Verify the cardinality in the relationship's properties.
5. Create the rest of the relationships. Then check: **every dimension has a relationship, every fact
   is filtered by the dimensions it should be.**
6. **Mark as date table:** right-click `DimDate` ▸ *Mark as date table* ▸ `Date`. Do this before writing
   any time intelligence (Module 5).
7. **Sort MonthName by MonthNumber:** select `MonthName` ▸ *Column tools ▸ Sort by column ▸ MonthNumber*.

### Relationship settings, and when to change them

| Setting | Default | Change it when |
|---|---|---|
| Cardinality | One-to-many | You have a true 1:1 (rare) or many-to-many (design red flag) |
| Cross-filter direction | Single | You need bidirectional — usually to enable a slicer on a fact. Prefer a bridge/dimension instead |
| Active | Yes | Role-playing dimensions: one active, the others used via `USERELATIONSHIP` |
| Assume referential integrity | Off | Turn on for speed *after* you have proven no orphan keys |

---

## 3.5 Role-playing dimensions (the accounting case you will meet constantly)

`FactGLJournal` has **two** user keys: `PreparedBy` and `ApprovedBy`. Both point at `DimUser`.
Power BI allows only one active relationship. Solution:

- `DimUser[UserID] → FactGLJournal[PreparedBy]` — **active**.
- `DimUser[UserID] → FactGLJournal[ApprovedBy]` — **inactive** (dotted line).

Then measure the approval side with `USERELATIONSHIP`:

```dax
Approved Amount =
CALCULATE ( [GL Amount Abs], USERELATIONSHIP ( DimUser[UserID], FactGLJournal[ApprovedBy] ) )
```

For a *better* experience, add a second, marked-up copy of the dimension — `DimUser_Approver`
(a DAX calculated table or an M reference query, `DimUser` with `UserID` renamed `ApproverID`).
Two dimensions, two slicers, no `USERELATIONSHIP` gymnastics. On a real engagement, prefer the
duplicate dimension: fewer surprises in the hands of a client.

---

## 3.6 The date table (why you must build your own)

**Turn off Auto date/time** (Module 1) and build `DimDate` properly. Requirements:

- One row per day, contiguous, covering the earliest to the latest transaction date — plus a year
  either side for comparatives.
- A **date** column typed as Date (this is the one the engine treats specially).
- Fiscal columns (`FiscalYear`, `FiscalPeriod`) so you can slice by financial year.
- Flags used by accountants: `IsMonthEnd`, `IsWeekend`, `IsCurrentFY`.
- **Mark as date table** so `SAMEPERIODLASTYEAR`, `DATESYTD` etc. work correctly.

Our `DimDate` already has all of this (1,461 rows, 2023–2026). Add these for real engagements:

```dax
-- Add to DimDate as calculated columns
Days From Period End = DimDate[FiscalPeriodEnd] - DimDate[Date]      -- day index inside the month
Working Day Flag = IF ( DimDate[IsWeekend] = "Yes", "Non-working", "Working" )
Post Close Flag  = IF ( DimDate[Days From Period End] < -5, "After close", "Within close" )
```

Why it matters: the *weekend/after-hours* forensic test in Module 9 is a join between
`FactGLJournal[EnteredOn]` and the calendar. Without a proper date table, you cannot run it.

---

## 3.7 Grain, aggregation and the "one fact, many analyses" principle

The temptation is to build one wide table per report (a "Sales Report table", a "Payroll Report
table"). Resist it. Instead:

| Grain | Table | Feeds |
|---|---|---|
| Ledger line | `FactGLJournal` | P&L, BS, forensic tests, cost-centre reporting |
| Month × account | `FactTrialBalance` | TB movement views, balance validation |
| Invoice | `FactARAgeing`, `FactAPInvoices` | Ageing, DSO, 3-way match |
| Order | `FactSalesOrders` | Margin, product, rep analysis |
| Month × account × CC | `FactBudget` | Variance |

The same dimensions filter all of them, so a single `DimDate` slicer drives the P&L, the ageing and
the budget comparison at once. That is the payoff.

---

## 3.8 Model quality checklist (run before you write a single measure)

- [ ] Every fact table's grain can be stated in one sentence
- [ ] Every relationship is one-to-many, dimension → fact, single direction
- [ ] No circular relationships; no bidirectional filters unless documented and justified
- [ ] `DimDate` marked as a date table; `MonthName` sorted by `MonthNumber`
- [ ] Account codes, cost-centre codes, vendor/customer IDs are **text** in both sides of the join
- [ ] No orphan rows: every fact key exists in its dimension (test below)
- [ ] Formatting set on columns and measures (`$#,##0.00`, `0.0%`, `#,##0`)
- [ ] Every measure and table has a description
- [ ] You can explain the model on one page — draw it and keep it in the working papers

### Orphan-key test (do this on every engagement)

```dax
-- Put on a card in a hidden "Data Quality" page
GL Lines With Unknown Account =
COUNTROWS (
    FILTER (
        FactGLJournal,
        NOT FactGLJournal[AccountCode] IN VALUES ( DimAccount[AccountCode] )
    )
)
```

If this returns anything other than 0 (blank is fine), **stop and fix it**. Unmatched ledger lines
are the number one cause of "the dashboard doesn't tie to the trial balance".

---

## 3.9 Star vs snowflake vs single table: choosing deliberately

| Design | Use when | Warning |
|---|---|---|
| **Star** (dims joined only to facts) | Default for everything | — |
| **Snowflake** (dim joined to dim) | The client genuinely has a hierarchy you cannot flatten | Extra hops confuse filter direction and slow the model |
| **Single wide flat table** | A 20-row teaching example, or a quick prototype | Cannot handle budget vs actual, multiple facts, or repeated attribute values |
| **Many-to-many** | Bridge tables (e.g. vendors belonging to several groups) | Requires a bridge and careful measures; see §3.10 |

---

## 3.10 The accounting hierarchies you must model

Three hierarchies do all the work in financial reporting:

1. **Chart of accounts hierarchy**: `AccountCode` → `AccountType` → `FSLine` → `Statement`.
   In Power BI, build it *in the dimension* with calculated columns, or in Power Query as a mapping table.
2. **Organisation hierarchy**: `CostCentreCode` → `Department` → Company.
3. **Time hierarchy**: Year → Quarter → Month → Day, plus the fiscal equivalent.

For the BS/P&L pages in Module 6 you will add a dedicated **FS structure table** so that statement
line order, subtotals, sign rules and formatting live in data rather than in 40 hard-coded measures.
Build it now:

| FSSortOrder | FSLine | Statement | SignMultiplier | IsSubtotal | CalcGroup |
|---|---|---|---|---|---|
| 10 | Revenue | PL | 1 | No | Revenue |
| 20 | Cost of sales | PL | -1 | No | COS |
| 30 | **Gross profit** | PL | 1 | Yes | — |
| 40 | Operating expenses | PL | -1 | No | OPEX |
| 50 | **Operating profit** | PL | 1 | Yes | — |
| … | | | | | |

---

## 3.11 Practical: verify the model with numbers, not with your eyes

Before leaving this module, run these three checks in DAX query view and record the results in your
working papers.

```dax
// 1. Does the GL tie to a control total? Total debits must equal total credits.
EVALUATE
ROW ( "Total debits", SUM ( FactGLJournal[Debit] ), "Total credits", SUM ( FactGLJournal[Credit] ) )
```

```dax
// 2. How many rows did we load, and do we have full periods?
EVALUATE
SUMMARIZECOLUMNS ( FactGLJournal[Period], "Lines", COUNTROWS ( FactGLJournal ) )
```

```dax
// 3. Are there facts not covered by a dimension row?
EVALUATE
FILTER ( VALUES ( FactGLJournal[AccountCode] ),
         ISBLANK ( CALCULATE ( COUNTROWS ( DimAccount ) ) ) )
```

Expected results are printed in [Lab 03](../labs/Lab_Index.md#lab-03--model-the-mhondoro-warehouse).
If your numbers differ, your model differs — find out why before continuing.

---

## 3.12 Module 3 checklist

- [ ] Star schema built with all relationships and correct cardinality
- [ ] `DimDate` marked as the date table; auto date/time off
- [ ] `MonthName` sorted by `MonthNumber`; `MonthYear` available for axes
- [ ] Role-playing user dimension handled (active + inactive or a duplicated dimension)
- [ ] Orphan-key test returns zero
- [ ] Total debits = total credits in the GL (13,929 rows / $122,878,886.54 each side)
- [ ] Model drawn on one page for the working papers
- [ ] FS structure table planned or built

**Next:** [Module 4 — DAX Fundamentals](04_DAX_Fundamentals.md).

---

## Related material

- [../labs/Lab_Index.md#lab-03--model-the-mhondoro-warehouse](../labs/Lab_Index.md#lab-03--model-the-mhondoro-warehouse)
- [../dax/Core_Measures_Library.dax](../dax/Core_Measures_Library.dax)
- [../reference/Cheat_Sheet.md](../reference/Cheat_Sheet.md)

**Next:** [Module 4 — DAX Fundamentals](04_DAX_Fundamentals.md)
