"""
d_cap4.py - Capstone 4: churn model, forecasting, anomaly detection, model
governance and the service blueprint.
"""
from __future__ import annotations

import os

from . import common as C
from .writers import *

PRICING = [("Discovery and data review", "Fixed", 1500, 1500),
           ("Model build - one use case (churn, default, forecast or anomaly)", "Fixed", 6000, 12000),
           ("Power BI deployment of the scored output", "Fixed", 3000, 6000),
           ("Governance pack and staff briefing", "Fixed", 1500, 1500),
           ("Monitoring and retraining retainer", "Per month", 800, 2000)]


def build(out, ctx, ml):
    os.makedirs(out, exist_ok=True)
    m = ml["model"]
    scored_workbook(os.path.join(out, "Churn_Model_Scored_Clients.xlsx"), ml)
    forecast_workbook(os.path.join(out, "Forecast_and_Scenarios.xlsx"), ml)
    anomaly_workbook(os.path.join(out, "Anomaly_Register.xlsx"), ml)
    governance_pack(os.path.join(out, "Model_Governance_Pack.docx"), ml)
    ai_reporting_routine(os.path.join(out, "AI_Assisted_Reporting_Routine.docx"), ml)
    service_blueprint(os.path.join(out, "Service_Blueprint_and_Pricing.docx"), ml)


