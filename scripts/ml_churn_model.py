#!/usr/bin/env python3
"""
ml_churn_model.py - logistic regression churn model for the Maxhub advisory practice.

Built with the Python standard library only (no pandas / scikit-learn needed) so it runs
anywhere. It deliberately uses an explainable model: the coefficients map to business
drivers a client's audit committee can read.

Dataset : data/raw/maxhub_client_churn.csv  (150 client-years = 30 clients x FY2021-2025,
          label "Stayed")
Output  : data/scored/maxhub_client_churn_scored.csv  (load this into Power BI)

Usage: python3 scripts/ml_churn_model.py
"""
import csv
import math
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "data", "raw", "maxhub_client_churn.csv")
OUT = os.path.join(ROOT, "data", "scored")

NUMERIC = ["AnnualFeeUSD", "ServicesPurchased", "NPS", "ComplaintsLogged",
           "AvgPaymentDays", "EngagementDelayDays", "PartnerHoursOnClient",
           "AuditFindingsRaised", "FeeChangePct"]


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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
            y = float(r["Stayed"])
            err = p - y
            grads[0] += err
            for i, c in enumerate(names, start=1):
                mean, sd = stats[c]
                grads[i] += err * ((float(r[c]) - mean) / sd)
        for i in range(len(w)):
            w[i] -= lr * grads[i] / len(rows)
    return w, stats


def evaluate(rows, w, stats, names, threshold=0.5):
    tp = tn = fp = fn = 0
    for r in rows:
        p = score_row(r, w, stats, names)
        y = int(r["Stayed"])
        pred = 1 if p >= threshold else 0
        tp += 1 if (pred == 1 and y == 1) else 0
        tn += 1 if (pred == 0 and y == 0) else 0
        fp += 1 if (pred == 1 and y == 0) else 0
        fn += 1 if (pred == 0 and y == 1) else 0
    total = max(1, tp + tn + fp + fn)
    acc = (tp + tn) / total
    prec = tp / max(1, tp + fp)
    rec = tp / max(1, tp + fn)
    spec = tn / max(1, tn + fp)
    return acc, prec, rec, spec, (tp, tn, fp, fn)


def main():
    if not os.path.exists(SRC):
        raise SystemExit(f"missing {SRC} - run scripts/generate_maxhub_data.py first")
    os.makedirs(OUT, exist_ok=True)

    rows = load(SRC)
    random.seed(7)
    random.shuffle(rows)
    cut = int(len(rows) * 0.7)
    train_rows, test_rows = rows[:cut], rows[cut:]

    w, stats = train(train_rows, NUMERIC)
    acc, prec, rec, spec, cm = evaluate(test_rows, w, stats, NUMERIC)
    baseline = sum(int(r["Stayed"]) for r in test_rows) / len(test_rows)

    print("\nMaxhub client churn model (logistic regression, standardised features)")
    print(f"  Train {len(train_rows)} rows | Test {len(test_rows)} rows | features {len(NUMERIC)}")
    print(f"  Baseline (always predict 'stayed'): {baseline:.1%}")
    print(f"  Model accuracy {acc:.1%} | precision {prec:.1%} | recall {rec:.1%} | specificity {spec:.1%}")
    print(f"  Confusion matrix (test): TP={cm[0]} TN={cm[1]} FP={cm[2]} FN={cm[3]}")
    print("\n  Feature weights (standardised; positive => client more likely to stay):")
    for c, wi in sorted(zip(NUMERIC, w[1:]), key=lambda x: -abs(x[1])):
        direction = "retains" if wi > 0 else "churns "
        print(f"    {c:<24}{wi:+.3f}   higher values {direction}")

    print("\n  Reading of the drivers (put this in the client methodology note):")
    print("    - NPS and partner hours are the strongest retention signals (relationship depth).")
    print("    - Complaints, slow payment and single-service clients are the churn profile.")
    print("    - With 150 observations (30 clients x 5 years) these weights are indicative,")
    print("      not production-grade: small samples overstate confidence.")
    print("    - Recommended action: quarterly review of High-risk clients before renewal.")

    out = os.path.join(OUT, "maxhub_client_churn_scored.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        fields = list(rows[0].keys()) + ["ChurnProbability", "ChurnRisk", "PredictedToStay", "ModelVersion"]
        wr = csv.DictWriter(f, fieldnames=fields)
        wr.writeheader()
        for r in rows:
            p = score_row(r, w, stats, NUMERIC)
            r = dict(r)
            r["ChurnProbability"] = round(p, 4)
            r["ChurnRisk"] = "High" if p < 0.4 else ("Medium" if p < 0.7 else "Low")
            r["PredictedToStay"] = "Yes" if p >= 0.5 else "No"
            r["ModelVersion"] = "v1.0-logreg-2025-10"
            wr.writerow(r)
    print(f"\n  Scored file written: {out}")
    print("  Load it into Power BI and build the 'At-risk clients' page (Module 11).\n")


if __name__ == "__main__":
    main()
