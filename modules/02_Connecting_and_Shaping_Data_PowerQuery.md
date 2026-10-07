# Module 2 — Connecting & Shaping Data (Power Query)

**Time:** 6 hours · **Lab:** [Lab 02](../labs/Lab_Index.md#lab-02--the-data-source-layer) · **Prerequisite:** Module 1

> Consulting truth: the visual is 10% of the work. The other 90% is getting the numbers right.
> Power Query is where a forensic accountant earns their fee, because it is where you can *prove*
> that nothing was lost, altered or double-counted on the way in.

---

## 2.1 The mental model

Power Query is a **recipe, not a result**. Every step you take is recorded as code (the *M* language).
Each refresh re-runs the recipe against the source. Three consequences:

1. **Refreshable:** next month, drop the new extract in the same folder, click Refresh, done.
2. **Auditable:** a reviewer can read your Applied Steps and see exactly what you did to their data.
3. **Reproducible:** the same steps produce the same output, every time — which is what makes your
   work defensible in a dispute or investigation.

Compare that to "copy, paste, delete rows, save as v7 final" in Excel. That is the practice this
course replaces.

---

## 2.2 Getting data — the connectors that matter for an accountant

**Home ▸ Get Data ▸ …**

| Source | When you will use it | Notes |
|---|---|---|
| **Excel workbook** | Client sends a trial balance, AR ageing, sales file | Fastest for extents you can see |
| **Text/CSV** | System exports (Sage, Pastel, SAP, QuickBooks, ERP dumps) | Watch delimiter and encoding (UTF-8) |
| **Folder** | Client drops monthly files into a folder | Combine Files — see 2.6 |
| **SharePoint folder / OneDrive** | Client's cloud working papers | Needs organisational account |
| **SQL Server / PostgreSQL / MySQL / Oracle** | Direct from an accounting database | Read-only credentials; do not touch their production box |
| **OData / Web** | Xero, QuickBooks Online, some ZIMRA/e-government portals | API/connector quality varies |
| **PDF** | Bank statements, invoices, scanned reports | Only when there is no alternative; verify totals |
| **Dataverse / Fabric / lakehouse** | Larger client deployments | Module 12 territory |

> **Forensic rule:** if you must use PDF or OCR, always reconcile the extracted totals to the
> document's printed control totals and record that reconciliation in your working papers.

---

## 2.3 The Power Query interface

**Home ▸ Transform data** opens the editor. Five panes:

```
Queries (left)          ┌───────────────────────────┐   Applied Steps (right)
DimAccount              │   Table preview           │   1. Source
DimVendor               │                           │   2. Promoted Headers
FactGLJournal           │                           │   3. Changed Type
...                     └───────────────────────────┘   4. Filtered Rows
Formula bar (top) - shows the M code of the selected step
```

Key techniques:

- **Right-click a column header:** rename, change type, remove, duplicate, split, unpivot.
- **Filter:** use the dropdown. Use *Text Filters ▸ Contains* sparingly — it makes the recipe
  sensitive to wording changes in the source.
- **Choose Columns:** explicitly select the columns you want. If the client adds a column, your
  model does not silently change shape.
- **Advanced Editor** (Home ▸ Advanced Editor): the whole query as M code. This is where you do
  anything serious.
- **Applied Steps** can be renamed, deleted and reordered. Rename them — `Filtered Rows` tells a
  reviewer nothing. `Keep FY2024-2025 postings only` tells them everything.

---

## 2.4 The seven data-quality failures you will meet in every engagement

| Failure | How it shows up | Fix |
|---|---|---|
| **Headers not promoted** | Column1, Column2, Column3 … | *Use First Row as Headers* |
| **Wrong data type** | Numbers stored as text, dates as text, "1,234.00" | Change type; use *Locale* where needed |
| **Trailing/leading spaces** | `"Harare "` ≠ `"Harare"`; joins silently fail | Transform ▸ Format ▸ Trim |
| **Inconsistent casing** | `ACME`, `acme corp`, `Acme Corp.` | Capitalise each word + lookup table mapping |
| **Duplicate rows** | The same invoice twice (sometimes deliberately) | Remove duplicates *only* on a true key — see warning below |
| **Nulls vs zeros vs blanks** | Empty cell treated as 0, shifting averages | *Replace Values* (null → 0) or *Fill Down* |
| **Mixed sign conventions** | Credits as negative numbers in one file, positive in another | Use *Multiply* by −1 on selected columns |

> **The duplicate warning.** In a forensic engagement you *never* blindly remove duplicates —
> duplicates are the evidence. Load both: keep a `DuplicateFlag` column so the same rows can be
> counted *and* reported. Removing duplicates is a modelling choice; finding them is the engagement.

---

## 2.5 The accounting data patterns you must be able to build

### 2.5.1 Sign normalisation (make debits positive, credits negative)

Ledgers arrive in at least four shapes. Normalise early, once:

```m
let
    Source = Csv.Document(File.Contents("data/raw/FactGLJournal.csv"),[Delimiter=",", Encoding=65001]),
    Promote = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Promote,{
        {"PostingDate", type date}, {"Debit", type number}, {"Credit", type number},
        {"AccountCode", type text}, {"Period", type text}}),
    // One signed amount column: debits positive, credits negative
    AddSigned = Table.AddColumn(Types, "AmountSigned",
        each (try [Debit] otherwise 0) - (try [Credit] otherwise 0), type number),
    // Absolute value for value-based tests (Benford, duplicates, thresholds)
    AddAbs = Table.AddColumn(AddSigned, "AmountAbs", each Number.Abs([AmountSigned]), type number)
in
    AddAbs
```

### 2.5.2 Splitting a combined "Account" column into code and name

Client extract: `"1100 Trade Receivables"`. Split on the first space:

```m
SplitCode = Table.SplitColumn(Source, "Account", Splitter.SplitTextByPositions({0, 4}, false),
                              {"AccountCode", "AccountName"})
```

Or, safely, on the first delimiter with a limit:

```m
SplitCode = Table.SplitColumn(Source, "Account", Splitter.SplitTextByEachDelimiter({" "}, QuoteStyle.None, true),
                              {"AccountCode", "AccountName"})
```

### 2.5.3 The debit/credit-aware trial balance

Arrives as `Account | Debit | Credit` with only one populated. Blank them, then compare:

```m
AddBalanced = Table.AddColumn(Source, "NetBalance",
    each (if [Debit] = null then 0 else [Debit]) - (if [Credit] = null then 0 else [Credit]))
```

Add a check column and a count of unbalanced rows — then look at the number before you use the data:

```m
AddCheck = Table.AddColumn(AddBalanced, "BalanceCheck",
    each if Number.Abs([NetBalance]) < 0.005 then "OK" else "INVESTIGATE", type text),
CountBad = List.Count(List.Select(Table.Column(AddCheck,"BalanceCheck"), each _ = "INVESTIGATE"))
```

### 2.5.4 Unpivoting a 12-month budget (wide → long)

Clients send budgets as `Account | Jan | Feb | … | Dec`. Power BI wants one row per month.

1. Select the *identity* columns (Account, CostCentre, Version).
2. **Transform ▸ Unpivot Other Columns** (or *Unpivot Columns* if you selected the months).
3. You get `Attribute` (month name) and `Value` (amount). Rename them `MonthName` and `BudgetUSD`.

Now the budget can be joined to your date table like any other fact — and next year's spreadsheet
needs no rework. This one technique removes hours of pain per client.

### 2.5.5 Mapping client account codes to standard captions

You will never get the client's chart of accounts in the shape you want. Build a mapping query:

```m
let
    Source = Excel.Workbook(File.Contents("data/xlsx/Mhondoro_Accounting_Data.xlsx"), null, true),
    Map = Source{[Item="DimAccount",Kind="Table"]}[Data],
    Keep = Table.SelectColumns(Map, {"AccountCode","AccountName","AccountType","FSLine","Statement"}),
    // Force the account code to text so "0100" never becomes 100
    AsText = Table.TransformColumnTypes(Keep, {{"AccountCode", type text}})
in
    AsText
```

**Golden rule: account codes are text, never numbers.** Leading zeros, alphanumeric codes
(`1000-A`) and codes like `0620` are common; converting them to integers destroys them silently.

### 2.5.6 Text cleaning for names (vendor and customer matching)

```m
let
    CleanName = Table.AddColumn(Source, "VendorNameClean", each
        let
            t = Text.Upper(Text.Trim([VendorName])),
            noLegal = Text.Replace(Text.Replace(Text.Replace(t, " (PVT) LTD", ""), " LIMITED", ""), " LTD", ""),
            noPunct = Text.Remove(noLegal, {".", ",", "&", "'"})
        in Text.Clean(Text.Trim(noPunct)), type text)
in
    CleanName
```

Use `VendorNameClean` for fuzzy matching in the ghost-vendor tests in Module 9.

---

## 2.6 Combining monthly files from a folder (the refresh pattern clients love)

Client drops `GL_2024-01.csv`, `GL_2024-02.csv`, … into a folder each month.

1. **Get Data ▸ Folder** → browse to the folder → **Combine & Transform Data**.
2. Power Query generates a **Sample File** query and a **Transform File** query.
   Edit `Transform File`: set types, remove blank rows, add a `SourceFile` column if useful.
3. Result: a single `FactGL` table that picks up any new file on refresh.

Add a defensive step so a stray file does not break the refresh:

```m
FilterFiles = Table.SelectRows(Source, each Text.StartsWith([Name], "GL_") and Text.EndsWith([Name], ".csv"))
```

**Diagnostic habit:** when a "combine files" refresh breaks, 9 times out of 10 a client has added a
file with different column headers or a `~$` Excel lock file. Filter the file list — never trust a folder.

---

## 2.7 Cleaning the MessyData table (worked example)

Source (`PowerBI_Practice_Workbook.xlsx ▸ MessyData`):

| Sale ID | Sale Date | Customer | Amount | Region  | Units |
|---|---|---|---|---|---|
| 1 | 01/03/2021 | Acme Corp | "1,250.00" | "Harare" | "12" |
| 2 | 2021-03-02 | acme corp | "R 2 500.50" | "harare " | "30" |
| 3 | 04 March 2021 | BETA LTD. | 2350 | Bulawayo | 8 |
| … | | | "" | | |

The full recipe:

```m
let
    Source = Excel.Workbook(File.Contents("data/xlsx/PowerBI_Practice_Workbook.xlsx"), null, true),
    Sheet  = Source{[Item="MessyData",Kind="Sheet"]}[Data],
    Promote = Table.PromoteHeaders(Sheet, [PromoteAllScalars=true]),
    TrimText = Table.TransformColumns(Promote, {
        {"Customer", Text.Proper, type text},
        {"Region ", Text.Trim, type text}}),
    Rename = Table.RenameColumns(TrimText, {{"Region ", "Region"}}),
    CleanAmount = Table.TransformColumns(Rename, {{"Amount", each
        let s = Text.Remove(Text.Trim(Text.From(_)), {"R","$",","," "})
        in if s = "" or s = "n/a" then null else Number.From(s, "en-US"), type number}}),
    CleanUnits = Table.TransformColumns(CleanAmount, {{"Units", each
        let s = Text.Trim(Text.From(_))
        in if s = "" or s = "n/a" then null else Number.From(s, "en-US"), type number}}),
    // Dates arrive in at least three formats - try each in order
    FixDates = Table.TransformColumns(CleanUnits, {{"Sale Date", each
        let s = Text.Trim(Text.From(_)) in
        if s = "" then null
        else if Date.FromText(s, "en-GB") <> null then Date.FromText(s, "en-GB")
        else Date.FromText(s, "en-US"), type date}}),
    DropBad = Table.SelectRows(FixDates, each [Sale Date] <> null and [Amount] <> null)
    // NOTE: rows with a blank/NaH amount are dropped here ^ - document that decision!
in
    DropBad
```

Rules the worked example demonstrates:

- **Every cleaning decision is a documented decision.** "Dropped 2 rows with no amount, client
  confirmed they were voided, listed in Appendix A." That sentence is the difference between a
  finding and an accusation.
- **No data quality issue is ever silently fixed.** If you replace nulls with zeros, note how many.
- **Dates:** always set the *locale* explicitly. `03/04/2021` is March or April depending on where the
  file was born.

---

## 2.8 Parameters — the single most valuable consulting feature

Make the reporting period a **parameter** so the same file serves any client year.

1. **Home ▸ Manage Parameters ▸ New Parameter**
   - Name `ReportStartDate`, Type Date, Suggested Values = Any value, Current Value `01/01/2024`.
2. Repeat for `ReportEndDate` = `30/09/2025`.
3. Use them in a filter step:

```m
FilterPeriod = Table.SelectRows(Types, each
    [PostingDate] >= ReportStartDate and [PostingDate] <= ReportEndDate)
```

4. Later, in Module 12, you drive them from a **client configuration table** so one template serves
   every client: `ClientName`, `ReportStartDate`, `ReportEndDate`, `VATRate`, `ApprovalThreshold`.

That last idea — a configuration table instead of hard-coded numbers — is what turns a one-off
report into a **productised service line**.

---

## 2.9 Query folding, performance and the professional habits

- **Query folding** = Power Query translating your steps into a single query against the source
  database. You can see it: right-click a step ▸ *View Native Query* (greyed out = not folding).
- Steps that break folding: adding an index column, custom columns with complex logic, merging to a
  local table. If the source is a large SQL table, do your filtering *before* the fold-breaking step.
- **Only load what you need.** Right-click a query ▸ untick *Enable load* for staging/intermediate
  queries. They stay in the recipe but never enter the model.
- **Disable load on staging queries** and name them with a `stg_` prefix: `stg_GL_Raw`, `DimAccount`.
- **Referenced queries** (right-click ▸ Reference) let several outputs share one cleaning path.

---

## 2.10 Module 2 checklist

- [ ] You can explain the difference between Power Query and the data model to a client
- [ ] You built a signed `AmountSigned` column and an absolute-value column
- [ ] You unpivoted a wide monthly table into a long fact table
- [ ] You cleaned MessyData: text, dates, currency symbols, duplicates, blanks — with notes on each decision
- [ ] You combined multiple files from a folder
- [ ] You created a parameter and filtered with it
- [ ] You turned *Enable load* off for a staging query
- [ ] You kept a duplicate-flag column instead of deleting duplicates

**Next:** [Module 3 — Data Modelling & the Star Schema](03_Data_Modelling_Star_Schema.md). Cleaning is
done; now we decide how the tables relate.

---

## Related material

- [../labs/Lab_Index.md#lab-02--the-data-source-layer](../labs/Lab_Index.md#lab-02--the-data-source-layer)
- [../powerquery/M_Query_Library.pqm](../powerquery/M_Query_Library.pqm)
- [../reference/Common_Errors_and_Fixes.md](../reference/Common_Errors_and_Fixes.md)

**Next:** [Module 3 — Data Modelling & the Star Schema](03_Data_Modelling_Star_Schema.md)
