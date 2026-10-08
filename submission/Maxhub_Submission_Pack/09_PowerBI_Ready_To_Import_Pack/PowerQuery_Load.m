// ============================================================================
// MAXHUB - Power Query (M) load script for the Power BI ready-to-import pack
// Generated 2025-10-08.  Column types were inferred from the values in
// the CSVs shipped in Data_Ready_To_Import, so this script and those files cannot
// disagree.  Table names match the repository's DAX libraries exactly.
//
// HOW TO USE
//   1. Create a parameter called DataFolder (Text) holding the full path to
//      Data_Ready_To_Import with no trailing slash, e.g. C:\Maxhub\PBI\Data
//   2. For each section below: Home > Transform data > New Source > Blank query,
//      then View > Advanced Editor, paste the section and rename the query to the
//      name in the comment.
// ============================================================================

// ---------- DimAccount ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/DimAccount.csv"),
        [Delimiter=",", Columns=18, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"AccountCode", Int64.Type},
        {"AccountName", type text},
        {"AccountType", type text},
        {"NormalBalance", type text},
        {"FSLine", type text},
        {"Statement", type text},
        {"IsCashAccount", type text},
        {"IsControlAccount", type text},
        {"IsSuspense", type text},
        {"IsPL", type text},
        {"PLSign", Int64.Type},
        {"BSSign", Int64.Type},
        {"StatementName", type text},
        {"NormalBalanceName", type text},
        {"IsRevenue", type text},
        {"IsExpense", type text},
        {"IsContra", type text},
        {"IsActive", type text}
    })
in
    Typed

// ---------- FactGLJournal ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactGLJournal.csv"),
        [Delimiter=",", Columns=54, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"LineID", type text},
        {"JournalID", type text},
        {"LineNo", Int64.Type},
        {"AccountCode", Int64.Type},
        {"PostingDate", type date},
        {"DocumentDate", type date},
        {"Period", type text},
        {"FiscalYear", Int64.Type},
        {"Description", type text},
        {"Debit", type number},
        {"Credit", type number},
        {"AmountUSD", type number},
        {"AbsAmountUSD", type number},
        {"Currency", type text},
        {"FXRate", type number},
        {"CostCentreCode", type text},
        {"PreparedBy", type text},
        {"ApprovedBy", type text},
        {"SourceSystem", type text},
        {"EntryType", type text},
        {"EnteredOn", type datetime},
        {"IsReversal", type text},
        {"VendorID", type text},
        {"CustomerID", type text},
        {"AnomalyLabel", type text},
        {"AccountName", type text},
        {"AccountType", type text},
        {"FSLine", type text},
        {"Statement", type text},
        {"StatementName", type text},
        {"IsPL", type text},
        {"PLSign", Int64.Type},
        {"BSSign", Int64.Type},
        {"NormalBalance", type text},
        {"IsCashAccount", type text},
        {"IsSuspense", type text},
        {"PLValue", type number},
        {"BSValue", type number},
        {"VendorName", type text},
        {"VendorCategory", type text},
        {"EmployeeLinkedVendor", type text},
        {"CustomerName", type text},
        {"PreparerName", type text},
        {"PreparerRole", type text},
        {"ApproverName", type text},
        {"IsApproved", type text},
        {"IsManual", type text},
        {"IsWeekendPosting", type text},
        {"IsAfterHours", type text},
        {"IsInjection", type text},
        {"SchemeID", type text},
        {"TestID", type text},
        {"Scheme", type text},
        {"RiskBand", type text}
    })
in
    Typed

// ---------- FactJournal ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactJournal.csv"),
        [Delimiter=",", Columns=33, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"JournalID", type text},
        {"PostingDate", type date},
        {"DocumentDate", type date},
        {"Period", type text},
        {"FiscalYear", Int64.Type},
        {"EntryType", type text},
        {"SourceSystem", type text},
        {"Description", type text},
        {"PreparedBy", type text},
        {"PreparerName", type text},
        {"PreparerRole", type text},
        {"ApprovedBy", type text},
        {"ApproverName", type text},
        {"IsApproved", type text},
        {"IsSelfApproved", type text},
        {"LineCount", Int64.Type},
        {"TotalDebitUSD", type number},
        {"TotalCreditUSD", type number},
        {"BalanceDiffUSD", type number},
        {"IsWeekendPosting", type text},
        {"IsAfterHours", type text},
        {"IsReversal", type text},
        {"VendorCount", Int64.Type},
        {"AccountCount", Int64.Type},
        {"TouchesSuspense", type text},
        {"TouchesRevenue", type text},
        {"IsInjection", type text},
        {"SchemeID", type text},
        {"TestID", type text},
        {"Scheme", type text},
        {"InjectionAmountUSD", type number},
        {"RiskScore", Int64.Type},
        {"RiskBand", type text}
    })
