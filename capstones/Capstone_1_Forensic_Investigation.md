# Capstone 1 — Forensic Investigation

**Client:** Mhondoro Manufacturing (Pvt) Ltd
**Engagement:** Suspected misappropriation, procure-to-pay and journal-entry cycles
**Period under review:** 1 January 2024 – 30 September 2025
**Deliverables:** findings report · evidence register · board presentation · remediation plan
**Estimated effort:** 8–10 hours · **Portfolio value:** this is the deliverable you show a prospective client

---

## 1. The instruction (simulated)

> *"The Audit Committee has received a whistle-blower report alleging that payments have been made to
> suppliers that are connected to employees, and that journal entries have been used to conceal
> transactions. You are instructed to analyse the company's accounting data for the period 1 January 2024
> to 30 September 2025, to identify and quantify any irregular transactions, and to report your findings
> to the Committee. You have full access to the accounting data extract. Your report must be capable of
> being relied upon by the Committee and, if required, by legal counsel."*

---

## 2. What you must produce

| # | Deliverable | Format | Assessed on |
|---|---|---|---|
| 1 | Engagement and methodology memo | 2 pages | Is the scope, data lineage and method clear and honest? |
| 2 | Test programme | Excel/Word table | 12 tests, each with population/assertion/expectation/exception/follow-up |
| 3 | Evidence register | Excel export from Power BI | 171 flagged lines, scored, with a conclusion column |
| 4 | Findings report | 8–12 pages, Maxhub structure | Quantification, evidence, root cause, recommendations |
| 5 | Board presentation | 12 slides | Can a non-accountant follow it? |
| 6 | Remediation plan | 1 page table | Specific, owned, dated, costed |
| 7 | `.pbix` workbench | Power BI file | Reproducible, documented, performs |

Use the templates in [`../business/`](../business/):
[`Advisory_Report_Template.md`](../business/Advisory_Report_Template.md),
[`PowerBI_Build_Standard.md`](../business/PowerBI_Build_Standard.md).

---

## 3. Phase plan

### Phase 1 — Prepare (60 min)

- Copy the data to a working folder. Do not analyse the originals.
- Record the SHA-256 hash of each source file, the date and time of extraction, and who provided it.
- Confirm the population: **13,929 ledger lines across 5,504 journals**; total debits = total credits
  = **$122,878,886.54** (including opening balances and the year-end close).
- Write the scope and limitations paragraph now (it is the hardest thing to write at the end).

### Phase 2 — Test (3 hours)

Run the 12-test programme from Lab 09. Save every result as a working paper with:
test ID · rule as written · population count · exceptions count · value · conclusion · preparer · date.

### Phase 3 — Investigate (2 hours)

For each of the top 30 exceptions by `Risk Weighted Value`, write a finding note:
what happened, evidence (journal IDs, invoices, dates, users), control that failed, amount at risk,
what is still needed to conclude.

### Phase 4 — Quantify (1 hour)

Produce three numbers per scheme — total value, value at risk, estimated loss — and be explicit about
the basis of each. State clearly that **estimated loss requires documentary corroboration** and is not
established by data analysis alone.

### Phase 5 — Report and present (2 hours)

Write the report, prepare the slides, deliver.

---

## 4. The known territory (your marking guide)

You should find all seven schemes. The authoritative detail is `data/raw/InjectionLog.csv` (171 lines).

| # | Scheme | Expected finding |
|---|---|---|
| 1 | Duplicate payments | 42 lines across 21 duplicate pairs, **$368,023.48** debited; probable overpayment **$184,011.74**; same invoice references, 4–12 days apart |
| 2 | Ghost / related-party vendors | 4 employee-linked vendors created Jul–Aug 2024 (SUP-771 to SUP-774), tax clearance blank, 7-day terms; **$445,568.39** injected; **$2,773,799.20** total paid to those vendors |
| 3 | Threshold avoidance | 30 payments of $4,985–$4,995 and $9,750–$9,900 — **$207,720.00** — siting just below the $5,000 PO and $10,000 approval limits |
| 4 | Split purchases | 21 pairs (42 lines), same vendor within days, each $3k–$5k, total above the PO limit — **$223,924.68** |
| 5 | Weekend / after-hours journals | 21 lines, **$406,300.00**, entered 02:00–04:00 or 22:00–23:00 and at weekends by USR-012, credited to the suspense account, no approver |
| 6 | Segregation-of-duties breach | 15 lines, **$279,600.00** — an Accounts Payable Clerk (USR-002) posting revenue credit notes |
| 7 | Unreversed accruals | 6 lines, **$14,400.00** |
| | **Total flagged** | **$1,945,536.55 across 171 journal lines** |

