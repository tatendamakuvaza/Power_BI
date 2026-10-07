# Module 9 — Forensic Accounting Analytics

**Time:** 12 hours · **Lab:** [Lab 09](../labs/Lab_Index.md#lab-09--the-forensic-workbench) · **Prerequisite:** Module 8

> Forensic analytics is detective work with a control total. You are not looking for "suspicious"
> things — you are running tests that have a defined population, a defined expectation and a
> defined exception. Everything else is a hunch, and hunches do not survive cross-examination.

Mhondoro Manufacturing contains **seven fraud schemes** injected across 21 months, 171 flagged
journal lines totalling $1,945,536.55. By the end of this module you will be able to find every one of them, and prove it.

---

## 9.1 The professional framework

**Test design** — every test you run has five parts. Write them down before you run it:

| Element | Meaning | Example |
|---|---|---|
| **Population** | Which rows the test applies to | All GL lines with a vendor, FY2024–FY2025 |
| **Assertion** | What could be wrong | Occurrence: the payment is not a genuine business expense |
| **Expectation** | What "correct" looks like | Invoices are unique per vendor + amount + document |
| **Exception** | The rule that flags a row | More than one payment for the same amount to the same vendor within 30 days |
| **Follow-up** | What you do with a hit | Trace to invoice, bank statement, approval, and vendor master |

**Evidence discipline**

- Never analyse the original file. Copy it, hash it (`certutil -hashfile source.csv SHA256`), record the hash.
- Record the date and time of extraction, who provided the data, and the system it came from.
- Every number in your report must be reproducible from your working papers.
- Distinguish **fact** ("the same invoice was paid twice") from **inference** ("this was deliberate")
  from **opinion** ("control weaknesses allowed it").

---

## 9.2 The vendor and payment tests

### Test 1 — Duplicate payments

**Power Query version (fast, scales to millions of rows):**

```m
let
    Source = FactGLJournal,
    OnlyPayments = Table.SelectRows(Source, each [VendorID] <> null and [Debit] > 0),
    Grouped = Table.Group(OnlyPayments, {"VendorID", "Debit"}, {
        {"Occurrences", each Table.RowCount(_), Int64.Type},
        {"FirstPosting", each List.Min([PostingDate]), type date},
        {"LastPosting",  each List.Max([PostingDate]), type date},
        {"Journals",     each Text.Combine(List.Distinct([JournalID]), ", "), type text},
        {"Total",        each List.Sum([Debit]), type number}}),
    Suspects = Table.SelectRows(Grouped, each [Occurrences] > 1 and [Total] >= 2000),
    Sorted = Table.Sort(Suspects, {{"Total", Order.Descending}})
in
    Sorted
```

**DAX version (interactive, for the dashboard):**

```dax
Duplicate Suspects =
COUNTROWS (
    FILTER (
        SUMMARIZE ( FactGLJournal, DimVendor[VendorName], FactGLJournal[Debit] ),
        CALCULATE ( COUNTROWS ( FactGLJournal) ) > 1
            && FactGLJournal[Debit] >= 2000
    )
)

Duplicate Value at Risk =
SUMX (
    FILTER (
        VALUES ( DimVendor[VendorID] ),
        VAR MaxAmt = CALCULATE ( MAX ( FactGLJournal[Debit] ), FactGLJournal[VendorID] <> BLANK () )
        VAR Cnt    = CALCULATE ( COUNTROWS ( FactGLJournal), FactGLJournal[VendorID] <> BLANK () )
        RETURN Cnt > 1 ),
    CALCULATE ( SUM ( FactGLJournal[Debit] ) ) * 0.5      -- conservative: half is over-paid
)
```

**Follow-up you must actually do:** a duplicate *amount* is not a duplicate *payment*. Compare the
description text and the document date. Two annual insurance premiums of the same amount are not fraud.
Our data makes this easy: the injected duplicates share the same invoice number in `Description`.

### Test 2 — Ghost vendors / related-party vendors

The classic: a vendor that exists only on paper, often controlled by an employee.

```dax
-- 1. Vendor created and used quickly (a strong indicator)
New Vendor Fast Payment =
SUMX (
    FILTER ( DimVendor,
        DimVendor[VendorCreatedOn] <> BLANK ()
            && CALCULATE ( MIN ( FactGLJournal[PostingDate] ) ) - DimVendor[VendorCreatedOn] <= 30 ),
    CALCULATE ( SUM ( FactGLJournal[Debit] ) )
)

-- 2. Vendors with no tax clearance on file (compliance + fraud signal)
Vendors Missing Tax Clearance =
CALCULATE ( COUNTROWS ( DimVendor ), DimVendor[TaxClearanceNo] = "" )

-- 3. Vendors missing a PO on every invoice
Vendors Never On A PO =
CALCULATE (
    COUNTROWS ( VALUES ( DimVendor[VendorID] ) ),
    FILTER ( FactAPInvoices, FactAPInvoices[PONumber] = "" ) )
```

```dax
-- 4. THE test: does a vendor's bank account match an employee's bank account?
Employee Vendor Matches =
COUNTROWS (
    FILTER ( DimVendor,
        CALCULATE ( COUNTROWS ( DimEmployee ),
            TREATAS ( VALUES ( DimVendor[BankAccount] ), DimEmployee[BankAccount] ) ) > 0 )
)
```

That last pattern — `TREATAS` across two tables with no relationship — is the workhorse of forensic DAX.
You will use it again for matching names, addresses and account numbers.

Add a **name-similarity check** in Power Query: strip legal suffixes, upper-case, then compare vendor
names to employee names using `Text.Contains` both ways, or fuzzy-match in the optional Python script
`scripts/fuzzy_match_vendors.py`.

### Test 3 — Round numbers and psychological thresholds

Fraudulent entries are often rounded; honest invoices are not.

```dax
Round Number Lines =
CALCULATE ( COUNTROWS ( FactGLJournal ),
    FILTER ( FactGLJournal,
        VAR A = ABS ( FactGLJournal[AmountUSD] )
        RETURN A > 0 && MOD ( A, 1000 ) = 0 ) )

Round Number % =
DIVIDE ( [Round Number Lines], CALCULATE ( COUNTROWS ( FactGLJournal ), FactGLJournal[AbsAmountUSD] > 0 ) )
```

**The threshold test** is sharper. Mhondoro's approval limit is $10,000 and the PO threshold is $5,000:

```dax
Entries Just Below Approval Limit =
CALCULATE ( COUNTROWS ( FactGLJournal ),
    FILTER ( FactGLJournal,
        FactGLJournal[Debit] >= 9000 && FactGLJournal[Debit] < 10000 ) )

Entries In Band Above Limit =
CALCULATE ( COUNTROWS ( FactGLJournal ),
    FILTER ( FactGLJournal,
        FactGLJournal[Debit] >= 10000 && FactGLJournal[Debit] < 11000 ) )
```

A spike in the band *just below* the limit with a hole just above it is a **Benford-defying
distribution** and a finding in its own right. Show it as a histogram:
`Visual ▸ Histogram` on `Debit` with bins of 1,000, plus a reference line at the limit.

### Test 4 — Split purchases (structuring)

```dax
Split Purchase Suspect Groups =
COUNTROWS (
    FILTER (
        SUMMARIZE ( FactGLJournal, DimVendor[VendorID], DimDate[MonthYear] ),
        VAR InvoicesBelowPO = CALCULATE ( COUNTROWS ( FactGLJournal ),
                FactGLJournal[Debit] > 3000, FactGLJournal[Debit] < 5000 )
        VAR TotalSpend = CALCULATE ( SUM ( FactGLJournal[Debit] ) )
        RETURN InvoicesBelowPO >= 2 && TotalSpend > 5000
    )
)
```

Follow-up: list the invoices, confirm the same goods/services, and check whether a PO exists for any
of them. Structuring is proven by **pattern + absence of approval**, not by a single invoice.

---

## 9.3 Journal entry testing (the core of every fraud investigation)

Standard practice (adapted from the ACFE and the major firms' "JE testing" methodologies):

| # | Test | Rule | DAX measure |
|---|---|---|---|
| J1 | Manual journals | Manual entries bypass controls | `CALCULATE ( COUNTROWS ( FactGLJournal ), FactGLJournal[EntryType] = "Manual" )` |
| J2 | Round amounts | `MOD(amount,1000)=0` | see Test 3 |
| J3 | Weekend / after-hours | `EnteredOn` day or hour | below |
| J4 | Backdated postings | `EnteredOn` > posting date by 14+ days | below |
| J5 | Unusual user/account pairs | Posting outside the user's normal account set | below |
| J6 | Reversals and unusual pairs | Entries reversed or offset to suspense | below |
| J7 | Entries posted to suspense never cleared | Suspense balance age | below |
| J8 | Journal IDs that do not balance | Debits ≠ credits in a journal | see Module 6 |
| J9 | High-value entries near period end | Top 1% of amounts, last 3 days of period | below |
| J10 | First-time / inactive account combinations | Account used < 3 times in the ledger | below |

```dax
-- J3 Weekend / after-hours postings
Weekend Postings =
CALCULATE ( COUNTROWS ( FactGLJournal ), FactGLJournal[EntryType] = "Manual",
    FILTER ( FactGLJournal, WEEKDAY ( FactGLJournal[EnteredOn], 2 ) >= 6 ) )

After Hours Postings =
CALCULATE ( COUNTROWS ( FactGLJournal ), FactGLJournal[EntryType] = "Manual",
    FILTER ( FactGLJournal, HOUR ( FactGLJournal[EnteredOn] ) < 7 || HOUR ( FactGLJournal[EnteredOn] ) > 19 ) )

-- J4 Backdated postings (10 days or more between document date and posting)
Backdated Postings =
CALCULATE ( COUNTROWS ( FactGLJournal ),
    FILTER ( FactGLJournal,
        FactGLJournal[DocumentDate] <> BLANK ()
        && DATEDIFF ( FactGLJournal[DocumentDate], FactGLJournal[PostingDate], DAY ) >= 10 ) )

-- J9 Period-end clustering: the last 3 days of each month
Period End Clustering % =
VAR LastThreeDays =
    CALCULATE ( [GL Amount Abs],
        FILTER ( DimDate, DimDate[Days From Period End] <= 3 ) )
VAR AllDays = [GL Amount Abs]
RETURN DIVIDE ( LastThreeDays, AllDays )

-- J10 Rarely used accounts (fewer than 3 postings in the whole ledger)
Rare Account Lines =
CALCULATE ( [GL Lines],
    FILTER ( VALUES ( DimAccount[AccountCode] ),
        CALCULATE ( [GL Lines], ALL ( DimDate ) ) < 3 ) )
```

---

## 9.4 Segregation of duties and user-access analytics

```dax
-- Postings by user and account type: outliers are the story
User Account Matrix % =
DIVIDE ( [GL Lines], CALCULATE ( [GL Lines], ALLSELECTED ( DimAccount[AccountType] ) ) )

-- AP clerk posting revenue/credit notes (does not happen in a controlled environment)
SoD Breach Lines =
CALCULATE ( COUNTROWS ( FactGLJournal ),
    DimUser[JobTitle] = "Accounts Payable Clerk",
    DimAccount[AccountType] = "Revenue" )

SoD Breach Value = CALCULATE ( [GL Amount Abs], DimUser[JobTitle] = "Accounts Payable Clerk", DimAccount[AccountType] = "Revenue" )

-- Maker-checker failures: who prepared, and who approved?
Unapproved Value =
CALCULATE ( [GL Amount Abs],
    FILTER ( FactGLJournal, FactGLJournal[ApprovedBy] = "" && FactGLJournal[AbsAmountUSD] > 10000 ) )

Unapproved % = DIVIDE ( [Unapproved Value], [GL Amount Abs] )

-- Self-approval: preparer = approver
Self Approved Lines =
CALCULATE ( COUNTROWS ( FactGLJournal ),
    FILTER ( FactGLJournal,
        FactGLJournal[ApprovedBy] <> "" && FactGLJournal[ApprovedBy] = FactGLJournal[PreparedBy] ) )
```

---

## 9.5 Benford's Law (and when not to use it)

**What it is:** in naturally occurring, unconstrained financial data, the first significant digit
follows a predictable distribution — about 30.1% of amounts start with a 1, 17.6% with a 2, and only
4.6% with a 9.

**The expected proportions for digits 1–9:**

| Digit | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|
| Expected % | 30.1 | 17.6 | 12.5 | 9.7 | 7.9 | 6.7 | 5.8 | 5.1 | 4.6 |

**Implementation in Power Query (recommended — build it once as a reusable table):**

```m
let
    Source = FactGLJournal,
    Positive = Table.SelectRows(Source, each [AbsAmountUSD] >= 10),   // below 10, Benford is noise
    FirstDigit = Table.AddColumn(Positive, "FirstDigit", each
        Number.From(Text.Start(Text.From(Number.Abs([AbsAmountUSD])), 1)), Int64.Type),
    Grouped = Table.Group(FirstDigit, {"FirstDigit"}, {{"Actual", each Table.RowCount(_), Int64.Type}}),
    Total = List.Sum(Grouped[Actual]),
    WithPct = Table.AddColumn(Grouped, "ActualPct", each [Actual] / Total, type number),
    Expected = Table.AddColumn(WithPct, "ExpectedPct", each Number.Log10(1 + 1 / [FirstDigit]), type number)
in
    Expected
```

**The test statistic (chi-square):**

```dax
Benford Chi Square =
VAR TotalLines = CALCULATE ( COUNTROWS ( BenfordDigtsTable ), FactGLJournal[AbsAmountUSD] >= 10 )
VAR ChiSq =
    SUMX ( BenfordDigtsTable,
        VAR Expected = TotalLines * BenfordDigtsTable[ExpectedPct]
        RETURN DIVIDE ( ( BenfordDigtsTable[Actual] - Expected ) ^ 2, Expected ) )
RETURN ChiSq
-- Degrees of freedom = 8. Critical values: 15.51 at 5%, 20.09 at 1%. Above 20 your data deserves a question.
```

**When Benford does NOT apply** (say this out loud in the report, it is what separates a professional
from a tool user):

- Data with built-in boundaries: VAT on a fixed rate, salaries in bands, fixed fees, credit limits.
- Small populations (under ~1,000 entries).
- Assigned or sequential numbers (invoice numbers, phone numbers, IDs).
- Transactions below ~$10 or rounded to hundreds.

**Critically:** Benford analyses **the whole population**, but the *forensic* use is to run it
**within subgroups** — per vendor, per user, per account — where deviations point at a person.

---

## 9.6 The forensic workbench: the dashboard you sell

Build five pages. Each one is a product in its own right.

| Page | Content | Client question answered |
|---|---|---|
| **1. Risk overview** | Cards: total value at risk, exceptions by scheme, 12-month trend of exceptions, top 10 risky journals | "How much could be going wrong?" |
| **2. Payments & vendors** | Duplicate suspects, ghost-vendor indicators, round-number histogram, threshold histogram, vendor concentration | "Is money leaving to the right people?" |
| **3. Journal entries** | JE test matrix (J1–J10 with counts, values, % of population), scatter of amount vs posting date, weekend/after-hours heatmap | "Can people book entries to hide things?" |
| **4. Users & access** | User × account-type matrix with SoD flags, unapproved value, self-approvals, rare combinations | "Who can do what they should not?" |
| **5. Evidence register** | Table of every flagged transaction with test name, rule, amount, preparer, status, follow-up owner | "What are we doing about each hit?" |

Add on **page 5** these columns so the workbench is also the working paper: `TestID`, `TestName`,
`ExceptionDate`, `AmountUSD`, `Preparer`, `DocumentRef`, `ReviewedBy`, `Status`, `Conclusion`.
Export it to Excel at the end of the engagement — that export is the deliverable appendix.

---

## 9.7 Risk scoring: from many exceptions to a shortlist

Clients cannot investigate 4,000 flags. Score them.

```dax
Risk Score =
VAR Duplicate      = IF ( [Is Duplicate] = 1, 30, 0 )
VAR RoundNumber    = IF ( MOD ( MAX ( FactGLJournal[Debit] ), 1000 ) = 0 && MAX ( FactGLJournal[Debit] ) > 5000, 15, 0 )
VAR Weekend        = IF ( WEEKDAY ( MAX ( FactGLJournal[EnteredOn] ), 2 ) >= 6, 15, 0 )
VAR NoApproval     = IF ( MAX ( FactGLJournal[ApprovedBy] ) = "", 20, 0 )
VAR ManualJE       = IF ( MAX ( FactGLJournal[EntryType] ) = "Manual", 10, 0 )
VAR NewVendor      = IF ( DATEDIFF ( MAX ( DimVendor[VendorCreatedOn] ), MAX ( FactGLJournal[PostingDate] ), DAY ) < 180, 20, 0 )
VAR HighValue      = IF ( MAX ( FactGLJournal[AbsAmountUSD] ) > 25000, 10, 0 )
RETURN Duplicate + RoundNumber + Weekend + NoApproval + ManualJE + NewVendor + HighValue
```

Prioritise by **score × value**. Rank, take the top 50, and investigate those first. Document the
scoring model in the methodology note — including that weights are judgmental (that is fine, as long
as it is disclosed).

---

## 9.8 What the data will show you (a nudge, not the answers)

When your workbench is built, look for:

- **A vendor created mid-period, paid within 7 days, with no tax clearance, whose bank details have
  never changed.** Then compare that bank account or name to the employee master.
- **The same invoice number twice, 4–12 days apart, same amount to the same vendor.**
- **A histogram with a wall just below $10,000 and $5,000.**
- **Two invoices from one vendor, same month, each a few thousand dollars, together over the PO limit.**
- **Manual journals entered at 02:00, 04:00, 22:00 or 23:00, or on a Saturday, with no approver.**
- **An AP clerk posting to revenue, or a preparer approving their own journal.**
- **Accruals that are never reversed the following period.**
- **A suspense account that only grows.**

Every one of those exists in the Mhondoro ledger. Module 10 shows you how to work them into a
report; `data/raw/InjectionLog.csv` shows you which lines carry them (open it only when the module
tells you to).

---

## 9.9 Module 9 checklist

- [ ] 12 forensic tests built (duplicates, ghost vendors, round numbers, thresholds, split purchases,
      J1–J10 journal-entry tests)
- [ ] Benford analysis built **with** its exclusions documented
- [ ] Risk score built; top 50 exceptions ranked by score × value
- [ ] Evidence register exported to Excel with the required columns
- [ ] Every test has population / assertion / expectation / exception / follow-up written down
- [ ] Data lineage recorded: source system, extract date, file hash, preparer

**Next:** [Module 10 — Fraud Investigation Project](10_Fraud_Investigation_Project.md): take those
flags, run the investigation, prove the loss, and write the report.

---

## Related material

- [../labs/Lab_Index.md#lab-09--the-forensic-workbench](../labs/Lab_Index.md#lab-09--the-forensic-workbench)
- [../dax/Forensic_Tests_Library.dax](../dax/Forensic_Tests_Library.dax)
- [../scripts/fuzzy_match_vendors.py](../scripts/fuzzy_match_vendors.py)
- [../capstones/Capstone_1_Forensic_Investigation.md](../capstones/Capstone_1_Forensic_Investigation.md)
- [../assessments/Practical_Assessments.md](../assessments/Practical_Assessments.md)

**Next:** [Module 10 — Fraud Investigation Project](10_Fraud_Investigation_Project.md)
