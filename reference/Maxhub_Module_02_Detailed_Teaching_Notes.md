# Module 2 — Connecting and Shaping Accounting Data with Power Query

## Learning purpose
Power Query is a recipe rather than merely a cleaned result. Every step is recorded and repeated whenever the model refreshes. This makes the work refreshable, auditable and reproducible. For an accountant or forensic practitioner, the visual is only the end product; professional value comes from proving that source records were not silently lost, changed or counted twice.

## Preserve Module 1
Before beginning, use **File > Save As** and save:
`C:\Users\Admin\Desktop\BI\Power_BI-main\powerbi\Maxhub_Lab02_Data_Source.pbix`

This preserves `Maxhub_Lab01.pbix` as the completed first submission.

## Import the 17 accounting queries
Use **Home > Get data > Excel workbook** and open:
`C:\Users\Admin\Desktop\BI\Power_BI-main\data\xlsx\Mhondoro_Accounting_Data.xlsx`

Select the following 17 queries and choose **Transform Data**:
- Dimensions: DimAccount, DimCostCentre, DimCustomer, DimDate, DimEmployee, DimFXRate, DimUser and DimVendor.
- Facts: FactAPInvoices, FactARAgeing, FactBankTransactions, FactBudget, FactExpenseClaims, FactFixedAssets, FactGLJournal, FactSalesOrders and FactTrialBalance.

Do not select `READ ME` or `InjectionLog`. InjectionLog is the forensic answer key and must remain hidden until after Lab 09.

### Common workbook structure correction
For each imported worksheet:
1. If Power Query shows Column1, Column2, etc., locate the real heading row.
2. Use **Home > Remove Rows > Remove Top Rows** and remove the note and blank row above the headings (normally two rows).
3. Use **Home > Use First Row as Headers**.
4. Rename the steps to explain the reason, for example `Remove workbook note and blank row` and `Promote accounting field names`.
5. Assign types only after headings and text indicators are corrected.
6. Use **View > Column quality**, **Column distribution** and **Column profile**; change profiling to the entire dataset.

Identifiers such as account codes, user IDs, vendor IDs and bank accounts are Text, even if they contain only digits. Monetary values are Decimal number. Counts and day numbers are Whole number. Dates are Date and timestamps are Date/Time.

## Converting Yes/No fields
Power Query's True/False type does not automatically accept text values `Yes` and `No` in every import. If conversion produces errors:
1. Delete the failed Changed Type step.
2. Keep the field as Text.
3. Replace `Yes` with `true` and `No` with `false`.
4. Assign True/False after replacement.

This correction was required for account indicators, user permissions, vendor indicators, employee indicators, date indicators and several transaction flags.

## Dimension tables
### DimAccount — 71 rows
Fields and types:
- Text: AccountCode, AccountName, AccountType, NormalBalance, FSLine, Statement.
- True/False: IsCashAccount, IsControlAccount, IsSuspense, IsPL.
- Whole number: PLSign.

AccountCode must be Text because it is an identifier. Standardise the four Yes/No fields before applying True/False. Confirm 71 rows, 71 distinct/unique AccountCode values and no errors.

### DimCostCentre — 9 rows
- Text: CostCentreCode, CostCentreName, Department.
- Decimal number: AnnualBudgetUSD.

Confirm nine rows and nine distinct/unique CostCentreCode values.

### DimUser — 12 rows
- Text: UserID, UserName, JobTitle, Department, Role, SystemAccess.
- True/False: CanPostManualJE, CanApprovePayment.
- Date: StartDate.

Convert dates using English (United Kingdom) locale if required. User data later supports segregation-of-duties and authorisation testing. Confirm 12 unique users and no errors.

### DimVendor — 26 rows
- Text: VendorID, VendorCode, VendorName, Category, BankAccount, BankName, TaxClearanceNo, Address.
- Whole number: PaymentTerms.
- Date: VendorCreatedOn, LastBankChangeDate.
- True/False: IsEmployeeLinked, IsActive.

Bank accounts and tax numbers remain Text to preserve leading zeros and avoid inappropriate arithmetic. Keep a missing LastBankChangeDate as null; never invent a date. Confirm 26 unique VendorID values.

