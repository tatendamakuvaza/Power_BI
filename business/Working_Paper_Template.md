# Working paper template

A working paper is the evidence that the work was done properly. It must let a reviewer who was not
there re-perform the test and reach the same conclusion.

Copy this file once per test, or keep the template as a Word/Excel page and complete one row per
exception. File working papers in the engagement folder in test-reference order.

---

```
WORKING PAPER — [Client] — [Engagement] — [Period]
WP reference: [e.g. FA-03]              Prepared by / date:  [initials] / [date]
Test name:    [e.g. Duplicate payment detection]
Test reference: [J/D/x]                 Reviewed by / date:  [initials] / [date]
```

## 1. Objective of the test

What assertion or risk does this test address, in one sentence?

> *Example: Test whether any supplier invoice has been paid more than once for the same goods or
> services during the period — addressing the occurrence assertion and the risk of misappropriation.*

## 2. Population

| Item | Detail |
|---|---|
| Source data | [file name, hash, extraction date, source system] |
| Records in the extract | [n] |
| Records in scope after exclusions | [n] |
| Exclusions (and why) | [e.g. reversed entries within the same month — reversed, so no cash effect] |
| Control total used | [e.g. total payments $30,505,968 per the creditor ledger] |
| Reconciliation of the extract to the control total | [ties / difference of $X, explained] |
| Completeness testing performed | [e.g. record count and value per month compared to the ledger; no gaps in journal IDs] |

## 3. Test design

| Element | Detail |
|---|---|
| Assertion | Occurrence / accuracy / cut-off / completeness (state which) |
| Expectation | [What should be true if controls worked] |
| Rule applied | [State it precisely enough to re-code, e.g. same vendor + same amount (±0.01) + posting dates within 10 days + not a reversal pair] |
| Fields used | [vendor, amount, date, invoice number, journal ID, preparer] |
| Tool | Power Query query [name] / DAX measure [name] / Python script [name and version] |
| Logic | [Copy the M or DAX or a plain-English equivalent, or attach the query] |
| Tolerances | [e.g. amounts rounded to 0.01; differences under $1 treated as immaterial for matching] |

## 4. Results

| Exception rule | Items | Value ($) | % of population |
|---|---|---|---|
| [Exact duplicate: identical vendor, amount, date] | [n] | [x] | [%] |
| [Near duplicate: same vendor and amount within 10 days] | [n] | [x] | [%] |
| **Total exceptions flagged** | **[n]** | **[x]** | |

**Summary conclusion:** [e.g. 21 invoice pairs totalling $368,023.48 were paid twice; the improper
portion is $184,011.74, being the second payment in each pair.]

## 5. Exception detail (one row per exception)

| # | Journal ID | Date | Account | Vendor | Invoice ref | Amount ($) | Preparer | Approver | Reversal? | Value at risk ($) | Conclusion | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | Y/N | | | Open/Explained/Recoverable/Referred |
| 2 | | | | | | | | | | | | |

Attach: the exported exception register (Excel), the test output (screenshot or CSV), and any documents
obtained for corroboration.

## 6. Investigation of exceptions

For each exception, or each category of exception:

| # | Exception | Document obtained | What the document shows | Corroborated? | Amount supported ($) |
|---|---|---|---|---|---|
| 1 | | [PO, GRN, invoice, bank statement, credit note, email approval] | | Yes/No/Partially | |

**Rule:** an uninvestigated exception is reported as an exception, never as a loss. Only amounts
supported by documents are described as quantified loss; the rest remain value at risk.

## 7. Conclusion

| | |
|---|---|
| **Finding** | [One sentence, factual, no adjectives] |
| **Amount at risk** | [$x, being the full improper portion identified on reasonable assumptions] |
| **Quantified loss** | [$y, supported by documents — or "not yet quantifiable"] |
| **Root cause** | [The control that failed: e.g. no duplicate-invoice block; single preparer can create and pay] |
| **Recommendation** | [Specific, owned, dated] |
| **Effect on the engagement objective** | [Addresses / does not address the whistle-blower allegation] |

## 8. Review

| Reviewer question | Answer |
|---|---|
| Can the test be re-performed from this paper alone? | Yes / No — if no, state what is missing and fix it |
| Does the population reconcile to a control total? | Yes — to [total] |
| Is every exception either investigated or explicitly outstanding? | Yes / No |
| Is the language free of accusation and of unsupported conclusion? | Yes / No |
| Is any personal data disclosed beyond what is necessary? | [State what was included and why] |

```
Prepared by:  ________________  [initials, date]
Reviewed by:  ________________  [initials, date]     (must be a different person)
```

---

## Rules that keep working papers defensible

1. **Write it as you go.** A working paper written from memory a week later is a story, not evidence.
2. **Hash the source file** when you receive it and record the hash on every working paper that uses it.
3. **One test, one paper.** Do not combine two tests to save paper — reviewers need to re-perform one at a time.
4. **Show the exclusions.** What you left out of the population is as important as what you tested.
5. **State the tolerance** you used for matching. "Duplicate" means different things at different tolerances.
6. **Distinguish the three amounts:** total value, value at risk, quantified loss. Every time.
7. **Never overwrite a working paper.** Correct on a new version and note why (`v2: corrected the
   population to exclude internal transfers, per review note 3`).
8. **Reference every document** you relied on (document register number, date, page) so it can be found again.