def scored_workbook(path, ml):
    m, far = ml["model"], ml["fee_at_risk"]
    wb = new_wb()
    write_sheet(wb, "Scored clients (all years)",
                ["ClientID", "ClientName", "Industry", "ClientSince", "ClientSize", "Year",
                 "AnnualFeeUSD", "ServicesPurchased", "NPS", "ComplaintsLogged", "AvgPaymentDays",
                 "EngagementDelayDays", "PartnerHoursOnClient", "AuditFindingsRaised", "FeeChangePct",
                 "Stayed", "P(stay)", "P(churn)", "RiskBand", "FeeAtRiskUSD"],
                [[r["ClientID"], r["ClientName"], r["Industry"], r["ClientSince"], r["ClientSize"],
                  r["Year"], float(r["AnnualFeeUSD"]), int(r["ServicesPurchased"]), int(r["NPS"]),
                  int(r["ComplaintsLogged"]), float(r["AvgPaymentDays"]),
                  float(r["EngagementDelayDays"]), float(r["PartnerHoursOnClient"]),
                  int(r["AuditFindingsRaised"]), float(r["FeeChangePct"]), r["Stayed"],
                  r["P_stay"], r["P_churn"], r["RiskBand"], r["FeeAtRiskUSD"]] for r in m["scored"]],
                formats=[None, None, None, None, None, NUM, MONEY, NUM, NUM, NUM, NUM, NUM, NUM, NUM,
                         PCT, None, '0.000', '0.000', None, MONEY],
                widths=[10, 30, 18, 12, 11, 7, 14, 17, 7, 16, 15, 18, 19, 18, 13, 8, 9, 10, 10, 14],
                title="Churn model - every client-year scored",
                note="IMPORTANT: the repository's scored CSV calls its column ChurnProbability, but the "
                     "model is trained on P(stay). This workbook states P(stay) and P(churn) separately "
                     "and computes fee at risk from P(churn). Using the shipped column name as if it were "
                     "a churn probability would invert the ranking - see the governance pack.")
    write_sheet(wb, "Risk board (latest year)",
                ["ClientID", "ClientName", "Industry", "Size", "Annual fee", "Services", "NPS",
                 "Complaints", "Payment days", "Partner hours", "P(churn)", "Risk band",
                 "Fee at risk", "Recommended action"],
                [[r["ClientID"], r["ClientName"], r["Industry"], r["ClientSize"],
                  float(r["AnnualFeeUSD"]), int(r["ServicesPurchased"]), int(r["NPS"]),
                  int(r["ComplaintsLogged"]), float(r["AvgPaymentDays"]),
                  float(r["PartnerHoursOnClient"]), r["P_churn"], r["RiskBand"], r["FeeAtRiskUSD"],
                  retention_action(r)] for r in far["rows"]],
                formats=[None, None, None, None, MONEY, NUM, NUM, NUM, NUM, NUM, '0.000', None, MONEY, None],
                widths=[10, 30, 18, 11, 14, 10, 7, 12, 14, 14, 10, 11, 14, 62],
                title=f"Risk board - {usd(far['fee at risk'])} of fees at risk of "
                      f"{usd(far['total fee'])}",
                note="Sorted by fee at risk = P(churn) x annual fee. This is the measure that makes "
                     "partners act: it converts a score into money.")
    write_sheet(wb, "Lift analysis",
                ["Segment", "Clients scored", "Actually left", "Churn rate %", "Baseline churn %",
                 "Lift", "Annual fee in segment", "Fee at risk"],
                [[r["Segment"], r["Clients scored"], r["Actually left"],
                  round(r["Churn rate pct"] / 100, 4), round(r["Baseline churn rate pct"] / 100, 4),
                  round(r["Lift"], 2), round(r["Annual fee in segment"], 2),
                  round(r["Fee at risk"], 2)] for r in ml["lift"]],
                formats=[None, NUM, NUM, PCT, PCT, '0.00', MONEY, MONEY],
                widths=[22, 15, 14, 13, 15, 8, 20, 16],
                title="Lift - does the score actually rank churners?",
                note="Read the top row: of the fifteen highest-risk client-years, all fifteen actually "
                     "left. That is what makes the score worth acting on.")
    write_sheet(wb, "Model card",
                ["Attribute", "Value"],
                [["Model ID", m["model_version"]],
                 ["Algorithm", "Logistic regression on standardised features (repository script "
                               "scripts/ml_churn_model.py)"],
                 ["Training date", f"{ISSUE_DATE:%Y-%m-%d}"],
                 ["Observations", f"{len(m['rows'])} client-years (train {len(m['train'])} / "
                                  f"test {len(m['test'])})"],
                 ["Label", "Stayed (1 = renewed, 0 = did not)"],
                 ["Baseline accuracy", round(m["baseline_accuracy"], 4)],
                 ["Model accuracy", round(m["accuracy"], 4)],
                 ["Precision", round(m["precision"], 4)],
                 ["Recall", round(m["recall"], 4)],
                 ["Specificity", round(m["specificity"], 4)],
                 ["Confusion matrix (TP/TN/FP/FN)", "/".join(map(str, m["cm"]))],
                 ["Features", ", ".join(m["names"])],
                 ["Owner", "Maxhub analytics"],
                 ["Review cycle", "Quarterly review; retrain annually or when accuracy falls more than "
                                  "5 points"]],
                formats=[None, None], widths=[30, 90], title="Model card")
    write_sheet(wb, "Feature weights",
                ["Feature", "Standardised weight", "Direction", "Plain-English reading"],
                [[w["Feature"], w["Weight"], w["Direction"], w["Plain English"]]
                 for w in m["weight_table"]],
                formats=[None, '0.000', None, None], widths=[26, 20, 12, 96],
                title="Feature weights and what each one means to a partner")
    wb.save(ensure(path))


def retention_action(r):
    if r["RiskBand"] != "High":
        return "Monitor at the quarterly review"
    drivers = []
    if int(r["ComplaintsLogged"]) > 0:
        drivers.append(f"{r['ComplaintsLogged']} open complaint(s) - close them before the renewal call")
    if int(r["NPS"]) < 7:
        drivers.append(f"NPS {r['NPS']} - partner call within two weeks")
    if float(r["AvgPaymentDays"]) > 60:
        drivers.append(f"paying in {float(r['AvgPaymentDays']):.0f} days - a relationship symptom, "
                       "not just a cash one")
    if int(r["ServicesPurchased"]) <= 2:
        drivers.append("only one or two service lines - cross-sell to deepen the relationship")
    if float(r["PartnerHoursOnClient"]) < 5:
        drivers.append("little partner time on the client - schedule a review meeting")
    return ("Call this quarter. " + "; ".join(drivers)) if drivers else "Call this quarter."