### DimCustomer — 18 rows
- Text: CustomerID, CustomerCode, CustomerName, Segment, Currency, Country, AccountManager.
- Decimal number: CreditLimitUSD.
- Whole number: PaymentTerms.
- Date: CustomerSince.

A zero credit limit is different from null: zero is a known rule, whereas null means unknown or unsupplied. Confirm 18 unique customers.

### DimEmployee — 63 rows
- Text: EmployeeID, EmployeeName, Department, JobTitle, GradeLevel, BankAccount.
- Decimal number: MonthlyGrossUSD.
- Date: DateOfBirth, HireDate, TerminationDate.
- True/False: NationalIDPresent, IsFlaggedForReview.

GradeLevel and BankAccount are identifiers/classifications and remain Text. Active employees may have null TerminationDate values. A review flag is analytical evidence, not a row to delete. Confirm 63 unique EmployeeID values.

### DimDate — 1,461 rows
- Date: Date, FiscalPeriodEnd.
- Whole number: DateKey, DayOfMonth, DayOfWeekNumber, WeekNumberISO, MonthNumber.
- Text: DayName, DayNameShort, MonthName, MonthShort, MonthYear, Quarter, QuarterYear, FiscalYear, FiscalPeriod.
- True/False: IsWeekend, IsMonthEnd, IsCurrentFY.

Date and DateKey must both be unique. MonthNumber must range from 1 to 12, and DayOfWeekNumber from 1 to 7. In the model, MonthName will later be sorted by MonthNumber.

### DimFXRate — 84 rows
- Text: Period, FromCurrency, ToCurrency.
- Date: PeriodEndDate.
- Decimal number: AverageRate, ClosingRate.

Average rates generally support income-statement translation and closing rates support period-end monetary balances, subject to the applicable reporting framework. Period alone can repeat; a logical record uses Period + FromCurrency + ToCurrency. Confirm 84 rows and positive rates.

## Fact tables
### FactGLJournal — 13,929 rows
Correct headings, then remove `AnomalyLabel`. It exposes the injected forensic answers and must not be available during detection work.

Types:
- Text: LineID, JournalID, AccountCode, Period, Description, Currency, CostCentreCode, PreparedBy, ApprovedBy, SourceSystem, EntryType, VendorID, CustomerID.
- Whole number: LineNo, FiscalYear.
- Decimal number: Debit, Credit, AmountUSD, AbsAmountUSD, FXRate.
- Date: PostingDate, DocumentDate.
- Date/Time: EnteredOn.
- True/False: IsReversal, after converting Yes/No.

Blank VendorID and CustomerID values are valid where a journal does not relate to those entities. Confirm 13,929 unique LineID values and no errors.

Add two custom columns:
```powerquery
AmountSigned = [Debit] - [Credit]
AmountAbs = Number.Abs([AmountSigned])
```
Set both to Decimal number. Debit lines become positive and credit lines negative. AmountSigned supports balances and statements; AmountAbs supports thresholds, duplicates, round-number tests and Benford analysis. Preserve the original source amount columns.

Known ledger controls for later reconciliation:
- 5,504 journals.
- Total debit: $122,878,886.54.
- Total credit: $122,878,886.54.
- Total signed difference: $0.00.

### FactTrialBalance — 1,323 rows
- Date: PeriodEnd.
- Text: Period, AccountCode.
- Whole number: FiscalYear.
- Decimal number: DebitMovement, CreditMovement, NetMovementSigned, OpeningBalance, ClosingBalance.

The expected logic is DebitMovement minus CreditMovement equals NetMovementSigned, and OpeningBalance plus NetMovementSigned equals ClosingBalance, subject to immaterial rounding. Period + AccountCode is the composite record key.

### FactARAgeing — 420 rows
- Text: InvoiceNo, CustomerID, Currency, AgeingBucket.
- Date: InvoiceDate, DueDate, AsAtDate.
- Decimal number: AmountUSD, AmountReceivedUSD.
- Whole number: DaysOverdue.
- True/False: DisputedFlag.

AsAtDate is the historical reporting date; do not recalculate ageing using today's date. Outstanding value is conceptually AmountUSD minus AmountReceivedUSD. A duplicate invoice number must be investigated, not blindly removed.

