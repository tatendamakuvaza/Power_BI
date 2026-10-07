# Capstone 4 — AI & Advisory Service

**Client:** Maxhub Pvt Ltd's own client base (the firm's data is in `data/raw/Maxhub*.csv`)
**Engagement:** predictive churn model, forecasting, AI-assisted reporting and the service blueprint
**Sellable as:** machine learning / AI advisory retainer ($6,000–$30,000 per model; $800–$2,000/month monitoring)
**Effort:** 8–12 hours · **Pass mark:** 70/100

---

## 1. The brief

> *"Maxhub has grown from three consultants to ten and we have 15 recurring clients. Two of them did not
> renew last year and it was a surprise both times. I need to know which clients are at risk before they
> leave — and I want a service we can sell that does exactly this for our own clients."*

— Maxhub Managing Partner

## 2. What you must deliver

| # | Deliverable | Format |
|---|---|---|
| 1 | Client churn risk model — scored client list with risk bands and drivers | Python (scored CSV) + Power BI page |
| 2 | Revenue forecast for the next 12 months with assumptions stated | Power BI page with confidence language |
| 3 | AI-assisted commentary — a monthly narrative draft produced with AI and reviewed by a human | Documented process + example |
| 4 | Anomaly detection page — unusual engagement economics (write-offs, over-runs, negative realisation) | Power BI page |
| 5 | Model governance pack — features, metrics, limitations, bias, retraining schedule | 2-page document |
| 6 | Service blueprint — how Maxhub sells and delivers this to clients, priced | Proposal + pricing page |

## 3. The starting point (already in the repository)

`data/raw/maxhub_client_churn.csv` — 150 rows: 30 clients × 5 financial years (2021–2025).
The outcome column is `Stayed` (yes/no). A client's features include fee level, services purchased,
NPS, complaints, partner hours, payment days, sector and tenure.

`scripts/ml_churn_model.py` contains a from-scratch logistic regression (standard library only, so you
can read every line of the maths). Running it today gives:

| Metric | Value | Meaning |
|---|---|---|
| Observations | 150 (train 105 / test 45) | 30 clients × 5 years |
| Baseline (always "stays") | 51.1% | **The number to beat** |
| Model accuracy | 68.9% | 17.8 points better than the baseline |
| Precision | 71.4% | Of those flagged at risk, 71% actually left |
| Recall | 65.2% | Of those who left, 65% were flagged |
| Specificity | 72.7% | Of those who stayed, 73% were left alone |
| Confusion matrix | TP 15 · TN 16 · FP 6 · FN 8 | On the 45-client test set |

**Strongest drivers (standardised weights):** annual fee **−0.761** (more fee… lower churn risk in this
model, because long-standing large clients churn least), NPS **+0.686**, services purchased **+0.665**,
complaints logged **−0.625**, partner hours on client **+0.408**.

> *Read the signs carefully:* a negative weight means the feature pushes towards **not** staying
> (churning); a positive weight pushes towards **staying**. Write one plain-English sentence for each —
> that sentence is the deliverable the managing partner actually wants.

## 4. Build steps

