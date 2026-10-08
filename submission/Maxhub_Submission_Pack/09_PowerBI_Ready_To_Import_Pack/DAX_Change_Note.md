# DAX change note

Generated 2025-10-08. The three DAX libraries in this pack are the repository's own files. Validating them against the ledger before shipping found 5 measures that did not agree with the client's control totals. Each is corrected in the copy shipped here; the repository originals are untouched, and the build stops if an upstream expression changes, so a correction can never be applied to the wrong text.

## [Tax Expense] in `Core_Measures_Library.dax`

The FSLine "Taxation" spans two accounts: 8000 Income Tax Expense (P&L) and 2130 Income Tax Payable (balance sheet). Without the statement filter the measure netted the liability into the charge and returned -239,329.32 - a negative tax expense. Filtered to the P&L it returns 221,440.69, agreeing with the tax charge in the financial statements.

## [Current Ratio] in `Core_Measures_Library.dax`

Current liabilities omitted income tax payable (account 2130, 460,770.01) and the suspense credit balance (51,058.87), so the measure returned 1.54 against 1.35 in the financial statements. Both are added by account code rather than by the Taxation FSLine, because that FSLine also contains 8000 Income Tax Expense in the P&L - filtering on it would drag the tax charge into current liabilities and give 1.43. Corrected, the measure returns 1.35 and agrees.

## [DSO] in `Core_Measures_Library.dax`

The day count was hard-coded to 365 while the revenue measure covers nine months, which overstates the days: 131 against the 98 published. Using [Days In Period] (273 days to 30 September 2025) agrees. Set it to 365 for a full-year model.

## [DPO] in `Core_Measures_Library.dax`

As DSO: 166 days on a 365-day basis against 124 on the 273 days actually elapsed.

## [DIO] in `Core_Measures_Library.dax`

As DSO: 61 days on a 365-day basis against 46 on the 273 days actually elapsed.

## Not a defect, but a trap worth knowing

The P&L measures sum every posting with no filter on `EntryType`. That is right for the open year, because the FY2024 closing entries transfer that year's result to retained earnings and so net the prior year to zero. The consequence is that a slicer set to `FiscalYear = 2024` returns zero revenue, not FY2024 revenue. To read a closed year, filter `EntryType <> "Closing"` and sum `FactGLJournal[PLValue]`; that returns 13,786,572.99 for FY2024. Both routes are validated in `Validation_Report.txt`.

## Sign conventions

- `[GL Amount Signed]` is `SUM(Debit) - SUM(Credit)`. On revenue accounts it is negative, so `[Total Revenue]` multiplies by -1.
- `[Closing Balance]` is the same sum filtered to dates up to the last visible date, with no sign adjustment. `[Liabilities Total]`, `[Equity Total]`, `[Payables Balance]` and `[Suspense Balance]` multiply by -1 to present credit balances as positive.
- `[Assets Total]` therefore includes the suspense account, which the chart of accounts classifies as an asset carrying a credit balance. `[BS Check]` still returns 0.00. The financial statements present it the other way round - suspense shown as a credit within current liabilities - and that presentation balances too. Both are validated.
