# Capstone 3 — Data Analytics Engagement

**Client:** Mhondoro Manufacturing (Pvt) Ltd
**Engagement:** Procurement, receivables and cash analytics suite
**Sellable as:** internal audit analytics / data analytics engagement ($6,000–$18,000)
**Effort:** 8–10 hours · **Pass mark:** 70/100

---

## 1. The brief (as the client would put it)

> *"The audit committee meets in three weeks. We have a new financial controller and the board wants
> assurance that we are actually buying what we pay for, that our debtors are being collected, and that
> our cash is being managed. Last year's external audit found nothing because they only tested samples.
> We want the whole population tested, and we want to see it ourselves."*

— [Client contact], Audit Committee Chair

## 2. What you must deliver

| # | Deliverable | Format | Audience |
|---|---|---|---|
| 1 | Procurement analytics report — spend concentration, vendor performance, PO compliance, three-way match exceptions | Power BI page + 2-page memo | Procurement Manager, CFO |
| 2 | Receivables analytics report — ageing, DSO, credit-limit breaches, disputed balances, collections priority list | Power BI page + collections action list | Credit Controller |
| 3 | Cash and working-capital report — cash conversion cycle, bank reconciliation exceptions, forecast vs actual | Power BI page | CFO |
| 4 | Data quality report — what is wrong with the source data and what it costs the business | One page, hidden tab | IT / Finance systems |
| 5 | Exception register | Excel export from the model | Internal audit |
| 6 | Committee pack | 8-slide deck + speaker notes | Audit Committee |

Every page must drill through to the underlying transactions and reconcile to the trial balance.

## 3. Background detail you should use

**The three-way match.** A purchase is properly controlled when the purchase order, the goods-received
note and the supplier invoice agree on quantity and price *before* payment. **168 of 520** AP invoices in
the dataset fail this test — that is 32%, not a rounding error.

**Procurement spend.** Total supplier spend is **$30,505,968** across 26 vendors; the largest vendor
accounts for **5.3%** and the top five only **24.6%** — unusually flat. **19 of 26** vendors are needed
to reach 80% of spend. Flat concentration is not automatically bad, but it means no single vendor
relationship is being managed strategically, and it makes duplicate-vendor creation easier to hide.

**Receivables.** Closing AR is **$3,790,174** on **$10,543,059** of nine-month revenue — DSO of
**98 days** on days elapsed. **11 of 420** customer accounts are flagged as disputed. The ageing is
spread across Current/1–30/31–60/61–90/91–180/Over 180 buckets; the collections priority list is not
"the biggest balance" but *balance × probability of collection × days at risk*.

**Cash.** Closing cash of **$792,548** against **$925,427** at the prior year end — a fall of $132,879
that the statements do not explain in words, while receivables grew by $1.2m. **129 of 1,400** bank
transactions are unreconciled, worth **$1,884,271**, of which **27 items are over 90 days** old and the
oldest is **210 days** old. The suspense account holds **$51,058.87**.

**Working capital.** DPO 124 days, DSO 98 days, DIO 46 days, giving a cash conversion cycle of
**20 days** — apparently efficient, but only because the company is stretching suppliers (124 days) to
pay for customers who pay in 98. The quality of that working capital is poor: it relies on both sides
being tolerant.

## 4. The seven analyses you must build

### Analysis 1 — Spend concentration and vendor profile
- Pareto of spend by vendor; cumulative % line; the **80% threshold** crosshair.
- Vendor profile table: spend, number of invoices, average invoice, last invoice date, employee-linked
  flag, whether the vendor has a PO on file, three-way match performance.
- **Client question it answers:** where is our non-payroll money going, and who are we dependent on?

### Analysis 2 — Procurement control testing
- Three-way match exception rate over time, by vendor and by buyer.
- Invoices without a PO (**109**), invoices with a PO but no GRN, invoices with price/quantity variance
  beyond tolerance.
- **Client question:** are we paying for things we did not order or receive?

### Analysis 3 — Vendor master quality
- Near-duplicate names (run [`../scripts/fuzzy_match_vendors.py`](../scripts/fuzzy_match_vendors.py)
  against the vendor master and against invoice-level vendor names).
- Bank-detail changes in the period (a classic fraud vector).
- Vendors with no tax clearance, no address, or created and paid inside a week.
- **Client question:** has anyone created a supplier we do not actually have?

### Analysis 4 — Days sales outstanding and the ageing bridge
- DSO trend by month, split into: same-month collections, slow payers, disputes, and credit notes.
- Ageing bridge: opening AR → invoiced → collected → written off → write-offs/credit notes → closing AR.
- **Client question:** is the debt real and is it being collected?

### Analysis 5 — Collections priority
- Score = outstanding balance × days overdue × (1 for undisputed / 0.5 disputed / 1.5 for a first-time
  large balance) — define your own and document it.
- Top 25 accounts with contact, invoice references, and the action for each.
- **Client question:** who do I call on Monday morning?

### Analysis 6 — Bank reconciliation exceptions
- 129 unreconciled items ($1,884,271) by age, by account and by amount; the 27 items over 90 days categorised.
- Matching logic: exact amount and reference, then amount and date within 3 days, then amount only.
- **Client question:** is our cash real, and are we missing payments or receipts?