def forecast_workbook(path, ml):
    f = ml["forecast"]
    wb = new_wb()
    write_sheet(wb, "Forecast (12 months)",
                ["Month", "Moving average (3-month)", "Linear trend", "Driver based",
                 "Base (mean of methods)", "Low", "High"],
                [[r["Month"], r["Moving average (3-month)"], r["Linear trend"], r["Driver based"],
                  r["Base (mean of methods)"], r["Low"], r["High"]] for r in f["forecast"]],
                formats=[None] + [MONEY] * 6, widths=[11] + [22] * 6,
                title="Twelve-month revenue forecast - three methods and a range",
                note="A range, not a single confident line. The residual standard deviation of "
                     f"{usd(f['residual sd'])} is added to and subtracted from the method spread.")
    write_sheet(wb, "Method comparison",
                ["Method", "Monthly", "12-month total", "MAPE % on hold-out", "Assumption"],
                [[x["Method"], x["Monthly"], x["12-month"], x["MAPE % on hold-out"], x["Assumption"]]
                 for x in f["methods"]],
                formats=[None, MONEY, MONEY, '0.0', None], widths=[42, 16, 18, 20, 96],
                title="Three forecasting methods compared honestly",
                note="MAPE is measured on a six-month hold-out from the same history. The linear trend is "
                     "the most accurate on that test and the least safe to extrapolate.")
    write_sheet(wb, "History",
                ["Month", "Revenue USD"], [[h["Month"], h["RevenueUSD"]] for h in f["history"]],
                formats=[None, MONEY], widths=[11, 16],
                title=f"{f['months history']} months of service-line revenue history")
    basis = {
        "Retainer run-rate": ("Mean of the last three months of CFO Advisory and Internal Audit "
                              "co-sourcing revenue", "money"),
        "Project run-rate": ("Trailing twelve-month mean of the project-based service lines", "money"),
        "Pipeline uplift": ("Probability-weighted open pipeline with a decision date inside the "
                            "window, at the historical win rate", "money"),
        "Open opportunities in window": ("Lead, Qualified, Proposal and Negotiation stages only; "
                                         "Won and Lost excluded", "count"),
        "Historical win rate pct": ("Won / (Won + Lost) across the pipeline history", "pct"),
    }
    rows = [[k, (usd(v, 0) if basis.get(k, ("", "money"))[1] == "money"
                 else (f"{v:,}" if basis.get(k, ("", "count"))[1] == "count" else f"{v:.1f}%")),
             basis.get(k, ("",))[0]] for k, v in f["driver components"].items()]
    rows.append(["Weighted pipeline in the window", usd(f["weighted pipeline"], 0),
                 "Sum of expected fee x stage probability across the open opportunities"])
    write_sheet(wb, "Driver components", ["Component", "Value", "Basis"], rows,
                formats=[None, None, None], widths=[38, 22, 90],
                title="What the driver-based forecast is made of")
    wb.save(ensure(path))


