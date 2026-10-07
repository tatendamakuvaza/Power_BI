# Portfolio case study template

Use this once per completed capstone. One page, written for a prospect or an interviewer who has two
minutes — not for a fellow analyst. Attach the artefacts it refers to (redacted where necessary).

**Rule:** label every case study built on the Mhondoro/Maxhub data as **"simulated engagement data"**.
It costs nothing to be honest and it protects you if a prospect ever checks.

---

# [Headline: the outcome, with the number]

> *Examples:*
> *"Found $1.9m of exceptions — and $184,011 of specifically recoverable duplicate payments — in 21 months of payments data."*
> *"Replaced an eight-day month-end close with a reporting pack that reconciles itself and flags its own data quality."*
> *"Built a client-churn model that beats the naive baseline by 17.8 points and tells the partners who to call this quarter."*

**Client:** [Simulated / anonymised real client] — sector, size, systems
**My role:** [Lead analyst / Designer and builder / Reviewer]
**Period:** [dates] · **Effort:** [days] · **Tooling:** [Power BI, DAX, Power Query, Python]

---

## 1. The situation (2–3 sentences, in the client's words)

> *"The audit committee had a whistle-blower report alleging payments to connected suppliers, our external
> auditor had tested only a sample, and the board wanted to know whether the numbers in the management
> pack could be trusted."*

## 2. What I was asked to deliver

- [Deliverable 1 — in the client's language, not the tool's]
- [Deliverable 2]
- [Deliverable 3]

## 3. What I did (the part a buyer evaluates)

1. **Data integrity first.** Received [n] extracts ([rows] rows); hashed and logged them; reconciled the
   ledger to the trial balance of **$122,878,886.54 debits = credits** before analysing anything.
2. **Built the model.** [Star schema, n tables; documented grain; role-playing dimensions handled;
   control-check page with debits/credits, orphan keys, unbalanced journals.]
3. **Ran the analytics.** [n tests with population, assertion, expectation, exception and follow-up;
   document-level corroboration of every exception above $X.]
4. **Quantified conservatively.** Distinguished total value, value at risk and quantified loss; stated
   the assumptions in writing.
5. **Reported and handed over.** [Report, board pack, evidence register, user guide, recorded handover —
   the client keeps the model.]

## 4. The numbers (put them in a table — this is the section that gets read)

| Measure | Value |
|---|---|
| Population tested | 13,929 ledger lines / 5,504 journals |
| Total value of the population | $122,878,886.54 |
| Exceptions identified | 171 journals — $1,945,536.55 |
| Improper amount (value at risk) | [$x] |
| Quantified loss (document-supported) | [$y] |
| Outcome for the client | [Recovery process opened / eight-day close reduced to three / three at-risk clients retained] |

## 5. What made it defensible

- Every figure reconciled to a control total before it was reported.
- Every exception traceable to a journal ID, a document and an approval trail.
- Findings written without accusation: transactions and controls, never people.
- Independent review by a second person before issue, with a signed QC checklist.
- Method documented so a third party could re-perform the work.

## 6. What I would do differently next time

[*One or two honest lines. This section is why interviewers believe the rest of the page.*]

> *Example: "I would agree the definition of 'duplicate' in writing at kick-off. Two of the 21 pairs
> needed re-work after the client questioned the 10-day matching window."*

## 7. The offer this case study supports

| Next phase | What it is | Indicative price |
|---|---|---|
| [Continuous monitoring retainer] | [Monthly exception report from the client's own data; quarterly control review] | [$900–$2,500 per month] |
| [Control remediation] | [Duplicate-invoice block, vendor onboarding controls, JE approval workflow] | [$x] |
| [Analytics build] | [Reporting pack on the model built during the review] | [$x] |

## 8. Attachments

- [ ] Findings report (redacted) — PDF
- [ ] Evidence register extract — Excel, one page
- [ ] One chart that proves the pattern — PNG
- [ ] Methodology note — PDF, one page
- [ ] Testimonial or client feedback, if available — [with written permission]

---

## How to present it in 90 seconds (the spoken version)

1. **Situation** (10s): "A whistle-blower alleged payments to connected suppliers; the audit had only tested a sample."
2. **What I did** (20s): "I tested 100% of 21 months of payments — 13,929 ledger lines — against 12 tests, and corroborated every exception to documents."
3. **The number** (15s): "Exceptions of $1.9m; $184,011 of duplicate payments I could support with documents; the rest is value at risk pending supplier confirmations."
4. **Why it holds up** (15s): "Every figure reconciles to a trial balance of $122.9m, every exception traces to a document, and a second reviewer re-performed the work before it was issued."
5. **The next step** (15s): "The obvious next phase is a monthly monitoring retainer so this is caught in month one next time, and a control fix so it cannot recur — I can scope both in a week."
6. **Stop talking.** Let them ask the technical questions; the answers are in sections 3 and 5.