in
    Typed

// ---------- DimDate ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/DimDate.csv"),
        [Delimiter=",", Columns=22, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"Date", type date},
        {"DateKey", Int64.Type},
        {"DayName", type text},
        {"DayNameShort", type text},
        {"DayOfMonth", Int64.Type},
        {"DayOfWeekNumber", Int64.Type},
        {"IsWeekend", type text},
        {"WeekNumberISO", Int64.Type},
        {"MonthNumber", Int64.Type},
        {"MonthName", type text},
        {"MonthShort", type text},
        {"MonthYear", type text},
        {"Quarter", type text},
        {"QuarterYear", type text},
        {"FiscalYear", type text},
        {"FiscalPeriod", type text},
        {"FiscalPeriodEnd", type date},
        {"IsMonthEnd", type text},
        {"IsCurrentFY", type text},
        {"IsWeekendYN", type text},
        {"IsMonthEndYN", type text},
        {"MonthYearSort", Int64.Type}
    })
in
    Typed

// ---------- DimVendor ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/DimVendor.csv"),
        [Delimiter=",", Columns=24, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"VendorID", type text},
        {"VendorCode", type text},
        {"VendorName", type text},
        {"Category", type text},
        {"BankAccount", Int64.Type},
        {"BankName", type text},
        {"TaxClearanceNo", type text},
        {"Address", type text},
        {"PaymentTerms", Int64.Type},
        {"VendorCreatedOn", type date},
        {"LastBankChangeDate", type date},
        {"IsEmployeeLinked", type text},
        {"IsActive", type text},
        {"BankAccountMasked", type text},
        {"HasTaxClearance", type text},
        {"EmployeeLinkedFlag", type text},
        {"VendorRiskFlag", type text},
        {"GLSpendUSD", type number},
        {"GLPostings", Int64.Type},
        {"GLSpendSharePct", type number},
        {"APSpendUSD", type number},
        {"APInvoices", Int64.Type},
        {"ThreeWayExceptions", Int64.Type},
        {"ExceptionRatePct", type number}
    })
in
    Typed

// ---------- DimCustomer ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/DimCustomer.csv"),
        [Delimiter=",", Columns=17, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"CustomerID", type text},
        {"CustomerCode", type text},
        {"CustomerName", type text},
        {"Segment", type text},
        {"Currency", type text},
        {"CreditLimitUSD", Int64.Type},
        {"PaymentTerms", Int64.Type},
        {"Country", type text},
        {"AccountManager", type text},
        {"CustomerSince", type date},
        {"AROutstandingUSD", type number},
        {"ARInvoices", Int64.Type},
        {"DisputedUSD", type number},
        {"Overdue90USD", type number},
        {"AvgDaysOverdue", type number},
        {"CreditUtilisationPct", type number},
        {"CollectionsAction", type text}
    })
in
    Typed

// ---------- DimUser ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/DimUser.csv"),
        [Delimiter=",", Columns=16, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"UserID", type text},
        {"UserName", type text},
        {"JobTitle", type text},
        {"Department", type text},
        {"Role", type text},
        {"CanPostManualJE", type text},
        {"CanApprovePayment", type text},
        {"SystemAccess", type text},
        {"StartDate", type date},
        {"JournalsPrepared", Int64.Type},
        {"JournalsApproved", Int64.Type},
        {"UnapprovedJournals", Int64.Type},
        {"UnapprovedValueUSD", type number},
        {"WeekendJournals", Int64.Type},
        {"ManualJournals", Int64.Type},
        {"ExceptionsPrepared", Int64.Type}
    })
in
    Typed