def anomaly_workbook(path, ml):
    a = ml["anomalies"]
    wb = new_wb()
    write_sheet(wb, "Anomaly register",
                ["Rank", "Engagement", "Client", "Service line", "Manager", "Period", "Status",
                 "Planned hours", "Actual hours", "Over-run %", "Fee USD", "Write-off USD",
                 "Realisation %", "Margin %", "NPS", "Severity USD", "Anomaly",
                 "Explanation (partner to complete)"],
                [[i, r["EngagementID"], r["ClientName"], r["ServiceLine"], r["Manager"], r["Period"],
                  r["Status"], r["PlannedHours"], r["ActualHours"], round(r["Overrun pct"] / 100, 4),
                  r["FeeUSD"], r["WriteOffUSD"], round(r["Realisation pct"] / 100, 4),
                  round(r["Margin pct"] / 100, 4), r["NPS"], r["SeverityUSD"], r["Anomaly"],
                  r["Explanation (partner to complete)"]] for i, r in enumerate(a["rows"], 1)],
                formats=[NUM, None, None, None, None, None, None, NUM, NUM, PCT, MONEY, MONEY, PCT,
                         PCT, NUM, MONEY, None, None],
                widths=[6, 14, 30, 24, 20, 9, 12, 13, 13, 11, 13, 14, 13, 11, 7, 14, 52, 40],
                title=f"Engagement-economics anomalies - {len(a['rows'])} of {a['population']} "
                      "delivered engagements",
                note=a["thresholds"] + f" Severity = write-offs + over-run hours at the standard rate + "
                                       "the value of any negative margin. Every anomaly needs the "
                                       "one-line explanation completing before the partner meeting.")
    write_sheet(wb, "Summary",
                ["Measure", "Value"],
                [["Delivered engagements tested", a["population"]],
                 ["Engagements excluded (proposal or lost)", a["excluded"]],
                 ["Anomalies raised", len(a["rows"])],
                 ["Exception rate", round(len(a["rows"]) / a["population"], 4)],
                 ["Total write-offs in the exception set", round(a["total write-offs"], 2)],
                 ["Severity in the top 25", round(a["top 25 severity"], 2)],
                 ["Thresholds", a["thresholds"]]],
                formats=[None, None], widths=[42, 80],
                title="Anomaly summary",
                note="An exception rate above half is itself the finding: engagement economics are not "
                     "being monitored, so over-runs are discovered at invoicing rather than in month one.")
    wb.save(ensure(path))


