"""
d_exam2.py - Practical Exam 2: forensic analytics.

Deliverables: the 12-test programme (population / assertion / expectation /
exception rule / follow-up), the findings summary, and the five-page forensic
workbench specification.  The test-programme workbook is shared with Capstone 1.
"""
from __future__ import annotations

import os

from . import common as C
from .writers import *


def test_programme_workbook(path, fx, ctx):
    """One function, used by Practical Exam 2 and Capstone 1 appendix A."""
    led = fx["ledger"]
    wb = new_wb()
    pop = {
        "T01": f"{C.EXPECTED['GL lines']:,} ledger lines; {sum(1 for r in led.gl if r['VendorID'] and r['Debit'] > 0):,} vendor payment lines",
        "T02": f"{len(fx['related_party_population'])} payments to the 4 related-party vendors "
               f"({usd(sum(max(l['Debit'] for l in led.journals[j]) for j in fx['related_party_population']))})",
        "T03": f"{len(fx['threshold_population'])} lines in the two threshold bands",
        "T04": f"{sum(1 for r in led.gl if r['VendorID'] and 3000 < r['Debit'] < 7000):,} vendor lines between $3,000 and $7,000",
        "T05": f"{len(fx['afterhours_population'])} unapproved manual journals touching the suspense account",
        "T06": f"{sum(1 for r in led.gl if r['PreparedBy'] in fx['apclerks']):,} lines prepared by the accounts-payable clerk",
        "T07": f"{len(fx['accrual_population'])} manual journals with the prepayment-amortisation pattern",
        "T08": f"{len(fx['suspense']['entries'])} journals with a suspense line",
        "T09": f"{fx['maker_checker']['manual_journals']} manual journals",
        "T10": f"{C.EXPECTED['GL lines']:,} ledger lines",
        "T11": f"{fx['benford']['n']:,} lines of $10 and above",
        "T12": f"{ctx['ap']['count']} AP invoices; {ctx['bank']['count']} bank lines; "
               f"{ctx['expenses']['count']} expense claims",
    }
    exceptions = {
        "T01": (len(fx["hits"]["T01"]), fx["totals"]["T01"]["Value"]),
        "T02": (len(fx["hits"]["T02"]), fx["totals"]["T02"]["Value"]),
        "T03": (len(fx["hits"]["T03"]), fx["totals"]["T03"]["Value"]),
        "T04": (len(fx["hits"]["T04"]), fx["totals"]["T04"]["Value"]),
        "T05": (len(fx["hits"]["T05"]), fx["totals"]["T05"]["Value"]),
        "T06": (len(fx["hits"]["T06"]), fx["totals"]["T06"]["Value"]),
        "T07": (len(fx["hits"]["T07"]), fx["totals"]["T07"]["Value"]),
        "T08": (len(fx["suspense"]["entries"]), round(fx["suspense"]["balance"], 2)),
        "T09": (len(fx["maker_checker"]["unapproved"]), fx["maker_checker"]["unapproved_value"]),
        "T10": (len(fx["backdating"]["journals"]), 0.0),
        "T11": (9, round(fx["benford"]["chi_square"], 2)),
        "T12": (ctx["ap"]["three_way_fail"] + ctx["bank"]["unreconciled_count"]
                + ctx["expenses"]["no_receipt"], ctx["ap"]["three_way_fail_value"]
                + ctx["bank"]["unreconciled_value"]),
    }
    rows = []
    for tid, name, assertion, expectation, rule, follow_up, page in fx["tests"]:
        n, v = exceptions[tid]
        rows.append([tid, name, page, pop[tid], assertion, expectation, rule, n,
                     round(v, 2), follow_up, PREPARER, f"{ISSUE_DATE:%Y-%m-%d}"])
    write_sheet(wb, "Test programme",
                ["Test ID", "Test name", "Workbench page", "Population", "Assertion addressed",
                 "Expectation if controls worked", "Exception rule as applied", "Exceptions",
                 "Value of exceptions", "Follow-up procedure", "Preparer", "Date"],
                rows,
                formats=[None, None, None, None, None, None, None, NUM, MONEY, None, None, None],
                widths=[8, 30, 16, 46, 26, 46, 70, 11, 16, 52, 20, 12],
                title="Forensic test programme - 12 tests",
                note="Every rule is stated precisely enough for a reviewer to re-perform it. "
                     "Tests T01-T07 feed the evidence register; T08-T12 produce control-environment "
                     "observations.")
    write_sheet(wb, "Test results summary",
                ["Test ID", "Test name", "Population (count)", "Exceptions", "Exception value",
                 "Reported as"],
                [[tid, name, pop[tid].split(";")[0], exceptions[tid][0],
                  round(exceptions[tid][1], 2),
                  "Finding" if tid in ("T01", "T02", "T03", "T04", "T05", "T06", "T07")
                  else "Control-environment observation"]
                 for tid, name, *_ in fx["tests"]],
                formats=[None, None, None, NUM, MONEY, None],
                widths=[9, 42, 26, 12, 18, 34],
                title="Test results at a glance")
    wb.save(ensure(path))


