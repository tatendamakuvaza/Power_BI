# Module 4 — DAX Fundamentals

**Time:** 8 hours · **Lab:** [Lab 04](../labs/Lab_Index.md#lab-04--twenty-five-core-measures) · **Prerequisite:** Module 3

> DAX is not Excel. Excel formulas calculate on one cell at a time; DAX calculates **a whole column
> of a table at once**, under a filter context you control. Once that clicks, everything else follows.

---

## 4.1 The three things DAX does

| Purpose | Object | Example | When |
|---|---|---|---|
| Calculate a number from the model | **Measure** | `Total Revenue = SUM ( FactGLJournal[AmountUSD] )` | 95% of your work |
| Add a column to a table (row by row) | **Calculated column** | `Debit - Credit for this row` | Only when you need it on an axis, in a slicer, or in a relationship |
| Create a new table | **Calculated table** | A date table, a mapping table | Occasionally |

**Decision rule:** if it must be sliced, filtered or aggregated by the user → **measure**.
If it must live on an axis or be a sort key → **calculated column**. If in doubt, measure.

Why this matters commercially: calculated columns are stored in memory and are computed on refresh.
On a 10-million-row ledger they will slow a client's refresh to a crawl. Measures compute at query time
and are free until used.

---

## 4.2 Row context vs filter context (the whole game)

**Row context** — "which row am I on?" Exists inside calculated columns and inside iterators
(`SUMX`, `FILTER`, `AVERAGE`). In a calculated column, `FactGLJournal[Debit]` means *this row's*
debit.

**Filter context** — "which rows are visible?" Determined by the visual (rows, columns, slicers,
page filters) and by `CALCULATE`. Every measure is evaluated inside a filter context.

```
Visual: Matrix with rows = AccountName, columns = Period
Cell (Revenue, 2025-03):
   filter context = AccountType contains Revenue AND Period = "2025-03"
   Total Revenue evaluates SUM(AmountUSD) over the rows that survive that context
```

**Context transition** an important subtlety you will meet soon: wrapping a *row context* inside a
`CALCULATE` turns it into a *filter context*. That is how `CALCULATE ( [Measure], condition )` inside
`SUMX`/`FILTER` works (Module 5).

---

## 4.3 The DAX you will use 90% of the time

### Aggregators

```dax
Total Debits      = SUM ( FactGLJournal[Debit] )
Total Credits     = SUM ( FactGLJournal[Credit] )
GL Lines          = COUNTROWS ( FactGLJournal )
Customers         = DISTINCTCOUNT ( FactARAgeing[CustomerID] )
Average Invoice   = AVERAGE ( FactAPInvoices[AmountUSD] )
```

Prefer `COUNTROWS ( table )` over `COUNT ( column )`: it is faster and it counts rows, not non-blank values.

### The accounting sign engine

Our GL stores debits in `[Debit]` and credits in `[Credit]`. The signed amount is:

```dax
GL Amount Signed = SUM ( FactGLJournal[Debit] ) - SUM ( FactGLJournal[Credit] )
GL Amount Abs    = SUMX ( FactGLJournal, ABS ( FactGLJournal[AmountUSD] ) )
```

- Use **Signed** for balances and statements (assets debit-positive, revenue credit-negative).
- Use **Abs** for value-based tests: thresholds, Benford, duplicate scanning.
  A $48,000 credit must show as 48,000 in a Benford test, not −48,000.

### Safe division

```dax
Gross Margin % = DIVIDE ( [Gross Profit], [Total Revenue] )
```

`DIVIDE` returns blank (not `#DIV/0!`) when the denominator is zero — mandatory in dashboards your
client will look at unsupervised.

### CALCULATE — the most important function in DAX

```dax
-- Syntax
CALCULATE ( <expression>, <filter1>, <filter2>, ... )
```

It evaluates the expression after **replacing** the filter context with the filters you supply.
Three forms you must know cold:

```dax
-- 1. Boolean/column filter (the modern, preferred form)
CoS Amount =
CALCULATE ( [GL Amount Signed], DimAccount[FSLine] = "Cost of sales" )

-- 2. Table filter via FILTER (use only when the condition must be row-level/complex)
Large Entries =
CALCULATE ( [GL Amount Abs], FILTER ( FactGLJournal, ABS ( FactGLJournal[AmountUSD] ) >= 10000 ) )

-- 3. Remove or override existing filters
All Accounts Revenue % =
DIVIDE ( [Total Revenue], CALCULATE ( [Total Revenue], ALL ( DimAccount ) ) )
```

Filters applied by `CALCULATE` **replace** existing filters on the same column, and **add** to filters
on other columns. That single sentence explains most "weird DAX behaviour".

### Iterators — SUMX, AVERAGEX, and when you need them

```dax
-- Sum of a row-by-row expression (you cannot use SUM)
Inventory Value = SUMX ( FactFixedAssets, FactFixedAssets[CostUSD] - FactFixedAssets[AccumulatedDepreciationUSD] )
Coverage Days    = AVERAGEX ( VALUES ( DimCustomer[CustomerID] ), [DSO] )
```

Rule: `SUM` works when the column already exists. `SUMX` is for expressions computed row by row —
which on a ledger is often the only way to get a weighted (not average-of-averages) answer.

### Time intelligence (preview — full treatment in Module 5)

```dax
Revenue YTD    = TOTALYTD ( [Total Revenue], DimDate[Date] )
Revenue LY     = CALCULATE ( [Total Revenue], SAMEPERIODLASTYEAR ( DimDate[Date] ) )
Revenue LY Var = [Total Revenue] - [Revenue LY]
Revenue LY %   = DIVIDE ( [Revenue LY Var], [Revenue LY] )
```

All of these require a properly marked date table (Module 3) — otherwise they silently return nonsense.

---

## 4.4 Variable tables: your measures should read like a schedule

`VAR` is not optional polish; it is how you write DAX another accountant can review.

```dax
-- Before: one long expression nobody can check
Margin % = DIVIDE ( CALCULATE ( [GL Amount Signed], DimAccount[FSLine]="Revenue" ) - ... )

-- After: a readable calculation
Gross Margin % =
VAR Revenue     = CALCULATE ( [GL Amount Signed], DimAccount[FSLine] = "Revenue" )
VAR CostOfSales = CALCULATE ( [GL Amount Signed], DimAccount[FSLine] = "Cost of sales" )
VAR GrossProfit = Revenue + CostOfSales          -- CoS is credit-negative, so ADD, not subtract
RETURN
    DIVIDE ( GrossProfit, Revenue )
```

> **Sign trap.** If you use signed amounts, expenses are negative, so gross profit is
> `Revenue + CostOfSales`, not `Revenue - CostOfSales`. This is the single most common error
> accountants make in DAX. Either work with signs consistently, or define a `PL Amount` measure that
> returns expenses as positive and revenue positive, and always subtract. Pick one convention, write
> it in the methodology note, and never mix.

---

## 4.5 The conventions Maxhub uses on every engagement

Put these in a `_Measures` table (a home for measures so the field list stays clean: **Modeling ▸ New table**:

```dax
_Measures = ROW ( "Note", "All measures live here - see the methodology note" )
```

Then a display folder structure:

| Folder | Example measures |
|---|---|
| `01 Base` | `GL Amount Signed`, `GL Amount Abs`, `GL Lines` |
| `02 P&L` | `Total Revenue`, `Cost of Sales`, `Gross Profit`, `Gross Margin %`, `Operating Expenses`, `Operating Profit` |
| `03 Balance Sheet` | `Closing Balance`, `Debtor Balance`, `Creditor Balance`, `Suspense Balance` |
| `04 Working Capital` | `DSO`, `DPO`, `DIO`, `Cash Conversion Cycle` |
| `05 Variance` | `Budget Amount`, `Variance $`, `Variance %`, `RAG Status` |
| `06 Forensic` | `Benford Chi Square`, `Duplicate Suspects`, `Round Number Count`, `Weekend Postings` |

Naming rules: Title Case, no abbreviations, **no prefix like `M_` or `Measure -`**, always a description
in the measure's properties, and a format string set in the model.

---

## 4.6 Twenty-five core measures (build every one of these)

These are written for our Mhondoro model. Build them in a `_Measures` table, then verify against the
expected numbers in Lab 04.

```dax
-- ============ 01 BASE ============
GL Amount Signed = SUM ( FactGLJournal[Debit] ) - SUM ( FactGLJournal[Credit] )
GL Amount Abs    = SUMX ( FactGLJournal, ABS ( FactGLJournal[AmountUSD] ) )
GL Lines         = COUNTROWS ( FactGLJournal )
Debit Total      = SUM ( FactGLJournal[Debit] )
Credit Total     = SUM ( FactGLJournal[Credit] )

-- ============ 02 P&L (revenue positive, expenses positive) ============
PL Amount =
VAR IsRevenue = SELECTEDVALUE ( DimAccount[Statement] ) = "PL"
VAR Amount    = [GL Amount Signed]
RETURN
    IF ( Amount < 0, -Amount, Amount )      -- present everything as a positive magnitude

Total Revenue =
CALCULATE ( [GL Amount Signed], DimAccount[AccountType] = "Revenue" ) * -1

Cost of Sales =
CALCULATE ( [GL Amount Signed], DimAccount[FSLine] = "Cost of sales" )

Gross Profit     = [Total Revenue] - [Cost of Sales]
Gross Margin %   = DIVIDE ( [Gross Profit], [Total Revenue] )

Operating Expenses = CALCULATE ( [GL Amount Signed], DimAccount[FSLine] = "Operating expenses" )
EBITDA = [Gross Profit] - [Operating Expenses] + CALCULATE ( [GL Amount Signed], DimAccount[AccountName] = "Depreciation" )
Operating Profit = [Gross Profit] - [Operating Expenses]
Finance Costs = CALCULATE ( [GL Amount Signed], DimAccount[FSLine] = "Finance costs" )
Profit Before Tax = [Operating Profit] - [Finance Costs]
Tax Expense = CALCULATE ( [GL Amount Signed], DimAccount[FSLine] = "Taxation" )
Profit After Tax = [Profit Before Tax] - [Tax Expense]

-- ============ 03 BALANCE SHEET ============
-- Cumulative-to-date balance as at the last date visible in the visual.
-- (Module 5 develops the full opening/closing-per-period engine.)
Closing Balance =
VAR LastVisibleDate = MAX ( DimDate[Date] )
RETURN
    CALCULATE ( [GL Amount Signed], DimDate[Date] <= LastVisibleDate )

Assets Total = CALCULATE ( [Closing Balance], DimAccount[AccountType] = "Asset" )
Liabilities Total = CALCULATE ( [Closing Balance], DimAccount[AccountType] = "Liability" ) * -1
Equity Total = CALCULATE ( [Closing Balance], DimAccount[AccountType] = "Equity" ) * -1
Suspense Balance = CALCULATE ( [GL Amount Signed], DimAccount[IsSuspense] = "Yes" ) * -1
// BS must be: Assets = Liabilities + Equity + current year result (see Module 6)
BS Check = [Assets Total] - ( [Liabilities Total] + [Equity Total] + [Current Year Result] )
Current Year Result =
VAR MaxFY = CALCULATE ( MAX ( DimDate[FiscalYear] ), ALL ( DimDate ) )
RETURN CALCULATE ( [Profit After Tax], DimDate[FiscalYear] = MaxFY )

-- ============ 04 WORKING CAPITAL ============
Receivables Balance = CALCULATE ( [GL Amount Signed], DimAccount[AccountCode] = "1100" )
Payables Balance    = CALCULATE ( [GL Amount Signed], DimAccount[AccountCode] = "2000" ) * -1
Inventory Balance   = CALCULATE ( [GL Amount Signed], DimAccount[FSLine] = "Inventories" )
DSO = DIVIDE ( [Receivables Balance], [Total Revenue] ) * 365
DPO = DIVIDE ( [Payables Balance], [Cost of Sales] ) * 365
Cash Conversion Cycle = [DSO] + [DIO] - [DPO]
DIO = DIVIDE ( [Inventory Balance], [Cost of Sales] ) * 365

-- ============ 05 VARIANCE ============
Budget Amount  = SUM ( FactBudget[BudgetUSD] )
Variance $     = [GL Amount Signed] * -1 - [Budget Amount]
Variance %     = DIVIDE ( [Variance $], [Budget Amount] )
RAG Status =
SWITCH ( TRUE (),
    [Variance %] > 0.10, "🔴 Over budget",
    [Variance %] > 0.02, "🟠 Watch",
    "🟢 Within budget" )
```

Now the payoff: because everything is a measure on a shared model, this ONE set of definitions powers
the P&L page, the BS page, the cost-centre report, the budget variance page and the forensic tests.
Change `Total Revenue` once; every page updates.

---

## 4.7 Calculated columns you will actually need

```dax
-- In DimAccount: a hierarchy-ready sorting column
FS Sort = SWITCH ( DimAccount[FSLine],
    "Revenue", 10, "Cost of sales", 20, "Operating expenses", 30,
    "Finance costs", 40, "Taxation", 50, 99 )

-- In FactGLJournal: a posting-size band used by the risk-scoring tests in Module 9
Amount Band =
VAR A = ABS ( FactGLJournal[AmountUSD] )
RETURN
SWITCH ( TRUE (),
    A >= 100000, "8. >100k",
    A >= 50000,  "7. 50k-100k",
    A >= 10000,  "6. 10k-50k",
    A >= 5000,   "5. 5k-10k",
    A >= 1000,   "4. 1k-5k",
    A >= 100,    "3. 100-1k",
    A >= 10,     "2. 10-100",
    "1. <10" )

-- In FactGLJournal: the manual-journal risk flag used across the forensic tests
Manual JE Flag = IF ( FactGLJournal[EntryType] = "Manual", 1, 0 )
```

Note the sort-friendly band labels ("1. ", "2. " …) — a cheap trick so bands sort logically in a chart
without extra modelling.

---

## 4.8 Debugging: how to find out why a number is wrong

| Symptom | First thing to check |
|---|---|
| Measure blank everywhere | Relationship missing, or filter column has no matching values (check for trailing spaces / data type) |
| Total does not equal sum of rows | You used `SUM` where `SUMX` was needed, or a measure in a visual row context |
| YTD doubles when you add a column | Two date relationships (one inactive); a filter is hitting both tables |
| `CALCULATE` seems to ignore a filter | The filter column is on the wrong side of a unidirectional relationship |
| Numbers correct per row, wrong in total | Aggregation of a non-additive value (rate, %, balance) — use `SUMX`/`AVERAGEX` or a semi-additive pattern (Module 5) |
| Different answer in DAX query view vs visual | The visual has a filter or a top-N you forgot about |

Tools: **DAX query view** (run `EVALUATE` and inspect actual rows), **Performance Analyzer**
(View ▸ Performance analyzer) to see how long each visual takes, and **Tabular Editor / DAX Studio**
for bulk measure management once you have more than ~40 measures.

---

## 4.9 Module 4 checklist

- [ ] `_Measures` table created; measures organised in display folders
- [ ] All 25 core measures built and formatted (`$#,##0.00`, `0.0%`)
- [ ] You can explain row context vs filter context in your own words
- [ ] You can explain why gross profit uses `+` not `−` on signed amounts
- [ ] Every measure has a description
- [ ] `BS Check` returns 0.00

**Next:** [Module 5 — Advanced DAX](05_Advanced_DAX_Time_Balance_Context.md): time intelligence,
semi-additive balances and the accountant-grade calculations that separate a template from a tool.

---

## Related material

- [../labs/Lab_Index.md#lab-04--twenty-five-core-measures](../labs/Lab_Index.md#lab-04--twenty-five-core-measures)
- [../dax/Core_Measures_Library.dax](../dax/Core_Measures_Library.dax)
- [../assessments/Quiz_Questions.md](../assessments/Quiz_Questions.md)

**Next:** [Module 5 — Advanced DAX: Time, Balance & Context](05_Advanced_DAX_Time_Balance_Context.md)