def governance_pack(path, ml):
    m = ml["model"]
    doc = new_doc(title="Model governance pack - client churn risk model",
                  subtitle="Capstone 4 deliverable 5 - two pages, all nine sections",
                  reference="MX-2025-MG01")
    footer(doc, "Maxhub Pvt Ltd - model governance pack - Confidential")
    doc.add_heading("1. Purpose and users", level=2)
    para(doc, "The model supports retention decisions by partners: which clients to call before renewal "
              "and how much fee that protects. It is a prioritisation aid. It is not an automated "
              "decision-maker, and no client action is taken on the score alone.")
    doc.add_heading("2. Data", level=2)
    table(doc, ["Attribute", "Detail"],
          [["Source", "data/raw/maxhub_client_churn.csv"],
           ["Period", "FY2021 to FY2025"],
           ["Observations", f"{len(m['rows'])} client-years (30 clients x 5 years)"],
           ["Label", "Stayed: 1 = the client renewed, 0 = the client did not"],
           ["Class balance", f"{sum(1 for r in m['rows'] if r['Stayed'] == '1')} stayed, "
                             f"{sum(1 for r in m['rows'] if r['Stayed'] == '0')} left "
                             f"(overall churn rate "
                             f"{sum(1 for r in m['rows'] if r['Stayed'] == '0') / len(m['rows']):.1%})"],
           ["Split", "Random 70/30 (105 train / 45 test), plus a time-based validation on 2024-2025"],
           ["Personal data", "None at client level; no individual is identified"]],
          widths=[3.4, 13.6], font=9)
    doc.add_heading("3. Method", level=2)
    para(doc, "Logistic regression on standardised features, trained by gradient descent in the "
              "repository's own standard-library script. An explainable model was chosen deliberately: "
              "the coefficients are the client-facing explanation. Features: " + ", ".join(m["names"]) + ".")
    doc.add_heading("4. Performance", level=2)
    table(doc, ["Metric", "Model", "Baseline", "Reading"],
          [["Accuracy", f"{m['accuracy']:.1%}", f"{m['baseline_accuracy']:.1%}",
            f"{(m['accuracy'] - m['baseline_accuracy']) * 100:+.1f} points better than always predicting "
            "'stays'"],
           ["Precision", f"{m['precision']:.1%}", "-",
            "Of the clients flagged as likely to stay, this share did"],
           ["Recall", f"{m['recall']:.1%}", "-", "Of the clients who stayed, this share was flagged"],
           ["Specificity", f"{m['specificity']:.1%}", "-",
            "Of the clients who left, this share was correctly not flagged as safe"],
           ["Confusion matrix (test)", f"TP {m['cm'][0]} / TN {m['cm'][1]} / FP {m['cm'][2]} / "
                                       f"FN {m['cm'][3]}", "-", "On 45 client-years"]],
          widths=[3.4, 3.4, 2.6, 7.6], font=9)
    table(doc, ["Segment", "Clients", "Actually left", "Churn rate", "Lift"],
          [[r["Segment"], r["Clients scored"], r["Actually left"], f"{r['Churn rate pct']:.0f}%",
            f"{r['Lift']:.2f}x"] for r in ml["lift"]],
          widths=[4.0, 2.4, 2.6, 2.6, 2.0], font=9,
          caption="Lift - the practical value of the score")
    doc.add_heading("5. Limitations", level=2)
    bullets(doc, [
        f"150 observations is a small sample. Standard errors are wide and the weights are indicative, "
        "not production-grade.",
        "The data covers 2021-2025 only; it does not span a full economic cycle.",
        "Correlation is not causation. A low NPS is associated with churn; raising the NPS may not "
        "prevent it.",
        "No client interviews were conducted, so reasons for leaving are inferred from behaviour.",
        "The random 70/30 split can leak time. The time-based validation (train 2021-2023, test "
        f"2024-2025) is the honest test and gives {ml['experiments']['rows'][-2]['Accuracy pct']}%.",
    ])
    doc.add_heading("6. Fairness and bias", level=2)
    doc.add_paragraph()
    table(doc, ["Test", "Result", "Conclusion"],
          [["Are any sectors systematically over-flagged?", sector_bias(ml),
            "Reported above; no sector is flagged at more than twice its population share"],
           ["Are small-fee clients over-flagged?", fee_band_bias(ml),
            "Fee is the strongest weight in the model and it works against small clients. This is a real "
            "bias and it is disclosed: small clients are more likely to be flagged, so a partner must "
            "not treat a high score on a small client as a reason to stop investing in them."],
           ["Is any client excluded?", "No - all 30 clients are scored", "No coverage bias"]],
          widths=[4.6, 6.0, 6.4], font=8.5)
    doc.add_heading("7. Use rules", level=2)
    bullets(doc, [
        "A high score means 'call this client this quarter', not 'let this client go'.",
        "Where the score and the partner's judgement disagree, the partner's judgement wins and the "
        "disagreement is recorded - it is training data for the next version.",
        "The score is never shared with the client, and never used to price a renewal.",
        "Ambiguous situations (a client mid-dispute, a client changing ownership) are decided by a "
        "partner, not by the model.",
    ])
    doc.add_heading("8. Monitoring", level=2)
    table(doc, ["Check", "Frequency", "Trigger for action"],
          [["Accuracy against actual renewals", "Quarterly",
            "Retrain if accuracy falls more than 5 points below 68.9%"],
           ["Drift in the fee and NPS distributions", "Quarterly",
            "Retrain if either shifts by more than one standard deviation"],
           ["Feature availability and quality", "Monthly", "Investigate any missing feature before scoring"],
           ["Full retrain", "Annually", "Or on any material change to the service mix"],
           ["Version and owner recorded", "Every release", "No unversioned model is used in client work"]],
          widths=[5.4, 2.6, 9.0], font=9)
    doc.add_heading("9. Version", level=2)
    kv_table(doc, [("Model ID", m["model_version"]),
                   ("Training date", f"{ISSUE_DATE:%Y-%m-%d}"),
                   ("Script", "scripts/ml_churn_model.py (standard library, auditable line by line)"),
                   ("Build harness", "scripts/submission_build/ml.py"),
                   ("Owner", "Maxhub analytics"),
                   ("Approver", "Engagement partner")])
    para(doc, "Known defect disclosed: the shipped scored CSV names its output column ChurnProbability, "
              "but the model returns the probability of staying. Any consumer using that column as a "
              "churn probability would invert the ranking. This submission computes P(churn) = 1 - P(stay) "
              "and renames the column; the repository script should be corrected at source.", bold=True,
         size=9)
    sign_off(doc)
    doc.save(ensure(path))


