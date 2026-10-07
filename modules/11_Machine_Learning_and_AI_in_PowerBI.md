# Module 11 — Machine Learning & AI in Power BI

**Time:** 12 hours · **Lab:** [Lab 11](../labs/Lab_Index.md#lab-11--churn-model-and-anomaly-detection) · **Prerequisite:** Modules 8–10

> Machine learning is not a different profession. It is the same analysis you have been doing —
> expectation, exception, follow-up — with the expectation learned from the data instead of set by a
> rule. For an accounting firm, that opens four new service lines.

---

## 11.1 The four AI/ML services an accounting firm can actually sell

| # | Service | Client problem | Technique | Deliverable |
|---|---|---|---|---|
| 1 | **Predictive analytics** | "Which clients/customers will churn, default or claim?" | Classification (logistic regression, decision tree, gradient boosting) | Scored list with drivers + a Power BI page |
| 2 | **Anomaly & fraud detection** | "What don't we know is wrong?" | Benford (Module 9), clustering, isolation forest, anomaly detection API | Exception register with risk score |
| 3 | **Forecasting & planning** | "What will the next 12 months look like?" | Time-series forecasting, driver-based models | Forecast with confidence band + assumption table |
| 4 | **Document & text intelligence** | "Invoice processing takes 3 days; board minutes take a week to summarise" | OCR, key-phrase extraction, sentiment, summarisation | Automated extraction pipeline + exceptions to human review |

Maxhub service catalogue entries and prices for each are in
[`../business/Maxhub_Service_Catalogue.md`](../business/Maxhub_Service_Catalogue.md).

**Reality check that keeps you credible:** with 60–13,000 rows and one financial year, you cannot build
a production-grade churn model. What you *can* build is a **decision-support model with honest limits**.
Say so. Clients trust the consultant who says "this model has 70% accuracy on a small sample; we would
need three more years of data before you should rely on it commercially" more than one who promises
magic.

---

## 11.2 The workflow (this is the part most analysts skip)

```
1. Frame the decision         -> What action changes based on the prediction?
2. Define the label           -> The historical outcome you will predict
3. Assemble features          -> Only what you would know AT the time of prediction
4. Split: train / test        -> Never evaluate on the data you trained on
5. Baseline first             -> "Always predict the majority class" - beat it or stop
6. Train a simple model       -> Logistic regression / decision tree, readable
7. Evaluate                   -> Accuracy, precision, recall, AUC, confusion matrix
8. Explain                    -> Which features matter, and do they make business sense?
9. Score + deploy in Power BI -> A table that refreshes, feeding report pages
10. Monitor                   -> Track accuracy over time; retrain when it drifts
```

**The number one mistake: leakage.** Using information that would not have been available at the
moment of prediction destroys the model's credibility. Example: predicting whether an invoice will be
paid late using its eventual payment date. Or predicting client churn using "services purchased next
year".

---

## 11.3 Path A — No-code: Key Influencers and AutoML inside Power BI

### Key Influencers (built into every Power BI Desktop)

1. Insert ▸ **Key influencers**.
2. *Analyse*: pick what you want explained — a measure or a categorical column.
   Example on our data: `FactAPInvoices[ThreeWayMatch]` or a `PaidStatus` = "Outstanding" flag.
3. *Explain by*: add candidate drivers — `DimVendor[Category]`, `DimVendor[PaymentTerms]`,
   `FactAPInvoices[PONumber]` (blank/not blank), `Amount Band`, `ApprovedBy` (blank/not blank).
4. Read the output as sentences: *"When PONumber is blank, the likelihood of an exception increases 4.2×."*

This is not a state-of-the-art model; it is a **hypothesis generator** that a partner can read in 30
seconds. In an investigation that is exactly what you need.

### AutoML (Premium / Fabric)

With Fabric capacity, **AutoML** applies to a table in a dataflow/lakehouse and returns a scored column
with a validation report (top features, accuracy metrics). The pragmatic small-firm alternative that
requires no premium licence: score in Python (Path B) and load the scored table into Power BI.

---

## 11.4 Path B — Python (fully within the free tooling)

Python gives you the same result and something you can defend in a methodology note. Our dataset
`data/raw/maxhub_client_churn.csv` (150 client-years, label `Stayed`) is designed for this exercise.

```python
"""
scripts/ml_churn_model.py - logistic regression churn model (standard library only).

Run it:   python3 scripts/ml_churn_model.py
Output :  data/scored/maxhub_client_churn_scored.csv
"""
import csv, math, os, random

NUMERIC = ["AnnualFeeUSD", "ServicesPurchased", "NPS", "ComplaintsLogged",
           "AvgPaymentDays", "EngagementDelayDays", "PartnerHoursOnClient",
           "AuditFindingsRaised", "FeeChangePct"]

def standardise(rows, cols):
    stats = {}
    for c in cols:
        vals = [float(r[c]) for r in rows]
        mean = sum(vals) / len(vals)
        var = sum((v - mean) ** 2 for v in vals) / max(1, len(vals) - 1)
        stats[c] = (mean, var ** 0.5 or 1.0)
    return stats

def score_row(row, weights, stats, names):
    z = weights[0]
    for i, c in enumerate(names, start=1):
        mean, sd = stats[c]
        z += weights[i] * ((float(row[c]) - mean) / sd)
    return 1.0 / (1.0 + math.exp(-z))          # sigmoid -> probability of staying

def train(rows, names, epochs=4000, lr=0.08):
    stats = standardise(rows, names)
    w = [0.0] * (len(names) + 1)
    for _ in range(epochs):
        grads = [0.0] * len(w)
        for r in rows:
            p = score_row(r, w, stats, names)
            err = p - float(r["Stayed"])
            grads[0] += err
            for i, c in enumerate(names, start=1):
                mean, sd = stats[c]
                grads[i] += err * ((float(r[c]) - mean) / sd)
        for i in range(len(w)):
            w[i] -= lr * grads[i] / len(rows)
    return w, stats
```

The full script (split, evaluation, scoring and export) is
[`../scripts/ml_churn_model.py`](../scripts/ml_churn_model.py). Run it now:

```text
Train 105 rows | Test 45 rows | features 9
Baseline (always predict 'stayed'): 51.1%
Model accuracy 68.9% | precision 71.4% | recall 65.2% | specificity 72.7%
Confusion matrix (test): TP=15 TN=16 FP=6 FN=8

Feature weights (standardised; positive => client more likely to stay):
  AnnualFeeUSD            -0.761   higher values churns
  NPS                     +0.686   higher values retains
  ServicesPurchased       +0.665   higher values retains
  ComplaintsLogged        -0.625   higher values churns
  PartnerHoursOnClient    +0.408   higher values retains
  ...
```

Read that output the way a client would: **the model beats the naive baseline by ~18 percentage
points**, and the drivers are commercially sensible — satisfaction (NPS), cross-selling (services
purchased) and relationship depth (partner hours) retain clients; complaints, slow payment and
concentration in a single service line precede churn.`

Why logistic regression and not a neural network on a 150-row teaching set: it is **explainable**
(weights map to business drivers), it does not overfit a small sample as badly, and you can explain it
to a client's audit committee. On a real 50,000-row invoice dataset, gradient boosting usually wins on
accuracy and you explain it with SHAP values — same workflow, different estimator.

**The four numbers to put in every model report:**

| Metric | What it means for the client | When it matters |
|---|---|---|
| **Accuracy** | How often the model is right overall | Misleading when classes are unbalanced — always quote the baseline next to it |
| **Precision** | Of those flagged, how many are real | When the follow-up cost per flag is high (fraud investigations) |
| **Recall** | Of the real cases, how many were caught | When missing one is expensive (compliance, credit risk) |
| **AUC / lift** | Ranking quality; how much better than random | When you use scores to prioritise a team's time |

For forensic work, **recall and lift** are the meaningful ones: you are prioritising a finite number of
investigator hours, not making an automated decision.

---

## 11.5 A second, accountant-friendly model: predicting late payment

Same workflow, more familiar label, and immediately useful in a credit-control engagement.

```python
# Build features from FactARAgeing + DimCustomer history:
#   payment_terms, credit_limit_used_pct, prior_late_payments_12m, dispute_flag,
#   invoice_value_band, segment, days_since_first_purchase
# Label: days_overdue > 30  (or AgeingBucket in {31-60, 61-90, 91-180, Over 180})
# Output: expected days to pay per open invoice -> "cash at risk" page in Power BI
```

This is a Maxhub **credit-risk analytics** service: score the debtor book, rank collections calls, and
quantify the expected cash impact. Clients understand it immediately and it is easy to price.

---

## 11.6 Anomaly detection without any modelling

Three built-in options, no code:

1. **Line chart anomaly detection** (Analytics pane ▸ *Find anomalies*): highlights unexpected spikes and
   dips in a time series — excellent for expense lines, bank fees or cost-centre spend.
2. **Scatter with a Z-score line** (Module 8): flag anything outside ±3 standard deviations.
3. **Decomposition tree with "high value" analysis**: finds the combination of dimensions where the
   unexpected value concentrates.

And one API option: **Cognitive Services / Azure AI Anomaly Detector** callable from Power Query or a
dataflow, giving you an anomaly score per period per series. For an accounting firm the practical
positioning is: *rules (Benford, thresholds, duplicates) first, anomaly detection second, ML third.*
Rules give findings a client can act on today; the others add depth.

---

## 11.7 Forecasting properly

| Approach | Tool | Honest use |
|---|---|---|
| Linear forecast | Analytics pane ▸ Forecast (line chart) | Quick direction, shown with its confidence band |
| Seasonal decomposition | DAX moving averages + `Revenue Same Period LY` | Showing a trend net of seasonality |
| Driver model | Scenario table + assumption inputs (Module 6) | Budgets and forecasts you can defend line by line |
| ML forecast | Python `statsmodels`/`prophet` or Fabric AutoML | When you have 3+ years and multiple drivers |

```dax
-- Seasonal index per month: >1 means the month is usually above average
Seasonal Index =
VAR MonthAvg = [Total Revenue]
VAR AllMonthsAvg = CALCULATE ( [Total Revenue], REMOVEFILTERS ( DimDate[MonthName] ), VALUES ( DimDate[FiscalYear] ) )
RETURN DIVIDE ( MonthAvg, AllMonthsAvg )
```

Rule for deliverables: **every forecast must show its assumptions and a band.** A single confident line
into the future is not a forecast, it is a guess with formatting.

---

## 11.8 Generative AI and Copilot — how to use it without risking your reputation

Power BI contains Copilot (requires Fabric capacity / Copilot licence) which can: generate a first draft
report page, write DAX from a description, summarise a page, and answer questions in natural language.
Adjacent tools you will actually use in practice:

| Use case | Tool | Discipline required |
|---|---|---|
| Draft a report page | Copilot in Power BI | Review every visual and every number; AI does not reconcile |
| Write DAX | Copilot / any LLM | Read it, then reconcile the output to a control total |
| Summarise a dataset | Smart narrative / Copilot | Human review before it reaches a client or a board |
| Draft the findings narrative | Any LLM, on **de-identified** text | Never paste client-identifiable data into a public model |
| Extract invoice fields | Power Automate + AI Builder / OCR | Always reconcile extracted totals to the document and the ledger |
| Classify transactions into codes | LLM few-shot, then human review of exceptions | Keep the mapping auditable; never silent |

**Governance rules Maxhub applies (write these into every engagement):**

1. **Client data never leaves the client's control** without written permission. Know which cloud the
   model processes on and where the data is stored.
2. **Data protection:** Zimbabwe's Cyber and Data Protection Act (2021) and, for cross-border clients,
   GDPR/POPIA impose duties on processing personal data. Personal data (names, salaries, bank accounts)
   needs a lawful basis, minimisation and security.
3. **Hallucination control:** every AI-generated number is verified against the model before it is sent.
4. **Disclosure:** state in the report which parts were AI-assisted and what human review was applied.
5. **Independence and objectivity:** an AI recommendation is a hypothesis; professional judgement stays
   with the engagement partner.

---

## 11.9 Deploying ML results into Power BI (the architecture that works for a small firm)

```
Client system  ->  monthly extract (CSV/DB)  ->  Power Query cleans
                                                        |
                          Python/notebook scores (churn, default, anomaly)
                                                        |
                                     scored table (CSV / Fabric table)
                                                        |
                   Power BI model (score table + dimensions, refreshed monthly)
                                                        |
             Pages: "At-risk clients", "Collections priority", "Anomaly queue"
```

Practical notes:

- Store the **model version, training date and metrics** in a small `ModelMetadata` table and show it on
  the report ("Model v1.2, trained 2025-10-01, AUC 0.78"). Clients and auditors love this; it is also
  your evidence of monitoring.
- **Drift monitoring:** add a page that tracks the churn rate and the model's flag rate month by month.
  If either moves sharply, the model needs retraining.
- Keep production simple: a scheduled script + a refreshed table beats a fragile real-time pipeline
  for a firm of Maxhub's size.

---

## 11.10 Module 11 checklist

- [ ] Key Influencers built against a real exception measure, and the sentence it produced written down
- [ ] Logistic-regression churn model trained, evaluated against the baseline, and explained
- [ ] Feature weights interpreted in business language
- [ ] Scored file loaded into Power BI and an "at-risk clients" page built
- [ ] Forecast built with assumptions and a confidence band
- [ ] Anomaly detection run on at least two time series
- [ ] Model metadata table built (version, date, metrics)
- [ ] AI governance rules included in the engagement's methodology note
- [ ] Limitations of the model stated in writing (sample size, accuracy, intended use)

**Next:** [Module 12 — The Advisory Practice](12_Advisory_Practice_and_Consulting.md): turning all of
this into Maxhub revenue.
