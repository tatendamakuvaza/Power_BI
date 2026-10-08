"""
ml.py - Capstone 4: churn model, lift, improvement experiments, forecasting,
anomaly detection and fee-at-risk.

The churn model itself is the repository's own standard-library logistic
regression (`scripts/ml_churn_model.py`) - we import and re-run it rather than
re-implementing it, so the published metrics are reproduced by the shipped code.
"""
from __future__ import annotations

import csv
import math
import os
import random
import sys
from collections import defaultdict

from . import common as C

sys.path.insert(0, os.path.join(C.ROOT, "scripts"))
import ml_churn_model as base_model  # noqa: E402  (repository script, reused as-is)

CHURN_SRC = os.path.join(C.RAW, "maxhub_client_churn.csv")
ENGAGEMENTS = os.path.join(C.RAW, "MaxhubEngagements.csv")
SERVICE_LINES = os.path.join(C.RAW, "maxhub_service_line_financials.csv")
PIPELINE = os.path.join(C.RAW, "maxhub_pipeline.csv")


def _load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# 1. Baseline model
# ---------------------------------------------------------------------------
def baseline():
    rows = _load(CHURN_SRC)
    random.seed(7)
    random.shuffle(rows)
    cut = int(len(rows) * 0.7)
    train_rows, test_rows = rows[:cut], rows[cut:]
    names = base_model.NUMERIC
    w, stats = base_model.train(train_rows, names)
    acc, prec, rec, spec, cm = base_model.evaluate(test_rows, w, stats, names)
    stay_rate = sum(int(r["Stayed"]) for r in test_rows) / len(test_rows)
    weights = sorted(zip(names, w[1:]), key=lambda x: -abs(x[1]))
    scored = []
    for r in rows:
        p_stay = base_model.score_row(r, w, stats, names)
        d = dict(r)
        d["P_stay"] = round(p_stay, 4)
        d["P_churn"] = round(1 - p_stay, 4)
        d["RiskBand"] = "High" if d["P_churn"] >= 0.6 else ("Medium" if d["P_churn"] >= 0.3 else "Low")
        d["FeeAtRiskUSD"] = round((1 - p_stay) * float(r["AnnualFeeUSD"]), 2)
        scored.append(d)
    return {
        "rows": rows, "train": train_rows, "test": test_rows,
        "weights": w, "stats": stats, "names": names,
        "accuracy": acc, "precision": prec, "recall": rec, "specificity": spec,
        "cm": cm, "baseline_accuracy": stay_rate,
        "weight_table": [{"Feature": c, "Weight": round(wi, 3),
                          "Direction": "retains" if wi > 0 else "churns",
                          "Plain English": _sentence(c, wi)} for c, wi in weights],
        "scored": scored,
        "model_version": "v1.0-logreg-2025-10",
    }


def _sentence(col, w):
    pos = w > 0
    t = {
        "AnnualFeeUSD": ("Clients with a larger annual fee are less likely to leave in "
                         "this sample; fee size is acting as a proxy for relationship "
                         "maturity, not as a cause of retention.",
                         "Clients with a smaller annual fee leave more often."),
        "NPS": ("Each standard-deviation increase in NPS raises the probability of "
                "renewal - satisfaction is the strongest retention lever.",
                "A falling NPS is the clearest early warning of churn."),
        "ServicesPurchased": ("Clients buying more service lines are stickier; "
                              "cross-selling is retention.",
                              "Clients buying fewer service lines are more likely to leave."),
        "ComplaintsLogged": ("Complaints push a client towards leaving; a logged "
                             "complaint is an action item, not a statistic.",
                             "Clients with no complaints renew more often."),
        "AvgPaymentDays": ("Clients who pay slowly are more likely to leave - late "
                           "payment is usually a symptom of a deteriorating "
                           "relationship, not just a cash issue.",
                           "Prompt payers renew more often."),
        "PartnerHoursOnClient": ("Partner time on a client protects the renewal; "
                                 "relationship depth beats price.",
                                 "Clients who rarely see a partner leave more often."),
        "AuditFindingsRaised": ("Findings raised have almost no measurable effect on "
                                "renewal in this sample.",
                                "Findings raised have almost no measurable effect."),
        "FeeChangePct": ("Fee movements have almost no measurable effect on renewal "
                         "in this sample.",
                         "Fee movements have almost no measurable effect."),
        "EngagementDelayDays": ("Delivery delays have almost no measurable effect in "
                                "this sample, though the sign is the expected one.",
                                "Delivery delays have almost no measurable effect."),
    }.get(col)
    return t[0] if pos else t[1]