Supporting observations that belong in the report:

- Suspense account balance **$51,058.87** — an unresolved clearing account.
- **129 of 1,400** bank transactions unreconciled; oldest unmatched item 210 days.
- **168 of 520** AP invoices failed the three-way match.
- **81 of 650** expense claims paid without a receipt.
- Trade receivables of **$3.79m** against $10.54m of nine-month revenue (DSO ≈ 98 days on days elapsed).

---

## 5. Report skeleton (use exactly this structure)

```
1. Cover page ............ client, engagement, period, date, classification
2. Executive summary ..... half a page: instruction, what we did, what we found (5 bullets with
                           amounts), what we recommend (3 actions), the limitation sentence
3. Basis of our work ..... instruction, scope, data received (with hashes and dates), methods,
                           limitations, reliance on client data
4. Findings (7) .......... one page each, in descending value order:
     Finding / Amount at risk / What we observed / How we tested / Why it matters /
     Root cause / Recommendation
5. Aggregate quantification ... table by scheme with total value, value at risk, estimated loss,
                           and the basis of each number
6. Control environment observations ... the supporting observations listed above
7. Recommendations ....... remediation plan with owner, date, cost
8. Appendices ............ A: test programme, B: evidence register (171 lines), C: data lineage,
                           D: methodology note for the Power BI model, E: glossary
```

**Language discipline** — the marking rubric awards more for accuracy than for drama:

| Do not write | Write instead |
|---|---|
| "The clerk stole $2.5m from the company." | "Payments totalling $2,773,799.20 were made to four vendors that the vendor master identifies as employee-linked. The propriety of these payments requires corroboration." |
| "This is definitely fraud." | "The pattern is inconsistent with the stated control environment and is not explained by the supporting documentation provided." |
| "The total loss is $1.8m." | "Exceptions totalling $1,945,536.55 were identified across 171 journal lines. The amount at risk is $X; estimated loss cannot be quantified without document-level corroboration, which we recommend as the next phase." |

---

## 6. Marking rubric (100 points)

| Area | Points | What earns full marks |
|---|---|---|
| Data governance | 10 | Originals untouched, hashes recorded, lineage documented, deletion/retention noted |
| Test programme | 15 | All 12 tests, correctly specified, with populations and rule logic a reviewer can re-perform |
| Detection accuracy | 20 | All seven schemes found; false positives identified and dismissed with reasons |
| Quantification | 20 | Value vs value at risk vs loss distinguished; conservative assumptions stated; totals tie to the ledger |
| Evidence quality | 10 | Each finding traceable to document references (journal IDs, invoice numbers, dates, users) |
| Report quality | 15 | Structure, clarity, tone, no accusations, limitations stated, recommendations specific |
| Board presentation | 10 | A non-accountant can follow it; each slide answers one question |

**Pass: 70.** Below 70, rework the quantification and report sections before adding this to your portfolio.

---

## 7. Extension (do this if you want the engagement to be genuinely sellable)

1. **Recovery pack:** for the duplicate payments, draft the letter to the supplier requesting the
   duplicate be refunded, with the evidence attached.
2. **Control design:** write the redesigned process for vendor onboarding and payment approval —
   a one-page flow with the control points marked.
3. **Monitoring:** propose the monthly exception report Maxhub would run for the client as a retainer
   (which of the 12 tests, how often, who reviews it, what they do with exceptions). Price it — see
   Module 12.
4. **Pitch it:** present the retainer as the natural next phase in your board presentation. This is how
   an investigation becomes a recurring engagement.
