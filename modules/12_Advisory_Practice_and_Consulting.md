# Module 12 — The Advisory Practice

**Time:** 6 hours · **Prerequisite:** Modules 1–11

> You now have a skill. This module is about turning it into a business: what you sell, what you
> charge, how you deliver it consistently, and how you keep the standard high enough that clients
> come back. Everything here is written for **Maxhub Pvt Ltd**.

---

## 12.1 The Maxhub service map

| Service line | What the client buys | Core deliverable | Indicative fee (USD) |
|---|---|---|---|
| **Forensic accounting** | Investigation of suspected misappropriation, dispute support, quantification of loss | Findings report, evidence register, remediation plan, expert-ready working papers | $8,000 – $45,000 per investigation |
| **Data analytics** | Continuous assurance: procurement, AR, payroll, expense analytics | Power BI analytics suite + monthly exception report | $2,500 build + $650–$1,500/month |
| **Machine learning & AI** | Churn/default prediction, anomaly detection, forecasting, document extraction | Scored dataset + Power BI pages + model documentation | $6,000 – $30,000 per model, $800–$2,000/month monitoring |
| **Advisory / CFO services** | Management reporting pack, budgeting, cash-flow forecasting, IFRS support | Live reporting pack + monthly commentary + board slides | $1,500 – $4,500/month retainer |
| **Internal audit co-sourcing** | Risk-based internal audit with data analytics | Audit plan, workpapers, findings, follow-up tracker | $1,200 – $3,500/month retainer |
| **Training** | Power BI and analytics skills for client finance teams | Delivered course (this one), templates, coaching | $1,800 – $6,000 per cohort |

The pricing logic, and the three ways to charge:

| Model | When to use | Watch out for |
|---|---|---|
| **Fixed fee per deliverable** | Well-defined scope (a dashboard, a model, a report) | Scope creep — list what is *not* included |
| **Day rate / hourly** | Investigations, advisory, anything exploratory | Clients dislike open-ended cost; cap and review weekly |
| **Retainer (monthly)** | Recurring reporting, analytics, monitoring | Define inclusions (refreshes, support hours, review meetings) |
| **Success / contingency element** | Recovery work, where permitted | Check independence and local ethical rules before proposing |

Indicative Maxhub day rates (adjust to your market): analyst $180–$280, senior consultant $300–$450,
manager $450–$650, partner/director $700–$1,200.

---

## 12.2 Packaging: how to turn a skill into a product

The difference between "I do Power BI" and a product:

| Generic offer | Productised Maxhub offer |
|---|---|
| "I can build you a dashboard" | **"Month-End Close Pack — 10-day close, live P&L, BS, cash flow and 9 control checks, delivered as a Power BI app with a monthly 60-minute review call."** |
| "I can analyse your data" | **"Procurement Risk Scan — 12 forensic tests across your last 24 months of spend, an exception register and a board-ready findings summary."** |
| "I can do machine learning" | **"Debtor Default Radar — every open invoice scored for late-payment risk, with a collections priority list refreshed monthly."** |
| "I can write reports" | **"Board Reporting Retainer — a one-page KPI pack, commentary, and a live Power BI report for your board pack."** |

Each productised offer should have: a name, a defined scope, a defined deliverable, a price, a
timeline, and a "what's not included" list. That is what goes in the proposal
([`../business/Client_Proposal_Template.md`](../business/Client_Proposal_Template.md)).

---

## 12.3 The engagement lifecycle (Maxhub's standard)

```
1. LEAD            -> referral, LinkedIn, tender, existing client, networking
2. QUALIFY         -> do they have data, a decision-maker, a budget, a deadline?
3. PROPOSAL        -> scope, approach, team, timeline, fee, assumptions, exclusions
4. ENGAGEMENT LETTER -> the contract: scope, fee, access, confidentiality, data handling,
                        limitation of liability, termination, deliverables, standards
5. MOBILISE        -> data request list, access, kick-off, confidentiality and conflict checks
6. FIELDWORK       -> data cleaning, modelling, testing, working papers
7. QUALITY CONTROL -> independent review (12.5); reconciliation to client control totals
8. REPORT          -> findings, recommendations, presentation
9. FOLLOW-UP       -> remediation tracking, next-phase proposal
10. ARCHIVE        -> engagement file, versioned .pbix, data retention and deletion policy
```

Step 5 and step 10 are where small firms lose money and reputation. Do not skip them.

