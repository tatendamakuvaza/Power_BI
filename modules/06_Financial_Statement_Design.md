# Module 6 — Financial Statement Design

**Time:** 10 hours · **Lab:** [Lab 06](../labs/Lab_Index.md#lab-06--the-financial-reporting-pack) · **Prerequisite:** Module 5

> Everything you have learned so far exists to make this module possible: a live set of financial
> statements, built from the ledger, that ties to the trial balance and refreshes itself.

Four pages you will build:

1. **Profit or loss** — actual, budget, variance, prior year, with commentary.
2. **Balance sheet** — opening, movement, closing, with the balance check visible.
3. **Cash flow** — movements in cash and a reconciliation of profit to cash.
4. **Close pack** — the control checks that prove the numbers are fit to publish.

---

## 6.1 The FS structure table (build this first)

Hard-coding statement line order into 40 measures is the mark of an amateur model. Put the structure
in data instead.

Create the table in Power Query (Home ▸ Enter Data) — call it `FSPresentation`:

| FSSortOrder | FSLine | Statement | SignMultiplier | IsSubtotal | Grouping |
|---|---|---|---|---|---|
| 10 | Revenue | PL | 1 | No | Income |
| 20 | Cost of sales | PL | -1 | No | Cost of sales |
| 30 | **Gross profit** | PL | 1 | Yes | Subtotal |
| 40 | Operating expenses | PL | -1 | No | Overheads |
| 50 | **Depreciation and amortisation** | PL | -1 | No | Overheads |
| 60 | **Operating profit** | PL | 1 | Yes | Subtotal |
| 70 | Finance costs | PL | -1 | No | Below the line |
| 80 | **Profit before tax** | PL | 1 | Yes | Subtotal |
| 90 | Taxation | PL | -1 | No | Below the line |
| 100 | **Profit after tax** | PL | 1 | Yes | Subtotal |
| 200 | Property, plant and equipment | BS | 1 | No | Non-current assets |
| 210 | Investment property | BS | 1 | No | Non-current assets |
| 220 | Deferred tax | BS | 1 | No | Non-current assets |
| 230 | **Total non-current assets** | BS | 1 | Yes | Subtotal |
| 240 | Inventories | BS | 1 | No | Current assets |
| 250 | Trade and other receivables | BS | 1 | No | Current assets |
| 260 | Cash and cash equivalents | BS | 1 | No | Current assets |
| 270 | **Total current assets** | BS | 1 | Yes | Subtotal |
| 280 | **TOTAL ASSETS** | BS | 1 | Yes | Subtotal |
| 300 | Share capital | BS | 1 | No | Equity |
| 310 | Retained earnings | BS | 1 | No | Equity |
| 320 | Other reserves | BS | 1 | No | Equity |
| 330 | **Total equity** | BS | 1 | Yes | Subtotal |
| 340 | Borrowings | BS | 1 | No | Non-current liabilities |
| 350 | Provisions | BS | 1 | No | Non-current liabilities |
| 360 | **Total non-current liabilities** | BS | 1 | Yes | Subtotal |
| 370 | Trade and other payables | BS | 1 | No | Current liabilities |
| 380 | Taxation | BS | 1 | No | Current liabilities |
| 390 | Suspense — to be cleared | BS | 1 | No | Current liabilities |
| 400 | **Total current liabilities** | BS | 1 | Yes | Subtotal |
| 410 | **TOTAL EQUITY AND LIABILITIES** | BS | 1 | Yes | Subtotal |
| 900 | (not used in statements) | BS | 1 | No | — |

Map every account to an `FSLine` (our `DimAccount[FSLine]` already does). Then:

- The **statement rows** come from the table (so the report shows every line even if the amount is zero).
- The **subtotals** are measures that pick the right accounts.
- The **order** comes from `FSSortOrder` (Sort by column).
- The **sign** comes from `SignMultiplier`.

Two relationship notes: `FSPresentation[FSLine]` joins to `DimAccount[FSLine]` (many-to-one, so
`FSPresentation` filters `DimAccount` filters the facts); and the subtotal rows do **not** map to
accounts — they are handled in DAX with `ISINSCOPE`/`HASONEVALUE` or by using the `Grouping` column.

### The "statement table" pattern (cleanest way to get a real statement)

Create a disconnected table listing exactly the rows you want, in order:

```dax
Statement Rows =
DATATABLE (
    "Statement", STRING, "SortOrder", INTEGER, "RowLabel", STRING,
    {
        { "PL", 10, "Revenue" },
        { "PL", 20, "Cost of sales" },
        { "PL", 30, "Gross profit" },
        { "PL", 40, "Operating expenses" },
        { "PL", 60, "Operating profit" },
        { "PL", 70, "Finance costs" },
        { "PL", 80, "Profit before tax" },
        { "PL", 90, "Taxation" },
        { "PL", 100, "Profit after tax" }
    }
)
```

Then one measure switches on the row:

```dax
Statement Amount =
SWITCH ( SELECTEDVALUE ( 'Statement Rows'[RowLabel] ),
    "Revenue",            [Total Revenue],
    "Cost of sales",      [Cost of Sales],
    "Gross profit",       [Gross Profit],
    "Operating expenses", [Operating Expenses],
    "Operating profit",   [Operating Profit],
    "Finance costs",      [Finance Costs],
    "Profit before tax",  [Profit Before Tax],
    "Taxation",           [Tax Expense],
    "Profit after tax",   [Profit After Tax],
    BLANK () )
```

Formatting: bold the subtotal rows using **Format ▸ Row headers ▸ Conditional formatting ▸ Font ▸ by
rules ▸ "Gross profit", "Operating profit", …**. Add a top border to subtotals the same way. Now the
statement *looks* like a financial statement, and the structure is data, not measures.

### Getting the budget onto the same rows

`FactBudget` uses `AccountCode`, not `FSLine`. Add a budget measure that respects the same statement
structure by mapping in the measure (`TREATAS`) rather than by duplicating the structure table:

```dax
Budget by FSLine =
CALCULATE (
    [Budget Amount],
    TREATAS ( VALUES ( DimAccount[AccountCode] ), FactBudget[AccountCode] )
)
```

Then `Variance $ = [Statement Amount] - ABS ( [Budget by FSLine] )` — mind the sign convention: budgets
are stored as positive magnitudes; expenses in the statement are also shown positive in our
presentation measures, so subtract.

---

## 6.2 Sign conventions — decide once, write it down

Three conventions exist in the wild. Pick one and never mix:

| Convention | Assets | Liabilities | Revenue | Expenses | Use for |
|---|---|---|---|---|---|
| **Ledger (signed)** | + | − | − | + | Balance checks, reconciliations, audit trails |
| **Presentation (positive)** | + | + | + | + | Any statement a human reads |
| **Contribution** | + | + | + | − | Contribution/margin bridges |

Maxhub standard: keep the ledger signed everywhere in the model. Convert to presentation only in the
display measures (`Total Revenue`, `Cost of Sales`, `Assets Total` …). Never in calculated columns;
never in the source.

> Every number in the *balance sheet* presentation measures must carry the correct `SignMultiplier`
> from `FSPresentation`. If you build it this way, flipping a sign later is a one-row change in a table,
> not a rewrite.

---

## 6.3 Page 1 — Profit or loss

**Layout (top to bottom):**

| Zone | Content |
|---|---|
| Slicer bar | Year + Period (between slicers for FY2024 / FY2025), Cost centre, Budget version |
| KPI strip | 4 cards: Revenue, Gross margin %, Operating profit, PAT — each with a small sparkline |
| Statement matrix | Rows: `Statement Rows[RowLabel]`, Columns: `DimDate[MonthYear]` + Total, Values: `Statement Amount`, `Budget by FSLine`, `Variance $`, `Variance %` |
| Bridge | Waterfall: prior month → revenue, cost of sales, opex, other → current month operating profit |
| Commentary | Text box or a measure-driven card carrying the auto-written sentence |

**The variance matrix setup (the single most useful matrix in accounting):**

- Rows: `Statement Rows[RowLabel]`
- Columns: `DimDate[MonthYear]`
- Values: `Statement Amount` | `Budget by FSLine` | `Variance $` | `Variance %`
- **Conditional formatting ▸ Background colour ▸ Format by: Field value → `Variance Colour`**
- Row headers bold for subtotals (by rule)
- Show on rows with no data: off

**Auto commentary that is honest:**

```dax
PL Commentary =
VAR Curr = [Operating Profit]
VAR VarToBudget = [Variance $]
VAR Driver =
    CALCULATE ( VALUES ( DimAccount[AccountName] ),
        TOPN ( 1, VALUES ( DimAccount[AccountName] ), ABS ( [Variance $] ), DESC ) )
RETURN
    "Operating profit was " & FORMAT ( Curr, "$#,##0" ) &
    " against a budget of " & FORMAT ( ABS ( [Budget by FSLine] ), "$#,##0" ) &
    IF ( ABS ( VarToBudget ) > 0, ". The largest single driver was " & Driver &
        " (" & FORMAT ( VarToBudget, "+$#,##0;-$#,##0" ) & ").", "." )
```

Rule for client work: **auto-generated commentary must be reviewed by a human before it is issued.**
State that in the methodology note. (The same rule applies to Copilot's narratives in Module 11.)

---

## 6.4 Page 2 — Balance sheet

The balance sheet is where the semi-additive engine from Module 5 pays off.

- **Rows:** `FSPresentation[FSLine]` where `Statement = "BS"`, sorted by `FSSortOrder`
- **Columns:** selectable period (use a slicer on `DimDate[MonthYear]`, single-select)
- **Values:** Opening balance | Movement | Closing balance — three measures, one per column
- **Bottom row:** `BS Check` — must show **0.00**

```dax
BS Check =
VAR Assets      = [Assets Total]
VAR Liabilities = [Liabilities Total]
VAR Equity      = [Equity Total]
VAR CYResult    = [Current Year Result]
RETURN Assets - ( Liabilities + Equity + CYResult )
```

> **The "current year result" trap.** If your ledger closes the previous year's profit into retained
> earnings (as Mhondoro's does on 31 December 2024) but the *current* year's profit has not yet been
> closed, then `Assets − (Liabilities + Equity)` will equal the current year's profit, not zero.
> That is not an error — it is what the ledger contains. Show `Retained earnings + current year result`
> as "Retained earnings (incl. current year result)" in the statement and the check goes to zero.
> Write this in the methodology note; it is exactly the kind of thing a reviewer will ask about.

For Mhondoro at 30 Sep 2025 the check reconciles as:

```
Assets  − (Liabilities + Equity) = -61,867   <- the FY2025 result to date (a loss)
Add current year result          = -61,867
BS Check                         =     0.00
```

That number (-61,867) is also the FY2025 result on the P&L page — if the two disagree, you have a model bug.

---

## 6.5 Page 3 — Cash flow

Power BI cannot infer cash flow from a P&L; you must model it. Two approaches:

### 6.5.1 Direct movements (simple, reliable)

Cash accounts are flagged in `DimAccount[IsCashAccount] = "Yes"`.

```dax
Opening Cash =
VAR FirstDate = MIN ( DimDate[Date] )
RETURN CALCULATE ( [GL Amount Signed], DimAccount[IsCashAccount] = "Yes", DimDate[Date] < FirstDate )

Closing Cash = CALCULATE ( [Closing Balance], DimAccount[IsCashAccount] = "Yes" )
Net Cash Movement = [Closing Cash] - [Opening Cash]
```

Then show the **sources and uses** by grouping the *counterparty* of each cash entry. In a real
engagement you add a `CashFlowCategory` mapping table (Operating / Investing / Financing) and tag the
descriptions in Power Query. For the course, build the classification as a calculated column from the
description and account:

```dax
Cash Flow Category =
SWITCH ( TRUE (),
    FactGLJournal[AccountCode] = "1100", "Receipts from customers",
    FactGLJournal[AccountCode] = "2000", "Payments to suppliers",
    FactGLJournal[AccountCode] = "6000" || FactGLJournal[AccountCode] = "5010", "Payments to employees",
    FactGLJournal[AccountCode] = "2100" || FactGLJournal[AccountCode] = "2110"
        || FactGLJournal[AccountCode] = "2120" || FactGLJournal[AccountCode] = "2130", "Taxes paid",
    FactGLJournal[AccountCode] = "7000", "Interest paid",
    FactGLJournal[AccountCode] = "3200", "Dividends paid",
    FactGLJournal[AccountCode] = "1400" || FactGLJournal[AccountCode] = "1410"
        || FactGLJournal[AccountCode] = "1420", "Capital expenditure",
    "Other" )
```

### 6.5.2 Indirect reconciliation (the one the client's bank asks for)

Show, per month: profit after tax → add back depreciation → working capital movements → cash generated
→ investing/financing → net movement → closing cash.

```dax
Working Capital Movement =
VAR Receivables = CALCULATE ( [Balance Movement], DimAccount[FSLine] = "Trade and other receivables" )
VAR Inventory   = CALCULATE ( [Balance Movement], DimAccount[FSLine] = "Inventories" )
VAR Payables    = CALCULATE ( [Balance Movement], DimAccount[FSLine] = "Trade and other payables" )
RETURN ( Receivables + Inventory + Payables ) * -1     -- an increase in AR/stock uses cash
```

Present it as a **waterfall chart** with a "Closing cash" total column. When the waterfall's final
column equals `Closing Cash`, your classification is complete — that is the reconciliation, and it is
the deliverable.

---

## 6.6 Page 4 — The close pack (the page that earns trust)

Auditors and CFOs trust a report that can prove itself. Build a page of *tick marks*, each a card:

| Check | Measure | Expected |
|---|---|---|
| GL debits = credits | `[Debit Total] - [Credit Total]` | 0.00 |
| Debits total (control) | `[Debit Total]` | 122,878,886.54 |
| Balance sheet checks | `[BS Check]` | 0.00 |
| P&L ties to BS result | `[Profit After Tax] - [Current Year Result]` | 0.00 |
| Unreconciled bank items | `CALCULATE ( COUNTROWS ( FactBankTransactions ), FactBankTransactions[ReconciledFlag] = "No" )` | (report it, do not hide it) |
| Suspense balance | `[Suspense Balance]` | Investigate if material |
| Activity in closed periods | `CALCULATE ( COUNTROWS ( FactGLJournal ), FactGLJournal[SourceSystem] = "Year-End Close" )` | posted entries only |
| Orphan keys | `[GL Lines With Unknown Account]` | 0 |
| Journal IDs out of balance | `[Unbalanced Journals]` | 0 |

```dax
Unbalanced Journals =
COUNTROWS (
    FILTER (
        VALUES ( FactGLJournal[JournalID] ),
        VAR Dr = CALCULATE ( SUM ( FactGLJournal[Debit] ) )
        VAR Cr = CALCULATE ( SUM ( FactGLJournal[Credit] ) )
        RETURN ABS ( Dr - Cr ) > 0.005
    )
)
```

This page is also your **engagement quality-control evidence**: screenshot it into the working papers
at every close. It proves you checked.

---

## 6.7 Working with budgets, forecasts and scenarios

- **Budget vs actual**: `FactBudget` (monthly, by account and cost centre). Join on `AccountCode` +
  `CostCentreCode` + `FiscalPeriod` — build a proper composite relationship, or (better) unpivot and
  conform the keys so you can use two clean relationships.
- **Forecast**: two approaches. (a) Let the client type a `ForecastUSD` column into a copy of the
  budget table with a `Scenario` column — simple and auditable. (b) Use DAX `FORECAST.LINEAR` and
  document it as a statistical projection, not a commitment.
- **Scenario switching** with a disconnected slicer table:

```dax
Scenario Table = DATATABLE ( "Scenario", STRING, { {"Actual"}, {"Budget"}, {"Forecast"}, {"Actual + Forecast"} } )

Scenario Amount =
SWITCH ( SELECTEDVALUE ( 'Scenario Table'[Scenario] ),
    "Actual",   CALCULATE ( [GL Amount Signed] ) * -1,
    "Budget",   [Budget by FSLine],
    "Forecast", [Forecast Amount],
    "Actual + Forecast",
        VAR LastActual = CALCULATE ( MAX ( FactGLJournal[PostingDate] ), ALL ( FactGLJournal ) )
        RETURN IF ( MAX ( DimDate[Date] ) <= LastActual, [GL Amount Signed] * -1, [Forecast Amount] ) )
```

---

## 6.8 Module 6 checklist

- [ ] `FSPresentation` (or `Statement Rows`) built and mapped; rows sorted by `FSSortOrder`
- [ ] P&L page with actual / budget / variance / variance % and conditional formatting
- [ ] Balance sheet page with opening, movement, closing and `BS Check = 0.00`
- [ ] Cash flow page with a waterfall that reconciles to the movement in cash accounts
- [ ] Close pack page with nine control checks, all explaining themselves
- [ ] Methodology note paragraph on sign conventions and the current-year-result treatment
- [ ] Every page's totals tie to `FactTrialBalance`

**Next:** [Module 7 — Visualisation & Dashboard Design](07_Visualisation_and_Dashboard_Design.md).

---

## Related material

- [../labs/Lab_Index.md#lab-06--the-financial-reporting-pack](../labs/Lab_Index.md#lab-06--the-financial-reporting-pack)
- [../capstones/Capstone_2_Financial_Reporting_Pack.md](../capstones/Capstone_2_Financial_Reporting_Pack.md)
- [../assets/PowerBI_Course_Theme.json](../assets/PowerBI_Course_Theme.json)

**Next:** [Module 7 — Visualisation & Dashboard Design](07_Visualisation_and_Dashboard_Design.md)
