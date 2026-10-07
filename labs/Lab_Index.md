# Lab Index — hands-on exercises

Every lab is written to be done with the module open beside you. Where a lab has an expected
result, it is printed so you can prove your model works before moving on.

**Before you start:** open `data/xlsx/Mhondoro_Accounting_Data.xlsx` once and read the READ ME sheet.
Note that the `InjectionLog` sheet is the answer key — do not open it until Lab 09 tells you to.

| Lab | Module | Time | You will produce |
|---|---|---|---|
| [Lab 01 — First report in 40 minutes](#lab-01--first-report-in-40-minutes) | 1 | 40 min | A published 5-visual report |
| [Lab 02 — The data source layer](#lab-02--the-data-source-layer) | 2 | 2 h | A cleaned, parameterised data source |
| [Lab 03 — Model the Mhondoro warehouse](#lab-03--model-the-mhondoro-warehouse) | 3 | 3 h | A validated star schema |
| [Lab 04 — Twenty-five core measures](#lab-04--twenty-five-core-measures) | 4 | 3 h | The `_Measures` library in your model |
| [Lab 05 — The time and balance engine](#lab-05--the-time-and-balance-engine) | 5 | 3 h | YTD, comparatives, closing balances that tie |
| [Lab 06 — The financial reporting pack](#lab-06--the-financial-reporting-pack) | 6 | 4 h | P&L, BS, cash flow, close pack |
| [Lab 07 — Executive dashboard to spec](#lab-07--executive-dashboard-to-spec) | 7 | 3 h | A board-ready one-page dashboard |
| [Lab 08 — Variance & exception pages](#lab-08--variance--exception-pages) | 8 | 3 h | Budget variance, KPIs, exception pages |
| [Lab 09 — The forensic workbench](#lab-09--the-forensic-workbench) | 9 | 5 h | Five-page forensic analytics tool |
| [Lab 10 — The investigation](#lab-10--the-investigation) | 10 | — | See Capstone 1 |
| [Lab 11 — Churn model and anomaly detection](#lab-11--churn-model-and-anomaly-detection) | 11 | 3 h | Scored clients + anomaly page |
| [Lab 12 — Propose and price](#lab-12--propose-and-price) | 12 | 2 h | A client-ready proposal |

---

## Lab 01 — First report in 40 minutes

**Objective:** complete the whole pipeline once: import → visual → publish.

**Steps**

1. Power BI Desktop ▸ **Get Data ▸ Excel workbook** ▸ `data/xlsx/PowerBI_Practice_Workbook.xlsx`.
2. Select **SimpleData** only ▸ **Transform Data** ▸ check the 12 rows and the column types are
   (`Month` text, `Sales` whole number, `Units` whole number) ▸ **Close & Apply**.
3. Build, in this order, giving each a sentence title:
   1. **Line chart** — Axis `Month`, Values `Sales` → title "Sales rose from $125k in January to $238k in December".
   2. **Clustered column** — Axis `Region`, Values `Sales` → "North and East lead on revenue".
   3. **Matrix** — Rows `Region`, Columns `Product`, Values `Sales`.
   4. **Card** — `Sales` (rename the measure later; for now accept the default aggregation).
   5. **Pie chart** — Legend `Product`, Values `Sales`.
4. Add a **slicer** on `Month` (Visualisations ▸ Slicer) and set it to *Dropdown*.
5. **File ▸ Save as** `Maxhub_Lab01.pbix`, then **Home ▸ Publish ▸ My workspace**.
6. In the Service, open the report and pin the line chart to a new dashboard. Look at it on your phone browser.

**Checkpoint:** you can explain what each of the four view icons on the left does.

---

## Lab 02 — The data source layer

**Objective:** import every Mhondoro table, clean it properly, and make the data layer refreshable.

### Part A — Import and type (40 min)

1. **Get Data ▸ Excel workbook** ▸ `data/xlsx/Mhondoro_Accounting_Data.xlsx` ▸ select **all** tables
   except `READ ME` and `InjectionLog` ▸ **Transform Data**.
2. For each query, in Power Query:
   - Set key columns to **Text**: `AccountCode`, `CostCentreCode`, `VendorID`, `CustomerID`,
     `EmployeeID`, `UserID`, `LineID`, `JournalID`, `Period`.
   - Set dates to **Date** (`PostingDate`, `DocumentDate`, `Date`, `InvoiceDate`, `DueDate`, `ClaimDate`);
     `EnteredOn` to **Date/Time**.
   - Set amounts to **Decimal Number** (`Debit`, `Credit`, `AmountUSD`, `AbsAmountUSD`, `BudgetUSD`, …).
   - If any column shows **Error**, click the error and read the message before changing anything.
3. Confirm the row counts (bottom-left of the status bar) against this table:

| Table | Expected rows |
|---|---|
| DimAccount | 71 |
| DimCostCentre | 9 |
| DimUser | 12 |
| DimDate | 1,461 |
| DimVendor | 26 |
| DimCustomer | 18 |
| DimEmployee | 63 |
| **FactGLJournal** | **13,929** |
| FactTrialBalance | 1,323 |
| FactARAgeing | 420 |
| FactAPInvoices | 520 |
| FactSalesOrders | 900 |
| FactBudget | 1,299 |
| FactBankTransactions | 1,400 |
| FactExpenseClaims | 650 |
| FactFixedAssets | 120 |
| DimFXRate | 84 |

### Part B — Clean the MessyData table (40 min)

Import the `MessyData` sheet and apply, in order: promote headers ▸ trim text ▸ Proper-case
`Customer` ▸ strip `R`, `$`, commas and spaces from `Amount` ▸ convert `Units` (`"n/a"` → null) ▸
convert `Sale Date` with locale **en-GB** (the source is a South African/Zimbabwean file) ▸ remove rows
where `Amount` is null ▸ remove the exact duplicate rows **after** adding a `DuplicateFlag` column.

**Deliverable:** a written note listing, for each change: what you did, how many rows were affected and why.

### Part C — Signed amounts and parameters (40 min)

1. In `FactGLJournal`, add:
   - `AmountSigned = [Debit] - [Credit]`
   - `AmountAbs = Number.Abs([AmountSigned])`
2. Create parameters `pReportStartDate` (Date, 2024-01-01) and `pReportEndDate` (Date, 2025-09-30),
   then add a filter step using them.
3. Remove load (**Enable load = off**) from any intermediate query, and rename staging queries with a `stg_` prefix.
4. Delete the `AnomalyLabel` column from `FactGLJournal`'s final query.

**Checkpoint — the numbers that must not move**

| Test | Expected |
|---|---|
| Rows in `FactGLJournal` after all cleaning | 13,929 |
| Total debits | 122,878,886.54 |
| Total credits | 122,878,886.54 |
| Rows dropped by cleaning | 0 (record the reason if not) |

**Troubleshooting:** if the row count has changed, check whether you filtered on `PostingDate` when a
2023 date came from `DimDate` — the period parameter should only apply to the GL.

---

## Lab 03 — Model the Mhondoro warehouse

**Objective:** build the star schema and prove it is sound.

**Steps**

1. In **Model view**, create these relationships (all one-to-many, single direction):

| Dimension | Fact | Key |
|---|---|---|
| DimAccount | FactGLJournal | AccountCode |
| DimCostCentre | FactGLJournal | CostCentreCode |
| DimVendor | FactGLJournal | VendorID |
| DimCustomer | FactGLJournal | CustomerID |
| DimUser | FactGLJournal | PreparedBy *(active)* |
| DimUser | FactGLJournal | ApprovedBy *(inactive)* |
| DimDate | FactGLJournal | Date → PostingDate *(active)* |
| DimDate | FactGLJournal | Date → DocumentDate *(inactive)* |
| DimDate | FactTrialBalance | Date → PeriodEnd |
| DimDate | FactARAgeing / FactAPInvoices / FactSalesOrders | date columns *(one active date relationship each)* |
| DimAccount + DimCostCentre + DimDate | FactBudget | AccountCode + CostCentreCode + Period |
| DimVendor | FactAPInvoices | VendorID |
| DimCustomer | FactARAgeing | CustomerID |
| DimEmployee | FactExpenseClaims | EmployeeID |

2. Right-click `DimDate` ▸ **Mark as date table** ▸ `Date`.
3. Sort `DimDate[MonthName]` by `MonthNumber`; `DimDate[MonthYear]` by `MonthNumber`.
4. `DimAccount[AccountCode]` and every other code: sort by their natural order, and **hide** all key
   columns from the report view (right-click ▸ *Hide in report view*) so users see names, not codes.
5. Create the three validation measures and check them:

```dax
Total Debits = SUM ( FactGLJournal[Debit] )
Total Credits = SUM ( FactGLJournal[Credit] )
GL Lines = COUNTROWS ( FactGLJournal )
Balance Check = [Total Debits] - [Total Credits]
GL Lines With Unknown Account =
COUNTROWS ( FILTER ( FactGLJournal, NOT FactGLJournal[AccountCode] IN VALUES ( DimAccount[AccountCode] ) ) )
```

**Expected results**

| Check | Expected value |
|---|---|
| GL Lines | 13,929 |
| Balance Check | 0.00 |
| GL Lines With Unknown Account | 0 |
| Journal lines with a vendor | 5,226 (all supplier-related lines) |
| Distinct accounts used | 64 |

6. Draw the model on one page (a screenshot of Model view is fine) and write a 10-line
   "model description" memo: grain of each fact, relationships, known limitations.

**Troubleshooting:** if a relationship shows "many-to-many", the key on the dimension side is not
unique — investigate before forcing it. If a slicer does nothing, the filter is trying to cross a
one-directional relationship; fix the model, do not add bidirectional filters.

---

## Lab 04 — Twenty-five core measures

**Objective:** build the whole core library from
[`../dax/Core_Measures_Library.dax`](../dax/Core_Measures_Library.dax) and verify each number.

**Steps**

1. **Modeling ▸ New table** → `_Measures = ROW ( "Note", "Course measures" )`.
2. Create display folders: `00 Data quality`, `01 Profit or loss`, `02 Balance sheet`,
   `03 Working capital`, `04 Time`, `05 Budget`, `06 AR`, `07 AP`, `08 Payroll`, `09 Bank`, `10 Helpers`.
3. Paste measures from the core library, folder by folder, setting the format string on each:
   `$#,##0` for amounts, `0.0%` for ratios, `#,##0` for counts.
4. Build a matrix to test: Rows `DimAccount[FSLine]`, Columns `DimDate[FiscalYear]`, Values `Total Revenue`,
   `Cost of Sales`, `Gross Profit`, `Gross Margin %`.

**Expected results (FY2024 / FY2025 to September)**

| Measure | FY2024 | FY2025 (9 months) |
|---|---|---|
| Total Revenue | 13,786,573 | 10,543,059 |
| Cost of Sales | ≈ 8,418,000 | ≈ 6,830,000 |
| Gross Margin % | 49.3% | 50.5% |
| Operating Profit | 447,052 | -61,867 |
| Profit After Tax | 447,052 | -61,867 |
| Total debits = credits | 122,878,886.54 | — |

5. Reconcile: `Assets Total − (Liabilities Total + Equity Total) = -61,867` = `Current Year Result` (a loss to date).
   Write down why (Module 6, §6.4).

**Troubleshooting:** if `Total Revenue` is negative, you forgot the `* -1` (revenue is a credit
balance in the ledger). If gross margin looks like ~5%, you subtracted instead of adding a negative
cost of sales.

---

## Lab 05 — The time and balance engine

**Objective:** the accountant-grade calculations, validated against the pre-built trial balance.

**Steps**

1. Build the time library from [`../dax/Time_Intelligence_Library.dax`](../dax/Time_Intelligence_Library.dax):
   `Revenue YTD`, `Revenue LY`, `Revenue Same Period LY`, `Revenue 3M Moving Average`, `Seasonal Index`.
2. Build the balance engine: `Opening Balance`, `Closing Balance`, `Closing Balance Period End`,
   `Balance Movement`, `Balance Reconciliation`.
3. Build the validation measures:

```dax
TB Extract Closing =
CALCULATE ( SUM ( FactTrialBalance[ClosingBalance] ), DimAccount[AccountType] = "Asset" )
Balance Engine Difference = [Assets Total] - [TB Extract Closing]
```

4. Matrix: Rows `DimAccount[AccountName]` (filter to Balance sheet accounts), Columns `DimDate[MonthYear]`,
   Values `Closing Balance`. Check that each month's closing equals the prior month's closing plus the movement.

**Expected results**

| Check | Expected |
|---|---|
| `Balance Reconciliation` on any month/account | "Ties" |
| `Assets Total` at 30 Sep 2025 | 8,949,384 |
| `Receivables Balance` at 30 Sep 2025 | 3,790,174 |
| `Payables Balance` at 30 Sep 2025 | 2,373,621 |
| `Suspense Balance` | 51,059 |
| `Cash Balance` | 792,548 |

**Troubleshooting:** if `Closing Balance` is blank in a month with no postings for that account, the
cumulative pattern is still correct — check the account had a balance carried in. If `Opening Balance`
equals `Closing Balance` in the first month of data, your `DimDate` starts too late; extend it back to 2023.

---

## Lab 06 — The financial reporting pack

**Objective:** four pages that a CFO would accept as a management pack.

### Page 1 — Profit or loss
- Slicers: `DimDate[FiscalYear]`, `DimDate[MonthYear]`, `DimCostCentre[CostCentreName]`.
- Matrix: Rows `Statement Rows[RowLabel]`; Columns `DimDate[MonthYear]`; Values `Statement Amount`,
  `Budget by FSLine`, `Variance $`, `Variance %`; conditional background formatting from `Variance Colour`;
  bold subtotal rows.
- Waterfall: prior month operating profit → revenue → cost of sales → opex → current month operating profit.
- One card carrying `PL Commentary`.

### Page 2 — Balance sheet
- Rows `FSPresentation[FSLine]` where `Statement = "BS"`, sorted by `FSSortOrder`.
- Columns `Opening Balance`, `Balance Movement`, `Closing Balance`.
- Cards: `Assets Total`, `Liabilities Total`, `Equity Total`, `Current Year Result`, **`BS Check`**.

### Page 3 — Cash flow
- Waterfall of `Cash Flow Category` movements.
- Cards `Opening Cash`, `Net Cash Movement`, `Closing Cash`.

### Page 4 — Close pack
- Nine control cards (Module 6, §6.6), each showing the expected value.

**Expected results**

| Check | Expected |
|---|---|
| `BS Check` | 0.00 |
| `Debit Total - Credit Total` | 0.00 |
| `Unbalanced Journals` | 0 |
| `GL Lines With Unknown Account` | 0 |
| `Closing Cash` (Sep 2025) | 792,548 |
| Unreconciled bank items | 129 |
| AP invoices failing 3-way match | 168 |
| Expense claims without a receipt | 81 |

Add a **methodology paragraph** at the bottom of the close pack page: sign convention, the
current-year-result treatment, the source and extraction date.

---

## Lab 07 — Executive dashboard to spec

**Objective:** build to a written specification, the way an engagement is delivered.

**The spec (write this into your working papers first, then build it):**

| Zone | Content | Question answered |
|---|---|---|
| Header | Report title measure, period, "Prepared by Maxhub Pvt Ltd", refresh date | Context |
| KPI strip | Revenue (with YoY %), Gross margin %, Operating profit, Cash, DSO, Overdue >90 days % | How are we doing? |
| Trend | Revenue vs prior year, 21 months, with a forecast of 3 months | Where are we heading? |
| Exception | Top 10 accounts by adverse variance to budget, with RAG formatting | What needs attention? |
| Cash | Closing cash trend + DSO/DPO/DIO lines | Can we pay our bills? |
| Footprint | "Data as at 30 Sep 2025 · Source: ERP GL extract · Page 1 of 1" | Trust |

**Steps**

1. Import the theme: **View ▸ Themes ▸ Browse for themes** ▸ `assets/PowerBI_Course_Theme.json`.
2. Build the zones. Use **Sync slicers** (View ▸ Sync slicers) to link the period slicer across pages.
3. Build the drillthrough page `Transaction Detail` and hide it. Add a back button.
4. Add a "Reset filters" bookmark; add buttons for page navigation.
5. Check the **mobile layout** for the KPI strip.
6. Run **Performance Analyzer** (View ▸ Performance analyzer ▸ Start recording ▸ Refresh visuals).

**Checkpoint**

- [ ] Every visual has a sentence title containing a number
- [ ] No visual takes more than 2 seconds on this dataset
- [ ] Drillthrough works from the revenue KPI to the ledger lines
- [ ] The page is readable when printed to PDF
- [ ] Alt text on every visual

---

## Lab 08 — Variance & exception pages

**Objective:** move from reporting to analysis.

**Steps**

1. **Budget variance page:** matrix of `Statement Rows[RowLabel]` × `DimDate[MonthYear]` with
   `Budget by FSLine`, `Variance $`, `Variance %`, plus a variance-type slicer (all / adverse only).
2. **Price–volume–mix bridge** for revenue using the Module 8 waterfalls (if you have not loaded
   budget units, do a simplified two-step bridge: volume at budget price, then price).
3. **KPI page:** DSO, DPO, DIO, cash conversion cycle as cards with trend sparklines and a comparison
   to the prior month. Add a text box stating each definition.
4. **Exception page:** table of the 20 largest journal lines where `EntryType = "Manual"` and
   `AbsAmountUSD > 25,000`, with `Risk Score` (build it from the forensic library) and drillthrough.
5. **Pareto page:** vendor spend bars with cumulative % line and an 80% reference line.
6. **Z-score outlier test** on accounts: `Outlier Flag = IF ( ABS ( [Z Score] ) > 3, "Outlier", "" )`.

**Expected results**

| Check | Expected |
|---|---|
| Budget records (FactBudget) | 1,299 |
| Total budget for FY2024 (all P&L lines) | 28,277,255 |
| Vendors needed to reach 80% of spend | 19 of 26 |
| Vendor concentration: largest vendor share | 5.3% |
| DSO at Sep 2025 | 98 days *(3,790,174 ÷ 10,543,059 × 273 days elapsed)* |

Write the **Finding / Impact / Action** block for DSO. That paragraph is the deliverable.

---

## Lab 09 — The forensic workbench

**Objective:** build the five-page workbench and find the seven injected schemes.

**Steps**

1. Import the forensic library from
   [`../dax/Forensic_Tests_Library.dax`](../dax/Forensic_Tests_Library.dax).
2. Build the Power Query tests (queries 06, 07, 08, 09 in
   [`../powerquery/M_Query_Library.pqm`](../powerquery/M_Query_Library.pqm)) and load them as tables:
   `DQ_DuplicatePayments`, `DQ_ThresholdBands`, `BenfordDigits`, `JERiskFlags`.
3. Build the five pages:

| Page | Visuals |
|---|---|
| 1. Risk overview | Cards: total flagged value, exceptions by scheme, top 10 risky journals; trend of exceptions by month |
| 2. Payments & vendors | Duplicate table; ghost-vendor indicator table; threshold histogram (bins of $500 between $4,000 and $11,000); round-number % card |
| 3. Journal entries | JE test matrix J1–J10 (count, value, % of population); scatter of amount vs posting date; heatmap of postings by weekday × hour |
| 4. Users & access | User × account-type matrix with SoD flags; unapproved value; self-approved lines; vendors with one preparer |
| 5. Evidence register | Table with TestID, TestName, Date, Amount, Preparer, DocumentRef, Risk Band, Status, Conclusion — exportable to Excel |

4. Score and rank: build `Risk Score`, `Risk Band`, `Risk Weighted Value`; show the top 50.
5. Export the evidence register: **visual ▸ … ▸ Export data** or run an `EVALUATE` in DAX query view.

**Vendor master matching (outside Power BI).** Names do not join cleanly in the real world, and a
duplicate supplier is one of the most common ways spend is hidden. Run the matcher in this repository:

```bash
python3 scripts/fuzzy_match_vendors.py                                                       # the 26-vendor master
python3 scripts/fuzzy_match_vendors.py --file data/practice/VendorName_Matching_Practice.csv  # teaching sample
python3 scripts/fuzzy_match_vendors.py --file data/raw/DimVendor.csv --threshold 0.70
```

It normalises names (case, punctuation, legal boilerplate, plurals), blocks on the name prefix so it
does not compare every pair, scores each candidate pair, and writes `data/scored/vendor_match_candidates.csv`
for review.

| Run | Expected result |
|---|---|
| `Dimension` — real 26-vendor master | **0 candidates** at 0.80: the names are genuinely distinct |
| `Practice` — `data/practice/VendorName_Matching_Practice.csv` | **7 pairs**: Nyatsime (3 spellings), Chinhoyi Hardware (2), Delta Beverages (2), Sunrise Trading (2), Zvishavane Steel (2) |

**Never merge a supplier on a name match alone.** Corroborate with VAT/tax numbers, bank account details,
address, and the approval trail. A name match is a reason to look; the documents decide.

**Expected results (the reveal — after you have built your own register)**

| Scheme | Lines | Value (debits) |
|---|---|---|
| DUPLICATE-PAYMENT | 42 | $368,023.48 — overpayment ≈ $184,011.74 |
| GHOST-VENDOR | 15 injected | $445,568.39 injected; **$2,773,799.20 total paid to the 4 vendors** |
| ROUND-NUMBER-THRESHOLD | 30 | $207,720.00 |
| SOD-RARE-COMBO | 15 | $279,600.00 |
| SPLIT-PURCHASE | 42 | $223,924.68 |
| UNREVERSED-ACCRUAL | 6 | $14,400.00 |
| WEEKEND-AFTERHOURS | 21 | $406,300.00 |
| **Total flagged (171 journals)** | | **$1,945,536.55** |

Also: suspense balance $51,058.87; 4 employee-linked vendors created Jul–Aug 2024;
129 unreconciled bank items; 168 AP invoices failing 3-way match; 81 claims without receipts.

**Now open `data/raw/InjectionLog.csv`** and compare it to your register, line by line. For every
scheme you missed, write down which test would have caught it and why yours did not fire.

---

## Lab 10 — The investigation

There is no separate lab: complete [Capstone 1 — Forensic Investigation](../capstones/Capstone_1_Forensic_Investigation.md).
It takes the Lab 09 outputs and turns them into an investigation report and board presentation.

---

## Lab 11 — Churn model and anomaly detection

**Objective:** build and evaluate a model, deploy its output, and add anomaly detection.

**Steps**

1. Run the model: `python3 scripts/ml_churn_model.py`. Read the output metrics and feature weights.
2. Load `data/scored/maxhub_client_churn_scored.csv` into Power BI (**Get Data ▸ Text/CSV**).
3. Model it: relationship `ClientID` to a small `DimClient` (create one with **Enter Data**, or use
   `ClientName` from the scored table) and to `DimDate` via a `Year` column.
4. Build the **At-risk clients** page:
   - Cards: high-risk clients, revenue at risk (`SUMX` over High risk rows of `AnnualFeeUSD`), model accuracy from the metadata table.
   - Table: client, industry, fee, NPS, complaints, partner hours, churn probability, risk band.
   - Scatter: NPS vs partner hours, size = annual fee, colour = risk band.
   - Key Influencers: analyse `ChurnRisk` explained by the feature columns.
5. Build the **Model metadata** table (Enter Data): `ModelVersion = v1.0-logreg-2025-10`,
   `TrainedOn = 2025-10-07`, `Rows = 150`, `BaselineAccuracy = 51.1%`, `ModelAccuracy = 68.9%`,
   `Precision = 71.4%`, `Recall = 65.2%`. Show it on the page.
6. Add **anomaly detection**: a line chart of monthly `Total Revenue` with
   Analytics ▸ Find anomalies; then a line chart of monthly expense claims with the same treatment.
7. Build a **forecast** on revenue with the Analytics pane forecast (3 months, 95% confidence) and label
   it "projection — assumption: trend continues".

**Expected results**

| Check | Expected |
|---|---|
| Scored rows | 150 |
| Baseline accuracy on the test set | 51.1% |
| Model accuracy | 68.9% |
| Strongest retention drivers | NPS (+), services purchased (+), partner hours (+), complaints (−) |
| High-risk clients flagged | the lowest-probability group in the scored file |

**Deliverable:** the page plus a 10-line methodology note: label, features, split, metrics, drivers,
limitations ("150 observations; indicative only; retrain with more history").

---

## Lab 12 — Propose and price

**Objective:** convert the skills into a sellable offer.

**Steps**

1. Choose one service line from [`../business/Maxhub_Service_Catalogue.md`](../business/Maxhub_Service_Catalogue.md).
2. Write a proposal using [`../business/Client_Proposal_Template.md`](../business/Client_Proposal_Template.md)
   for a named (real or hypothetical) client. Include scope, deliverables, timeline, team, fee,
   assumptions and exclusions.
3. Draft the engagement letter from [`../business/Engagement_Letter_Template.md`](../business/Engagement_Letter_Template.md),
   with the data-handling and confidentiality clauses completed.
4. Prepare the **scope-of-work estimate**: how many hours for data cleaning, modelling, testing, review
   and reporting — then price at your day rate and compare against the market range in Module 12.
5. Present it: a 10-minute pitch with three slides (the problem, the approach, the price) and answer
   the three questions every client asks — *how long, how much, and how do I know it is right?*

**Checkpoint:** your proposal names a deliverable, a date and a price, and your engagement letter has a
data-deletion clause.