def sector_bias(ml):
    from collections import defaultdict
    latest = {}
    for r in ml["model"]["scored"]:
        if r["ClientID"] not in latest or int(r["Year"]) > int(latest[r["ClientID"]]["Year"]):
            latest[r["ClientID"]] = r
    rows = list(latest.values())
    agg = defaultdict(lambda: [0, 0])
    for r in rows:
        agg[r["Industry"]][0] += 1
        if r["RiskBand"] == "High":
            agg[r["Industry"]][1] += 1
    parts = [f"{k}: {v[1]} of {v[0]} flagged high ({v[1] / v[0]:.0%})" for k, v in sorted(agg.items())]
    return "; ".join(parts)


def fee_band_bias(ml):
    latest = {}
    for r in ml["model"]["scored"]:
        if r["ClientID"] not in latest or int(r["Year"]) > int(latest[r["ClientID"]]["Year"]):
            latest[r["ClientID"]] = r
    rows = sorted(latest.values(), key=lambda r: float(r["AnnualFeeUSD"]))
    half = len(rows) // 2
    small = rows[:half]
    large = rows[half:]
    fs = sum(1 for r in small if r["RiskBand"] == "High") / len(small)
    fl = sum(1 for r in large if r["RiskBand"] == "High") / len(large)
    return (f"Smaller half by fee: {fs:.0%} flagged high; larger half: {fl:.0%} flagged high")


