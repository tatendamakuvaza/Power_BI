# Advisory Report Template (Maxhub standard)

Use this structure for forensic, analytics and advisory reports. It is written so that a report cannot
be mistaken for an audit opinion, cannot accuse anyone of a crime, and can be re-performed by a reviewer.

Replace everything in [brackets]. Delete the guidance notes (in *italics*) before issuing.

---

```
[CLIENT LOGO]                        CONFIDENTIAL

[REPORT TITLE]
[Client legal name]
Period under review: [start date] to [end date]

Prepared by: Maxhub Pvt Ltd
Date of issue: [date]
Report reference: MX-[year]-[number]
Classification: [Confidential / Confidential and legally privileged]
Distribution: [named recipients only]
```

---

## 1. Executive summary

*Half a page, no jargon, no tables. A board member should be able to act on this page alone.*

| | |
|---|---|
| **What we were asked to do** | [one sentence] |
| **What we did** | [one sentence: data received, period, tests performed] |
| **What we found** | 1. [finding + amount] 2. [finding + amount] 3. [finding + amount] |
| **What it is worth** | Exceptions totalling [$X] across [n] transactions; [$Y] is supported by documentation as at the date of this report |
| **What we recommend** | 1. [immediate action + owner] 2. [control redesign] 3. [monitoring] |
| **Limitation** | Our work is data analytics and document review. It identifies exceptions requiring management action; it is not an audit, and it does not express a legal opinion or determine intent. |

## 2. Basis of our work

### 2.1 Instruction
[Who instructed us, when, and in what terms. Attach the instruction if written.]

### 2.2 Scope
[Cycles, entities, periods, systems, and what was excluded.]

### 2.3 Data received

| # | Data set | Source system | Provided by | Date received | Format | Records |
|---|---|---|---|---|---|---|
| 1 | General ledger | [ERP] | [name] | [date] | CSV | 13,929 |
| 2 | Vendor master | [ERP] | [name] | [date] | Excel | 26 |
| 3 | Bank statements | [bank] | [name] | [date] | PDF→CSV | 1,400 |

### 2.4 Data integrity procedures
- Originals stored unaltered; hash values recorded: [list file names and SHA-256 values].
- Reconciliation of the extract to the trial balance: total debits and credits agree at
  [$122,878,886.54 each]; no orphan account keys; all journal IDs balance.
- Known limitations of the data: [e.g. approvals recorded in a separate system not provided].

### 2.5 Procedures performed
[List the tests, in the language of the test programme: duplicates, ghost vendors, threshold testing,
split payments, weekend and after-hours journal entries, segregation of duties, Benford, and the
document-level corroboration performed. State the number of items investigated.]

### 2.6 Limitations
- [Data analytics tests identify exceptions; they do not establish intent or illegality.]
- [We have not verified the completeness of the systems that produced the extracts.]
- [Amounts stated as "amount at risk" are the full value of the exceptions; only the items with
  documentary support are reported as quantified loss.]
- [We have not performed any procedure to identify subsequent events after [date].]

### 2.7 Standards and independence
[We performed this work in accordance with [applicable professional standards], the IESBA Code of
Ethics, and Maxhub's internal quality-control standards. An independent Maxhub partner reviewed this
report before issue.]

## 3. Findings

*One section per finding, in descending order of value. Repeat the structure for each.*

### Finding [n] — [Short descriptive title, not an accusation]
**Amount at risk:** [$X] across [n] transactions ([period])
**Estimated loss:** [$Y] (documentary support: [state what was obtained]) *or* "not quantified; requires
document-level corroboration, which we recommend as the next phase"

| | |
|---|---|
| **What we observed** | [factual description with dates, references, and one worked example. No adjectives.] |
| **How we tested** | [population, rule, exclusions, sample investigated] |
| **Evidence** | [journal IDs, invoice numbers, bank references, system trails — appendix references] |
| **Why it matters** | [the assertion or control that is undermined, and the financial consequence] |
| **Root cause** | [the control that failed; not a person] |
| **Recommendation** | [specific, owned, dated, costed] |

## 4. Aggregate quantification

| # | Scheme / matter | Transactions | Total value ($) | Amount at risk ($) | Quantified loss ($) | Basis |
|---|---|---|---|---|---|---|
| 1 | [Duplicate payments] | 42 | 368,023.48 | 184,011.74 | [x] | [duplicate pairs; credit notes obtained] |
| … | | | | | | |
| | **Total** | **171** | **1,945,536.55** | **[x]** | **[y]** | |

*State clearly what "amount at risk" means and what evidence would convert it into quantified loss.*

## 5. Control environment observations

*Observations that are not findings in themselves but affect risk: unreconciled bank items, suspense
balances, missing approvals, unmatched invoices, aged debtors, access rights.*

| Observation | Value / count | Implication |
|---|---|---|
| Unreconciled bank items | 129 of 1,400 | Payments may be unrecorded or duplicated |
| Suspense account balance | $51,058.87 | Transactions are not allocated to their proper account |
| AP invoices failing 3-way match | 168 of 520 | Purchases may not be properly authorised or received |
| Expense claims without receipts | 81 of 650 | Weak substantiation; an audit-adjustment risk |

## 6. Recommendations and remediation plan

| # | Recommendation | Owner | Due date | Indicative cost | Priority |
|---|---|---|---|---|---|
| 1 | [Recover the duplicate payments; issue credit notes] | [FD] | [date] | — | High |
| 2 | [Freeze the four employee-linked vendor accounts pending verification] | [CFO] | [date] | — | High |
| 3 | [Mandate PO for all purchases; remove value-based exception] | [Procurement] | [date] | [cost] | High |
| 4 | [Restrict manual journal posting to business hours; second approver for all manual JEs] | [Financial Controller] | [date] | [cost] | Medium |
| 5 | [Monthly exception report produced from the client's own data] | [Maxhub] | [date] | [$x/month] | Medium |

## 7. Appendices

- **A** — Test programme (12 tests: population, assertion, expectation, exception, follow-up)
- **B** — Evidence register (all flagged transactions, scored, with conclusion and status)
- **C** — Data lineage and integrity record (files, hashes, extraction dates, reconciliations)
- **D** — Methodology note for the analytics model (definitions, sign conventions, exclusions)
- **E** — Documents examined and correspondence with third parties
- **F** — Glossary of terms

---

**Prepared by:** [name, title] · **Date:** [date]
**Reviewed by (independent QC):** [name, title] · **Date:** [date]
**Issued to:** [names and roles]
**Next review:** [date]

*This report is confidential and prepared solely for the addressee for the purpose set out in section 1.
It may not be relied upon by any other party without Maxhub's written consent.*