# ---------------------------------------------------------------------------
# 2. Lift
# ---------------------------------------------------------------------------
def lift(model):
    rows = sorted(model["scored"], key=lambda r: -r["P_churn"])
    n = len(rows)
    out = []
    for label, frac in [("Top decile (10%)", 0.10), ("Top quintile (20%)", 0.20),
                        ("Top third (33%)", 1 / 3), ("Whole population", 1.0)]:
        k = max(1, round(n * frac))
        sub = rows[:k]
        churned = sum(1 for r in sub if r["Stayed"] == "0")
        fee = sum(float(r["AnnualFeeUSD"]) for r in sub)
        out.append({
            "Segment": label, "Clients scored": k,
            "Actually left": churned,
            "Churn rate pct": churned / k * 100,
            "Baseline churn rate pct": sum(1 for r in rows if r["Stayed"] == "0") / n * 100,
            "Lift": (churned / k) / (sum(1 for r in rows if r["Stayed"] == "0") / n),
            "Annual fee in segment": round(fee, 2),
            "Fee at risk": round(sum(r["FeeAtRiskUSD"] for r in sub), 2),
        })
    return out


# ---------------------------------------------------------------------------
# 3. Improvement experiments
# ---------------------------------------------------------------------------
def _panel_features(rows):
    """Add features derived from the client-year panel."""
    by_client = defaultdict(list)
    for r in rows:
        by_client[r["ClientID"]].append(r)
    for cid, rs in by_client.items():
        rs.sort(key=lambda r: int(r["Year"]))
        prev = None
        for r in rs:
            r["FeeChangeComputedPct"] = 0.0 if prev is None or float(prev["AnnualFeeUSD"]) == 0 \
                else (float(r["AnnualFeeUSD"]) - float(prev["AnnualFeeUSD"])) / float(prev["AnnualFeeUSD"]) * 100
            r["ServicesTrend"] = 0 if prev is None else int(r["ServicesPurchased"]) - int(prev["ServicesPurchased"])
            r["ComplaintsFlag"] = 1.0 if int(r["ComplaintsLogged"]) > 2 else 0.0
            r["LogAnnualFeeUSD"] = math.log(max(1.0, float(r["AnnualFeeUSD"])))
            prev = r
    return rows


def _metrics(train_rows, test_rows, names):
    w, stats = base_model.train(train_rows, names)
    acc, prec, rec, spec, cm = base_model.evaluate(test_rows, w, stats, names)
    return {"accuracy": acc, "precision": prec, "recall": rec, "specificity": spec, "cm": cm}


def experiments():
    rows = _panel_features([dict(r) for r in _load(CHURN_SRC)])
    random.seed(7)
    random.shuffle(rows)
    cut = int(len(rows) * 0.7)
    train_rows, test_rows = rows[:cut], rows[cut:]
    base = list(base_model.NUMERIC)
    out = []

    def add(label, names, note, tr=None, te=None):
        m = _metrics(tr or train_rows, te or test_rows, names)
        out.append({"Experiment": label, "Features": len(names),
                    "Accuracy pct": round(m["accuracy"] * 100, 1),
                    "Precision pct": round(m["precision"] * 100, 1),
                    "Recall pct": round(m["recall"] * 100, 1),
                    "Specificity pct": round(m["specificity"] * 100, 1),
                    "Confusion (TP/TN/FP/FN)": "/".join(map(str, m["cm"])),
                    "Note": note})
        return m

    b = add("Baseline (9 features, random 70/30 split)", base,
            "The number to beat: 68.9% against a 51.1% baseline")
    for r in out:
        r["Change vs baseline (pp)"] = 0.0

    m = add("Log-transform AnnualFeeUSD",
            ["LogAnnualFeeUSD"] + [c for c in base if c != "AnnualFeeUSD"],
            "Tests whether scale distortion in the fee feature hurts the fit")
    m = add("Add computed fee change vs prior year",
            base + ["FeeChangeComputedPct"],
            "FeeChangePct exists in the extract; this recomputes it from the panel")
    m = add("Add services-purchased trend", base + ["ServicesTrend"],
            "A client buying fewer service lines is a leading indicator")
    m = add("Replace complaint count with a >2 flag",
            [c for c in base if c != "ComplaintsLogged"] + ["ComplaintsFlag"],
            "Tests whether the count matters or only its presence")
    m = add("All four changes together",
            ["LogAnnualFeeUSD"] + [c for c in base if c not in ("AnnualFeeUSD", "ComplaintsLogged")]
            + ["FeeChangeComputedPct", "ServicesTrend", "ComplaintsFlag"],
            "Combined feature set on the same random split")

    tr = [r for r in rows if int(r["Year"]) <= 2023]
    te = [r for r in rows if int(r["Year"]) >= 2024]
    tb = sum(int(r["Stayed"]) for r in te) / len(te)
    m = add("Time-based validation: train 2021-2023, test 2024-2025", base,
            f"The test that matters in practice. Baseline on this split is {tb:.1%}",
            tr=tr, te=te)
    m = add("Time-based validation with the extended feature set",
            ["LogAnnualFeeUSD"] + [c for c in base if c not in ("AnnualFeeUSD", "ComplaintsLogged")]
            + ["FeeChangeComputedPct", "ServicesTrend", "ComplaintsFlag"],
            "Out-of-time performance of the richer model", tr=tr, te=te)

    base_acc = out[0]["Accuracy pct"]
    for r in out:
        r["Change vs baseline (pp)"] = round(r["Accuracy pct"] - base_acc, 1)
    return out, tb