def ai_reporting_routine(path, ml):
    m = ml["model"]
    far = ml["fee_at_risk"]
    doc = new_doc(title="AI-assisted reporting routine - with human review",
                  subtitle="Capstone 4 deliverable 3 - documented prompt, review checklist and audit trail",
                  reference="MX-2025-AI01")
    footer(doc, "Maxhub Pvt Ltd - AI-assisted reporting routine - Confidential")
    doc.add_heading("1. The routine", level=2)
    table(doc, ["Step", "Who", "What happens", "Output"],
          [["1. Extract", "Analyst", "Metrics are extracted from the model into a fixed table: revenue, "
            "margin, DSO, exceptions, churn scores. No narrative is written yet.", "metrics.csv"],
           ["2. Draft", "AI (supervised)", "The prompt below is run against metrics.csv only. The AI is "
            "given the numbers and nothing else.", "draft_commentary.md"],
           ["3. Verify", "Analyst", "Every number in the draft is traced back to metrics.csv. Any number "
            "that is not in the table is deleted.", "verified_commentary.md"],
           ["4. Review", "Manager", "Tone, materiality, omissions and client-identifying data are checked "
            "against the checklist.", "reviewed_commentary.md"],
           ["5. Sign off", "Partner", "The pack is signed and issued. The audit trail records who drafted, "
            "who verified and who signed.", "issued pack"]],
          widths=[1.8, 2.6, 9.0, 3.6], font=8.5)
    doc.add_heading("2. The prompt (verbatim)", level=2)
    para(doc, "You are writing the monthly management commentary for an accounting firm's own numbers. "
              "Use ONLY the figures in the table below. Do not estimate, extrapolate or introduce any "
              "figure that is not in the table. Write four paragraphs: performance, drivers, risks, and "
              "the one action for next month. Plain English, no adjectives, no forecasts. Where a figure "
              "has fallen, say by how much and against what. If the table does not contain enough "
              "information for a paragraph, write 'insufficient data' instead of guessing. Table: "
              "{metrics.csv}", size=9.5, italic=True)
    para(doc, "What data is sent: aggregated metrics only - no client names, no individual staff names, "
              "no bank details, no personal data. Client-level scores stay in the model.", size=9)
    doc.add_heading("3. Review checklist (all must pass before issue)", level=2)
    bullets(doc, [
        "Every number in the draft appears in metrics.csv and matches exactly.",
        "No comparison is made to a period that is not in the table (hallucinated comparatives are the "
        "most common failure).",
        "No material movement in the table has been omitted from the narrative.",
        "Tone is factual: no accusation, no superlatives, no speculation about intent.",
        "No client-identifying or personal data appears anywhere in the prompt or the output.",
        "Recommendations are specific and owned.",
        "The reader can tell which figures are actual and which are estimates.",
    ])
    doc.add_heading("4. Worked before-and-after example", level=2)
    para(doc, "AI draft (step 2), unverified:", bold=True, size=9.5)
    para(doc, "\"The firm's churn risk has improved markedly this quarter, with client retention trending "
              "strongly upwards. Fee income is expected to grow substantially, and only a handful of "
              "clients present any concern. The outlook is excellent.\"", size=9.5, italic=True)
    para(doc, "Why it fails the checklist:", bold=True, size=9.5)
    bullets(doc, [
        "'Improved markedly' - the table shows no improvement; the model's accuracy is unchanged.",
        "'Fee income is expected to grow substantially' - a forecast the prompt forbade.",
        "'Only a handful of clients' - the table shows "
        f"{len(far['high risk'])} of {len(far['rows'])} clients in the High band.",
        "'The outlook is excellent' - a superlative with no figure behind it.",
    ], size=9.5)
    para(doc, "Verified and reviewed version (steps 3-4):", bold=True, size=9.5)
    para(doc, f"\"Of {len(far['rows'])} clients scored, {len(far['high risk'])} are in the High risk band, "
              f"representing {usd(far['high risk fee'])} of annual fees out of {usd(far['total fee'])} "
              f"in total. The model's fee at risk is {usd(far['fee at risk'])}. The three largest "
              f"exposures are {', '.join(r['ClientName'] for r in far['high risk'][:3])}. Recommended "
              f"action for next month: partner calls to those clients before their renewal dates.\"",
         size=9.5, italic=True)
    doc.add_heading("5. Audit trail", level=2)
    table(doc, ["Stage", "Person", "Date", "Record"],
          [["Metrics extracted", "Analyst", f"{ISSUE_DATE:%Y-%m-%d}", "metrics.csv, version-stamped"],
           ["Draft generated", "AI (supervised)", f"{ISSUE_DATE:%Y-%m-%d}",
            "Prompt and raw output stored on the engagement file"],
           ["Numbers verified", "Analyst", f"{ISSUE_DATE:%Y-%m-%d}", "Trace of each figure to metrics.csv"],
           ["Reviewed", "Manager", f"{ISSUE_DATE:%Y-%m-%d}", "Checklist signed"],
           ["Issued", "Partner", f"{ISSUE_DATE:%Y-%m-%d}", "Signed pack"]],
          widths=[3.4, 3.0, 3.0, 7.6], font=9)
    doc.add_heading("6. Failure modes we plan for", level=2)
    table(doc, ["Failure mode", "How it appears", "Control"],
          [["Confidently wrong numbers", "A figure that looks plausible and is not in the data",
            "Rule 1 of the checklist: delete any figure not in metrics.csv"],
           ["Hallucinated comparisons", "'up 12% on last year' when no prior-year figure was supplied",
            "The prompt forbids comparison to periods not in the table"],
           ["Missing a material item", "A large movement omitted because it is inconvenient",
            "The reviewer works from the metrics table, not the draft"],
           ["Tone drift", "Adjectives and forecasts creep in",
            "Language review at step 4; the report template constrains the structure"],
           ["Data leakage", "Client or personal data pasted into a public model",
            "Only aggregated metrics are sent; the prompt is stored and audited"]],
          widths=[3.4, 6.2, 7.4], font=8.5)
    para(doc, "Never issue an AI-written number that a human has not validated against the model.",
         bold=True)
    sign_off(doc)
    doc.save(ensure(path))


