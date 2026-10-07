# Career and portfolio guide

You have an accounting background and a new technical skill. This file is about converting them into
work — inside an employer, or through Maxhub.

---

## 1. Where this skill set fits

| Role | Employers | What they pay for |
|---|---|---|
| Forensic accountant / investigator | Advisory firms, banks, insurers, regulators | Finding and proving what went wrong |
| Data analytics / internal audit analytics | Corporates, audit firms, banks | Testing 100% of populations, not samples |
| Management reporting / FP&A analyst | Any medium or large business | Reporting that closes faster and explains itself |
| BI / analytics consultant | Consultancies, boutique firms, freelance | Building the tools and handing them over |
| Risk and controls analyst | Banks, telecoms, insurance | Continuous control monitoring |
| Practice owner (Maxhub) | Yourself | All of the above, sold as services |

The differentiator you bring: you understand debits, credits, controls and materiality. Most Power BI
developers do not. Do not compete on visuals — compete on **rigour and reconciliation**.

---

## 2. Portfolio: what to build and what to show

You need **three artefacts**, not twenty screenshots.

### Artefact 1 — The forensic investigation (Capstone 1)
Show: the findings report (redacted), the test programme, one chart that proves a pattern (the threshold
histogram or the duplicate-pair scatter), and the executive summary page.

Say: *"I analysed 21 months and 13,929 ledger lines, ran 12 tests, found exceptions totalling $1.9m
across 171 journals, and quantified the recoverable amount conservatively at $184,011.74. The client's
audit committee used it to open a recovery process."*

### Artefact 2 — The reporting pack (Capstone 2)
Show: the executive page, the P&L with variance, the close-pack page that proves the numbers tie.

Say: *"I can replace an eight-day Excel close with a model that reconciles to the trial balance, shows
its own control checks, and lets the CFO drill to any transaction."*

### Artefact 3 — The predictive model (Capstone 4 / Lab 11)
Show: the churn or default model page with its metadata (version, training date, accuracy, baseline)
and the driver explanation.

Say: *"This model beats the naive baseline by 18 percentage points and tells the partner team which
client relationships are deteriorating, and why."*

**Do not** show: dashboards of fictional sales, decorative nightingale charts, or anything you cannot
explain down to the source row.

---

## 3. How to tell the story

Use this structure every time (interview, LinkedIn, proposal):

1. **The problem in the client's language** ("the board did not trust the DSO figure").
2. **What you did** (data, tests, model, in one or two sentences — no tool names yet).
3. **The number** (found, recovered, saved, reduced).
4. **The evidence** ("reconciled to a trial balance of $122.9m of debits").
5. **The tool**, mentioned last, as the means ("built in Power BI so the client could refresh it").

Accountants who learn analytics often lead with the tool. Buyers pay for outcomes and reassurance.

---

## 4. Preparing for the interview

**Technical questions you should be able to answer cold**

- Explain row vs filter context with an example.
- Why is a star schema better than one flat table for a P&L?
- How would you test for duplicate payments across 5 million rows?
- How do you handle a client who says "the dashboard is wrong"?
- What does Benford's Law not tell you?
- How do you stop the same number appearing differently on two pages?

**Case exercise you will probably be given**

"We have given you 12 months of supplier payments. Tell us what you would look at and why."
Answer with the five-element test design (population, assertion, expectation, exception, follow-up),
then prioritise: duplicates and ghost vendors first (money out), then thresholds, then journal entries.

**The question that separates candidates**

*"How do you know your numbers are right?"*
Answer: reconciliation to control totals, orphan-key and balance tests, an independent review before
issue, and a methodology note that lets someone else re-perform the work.

---

## 5. Positioning Maxhub (if you are building the practice)

**One-liner:** "Maxhub finds what is wrong in your numbers and builds the reporting that stops it
happening again — forensic accounting, analytics and AI for Zimbabwean businesses."

**Three proof assets to publish**

1. An anonymised case study with a number in it ("identified $184k of duplicate payments in 21 months").
2. A free tool people can use: a "Procurement Risk Scan" checklist, or a template Power BI file.
3. A monthly analytical post: one chart, one finding pattern, two paragraphs of what it means.

**Where the work comes from**

| Source | Why they buy |
|---|---|
| External auditors | They need forensic and analytics depth they do not staff |
| Lawyers (fraud, insolvency, contract disputes) | They need quantification and a report that survives scrutiny |
| Banks and credit committees | They need to understand a borrower's numbers |
| SMEs with an ERP and no analytics | They need reporting that closes faster |
| Boards after a loss | They need to know whether it can happen again |
| Donor/development programmes | They need assurance over funds and fraud-risk management |

**The first engagement rule:** start small, deliver fast, quantify the outcome. A $2,500 risk scan that
finds something is worth more to your pipeline than a $50,000 proposal that takes three months to win.

---

## 6. Continuing professional development

| Area | Next step |
|---|---|
| Certification | Microsoft PL-300 (Power BI Data Analyst) — the credential clients recognise |
| Forensic | Certified Fraud Examiner (CFE) — the standard for investigations |
| Analytics | ACFE/ACCA analytics certificates; Python for data analysis (pandas) |
| Audit analytics | CAAT/IDEA skills translate directly; learn SQL |
| AI governance | Short courses on data protection and AI risk (Zimbabwe's Cyber and Data Protection Act (2021) is your local context) |
| Professional body | Maintain ICAZ/ACCA CPD records — your course hours count |

**A 12-month plan**

| Quarter | Focus | Output |
|---|---|---|
| Q1 | Finish this course; PL-300 exam | Certification, three portfolio artefacts |
| Q2 | Five free/low-fee risk scans under a short confidentiality letter | Case studies, first paying retainer |
| Q3 | Productise the monitoring retainer; publish monthly | Two retainers signed |
| Q4 | Larger investigation or ML build; write it up | A flagship case study and a higher price point |

---

## 7. The ten principles that keep you employed

1. Reconcile everything, every time.
2. Document as you go; memory is not evidence.
3. Never overstate a finding — understate it and let the evidence speak.
4. Keep the client's data safer than they do.
5. Hand over the model; do not hold clients hostage to your file.
6. Say "I do not know yet, and here is how I will find out".
7. Charge for the review, the documentation and the handover, not just the build.
8. Write in the client's language, not yours.
9. Keep learning: the tools change, the standards do not.
10. Protect your independence — it is the only asset you cannot rebuild quickly.
