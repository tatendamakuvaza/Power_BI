# Capstone 2 — Financial Reporting Pack

**Client:** Mhondoro Manufacturing (Pvt) Ltd
**Engagement:** Management reporting and month-end close pack
**Deliverable:** a live Power BI reporting pack that replaces a manually-built monthly Excel pack
**Estimated effort:** 8 hours · **Portfolio value:** this is the retainer product ("CFO Advisory" service line)

---

## 1. The brief

> *"Our finance team spends eight days each month rebuilding the management pack in Excel. Every
> version has a different DSO. The board wants the pack five working days after month end, with
> commentary that explains the variances, and we want to be able to drill into any number down to the
> ledger line. We have a Power BI licence and we want the model to refresh from our ERP extract."*

---

## 2. What you deliver

| # | Deliverable | Notes |
|---|---|---|
| 1 | `.pbix` reporting pack | Five pages: Executive, P&L, Balance Sheet, Cash Flow, Close Pack (hidden data-quality page included) |
| 2 | Model documentation | Star schema diagram, measure list with definitions, data lineage, refresh instructions |
| 3 | Methodology note | Sign conventions, current-year-result treatment, ratio definitions (DSO/DPO/DIO), limitations |
| 4 | User guide | One page: how to use the slicers, how to drill through, who to call |
| 5 | Handover pack | `.pbix` + data dictionary + 30-minute recorded walkthrough |

---

## 3. Requirements the pack must satisfy

**Functional**

1. The pack refreshes from a single Excel/CSV extract dropped into a folder (no manual editing).
2. A period slicer controls every page; comparatives (prior month, prior year, same period last year) work.
3. Actual vs budget by account, cost centre and month.
4. Drillthrough from every statement line to the underlying journal lines.
5. A close-pack page proving: debits = credits; BS check = 0; P&L ties to the movement in retained earnings.

**Non-functional**

6. Any visual responds in under 2 seconds on the current dataset.
7. Numbers formatted consistently: `$#,##0;($#,##0);"-"`, percentages to 0.0%.
8. Every measure has a description; every table and column a sensible name.
9. The client can refresh it themselves after a recorded handover.
10. Printed to PDF, it still looks like a management pack.

---

## 4. The numbers your pack must reproduce

| Line | FY2024 | FY2025 (9M) |
|---|---|---|
| Revenue | 13,786,573 | 10,543,059 |
| Profit after tax | 447,052 | -61,867 (loss to date) |
| Closing cash (30 Sep 2025) | — | 792,548 |
| Receivables | — | 3,790,174 |
| Payables | — | 2,373,621 |
| Inventory (net) | — | 871,343 |
| Suspense balance | — | 51,059 |
| BS Check | — | **0.00** |
| Current year result (loss to date) | — | -61,867 |
| Debits = Credits (whole ledger) | 122,878,886.54 | 122,878,886.54 |

Ratios to publish with definitions:

| Ratio | Formula used | Sep 2025 value |
|---|---|---|
| DSO | Closing AR ÷ Revenue × days elapsed (273) | 98 days |
| DPO | Closing AP ÷ Cost of sales × days elapsed | 124 days |
| DIO | Closing inventory ÷ Cost of sales × days elapsed | 46 days |
| Cash conversion cycle | DSO + DIO − DPO | 20 days |
| Gross margin | Gross profit ÷ revenue | 50.5% (FY2025 to date) |
| Current ratio | Current assets ÷ current liabilities | 1.35 (CA 5,606,400 ÷ CL 4,147,758) |

---

## 5. Page specifications

### Page 1 — Executive summary (one page, board-ready)
KPI strip (revenue + YoY, gross margin, operating profit, cash, DSO, overdue >90 days %); revenue vs
prior year trend with a 3-month projection; top five adverse variances; cash trend; a "prepared by /
data as at / source" footer.

### Page 2 — Profit or loss
Statement matrix (rows in FS order, months as columns) with budget, variance $ and variance %;
conditional formatting (adverse red, favourable green); a waterfall bridge; auto commentary card.

### Page 3 — Balance sheet
Opening / movement / closing columns; subtotals; the check card; trend of working-capital components.

### Page 4 — Cash flow
Sources-and-uses waterfall reconciling to the movement in cash accounts; a statement of the indirect
reconciliation (PAT → depreciation → working capital → investing/financing → net movement).

### Page 5 — Close pack
Nine control cards with expected values and a "Ties / Investigate" status; the list of unreconciled
bank items and 3-way-match exceptions with counts and values.

### Hidden page — Data quality
Orphan keys, unbalanced journals, rows with missing documents, period coverage table.

---

## 6. Process (do it in this order)

1. **Scope and agree the definitions** (30 min). Write the ratio definitions down *before* building;
   half of all pack disputes are definition disputes.
2. **Build the data layer** (2 h) — Power Query with parameters; no manual steps.
3. **Model** (1 h) — star schema, date table marked, role-playing user dimension.
4. **Measures** (2 h) — the core and time libraries, renamed to the client's language.
5. **Pages** (2 h) — build to the specification above, then stop and look at it as a CFO would.
6. **Quality control** (30 min) — an independent review against the checklist in
   [`../business/PowerBI_Build_Standard.md`](../business/PowerBI_Build_Standard.md).
7. **Handover** (1 h) — record a walkthrough, write the one-page guide, agree the refresh routine.

---

## 7. Marking rubric (100 points)

| Area | Points | Full marks |
|---|---|---|
| Reconciliation | 25 | Every statement ties to the trial balance; check page proves it |
| Model design | 15 | Clean star schema, text keys, documented, performant |
| DAX quality | 15 | Measures organised, named, described; VAR used; no hard-coded periods |
| Report design | 15 | Sentence titles, right visuals, consistent formatting, theme applied |
| Definitions | 10 | Ratio and sign conventions published in the methodology note |
| Data layer | 10 | Parameterised, refreshable, no manual intervention, staging queries not loaded |
| Handover | 10 | User guide, walkthrough, refresh instructions, client can self-serve |

**Pass: 70.**

---

## 8. Commercial wrap (how Maxhub sells it)

| Component | Price basis |
|---|---|
| Build (data layer + model + 5 pages + documentation) | 5–12 days at the rates in Module 12 |
| Monthly retainer (refresh monitoring, exception report, 60-minute review call) | from $650/month |
| Change requests after sign-off | time and materials, or a change-order list in the engagement letter |
| Training for the client's finance team | half-day or full-day rate |
| Annual model review (structure, definitions, performance) | 1–2 days |

Write the proposal for this capstone using
[`../business/Client_Proposal_Template.md`](../business/Client_Proposal_Template.md), with the fee
built from the hours you actually spent. That gap between your estimate and the actual is your first
real pricing lesson.