// ---------- DimEmployee ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/DimEmployee.csv"),
        [Delimiter=",", Columns=13, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"EmployeeID", type text},
        {"EmployeeName", type text},
        {"Department", type text},
        {"JobTitle", type text},
        {"GradeLevel", type text},
        {"MonthlyGrossUSD", type number},
        {"DateOfBirth", type date},
        {"HireDate", type date},
        {"BankAccount", Int64.Type},
        {"NationalIDPresent", type text},
        {"TerminationDate", type date},
        {"IsFlaggedForReview", type text},
        {"BankAccountMasked", type text}
    })
in
    Typed

// ---------- DimCostCentre ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/DimCostCentre.csv"),
        [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"CostCentreCode", type text},
        {"CostCentreName", type text},
        {"Department", type text},
        {"AnnualBudgetUSD", Int64.Type}
    })
in
    Typed

// ---------- DimFXRate ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/DimFXRate.csv"),
        [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"Period", type text},
        {"PeriodEndDate", type date},
        {"FromCurrency", type text},
        {"ToCurrency", type text},
        {"AverageRate", type number},
        {"ClosingRate", type number}
    })
in
    Typed

// ---------- DimScheme ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/DimScheme.csv"),
        [Delimiter=",", Columns=18, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"SchemeKey", Int64.Type},
        {"SchemeID", type text},
        {"Scheme", type text},
        {"TestID", type text},
        {"TestName", type text},
        {"Assertion tested", type text},
        {"Control weakness", type text},
        {"Detection rule", type text},
        {"Follow-up", type text},
        {"Process area", type text},
        {"JournalsInjected", Int64.Type},
        {"ValueInjectedUSD", type number},
        {"JournalsDetected", Int64.Type},
        {"ValueDetectedUSD", type number},
        {"DetectionRatePct", type number},
        {"AnswerKeyExpected", Int64.Type},
        {"AnswerKeyDetected", Int64.Type},
        {"AnswerKeyMissed", Int64.Type}
    })
in
    Typed

// ---------- FactAPInvoices ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactAPInvoices.csv"),
        [Delimiter=",", Columns=21, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"APInvoiceNo", type text},
        {"SupplierInvoiceRef", type text},
        {"VendorID", type text},
        {"InvoiceDate", type date},
        {"DueDate", type date},
        {"AmountUSD", type number},
        {"PONumber", type text},
        {"GRNNumber", type text},
        {"ThreeWayMatch", type text},
        {"DuplicateSuspected", type text},
        {"ApprovedBy", type text},
        {"PaidStatus", type text},
        {"PaymentDate", type date},
        {"VendorName", type text},
        {"VendorCategory", type text},
        {"EmployeeLinkedVendor", type text},
        {"HasPO", type text},
        {"HasGRN", type text},
        {"DuplicateFlag", type text},
        {"ExceptionFlag", type text},
        {"ExceptionReason", type text}
    })
in
    Typed

// ---------- FactARAgeing ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactARAgeing.csv"),
        [Delimiter=",", Columns=21, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"InvoiceNo", type text},
        {"CustomerID", type text},
        {"InvoiceDate", type date},
        {"DueDate", type date},
        {"Currency", type text},
        {"AmountUSD", type number},
        {"AmountReceivedUSD", type number},
        {"DaysOverdue", Int64.Type},
        {"AgeingBucket", type text},
        {"DisputedFlag", type text},
        {"AsAtDate", type date},
        {"CustomerName", type text},
        {"Segment", type text},
        {"AccountManager", type text},
        {"OutstandingUSD", type number},
        {"SettledFlag", type text},
        {"DisputedFlagYN", type text},
        {"Overdue90Flag", type text},
        {"PriorityScore", type number},
        {"PriorityRank", Int64.Type},
        {"RecommendedAction", type text}
    })
in
    Typed

// ---------- FactBankTransactions ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactBankTransactions.csv"),
        [Delimiter=",", Columns=16, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"BankTxnID", type text},
        {"BankAccount", type text},
        {"TxnDate", type date},
        {"ValueDate", type date},
        {"Narration", type text},
        {"DebitUSD", type number},
        {"CreditUSD", type number},
        {"BalanceUSD", type number},
        {"ReconciledFlag", type text},
        {"UnmatchedItemsAgeDays", Int64.Type},
        {"AmountUSD", type number},
        {"Direction", type text},
        {"ReconciledYN", type text},
        {"ExceptionFlag", type text},
        {"AgeBucket", type text},
        {"Over90Flag", type text}
    })
