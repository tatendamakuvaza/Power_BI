# Power Query (M) library

Ten reusable queries that cover 90% of the data preparation in an accounting engagement.
Read [`../modules/02_Connecting_and_Shaping_Data_PowerQuery.md`](../modules/02_Connecting_and_Shaping_Data_PowerQuery.md)
alongside this folder.

| # | Query | Use it for | Client situation |
|---|---|---|---|
| 00 | Parameters | Period, thresholds, VAT rate, folder path | Every engagement — never hard-code |
| 01 | Fact GL Journal | Type-safe ledger import with signed and absolute amounts | Any ERP export |
| 02 | Dimensions with text keys | Stop account codes becoming numbers | Where `"0110"` became `110` |
| 03 | Unpivot a wide budget | `Jan…Dec` columns → one row per month | Annual budget spreadsheets |
| 04 | Combine monthly files | A folder that refreshes itself | Client drops a file each month |
| 05 | Clean a vendor/customer list | Name and bank-detail cleaning before matching | Ghost-vendor and duplicate-name tests |
| 06 | Duplicate payment detection | Group by vendor + amount + window | Forensic engagements (populations over ~100k rows) |
| 07 | Threshold/structuring test | Count payments just below control limits | Fraud risk assessment |
| 08 | Benford digits | Build the digit table, test chi-square in DAX | Forensic analytics |
| 09 | Journal entry risk flags | One `RiskFlags` column per GL line | The forensic workbench |
| 10 | Maxhub churn features | Risk profile for the ML lab | Module 11 |

## How to use

1. Open Power BI Desktop ▸ **Home ▸ Transform data** ▸ **Home ▸ Advanced Editor**.
2. Paste one query block, give the query the same name as the comment header (**names matter** —
   later queries reference `FactGLJournal` and `pSourceFolder`).
3. Set the parameters first (query 00) — the rest will not evaluate without them.
4. After each step, check the **profile** (View ▸ Column profile) for nulls, errors and unexpected values
   *before* moving on. Document anything you fix.
5. For CSV sources, always verify `Encoding = 65001` (UTF-8). A wrong encoding turns `Müller` into
   `MÃ¼ller` and silently breaks name matching.

## Rules for engagements

- Keep a `stg_` prefix for staging queries and set **Enable load = off**; only final queries enter the model.
- Rename every Applied Step to say *why* it exists, e.g. `Keep FY2024-2025 postings only`.
- Never remove duplicates without a documented reason and a `DuplicateFlag` column where the duplicates
  themselves are evidence.
- Every data-cleaning decision goes in the working papers: what was excluded, how many rows, and who approved it.
- If a step makes the query slow (over ~5 minutes on a client machine), look for a fold-breaking custom
  column before the filter and move the filter earlier.