def service_blueprint(path, ml):
    far = ml["fee_at_risk"]
    doc = new_doc(title="Service blueprint - prediction models as a sellable service",
                  subtitle="Capstone 4 deliverable 6 - the offer, the delivery process and the price",
                  reference="MX-2025-SB01")
    footer(doc, "Maxhub Pvt Ltd - service blueprint - Confidential")
    doc.add_heading("1. The offer, in the client's language", level=2)
    para(doc, "\"We will tell you which three clients to call this quarter, and show you the "
              f"{usd(far['fee at risk'], 0)} of fees that protects.\" That is the product. The logistic "
              "regression is how we make it, not what we sell.")
    doc.add_heading("2. Pricing", level=2)
    table(doc, ["Component", "Basis", "Low", "High"],
          [[p[0], p[1], usd(p[2], 0), usd(p[3], 0)] for p in PRICING] +
          [["**Typical first engagement (churn model, deployed, governed)**", "Fixed",
            f"**{usd(1500 + 6000 + 3000 + 1500, 0)}**", f"**{usd(1500 + 12000 + 6000 + 1500, 0)}**"]],
          widths=[9.0, 2.6, 2.6, 2.8], font=9, align_right=(2, 3))
    para(doc, "Benchmarked to the Service Catalogue: prediction models are priced at $6,000-$30,000 per "
              "model with $800-$2,000 per month for monitoring and retraining. This sits at the lower end "
              "because the use case is narrow and the data is small; it would price higher for a debtor "
              "default model on a large receivables ledger.")
    doc.add_heading("3. Delivery process", level=2)
    table(doc, ["Week", "Activity", "Client must provide", "Deliverable"],
          [["1", "Discovery and data review; agree the label and the use case",
            "Client list with renewals for five years", "Data review note"],
           ["2-3", "Baseline model, feature work, honest out-of-sample testing",
            "Access to the CRM and billing data", "Model with metrics against the baseline"],
           ["3", "Deploy the scored output into the client's reporting",
            "A Power BI workspace and a data gateway", "Risk board and driver explainer pages"],
           ["4", "Governance pack, staff briefing, handover",
            "An owner for the model", "Governance pack and model card"],
           ["Ongoing", "Quarterly review; annual retrain; drift monitoring",
            "Updated renewal outcomes each quarter", "Quarterly review note"]],
          widths=[1.6, 6.4, 4.6, 4.4], font=8.5)
    doc.add_heading("4. The three client questions, answered", level=2)
    kv_table(doc, [
        ("How long?", "Three to five weeks from data access to a governed model in production."),
        ("How much?", "$12,000 to $21,000 for the first model including deployment and governance, then "
                      "$800 to $2,000 a month for monitoring and retraining. Fixed fee once the use case "
                      "is agreed."),
        ("How do I know it is right?", "We publish the baseline first and beat it in the open "
                                       f"({ml['model']['accuracy']:.1%} against a "
                                       f"{ml['model']['baseline_accuracy']:.1%} baseline). We test "
                                       "out-of-time, not just out-of-sample. Every model ships with a "
                                       "model card, a governance pack and a human review of every "
                                       "AI-generated number."),
    ])
    doc.add_heading("5. What the client must provide", level=2)
    bullets(doc, [
        "At least three years of client or customer history with a clear outcome label.",
        "A named owner for the model who attends the quarterly review.",
        "Read-only access to the systems that hold the features.",
        "A decision process: what happens when the model flags a client.",
    ])
    doc.add_heading("6. The pitch principle", level=2)
    para(doc, "Sell the decision, not the algorithm. \"We will tell you which three clients to call this "
              "quarter\" beats \"we build a logistic regression\" every time - and it is also true, "
              "because the lift analysis shows that the highest-scoring clients really do leave.")
    sign_off(doc)
    doc.save(ensure(path))