### Analysis 7 — Working capital and cash conversion
- DSO / DPO / DIO / CCC trend, each with its formula in the tooltip and a methodology note.
- Scenario slider: "if collections improve to 60 days, cash released = ?" (build it with a what-if
  parameter, not a hard-coded calculation).
- **Client question:** how much cash is trapped, and what does fixing it release?

## 5. Requirements (functional and non-functional)

| # | Type | Requirement |
|---|---|---|
| 1 | Functional | All figures reconcile to the trial balance; the close-pack checks appear on a hidden page |
| 2 | Functional | Every page has drillthrough to transaction detail |
| 3 | Functional | Exception register exportable to Excel with the client's reference numbers |
| 4 | Functional | Slicers for period, cost centre and vendor/customer; synchronised across pages |
| 5 | Functional | Any ratio shows its formula and its date basis in a tooltip or methodology note |
| 6 | Non-functional | Refresh under 5 minutes on the client's laptop |
| 7 | Non-functional | Every visual title is a sentence with a finding |
| 8 | Non-functional | No personal data exposed beyond what the role requires (design RLS for the credit team) |
| 9 | Non-functional | Report works on a screen and printed to A4 landscape |
| 10 | Professional | A written methodology note and a data-quality disclaimer accompany the pack |

## 6. Process (follow it, and write it up as you go)

1. **Data request and confirmation** — list every file, period and owner; record extraction dates.
2. **Integrity check** — debits = credits = **$122,878,886.54**; orphan keys zero; reconcile AR/AP
   sub-ledgers to the control accounts.
3. **Model** — reuse the star schema from Modules 3–5; add the collections and procurement-specific
   tables as conformed dimensions (do not duplicate the model).
4. **Build** the seven analyses against the business questions, not the available fields.
5. **Reconcile** each page to the trial balance and to the client's own reports; document every
   difference and its cause.
6. **Peer review** — a second person re-performs one number per page.
7. **Committee pack** — one slide per analysis: question, finding, number, recommendation, and the
   limitation.
8. **Handover** — user guide, recorded walkthrough, `.pbix`, and the exception register.

## 7. What "good" looks like (marking guide, 100 points)

| Criterion | Points | Full marks require |
|---|---|---|
| Procurement analysis | 20 | Pareto with the 80% line; three-way match failures quantified by vendor and period; 109 no-PO invoices identified and explained |
| Receivables analysis | 20 | DSO 98 days with the definition stated; ageing bridge ties to closing AR of 3,790,174; collections list is ranked by a documented score, not by size |
| Cash and working capital | 15 | 129 unreconciled items ($1.88m) aged and categorised; CCC of 20 days decomposed; what-if shows cash released |
| Data quality report | 10 | Suspense $51,058.87 disclosed; source-data failures traced to processes and owners, with cost implications |
| Reconciliation and QC | 10 | Every page ties; close-pack page returns zeros; independent re-performance documented |
| Committee pack | 10 | One slide per analysis with a recommendation and an honest limitation; a committee member could act on each slide |
| Methodology and documentation | 10 | Formulas, date basis, exclusions and definitions all stated; a stranger could reproduce the numbers |
| Professional presentation | 5 | Sentence titles, consistent theme, drillthrough, no decorative clutter |

**Automatic deductions:** any unreconciled headline figure (−10 each); a ratio presented without its
definition (−5); a finding with no recommendation (−5).

## 8. The commercial wrap (Module 12 practice)

**Scope your work as if you were billing it:**

| Phase | Hours | Role | Rate | Fee |
|---|---|---|---|---|
| Data preparation and integrity | 6 | Analyst | $120 | $720 |
| Procurement analytics | 8 | Analyst/Senior | $150 | $1,200 |
| Receivables and collections | 8 | Senior | $200 | $1,600 |
| Cash and working capital | 6 | Senior | $200 | $1,200 |
| Model build and reconciliation | 10 | Senior | $200 | $2,000 |
| Committee pack and presentation | 6 | Manager | $280 | $1,680 |
| Peer review and QC | 4 | Partner | $450 | $1,800 |
| **Total** | **48** | | | **$10,200** |

Then answer the three client questions in writing:

1. *How long?* — 4 calendar weeks, 12 client-hours of involvement.
2. *How much?* — $10,200 fixed fee, plus a proposed $1,200/month analytics retainer for monthly
   refreshes, exception reporting and one review call.
3. *How do I know it is right?* — every figure reconciles to the trial balance; a partner who did not
   build it re-performed a number on every page; the methodology note lets your team reproduce
   everything independently.

**Extension exercise:** write the 90-second pitch that sells the *retainer*, not the report, and answer
the objection "we already get this from our auditors" (they test samples; you test populations, more
often, and you leave the model behind).

---

## 9. Deliverable checklist

- [ ] Seven analyses built and each one answering its client question
- [ ] Every figure reconciled to the trial balance; close-pack page returns zeros
- [ ] 80% Pareto crosshair on the spend chart
- [ ] 168 of 520 three-way match failures analysed by cause
- [ ] 129 of 1,400 unreconciled bank items ($1,884,271) aged, 27 of them over 90 days
- [ ] Collections priority list ranked by a documented score
- [ ] What-if cash-release scenario working from a parameter
- [ ] Method note, user guide, exception register, committee pack
- [ ] Priced scope of work and the three client answers in writing