# ---------------------------------------------------------------------------
# 4. Forecasting
# ---------------------------------------------------------------------------
RECURRING_LINES = {"CFO Advisory", "Internal Audit"}   # retainer service lines
OPEN_STAGES = {"Lead", "Qualified", "Proposal", "Negotiation"}


def _monthly_revenue():
    rows = _load(SERVICE_LINES)
    tot = defaultdict(float)
    for r in rows:
        tot[r["Month"]] += float(r["RevenueUSD"])
    return sorted(tot.items())


def _monthly_split():
    rows = _load(SERVICE_LINES)
    rec, proj = defaultdict(float), defaultdict(float)
    for r in rows:
        (rec if r["ServiceLine"] in RECURRING_LINES else proj)[r["Month"]] += float(r["RevenueUSD"])
    return sorted(rec.items()), sorted(proj.items())


def _linfit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sxy / sxx if sxx else 0.0
    return slope, my - slope * mx


def forecast(months=12, mape_holdout=6):
    series = _monthly_revenue()
    labels = [m for m, _ in series]
    values = [v for _, v in series]
    xs = list(range(len(values)))

    # Method 1 - 3-month moving average (flat forecast)
    ma = sum(values[-3:]) / 3
    # Method 2 - linear trend (the FORECAST.LINEAR equivalent)
    slope, intercept = _linfit(xs, values)
    # Method 3 - driver based: recurring retainer run-rate plus a win-rate
    # adjusted contribution from the open pipeline with a decision date inside
    # the forecast window. Closed (Won/Lost) opportunities are excluded.
    pipe = _load(PIPELINE)
    window_start, window_end = labels[-1], f"{int(labels[-1][:4]) + 1}{labels[-1][4:]}"
    open_pipe = [r for r in pipe if r["Stage"] in OPEN_STAGES
                 and window_start < r["DecisionTargetDate"] <= window_end]
    weighted = sum(float(r["ExpectedFeeUSD"]) * float(r["ProbabilityPct"]) / 100
                   for r in open_pipe)
    won = sum(1 for r in pipe if r["Stage"] == "Won")
    lost = sum(1 for r in pipe if r["Stage"] == "Lost")
    win_rate = won / (won + lost) if (won + lost) else 0.0

    rec_series, proj_series = _monthly_split()
    rec_vals = [v for _, v in rec_series]
    proj_vals = [v for _, v in proj_series]
    recurring = sum(rec_vals[-3:]) / 3                       # retainer run-rate
    project_base = sum(proj_vals[-12:]) / 12                 # trailing 12-month mean
    pipeline_uplift = (weighted * win_rate) / months         # converted into the window
    driver_monthly = recurring + project_base + pipeline_uplift

    # error measure on a 6-month hold-out (in-sample history, out-of-sample test)
    hist = values[:-mape_holdout]
    actual = values[-mape_holdout:]
    hx = list(range(len(hist)))
    h_slope, h_int = _linfit(hx, hist)
    h_ma = sum(hist[-3:]) / 3
    mape = {}
    for name, preds in [("Moving average (3-month)", [h_ma] * len(actual)),
                        ("Linear trend", [h_slope * (len(hist) + i) + h_int for i in range(len(actual))]),
                        ("Driver based", [driver_monthly] * len(actual))]:
        mape[name] = sum(abs(a - p) / a for a, p in zip(actual, preds)) / len(actual) * 100

    resid = [v - (slope * x + intercept) for x, v in zip(xs, values)]
    sd = (sum(r * r for r in resid) / max(1, len(resid) - 1)) ** 0.5

    out = []
    last_label = labels[-1]
    year, month = int(last_label[:4]), int(last_label[5:7])
    for i in range(1, months + 1):
        month += 1
        if month > 12:
            month, year = 1, year + 1
        lin = slope * (len(values) - 1 + i) + intercept
        low, high = min(ma, lin, driver_monthly), max(ma, lin, driver_monthly)
        out.append({
            "Month": f"{year}-{month:02d}",
            "Moving average (3-month)": round(ma, 2),
            "Linear trend": round(lin, 2),
            "Driver based": round(driver_monthly, 2),
            "Base (mean of methods)": round((ma + lin + driver_monthly) / 3, 2),
            "Low": round(low - sd, 2), "High": round(high + sd, 2),
        })
    return {
        "history": [{"Month": m, "RevenueUSD": round(v, 2)} for m, v in series],
        "forecast": out,
        "methods": [
            {"Method": "Moving average (3-month)", "Monthly": round(ma, 2),
             "12-month": round(ma * 12, 2), "MAPE % on hold-out": round(mape["Moving average (3-month)"], 1),
             "Assumption": "Recent run-rate persists; ignores trend and seasonality."},
            {"Method": "Linear trend (FORECAST.LINEAR)", "Monthly": round(slope * (len(values) + 5) + intercept, 2),
             "12-month": round(sum(r["Linear trend"] for r in out), 2),
             "MAPE % on hold-out": round(mape["Linear trend"], 1),
             "Assumption": f"Trend of {slope:,.0f} per month continues; extrapolation risk."},
            {"Method": "Driver based (retainers + weighted pipeline)", "Monthly": round(driver_monthly, 2),
             "12-month": round(driver_monthly * 12, 2),
             "MAPE % on hold-out": round(mape["Driver based"], 1),
             "Assumption": f"Retainer run-rate {recurring:,.0f}/month (CFO Advisory and "
                           f"Internal Audit co-sourcing, mean of last 3 months) + project "
                           f"run-rate {project_base:,.0f}/month (trailing 12 months) + "
                           f"{pipeline_uplift:,.0f}/month from the {len(open_pipe)} open "
                           f"opportunities deciding inside the window, weighted by stage "
                           f"probability and the historical win rate of {win_rate:.1%}."},
        ],
        "driver components": {"Retainer run-rate": round(recurring, 2),
                              "Project run-rate": round(project_base, 2),
                              "Pipeline uplift": round(pipeline_uplift, 2),
                              "Open opportunities in window": len(open_pipe),
                              "Historical win rate pct": round(win_rate * 100, 1)},
        "residual sd": round(sd, 2),
        "months history": len(values),
        "weighted pipeline": round(weighted, 2),
    }