### FactAPInvoices — 520 rows
- Text: APInvoiceNo, SupplierInvoiceRef, VendorID, PONumber, GRNNumber, ThreeWayMatch, ApprovedBy, PaidStatus.
- Date: InvoiceDate, DueDate, PaymentDate.
- Decimal number: AmountUSD.
- True/False: DuplicateSuspected.

Keep null purchase orders, GRNs, approvers and payment dates because they can be control exceptions or valid unpaid transactions. A three-way match compares the purchase order, goods received note and supplier invoice. An exception is not automatically fraud or confirmed loss.

### FactBankTransactions — 1,400 rows
- Text: BankTxnID, BankAccount, Narration.
- Date: TxnDate, ValueDate.
- Decimal number: DebitUSD, CreditUSD, BalanceUSD.
- True/False: ReconciledFlag.
- Whole number: UnmatchedItemsAgeDays.

TxnDate and ValueDate can legitimately differ. Preserve the source debit/credit convention until it is tested against the running balance. Confirm 1,400 unique BankTxnID values. Later targets include 129 unreconciled transactions, 27 older than 90 days and an oldest item of 210 days.

### FactExpenseClaims — 650 rows
- Text: ClaimID, EmployeeID, EmployeeName, Period, ExpenseCategory, ApprovedBy.
- Date: ClaimDate, PaidDate.
- Decimal number: ClaimedUSD.
- True/False: ReceiptAttached, DuplicateSuspected, WeekendClaim.

Keep null PaidDate or ApprovedBy where appropriate. Missing receipts, weekends and duplicate indicators are exceptions requiring review, not proof of fraud. Confirm 650 unique ClaimID values. The dataset contains 81 claims without receipts for later analytical reproduction.

### FactSalesOrders — 900 rows
- Text: OrderNo, CustomerID, Period, ProductFamily, ProductLine, CostCentreCode, SalesRep, Status.
- Date: OrderDate.
- Whole number: Quantity.
- Decimal number: UnitPriceUSD, GrossAmountUSD, DiscountPct, MarginPct.

DiscountPct and MarginPct contain percentage points such as 15 or 33.3. Keep them as Decimal number now; applying Percentage directly would display 15 as 1,500%. Keep cancelled orders as operational evidence. Sales orders are not automatically recognised accounting revenue. Confirm 900 unique OrderNo values.

### FactBudget — 1,299 rows
- Text: Period, AccountCode, CostCentreCode, BudgetVersion.
- Whole number: FiscalYear, MonthNum.
- Decimal number: BudgetUSD.

The grain is one row per Period + AccountCode + CostCentreCode + BudgetVersion. Keep BudgetVersion to support original, revised and forecast scenarios. Known later controls are approximately $28,277,255 for FY2024 and $22,211,749 for FY2025.

### FactFixedAssets — 120 rows
- Text: AssetID, AssetDescription, AssetClass, CostAccountCode, AccDepAccountCode, LocationCode, Custodian.
- Date: AcquisitionDate, DisposalDate.
- Decimal number: CostUSD, MonthlyDepreciationUSD, AccumulatedDepreciationUSD, NBVUSD.
- Whole number: UsefulLifeYears.

Keep null DisposalDate for assets with no recorded disposal. Account and location codes remain Text. Cost minus accumulated depreciation should normally equal NBV, subject to rounding. Confirm 120 unique AssetID values.

## Final review and first load
Before loading, click every query and confirm:
- no Column1/Column2 headings or workbook notes remain;
- no errors;
- IDs are Text, dates are Date, timestamps are Date/Time, money is Decimal and flags are True/False;
- intentional nulls remain null;
- FactGLJournal has no AnomalyLabel and includes AmountSigned and AmountAbs.

Use **Home > Close & Apply**, wait for all 17 tables to load, inspect FactGLJournal in Table view, and save the PBIX. Do not accept or modify automatic relationships yet; relationships will be built deliberately in Module 3.

## Deliberately messy-data exercise
Import only `MessyData` from `PowerBI_Practice_Workbook.xlsx` and choose Transform Data. Remove the note and blank row, promote headings, and rename the heading `Region ` to `Region`.