in
    Typed

// ---------- FactExpenseClaims ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactExpenseClaims.csv"),
        [Delimiter=",", Columns=16, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"ClaimID", type text},
        {"EmployeeID", type text},
        {"EmployeeName", type text},
        {"ClaimDate", type date},
        {"Period", type text},
        {"ExpenseCategory", type text},
        {"ClaimedUSD", type number},
        {"ReceiptAttached", type text},
        {"ApprovedBy", type text},
        {"PaidDate", type date},
        {"DuplicateSuspected", type text},
        {"WeekendClaim", type text},
        {"ReceiptFlag", type text},
        {"ApprovedFlag", type text},
        {"ExceptionFlag", type text},
        {"ExceptionReason", type text}
    })
in
    Typed

// ---------- FactExceptionRegister ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactExceptionRegister.csv"),
        [Delimiter=",", Columns=34, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"Rank", Int64.Type},
        {"JournalID", type text},
        {"TestID", type text},
        {"TestName", type text},
        {"AllTestsFired", type text},
        {"SchemeID", type text},
        {"ExceptionDate", type date},
        {"DocumentDate", type date},
        {"EnteredOn", type datetime},
        {"Period", type text},
        {"AccountCode", Int64.Type},
        {"AccountName", type text},
        {"Description", type text},
        {"DocumentRef", type text},
        {"VendorID", type text},
        {"VendorName", type text},
        {"EmployeeLinked", type text},
        {"CounterAccount", type text},
        {"AmountUSD", type number},
        {"JournalDebits", type number},
        {"Debit", type number},
        {"Credit", type number},
        {"Preparer", type text},
        {"PreparerName", type text},
        {"PreparerRole", type text},
        {"Approver", type text},
        {"EntryType", type text},
        {"SourceSystem", type text},
        {"RiskScore", Int64.Type},
        {"RiskBand", type text},
        {"RiskWeightedValueUSD", type number},
        {"Status", type text},
        {"Conclusion", type text},
        {"ReviewedBy", type text}
    })
in
    Typed

// ---------- FactDismissedExceptions ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactDismissedExceptions.csv"),
        [Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"TestID", type text},
        {"TestName", type text},
        {"JournalID", type text},
        {"ExceptionDate", type date},
        {"Description", type text},
        {"AmountUSD", type number},
        {"Preparer", type text},
        {"ReasonDismissed", type text},
        {"PopulationNote", type text}
    })
in
    Typed

// ---------- FactTrialBalance ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactTrialBalance.csv"),
        [Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"PeriodEnd", type date},
        {"Period", type text},
        {"FiscalYear", Int64.Type},
        {"AccountCode", Int64.Type},
        {"DebitMovement", type number},
        {"CreditMovement", type number},
        {"NetMovementSigned", type number},
        {"OpeningBalance", type number},
        {"ClosingBalance", type number}
    })
in
    Typed

// ---------- FactBudget ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactBudget.csv"),
        [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"Period", type text},
        {"FiscalYear", Int64.Type},
        {"MonthNum", Int64.Type},
        {"AccountCode", Int64.Type},
        {"CostCentreCode", type text},
        {"BudgetUSD", type number},
        {"BudgetVersion", type text}
    })
in
    Typed

// ---------- FactSalesOrders ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactSalesOrders.csv"),
        [Delimiter=",", Columns=14, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"OrderNo", type text},
        {"CustomerID", type text},
        {"OrderDate", type date},
        {"Period", type text},
        {"ProductFamily", type text},
        {"ProductLine", type text},
        {"Quantity", Int64.Type},
        {"UnitPriceUSD", type number},
        {"GrossAmountUSD", type number},
        {"DiscountPct", type number},
        {"CostCentreCode", type text},
        {"SalesRep", type text},
        {"Status", type text},
        {"MarginPct", type number}
    })
in
    Typed

// ---------- FactFixedAssets ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactFixedAssets.csv"),
        [Delimiter=",", Columns=14, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"AssetID", type text},
        {"AssetDescription", type text},
        {"AssetClass", type text},
        {"CostAccountCode", Int64.Type},
        {"AccDepAccountCode", Int64.Type},
        {"LocationCode", type text},
        {"AcquisitionDate", type date},
        {"CostUSD", type number},
        {"UsefulLifeYears", Int64.Type},
        {"MonthlyDepreciationUSD", type number},
        {"AccumulatedDepreciationUSD", type number},
        {"NBVUSD", type number},
        {"DisposalDate", type date},
        {"Custodian", type text}
    })
