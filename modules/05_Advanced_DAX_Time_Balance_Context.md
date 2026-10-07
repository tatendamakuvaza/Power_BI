# Module 5 — Advanced DAX: Time, Balance and Filter Context

**Time:** 10 hours · **Lab:** [Lab 05](../labs/Lab_Index.md#lab-05--the-time-and-balance-engine) · **Prerequisite:** Module 4

> This is the module that makes an accountant's Power BI model different from a generic business
> dashboard. Anyone can sum sales. Getting a **closing balance per period that reconciles to the
> trial balance** is a professional skill.

---

## 5.1 Which calculations are additive, and which are not

| Type | Example | DAX pattern |
|---|---|---|
| **Additive** | Revenue, expenses, units, debits | `SUM` — rows add up, all periods add up |
| **Semi-additive** | Account balances, headcount, bank balance | Add across accounts/centres, **not across time** — you need opening/closing logic |
| **Non-additive** | Margins, ratios, rates, DSO | Never sum. Recalculate from components (`DIVIDE(total numerator, total denominator)`) |

Half of all "my numbers are wrong" complaints come from summing a semi-additive value. Get this
classification right for every measure you write.

---

## 5.2 The date table rules that time intelligence depends on

Before any `TOTALYTD` or `SAMEPERIODLASTYEAR` works correctly:

1. `DimDate` is a **continuous** table of dates with no gaps (ours: 1,461 rows, 2023-01-01 to 2026-12-31).
2. It is **marked as a date table** (Model view ▸ right-click ▸ *Mark as date table* ▸ `Date`).
3. **Auto date/time is off** (otherwise Power BI creates hidden date tables that filter first and
   silently take precedence).
4. The date table is on the **one** side of every relationship; facts are on the many side.
5. `MonthName` is sorted by `MonthNumber`; a numeric `Year` exists for axes.

Test it before you trust it:

```dax
EVALUATE
ADDCOLUMNS (
    SUMMARIZECOLUMNS ( DimDate[FiscalPeriod], "Lines", COUNTROWS ( FactGLJournal ) ),
    "Days in period", CALCULATE ( COUNTROWS ( DimDate ) )
)
```

Every period should show 28–31 days and a plausible line count. A period with 0 lines is a period
with no data — you need to know that before a client does.

---

## 5.3 The standard time-intelligence set (write these once)

```dax
-- ==================== COMPARATIVES ====================
Revenue LY = CALCULATE ( [Total Revenue], SAMEPERIODLASTYEAR ( DimDate[Date] ) )

Revenue LM =  -- last month (the prior *period*, not prior day)
CALCULATE ( [Total Revenue], DATEADD ( DimDate[Date], -1, MONTH ) )

Revenue LQ = CALCULATE ( [Total Revenue], DATEADD ( DimDate[Date], -1, QUARTER ) )

Revenue YoY $ = [Total Revenue] - [Revenue LY]
Revenue YoY % = DIVIDE ( [Revenue YoY $], [Revenue LY] )
Revenue MoM $ = [Total Revenue] - [Revenue LM]
Revenue MoM % = DIVIDE ( [Revenue MoM $], [Revenue LM] )

-- ==================== TO DATE ====================
Revenue YTD  = TOTALYTD ( [Total Revenue], DimDate[Date] )
Revenue QTD  = TOTALQTD ( [Total Revenue], DimDate[Date] )
Revenue MTD  = TOTALMTD ( [Total Revenue], DimDate[Date] )
Revenue FYTD = CALCULATE ( [Total Revenue], DATESYTD ( DimDate[Date], "12-31" ) )   -- calendar year end

-- ==================== WORKING-DAY AWARE COMPARATIVES ====================
-- September 2025 is a part-month: never compare month-to-date with a full month.
Revenue Same Period LY =
VAR CutOffDay = MAX ( DimDate[DayOfMonth] )
RETURN
    CALCULATE ( [Total Revenue],
        SAMEPERIODLASTYEAR ( DimDate[Date] ),
        DimDate[DayOfMonth] <= CutOffDay )

-- ==================== MOVING AVERAGES (smooth seasonal noise) ====================
Revenue 3M Average =
AVERAGEX ( DATESINPERIOD ( DimDate[Date], MAX ( DimDate[Date] ), -3, MONTH ), [Total Revenue] )

Revenue 12M Average =
AVERAGEX ( DATESINPERIOD ( DimDate[Date], MAX ( DimDate[Date] ), -12, MONTH ), [Total Revenue] )
```

The **same-period-last-year** measure is the one you will use most with real clients: nearly every
management pack is prepared mid-month, and comparing a 15-day month to a 30-day month is how analysts
lose credibility.

---

## 5.4 The opening / closing balance engine

This is the heart of the module. A balance sheet account's balance is **not** the sum of a month's
movements — it is everything up to the period end.

```dax
-- Movement in the currently selected period only (credit-negative)
Balance Movement = [GL Amount Signed]

-- Opening balance: everything posted BEFORE the first date in the current context
Opening Balance =
VAR FirstVisibleDate = MIN ( DimDate[Date] )
RETURN
    CALCULATE ( [GL Amount Signed], DimDate[Date] < FirstVisibleDate )

-- Closing balance: everything posted up to and including the last date in context
Closing Balance =
VAR LastVisibleDate = MAX ( DimDate[Date] )
RETURN
    CALCULATE ( [GL Amount Signed], DimDate[Date] <= LastVisibleDate )

-- Balance at the end of a specific period, ignoring the visual's month filter
Closing Balance (Period End) =
VAR PeriodEnd = MAX ( DimDate[FiscalPeriodEnd] )
RETURN
    CALCULATE ( [GL Amount Signed], DimDate[Date] <= PeriodEnd )

-- Balance sheet presentation (debit-positive assets, credit-positive liabilities and equity)
Asset Balance     = CALCULATE ( [Closing Balance], DimAccount[AccountType] = "Asset" )
Liability Balance = CALCULATE ( [Closing Balance], DimAccount[AccountType] = "Liability" ) * -1
Equity Balance    = CALCULATE ( [Closing Balance], DimAccount[AccountType] = "Equity" )  * -1
```

**Why `MIN`/`MAX` and not `FIRSTDATE`/`LASTDATE`:** they behave the same on a single date column but
`MIN`/`MAX` are faster and clearer in review. Use `FIRSTDATE`/`LASTDATE` only when you need a table.

### The movement reconciliation (put this in your working papers)

```dax
TB Reconciliation =
VAR Opening  = [Opening Balance]
VAR Movement = [Balance Movement]
VAR Closing  = [Closing Balance]
RETURN
    IF (
        ABS ( Opening + Movement - Closing ) < 0.005,
        "Ties",
        "ERROR: " & FORMAT ( Opening + Movement - Closing, "#,##0.00" )
    )
```

Put `TB Reconciliation` on a hidden data-quality page. Every engagement deliverable should show
"Ties" everywhere before it goes to a client.

### Validating against the pre-built trial balance

The dataset ships with `FactTrialBalance` (monthly, by account). Cross-check your engine:

```dax
TB Extract Closing =
CALCULATE ( SUM ( FactTrialBalance[ClosingBalance] ),
            DimAccount[AccountType] = "Asset",
            FactTrialBalance[AccountCode] IN VALUES ( DimAccount[AccountCode] ) )

Balance Engine vs TB =
VAR Engine = [Asset Balance]
VAR Extract = [TB Extract Closing]
RETURN FORMAT ( Engine - Extract, "#,##0.00" )
```

A non-zero difference is either a model problem or a genuine extract problem — both are findings.

---

## 5.5 Semi-additive patterns for real accounting questions

### 5.5.1 "The balance at the end of each month" in a matrix

Put `DimDate[MonthYear]` on rows. `Closing Balance` already returns the month-end balance because it
cumulates up to `MAX(DimDate[Date])` inside that month's context. Two things to watch:

- If a month has no postings for an account, the cumulative pattern still returns the carried-forward
  balance (correct for a balance sheet) but shows blank for movement measures (also correct).
  Hide the blanks: **Visual ▸ Field ▸ Format ▸ Show items with no data = off**, or accept the blanks.
- Do not put `Closing Balance` in a chart with a month granularity *below* month end — the value at
  15 September is the balance at 15 September, which is meaningful but not what a month-end report means.

### 5.5.2 Period end that is not a calendar month

Some clients run 4-4-5 periods. Add a `PeriodNumber` to `DimDate` from their mapping table, then use
it everywhere in place of `MonthNumber`. The patterns above do not change.

### 5.5.3 Multi-company / multi-currency closing balances

Keep the ledger in the transaction currency and translate in DAX using `DimFXRate`:

```dax
Revenue USD from ZAR =
SUMX (
    FILTER ( FactGLJournal, FactGLJournal[Currency] = "ZAR" ),
    FactGLJournal[AmountUSD] * RELATED ( DimFXRate[AverageRate] )
)
```

Better: translate in Power Query (Module 2) with a merge, keep the model thin. Whichever you choose,
state in your methodology note whether you used average or closing rates and where they came from.

---

## 5.6 Dynamic titles, subtitles and RAG — making a report read like commentary

A dashboard that says "Revenue" on top of a chart makes the reader do the work. Make the report say
the sentence:

```dax
Revenue Title =
VAR Curr = [Total Revenue]
VAR Prior = [Revenue LY]
VAR Pct = DIVIDE ( Curr - Prior, Prior )
RETURN
    "Revenue " & FORMAT ( Curr, "$#,##0,," ) & "m (" &
    FORMAT ( Pct, "+0.0%;-0.0%;0.0%" ) & " vs prior year)"
```

Use it in a card with the title hidden, or as a text box whose value is driven by a measure
(Insert ▸ Text box ▸ type `Revenue Title` in the field well... in practice: use a **Card (new)** visual
with `Revenue Title` and turn off the category label).

```dax
-- Traffic-light colour for conditional formatting
Variance Colour =
SWITCH ( TRUE (),
    [Variance %] >  0.10, "#C00000",     -- red = overspend (expense context)
    [Variance %] >  0.02, "#ED7D31",     -- amber
    [Variance %] < -0.05, "#548235",     -- green = underspend
    "#7F7F7F" )
```

Apply with **Format ▸ Cells ▸ Font colour ▸ Conditional formatting ▸ Field value**.

---

## 5.7 Ranking, TOPN and exception reporting

```dax
-- Rank accounts/vendors by value inside whatever is on the axis
Vendor Rank = RANKX ( ALLSELECTED ( DimVendor[VendorName] ), [GL Amount Abs], , DESC, DENSE )

-- "Only show me the top 10 accounts, and tell me what share they are"
Top 10 Accounts % =
VAR Top10 = CALCULATE ( [GL Amount Abs], TOPN ( 10, ALLSELECTED ( DimAccount[AccountName] ), [GL Amount Abs] ) )
VAR AllAccts = CALCULATE ( [GL Amount Abs], ALLSELECTED ( DimAccount[AccountName] ) )
RETURN DIVIDE ( Top10, AllAccts )

-- Exception flag used all over the forensic pages
Is Exception = IF ( [GL Amount Abs] > 25000 && [GL Lines] <= 3, "Exception", "Normal" )
```

---

## 5.8 Context transition: the concept that unlocks the hard stuff

Inside an iterator (a calculated column, `SUMX`, `FILTER`), you are in **row context** — you have a row,
not a filter. Wrap it in `CALCULATE` and DAX converts the row's values into a filter:

```dax
-- Count, per ledger line, how many earlier lines share the same vendor + amount (Module 9's
-- duplicate detector is built exactly like this)
Duplicate Group Size =
COUNTROWS (
    FILTER (
        FactGLJournal,
        FactGLJournal[VendorID] = EARLIER ( FactGLJournal[VendorID] ) &&
        FactGLJournal[AbsAmountUSD] = EARLIER ( FactGLJournal[AbsAmountUSD] )
    )
)
```

`EARLIER` is the older syntax for "the row context from outside the FILTER". Modern DAX prefers a
variable:

```dax
Duplicate Group Size =
VAR ThisVendor = FactGLJournal[VendorID]
VAR ThisAmount = FactGLJournal[AbsAmountUSD]
RETURN
    COUNTROWS ( FILTER ( FactGLJournal,
        FactGLJournal[VendorID] = ThisVendor &&
        FactGLJournal[AbsAmountUSD] = ThisAmount ) )
```

Both work. The variable version is easier for a reviewer to check — prefer it in client work.

**Caution:** this pattern is O(n²) per row. On our 13,929-row GL it is instant. On a 5-million-row
client ledger it will run for minutes. The alternative: do duplicate detection **in Power Query** with a
`Table.Group` (Module 9 shows both) and load a small flag table. Know which tool to reach for.

---

## 5.9 A worked accountant's problem: "show me each month's over/under recovery of overhead"

Manufacturing clients recover overhead into cost of sales using an absorption rate. You need, per month:

```dax
Overhead Absorbed = CALCULATE ( [GL Amount Signed], DimAccount[AccountCode] = "5020" )
Overhead Actual =
CALCULATE ( [GL Amount Signed],
    DimAccount[AccountCode] IN { "6040", "6050", "6060", "6020" },
    FactGLJournal[Description] <> "Reclassification of factory costs to cost of sales" )

Overhead Under / (Over) Recovery = [Overhead Absorbed] - [Overhead Actual]
Overhead Recovery % = DIVIDE ( [Overhead Absorbed], [Overhead Actual] )
```

Why this is worth the ink: it demonstrates the *distribution* of a real analysis task — two measures,
one subtraction, one ratio, and you have replaced a manual spreadsheet schedule that a client
rebuilds every month.

---

## 5.10 Performance habits (so the model stays usable as it grows)

| Habit | Why |
|---|---|
| Use `VAR` heavily | Variables are computed once per context; repeated expressions are not |
| Filter a column, not a table, inside `CALCULATE` | Column filters are cheap; `FILTER(table, …)` scans |
| Avoid `FILTER` over a fact table if a dimension filter will do | Filters on `DimX[Column]` are faster and simpler |
| Prefer `SUMMARIZE`/`SUMMARIZECOLUMNS` to nested iterators | Clearer and better optimised |
| Aggregate **before** iterating: `SUMX(VALUES(...), [Measure])` not `SUMX(Fact, expression)` where possible | Fewer rows iterated |
| Keep calculated columns out of big fact tables | They cost memory on every refresh |
| Measure performance with *Performance Analyzer* | Guesswork wastes fees |

---

## 5.11 Module 5 checklist

- [ ] All the comparative and to-date measures built
- [ ] Opening / Closing / Movement engine built and reconciles (`TB Reconciliation` = "Ties")
- [ ] Balance engine agrees with `FactTrialBalance` closing balances
- [ ] Matrix showing MonthYear × AccountName with closing balances carried forward correctly
- [ ] Dynamic title measure used on at least one visual
- [ ] Conditional formatting driven by a DAX colour measure
- [ ] Duplicate-detection pattern built and understood (row context vs context transition)

**Next:** [Module 6 — Financial Statement Design](06_Financial_Statement_Design.md).

---

## Related material

- [../labs/Lab_Index.md#lab-05--the-time-and-balance-engine](../labs/Lab_Index.md#lab-05--the-time-and-balance-engine)
- [../dax/Time_Intelligence_Library.dax](../dax/Time_Intelligence_Library.dax)
- [../assessments/Quiz_Questions.md](../assessments/Quiz_Questions.md)

**Next:** [Module 6 — Financial Statement Design](06_Financial_Statement_Design.md)
