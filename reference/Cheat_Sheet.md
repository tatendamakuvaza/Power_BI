# One-page cheat sheet

Print this, tape it next to your monitor. Everything here appears in the course with more explanation.

---

## The pipeline

`Get Data → Transform (Power Query) → Model (star schema + DAX) → Visuals → Publish → Share`

Reconcile at *every* step. A number you cannot tie is a number you cannot report.

---

## Star schema rules

| Do | Don't |
|---|---|
| One fact table per grain | Mix grains in one table |
| Dimensions filter facts (one-to-many, single direction) | Fact-to-fact joins |
| Text keys on both sides | Numeric account codes |
| One marked date table, auto date/time off | Rely on Power BI's hidden date tables |
| State the grain in the table description | Leave "Table1" with unknown grain |

---

## DAX essentials

```dax
-- Base
GL Amount Signed = SUM ( FactGLJournal[Debit] ) - SUM ( FactGLJournal[Credit] )
GL Amount Abs    = SUMX ( FactGLJournal, ABS ( FactGLJournal[AmountUSD] ) )
Total Revenue    = CALCULATE ( [GL Amount Signed], DimAccount[AccountType] = "Revenue" ) * -1
Gross Profit     = [Total Revenue] - [Cost of Sales]
Gross Margin %   = DIVIDE ( [Gross Profit], [Total Revenue] )

-- Balances (semi-additive)
Closing Balance =
VAR LastDate = MAX ( DimDate[Date] )
RETURN CALCULATE ( [GL Amount Signed], DimDate[Date] <= LastDate )

Opening Balance =
VAR FirstDate = MIN ( DimDate[Date] )
RETURN CALCULATE ( [GL Amount Signed], DimDate[Date] < FirstDate )

-- Comparisons
Revenue LY = CALCULATE ( [Total Revenue], SAMEPERIODLASTYEAR ( DimDate[Date] ) )
Revenue YoY % = DIVIDE ( [Total Revenue] - [Revenue LY], [Revenue LY] )
Revenue YTD = TOTALYTD ( [Total Revenue], DimDate[Date] )

-- Variance and RAG
Variance $ = [GL Amount Abs] - [Budget Amount]
Variance % = DIVIDE ( [Variance $], [Budget Amount] )
Variance Colour =
SWITCH ( TRUE (),
    [Variance %] >  0.10, "#C00000",
    [Variance %] >  0.02, "#ED7D31",
    [Variance %] < -0.05, "#548235",
    "#7F7F7F" )

-- Working capital
DSO = DIVIDE ( [Receivables Balance], [Total Revenue] ) * 365
DPO = DIVIDE ( [Payables Balance], [Cost of Sales] ) * 365
DIO = DIVIDE ( [Inventory Balance], [Cost of Sales] ) * 365
CCC = [DSO] + [DIO] - [DPO ]

-- Forensic basics
Manual JE %   = DIVIDE ( CALCULATE ( [GL Lines], FactGLJournal[EntryType] = "Manual" ), [GL Lines] )
Round Numbers = CALCULATE ( [GL Lines], FILTER ( FactGLJournal,
                    ABS ( FactGLJournal[AmountUSD] ) > 0 &&
                    MOD ( ABS ( FactGLJournal[AmountUSD] ), 1000 ) = 0 ) )
Unapproved    = CALCULATE ( [GL Amount Abs],
                    FILTER ( FactGLJournal,
                        FactGLJournal[ApprovedBy] = "" && FactGLJournal[AbsAmountUSD] > 10000 ) )
```

---

## The seven DAX habits

1. `VAR` blocks in every non-trivial measure.
2. `DIVIDE()` not `/`.
3. Filter columns, not tables, in `CALCULATE` when you can.
4. Aggregate before iterating.
5. `ALLSELECTED` for user-driven comparisons; `ALL` for internal denominators.
6. No hard-coded dates or rates — parameters or a configuration table.
7. Every measure has a description and a format string.

---

## Power Query moves

| Need | Transformation |
|---|---|
| Headers are wrong | Use First Row as Headers |
| Numbers arrive as text | Change type; *Replace Values* for symbols/commas |
| Trailing spaces break joins | Transform ▸ Format ▸ Trim |
| Month columns Jan–Dec | Select identity columns ▸ Unpivot Other Columns |
| Combine monthly files | Get Data ▸ Folder ▸ Combine & Transform |
| Split "1100 Trade Receivables" | Split Column ▸ By Delimiter (first space), limit 1 |
| Replace blanks with 0 | Replace Values (null → 0), or Fill Down |
| Make a period a parameter | Manage Parameters ▸ add filter step |

Forensic reminder: **flag duplicates, do not delete them.**

---

## Control checks (put these on a page in every model)

| Check | Target |
|---|---|
| Debits − credits | 0.00 |
| Assets − (Liabilities + Equity + current result) | 0.00 |
| Orphan keys | 0 |
| Journals out of balance | 0 |
| P&L result vs retained earnings movement | ties |
| Sub-ledger vs control account | ties |

---

## Design rules

- Title = a sentence with the number in it.
- One question per visual; one idea per page zone.
- Colour means something: actual (dark blue), budget (grey), favourable (green), adverse (red).
- Sort by value or by statement order — never alphabetically, unless alphabetical *is* the order.
- Drillthrough to transaction detail on every financial page.
- Alt text, ≥10 pt fonts, not colour-dependent.

---

## File and folder conventions

```
Mhondoro_Forensic_v1.0.pbix
├── stg_*            (staging queries, load disabled)
├── Dim*             (dimensions)
├── Fact*            (facts)
├── _Measures        (all measures, display folders)
└── Ref*/Map*        (mapping and configuration tables)
```

Reports: `Executive · Financials · Analytics · Forensic · Data Quality (hidden)`

---

## Numbers to memorise for this dataset (so you know your model is right)

| Measure | Value |
|---|---|
| GL lines / journals | 13,929 / 5,504 |
| Total debits = credits | 122,878,886.54 |
| Revenue FY2024 / FY2025 (9M) | 13,786,573 / 10,543,059 |
| PAT FY2024 / FY2025 | 447,052 / −61,867 |
| AR / AP / inventory / cash | 3,790,174 / 2,373,621 / 871,343 / 792,548 |
| Suspense balance | 51,059 |
| Flagged forensic value | 1,945,536.55 across 171 journals |

---

## The professional rules

1. Never analyse the original file; hash it and work on a copy.
2. Every cleaning decision is documented: what, how many rows, and who approved it.
3. Facts, inferences and opinions are labelled separately.
4. Value at risk ≠ quantified loss; never blur them.
5. No accusations in a report; findings are about controls and transactions.
6. An independent reviewer signs off before anything is issued.
7. The client owns their model and their data.