### Data request list (send before the first day of fieldwork)

1. Trial balance for the period(s), with the account structure.
2. General ledger detail export — every line: date, journal number, account, description, debit, credit,
   user, source system.
3. Master files: chart of accounts, cost centres, customers, vendors, employees, users/roles.
4. Sub-ledgers: AR ageing, AP ledger, fixed asset register, inventory listing.
5. Bank statements for all accounts (and pass-through accounts).
6. Budget/forecast files and the board pack for the same period.
7. Approval matrix and delegation-of-authority document.
8. Prior audit / investigation reports and the current risk register.
9. A named client contact for data queries and a named escalation contact.

Always ask for **the export, not the screen**. Screenshots cannot be tested at scale and cannot be
refreshed.

---

## 12.4 Delivery standards (Maxhub's build standard)

Non-negotiables for any Power BI asset delivered to a client
(full version in [`../business/PowerBI_Build_Standard.md`](../business/PowerBI_Build_Standard.md)):

1. **Naming:** `Dim*` for dimensions, `Fact*` for facts, measures in a `_Measures` table organised in
   display folders, Title Case, no cryptic abbreviations.
2. **Documentation:** every measure has a description; a `ModelMetadata` table records source, extraction
   date, refresh frequency, model owner and version.
3. **Reconciliation:** a visible page or card proving the model ties to the client's trial balance
   (debits = credits, BS check = 0, P&L ties to retained-earnings movement).
4. **Refresh:** the client can refresh it themselves (documented steps + who to call), or it runs
   scheduled in the Service with a failure notification.
5. **Security:** row-level security where a client has multiple entities or branches; no personal data
   in reports unless required and minimised.
6. **Performance:** any visual over 3 seconds must be optimised or explained.
7. **Handover:** a one-page user guide, a training session recorded, and the `.pbix` plus the data
   dictionary handed to the client at the end. **Clients own their data and their model.** Withholding
   it destroys referrals.
8. **Versioning:** `ClientName_ReportName_vX.Y.pbix`, with a change log in the working papers.

---

## 12.5 Quality control: the independent review that saves the engagement

Before any deliverable leaves Maxhub, a person who did not build it must:

- [ ] Re-perform one calculation from raw data end-to-end
- [ ] Confirm every headline number ties to a control total (debits = credits; ageing to the GL balance;
      P&L profit to the retained-earnings movement)
- [ ] Check the evidence register: is each flag traceable to a source document reference?
- [ ] Read the report as the client: does the exec summary stand alone? Is every amount explained?
- [ ] Check language: facts vs inferences clearly separated; no accusations; limitations stated
- [ ] Confirm data handling followed the engagement letter (who saw what, where it is stored, deletion date)
- [ ] Sign and date the QC checklist — it goes in the engagement file

**Never** issue a forensic deliverable without an independent review. If you are a one-person firm,
engage an external reviewer or a peer firm on a reciprocal basis — the cost of one review is far below
the cost of one retraction.

---

## 12.6 Marketing and business development for a data-driven firm

| Channel | What to publish | Cadence |
|---|---|---|
| LinkedIn | A finding pattern (anonymised), a chart, a two-paragraph lesson. "How a $4,985 payment dodges a $5,000 control" performs better than "we do Power BI" | 2–3 per week |
| Website / landing pages | One page per productised service, with a sample dashboard (anonymised) | Quarterly refresh |
| Speaking | CPD sessions for the local institute, chamber of commerce, industry associations. Teach the method; clients follow | Monthly |
| Referral network | Auditors, lawyers (fraud, insolvency), banks (credit teams), insurers (claims) — each has clients with your problem | Quarterly touch points |
| Content lead magnets | "Procurement Risk Scan — free 12-test summary for one year of data" converts better than any brochure | Continuous |
| Client reviews | A quarterly value review with every retainer client: what the analytics found, what was actioned, what we propose next | Quarterly |
| Newsletter | One-page: a case study, a technical tip, a regulatory update | Monthly |

**Sales discipline for advisory work:** sell the *outcome* (cash recovered, control restored, reporting
that closes in 5 days), never the tool. Clients do not buy dashboards; they buy certainty, speed and
recoveries.

### A 90-day plan for the practice