in
    Typed

// ---------- FactPipeline ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactPipeline.csv"),
        [Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"OpportunityID", type text},
        {"ClientName", type text},
        {"Industry", type text},
        {"ServiceLine", type text},
        {"OpenedDate", type date},
        {"Period", type text},
        {"Stage", type text},
        {"ProbabilityPct", Int64.Type},
        {"ExpectedFeeUSD", type number},
        {"Source", type text},
        {"DecisionTargetDate", type date}
    })
in
    Typed

// ---------- FactServiceLineMonthly ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactServiceLineMonthly.csv"),
        [Delimiter=",", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"Month", type date},
        {"Period", type text},
        {"FiscalYear", Int64.Type},
        {"ServiceLine", type text},
        {"RevenueUSD", type number},
        {"DirectStaffCostUSD", type number},
        {"RechargeableExpensesUSD", type number},
        {"OverheadAllocatedUSD", type number},
        {"GrossProfitUSD", type number},
        {"EngagementsDelivered", Int64.Type},
        {"ProposalsSubmitted", Int64.Type},
        {"ProposalsWon", Int64.Type}
    })
in
    Typed

// ---------- FactClientChurnScored ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactClientChurnScored.csv"),
        [Delimiter=",", Columns=21, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"ClientID", type text},
        {"ClientName", type text},
        {"Industry", type text},
        {"ClientSince", Int64.Type},
        {"ClientSize", type text},
        {"Year", Int64.Type},
        {"AnnualFeeUSD", type number},
        {"ServicesPurchased", Int64.Type},
        {"NPS", Int64.Type},
        {"ComplaintsLogged", Int64.Type},
        {"AvgPaymentDays", type number},
        {"EngagementDelayDays", type number},
        {"PartnerHoursOnClient", type number},
        {"AuditFindingsRaised", Int64.Type},
        {"FeeChangePct", type number},
        {"Stayed", Int64.Type},
        {"PStay", type number},
        {"PChurn", type number},
        {"RiskBand", type text},
        {"FeeAtRiskUSD", type number},
        {"ModelVersion", type text}
    })
in
    Typed

// ---------- FactEngagementEconomics ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactEngagementEconomics.csv"),
        [Delimiter=",", Columns=17, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"EngagementID", type text},
        {"ClientName", type text},
        {"ServiceLine", type text},
        {"EngagementManager", type text},
        {"Period", type text},
        {"Status", type text},
        {"PlannedHours", type number},
        {"ActualHours", type number},
        {"OverrunPct", type number},
        {"FeeUSD", type number},
        {"WriteOffUSD", type number},
        {"RealisationPct", type number},
        {"MarginPct", type number},
        {"NPS", Int64.Type},
        {"SeverityUSD", type number},
        {"AnomalyFlag", type text},
        {"Anomaly", type text}
    })
in
    Typed

// ---------- FactRevenueForecast ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/FactRevenueForecast.csv"),
        [Delimiter=",", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"Month", type text},
        {"Moving average (3-month)", type number},
        {"Linear trend", type number},
        {"Driver based", type number},
        {"Base (mean of methods)", type number},
        {"Low", type number},
        {"High", type number},
        {"Method", type text},
        {"IsForecast", type text},
        {"Source", type text}
    })
in
    Typed

// ============================================================================
// AFTER LOADING
//   1. Model view > Manage relationships: create the relationships listed on the
//      Relationships tab of PowerBI_Data_Model.xlsx.  Auto-detect will get most of
//      them, but check the three role-playing DimDate relationships and confirm
//      nothing was created many-to-many.
//   2. Table tools > Mark as date table on DimDate (Date column = Date), then turn
//      off Auto date/time in Options > Data Load.
//   3. Hide key columns from report view.
//   4. Paste the measures from Core_Measures_Library.dax, then
//      Forensic_Tests_Library.dax, then Time_Intelligence_Library.dax.
//   5. Run the validation checks in DAX_Measures_Reference.xlsx before building
//      any visual.  Every one must tie.
// ============================================================================
