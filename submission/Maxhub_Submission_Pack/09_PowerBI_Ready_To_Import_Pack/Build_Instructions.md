# Power BI ready-to-import pack

Generated 2025-10-08. Table and column names match the raw extract and the repository's three DAX libraries exactly, so `Core_Measures_Library.dax`, `Forensic_Tests_Library.dax` and `Time_Intelligence_Library.dax` work against these CSVs without a rename.

## Contents

| File | What it is |
|---|---|
| `Data_Ready_To_Import/` | 26 CSV files - the warehouse |
| `PowerQuery_Load.m` | M code with types inferred from the shipped files |
| `Core_Measures_Library.dax` | Financial and data-quality measures |
| `Forensic_Tests_Library.dax` | The twelve forensic tests as DAX |
| `Time_Intelligence_Library.dax` | Period, YTD and prior-year measures |
| `DAX_Measures_Reference.xlsx` | Every measure, plus 30 build validation checks |
| `PowerBI_Data_Model.xlsx` | Star schema, columns, relationships, control totals |
| `Validation_Report.txt` | Proof the shipped files reproduce the control totals |
| `Import_Manifest.json` | Machine-readable manifest |

## Tables

| Query | Type | Rows | Columns | Description |
|---|---|---:|---:|---|
| `FactGLJournal` | Fact | 13,929 | 54 | Every general ledger line, with statement signs and fraud flags pre-computed |
| `FactJournal` | Fact | 5,504 | 33 | Journal header: one row per journal with its approval status |
| `DimDate` | Dimension | 1,461 | 22 | Calendar with fiscal period, weekend and month-end flags |
| `DimAccount` | Dimension | 71 | 18 | Chart of accounts with statement sign columns |
| `DimVendor` | Dimension | 26 | 24 | Vendor master with bank masking and spend analytics |
| `DimCustomer` | Dimension | 18 | 17 | Customer master with receivables and collections priority |
| `DimUser` | Dimension | 12 | 16 | System users with posting and approval statistics |
| `DimEmployee` | Dimension | 63 | 13 | Employee master (bank accounts masked) |
| `DimCostCentre` | Dimension | 9 | 4 | Cost centres and annual budgets |
| `DimFXRate` | Dimension | 84 | 6 | Monthly FX rates |
| `DimScheme` | Dimension | 7 | 18 | The seven fraud schemes, injected vs detected |
| `FactAPInvoices` | Fact | 520 | 21 | Supplier invoices with three-way-match exception reasons |
| `FactARAgeing` | Fact | 420 | 21 | Receivables ageing with collections priority scores |
| `FactBankTransactions` | Fact | 1,400 | 16 | Bank transactions with reconciliation status |
| `FactExpenseClaims` | Fact | 650 | 16 | Expense claims with receipt and approval exceptions |
| `FactExceptionRegister` | Fact | 171 | 34 | The 171 scored exceptions raised by the twelve forensic tests |
| `FactDismissedExceptions` | Fact | 141 | 9 | Exceptions raised by a test, investigated and dismissed with a reason |
| `FactTrialBalance` | Fact | 1,323 | 9 | Delivered trial balance, for the GL-to-TB reconciliation |
| `FactBudget` | Fact | 1,299 | 7 | Monthly budget by account and cost centre |
| `FactSalesOrders` | Fact | 900 | 14 | Sales orders with margin |
| `FactFixedAssets` | Fact | 120 | 14 | Fixed asset register |
| `FactClientChurnScored` | Fact | 150 | 21 | Maxhub client churn: every client-year scored, with P(churn) and fee at risk |
| `FactEngagementEconomics` | Fact | 160 | 17 | Maxhub engagement economics with over-run, realisation, margin and anomaly flags |
| `FactRevenueForecast` | Fact | 45 | 10 | Twelve-month revenue forecast, three methods |
| `FactPipeline` | Fact | 240 | 11 | Maxhub opportunity pipeline with weighted values |
| `FactServiceLineMonthly` | Fact | 231 | 12 | Maxhub service-line revenue and margin by month |

## Build in seven steps

1. **Set up the folder.** Copy `Data_Ready_To_Import` somewhere stable and create a Power Query parameter `DataFolder` pointing at it, with no trailing slash.
2. **Load the tables.** Dimensions first, then facts. Paste each section of `PowerQuery_Load.m` into the Advanced Editor of a blank query and rename the query to match. Do not use Get Data > CSV - Power BI guesses the types and gets `AccountCode` and the currency columns wrong.
3. **Build the model.** Create the relationships on the `Relationships` tab of `PowerBI_Data_Model.xlsx`. One-to-many, single direction, dimension to fact. The three role-playing `DimDate` relationships and the approver relationship must be inactive. Mark `DimDate` as the date table and switch off Auto date/time.
4. **Add the measures.** Paste the three `.dax` libraries in order, using the `// FOLDER:` comments for the display folders. 196 measures in total.
5. **Validate.** `Validation_Report.txt` re-performs the key measures against the shipped CSVs and ties each one to a control total. Reproduce them in the model using the `Validation` tab of `DAX_Measures_Reference.xlsx`.
6. **Build the six pages** described in `Build_Instructions.docx`. The interactive dashboard in `10_Interactive_Dashboard` is a working specification of four of them.
7. **Govern before publishing.** Row-level security per cost centre, daily gateway refresh at 06:00 with failure alerts, sensitivity labels, descriptions on every measure.

## Sign conventions (the two things that break every model)

- **P&L measures** sum `FactGLJournal[PLValue]`, which is `-AmountUSD x PLSign`, and exclude `EntryType = "Closing"`.
- **Balance-sheet measures** sum `FactGLJournal[BSValue]`, which is `AmountUSD x BSSign` (assets +1, everything else -1), filtered to the as-at date and keeping all entry types.

## Control totals the model must reproduce

| Control | Value |
|---|---:|
| GL lines | 13,929 |
| Journals | 5,504 |
| Total debits = total credits | $122,878,886.54 |
| Unbalanced journals | 0 |
| Trial balance differences | 0 |
| Revenue FY2024 | $13,786,572.99 |
| Revenue FY2025 nine months | $10,543,059.22 |
| Net profit FY2025 nine months | $-61,866.98 |
| Total assets | $9,000,443.24 |
| Balance sheet check | 0.00 |
| Supplier spend | $30,505,968.04 |
| Exception journals | 171 |
| Exception value | $1,945,536.55 |
| Detection rate against the answer key | 100% |

## Why there is no .pbix

A `.pbix` is a binary container that cannot be authored or verified outside Power BI Desktop. Shipping an unverified binary would mean handing over a file nobody has opened. This pack builds the same model, and `Validation_Report.txt` proves the numbers before you start.