The exercise demonstrates inconsistent casing, whitespace, mixed date formats, currency symbols inside amounts, commas/spaces in numbers, `n/a` in a numeric field, blanks and an exact duplicate. It is separate training data and should not be mixed into the accounting model.

### Clean Customer and Region
Select Customer and Region and apply **Transform > Format > Trim**, then **Clean**, then **Capitalize Each Word**. Trim removes leading/trailing whitespace; Clean removes non-printing characters. Capitalisation does not resolve legal-name variants such as `Beta Ltd` versus `Beta Ltd.`—that requires controlled mapping or fuzzy matching. Set Sale ID to Text.

### Clean Amount
If replacing `R` fails, Amount is probably Any rather than Text. Delete the failed step, set Amount to Text, use Replace Values and ensure `Match entire cell contents` is off.

Remove these characters while Amount is Text:
- `R` → empty;
- `$` → empty;
- comma → empty;
- one space → empty.

Examples become `R 2 500.50` → `2500.50`, `$3,100` → `3100`, and `4 800.75` → `4800.75`.

Convert Amount using **Change Type > Using Locale**, Decimal number, English (United States), because the cleaned decimal separator is a period. Exclude the one null-Amount row and document that no zero was substituted. Fourteen rows remain.

### Clean Units
Keep Units as Text while replacing the complete value `n/a` with null, then change Units to Whole number. Keep the null-Units record because its Amount is valid. Null means unknown; zero would mean a known sale of no units.

### Standardise Sale Date
Use **Change Type > Using Locale**, Date, English (United Kingdom). This interprets `01/03/2021` as 1 March, consistent with Zimbabwe/UK date conventions. Mixed values such as ISO dates, hyphenated dates and `4 March 2021` should all convert. Keep the one missing Sale Date as null rather than inferring it.

### Preserve duplicate evidence
Do not blindly remove duplicates. Use **Home > Group By > Advanced**, group by all six original fields (Sale ID, Sale Date, Customer, Amount, Region, Units), and add `DuplicateCount` using Count Rows. Add a custom True/False column:
```powerquery
DuplicateFlag = [DuplicateCount] > 1
```
The resulting table has 13 analytical rows. One row has DuplicateCount 2 and DuplicateFlag TRUE. This preserves evidence that the supplied source contained two identical records. It does not prove that two payments occurred.

Methodology summary: the source contained 15 rows. Text was trimmed, cleaned and standardised. Amount was normalised and one null-Amount record excluded, leaving 14 usable source rows. One exact duplicate pair was consolidated while preserving its count and flag, leaving 13 analytical rows. Missing Sale Date, Region and Units values were retained as null. Close & Apply and save the PBIX.

## Reporting-date parameters
Open Power Query and use **Home > Manage Parameters > New Parameter**.

Create:
- `pReportStartDate`: Type Date, current value 01/01/2024, description “First posting date included in the reporting model”.
- `pReportEndDate`: Type Date, current value 30/09/2025, description “Last posting date included in the reporting model”.

Select FactGLJournal and filter PostingDate using a custom date filter: PostingDate is after or equal to pReportStartDate AND before or equal to pReportEndDate. Rename the step `Keep postings within parameter reporting period`.

If the interface does not offer parameters, add a step with the formula bar, replacing the previous-step name with the exact actual name:
```powerquery
= Table.SelectRows(
    #"Previous Step Name",
    each [PostingDate] >= pReportStartDate
        and [PostingDate] <= pReportEndDate
)
```
The source already lies inside this reporting window, so FactGLJournal should remain at 13,929 rows. Confirm no errors, Close & Apply, and save.

## Professional principles learned so far
1. Clean the structure before assigning types.
2. Use descriptive Applied Step names as an audit trail.
3. Treat IDs as Text, even when they look numeric.
4. Keep null, zero and blank conceptually distinct.
5. Do not invent missing dates, amounts or approvers.
6. Do not delete suspicious records merely because they are inconvenient.
7. An exception is not proof of fraud or confirmed loss.
8. Preserve source fields and add analytical fields.
9. Reconcile row counts and keys after every transformation.
10. Parameters make refresh periods controlled and reviewable.
