# Practical assessments

Three timed practical exams. They are deliberately similar to real engagement work: you get data, a
brief and a deadline. Mark yourself against the rubric, or have a colleague mark it.

---

## Practical Exam 1 — Modelling and DAX (4 hours, 100 points)

**Brief:** You are the analyst on a new engagement. The client has sent the Mhondoro ledger extract and
asked for "a report that shows whether the business is doing better than last year, and the numbers must
tie to our trial balance".

**You must produce:**

1. A `.pbix` with a clean star schema (30 points)
   - Text keys, one date table marked as such, correct cardinality and direction.
   - Role-playing user dimension handled correctly.
   - Orphan-key test and unbalanced-journal test built.
2. A measure set demonstrating (40 points)
   - Total revenue, COS, gross profit, gross margin %, operating profit, PAT.
   - Opening / movement / closing balance engine with a reconciliation measure that returns "Ties".
   - YTD, prior-year, prior-month and same-period-last-year comparatives.
   - DSO, DPO, DIO, cash conversion cycle with definitions documented.
3. A one-page validation page (20 points) showing at least eight control checks with expected values.
4. A methodology note (10 points): sign conventions, current-year-result treatment, ratio definitions,
   known limitations.

**Expected results** (your model must reproduce these, ±0.01):

| Check | Value |
|---|---|
| GL lines | 13,929 |
| Total debits = credits | 122,878,886.54 |
| Revenue FY2024 / FY2025 (9M) | 13,786,573 / 10,543,059 |
| Gross margin FY2024 / FY2025 | 49.3% / 50.5% |
| PAT FY2024 / FY2025 | 447,052 / −61,867 |
| BS check | 0.00 |
| AR / AP / inventory / cash at 30 Sep 2025 | 3,790,174 / 2,373,621 / 871,343 / 792,548 |

**Rubric penalties:** any headline number that does not tie (−10 each, minimum 0); undocumented measures
(−5); an unbalanced-Journal test that returns a non-zero count without explanation (−10).

---

## Practical Exam 2 — Forensic analytics (5 hours, 100 points)

**Brief:** The Audit Committee of Mhondoro Manufacturing has received a whistle-blower report alleging
payments to connected suppliers and the use of journal entries to conceal transactions. Analyse
1 January 2024 – 30 September 2025.

**You must produce:**

1. Test programme (25 points): 12 tests, each with population, assertion, expectation, exception rule
   and follow-up.
2. Forensic workbench (35 points): the five pages from Module 9, with the risk score and the evidence
   register exportable.
3. Findings summary (30 points): findings quantified to **$1,945,536.55 across 171 flagged lines**,
   with value at risk distinguished from quantified loss.
4. Data governance record (10 points): hashes, extraction dates, integrity checks, reconciliation to
   the control total of $122,878,886.54.

**Rubric**

| Area | Full marks require |
|---|---|
| Detection | All seven schemes found: duplicates (42 lines, $368,023.48), ghost vendors (4 vendors, $445,568.39 injected / $2,773,799.20 total), thresholds (30 lines, $207,720), split purchases (42 lines, $223,924.68), weekend/after-hours (21 lines, $406,300), SoD (15 lines, $279,600), unreversed accruals (6 lines, $14,400) |
| Quantification | Overpayment stated as $184,011.74 (conservative half) and the basis explained |
| Evidence | Every finding traceable to journal IDs, invoice references, dates and users |
| Judgement | No accusations; intent not asserted; corroboration requirements stated |
| Presentation | An Audit Committee could act on it |

---

## Practical Exam 3 — Advisory proposal (2 hours, 100 points)

**Brief:** Using your exam-2 findings, prepare the **next-phase proposal** for Mhondoro Manufacturing:
a continuous monitoring retainer plus the control remediation work.

**You must produce:**

1. A completed proposal using [`../business/Client_Proposal_Template.md`](../business/Client_Proposal_Template.md) (40 points).
2. An engagement letter covering data handling, confidentiality, retention and independence (30 points).
3. A priced scope-of-work estimate with hours by phase and role, at Maxhub day rates (20 points).
4. A 10-minute pitch outline: problem, approach, price, and the three client questions answered (10 points).

**Rubric**

| Area | Full marks require |
|---|---|
| Commercial logic | Price built from hours and roles, benchmarked to market ranges |
| Scope discipline | Clear "not included" list; assumptions that protect margin |
| Risk allocation | Data handling, liability, termination and retention clauses that are fair and specific |
| Client value | The retainer is tied to a monthly deliverable that the client's own team can use |
| Delivery | The pitch leads with the finding and the money, not with the tool |

---

## Marking record

| Assessment | Score | Pass mark | Date | Marker |
|---|---|---|---|---|
| Practical 1 — modelling & DAX | /100 | 70 | | |
| Practical 2 — forensic analytics | /100 | 70 | | |
| Practical 3 — advisory proposal | /100 | 70 | | |
| Capstone 1 — investigation (see rubric) | /100 | 70 | | |
| Capstone 2, 3 or 4 (see rubric) | /100 | 70 | | |

**Rule for self-marking:** if you cannot explain a number to a colleague in plain language, deduct the
points and rework it. The exam tests understanding, not file completion.
