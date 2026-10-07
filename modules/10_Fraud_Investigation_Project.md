# Module 10 — Fraud Investigation Project

**Time:** 10 hours · **Lab:** the capstone itself ([Capstone 1](../capstones/Capstone_1_Forensic_Investigation.md)) · **Prerequisite:** Module 9

> This is the module where the course stops being a course. You are the engagement team.
> Client: Mhondoro Manufacturing (Pvt) Ltd. Subject: suspected misappropriation in the
> procure-to-pay and journal-entry cycles, FY2024 – 9M FY2025.

---

## 10.1 The engagement at a glance

| Item | Detail |
|---|---|
| **Client** | Mhondoro Manufacturing (Pvt) Ltd |
| **Instruction** | Written instruction from the Board Audit Committee (signed, dated) |
| **Scope** | Procure-to-pay and journal-entry cycle, 1 Jan 2024 – 30 Sep 2025 |
| **Data received** | GL journal (13,929 lines / 5,504 journals), vendor master, AP invoices, employee master, users, bank statement, expense claims, budgets, trial balance |
| **Objective** | Identify and quantify exceptions indicating fraud or material control failure; quantify loss; recommend remediation |
| **Standard** | Investigative analytics per Maxhub methodology; findings to be supportable by source documents |
| **Deliverable** | Findings report + evidence register + remediation plan + board presentation |

**Before you touch the data:** copy it to a working folder, record the hash of the originals, note the
extraction date and the person who provided each file. Write it in the working papers now, not later.
On Windows:

```powershell
Get-FileHash data\raw\FactGLJournal.csv -Algorithm SHA256
```

---

## 10.2 Phase 1 — Understand the business and the controls (2 hours)

Document, from the data itself:

1. **The cycles.** Cash receipts from customers (1100 → 1010), purchases (2000 → 1010), payroll
   (6000/5010 → 1010), statutory (2100/2110/2120/2130 → 1010), expenses (6190 etc → 1010).
2. **The controls that should exist** — and where the data says they were absent:

| Expected control | Data column that proves presence/absence |
|---|---|
| Payments above $10,000 approved by the CFO | `ApprovedBy` blank where `AbsAmountUSD >= 10000` |
| Purchases above $5,000 supported by a PO | `FactAPInvoices[PONumber]` blank |
| Goods received before payment (3-way match) | `ThreeWayMatch = "Exception"` |
| Vendor onboarding with tax clearance | `DimVendor[TaxClearanceNo]` blank |
| Segregation: AP clerk cannot post revenue | `DimUser[JobTitle]` × `DimAccount[AccountType]` |
| Journals not posted in closed/odd periods or times | `EnteredOn` hour/day; `SourceSystem` |

3. **Establish the control totals** you will reconcile every finding to:

```dax
Control Totals =
VAR Debits  = [Debit Total]
VAR Credits = [Credit Total]
RETURN "Debits: " & FORMAT ( Debits, "$#,##0.00" ) & " | Credits: " & FORMAT ( Credits, "$#,##0.00" )
```

Expected: **$122,878,886.54** on both sides across **13,929 ledger lines (5,504 journals)**,
including opening balances and the year-end close. If your numbers
differ, stop and reconcile before doing anything else.

---

## 10.3 Phase 2 — Run the test programme (4 hours)

Run all twelve tests from Module 9. For each, capture: population, rule, number of exceptions, value,
and your preliminary conclusion. Use this **working paper template** (one row per test):

| TestID | Test | Population | Rule | Exceptions | Value USD | Conclusion |
|---|---|---|---|---|---|---|
| P1 | Duplicate payments | Payments to vendors | Same vendor + same amount within 30 days | | | |
| P2 | Ghost / related-party vendors | Vendor master | Employee-linked, no tax clearance, created <180 days before first payment | | | |
| P3 | Round numbers | All manual entries | `MOD(amount,1000)=0` and >$5,000 | | | |
| P4 | Just below approval limit | All payments | $9,000 ≤ amount < $10,000 | | | |
| P5 | Split purchases | Purchases | ≥2 invoices $3k–$5k, same vendor, same month, total >$5,000 | | | |
| J1 | Manual journals | GL | `EntryType = "Manual"` | | | |
| J3 | Weekend / after-hours | Manual GL | Entered Sat/Sun or before 07:00 / after 19:00 | | | |
| J4 | Backdated postings | GL | `PostingDate − DocumentDate ≥ 10 days` | | | |
| J5 | Unusual user × account | GL | Posting outside the user's normal account set | | | |
| J7 | Suspense not cleared | GL, account 1990 | Balance at period end, and age | | | |
| J10 | Rarely used accounts | GL | Fewer than 3 postings in the ledger | | | |
| U1 | Maker–checker failures | Payments ≥ $10k | Blank `ApprovedBy`, or preparer = approver | | | |

Then build the **risk-shortlisted** evidence register (Module 9 §9.7) and export it:

**Page ▸ Export data** from a table visual, or `EVALUATE` in DAX query view and copy to Excel.
Name it `Mhondoro_Evidence_Register_v01.xlsx`.

---

## 10.4 Phase 3 — Investigate the flags (3 hours)

Work the top-scoring 30 exceptions. For each: pull the source documents (in this simulation: the GL
lines, the AP invoice, the vendor master row, the bank line), and write a **finding note** with:

1. **What happened** (fact, with document references and amounts).
2. **The evidence** (journal IDs, invoice numbers, dates, users, system trail).
3. **The control that failed.**
4. **The amount at risk** (and how you calculated it).
5. **What you still need** to conclude (a document, an interview, a bank confirmation).

### The reveal — what is actually in the Mhondoro data

**Do not read this section until your own register is built.** Then open
`data/raw/InjectionLog.csv` and compare. The detail is in that file (171 flagged lines).

| Scheme | How it presents in the data | Lines | Value (debits) |
|---|---|---|---|
| **Duplicate payments** | The same vendor + the same amount + the same invoice number in the description, paid 4–12 days apart, prepared by the same clerk | 42 lines / 21 pairs | $368,023.48 (overpayment ≈ half = **$184,011.74**) |
| **Ghost / related-party vendors** | 4 vendors created July–August 2024 with `IsEmployeeLinked = Yes`, blank tax clearance, 7-day payment terms; two name employees (`R Chikafu Trading Enterprises`, `Zhou Logistics & Advisory`); all paid through the Advisory Services cost centre by the Financial Controller | 15 injected lines | $445,568.39 injected — **$2,773,799.20 total paid to those 4 vendors over the period** (the full scope of the enquiry) |
| **Round-number / threshold avoidance** | Payments of $4,985–$4,995 (just under the $5,000 PO limit) and $9,750–$9,900 (just under the $10,000 approval limit), all round to the nearest $5 | 30 lines | $207,720.00 |
| **Split purchases (structuring)** | Two invoices 2 days apart, same vendor, $4.5k–$6.5k each, total above the PO threshold, on engineering spares | 42 lines / 21 pairs | $223,924.68 |
| **Weekend / after-hours manual journals** | Manual entries entered at 02:00, 04:00, 22:00 or 23:00, or on Saturdays, posted by `USR-012` (Shared Services Clerk) with no approver, using the suspense account as the credit side | 21 lines | $406,300.00 |
| **Segregation-of-duties breach** | An Accounts Payable Clerk (`USR-002`) posting revenue credit notes and reclassifications | 15 lines | $279,600.00 |
| **Unreversed accruals** | Prepayment/accrual postings with no reversal in the following period, building expense overstatement | 6 lines | $14,400.00 |
| **TOTAL FLAGGED** | 171 journal lines | | **$1,945,536.55** |

Also inherited by the investigation (not "injected" but visible in the data and worth a finding):

- **Suspense account balance $51,058.87** — an unresolving clearing account is a control failure in
  itself and a place to hide entries.
- **Trade receivables $3.79m against $10.54m of 9-month revenue** — 36% of a full year's revenue
  outstanding; see Module 8's DSO analysis. Overdue concentration is a credit-control and possibly
  a revenue-recognition issue.

**Quantify properly.** Distinguish three numbers in every finding:

| Number | Meaning | Example (ghost vendors) |
|---|---|---|
| **Total value of transactions** | Everything that moved | $2,773,799.20 |
| **Value at risk** | What could be improper, on conservative assumptions | $445,568.39 (the flagged injections) to $2,773,799.20 (all spend with those vendors) |
| **Estimated loss** | Evidence-supported misappropriation | Established only after document tracing and interviews — **do not state a loss figure you cannot support** |

---

## 10.5 Phase 4 — Report (1.5 hours)

Maxhub's findings report structure (template in [`../business/Advisory_Report_Template.md`](../business/Advisory_Report_Template.md)):

1. **Cover page** — client, engagement, period, date issued, classification (Confidential / Legally privileged).
2. **Executive summary** (one page, no jargon):
   - What we were asked to do, what we did, over what period.
   - What we found — up to five findings, each one sentence with an amount.
   - What we recommend — the three highest-impact actions.
   - The limitation: this is data analytics; it identifies exceptions requiring document-level follow-up.
3. **Basis of our work** — instruction, scope, data received (with dates and hashes), methods used
   (list the tests), limitations and reliance on client data.
4. **Findings** — one page each, in the order of value at risk:

   ```
   FINDING 1 — Payments made twice for the same supplier invoice
   Amount at risk: $184,011.74 across 21 invoice pairs (21 months to 30 Sep 2025)

   What we observed ....... same vendor, same amount, same invoice reference, two postings
                            4–12 days apart (Example: INV-24731 to Steel Supplies Zimbabwe,
                            $11,842.55 on 2025-03-04 and 2025-03-12, both posted by USR-012)
   How we tested .......... [test P1, rule, population, exclusions]
   Why it matters ......... the second payment is not supported by a liability; the supplier
                            may hold a credit or the funds may be recoverable
   Root cause ............. no duplicate-invoice check in the AP process; no PO reference on
                            the second payment; approval limit not applied
   Recommendation ......... [specific, costed, with an owner]
   ```

