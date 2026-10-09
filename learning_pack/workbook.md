# Start here | Your learning route
Tatenda, this workbook follows the twelve topics already in your Power_BI repository. It is self-contained: you need only the accompanying CSV, this PDF and Power BI Desktop to complete the core exercises. The data combines fictional Mhondoro Manufacturing financial records with Maxhub consulting-practice records.
## What to study, in order
01 Tool fluency: Desktop, Service, import, report versus dashboard, saving and publishing.
02 Power Query: parameters, types, profiling, nulls, cleaning, references, merge, append, group, pivot and unpivot.
03 Modelling: grain, dimensions, keys, star schemas, relationships, dates, roles and filter direction.
04 DAX fundamentals: measures, calculated columns, row/filter context, CALCULATE, iterators and safe ratios.
05 Advanced DAX: time intelligence, partial years, closing balances, ranking, share, inactive relationships and what-if scenarios.
06 Financial statements: P&L, balance sheet, cash movements, trial-balance reconciliation and currency limitations.
07 Visual design: visual choice, layout, accessibility, interactions, bookmarks, tooltips and drill-through.
08 Analytics: budgets, variance, ageing, working capital, operational KPIs, concentration and discovery.
09 Forensics: duplicates, vendor links, thresholds, split purchases, journal tests, Benford and risk scoring.
10 Investigation: evidence, population, case selection, hypotheses, defensible findings and loss quantification.
11 AI/ML: influencers, forecasting, anomalies, churn classification, evaluation, leakage, Python/R and responsible AI.
12 Advisory and deployment: scoping, pricing, quality assurance, RLS, refresh, sharing, performance and handover.
Then complete four portfolio capstones: investigation, reporting pack, analytics engagement and AI advisory prototype.
## Suggested rhythm
Allow about 110-140 hours including practice and capstones. Study two sessions of 90 minutes and one three-hour lab each week. Spend more time on Modules 3-6 if DAX or accounting is new. A realistic flexible schedule is 18-24 weeks; an intensive route may be faster. Do not advance until the control totals reconcile.
Each module contains notes, numbered actions, a visual specification and questions with worked answers. Numeric answer tables are generated directly from the CSV source records. Clear all filters unless an exercise explicitly names a period, account or population. Dollar results are rounded to two decimals; ratios to two decimal places in percentage display.
## Navigation within this PDF
Use the PDF bookmarks to jump between sections, or your viewer's search: “Module 01”, “Module 09”, “Control answers”, “Monthly answers”, “Schema |” and “Spoiler” locate the sections. The schema appendix lists every source field, its suggested type and either a definition or a sample value. The final appendix reveals the injected journal IDs: do not read it before completing Module 09.
# Dataset contract | Read before importing
## One physical file; many analytical populations
The CSV is a wide, typed bundle, not a single sales fact. RecordType tells you which logical table a row belongs to. RecordID uniquely identifies a bundle row. Fields not relevant to that RecordType are blank by design. Split the bundle in Power Query before modelling. Never sum AmountUSD over the entire bundle: the same column means different things in different tables, and control populations would be double-counted.
The bundle preserves the existing practice data except that the GL AnomalyLabel and the separate InjectionLog have been withheld. The injection answer key is in this PDF. Vendor employee-link and AP duplicate-suspected flags remain supplied assertions: use them to validate, not to substitute for independent tests.
All people, businesses, account numbers and events are synthetic. FX rates and the 15% VAT convention belong to this fictional scenario, not to current tax or currency advice. Do not apply a second FX conversion to a column already expressed in USD.
## Important limitations that good analysts disclose
The general ledger and its derived trial balance are the accounting reconciliation backbone. AR, AP, sales orders, bank, fixed assets and budgets are separate synthetic practice populations: do not assume they tie to the GL or one another. Treat each table's control total separately. A sales order is not recognised GL revenue; an AP invoice is not proof of payment.
The GL spans January 2024 to September 2025. The supplied date dimension is January 2023 to December 2026; the original repository prose described a different date range. In this workbook create a fresh 2021-2026 calendar to cover client-year and monthly practice data too. Client churn covers 2021-2025. Preserve the source date table for inspection only; do not use its FiscalPeriodEnd field as a month-end without checking it.
GrossAmountUSD in FactSalesOrders is already Quantity × UnitPriceUSD × (1 - DiscountPct / 100), despite its name. MarginPct and DiscountPct are percentage points, e.g. 15 means 15%, not 0.15. FactTrialBalance balances are normal-balance signed; GL Debit - Credit is debit-positive. Their signs differ for credit-normal accounts. Annual budget and snapshot balances are not additive over time.
The bank BalanceUSD follows generation order, not a verified chronological statement sequence. Do not use it as an audited closing-bank balance. Some practice metrics can look implausible (e.g. monthly proposals won exceeding submitted): identify the mismatch and ask whether wins relate to prior-period proposals.
@HASH
# Table inventory | Import checkpoints
These are the logical tables available inside the single CSV. The row counts below must match after splitting. A reference query shares transformations; it does not physically create another source file.
@MANIFEST
# Module 01 | Your first report
## Notes
Power BI Desktop is the Windows authoring application. Power Query prepares data; Model view defines relationships; Report view presents visuals; DAX evaluates calculations in the current filter context. The Power BI Service hosts shared semantic models, reports and dashboards. A report can have multiple pages; a Service dashboard is a separate pinned-tile canvas. A PDF export is static, not an interactive report.
Desktop core labs work locally without a paid sharing licence. Desktop does not run natively on macOS: use an appropriate Windows machine or Windows virtual environment. Publishing, sharing, Fabric and AI features depend on tenant settings and licences; complete the local alternative when those services are not available. Menus may move between releases.
## Practical 01 | Build the first screen
1. Extract the ZIP into a permanent folder. Keep both delivered files together. Open Desktop, create a blank report and save it as Tatenda_PowerBI_Practice.pbix.
2. Select Get data > Text/CSV. Choose Tatenda_Makuvaza_Practice_Data.csv, UTF-8 and comma delimiter, then Transform Data. Confirm the first row is used as headers. Delete an automatically inserted Changed Type step: the bundle deliberately mixes table schemas.
3. Name the query Bundle. Filter RecordType to FactGLJournal. Keep LineID, JournalID, PostingDate, Debit and Credit. Set PostingDate to Date and Debit/Credit to Fixed decimal number. Name this temporary query FirstGL and Close & Apply.
4. Create the three measures below using New measure. Add two cards for Debit and Credit, a line chart using PostingDate (not the automatic hierarchy) and Debit, and a table with JournalID, Debit and Credit. Add a PostingDate between slicer.
5. Save. Optional: publish only to a private training workspace in your tenant. Do not use Publish to web for confidential work. You will replace FirstGL with the full model in Module 02.
```
First Debit = SUM(FirstGL[Debit])
First Credit = SUM(FirstGL[Credit])
First Difference = [First Debit] - [First Credit]
```
## Expected visual and answers
Q1. What should the two cards show with no slicer? Answer: each shows USD 122,878,886.54; First Difference is 0.00. Set display units to None to see cents. The line chart shows debit activity, not sales performance.
Q2. Is a debit line a complete transaction? Answer: no. LineID identifies a ledger line. JournalID groups the debit and credit lines into a journal. Distinct journals and row counts differ.
Q3. Does balancing prove the data is fraud-free? Answer: no. Balanced journals can be unauthorised, misclassified or fictitious. Balance is a population-integrity control, not a fraud conclusion.
Checkpoint: screenshot your first page and write one sentence distinguishing report, dashboard and semantic model.
# Module 02 | Power Query and reliable preparation
## Notes
Power Query transformations run on refresh; DAX measures run when a visual is queried. Treat source extracts as read-only. Preserve blanks rather than replacing every null with zero: an absent approver is not a numeric zero. Set IDs to Text, currency amounts to Fixed decimal, counts to Whole number and timestamps to Date/Time. Decimal number is suitable for model features and rates with more than four decimal places.
Data profiling defaults can examine only the first 1,000 rows. Switch Column profiling to the entire dataset before interpreting empty/error/distinct counts. Keep an exception query when a conversion fails instead of silently deleting the failing rows.
## Practical 02A | One source, reusable references
1. Delete FirstGL and its three temporary measures after saving your first screenshot. Start a fresh Text/CSV import; call it Bundle. Do not filter Bundle itself. Remove automatic type steps. Disable Enable load for Bundle.
2. In Manage Parameters create a Text parameter pCsvPath with the full path to your extracted CSV. Replace Bundle's Advanced Editor code with this code. Only the parameter value is computer-specific.
```
let
    Source = Csv.Document(File.Contents(pCsvPath),
        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    Headers
```
3. Right-click Bundle > Reference. Name the query FactGLJournal. Filter RecordType to FactGLJournal. Select only the columns listed in its schema appendix, then Remove Other Columns. This removes the routing keys too. Do not remove rows just because irrelevant bundle fields were blank.
4. Repeat the reference-filter-select process for the other 20 analytical tables. For the source DimDate, call the query SourceDate and disable its load; you will create a new DimDate in Module 03. Load the other 21 tables. Each query's name must match the inventory exactly for the DAX below.
5. Apply types from the schema appendix. Treat FiscalYear as Text in the GL if following the appendix. For maxhub_client_churn set Year, Stayed and all model features to numbers. Treat PONumber, account codes and IDs as Text. Use locale English (United States) when parsing dot-decimal values and check ISO dates.
6. Check row counts against the inventory, Close & Apply, and save. For a CSV source, query folding does not occur; reference queries can reread the source. This small training bundle is convenient, not a recommended large-enterprise storage design.
## Optional shortcut | A reusable function
Create a blank query called fnTable; paste the function below. It lets you replace the reference-filter-select steps with an explicit column list from the schema. Do not use it to discard rows with nulls.
```
(kind as text, keep as list) as table =>
let
    Rows = Table.SelectRows(Bundle, each [RecordType] = kind),
    Columns = Table.SelectColumns(Rows, keep)
in
    Columns
```
Example for a small dimension; then set each column's type:
```
= fnTable("DimCostCentre",
    {"CostCentreCode", "CostCentreName", "Department", "AnnualBudgetUSD"})
```
# Module 02 | Cleaning, combining and reshaping lab
## Practical 02B | Controlled transformations
1. Duplicate DimVendor as VendorCleanPractice and disable its load. Select VendorName > Transform > Format > Trim and Clean. Add an uppercase comparison name without overwriting the original. Preserve names and BankAccount as evidence fields.
2. Duplicate FactGLJournal as GLGroupPractice. Use Group By (Advanced): group on JournalID, sum Debit as JournalDebit, sum Credit as JournalCredit, Count Rows as Lines. Add Difference = [JournalDebit] - [JournalCredit]. Filter absolute Difference > 0.01 into a separate Exceptions query. All journals should balance.
3. Merge a reference of FactAPInvoices with DimVendor on VendorID, Left Outer. Expand VendorName and Category only. Before and after the merge, row counts should both be 520. A larger count means the vendor side is not unique. A Left Anti merge is an orphan-key test, not a valid substitute for a left join.
4. Reference FactBudget. Keep Period, AccountCode, CostCentreCode and BudgetUSD. Group by Period and sum BudgetUSD. Duplicate it twice, filtering 2024 in one and 2025 in the other; Append as New. The appended table must equal the original grouped monthly population. Merge joins columns by keys; Append stacks rows with aligned column names.
5. In the grouped budget query, pivot Period using BudgetUSD with Sum. Then select the period columns and Unpivot Columns. Rename Attribute to Period and Value to BudgetUSD. The sum must be unchanged; grain is now a month/value row again. Disable load for all practice copies to avoid duplicate analytical populations.
6. Use a custom column to check a sales-order amount: Number.Round([Quantity] * [UnitPriceUSD] * (1 - [DiscountPct] / 100), 2). Compare with GrossAmountUSD using an absolute difference tolerance of 0.01.
## Questions and worked answers
Q1. Should you remove every row containing a blank? Answer: no. Most bundle fields are structurally blank for a given RecordType; even within a table, optional VendorID or ApprovedBy can be legitimately absent. Filter the correct population first.
Q2. What is the journal-group result? Answer: 5,504 journal groups and zero differences above one cent. Do not remove distinct journal lines as “duplicates” merely because amounts repeat.
Q3. Why parameterise the path? Answer: you can move the extract and change one parameter rather than rewriting every query. The Service still needs access to that path through a configured source/gateway.
Q4. How do you audit cleaning? Answer: retain the untouched CSV, record its hash, name each applied step, count rows before/after and separately capture exceptions. The control section includes the delivered CSV hash.
Expected visuals: a data-quality table containing population, source rows, loaded rows, type errors and exception rows. Accept only exact inventory row matches and explained type errors; formatting improvements must not alter money totals.
# Module 03 | Model the data, not the picture
## Notes
A fact records an event or snapshot at a declared grain. A dimension describes business entities. One-to-many relationships should run from a unique dimension key to repeated fact keys, with single-direction filtering. Avoid fact-to-fact relationships, automatic many-to-many fixes and casual bidirectional relationships: they can create ambiguous or inflated results.
The CSV is a transport format. Your model must separate populations. Do not connect all tables simply because they contain Period, AmountUSD or BankAccount. Employee bank account identifiers and bank statement account labels are not the same key domain.
## Practical 03A | Create the calendar
1. In Options for this file, turn off Auto date/time. Use New table to create the following calculated table. Mark it as a date table using Date; Date must be unique, continuous and nonblank.
```
DimDate =
ADDCOLUMNS(
    CALENDAR(DATE(2021,1,1), DATE(2026,12,31)),
    "Year", YEAR([Date]),
    "MonthNo", MONTH([Date]),
    "Month", FORMAT([Date], "MMM"),
    "YearMonth", FORMAT([Date], "yyyy-MM"),
    "YearMonthSort", YEAR([Date]) * 100 + MONTH([Date]),
    "Quarter", "Q" & FORMAT([Date], "Q")
)
```
2. Sort Month by MonthNo and YearMonth by YearMonthSort. You should have 2,191 dates. Use YearMonth for multi-year visuals; Month alone combines different years.
3. In Power Query add BudgetDate to FactBudget: Date.FromText([Period] & "-01"). Add the same MonthStart construction to maxhub_billable_hours and maxhub_pipeline when you need monthly reporting. maxhub_service_line_financials already has Month as a date. Calendar-year accounting is assumed; do not label it a non-calendar fiscal year.
## Practical 03B | Set relationships manually
DimAccount[AccountCode] -> FactGLJournal[AccountCode], FactBudget[AccountCode], FactTrialBalance[AccountCode]. Each is 1:* single direction. Do not connect FactFixedAssets to both CostAccountCode and AccDepAccountCode as active relationships.
DimCostCentre[CostCentreCode] -> FactGLJournal, FactBudget and FactSalesOrders on CostCentreCode.
DimVendor[VendorID] -> FactGLJournal[VendorID] and FactAPInvoices[VendorID]. DimCustomer[CustomerID] -> FactGLJournal, FactARAgeing and FactSalesOrders on CustomerID.
DimUser[UserID] -> FactGLJournal[PreparedBy] active; -> FactGLJournal[ApprovedBy] inactive. Add a separate Approver dimension reference instead if you need simultaneous preparer and approver slicers. DimEmployee[EmployeeID] -> FactExpenseClaims[EmployeeID].
DimDate[Date] -> GL PostingDate, Budget BudgetDate, TB PeriodEnd, AP InvoiceDate, Sales OrderDate, Expense ClaimDate, Bank TxnDate, Engagement StartDate and service-financial Month. Add the billable-hours Month date if used. All are single-direction 1:* relationships. GL DocumentDate is an optional inactive relationship.
AR is a snapshot at AsAtDate: relate AsAtDate, not InvoiceDate, for the snapshot page. Fixed assets are also a snapshot-style register; do not date-filter NBV by acquisition date and call it a historical balance. Keep FX and client-year churn disconnected until their own deliberate modelling exercises.
# Module 03 | Validation and model answers
## Practical 03C | Test keys and propagation
1. In Power Query use Group By on each dimension key with Count Rows. Filter Count > 1. Each primary key should be unique. Blank optional foreign keys do not mean the fact row should be deleted.
2. Use a left anti join GL AccountCode to DimAccount AccountCode. Expected result: zero orphan account codes. A matching test on nonblank VendorID also produces zero orphan vendor IDs.
3. Make a matrix with DimAccount[AccountType] rows and SUM(FactGLJournal[Debit]) values. Add DimDate[Year] as a slicer and check that selecting 2024 changes the amounts. Next select an account: budget and GL should both filter, but an unrelated bank statement table should not.
4. Hide technical keys from Report view when users have descriptive alternatives; do not delete relationship columns. Set numeric identifiers to Do not summarise. Create display folders for financial, operations and forensic measures. Take a screenshot of Model view with the central GL star readable.
## Questions and worked answers
Q1. Why does annual budget repeat in a transaction table? Answer: a dimension attribute such as DimCostCentre[AnnualBudgetUSD] is not a monthly fact. Summing it after merging into GL multiplies it by ledger lines. Use FactBudget at its own declared grain.
Q2. Which relationship makes ApprovedBy slicers work? Answer: either activate the inactive user-to-approver relationship inside a measure or use a role-playing Approver dimension. Do not make two competing user relationships active to the same fact.
Q3. Should DimFXRate connect to GL by Currency only? Answer: no. Currency repeats across periods. A valid lookup requires currency plus period and an agreed rate convention. Since GL figures here are already USD, a second conversion would be wrong.
Q4. How many logical tables are in the delivered CSV? Answer: 22. The analytical model uses 21 of them plus a freshly created calendar; SourceDate is retained as a non-loaded inspection query. Practice helper queries should also have load disabled.
Expected visual: a star-schema model diagram, plus a validation table with zero duplicate dimension keys and zero unmatched nonblank account/vendor keys. Cross-filter behaviour is part of the test, not merely the appearance of relationship lines.
# Module 04 | DAX fundamentals and the financial core
## Notes
A calculated column evaluates row by row and is stored after refresh. A measure evaluates in the visual's filter context: slicers, rows, columns and relationships. SUM aggregates a column; SUMX iterates a table expression; DIVIDE safely handles zero denominators. CALCULATE changes filter context. Context transition converts row context to filter context when a measure is evaluated inside an iterator.
Enter each definition below separately with New measure. Suggested home table: FactGLJournal. Fixed decimal source types reduce floating-point noise. Format money as USD with two decimals, counts as integers and ratio measures as percentages.
## Practical 04A | Core measures
```
GL Lines = COUNTROWS(FactGLJournal)
Journals = DISTINCTCOUNT(FactGLJournal[JournalID])
Debit USD = SUM(FactGLJournal[Debit])
Credit USD = SUM(FactGLJournal[Credit])
Net Debit = [Debit USD] - [Credit USD]
Balance Check = [Net Debit]
Activity Net Debit =
CALCULATE([Net Debit],
    FactGLJournal[EntryType] <> "Opening",
    FactGLJournal[EntryType] <> "Closing")
Revenue =
-CALCULATE([Activity Net Debit], DimAccount[FSLine] = "Revenue")
Cost of Sales =
CALCULATE([Activity Net Debit], DimAccount[FSLine] = "Cost of sales")
Gross Profit = [Revenue] - [Cost of Sales]
Gross Margin = DIVIDE([Gross Profit], [Revenue])
Operating Expenses =
CALCULATE([Activity Net Debit], DimAccount[FSLine] = "Operating expenses")
Finance Costs =
CALCULATE([Activity Net Debit], DimAccount[FSLine] = "Finance costs")
Operating Profit = [Gross Profit] - [Operating Expenses]
PL Result =
-CALCULATE([Activity Net Debit], DimAccount[IsPL] = "Yes")
Net Margin = DIVIDE([PL Result], [Revenue])
PL Signed = -[Activity Net Debit]
```
A revenue credit is positive revenue. A cost debit is positive cost. PL Signed deliberately presents costs as negative for an additive P&L matrix. Exclude closing entries from performance: December 2024 includes a year-end transfer to retained earnings that otherwise wipes out annual P&L balances. Include opening and closing entries for balance-sheet and TB reconciliation.
## Visual and questions
1. Add cards for Revenue, Gross Profit, PL Result and Gross Margin. Add a matrix with DimDate[Year] rows and those measures as values. Compare with Control answers.
2. Add DimAccount[FSLine] rows and PL Signed values, with the visual filtered to IsPL = Yes. The total is net result, not total revenue.
Q1. Why is SUM(Revenue) / SUM(Revenue) wrong for share? Answer: both see the same filter context and return 100%. The denominator must remove the intended category filter.
Q2. Why not average row-level margins? Answer: small and large transactions would receive equal weight. Divide aggregated profit by aggregated revenue instead.
# Module 04 | Operational measures and context lab
## Practical 04B | Extend the library
```
Budget USD = SUM(FactBudget[BudgetUSD])
Revenue Budget =
CALCULATE([Budget USD], DimAccount[FSLine] = "Revenue")
Revenue Variance = [Revenue] - [Revenue Budget]
Revenue Variance % = DIVIDE([Revenue Variance], [Revenue Budget])
Order Value = SUM(FactSalesOrders[GrossAmountUSD])
Units = SUM(FactSalesOrders[Quantity])
Order Margin USD =
SUMX(FactSalesOrders,
    FactSalesOrders[GrossAmountUSD] * FactSalesOrders[MarginPct] / 100)
Order Margin % = DIVIDE([Order Margin USD], [Order Value])
AR Outstanding =
SUMX(FactARAgeing,
    FactARAgeing[AmountUSD] - FactARAgeing[AmountReceivedUSD])
AP Invoices = COUNTROWS(FactAPInvoices)
AP Exceptions =
CALCULATE([AP Invoices], FactAPInvoices[ThreeWayMatch] <> "Matched")
AP Exception % = DIVIDE([AP Exceptions], [AP Invoices])
Net Fees =
SUM(MaxhubEngagements[FeeUSD]) - SUM(MaxhubEngagements[WriteOffUSD])
Fee per Hour = DIVIDE([Net Fees], SUM(MaxhubEngagements[ActualHours]))
Utilisation =
DIVIDE(SUM(maxhub_billable_hours[BillableHours]),
    SUM(maxhub_billable_hours[AvailableHours]))
Weighted Pipeline =
SUMX(maxhub_pipeline,
    maxhub_pipeline[ExpectedFeeUSD] * maxhub_pipeline[ProbabilityPct] / 100)
```
1. Create a page called Operations. Use a column chart ProductFamily / Order Value, a matrix ServiceLine / Net Fees / Fee per Hour, and cards AP Exception % and Utilisation. Use slicers from the appropriate fact/dimension; a sales product filter should not change engagement fees.
2. Add a FactSalesOrders calculated column for interpretation only: Discount Band = IF(FactSalesOrders[DiscountPct] >= 10, "10% or more", "Below 10%"). It recalculates on refresh, not each slicer click.
3. Put Order Margin % and the arithmetic average of MarginPct side by side. Explain why the weighted measure is preferred. Remove the implicit average from the final page.
## Answers
Q1. What is the AP exception rate? Answer: 168 / 520 = 32.31%. It is a three-way-match exception rate, not a fraud rate.
Q2. Should GrossAmountUSD be discounted again? Answer: no. The source formula already deducted DiscountPct. A second discount understates order value.
Q3. Are Weighted Pipeline and Net Fees the same thing? Answer: no. The former is probability-weighted potential opportunity value; the latter is fees less write-offs on recorded engagements. Do not add them as recognised revenue.
Q4. Does Balance Check always equal zero by account? Answer: no. Individual accounts have balances. The all-account journal population nets to zero; a filtered account should generally not.
# Module 05 | Time intelligence that respects the period
## Practical 05A | Add period measures
Use the marked DimDate and its active PostingDate relationship. These measures depend on the date selection; do not use bare fact Period strings as the only filter.
```
Revenue YTD = TOTALYTD([Revenue], DimDate[Date])
Revenue PY =
CALCULATE([Revenue], SAMEPERIODLASTYEAR(DimDate[Date]))
Revenue YoY = [Revenue] - [Revenue PY]
Revenue YoY % = DIVIDE([Revenue YoY], [Revenue PY])
Revenue Rolling 3M =
CALCULATE([Revenue],
    DATESINPERIOD(DimDate[Date], MAX(DimDate[Date]), -3, MONTH))
Revenue Share of CC =
DIVIDE([Revenue],
    CALCULATE([Revenue], REMOVEFILTERS(DimCostCentre)))
CC Revenue Rank =
RANKX(ALL(DimCostCentre[CostCentreName]), [Revenue], , DESC, DENSE)
Document Date Debit =
CALCULATE([Debit USD],
    USERELATIONSHIP(DimDate[Date], FactGLJournal[DocumentDate]))
```
1. Build a matrix with YearMonth rows, Revenue, Revenue YTD, Revenue PY and Revenue YoY %. Filter dates from 1 January 2024 to 30 September 2025. Verify monthly Revenue against Monthly answers.
2. Create a second page filtered specifically 1 January-30 September 2025. PY now refers to the same nine months in 2024. Do not compare nine months of 2025 against twelve months of 2024 and call it like-for-like growth.
3. Build a cost-centre bar chart ranked descending. Revenue Share of CC retains dates but removes cost-centre filters. If using ALLSELECTED instead, explain that the denominator becomes the selected cost-centre population.
4. If you created the inactive GL DocumentDate relationship, put Debit USD and Document Date Debit in a monthly matrix. Their timing may differ even though population totals without date filters are equal.
## Answers
Q1. Why is revenue blank in October 2025? Answer: there are no GL events for that month. Do not interpret an unobserved month as an actual zero-revenue month. Default visuals to dates with observed data.
Q2. What does YTD mean here? Answer: from 1 January of the selected calendar year through the last selected date. A non-calendar financial year requires an explicit alternative year-end and a matching definition.
Q3. What does REMOVEFILTERS(DimDate) change? Answer: it removes date-table filters, not customer/account filters. It cannot remove an independent filter placed directly on GL Period. Use dimension fields consistently.
# Module 05 | Closing balances and scenario measures
## Notes
A balance is semi-additive: add accounts at one date, not balances across months. The trial balance stores each account in its normal-balance sign. Contra-assets are credit-normal and must reduce assets when you present a debit-positive balance sheet.
## Practical 05B | Build the closing engine
```
Closing Net Debit =
VAR Cutoff = MAX(DimDate[Date])
RETURN
CALCULATE([Net Debit],
    FILTER(ALL(DimDate), DimDate[Date] <= Cutoff))
TB Closing Debit Signed =
VAR Cutoff = MAX(DimDate[Date])
VAR LastSnapshot =
    CALCULATE(MAX(FactTrialBalance[PeriodEnd]),
        REMOVEFILTERS(DimDate), REMOVEFILTERS(DimAccount),
        FactTrialBalance[PeriodEnd] <= Cutoff)
RETURN
CALCULATE(
    SUMX(FactTrialBalance,
        FactTrialBalance[ClosingBalance] *
        IF(RELATED(DimAccount[NormalBalance]) = "Debit", 1, -1)),
    REMOVEFILTERS(DimDate), FactTrialBalance[PeriodEnd] = LastSnapshot)
TB Reconciliation = [Closing Net Debit] - [TB Closing Debit Signed]
```
1. Matrix: AccountCode and AccountName rows, Closing Net Debit, TB Closing Debit Signed and TB Reconciliation values. Filter to 30 September 2025, then to 31 December 2024. Every account reconciles within USD 0.01. Use only whole-population account/date filters: the TB has no cost-centre or vendor grain.
2. Repeat at 15 September 2025. Explain why GL can differ from the August month-end TB: it includes September transactions before the requested date, while the latest available TB is August. Compare only on stored month-end dates when testing exact equality.
3. Use Modeling > New parameter > Numeric range. Name it Price Change, minimum -0.20, maximum 0.20, increment 0.01, default 0. Format as Percentage. Add its slicer, then the measure below. Desktop normally creates [Price Change Value]; use your generated measure's exact name if different.
```
Scenario Revenue = [Revenue] * (1 + [Price Change Value])
Scenario Profit = [PL Result] + ([Scenario Revenue] - [Revenue])
```
## Answers and visual
Q1. What happens at +10%? Answer: scenario revenue is 1.10 × Revenue. Scenario profit rises by 0.10 × Revenue only under the stated constant-volume, constant-cost assumption. It is a sensitivity calculation, not a forecast.
Q2. Why not SUM(ClosingBalance) across 21 periods? Answer: the same accumulated balances recur at successive month ends. Select the most recent snapshot, then aggregate accounts with the correct signs.
Expected visuals: a reconciliation matrix with near-zero differences at valid month ends; a two-card baseline/scenario comparison that responds to the slider. The slider must not change historical actuals.
# Module 06 | Financial statements and reconciliation
## Practical 06A | P&L and balance sheet
1. Create a P&L page. Matrix rows: DimAccount[FSLine] then AccountName. Values: PL Signed. Columns: DimDate[YearMonth]. Visual filter: IsPL = Yes. Add Revenue, Gross Profit, Gross Margin and PL Result cards. Use a sensible manual FSLine sort rather than an arbitrary alphabetical narrative.
2. Use the following measures on a Balance Sheet page. Set the date to 30 September 2025. Assets are debit-positive; liabilities and equity are credit-positive. Contra-accounts remain correctly signed because we use GL movement rather than taking absolute values.
```
Assets =
CALCULATE([Closing Net Debit], DimAccount[AccountType] = "Asset")
Liabilities =
-CALCULATE([Closing Net Debit], DimAccount[AccountType] = "Liability")
Equity Posted =
-CALCULATE([Closing Net Debit], DimAccount[AccountType] = "Equity")
Unclosed PL =
-CALCULATE([Closing Net Debit], DimAccount[IsPL] = "Yes")
BS Check = [Assets] - [Liabilities] - [Equity Posted] - [Unclosed PL]
```
3. Make a matrix of BS FSLine / Closing Net Debit (debit-positive presentation) and cards for the five measures. Label liability credit balances clearly. Do not silently switch sign conventions between table and cards.
4. Validate against the TB engine at month end. BS Check should be 0.00. At September 2025 the unclosed P&L is the year-to-date loss; at December 2024 the explicit close has moved the annual result to retained earnings.
## Answers
Q1. Why can Assets - Liabilities - Equity Posted fail to zero before the annual close? Answer: current unclosed P&L must be included in equity for presentation. Do not post an arbitrary plug to force the report to balance.
Q2. What happens if you include Closing in the P&L? Answer: 2024 revenue and expense balances are reversed by closing entries. Operational performance is obscured; exclude Opening and Closing only for performance measures.
Q3. Can you call this statutory financial reporting? Answer: not without policies, disclosures, cash-flow classification, tax treatment and professional review. This is a reconciled training reporting pack, not a signed statutory set of accounts.
Expected visuals: monthly P&L matrix with red negative results, BS cards, account-level reconciliation matrix and a visible reporting date. Annual and monthly exact results are in the answer sections.
# Module 06 | Cash, FX and supporting schedules
## Practical 06B | Cash movement bridge
1. On a Cash page, use DimAccount[IsCashAccount] = Yes to select cash accounts. Create the following measures and filter the page to January-September 2025. Opening plus movement must equal closing.
```
Cash Movement =
CALCULATE([Net Debit], DimAccount[IsCashAccount] = "Yes")
Cash Closing =
CALCULATE([Closing Net Debit], DimAccount[IsCashAccount] = "Yes")
Cash Opening =
VAR StartDate = MIN(DimDate[Date])
RETURN
CALCULATE([Cash Movement],
    FILTER(ALL(DimDate), DimDate[Date] < StartDate))
Cash Bridge Check = [Cash Opening] + [Cash Movement] - [Cash Closing]
```
2. Build a monthly column chart with Cash Movement and a line with Cash Closing. Add cards for Cash Opening, Cash Movement, Cash Closing and Cash Bridge Check. Expected check: 0.00 for a contiguous date range without unrelated account filters.
3. For a true direct-method cash-flow statement, group cash-account GL lines by JournalID, inspect noncash counterparts and classify operating, investing, financing or cash-to-cash transfer. Exclude pure interbank transfers from external cash flows. Record uncertain allocations separately and ensure the classified sum still equals Cash Movement.
4. Build an asset-register table using AssetClass, CostUSD, AccumulatedDepreciationUSD and NBVUSD. Verify row-level CostUSD minus accumulated depreciation equals NBVUSD within rounding. Do not add monthly depreciation and NBV as if they were comparable amounts.
5. Inspect DimFXRate by FromCurrency and Period. Show AverageRate and ClosingRate as non-additive values. To practise a conversion, choose one documented foreign amount and matching currency-period rate; USD-equivalent = foreign amount × rate if the rate is explicitly USD per foreign unit. This is a worked convention, not permission to reconvert USD fields.
## Answers and limitations
Q1. Is Cash Movement already an IAS 7 statement? Answer: no. It reconciles the net cash change but does not establish operating/investing/financing classification. Net movement alone is insufficient for a full cash-flow statement.
Q2. Can bank BalanceUSD validate the GL closing cash? Answer: not in this synthetic bundle. The bank population and sequence are not a reconciled ledger cash-book extract. Present unreconciled bank items as an independent operational exception analysis.
Q3. What evidence is missing for a production cash-flow statement? Answer: reliable counterpart mapping, cash-equivalent policy, noncash transaction identification, opening/closing reconciliation and review of taxes, interest, leases and acquisitions. The correct professional answer may be “not determinable from this extract alone.”
# Module 07 | Design a report someone can use
## Notes
Choose visuals by question: trend -> line; comparison -> bar; composition -> stacked bar; relationship -> scatter; exact finance detail -> matrix; investigation detail -> table. Avoid 3D, crowded pie charts, rainbow colour scales and unexplained dual axes. Use USD labels, consistent dates, meaningful titles and accessible contrast. Never use red/green alone to communicate status.
## Practical 07 | Six report pages
1. Executive: use a 16:9 canvas. Header: “Mhondoro | performance to September 2025”. Top row: Revenue, Gross Profit, Gross Margin and PL Result cards. Middle: monthly Revenue line and cost-centre Revenue bars. Bottom: exception summary and a short limitations note. Add Year and CostCentreName slicers.
2. Financial Pack: P&L and balance sheet matrices, cash movement trend and TB reconciliation. Financial pages must display their “as at” or “period ended” date.
3. Operations: sales ProductFamily bar, AR AgeingBucket bar, AP three-way-match donut or bar, and engagement profitability table. Do not imply these separate populations reconcile to each other.
4. Forensic Workbench: exception counts, amount bands, vendor links and searchable JournalID table. Add a drill-through page with JournalID in the drill-through field and LineID, AccountName, Debit, Credit, PreparedBy and ApprovedBy in a detail table. Add a Back button.
5. Maxhub Practice: Net Fees by ServiceLine, weighted Utilisation trend and Weighted Pipeline by Stage. Keep its business identity distinct from Mhondoro.
6. AI and Methodology: churn population summary, model-evaluation results if you run a model, assumptions, data lineage and refresh timestamp. Do not display made-up accuracy values.
## Practical interactions
Create a tooltip page at tooltip size with Revenue, PL Result and YearMonth. Assign it to the monthly chart. Create bookmarks called Overview and Detail to show/hide an explanatory panel; disable bookmark Data capture if it should not reset slicers. Add a Clear Filters bookmark that intentionally captures the initial slicer state. Use Edit interactions to stop irrelevant cross-highlighting, and sync shared date slicers only across compatible pages.
Build a mobile layout with the four headline cards followed by the trend. Add alt text to meaningful visuals and put tab order in a logical reading sequence. A descriptive title should state what is measured, not claim causation.
## Questions and answers
Q1. What should a user see after drilling into a journal? Answer: all its relevant debit and credit lines under the current report filters. Show the selected JournalID visibly and explain inherited filters.
Q2. Why does a bookmark unexpectedly reset a slicer? Answer: it captured Data state. Disable that option for navigation-only bookmarks, update the bookmark and retest.
Q3. Which page is suitable for a board meeting? Answer: the executive page, with readable KPIs, period labels, one trend and exception context. The 13,929-line ledger belongs on a drill-through page, not on the front page.
# Visual reference | Monthly revenue
@CHART
This reference chart is generated directly from the CSV, using credit-minus-debit on Revenue accounts and excluding Opening/Closing. It is a visual target for the data pattern, not a Power BI screenshot.
1. Add a line chart in Desktop with DimDate[YearMonth] on the X-axis and Revenue on Y.
2. Sort ascending by YearMonthSort. Filter to January 2024-September 2025 and set the Y-axis title to Revenue (USD).
3. Add tooltips for Revenue, Revenue PY and Revenue YoY %. Use a descriptive title and avoid showing the empty future calendar as actual zero sales.
4. Verify every point against Monthly answers. Your line and this column reference should encode the same monthly amounts even though the visual forms differ.
Expected layout for the executive page: four cards across the top, the monthly trend occupying the left two-thirds, cost-centre bars on the right, slicers above and a source/period/limitations line below. Keep the current reporting period visible after slicer changes.
# Module 08 | Variance, KPIs and analytical discovery
## Practical 08A | Explain actual versus budget
1. Use a matrix with DimDate[YearMonth] rows and Revenue, Revenue Budget, Revenue Variance and Revenue Variance % values. Set the period to January-September 2025. Use cost-centre and account dimension slicers that filter both facts.
2. Add a clustered column chart Revenue versus Revenue Budget by month. Add a waterfall of Revenue Variance by cost centre to show contributors to the total. Label positive revenue variance as favourable, but positive cost variance as unfavourable.
3. For costs, define Cost Budget as CALCULATE([Budget USD], DimAccount[FSLine] = "Cost of sales"). Define Cost Variance = [Cost of Sales] - [Cost Budget]. A positive number means overspend; do not colour it green merely because it is positive.
4. Budgets are month-start facts. For these comparisons use whole calendar months. A day-level slicer that excludes the first day excludes the monthly budget row. Do not prorate silently: a daily budget requires an explicit allocation rule.
## Practical 08B | Ageing and concentration
1. On an AR page, select snapshot AsAtDate = 30 September 2025. Build AgeingBucket / AR Outstanding bars and CustomerName / AR Outstanding table sorted descending. Sort ageing buckets with an explicit helper sort index rather than alphabetically.
2. Add Overdue AR = CALCULATE([AR Outstanding], FactARAgeing[DaysOverdue] > 0), and Overdue % = DIVIDE([Overdue AR], [AR Outstanding]). Review DisputedFlag separately. AmountUSD - AmountReceivedUSD is outstanding, not original invoice value.
3. For vendor concentration, use GL positive debits as a clearly labelled expenditure indicator, not all-account Net Debit. Select accounts appropriate to procurement and avoid double-counting VAT/cash legs. Show a Pareto-style sorted bar; calculate cumulative share only after defining the denominator and scope.
4. Make a scatter using MaxhubEngagements[ActualHours] on X, Net Fees on Y and EngagementID in the detail/category field. Outliers are investigations, not automatically bad engagements. Compare planned versus actual hours before recommending prices.
## Questions and answers
Q1. What is a defensible DSO formula? Answer: average trade receivables / credit sales for the same period × days in that period. DPO similarly uses average trade payables / credit purchases × days. The supplied single AR snapshot and independent subledgers do not establish those complete inputs. A closing-AR / sales proxy must be labelled approximate and not presented as audited DSO.
Q2. Can you infer price versus volume variance from these tables alone? Answer: only after defining matching product-level baseline prices/volumes and comparable periods. Revenue versus budget is available; a full price-volume-mix bridge is not automatically supported by account-level budget.
Q3. What is the correct denominator for utilisation? Answer: total AvailableHours for the same consultant-month population. Sum BillableHours / sum AvailableHours, not average of row percentages.
Expected visuals: actual-versus-budget columns, variance waterfall, sorted ageing bar, top-customer table and engagement scatter. Every KPI needs a numerator, denominator, period, population and interpretation.
# Module 09 | Forensic analytics: rules before results
## Notes
An exception is a reason to investigate, not proof of fraud. Preserve the extract and its hash. Declare each test's population, assertion, rule, threshold, exception count and follow-up. Keep test-level counts separate from distinct flagged journals: multiple tests can hit the same journal. Never sum debit and credit legs as two separate losses.
Your CSV hides GL injection labels so you can investigate independently. AP DuplicateSuspected and vendor IsEmployeeLinked are synthetic review labels, not validated evidence. Test them against transaction patterns and bank-account matches. Exact detection may return legitimate transactions beyond the injected cases.
## Practical 09A | Six vendor and payment tests
1. Duplicate candidates: reference GL, retain Debit > 0 and nonblank VendorID. Group by VendorID and Debit, count rows and retain All Rows. Keep groups with count > 1. Expand JournalID, PostingDate and Description. Sort within each group; compare invoice references in Description and dates within 30 days. Repeated vendor amounts alone are not exact invoice duplicates. Record both entries of a pair, but potential excess payment is normally one duplicate leg, not their sum.
2. Vendor-employee link: merge DimVendor to DimEmployee on BankAccount as Text, Inner join. Expand EmployeeID and EmployeeName. Use independent shared-bank matches to compare with IsEmployeeLinked = Yes. Four supplied vendors are employee-linked, but a shared account is a risk indicator requiring ownership evidence.
3. Threshold testing: filter positive debit amounts to 4,900 <= Debit < 5,000; separately test 9,500 <= Debit < 10,000. Create USD 100 amount bins and a histogram. Label the review bands and ask whether approval controls actually apply to this population.
4. Split purchase candidates: group positive-debit vendor rows by VendorID and PostingDate. Retain row count >= 2, each individual debit < 5,000 and group sum > 5,000. Expand details and inspect Description/invoice references. Same-day routine purchases may be legitimate; injection IDs in the appendix are the adjudicated synthetic training cases, not all candidates.
5. Round-number candidates: on positive debit GL rows add IsRound = Number.Mod([Debit], 1000) = 0. Filter Debit > 5000. Compare proportions by preparer rather than claiming every round number is fraud.
6. New-vendor risk: merge vendor creation dates onto positive-debit vendor rows. Add DaysSinceCreation = Duration.Days([PostingDate] - [VendorCreatedOn]). Review 0-30 days and separately flag negative values as a source inconsistency. Missing tax clearance plus a short age strengthens an investigation priority, not a conclusion.
## Visual specification and answers
Build a vendor table with VendorID, VendorName, employee-bank match, candidate journal count and debit-side candidate value; add an amount histogram and drill-through to evidence.
Q1. How many transactions should a duplicate rule return? Answer: it depends on the precise keys, time window and treatment of repeated normal payments. Reproduce your declared rule. The hidden synthetic duplicate scheme contains 42 journals representing 21 pairs, with combined two-entry value USD 368,023.48 and potential excess USD 184,011.74. Candidate matches can exceed this.
Q2. Can the GL prove cash was paid twice? Answer: not by itself. Inspect the journal accounts and obtain bank-cleared payment evidence. A repeated expense journal is not necessarily two cash outflows.
# Module 09 | Journal, Benford and scoring workbench
## Practical 09B | Journal tests
1. Manual and out-of-hours: add Power Query custom columns Date.DayOfWeek([PostingDate], Day.Monday) >= 5 and Time.Hour(Time.From([EnteredOn])) < 7 or Time.Hour(Time.From([EnteredOn])) >= 20. Distinguish posting-date weekends from entry-timestamp weekends; they are different rules.
2. Missing/self approval: add MissingApproval using null/empty trimmed ApprovedBy. Add SelfApproved only when ApprovedBy is nonblank and equals PreparedBy. Restrict to positive-debit lines for value summaries; retain all lines for evidence.
3. Backdating: add Duration.Days([PostingDate] - [DocumentDate]) and review >= 10. Also calculate entry date minus posting date to identify late entry. Neither date gap automatically proves manipulation.
4. Segregation of duties: merge DimUser on PreparedBy and DimAccount on AccountCode. Filter preparer USR-002 and AccountType = Revenue. Inspect permission evidence rather than trusting job title alone. All-population rule counts and debit totals are printed below.
5. Unbalanced journals: group by JournalID and compare sum Debit versus sum Credit. Expected exceptions > USD 0.01: zero. Rare account/user pairs: group by PreparedBy and AccountCode, count lines, then inspect counts under three. Rarity is contextual, not inherently fraudulent.
6. Unreversed accruals: identify accrual descriptions/accounts, retain original JournalID and search subsequent periods for a documented reversal with matching amount and appropriate account. IsReversal alone is only a source flag. A missing October reversal cannot be established from data ending in September.
@RULES
## Practical 09C | Benford demonstration
Use positive GL Debit amounts >= 10 only, not both Debit and Credit legs and not account/ID numbers. In Power Query add FirstDigit = Number.FromText(Text.Start(Text.From(Number.RoundDown([Debit]), "en-US"), 1)). Group by FirstDigit, count lines, divide by total selected lines. Create an independent digit table 1-9 using Enter Data and calculate ExpectedPct = LOG10(1 + 1 / [Digit]). Left-join counts to all nine digits so absent digits remain visible. Make a clustered column comparison of observed versus expected percentage.
Expected Benford percentages for digits 1-9: 30.10%, 17.61%, 12.49%, 9.69%, 7.92%, 6.69%, 5.80%, 5.12%, 4.58%. This synthetic dataset uses bounded, repeated price bands; it is not a suitable population for a strong Benford fraud inference. A deviation is a teaching result, not a p-value proving wrongdoing.
## Practical 09D | Prioritise without double-counting
Create one row per candidate JournalID with binary flags aggregated from your line tests. Score = 30 × duplicate candidate + 20 × missing approval + 15 × weekend + 15 × self-approval + 20 × vendor-bank link. A flag contributes once per journal. Sort score descending, then positive-debit journal value descending. Keep rule versions and analyst judgement visible.
Answer: score ranges from 0 to 100 for these five binary flags. It is a judgemental priority score, not a calibrated fraud probability. Count DISTINCT JournalID for the case population, not summed test hits. A numeric count for your custom composite score is not prescribed because candidate definitions and adjudication affect the shortlist.
# Module 10 | From flags to a defensible investigation
## Practical 10 | Work one case end-to-end
1. Freeze the extract and record filename, SHA-256, source, period, extraction method, analyst and date. Keep the original read-only. Save transformation and query versions in your working papers.
2. Choose one candidate duplicate pair and one linked-vendor case from your workbench. State two competing hypotheses: duplicate payment versus legitimate repeated purchase; undisclosed conflict versus authorised shared account.
3. Create an evidence register using Enter Data: CaseID, JournalID, TestID, RuleVersion, SourceReference, CandidateAmount, Status, Owner, EvidenceRequested, Finding, ReviewedBy. SourceReference should point to the retained file and LineID/JournalID, not merely a screenshot.
4. Request purchase order, invoice, goods-received evidence, approval log, bank settlement, vendor ownership and relevant access-rights evidence. Mark unavailable items as “not provided”, not “passed”. Review access law and privacy obligations before any real investigation.
5. Write a one-page finding: condition (what the records show), criterion (policy/control expected), cause (confirmed or unresolved), risk/effect, quantified exposure and recommendation. Keep observed facts separate from interpretation.
6. Quantify each case only after resolving duplicates and overlapping tests. Use one-side values and document recoveries, reversals, unpaid invoices and legitimate repeats. Do not describe the entire exception population as confirmed loss.
7. After writing your own findings, open the Spoiler appendix. Compare your shortlisted JournalIDs with the 171 injected cases. Investigate missed cases and false positives; do not silently tune thresholds until the answer key fits.
## Worked response template
Finding: “Two journals reference the same vendor, amount and invoice description within the review window. The records are consistent with a possible duplicate posting/payment. Supporting bank-cleared payment evidence has not been supplied. Potential excess exposure is one repeated amount; confirmed loss is not determined. The payment owner should reconcile invoice, receipt and settlement records, then document correction or recovery.”
This is a better answer than “fraud was proven by Power BI”. The synthetic answer key records injected patterns, not independent legal evidence.
## Questions and answers
Q1. Why is USD 1,945,536.55 not automatically the loss? Answer: it is the one-side value associated with all 171 injected journals, including both journals in duplicate pairs and other schemes that may overlap economically. Scheme totals are teaching controls, not an audited loss calculation.
Q2. What is the injected duplicate excess if one entry of each pair is unnecessary? Answer: USD 184,011.74, assuming both were paid, neither reversed and no offset/recovery. Validate these conditions before claiming loss.
Q3. What belongs in a management summary? Answer: scope, period, procedures, top facts, quantified candidate exposure, evidence limitations, remediation owner and due date. Names alone are not evidence; avoid accusatory conclusions.
Expected deliverable: a forensic dashboard, searchable evidence register, two case write-ups and an honest limitations paragraph. Report candidate precision only after adjudicating both hits and non-hits.
# Module 11 | AI, forecasting and responsible interpretation
## Notes
Descriptive analytics explains what happened; diagnostic analysis explores associations; predictive modelling estimates unseen outcomes; prescriptive advice chooses actions under assumptions. Key Influencers is an association-discovery tool, not a causal proof. Forecasts require uncertainty intervals and a documented horizon. Feature availability and tenant policies can change: the local statistical alternatives below do not require Copilot or Fabric.
## Practical 11A | No-code discovery
1. Add a Key influencers visual. Analyse FactAPInvoices[ThreeWayMatch] and select a non-Matched category available in the data. Explain by amount, vendor category, payment terms and a HasPO column. Add HasPO in Power Query as if [PONumber] = null or Text.Trim([PONumber]) = "" then "No" else "Yes".
2. Remove IDs, duplicate flags and variables derived directly from the outcome. Note that purchase-order absence may be part of the business definition of failed matching, not an independent causal factor.
3. Record the factor, direction, sample size and definition. Expected result: an interpretable association report, or an explicit insufficient-data result. There is no guaranteed “4.2 times” coefficient; algorithm versions, filters and categories can change it. A grouped bar of exception rate by HasPO is a transparent fallback.
4. Add a decomposition tree analysing Revenue with cost centre, FSLine and account as explain-by fields. Keep account context sensible: a revenue-only measure does not become a cost measure when drilled to an expense account. Use it to discover where revenue is concentrated, not why causally.
## Practical 11B | Forecast and anomalies
1. Use a separate line chart with a continuous Date axis at monthly grain, Revenue values, a single series and data limited through September 2025. Where available, open Analytics > Forecast, select a 3-month horizon and 95% interval; document the seasonality choice. Not all visual field combinations expose forecasting.
2. For a reproducible fallback, calculate an October baseline as the arithmetic mean of July, August and September 2025 revenues in Monthly answers. Flat-repeat that estimate for November and December. This is a three-month mean baseline, not a validated seasonal forecast.
3. For backtesting, hide July-September 2025, forecast them using only data up to June, and compare with the withheld actuals. MAE = mean absolute error; RMSE = square root of mean squared error. Compare with a simple prior-month naive forecast before celebrating complexity.
4. Where available, turn on anomaly detection in a compatible time-series line chart. Document sensitivity, highlighted points and contextual follow-up. Tool outputs are exploratory; no anomaly is guaranteed solely because a training scheme exists.
## Answers
Q1. Should a 21-month series support a confident annual-seasonality claim? Answer: no. Fewer than two complete annual cycles provide weak evidence; report uncertainty and avoid an elaborate seasonal story.
Q2. Is a confidence interval a promise? Answer: no. Model assumptions, structural changes and limited history affect coverage. An unexplained exact future dollar figure is not an acceptable forecast answer.
# Module 11 | Churn classification, metrics and AI safety
## Practical 11C | A reproducible baseline
Use maxhub_client_churn. Grain is client-year, not unique client. Stayed = 0 means churn; Stayed = 1 means retained. Create Churn = 1 - Stayed. Treat the synthetic outcome timing as a training assumption: a real project needs a precise prediction date and outcome window before model features can be approved.
1. Create a Power Query reference and filter Year <= 2023 for training. Create validation Year = 2024 and test Year = 2025. Never fit preprocessing, feature selection or threshold choice on the test split. The same clients recur across years; this temporal design evaluates later outcomes for existing clients, not generalisation to new clients.
2. Compute the training majority outcome and predict it for every test row. On the supplied split the majority is churn; verify using the table below. Build a confusion matrix with actual Churn as rows and predicted Churn as columns. Use the answer calculation below before fitting a more complex model.
@TRAIN
3. Optional Python modelling: after splitting, select feature columns whose values truly precede the outcome, such as prior-year NPS, complaints and payment behaviour. Shift client-year features to the next outcome year rather than assuming same-year data was known in advance. Fit an imputer and scaler only on training rows, then logistic regression; choose the probability threshold with validation data and evaluate once on held-out test rows. Report the reduced population after lagging.
4. For a no-code reproducible training-only rule, predict churn when NPS <= 6. In Power Query add PredictedChurn = if [NPS] <= 6 then 1 else 0. Label this a concurrent illustrative rule, not a deployment-ready future prediction: timing has not been established. Build a 2×2 confusion matrix filtered to 2025 and compare with the majority baseline using the code below if desired.
5. Python/R visuals require local runtimes and libraries configured in Desktop; Service execution has additional support and refresh constraints. Use them to plot prevalidated values, not as a substitute for a governed data pipeline. Fabric AutoML/Copilot require appropriate licensing, capacity and permissions. If unavailable, your baseline and manual confusion matrix complete this lab.
## Metric answers
Treat churn as positive. Precision = TP / (TP + FP), recall = TP / (TP + FN), F1 = 2 × precision × recall / (precision + recall), accuracy = (TP + TN) / N. Report a blank/undefined precision when no positive predictions exist. A model predicting churn for everyone has recall 100%, specificity 0%, and accuracy/precision equal to test churn prevalence. High accuracy on an imbalanced sample can be trivial.
AUC requires ranked probabilities, not just a hard 0/1 decision. Calibration asks whether predicted probabilities match observed frequencies. Assess the cost of false alerts and missed churn, stability across client segments, drift and a human review path before deploying.
# Module 11 | Responsible AI and document intelligence
## Practical 11D | Safe AI use
Ask an approved AI tool: “Draft three hypotheses for this aggregated exception rate; list alternative explanations and evidence needed. Do not accuse a person or invent records.” Supply synthetic or authorised aggregate data only. Check every suggested DAX formula against the control totals. Record prompt, version, inputs, outputs and human edits. For document AI/OCR, use an authorised sample invoice and manually verify vendor, date, amount and tax fields; this bundle contains no invoice images, so OCR is a design exercise rather than an executable extraction lab.
Answer: AI output is a draft or hypothesis. It is not accounting evidence, and an invented citation or unexplained metric must be rejected.
## Practical 11E | Design an invoice-extraction workflow
This is a design lab because the delivered dataset contains structured records, not source invoice images. It does not require a paid AI account or another download.
1. Use one FactAPInvoices row to define the desired structured output: APInvoiceNo, SupplierInvoiceRef, VendorID, InvoiceDate, AmountUSD and currency convention. Identify fields missing for a production tax invoice, such as line items, tax amount and seller legal identity.
2. Sketch a pipeline: authorised document intake, OCR/extraction, schema validation, vendor-master matching, duplicate checks, human review and approved posting/export. Store a reference to the original document and extraction version.
3. Specify deterministic controls before using a model: dates parse correctly; gross equals net plus tax when those fields exist; invoice reference is retained as text; supplier matches an approved vendor; duplicate candidate rules operate on consistent currencies and amount definitions.
4. Set a review policy: route low-confidence fields, new vendors, missing references and unusual amounts to an authorised person. A high model-confidence score does not waive financial controls. Record both the extracted value and the corrected value with reviewer and timestamp.
5. Define an evaluation set of representative authorised invoices that a human has labelled. Keep it separate from prompt/threshold tuning examples. Measure field-level exact-match accuracy and monetary error, plus document-level pass rate and review workload. Do not claim a numerical extraction accuracy without running this evaluation.
## Expected answer and visual
Create a process diagram with six boxes: intake -> extract -> validate -> match -> review -> approve. Below it, create an exception table design with DocumentRef, FieldName, ExtractedValue, ProposedCorrection, Reason, Reviewer and Status. The correct result is a controlled workflow specification, not fictitious OCR output.
Q1. What if an invoice contains instructions telling an AI to ignore previous rules? Answer: treat the document as untrusted source data. It must not change workflow rules, grant access, choose a payment beneficiary or trigger unauthorised actions.
Q2. Can confidential bank details be sent to any chatbot? Answer: no. Use only approved tools under the organisation's privacy, retention, access and data-processing policies. Prefer redacted or synthetic information for learning.
Q3. What makes AI advisory credible? Answer: a defined business decision, measurable baseline, independent evaluation, clear failure handling, human accountability and a maintenance plan. A fluent summary alone is not validation.
# Module 11 | Optional exact baseline check in Python
This script uses only Python's standard library and reads the one delivered CSV directly. Run it in the folder containing the CSV (save your own scratch script outside the two-file delivery). It prints the majority baseline and the NPS rule results for the 2025 test split. It does not train a predictive model and should not be sold as one.
```
import csv
from collections import Counter

path = "Tatenda_Makuvaza_Practice_Data.csv"
with open(path, encoding="utf-8-sig", newline="") as f:
    rows = [r for r in csv.DictReader(f)
            if r["RecordType"] == "maxhub_client_churn"]
train = [r for r in rows if int(r["Year"]) <= 2023]
test = [r for r in rows if int(r["Year"]) == 2025]
majority = Counter(1-int(r["Stayed"]) for r in train).most_common(1)[0][0]

for name, predict in [
    ("Majority", lambda r: majority),
    ("NPS <= 6", lambda r: int(float(r["NPS"]) <= 6))
]:
    tp = fp = tn = fn = 0
    for r in test:
        actual, pred = 1-int(r["Stayed"]), predict(r)
        tp += actual == 1 and pred == 1
        fp += actual == 0 and pred == 1
        tn += actual == 0 and pred == 0
        fn += actual == 1 and pred == 0
    accuracy = (tp+tn) / len(test)
    precision = tp / (tp+fp) if tp+fp else None
    recall = tp / (tp+fn) if tp+fn else None
    print(name, "TP FP TN FN:", tp, fp, tn, fn)
    print("Accuracy / precision / recall:", accuracy, precision, recall)
```
Do not tune the NPS threshold by repeatedly looking at the test split. The rule above is fixed in advance for teaching. A real comparison should lock features, preprocessing and thresholds before the final evaluation and use enough independent observations to assess uncertainty.
# Module 12 | Deliver, secure and maintain
## Notes
A useful report is refreshable, secure, understandable and supported. Row-level security limits visible rows; hiding a column is not security. RLS applies according to Service roles and permissions; elevated workspace access can bypass normal consumer restrictions. Test as the intended viewer rather than as an administrator.
## Practical 12A | Publishing and RLS
1. Save a dated PBIX backup. Create a training workspace if your account allows it. Publish only synthetic data. Document semantic model ownership, source parameter, refresh credentials, audience and backup policy. If you cannot publish, complete the Desktop checks and write the deployment plan.
2. Modeling > Manage roles > create HarareOnly. Filter DimCostCentre with [CostCentreCode] = "CC200". View as this role and check that GL, budget and sales rows are restricted by their relationships. Unrelated fact tables are NOT automatically secured. Do not use this single-role exercise as a production security design.
3. Build one test matrix for each sensitive fact. Compare the role-filtered result with a normal CC200 slicer on GL/budget/sales. For a production report spanning all domains, add appropriate role filters/security relationships for every exposed population or separate reports by audience.
4. In the Service assign the role to intended Viewer users/groups and test effective access. Build permission, workspace role and sharing scope need review. Do not use Publish to web for sensitive reports; it makes data publicly accessible.
5. A local CSV source generally needs a configured gateway accessible to the Service refresh identity. Alternatively use an approved cloud file source with supported credentials. Change pCsvPath only where the Service can resolve it. Trigger refresh, examine refresh history and reconcile the same controls after success.
## Practical 12B | Performance and lifecycle
Use Performance Analyzer: Start recording, Refresh visuals, inspect slow queries. Remove unused columns, avoid high-cardinality text in visuals, limit page visuals and replace unnecessary bidirectional relationships. Import is appropriate for this CSV. DirectQuery is not a mode for querying a local CSV directly. Composite models and aggregations require an appropriate supported source and a deliberate latency/security design.
Incremental refresh is an advanced partitioning strategy using RangeStart/RangeEnd date parameters and a service policy. A non-folding CSV can still require broad file reads, so it is not a credible performance demonstration here. Document a proposed database/lakehouse source and folding strategy rather than claiming the bundle demonstrates production incremental refresh.
Track development/test/production versions, refresh tests, RLS roles, measure changes and release notes. Deployment pipelines and formal Git integration depend on platform/licensing; a documented manual release checklist is the local alternative.
## Answers
Q1. Does RLS on cost centre secure disconnected churn records? Answer: no. Security propagates only through defined relationships and roles. Test each domain or omit it from that audience's report.
Q2. What proves refresh worked? Answer: refresh history plus unchanged population/control checks (or explained, expected changes), not merely a green success banner.
Q3. How should you handle a broken refresh? Answer: preserve the last good report, capture the error, check path, credentials, gateway and schema, correct the cause and rerun controls before notifying users of restoration.
# Module 12 | Scope and price your advisory work
## Practical 12C | A consulting proposal
1. Define client decision and audience: “Monthly profitability and payment-exception monitoring for the finance manager.” Specify entities, currencies, dates, source systems and the reporting frequency.
2. List deliverables: approved data map, clean model, KPI dictionary, six report pages, RLS/refresh tests, one training session and handover guide. Exclude statutory assurance, confirmed fraud-loss opinions, source-system fixes and production ML unless separately agreed.
3. Define acceptance: journal balance within USD 0.01; zero unexplained orphan keys; control totals reconciled; correct RLS test results; refresh succeeds; designated users can explain the KPIs. Record any unresolved subledger/GL reconciliation limits.
4. Estimate hours by phase. Worked example: discovery 6, preparation 12, modelling/DAX 16, visuals 10, testing/security 8, training/handover 4 = 56 hours. At USD 50/hour base fee = USD 2,800; add a disclosed 15% contingency = USD 420; illustrative fixed quote = USD 3,220 before tax and licences. These are learning assumptions, not market rates.
5. Propose milestones: 30% mobilisation USD 966; 40% model/visual acceptance USD 1,288; 30% handover USD 966. Specify revision limits, change-control rate, client responsibilities and payment terms.
6. Write a support plan: named owner, refresh schedule, incident route, monthly access review, KPI change approval and separately priced future enhancements. Do not promise 24/7 support without pricing and staffing it.
## Questions and answers
Q1. What changes the scope? Answer: a new entity, source, reporting currency, historical backfill, extra security domain or predictive model. Estimate the impact and obtain written approval before doing unpriced additional work.
Q2. What is the difference between analytics and assurance? Answer: analytics highlights patterns and informs decisions; assurance involves an agreed professional standard, procedures and a supported conclusion. A dashboard is not an audit opinion.
Q3. What makes this a portfolio case? Answer: the problem, your modelling decisions, tested calculations, visual design, limitations, evidence of validation and a clear business recommendation. Screenshots alone do not demonstrate reconciliation or security.
Expected deliverable: a two-page proposal with a clear scope, fee, acceptance tests, responsibilities, timeline and exclusions. The worked numbers above are the price-answer key for this lab.
# Four capstones | Apply the whole learning path
## Capstone 1 | Forensic investigation (8 hours)
Brief: investigate possible duplicate postings and vendor conflicts without assuming guilt. Build the workbench, document six transaction rules and six journal/control checks, shortlist ten distinct journals, write two case findings and reconcile your tested population.
Expected visuals: risk overview, vendor links, threshold histogram, journal-detail drill-through and evidence register. Expected answer: zero unbalanced journals; four supplied employee-linked vendors; the injected scheme controls appear in the Spoiler section. Full candidate-rule counts can differ from injected cases. A sound answer distinguishes a candidate flag, a confirmed duplicate posting and a confirmed cash loss.
Marking /100: population and lineage 20; reproducible tests 25; correct one-side quantification 20; evidence/alternative explanations 20; visual usability 15. Automatic revision required if the report calls all flagged value proven fraud loss.
## Capstone 2 | Financial reporting pack (8 hours)
Brief: present January-September 2025 performance with comparable prior-year months and a 30 September 2025 balance sheet. Include the 2024 annual result for context, but label the differing period lengths.
Expected visuals: executive KPI page, monthly P&L, BS, cash-movement bridge and account-level TB reconciliation. Expected answers: annual/monthly values in the answer tables; BS Check 0.00; Cash Bridge Check 0.00; account TB differences within USD 0.01 at stored month ends. A cash-movement page must not claim full statutory cash-flow classification without counterpart review.
Marking /100: signs and closing exclusions 25; comparable periods 15; TB/BS/cash reconciliation 30; narrative 15; design 15.
## Capstone 3 | Analytics engagement (8 hours)
Brief: identify operational priorities without forcing synthetic subledgers to reconcile. Combine revenue/budget variance, AR ageing, AP matching and Maxhub utilisation in distinct pages with explicit populations.
Expected visuals: variance waterfall, overdue receivables bar, AP exception table, consultant utilisation trend and engagement fee/hour scatter. Expected answer: AP three-way-match exceptions 168/520 = 32.31%; missing receipts 81/650 = 12.46%; unreconciled bank items 129/1,400 = 9.21%. Monetary and weighted totals appear in Control answers. Recommend a review process and owner, not a causal story unsupported by evidence.
Marking /100: KPI definitions 25; correct grains 25; actionable recommendations 20; interactions 15; limitations and validation 15.
## Capstone 4 | AI advisory prototype (8 hours)
Brief: assess whether churn decision support is credible for this small dataset. Build temporal splits, reproduce the baseline, specify a leakage-safe feature plan and design a human-reviewed retention workflow.
Expected visuals: class balance, confusion matrix, threshold/cost comparison and methodology card. Expected answer: 150 client-years from 30 clients; 86 churn outcomes overall. A fixed 2025 baseline is provided in the Extended answers. No minimum model accuracy is promised; rejecting an unreliable model is a valid, professional result.
Marking /100: outcome/prediction timing 25; split/baseline 20; metric interpretation 20; governance/limitations 20; commercial proposal 15. Training accuracy alone earns no evaluation credit.
# Practical exams | Questions and solutions
## Exam A | Modelling and DAX (4 hours)
Task: from a blank PBIX, load the bundle, create a clean GL star, build Revenue, PL Result, Revenue PY and Closing Net Debit, and show a two-year matrix plus month-end reconciliation. Do not consult your prior PBIX.
Solution checklist: Bundle load off; RecordType filtering before column/type operations; account and calendar keys unique; date relationship on PostingDate; revenue credit-positive; performance excludes Opening/Closing; prior year uses the marked date dimension; balance includes all ledger movement to the cutoff. GL counts and controls must match. Award 20 marks each for import, relationships, measures, temporal logic and validation. Pass target: 70/100 with no unresolved balance error.
## Exam B | Forensic analytics (5 hours)
Task: implement duplicate candidates, employee-bank links, threshold band, manual-weekend, missing approval and self-approval rules. Produce an evidence register and explain why candidate exposure differs from loss.
Solution checklist: state exact population and thresholds; preserve both entries for duplicate evidence but use only excess when justified; exclude blank self-approval matches; use a chosen weekend date consistently; count unique journals across overlapping tests. Compare the six fixed-rule answers printed in Module 09 and the injection key only after completing your independent analysis. Award 30 for reproducibility, 25 for quantification, 25 for evidence and 20 for communication.
## Exam C | Advisory proposal (2 hours)
Task: quote the six-page reporting engagement using the worked 56-hour plan. Include acceptance, security, refresh, training and exclusions.
Solution: base USD 2,800; contingency USD 420; quote USD 3,220 before tax/licences; milestones USD 966 / 1,288 / 966. Acceptance must include controls, RLS and refresh, not just attractive charts. Award 25 each for scope, arithmetic, acceptance tests and handover/limits.
## Ten quick knowledge checks
1. Can a measure change with a slicer? Yes: its filter context changes. A stored calculated column does not recalculate per slicer click.
2. Does a one-to-many relationship require a unique “one” side? Yes; repeated keys there invalidate the intended relationship.
3. Is a snapshot additive over dates? No; choose an as-at snapshot or explicit semi-additive calculation.
4. Is 2025 a full GL year in this bundle? No; it ends 30 September 2025.
5. Can credit-normal contra-assets be shown as positive assets? Not without correcting the sign; they reduce the asset category.
6. Does Benford apply to assigned account numbers? No; assigned identifiers do not meet the underlying premise.
7. Does a bank-account match prove a ghost vendor? No; obtain ownership, independence and authorisation evidence.
8. Does a balanced GL prove every transaction is legitimate? No; balance is necessary but not sufficient.
9. Should test data determine a model threshold? No; use validation data, then evaluate once on held-out test data.
10. Does hiding a field enforce security? No; use actual data access controls and test effective permissions.
# Control answers | Exact population checks
All values below are calculated from the delivered source records. They are not made-up target numbers. No report filters are applied except the year restrictions printed in labels. “2025” for GL performance means January-September. The all-row budget total is an import control only: it mixes revenue and expenditure budgets and is not a net target.
@CONTROLS
Tolerance: money comparisons within USD 0.01; integer counts exact. Floating-point feature inputs may need reasonable decimal tolerance. If your result differs, check query filtering, source types, active relationships, page/visual filters, closing-entry exclusions and sign conventions before editing formulas.
# Monthly answers | Revenue and P&L
Population: GL excluding EntryType Opening and Closing. Revenue = credits minus debits on FSLine Revenue. P&L = credits minus debits on IsPL = Yes accounts. A monthly matrix with DimDate[YearMonth] and the workbook measures should reproduce every row below. Negative P&L denotes a loss.
@MONTHLY
For the fallback October-December forecast, calculate the simple mean of July-September 2025 revenues; see the exact baseline in Extended answers. The forecast is a training assumption, not an observed result.
# Extended answers | Financial, operational and AI checks
@EXTENDED
# Troubleshooting | Find the cause, not a plug
Wrong total by an exact multiple: inspect dimension duplicates, expanded merges and accidentally loaded helper queries. Relationship cardinality or duplicated populations are common causes.
Revenue is zero for 2024: closing entries were probably included. Use the workbook's activity measure excluding Opening and Closing, then filter FSLine = Revenue.
Budget disappears on a mid-month day: monthly budget is stored at the first day of the month. Compare full months or define a documented allocation; do not replace blank with a guessed amount.
Date slicer does nothing: check Date versus Date/Time data types, active relationships, table names and whether the slicer comes from DimDate. A disconnected table intentionally does not filter facts.
Month sort is alphabetical: sort Month by MonthNo; use YearMonth sorted by YearMonthSort for multi-year charts.
Too many blank names: inspect unmatched nonblank keys with an anti join. A blank vendor on a non-vendor GL row is expected. Do not delete it merely to improve appearance.
P&L does not tie to cash: accrual performance and cash movement are different concepts. Reconcile receivables, payables and other timing/noncash items before drawing conclusions.
Assets or liabilities seem inflated: never ABS every balance. Credit-normal contra-assets must reduce assets. Reconcile in debit-positive signs to the GL and TB.
RLS works in Desktop but not as expected online: verify assigned roles, workspace permissions and actual consumer access. Administrative/elevated workspace users are not equivalent to Viewer consumers.
Forecast/AI button missing: check supported visual fields, axis type, tenant settings and licensing. Use the deterministic baseline or grouped-rate fallback; do not invent an output for a feature you cannot run.
Refresh fails after moving files: update pCsvPath, gateway/source credentials and privacy settings appropriately. Do not disable security settings blindly to make a refresh succeed.
## Final quality checklist
[ ] Correct dataset and hash recorded; each RecordType count matches the inventory.
[ ] IDs preserved as Text; money and dates typed; errors investigated, not deleted silently.
[ ] Unique dimension keys and valid relationship directions; no accidental fact-to-fact joins.
[ ] Performance excludes closing entries; balance calculations include them.
[ ] All GL/TB/BS/cash controls reconcile at declared cutoffs.
[ ] Page titles state periods, populations, currency and units.
[ ] Report interactions, drill-through, keyboard order and mobile layout tested.
[ ] Candidate flags distinguished from proven findings and confirmed loss.
[ ] AI timing, split, baseline and limitations documented; no invented accuracy.
[ ] Every shared population covered by security tests; refresh and handover tested.
# Glossary | Keep the language precise
Grain: what one row represents. A journal line, invoice and month-end balance have different grains.
Star schema: facts linked to descriptive dimensions through unique keys, usually one-to-many and single-direction.
Filter context: the set of filters in which a DAX measure is evaluated. Row context: the current row in a column calculation or iterator.
Context transition: row context becoming filter context through CALCULATE or a measure evaluation inside row context.
Query folding: Power Query operations delegated to a capable source. Local CSV transformations do not fold to a database engine.
Snapshot: a state at a point in time. Semi-additive: can be summed across some dimensions but not across every dimension, especially time.
Normal balance: the debit or credit side that conventionally increases an account. Contra-accounts have the opposite normal balance to their containing category.
Variance: actual minus comparator, with favourable/unfavourable interpretation depending on what is measured.
RLS: row-level security. OLS: object-level security for tables/columns; hiding a field is neither.
Semantic model: data tables, relationships, measures and security rules used to answer report queries.
Data lineage: trace from reported value back through transformations to source records.
False positive: a flagged item that does not meet the investigated outcome. False negative: a real outcome missed by a test.
Precision: proportion of predicted positives that are actual positives. Recall: proportion of actual positives detected.
Leakage: information reaching a model that would not have been available at the intended prediction time, including test-set information used to fit the pipeline.
Calibration: agreement between predicted probabilities and observed outcome frequencies.
Exposure: value potentially affected under a stated assumption. Loss: substantiated economic detriment, adjusted for overlap, reversals and recovery where appropriate.
## Further reading and version notes
This pack adapts the topics and synthetic CSVs already present in tatendamakuvaza/Power_BI. It is a standalone learning edition; some original repository descriptions and lab totals may differ in detail. Use the computed answer tables and schema here for this bundle.
For changing product capabilities and licensing, consult official Microsoft Learn documentation before production deployment: learn.microsoft.com/power-bi/ ; learn.microsoft.com/power-query/ ; learn.microsoft.com/dax/ ; learn.microsoft.com/fabric/ . These are suggested references, not claims that a particular paid feature is available in your tenant.
Core calculations in this PDF have been independently checked against the CSV with Python. Power BI Desktop visual rendering, tenant publishing and Service permissions cannot be executed in the build environment; perform the local and tenant-specific acceptance tests yourself. The PDF shows specifications and a generated reference chart, not screenshots of an executed PBIX.
# Schema appendix | Field reference
The following pages list every retained source column per logical table. A sample value is a usage hint, not a complete business definition. Prefer financial source amounts as Fixed decimal where appropriate; use Decimal number for rates/features that need more than four decimals. Yes/No fields remain Text unless you explicitly convert them to logical true/false.
RecordType and RecordID are bundle-level Text fields. RecordID is a unique transport identifier, not the natural accounting key. Null fields outside a row's RecordType are intentional. Keep the columns listed for each logical table even if a particular field happens to be empty in this extract. This avoids schema drift caused by automatically deleting all-null columns.
@DICTIONARY
# Spoiler | Synthetic investigation answer key
Stop here until you have completed your independent tests and written two findings. The table below describes deliberately injected schemes. It is not the output of a universal fraud rule and it is not proof of real wrongdoing. The full journal list follows so you can audit recall and investigate false negatives at record level.
The 171 journal cases generate 342 labelled ledger lines in the source data (both sides). Those labels have been removed from your CSV. All scheme amounts below count one debit side per injected journal, not debit plus credit. The 42 duplicate journals include both members of 21 pairs.
@FORENSIC
For the duplicate scheme only, the potential excess under the stated assumptions is half its two-entry total: USD 184,011.74. The linked-vendor injected value is USD 445,568.39; a broader vendor payment population may be much larger and must not be equated to proven loss. Unreversed accrual and threshold patterns need account, policy and subsequent-event evidence before a conclusion.
Use JournalID to locate every case in FactGLJournal. In a small training model, create your own review register with one row per case; do not merge it at line level and then sum case value once per ledger line.
# Spoiler | Complete journal-level key
@JOURNALS
# Your next step | Build, explain, reconcile
Tatenda, begin with Module 01 and keep a brief learning log: what you built, what did not work, the control you used and how you corrected the issue. By the end, your portfolio should show not only attractive charts, but trusted calculations, careful evidence handling and practical business advice.
The two delivered documents are the reusable CSV and this workbook. Your PBIX files, screenshots, proposals and investigation notes are the outputs you create while completing the tasks. Keep them in a separate working folder so the original extract stays unchanged.
Completion statement: “I can explain my data grain, reproduce my control totals, defend my calculation choices, state my limitations and show the user what action the report supports.” That is the standard to aim for.