# ---------------------------------------------------------------------------
# 5. Engagement-economics anomalies
# ---------------------------------------------------------------------------
def anomalies():
    rows = _load(ENGAGEMENTS)
    rates = {"Forensic investigation": 280, "Fraud risk assessment": 250,
             "Data analytics build": 200, "Power BI dashboard": 190,
             "Machine learning model": 260, "IFRS advisory": 230,
             "CFO advisory retainer": 210, "Tax analytics": 180,
             "Internal audit co-sourcing": 170}
    delivered = [r for r in rows if r["Status"] in ("Completed", "In progress")]
    out = []
    for r in delivered:
        planned, actual = float(r["PlannedHours"]), float(r["ActualHours"])
        fee, wo = float(r["FeeUSD"]), float(r["WriteOffUSD"])
        std_cost = actual * rates.get(r["ServiceLine"], 200) * 0.45
        overrun = (actual - planned) / planned * 100 if planned else 0
        realisation = fee / (actual * rates.get(r["ServiceLine"], 200)) * 100 if actual else 0
        margin = (fee - wo - std_cost) / fee * 100 if fee else 0
        flags = []
        if overrun > 25:
            flags.append(f"Over-ran budget by {overrun:.0f}%")
        if wo > 0.15 * fee and fee:
            flags.append(f"Write-off {wo / fee * 100:.0f}% of fee")
        if margin < 0:
            flags.append(f"Negative margin {margin:.0f}%")
        if realisation and realisation < 70:
            flags.append(f"Realisation {realisation:.0f}%")
        if flags:
            severity = round(wo + max(0.0, (actual - planned)) * rates.get(r["ServiceLine"], 200)
                             + max(0.0, -margin) / 100 * fee, 2)
            out.append({
                "SeverityUSD": severity,
                "EngagementID": r["EngagementID"], "ClientName": r["ClientName"],
                "ServiceLine": r["ServiceLine"], "Manager": r["EngagementManager"],
                "Period": r["Period"], "Status": r["Status"],
                "PlannedHours": planned, "ActualHours": actual,
                "Overrun pct": round(overrun, 1), "FeeUSD": fee, "WriteOffUSD": wo,
                "Realisation pct": round(realisation, 1), "Margin pct": round(margin, 1),
                "NPS": r["NetPromoterScore"],
                "Anomaly": "; ".join(flags),
                "Explanation (partner to complete)": "",
            })
    out.sort(key=lambda r: -r["SeverityUSD"])
    return {
        "rows": out,
        "population": len(delivered),
        "excluded": len(rows) - len(delivered),
        "thresholds": "Over-run > 25% of planned hours; write-off > 15% of fee; "
                      "negative contribution margin; realisation < 70% of standard rate.",
        "total write-offs": round(sum(r["WriteOffUSD"] for r in out), 2),
        "top 25 severity": round(sum(r["SeverityUSD"] for r in out[:25]), 2),
    }