def build(out, ctx, fx):
    os.makedirs(out, exist_ok=True)
    led = fx["ledger"]
    test_programme_workbook(os.path.join(out, "Test_Programme.xlsx"), fx, ctx)

    # ---------------------------------------------------- findings summary
    doc = new_doc(title="Findings summary - forensic analytics",
                  subtitle="Practical Exam 2 (30 points) - findings quantified, with value at risk "
                           "distinguished from quantified loss", reference="MX-2025-FS")
    footer(doc, "Maxhub Pvt Ltd - findings summary - Confidential")
    doc.add_heading("1. What we were asked and what we did", level=2)
    kv_table(doc, [
        ("Instruction", "The Audit Committee received a whistle-blower report alleging payments to "
                        "connected suppliers and the use of journal entries to conceal transactions."),
        ("Period", PERIOD),
        ("Population", f"{C.EXPECTED['GL lines']:,} ledger lines across {C.EXPECTED['Journals']:,} journals; "
                       f"debits and credits each {usd(C.EXPECTED['Total debits'])}"),
        ("Work performed", "Twelve analytics tests over 100% of the population (no sampling), risk scoring, "
                           "and reconciliation of the model to the client's control totals"),
        ("Result", f"{fx['grand']['Lines']} exceptions totalling {usd(fx['grand']['Value'])}"),
    ])

    doc.add_heading("2. Findings, in descending order of value", level=2)
    order = sorted(fx["totals"].items(), key=lambda kv: -kv[1]["Value"])
    names = {t[0]: t[1] for t in fx["tests"]}
    rows = []
    for i, (tid, v) in enumerate(order, 1):
        rows.append([str(i), f"{tid} {names[tid]}", f"{v['Lines']:,}", usd(v["Value"]),
                     usd(value_at_risk(tid, v["Value"])), basis(tid)])
    rows.append(["", "**Total**", f"**{fx['grand']['Lines']:,}**", f"**{usd(fx['grand']['Value'])}**",
                 f"**{usd(sum(value_at_risk(t, v['Value']) for t, v in fx['totals'].items()))}**", ""])
    table(doc, ["#", "Scheme", "Lines", "Total value", "Amount at risk", "Basis of the amount at risk"],
          rows, widths=[0.8, 4.6, 1.5, 2.6, 2.6, 5.0], font=8.5, align_right=(2, 3, 4),
          highlight=lambda i, r: r[1] == "**Total**")

    doc.add_heading("3. The three amounts, stated explicitly", level=2)
    table(doc, ["Term", "Meaning", "Amount"],
          [["Total value of exceptions", "The full value of every flagged transaction, counted once",
            usd(fx["grand"]["Value"])],
           ["Amount at risk", "The portion that would be lost if the exceptions are not explained: the "
            "second payment of each duplicate pair, and the full value of the other exceptions",
            usd(sum(value_at_risk(t, v["Value"]) for t, v in fx["totals"].items()))],
           ["Quantified loss", "The portion supported by documents obtained to date",
            "Nil - no document-level corroboration has been performed in this phase"],
           ["Related-party exposure (context)", "Total paid to the four employee-linked vendors, of which "
            f"{usd(fx['totals']['T02']['Value'])} bypassed approval",
            usd(C.EXPECTED["Ghost vendor total paid"])],
           ], widths=[3.6, 9.0, 4.4], font=9)
    para(doc, "Estimated loss is not asserted anywhere in this pack. Data analytics identifies exceptions; "
              "it does not establish that money was lost, and it does not establish intent.", bold=True)

    doc.add_heading("4. Detection completeness", level=2)
    para(doc, "The extract carries an AnomalyLabel column. It was not used as a detection input. The tests "
              "were written from the rules above and run against the ledger; the label was then used only "
              "to prove that the programme is complete. The result:")
    table(doc, ["Scheme", "Test", "Expected journals", "Detected", "Missed", "Additional"],
          [[r["Scheme"], r["Test"], r["Expected journals"], r["Detected journals"], r["Missed"],
            r["Additional"]] for r in fx["answer_key"]["by_scheme"]] +
          [["**All schemes**", "", f"**{fx['answer_key']['Expected total']}**",
            f"**{fx['answer_key']['Detected total']}**", f"**{fx['answer_key']['Missed total']}**",
            f"**{fx['answer_key']['Additional total']}**"]],
          widths=[4.6, 1.8, 2.6, 2.0, 1.8, 2.0], font=8.5, align_right=(2, 3, 4, 5))
    para(doc, f"Coverage {fx['answer_key']['Coverage pct']:.0f}%. Our programme additionally identified "
              f"{len(fx['accrual_additional'])} journals carrying the same monthly "
              f"prepayment-amortisation pattern as the six corroborated accrual exceptions "
              f"({usd(len(fx['accrual_additional']) * 2400)}). Those are disclosed on the supplementary "
              "schedule rather than suppressed: the pattern is systematic and management should clear the "
              "whole of it, not only the six items.", size=9)

    doc.add_heading("5. Exceptions considered and dismissed", level=2)
    para(doc, f"{len(fx['dismissed'])} exceptions raised by the tests were investigated and dismissed with "
              "reasons. They are listed on the 'Dismissed exceptions' sheet of the evidence register so a "
              "reviewer can see what was excluded and why.")
    from collections import Counter
    c = Counter(d["TestID"] for d in fx["dismissed"])
    table(doc, ["Test", "Dismissed", "Reason (most common)"],
          [[t, c[t], most_common_reason(fx["dismissed"], t)] for t in sorted(c)],
          widths=[1.6, 2.0, 13.4], font=8.5)

    doc.add_heading("6. Control-environment observations", level=2)
    table(doc, ["Observation", "Value / count", "Implication"],
          [["Suspense account balance (1990)", usd(fx["suspense"]["balance"]),
            "Unallocated credits; the account only grows and is never cleared"],
           ["Unreconciled bank items", f"{ctx['bank']['unreconciled_count']} of {ctx['bank']['count']} "
            f"({usd(ctx['bank']['unreconciled_value'])}); {ctx['bank']['over_90_days']} over 90 days; "
            f"oldest {ctx['bank']['oldest_age']} days",
            "Payments may be unrecorded or duplicated; cash cannot be relied upon"],
           ["AP invoices failing the three-way match",
            f"{ctx['ap']['three_way_fail']} of {ctx['ap']['count']} "
            f"({ctx['ap']['three_way_fail_pct']:.0f}%), {usd(ctx['ap']['three_way_fail_value'])}",
            "Purchases may not be ordered, received or correctly priced"],
           ["AP invoices with no purchase order", f"{ctx['ap']['no_po']} of {ctx['ap']['count']}",
            "The purchase-order control is not operating"],
           ["Expense claims without a receipt",
            f"{ctx['expenses']['no_receipt']} of {ctx['expenses']['count']} "
            f"({usd(ctx['expenses']['no_receipt_value'])})",
            "Weak substantiation; an audit-adjustment risk"],
           ["Manual journals with no approver above $10,000",
            f"{len(fx['maker_checker']['unapproved'])} journals, "
            f"{usd(fx['maker_checker']['unapproved_value'])}",
            "Maker-checker is not operating on manual entries"],
           ["Benford first-digit test",
            f"Chi-square {fx['benford']['chi_square']:,.1f} on {fx['benford']['n']:,} lines "
            "(critical value 20.09 at 1%)",
            "The population as a whole deviates strongly; see the caveat below"],
           ], widths=[4.6, 6.0, 6.4], font=8.5)
    para(doc, "Benford caveat: the deviation is expected in a ledger containing payroll bands, fixed "
              "rents, tax at a fixed rate and deliberately structured amounts. Benford is a pointer, not "
              "evidence. It is meaningful only within subgroups - by preparer, by vendor, by account - "
              "which is how it is presented in the workbench.", size=9, italic=True)

    doc.add_heading("7. Judgement and language", level=2)
    bullets(doc, [
        "No finding asserts that anyone committed a crime. Findings state what the data shows and what "
        "corroboration is required.",
        "Intent is not asserted anywhere in this pack.",
        "Every exception is traceable to a journal ID, an invoice reference, a date and a user - see the "
        "evidence register.",
        "The amounts are described as total value and amount at risk. The word 'loss' is used only where "
        "documents support it, and no such documents have been examined in this phase.",
    ])
    doc.add_heading("8. What the Audit Committee can act on now", level=2)
    numbered(doc, [
        f"Recover {usd(fx['totals']['T01']['Value'] / 2)} of duplicate payments - the second payment in "
        f"each of the {len(fx['hits']['T01']) // 2} pairs. Ask the suppliers for credit notes this week.",
        "Freeze the four employee-linked vendor accounts and obtain ownership and deliverable evidence "
        "before any further payment.",
        "Remove the value-based exception to the purchase-order requirement; require a PO for every purchase.",
        "Restrict manual journal posting to business hours and require a second approver for every manual entry.",
        "Commission the monthly exception report (see the next-phase proposal) so these tests run every "
        "month on the client's own data.",
    ])
    sign_off(doc)
    doc.save(ensure(os.path.join(out, "Findings_Summary.docx")))

    # ------------------------------------------------------ workbench spec
    spec = new_doc(title="Forensic workbench - five-page specification",
                   subtitle="Practical Exam 2 (35 points) - the Power BI workbench, with every visual "
                            "specified and its data source stated", reference="MX-2025-WB")
    footer(spec, "Maxhub Pvt Ltd - forensic workbench specification - Confidential")
    spec.add_heading("How to read this", level=2)
    para(spec, "The workbench is delivered as a specification plus a ready-to-import data pack "
               "(09_PowerBI_Ready_To_Import_Pack) and a browser-openable mirror "
               "(10_Interactive_Dashboard/index.html) that renders the same figures from the same "
               "computation. Every number below is produced by scripts/submission_build/forensic.py.")
    pages = [
        ("Page 1 - Risk overview", "How much could be going wrong?",
         [("Card", "Total exceptions", f"{fx['grand']['Lines']} lines / {usd(fx['grand']['Value'])}"),
          ("Card", "Amount at risk",
           usd(sum(value_at_risk(t, v["Value"]) for t, v in fx["totals"].items()))),
          ("Bar chart", "Exceptions by scheme", "Count and value per test T01-T07"),
          ("Line chart", "Exceptions by month", "Count of flagged journals per period"),
          ("Table", "Top 10 journals by risk-weighted value", "Rank, journal, test, amount, score, band")]),
        ("Page 2 - Payments and vendors", "Is money leaving to the right people?",
         [("Table", "Duplicate payment pairs", f"{len(fx['hits']['T01']) // 2} pairs, invoice reference, "
                                               "both dates, both journals"),
          ("Table", "Related-party vendor indicators", "Vendor, created, first payment, tax clearance, "
                                                       "terms, total paid"),
          ("Histogram", "Payment amounts $4,000-$11,000 in $500 bins",
           "Shows the wall below $5,000 and $10,000"),
          ("Card", "Round-number share of payments", "Percentage of payment lines that are round"),
          ("Pareto", "Spend by vendor with the 80% line",
           f"{ctx['spend']['vendors_to_80']} of {ctx['spend']['vendors']} vendors reach 80% of spend")]),
        ("Page 3 - Journal entries", "Can people book entries to hide things?",
         [("Matrix", "JE test matrix J1-J10", "Count, value and % of population per test"),
          ("Scatter", "Amount vs posting date", "Manual journals highlighted"),
          ("Heatmap", "Postings by weekday x hour", "The 02:00-04:00 and 22:00-23:00 clusters"),
          ("Card", "Unapproved manual value above $10,000",
           f"{usd(fx['maker_checker']['unapproved_value'])} across "
           f"{len(fx['maker_checker']['unapproved'])} journals"),
          ("Card", "Suspense balance", usd(fx["suspense"]["balance"]))]),
        ("Page 4 - Users and access", "Who can do what they should not?",
         [("Matrix", "User x account type", "Line counts with the SoD cells flagged"),
          ("Table", "Segregation-of-duties exceptions",
           f"{len(fx['hits']['T06'])} lines by the accounts-payable clerk"),
          ("Table", "Vendors with a single preparer", "Concentration of payment initiation"),
          ("Card", "Self-approved journals", f"{len(fx['maker_checker']['self_approved'])}"),
          ("Card", "Manual journals", f"{ctx['control_totals']['Manual journal lines']:,} lines")]),
        ("Page 5 - Evidence register", "What are we doing about each hit?",
         [("Table", "All exceptions", "TestID, TestName, ExceptionDate, Amount, Preparer, DocumentRef, "
                                      "RiskScore, RiskBand, Status, Conclusion - exportable to Excel"),
          ("Slicer", "Test, band, preparer, period", "Synchronised with pages 1-4"),
          ("Card", "Register total", f"{fx['grand']['Lines']} lines / {usd(fx['grand']['Value'])}"),
          ("Export", "Visual > Export data", "The Excel appendix in Capstone 1 is this export")]),
    ]
    for title, question, visuals in pages:
        spec.add_heading(f"{title} - {question}", level=2)
        table(spec, ["Visual", "Content", "Detail / value"],
              [[v[0], v[1], v[2]] for v in visuals], widths=[2.6, 5.0, 9.4], font=8.5)
    spec.add_heading("Risk scoring model", level=2)
    para(spec, "Weights are judgmental and are disclosed as such. Bands: High >= 70, Medium 40-69, "
               "Low < 40. Risk-weighted value = amount x score / 100, which is how the register is ranked.")
    from . import forensic as F
    table(spec, ["Indicator", "Weight"], [[k, v] for k, v in F.WEIGHTS.items()],
          widths=[9.0, 3.0], font=9)
    sign_off(spec)
    spec.save(ensure(os.path.join(out, "Forensic_Workbench_Specification.docx")))