### Step 1 — Understand the model before trusting it
1. Run `python3 scripts/ml_churn_model.py`. Confirm you reproduce the metrics above.
2. Read the weight table. For each feature, write the client-facing sentence (*"clients who log more
   complaints are X% more likely to leave"*).
3. Compute the **lift**: take the top 20% of clients by churn probability and state how many of them
   actually left (top-decile/top-quintile analysis).

### Step 2 — Improve the model honestly
Try, and document, each of these:

| Change | What it tests |
|---|---|
| Log-transform `AnnualFeeUSD` | Does scale distortion hurt the fit? |
| Add a "fee change vs prior year" feature | Growth is rarely linear — churn often follows a fee reduction |
| Add "services purchased trend" | A client buying fewer service lines is a leading indicator |
| Combine `ComplaintsLogged` > 2 into a flag | Does the count matter or just the presence? |
| Swap years: train on 2021–2023, test on 2024–2025 | **Time-based validation** — the test that matters in practice |

Record before/after accuracy, precision and recall in a table. **A change that does not improve
out-of-sample accuracy is not an improvement**, even if the training accuracy rises.

### Step 3 — Deploy to Power BI
1. Load the scored CSV (`data/scored/maxhub_client_churn_scored.csv`) into the model built for the firm.
2. Pages:
   - **Risk board** — clients by risk band, fee at risk (probability × annual fee), sorted descending.
   - **Driver explainer** — why the model flags this client, in words, per row.
   - **Trend** — risk by year for each client (a rising line is a conversation waiting to happen).
   - **Model card** — version, training date, accuracy, baseline, features, limitations.
3. Add a **fee-at-risk** measure: `SUMX ( Clients, ChurnProbability × AnnualFeeUSD )` — this converts a
   score into money, which is what makes partners act.

### Step 4 — Forecasting
1. Use the revenue history to build a 12-month forecast.
2. Try three methods and compare them honestly: **moving average**, **`FORECAST.LINEAR`** in DAX, and a
   **manual driver-based forecast** (retainer revenue + pipeline conversion).
3. State assumptions on the page, and show a range (low/base/high) rather than a single confident line.
4. Add a "forecast vs actual" page that fills in over time and displays its own error (MAPE).

### Step 5 — Anomaly detection
Test engagement economics: realisation rate below threshold, write-offs, engagements that over-ran budget
by more than 25%, clients with negative margin, unusual consultant mix. Use `Key Influencers` or
`Anomaly detection` in Power BI, plus a DAX outlier measure. Every anomaly needs a one-line explanation
field for the partner to complete.

### Step 6 — AI-assisted reporting (with human review)
Design a monthly routine: metrics extracted into a table → an AI drafting step writes the narrative →
a human reviews, corrects and signs off → the pack is issued. Document:

- the prompt or template used, and what data is sent;
- the **review checklist** (numbers verified, tone, no client-identifying data in a public model);
- the audit trail (who drafted, who reviewed, when);
- the failure modes: confidently wrong numbers, hallucinated comparisons, missing a material item.

**Never issue an AI-written number that a human has not validated against the model.**

## 5. Model governance pack (2 pages, maximum)

| Section | Content |
|---|---|
| Purpose and users | Retention decisions by partners; not an automated decision-maker |
| Data | Source, period, 150 observations, how the label was defined |
| Method | Logistic regression; features listed with rationale; training/test split and validation type |
| Performance | Baseline vs model; accuracy, precision, recall, specificity; confusion matrix; lift |
| Limitations | Small sample; 2021–2025 only; correlation not causation; no client interviews |
| Fairness/bias | Are any sectors or fee bands systematically over-flagged? Test and state it |
| Use rules | Ambiguous client situations |
| Monitoring | Review quarterly; retrain annually or when accuracy falls more than 5 points; drift check on fee/NPS distributions |
| Version | ModelID, training date, script version, owner |

## 6. Rubric (100 points)

| Criterion | Points | Full marks require |
|---|---|---|
| Baseline discipline | 10 | Baseline stated, model compared against it, improvement quantified |
| Model quality | 15 | Reasonable accuracy, honest reporting of precision/recall, time-based validation attempted |
| Driver explanation | 15 | Each feature translated into client language; sign of each weight interpreted correctly |
| Power BI deployment | 20 | Risk board sorted by fee-at-risk; drillthrough to the client-year row; model card page present |
| Forecasting | 10 | Three methods compared; assumptions and a range shown; error measure displayed |
| Anomaly detection | 10 | Engagement-economics anomalies surfaced with an explanation field |
| AI-assisted reporting | 10 | Documented prompt, review checklist, and a worked before/after example; no unverified numbers |
| Governance pack | 5 | All nine sections; limitations and monitoring are specific, not generic |
| Service blueprint | 5 | Priced offer, delivery process, and what the client must provide |

## 7. The commercial wrap

**Offer to clients, priced from the Service Catalogue:**

| Item | Price |
|---|---|
| Discovery and data review | $1,500 (fixed) |
| Model build (one use case: churn, default, forecast or anomaly) | $6,000 – $12,000 |
| Power BI deployment of the scored output | $3,000 – $6,000 |
| Governance pack and staff briefing | $1,500 |
| **Monitoring and retraining retainer** | **$800 – $2,000 per month** |

**Answer the client's three questions in one paragraph each:** how long (3–5 weeks), how much
(range above, fixed fee once the use case is agreed), how do I know it is right (baseline comparison,
out-of-sample testing, model card, human review of every AI-generated number).

**The pitch principle:** sell the *decision*, not the algorithm. "We will tell you which three clients
to call this quarter, and show you the $X of fees that protects" beats "we build a logistic regression".

## 8. Deliverable checklist

- [ ] Metrics reproduced: 68.9% accuracy vs 51.1% baseline, precision 71.4%, recall 65.2%
- [ ] Lift analysis on the top decile/quintile by churn probability
- [ ] At least two improvement experiments documented with out-of-sample results
- [ ] Four Power BI pages including a model card, with fee-at-risk measure
- [ ] Twelve-month forecast with three methods compared, range and error measure
- [ ] Anomaly page with an explanation field per item
- [ ] AI-assisted reporting routine with prompt, review checklist and audit trail
- [ ] Governance pack (2 pages) with limitations, bias check and retraining triggers
- [ ] Service blueprint priced with the three client answers written out