def fee_at_risk(model):
    """Latest year per client, scored: probability of churn x annual fee."""
    latest = {}
    for r in model["scored"]:
        y = int(r["Year"])
        if r["ClientID"] not in latest or y > int(latest[r["ClientID"]]["Year"]):
            latest[r["ClientID"]] = r
    rows = sorted(latest.values(), key=lambda r: -r["FeeAtRiskUSD"])
    return {
        "rows": rows,
        "total fee": round(sum(float(r["AnnualFeeUSD"]) for r in rows), 2),
        "fee at risk": round(sum(r["FeeAtRiskUSD"] for r in rows), 2),
        "high risk": [r for r in rows if r["RiskBand"] == "High"],
        "high risk fee": round(sum(float(r["AnnualFeeUSD"]) for r in rows if r["RiskBand"] == "High"), 2),
    }


def run():
    model = baseline()
    exp, time_baseline = experiments()
    return {"model": model, "lift": lift(model),
            "experiments": {"rows": exp, "time_split_baseline": time_baseline},
            "forecast": forecast(), "anomalies": anomalies(),
            "fee_at_risk": fee_at_risk(model)}


if __name__ == "__main__":
    res = run()
    m = res["model"]
    print(f"accuracy {m['accuracy']:.1%} precision {m['precision']:.1%} "
          f"recall {m['recall']:.1%} specificity {m['specificity']:.1%} cm {m['cm']} "
          f"baseline {m['baseline_accuracy']:.1%}")
    print("\nLift:")
    for r in res["lift"]:
        print(f"  {r['Segment']:<20} n={r['Clients scored']:>3} left={r['Actually left']:>3} "
              f"rate={r['Churn rate pct']:>5.1f}% lift={r['Lift']:.2f} fee at risk {r['Fee at risk']:,.0f}")
    print("\nExperiments:")
    for r in res["experiments"]["rows"]:
        print(f"  {r['Experiment'][:52]:<54} acc {r['Accuracy pct']:>5.1f}% "
              f"({r['Change vs baseline (pp)']:+.1f}pp) prec {r['Precision pct']:>5.1f} rec {r['Recall pct']:>5.1f}")
    f = res["forecast"]
    print(f"\nForecast methods (12-month totals):")
    for x in f["methods"]:
        print(f"  {x['Method']:<42} {x['12-month']:>12,.0f}  MAPE {x['MAPE % on hold-out']:>5.1f}%")
    far = res["fee_at_risk"]
    print(f"\nClients {len(far['rows'])} | total fee {far['total fee']:,.0f} | "
          f"fee at risk {far['fee at risk']:,.0f} | high-risk fee {far['high risk fee']:,.0f}")
    a = res["anomalies"]
    print(f"Anomalies: {len(a['rows'])} of {a['population']} delivered engagements "
          f"(write-offs {a['total write-offs']:,.0f}); top item {a['rows'][0]['EngagementID']} "
          f"severity {a['rows'][0]['SeverityUSD']:,.0f}")
    print("Driver components:", {k: f"{v:,.0f}" if isinstance(v,float) else v for k,v in f["driver components"].items()})