| Days | Focus | Output |
|---|---|---|
| 1–30 | Finish the course; build Capstone 1 and 2 on your own or a friendly client's data | Two portfolio pieces, one case study, three productised offers |
| 31–60 | Publish: three LinkedIn posts a week, one CPD talk, one free risk-scan for a target client | 20 qualified conversations, 5 proposals |
| 61–90 | Deliver one paid engagement (start small: a $2,500 build or a $1,200/month retainer), then systematise it | Case study with a real number; repeatable process; fee data for pricing |

---

## 12.7 Ethics, independence and professional conduct

Follow the IESBA code as adopted locally, and at minimum these rules:

1. **Integrity:** report what the data shows, including the parts that are inconvenient for the client's
   management or for your own earlier conclusion.
2. **Objectivity:** do not accept an engagement where the outcome is pre-decided. Do not audit your own work.
3. **Confidentiality:** data is used only for the engagement, stored securely, and destroyed per policy.
4. **Competence:** take work you can do to standard; bring in specialists (IT forensics, legal, tax)
   where the scope requires it.
5. **Conflicts:** record and manage them, especially where you provide both internal audit and advisory
   to the same client.
6. **Evidence:** do not overstate. "We identified exceptions totalling $1.8m requiring follow-up" is a
   finding; "the company lost $1.8m to fraud" is a conclusion you may not be entitled to make.
7. **Privilege and legal process:** where a matter may become litigious, work under legal instruction
   where possible and preserve evidence properly from the first hour.

---

## 12.8 The tech stack that runs a modern small practice

| Layer | Maxhub choice | Why |
|---|---|---|
| Reporting | Power BI Desktop + Service (Fabric capacity when client sharing is needed) | Client comfort; Excel-adjacent |
| Data prep | Power Query + Python scripts (`scripts/`) | Reproducible and versionable |
| Exploration/ML | Python (pandas, scikit-learn, statsmodels) + notebooks | Free, portable, explainable |
| File management | OneDrive/SharePoint with per-client folders; engagement file structure per ISA-style index | Auditability |
| Documentation | Word/Excel templates in `business/`; working papers as PDFs + source files | Standardisation |
| Time & billing | Any time-tracking tool; capture hours per engagement (this is how you price next time) | Margin control |
| Version control | Git for scripts and templates; `.pbix` versioned by file name and change log | Traceability |
| Backup | 3-2-1: three copies, two media, one off-site | Client data protection |

---

## 12.9 Growing beyond yourself

| Phase | You | Team | Revenue shape |
|---|---|---|---|
| 1 | Doer | Just you + this course | Project fees |
| 2 | Specialist | +1 analyst, you sell and review | Projects + first retainer |
| 3 | Manager | +2–3, you QC and manage relationships | Retainers dominate; products repeat |
| 4 | Partner | Team delivers; you own relationships and standards | Productised services, training, larger investigations |

Two habits that make the transition possible: **write the methodology down** (so others can repeat it)
and **measure your own delivery** (hours per engagement vs fee — the Maxhub engagement log in
`data/raw/MaxhubEngagements.csv` shows exactly what that analysis looks like: planned vs actual hours,
fees, write-offs and satisfaction score. Analyse your own practice with the same tools you sell).

---

## 12.10 Course completion: your 30-day action list

1. **Day 1–2:** finish Capstone 1 (forensic investigation) and put it in your portfolio folder.
2. **Day 3–5:** finish Capstone 2 (financial reporting pack) using the Mhondoro data.
3. **Day 6–10:** run the free Procurement Risk Scan process on one friendly client's data (under a
   short confidentiality letter). Time it. That timing is your pricing basis.
4. **Day 11–15:** write your three productised offers with prices. Use the templates in `business/`.
5. **Day 16–20:** publish three case-study posts (anonymised) and one CPD talk proposal.
6. **Day 21–30:** send five proposals. Track them in the Maxhub pipeline table, and analyse your own
   conversion with the same funnel measures you built in Module 11.

The course ends here. The practice starts now.

---

## 12.11 Module 12 checklist

- [ ] Six service lines defined with deliverables and price ranges
- [ ] Three productised offers written with scope and exclusions
- [ ] Proposal and engagement letter templates customised with Maxhub details
- [ ] Data request list and QC checklist in use
- [ ] Build standard documented and applied to your capstone files
- [ ] Marketing cadence scheduled for the next 90 days
- [ ] Ethics and data-handling rules agreed and written into your standard engagement letter
- [ ] 30-day action list started

**Back to:** [Course home](../README.md) · [Capstones](../capstones/) ·
[Business templates](../business/)