5. **Appendices** — evidence register, test programme, data lineage (source files, hashes, extraction
   dates), and the reconciliation of tested population to the trial balance.
6. **Distribution and legal handling** — who receives it, what is privileged, retention policy.

Rules that keep you out of trouble:

- Write **facts**, then **inferences**, clearly labelled. Never accuse a named person of a crime.
- Never speculate about intent. "The pattern is inconsistent with the stated payment terms" is a
  finding; "the clerk stole the money" is a conclusion for the court, counsel and the investigators.
- Quantify with a stated basis and a range where uncertainty exists.
- Reference every number to a working paper.

---

## 10.6 Phase 5 — Remediation and recovery (1 hour)

For each finding, produce recommendations that are **specific, owned and costed**:

| Finding | Immediate action | Control redesign | Recovery path |
|---|---|---|---|
| Duplicate payments | Recover from suppliers; credit note or refund | Three-way match before payment; duplicate check on vendor + amount + invoice no. at capture | $184,011.74 pursued; expect partial recovery |
| Ghost/related-party vendors | Freeze the 4 vendor accounts; confirm existence; declare interests | Vendor onboarding with tax clearance, independent bank verification, employee-conflict declaration on file | Suspension of further payments; civil recovery review |
| Threshold avoidance | Mandate PO for all purchases regardless of value | Remove the value-based exception; automate the limit; exception report weekly | Process discipline |
| Split purchases | Enforce PO on cumulative monthly spend per vendor | Block payment without PO; threshold based on aggregate, not invoice | Process discipline |
| Weekend/after-hours entries | Suspend manual posting rights; requeue for approval | Posting restricted to business hours; every manual JE needs a second approver | Reverse unsupported entries ($406,300) |
| SoD breach | Remove AP clerk's GL posting rights to revenue accounts | Role-based access review; quarterly user-access recertification | Review the 15 entries ($279,600) |
| Unreversed accruals | Reverse; correct the monthly close checklist | Automated reversal of accruals next period; suspense age report | $14,400 expense correction |
| Suspense balance ($51,059) | Clear or reclassify every line by period end | Suspense must be nil at each close (a hard close rule) | Balance sheet accuracy |

The recommendations section is worth as much as the findings: it is what turns a one-off investigation
into a **controls advisory engagement** — the natural next sale for Maxhub.

---

## 10.7 Presentation (1 hour)

Prepare a **12-slide board presentation** and a **one-page findings summary**:

1. Purpose and scope · 2. What we did (methods in plain language) · 3. Headline: value at risk
$1.8m flagged, top schemes · 4–8. One slide per scheme, one chart each, annotated
("the wall below $10,000") · 9. Root causes (control failures, not people) ·
10. Recommendations with owners and dates · 11. Recovery and next steps · 12. Appendix pointers.

Charts that work on a board slide: threshold histogram, duplicate-pair scatter (posting date vs amount),
Pareto of vendors, heatmap of postings by hour × weekday, waterfall of value at risk by scheme.

---

## 10.8 What you now have in your portfolio

| Deliverable | File type | Shows a client |
|---|---|---|
| Data lineage memo with hashes | Word/PDF | You are disciplined and defensible |
| Test programme (12 tests × 5 elements) | Excel/Word | You know the methodology, not just the tool |
| Evidence register (171 lines, scored) | Excel | You can produce evidence at scale |
| Forensic workbench | `.pbix` | You can build a tool they can keep using |
| Findings report with quantified losses | PDF | You can write to a professional standard |
| Remediation plan with owners and costs | Excel | You deliver commercial value, not just criticism |
| Board presentation | PPT/PDF | You can present to a board |

That pack is the product. Price it in Module 12.

---

## 10.9 Module 10 checklist

- [ ] Evidence preserved: originals untouched, hashes recorded, extraction log written
- [ ] Control totals reconciled to $122,878,886.54 (debits = credits)
- [ ] All 12 tests run, each with population, rule, exceptions, value, conclusion
- [ ] Top 30 exceptions investigated with finding notes and document references
- [ ] Findings aggregated to **$1,945,536.55** flagged across 171 lines
- [ ] Loss vs value at risk distinguished honestly in every finding
- [ ] Report issued in the Maxhub structure with appendices
- [ ] Remediation plan with owners, dates and costs
- [ ] Board pack delivered
- [ ] Working papers archived and indexable (see Module 12's quality-control checklist)

**Next:** [Module 11 — Machine Learning & AI in Power BI](11_Machine_Learning_and_AI_in_PowerBI.md).