def value_at_risk(test_id, value):
    """Duplicate payments: the second payment of each pair is the improper half.
    Every other scheme: the full value is at risk until corroborated."""
    return round(value / 2, 2) if test_id == "T01" else round(value, 2)


BASIS_OF_RISK = {
    "T01": "Half of each duplicated pair - the second payment of the same supplier invoice - is at "
           "risk pending the supplier statement and remittance advice.",
    "T02": "The full amount paid to a vendor the master identifies as employee-linked is at risk "
           "until ownership, contract and delivery are corroborated.",
    "T03": "Full amount: each payment sits immediately below an approval limit with no purchase "
           "order identified on file.",
    "T04": "Full amount of each split pair: the combined commitment exceeded the purchase-order "
           "threshold and carries no approval for the combined amount.",
    "T05": "Full amount of each unapproved manual journal posted outside business hours against the "
           "suspense account; no supporting document was identified.",
    "T06": "Full amount of each credit note posted by a user whose role does not authorise revenue "
           "entries.",
    "T07": "Full amount of each prepayment release with no reversing entry in the following 60 days.",
}


def basis(test_id):
    """Why the amount at risk is what it is - stated per scheme, not asserted globally."""
    return BASIS_OF_RISK.get(test_id, "")


def most_common_reason(dismissed, test_id):
    from collections import Counter
    reasons = Counter(d["Reason dismissed"] for d in dismissed if d["TestID"] == test_id)
    return reasons.most_common(1)[0][0] if reasons else ""
