# Module 8 — Analytics, KPIs & Discovery

**Time:** 8 hours · **Lab:** [Lab 08](../labs/Lab_Index.md#lab-08--variance--exception-pages) · **Prerequisite:** Module 7

> Reporting shows what happened. Analytics explains why, and points at what to do next. This module
> turns your report into advice — which is what Maxhub sells.

---

## 8.1 The four questions ladder

| Level | Question | Techniques in this module |
|---|---|---|
| **Descriptive** | What happened? | Trend, mix, Pareto, ratio analysis |
| **Diagnostic** | Why did it happen? | Variance decomposition, Decomposition tree, Key Influencers, correlation |
| **Predictive** | What will happen? | Forecasting, regression, ML (Module 11) |
| **Prescriptive** | What should we do? | Scenario analysis, thresholds, alerts, recommendations |

Clients pay for levels 2–4. Most accountants stop at level 1.

---

## 8.2 Variance analysis that a CFO will read

A single "variance %" column is not analysis. Decompose it:

```dax
-- PRICE / VOLUME / MIX decomposition for revenue
Revenue Actual   = [Total Revenue]
Revenue Budget   = [Budget by FSLine]
Revenue Variance = [Revenue Actual] - [Revenue Budget]

-- Volume effect: (actual units - budget units) x budget price
Volume Effect =
VAR ActQty = SUM ( FactSalesOrders[Quantity] )
VAR BugQty = [Budget Units]                    -- add budget units to FactBudget for this to work
VAR BugPrice = DIVIDE ( [Revenue Budget], BugQty )
RETURN ( ActQty - BugQty ) * BugPrice

-- Price effect: (actual price - budget price) x actual units
Price Effect =
VAR ActQty = SUM ( FactSalesOrders[Quantity] )
VAR ActPrice = DIVIDE ( [Revenue Actual], ActQty )
VAR BugPrice = DIVIDE ( [Revenue Budget], [Budget Units] )
RETURN ActQty * ( ActPrice - BugPrice )

-- Mix effect is the residual: total variance - volume - price
Mix Effect = [Revenue Variance] - [Volume Effect] - [Price Effect]
```

Present as a **waterfall**: Budget → Volume → Price → Mix → Actual. If the residual is large, your mix
story needs a further split (by customer segment or product family).

For costs, do the same with **rate × quantity**: `(actual rate − standard rate) × actual quantity` is
the rate variance; the rest is the usage/efficiency variance.

---

## 8.3 The KPI set every client needs (and how to define them properly)

| KPI | Formula | Watch out for |
|---|---|---|
| Gross margin % | `Gross Profit / Revenue` | Never average monthly percentages — always total ÷ total |
| EBITDA margin % | `EBITDA / Revenue` | State whether depreciation is included |
| DSO | `Closing AR / Revenue × 365` | Use 365 for the period; for partial years use days elapsed, not 365 |
| DPO | `Closing AP / Cost of sales × 365` | Purchases is better than cost of sales if available |
| DIO | `Closing inventory / Cost of sales × 365` | |
| Cash conversion cycle | `DSO + DIO − DPO` | Negative is good; watch for window-dressing at year end |
| Current ratio | `Current assets / Current liabilities` | Includes inventory; use quick ratio too |
| Debtor ageing > 90 days % | Bucket 91+ / total AR | The number the bank cares about |
| Revenue per employee | `Revenue / headcount` | Headcount is a semi-additive measure |
| Recovery rate (prof services) | `Realised rate / standard rate` | Our Maxhub data (Module 11) |
| Overhead absorption | `Absorbed / Actual overhead` | Manufacturing clients, see Module 5 |
| Expense claims without receipts % | Claims flagged / total claims | A control KPI, not a finance KPI |

```dax
DSO = DIVIDE ( [Receivables Balance], [Total Revenue] ) * 365
DPO = DIVIDE ( [Payables Balance], [Cost of Sales] ) * 365
DIO = DIVIDE ( [Inventory Balance], [Cost of Sales] ) * 365
Cash Conversion Cycle = [DSO] + [DIO] - [DPO]
```

Be honest about definitions in the footnotes: two analysts can both compute "DSO" and get different
numbers because of averages vs closing balances. **Publish your definition**; that alone marks you as
a professional.

---

## 8.4 Pareto and concentration analysis (fraud's favourite hiding place)

```dax
-- Cumulative % of spend, so you can show the 80/20 line
Vendor Spend Rank = RANKX ( ALLSELECTED ( DimVendor[VendorName] ), [GL Amount Abs], , DESC, DENSE )

Cumulative Vendor Spend % =
VAR CurrentRank = [Vendor Spend Rank]
VAR TotalSpend  = CALCULATE ( [GL Amount Abs], ALLSELECTED ( DimVendor[VendorName] ) )
VAR SpendToHere = CALCULATE ( [GL Amount Abs],
        FILTER ( ALLSELECTED ( DimVendor[VendorName] ), [Vendor Spend Rank] <= CurrentRank ) )
RETURN DIVIDE ( SpendToHere, TotalSpend )
```

Then a combo chart (bars = spend, line = cumulative %) with a reference line at 80%. Typical finding on the Mhondoro data: "the top five of 26 vendors account for only 24.6% of
$30.5m of spend — 19 vendors are needed to reach 80%, which tells you control is spread thin and
no single relationship is being managed." On a real client the pattern is usually the opposite:
a handful of vendors taking most of the spend, often the ones onboarded most recently. Either
finding is a deliverable.

---

## 8.5 Statistical thinking for auditors (the minimum viable toolkit)

| Concept | Formula in DAX | Use |
|---|---|---|
| Mean of a set of values | `AVERAGEX ( VALUES ( t[key] ), [Measure] )` | Benchmarks, expected values |
| Standard deviation | `STDEVX.S ( VALUES ( t[key] ), [Measure] )` | Spread of invoice values |
| **Z-score** | `DIVIDE ( [Measure] - [Mean], [StDev] )` | Flag anything beyond ±3 SD — classic outlier test |
| Median | `MEDIANX ( VALUES ( t[key] ), [Measure] )` | Robust to outliers where the mean is not |
| Percentile | `PERCENTILEX.INC ( VALUES ( t[key] ), [Measure], 0.95 )` | Set materiality-style thresholds from data |
| Coefficient of variation | `DIVIDE ( [StDev], [Mean] )` | Compare variability across portfolios |

```dax
-- Outlier test that works in a table visual of users, vendors or accounts
Mean Amount per Group = AVERAGEX ( VALUES ( DimAccount[AccountCode] ), [GL Amount Abs] )
StDev Amount per Group = STDEVX.S ( VALUES ( DimAccount[AccountCode] ), [GL Amount Abs] )
Z Score = DIVIDE ( [GL Amount Abs] - [Mean Amount per Group], [StDev Amount per Group] )
Outlier Flag = IF ( ABS ( [Z Score] ) > 3, "Outlier", "" )
```

**Discipline:** a statistical outlier is a *question*, not a finding. Always corroborate with a document,
a bank statement or an interview before it goes in a report.

---

## 8.6 Trend, seasonality and forecasting (preview of Module 11)

- **Seasonality:** compare each month to the same month last year (`[Revenue Same Period LY]`), or index
  each month against the 12-month average.
- **Forecasting:** the built-in *Analytics ▸ Forecast* on a line chart gives a linear forecast with a
  confidence band in seconds, using `FORECAST.LINEAR` semantics. Always label it "projection, not
  budget" and state the assumption (that the trend continues).
- **Better forecasts** come from understanding drivers, not from extending a line: if revenue = volume ×
  price, forecast volume and price separately and show the assumption table.

```dax
Revenue Forecast = CALCULATE ( FORECAST.LINEAR ( MAX ( DimDate[Date] ), /* known Y */ [Total Revenue], /* known X */ MAX ( DimDate[Date] ) ) )
```

---

## 8.7 Discovery tools: finding the story you did not know was there

| Tool | How to use it | Example finding from our data |
|---|---|---|
| **Decomposition tree** | Insert ▸ Decomposition tree; Explain by: Absolute value, use `[GL Amount Abs]`; Analyse: Accounting type → Cost centre → Account → Vendor | "Marginal decline in profit is driven by Harare Plant materials cost, concentrated in one vendor" |
| **Key influencers** | Insert ▸ Key influencers; Explore: which vendors influence `[Exception Rate]` | "Payments without an approver are most influenced by UserID = USR-012" |
| **Q&A** | Insert ▸ Q&A, type "revenue by month for 2025" | Client self-service; add synonyms (`DimAccount[AccountName]` ← "category") in Model view ▸ Q&A setup |
| **Smart narrative** | Insert ▸ Smart narrative, customise the default text | Auto commentary for the management pack |
| **Top-N filter + ranking measures** | Filter pane ▸ Top N | "Show me the 15 biggest exceptions this quarter" |
| **Anomaly detection on a line chart** | Analytics pane ▸ Find anomalies (preview) | Automatic spikes/dips in expense lines |

---

## 8.8 Turning analytics into advice (what Maxhub invoices for)

Every analytical page should end with a **recommendation block** — three lines:

```
FINDING:  DSO is 98 days on nine months of revenue ($3.79m of debtors); the ledger also shows
         $51,059 sitting in suspense and a current-year loss of $61,867 against a $447,052 profit
         last year.
IMPACT:  Every 10 days of DSO is roughly $386k of cash tied up; at a 14% funding cost that is
         about $54k a year. Collecting to 60 days would release over $1.4m.
ACTION:  (1) Credit-limit review for the top 5 exposures; (2) automated 30/60/90 dunning;
         (3) suspend sales orders for accounts 90+ days until a payment plan is signed.
```

The **IMPACT** line is the one that converts analysis into a fee. Quantify everything: days, dollars,
percentages, hours. "Improve efficiency" is not a finding.

---

## 8.9 Module 8 checklist

- [ ] Price / volume / mix bridge built (waterfall)
- [ ] Full KPI set built with published definitions
- [ ] Pareto of vendor spend with cumulative %
- [ ] Z-score outlier test on at least one dimension
- [ ] Decomposition tree configured and used on a real question
- [ ] Key influencers run against an exception measure
- [ ] Recommendation block (Finding / Impact / Action) written for every page

**Next:** [Module 9 — Forensic Accounting Analytics](09_Forensic_Accounting_Analytics.md), where the
techniques above become a fraud-detection workbench.

---

## Related material

- [../labs/Lab_Index.md#lab-08--variance--exception-pages](../labs/Lab_Index.md#lab-08--variance--exception-pages)
- [../capstones/Capstone_3_Data_Analytics_Engagement.md](../capstones/Capstone_3_Data_Analytics_Engagement.md)
- [../reference/Cheat_Sheet.md](../reference/Cheat_Sheet.md)

**Next:** [Module 9 — Forensic Accounting Analytics](09_Forensic_Accounting_Analytics.md)
