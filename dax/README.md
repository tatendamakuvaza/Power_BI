# DAX libraries

Copy-paste-ready measures for Maxhub engagements. Written for the Mhondoro model
(`FactGLJournal` + `Dim*` as built in Module 3) and reusable on client work by changing
table/column names.

| File | Contents | Read it with |
|---|---|---|
| [`Core_Measures_Library.dax`](Core_Measures_Library.dax) | Data quality, P&L, balance sheet, working capital, time comparatives, budget, AR, AP, payroll, bank, presentation helpers | Modules 4 and 6 |
| [`Time_Intelligence_Library.dax`](Time_Intelligence_Library.dax) | Period comparatives, YTD/MTD/QTD, semi-additive balances, moving averages, seasonality, close-management measures, forecasting helpers, dynamic titles | Module 5 |
| [`Forensic_Tests_Library.dax`](Forensic_Tests_Library.dax) | Duplicate payments, ghost vendors, round numbers, thresholds, split purchases, J1–J10 journal entry tests, SoD, risk scoring, Benford | Module 9 |

## How to use them

1. **One measure at a time.** In Power BI Desktop: *Modeling ▸ New measure*, paste
   `Name = expression`, press Enter. Rename nothing — the libraries reference each other by name.
2. **Order matters for dependencies.** Build the `Core` library first (the forensic library calls
   `[GL Amount Abs]`, `[Closing Balance]` and friends).
3. **Create the `_Measures` table first** so measures are not scattered across your facts:
   *Modeling ▸ New table* → `_Measures = ROW("Note", "Course measures")`.
4. **Set format strings in the model**, not per visual:
   `$#,##0.00` · `$#,##0;($#,##0);"-"` · `0.0%` · `#,##0`
5. **Add descriptions.** Select the measure ▸ *Properties ▸ Description*. On an engagement, an
   undocumented measure is an unfinished measure.

## Bulk editing (from Module 5 onward)

With more than ~40 measures, use a free external tool:

- **Tabular Editor 2/3** — a tree view of the whole model with a DAX editor, bulk rename/reformat,
  and Best Practice Analyzer (run it before every client handover).
- **DAX Studio** — run `EVALUATE` queries, measure performance, trace queries, and export results
  to Excel for working papers.

Both connect to the model open in Power BI Desktop (External Tools ribbon tab).

## Conventions enforced in these libraries

| Convention | Why |
|---|---|
| Measures, never calculated columns, for anything aggregated | Performance and refresh time on client ledgers |
| Ledger sign convention internally (debits +, credits −) | Makes the balance checks work; convert to presentation only in display measures |
| `VAR` blocks in every non-trivial measure | A reviewer can check your logic line by line |
| `DIVIDE` instead of `/` | Blank instead of `#DIV/0!` in front of a client |
| `ALLSELECTED` for user-driven comparisons, `ALL` for internal totals | Correct behaviour with slicers |
| No hard-coded dates | Period parameters, so the model survives next year |
