# Instructor guide

For self-study it doubles as a *how to study this* guide; for Maxhub it is the delivery plan for
running the course as a paid cohort. Total **~90–110 hours** of learner effort, of which about
60% is hands-on.

---

## 1. Teaching principles

1. **Data first, tool second.** Every session opens with a business question and a number, never with a
   ribbon tab. Learners who start with "click here" cannot answer "why is this wrong" later.
2. **Nothing is accepted until it ties.** Every deliverable is reconciled to a control total in view of
   the class. This single habit separates professional work from dashboard hobbyism.
3. **Break it deliberately.** Teach the broken version (a flat table, a `SUM` over a semi-additive
   balance, a chart with the wrong denominator) and let the class find the failure. The error becomes
   memorable and becomes a slot in
   [`../reference/Common_Errors_and_Fixes.md`](../reference/Common_Errors_and_Fixes.md).
4. **Write to the audience.** Every lab output is reviewed twice: does it tie, and would a CFO
   understand the title without explanation?
5. **The reveal comes last.** Do not show `data/raw/InjectionLog.csv` before Lab 09 finishes. The
   learning happens in the gap between what they found and what is there.

## 2. Delivery formats

| Format | Schedule | Best for |
|---|---|---|
| Full-time intensive | 10 working days, 09:00–16:00, labs in the afternoon | Career changers, staff between engagements |
| Part-time evening | 2 evenings/week × 12 weeks | Working accountants |
| Weekend | Saturdays × 16 weeks | Full-time employees, self-study |
| Blended bootcamp | 5 days in-person + 8 weeks mentored online | Audit/consulting teams |
| Self-study | Own pace, tracker-driven | The default reader of this repository |

**Suggested intensive schedule (10 days)**

| Day | Content | Lab output |
|---|---|---|
| 1 | Modules 1–2 | First report published; MessyData cleaned |
| 2 | Module 3 | Star schema modelled, orphan tests passing |
| 3 | Module 4 | 25 core measures matching the expected table |
| 4 | Module 5 | Time intelligence + closing-balance engine |
| 5 | Module 6 | P&L, BS, cash flow pages reconciling to the trial balance |
| 6 | Module 7 | Executive dashboard built to a written spec |
| 7 | Module 8 | Variance, DSO/DPO and exception pages |
| 8 | Module 9 | Forensic workbench, 12 tests, evidence register |
| 9 | Module 10 + Capstone 1 | Investigation report and board pack |
| 10 | Modules 11–12 + Capstone 4 | Churn model, proposal, pitch and QC review |

## 3. Session structure (any format)

| Minutes | Activity |
|---|---|
| 0–10 | **Recap with a number** — one figure from the last session, produced live from the model |
| 10–35 | **Concept** — one idea, one worked example, one failure case |
| 35–75 | **Lab** — learners at the keyboard; instructor circulates |
| 75–90 | **Review against expected results** — compare, investigate differences, agree the fix |
| 90–100 | **Professional framing** — how this appears in a client engagement, what it is worth, what it costs to get wrong |

## 4. Marking

| Element | Weight | Pass |
|---|---|---|
| Quizzes (12 × 5 questions) | 10% | 70%+ combined |
| Lab outputs (12) | 25% | Expected-results tables matched |
| Practical exam 1 (modelling & DAX) | 15% | 70 |
| Practical exam 2 (forensic) | 20% | 70 |
| Practical exam 3 (proposal) | 10% | 70 |
| Capstone (any two of four) | 20% | 70 each |

The pass mark is **70% overall with no single element below 50%**. A learner who cannot get the
control checks to return zero has not passed, regardless of how good the visuals are — that is the
professional standard, and it is worth failing someone over.

**Marking the forensic capstone:** the answer is not the list of journal IDs. It is whether the learner
(a) found all seven schemes, (b) quantified the *recoverable* amount conservatively, (c) distinguished
value at risk from quantified loss, and (d) wrote it without accusing anyone.

## 5. Common learner problems and the fix

| Problem | What is really happening | Fix |
|---|---|---|
| "My total revenue is negative" | Sign convention not understood | Return to Module 4 §4.3; make them derive the sign from a known journal |
| "The slicer does nothing" | Relationship path or direction | Trace the path out loud on the model diagram; never add bidirectional filters |
| "The closing balance is the same every month" | Total was computed once | Rebuild with the `MAX(DimDate[Date])` pattern, watching the filter context change |
| "My percentages are wrong when I add a month" | Non-additive measure summed | Show the average-of-percentages error and rebuild as division of sums |
| "Refresh fails at home" | File path moved | Parameterise the path; teach the client handover routine |
| "I found the duplicates" (missing five other schemes) | Stopped at the first win | Return to the test matrix; require every test to be run and documented, including the ones returning nothing |
| "The report already exists" (bored by Module 5) | Ready to move on | Hand them the client's question instead of the lab: "the CFO says DSO rose — prove it or disprove it" |
| Cannot explain a visual | Built it to complete a step, not to answer a question | Remove the visual and require the question first |

## 6. The quality-control drill (run it every cohort)

Have learners swap models. The reviewer must, without asking questions:

1. Re-perform one number from the raw CSV.
2. Tie every headline figure to the trial balance.
3. Find the description of every measure in the `_Measures` table (missing descriptions = fail).
4. Open the data-quality page and confirm the checks return zero.
5. Read every visual title and say what the reader learns.
6. Write one improvement and one risk.

This mirrors [`../business/PowerBI_Build_Standard.md`](../business/PowerBI_Build_Standard.md) §7 and is
what Maxhub does before any client deliverable is issued.

## 7. Turning the course into Maxhub revenue

| Course element | Commercial use |
|---|---|
| Lab 09 + Capstone 1 | A live demonstration for audit committees and law firms ("bring 12 months of payments and watch") |
| Capstone 2 | The deliverable in a CFO-reporting retainer pitch |
| Capstone 4 | The AI/ML service pitch; the churn model is directly reusable as a demo |
| Quizzes and practical exams | Entry assessment for hiring analysts; partner CPD sessions |
| This guide | The curriculum for a paid public cohort ($1,800–$6,000 per learner cohort) |

**Prices for a delivered cohort:** $1,800 per learner for a 10-day intensive (min 4 learners), or
$6,000 for an in-house team cohort up to 10, plus $250 per additional learner. Materials are already
built; delivery is the cost.

## 8. Instructor readiness checklist

- [ ] I can complete every lab from scratch without notes.
- [ ] I know the expected-value table for Labs 03–09 by heart (see Key Results in the course README).
- [ ] I can explain the sign convention, semi-additive balances and context transition three different ways.
- [ ] I have run a full independent QC review on my own model.
- [ ] I can price and defend an engagement using
      [`../business/Maxhub_Service_Catalogue.md`](../business/Maxhub_Service_Catalogue.md).
- [ ] I can state the professional-standards rules (evidence preservation, no accusations, independence)
      without reading them.
