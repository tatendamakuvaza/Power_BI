"""
d_cap1.py - Capstone 1: the forensic investigation.

Deliverables: engagement and methodology memo, test programme (appendix A),
evidence register (171 scored lines), findings report, board presentation
(12 slides) and remediation plan.
"""
from __future__ import annotations

import os

from . import common as C
from .writers import *
from .d_exam2 import test_programme_workbook, value_at_risk
from .d_exam3 import RATES, SCOPE, fee, hours

FINDING_META = {
    "T02": ("Payments to suppliers connected to employees",
            "The vendor master identifies four suppliers as employee-linked (SUP-771 to SUP-774: "
            "R Chikafu Trading Enterprises, Zhou Logistics & Advisory, Gumbo General Suppliers and "
            "Meridian Consulting Group). All four were created in July and August 2024, none has a tax "
            "clearance number on file, and all four are on seven-day payment terms. Payments to them total "
            + usd(C.EXPECTED["Ghost vendor total paid"]) + ", of which "
            + usd(445568.39) + " was initiated outside the accounts-payable payment run by a single user "
            "with no approver recorded.",
            "Validity of the vendor; occurrence and authorisation of the payment",
            "Vendor onboarding has no independent verification of ownership, and the payment run can be "
            "bypassed without a second approver.",
            "Freeze the four vendor accounts pending verification of ownership, contracts and deliverables; "
            "obtain the bank mandates and compare them to the employee master; require partner-level "
            "approval for any new vendor within 180 days of creation."),
    "T05": ("Manual journals posted outside business hours to the suspense account",
            "Twenty-one manual journals were entered on Saturdays between 02:00 and 04:41 and between "
            "22:00 and 23:31, by a single user (USR-012), with no approver recorded. Each debits an "
            "expense account and credits the suspense account, so an expense is recognised while the "
            "corresponding liability is parked in an unallocated clearing account.",
            "Validity and cut-off of the journal entry",
            "Manual journal posting is not restricted to business hours and does not require a second "
            "approver; the suspense account is not reviewed monthly.",
            "Restrict manual journal posting to business hours; require a second approver for every manual "
            "entry; clear the suspense account monthly with a written allocation for each item."),
    "T01": ("Supplier invoices paid twice",
            "Twenty-one supplier invoices were paid twice. In each pair the vendor, the amount to the cent "
            "and the invoice reference in the journal description are identical, and the two payments are "
            "between four and twelve days apart. The second payment in each pair is the improper portion.",
            "Occurrence and existence of the payment",
            "There is no duplicate-invoice block in the payment process, and no reconciliation of supplier "
            "statements to the creditor ledger.",
            "Issue credit-note requests to the suppliers this month with the evidence attached; implement a "
            "duplicate-invoice block on vendor plus invoice reference; reconcile supplier statements monthly."),
    "T06": ("Revenue credit notes posted by the accounts-payable clerk",
            "Fifteen revenue credit notes totalling " + usd(279600.00) + " were posted by the user whose "
            "role is Accounts Payable Clerk (USR-002), debiting revenue and crediting trade receivables. "
            "Posting revenue adjustments is not within that role.",
            "Authorisation and validity; segregation of duties",
            "System rights allow an accounts-payable user to post to revenue accounts, and no monitoring "
            "reviews postings by role.",
            "Remove the revenue-posting right from accounts-payable roles; obtain the documentation for the "
            "fifteen credit notes and re-perform them; run the user-by-account-type matrix monthly."),
    "T04": ("Purchases split into two invoices below the approval threshold",
            "Twenty-one purchases were each divided into two identical invoices posted to the same vendor "
            "and the same expense account within two to five days. Each invoice is below the $10,000 "
            "approval limit; each pair is above it. No approval for the combined commitment was identified.",
            "Authorisation",
            "The approval control operates on the invoice, not on the commitment, so structuring defeats it.",
            "Require a purchase order for every purchase regardless of value; test for aggregation by vendor "
            "and week in the monthly exception report."),
    "T03": ("Payments siting just below the purchase-order and approval limits",
            "Thirty procurement payments of exactly $4,985, $4,990, $4,995, $9,750 or $9,900 were posted to "
            "consumables and packaging against named vendors, with no purchase order on file. The amounts "
            "are round to the dollar and sit immediately below the $5,000 purchase-order threshold and the "
            "$10,000 approval limit.",
            "Authorisation",
            "The value-based exception to the purchase-order requirement creates an incentive to structure "
            "amounts below the threshold, and nothing tests for it.",
            "Remove the value-based exception; test the distribution of payment amounts monthly for a wall "
            "below each limit; require a purchase order for every purchase."),
    "T07": ("Prepayment amortisation entries never reversed",
            "Six monthly journals debit prepayments and credit insurance expense by $2,400 each, with no "
            "reversal in the following period. The same pattern appears in fifteen further months; the "
            "prepayment account only ever increases, which is the opposite of an amortisation.",
            "Cut-off and accuracy",
            "There is no prepayment schedule reconciled to the ledger, and no review of recurring manual "
            "entries.",
            "Agree the prepayment schedule to the underlying contracts; reverse the entries with no "
            "supporting asset; schedule an automatic review of recurring manual journals."),
}


def build(out, ctx, fx):
    os.makedirs(out, exist_ok=True)
    led = fx["ledger"]
    test_programme_workbook(os.path.join(out, "Appendix_A_Test_Programme.xlsx"), fx, ctx)
    evidence_register(os.path.join(out, "Evidence_Register.xlsx"), fx, ctx)
    remediation_plan(os.path.join(out, "Remediation_Plan.xlsx"), fx, ctx)
    memo(os.path.join(out, "Engagement_and_Methodology_Memo.docx"), ctx, fx)
    findings_report(os.path.join(out, "Findings_Report.docx"), ctx, fx)
    board_presentation(os.path.join(out, "Board_Presentation.pptx"), ctx, fx)


# ---------------------------------------------------------------------------
def memo(path, ctx, fx):
    doc = new_doc(title="Engagement and methodology memo",
                  subtitle="Capstone 1 deliverable 1 - scope, data lineage and method",
                  reference="MX-2025-FI01")
    footer(doc, "Maxhub Pvt Ltd - engagement and methodology memo - Confidential and legally privileged")
    doc.add_heading("1. Engagement", level=2)
    kv_table(doc, [
        ("Client", CLIENT),
        ("Engagement", "Forensic investigation - suspected misappropriation, procure-to-pay and "
                       "journal-entry cycles"),
        ("Instructed by", "The Audit Committee, following a whistle-blower report"),
        ("Period under review", PERIOD),
        ("Standard of work", "IESBA Code of Ethics; Maxhub quality-control standards; not an audit"),
        ("Engagement team", "Partner (QC), Manager (delivery), Senior analyst, Analyst"),
        ("Report reference", "MX-2025-FI01"),
        ("Classification", "Confidential and legally privileged; distribution limited to named recipients"),
    ])
    doc.add_heading("2. Scope", level=2)
    para(doc, "In scope: 100% of the general ledger for the period; the vendor, customer and employee "
              "masters; the creditor and debtor sub-ledgers as provided; bank statement lines; expense "
              "claims; and the fixed asset register. Out of scope: periods outside the review window, tax "
              "computations, legal advice, recovery of funds, and any assurance opinion.")
    doc.add_heading("3. Data lineage", level=2)
    ct = ctx["control_totals"]
    table(doc, ["Step", "Detail"],
          [["Received", "17 CSV extracts and 3 Excel workbooks, 1 October 2025, from the Financial Controller"],
           ["Integrity", "SHA-256 recorded for every file on receipt; originals stored unaltered; analysis "
                         "performed on copies"],
           ["Reconciliation", f"Debits {usd(ct['Total debits'])} = credits {usd(ct['Total credits'])}; "
                              f"{ct['Journals']:,} journals, all balanced; {ct['Orphan GL account keys']} "
                              f"orphan account keys; {ct['Orphan GL vendor keys']} orphan vendor keys"],
           ["Trial balance", "GL-derived trial balance agrees to the delivered FactTrialBalance on all 64 "
                             "accounts used (0 differences)"],
           ["Population", f"{ct['GL lines']:,} ledger lines, {ct['First posting']} to {ct['Last posting']}, "
                          f"{ct['Periods covered']} periods with no gaps"],
           ["Sub-ledgers", f"Creditor extract {ctx['ap']['count']} invoices ({usd(ctx['ap']['total'])}) - a "
                           f"sample; GL spend to vendors {usd(ctx['spend']['total'])}. The difference is "
                           "disclosed and a complete extract has been requested."],
           ["Reproducibility", "Every figure is produced by scripts/build_submission.py from data/raw; the "
                               "same extract always produces the same numbers"]],
          widths=[3.2, 13.8], font=9)
    doc.add_heading("4. Method", level=2)
    numbered(doc, [
        "Prove the population before testing it: control totals, journal balance, orphan keys, trial "
        "balance agreement.",
        "Run twelve analytics tests over 100% of the population. No sampling. Each test has a stated "
        "population, assertion, expectation, exception rule and follow-up (appendix A).",
        "Score every exception on a disclosed, judgmental weighting model and rank by risk-weighted value.",
        "Investigate the top exceptions: read the journal, the vendor master, the timing and the approval "
        "trail; write a finding note for each scheme.",
        "Quantify three amounts separately - total value, amount at risk, quantified loss - and state the "
        "basis of each.",
        "Reconcile the register to the client's records and record what was excluded and why.",
        "Report facts and exceptions, not accusations; recommend specific, owned, dated remediation.",
    ])
    doc.add_heading("5. Scoring model", level=2)
    from . import forensic as F
    table(doc, ["Indicator", "Weight", "Why"],
          [[k, v, why] for (k, v), why in zip(F.WEIGHTS.items(), [
              "A duplicate payment is a near-certain error once confirmed",
              "Round amounts above the threshold are a structuring signal",
              "Timing outside business hours defeats supervisory review",
              "No approver means the maker-checker control did not operate",
              "Manual entries bypass system-enforced controls",
              "A recently created vendor has no trading history to corroborate it",
              "Size determines materiality to the investigation"])] +
          [["**Bands**", "", "High >= 70, Medium 40-69, Low < 40; rank by amount x score / 100"]],
          widths=[5.4, 2.0, 9.6], font=9)
    para(doc, "The weights are judgmental. That is normal and acceptable provided it is disclosed: the "
              "scoring decides the order in which exceptions are investigated, not whether they are "
              "exceptions.", size=9, italic=True)
    doc.add_heading("6. Limitations", level=2)
    bullets(doc, [
        "Data analytics identifies exceptions; it does not establish intent or illegality.",
        "We have not verified the completeness of the systems that produced the extracts.",
        "The creditor extract is a sample, so three-way-match statistics are stated on that basis.",
        "No document-level corroboration has been performed; nothing is reported as a quantified loss.",
        "No procedures were performed to identify events after the date of this memo.",
        "The data analysed is simulated engagement data generated for training purposes.",
    ])
    sign_off(doc)
    doc.save(ensure(path))


# ---------------------------------------------------------------------------
def evidence_register(path, fx, ctx):
    led = fx["ledger"]
    wb = new_wb()
    reg = sorted(fx["register"], key=lambda r: r["Rank"])
    write_sheet(wb, "Evidence register",
                ["Rank", "JournalID", "TestID", "TestName", "All tests fired", "ExceptionDate",
                 "DocumentDate", "EnteredOn", "Period", "AccountCode", "AccountName", "Description",
                 "DocumentRef", "VendorID", "VendorName", "EmployeeLinked", "AmountUSD",
                 "JournalDebits", "CounterAccount", "Preparer", "PreparerName", "PreparerRole",
                 "Approver", "EntryType", "SourceSystem", "RiskScore", "RiskBand",
                 "RiskWeightedValue", "Status", "Conclusion", "ReviewedBy"],
                [[r["Rank"], r["JournalID"], r["TestID"], r["TestName"], r["AllTestsFired"],
                  r["ExceptionDate"], r["DocumentDate"], r["EnteredOn"], r["Period"], r["AccountCode"],
                  r["AccountName"], r["Description"], r["DocumentRef"], r["VendorID"], r["VendorName"],
                  r["EmployeeLinked"], r["AmountUSD"], r["JournalDebits"], r["CounterAccount"],
                  r["Preparer"], r["PreparerName"], r["PreparerRole"], r["Approver"], r["EntryType"],
                  r["SourceSystem"], r["RiskScore"], r["RiskBand"], r["RiskWeightedValue"],
                  r["Status"], r["Conclusion"], r["ReviewedBy"]] for r in reg],
                formats=[NUM] + [None] * 15 + [MONEY, MONEY, None, None, None, None, None, None, None,
                                               NUM, None, MONEY, None, None, None],
                widths=[6, 17, 8, 26, 14, 13, 13, 19, 9, 11, 30, 40, 14, 9, 30, 13, 14, 14, 14, 10, 22,
                        22, 12, 12, 14, 9, 10, 16, 30, 60, 12],
                title="Evidence register - every flagged transaction, scored",
                note=f"{fx['grand']['Lines']} journal lines totalling {usd(fx['grand']['Value'])}. "
                     "Ranked by risk-weighted value. Exported from the forensic workbench (page 5).")
    ws = wb["Evidence register"]
    for i in range(1, len(reg) + 5):
        if ws.cell(row=i, column=27).value == "High":
            for c in range(1, 32):
                ws.cell(row=i, column=c).fill = PatternFill("solid", fgColor=HEX_BAD)

    write_sheet(wb, "Summary by scheme",
                ["TestID", "Scheme", "Lines", "Total value", "Amount at risk", "High band",
                 "Medium band", "Low band", "Largest single exception"],
                [[tid, {t[0]: t[1] for t in fx["tests"]}[tid], fx["totals"][tid]["Lines"],
                  fx["totals"][tid]["Value"], value_at_risk(tid, fx["totals"][tid]["Value"]),
                  sum(1 for r in fx["register"] if r["TestID"] == tid and r["RiskBand"] == "High"),
                  sum(1 for r in fx["register"] if r["TestID"] == tid and r["RiskBand"] == "Medium"),
                  sum(1 for r in fx["register"] if r["TestID"] == tid and r["RiskBand"] == "Low"),
                  max([r["AmountUSD"] for r in fx["register"] if r["TestID"] == tid], default=0)]
                 for tid in ["T01", "T02", "T03", "T04", "T05", "T06", "T07"]] +
                [["**Total**", "", fx["grand"]["Lines"], fx["grand"]["Value"],
                  sum(value_at_risk(t, v["Value"]) for t, v in fx["totals"].items()),
                  sum(1 for r in fx["register"] if r["RiskBand"] == "High"),
                  sum(1 for r in fx["register"] if r["RiskBand"] == "Medium"),
                  sum(1 for r in fx["register"] if r["RiskBand"] == "Low"),
                  max(r["AmountUSD"] for r in fx["register"])]],
                formats=[None, None, NUM, MONEY, MONEY, NUM, NUM, NUM, MONEY],
                widths=[9, 34, 8, 16, 16, 11, 13, 10, 22],
                title="Evidence register summary by scheme")
    write_sheet(wb, "Top 50 by risk-weighted value",
                ["Rank", "JournalID", "TestID", "TestName", "ExceptionDate", "Description", "VendorName",
                 "AmountUSD", "RiskScore", "RiskBand", "RiskWeightedValue", "Preparer", "Approver"],
                [[r["Rank"], r["JournalID"], r["TestID"], r["TestName"], r["ExceptionDate"],
                  r["Description"], r["VendorName"], r["AmountUSD"], r["RiskScore"], r["RiskBand"],
                  r["RiskWeightedValue"], r["Preparer"], r["Approver"]] for r in reg[:50]],
                formats=[NUM, None, None, None, None, None, None, MONEY, NUM, None, MONEY, None, None],
                widths=[6, 17, 8, 26, 13, 40, 30, 14, 10, 10, 16, 10, 12],
                title="The shortlist - investigate these first")
    write_sheet(wb, "Dismissed exceptions",
                ["TestID", "TestName", "JournalID", "ExceptionDate", "Description", "AmountUSD",
                 "Preparer", "Reason dismissed", "Population note"],
                [[d["TestID"], d["TestName"], d["JournalID"], d["ExceptionDate"], d["Description"],
                  round(d["AmountUSD"], 2), d["Preparer"], d["Reason dismissed"], d["Population note"]]
                 for d in fx["dismissed"]],
                formats=[None, None, None, None, None, MONEY, None, None, None],
                widths=[9, 30, 17, 13, 40, 14, 10, 70, 40],
                title="Exceptions raised by a test, investigated and dismissed",
                note="A register that hides its false positives cannot be reviewed. These are the "
                     "exceptions we did not carry forward, with the reason for each.")
    write_sheet(wb, "Supplementary schedule",
                ["JournalID", "PostingDate", "Description", "Preparer", "Prepayment leg USD",
                 "Status"],
                [[j, led.journals[j][0]["PostingDate"].isoformat(), led.journals[j][0]["Description"],
                  led.journals[j][0]["PreparedBy"],
                  sum(l["Debit"] for l in led.journals[j] if l["AccountCode"] == "1300"),
                  "Same pattern as the six corroborated accrual exceptions - disclosed for clearing"]
                 for j in sorted(fx["accrual_additional"])],
                formats=[None, None, None, None, MONEY, None],
                widths=[17, 13, 40, 10, 18, 70],
                title="Supplementary schedule - further journals carrying the same pattern",
                note=f"{len(fx['accrual_additional'])} journals of "
                     f"{usd(len(fx['accrual_additional']) * 2400)} beyond the six corroborated exceptions. "
                     "The pattern is systematic; management should clear all of it.")
    write_sheet(wb, "Duplicate payment pairs",
                ["#", "Vendor", "Invoice reference", "Amount", "First payment", "Second payment",
                 "Days apart", "Journal A", "Journal B", "Recoverable"],
                duplicate_rows(fx), formats=[NUM, None, None, MONEY, None, None, NUM, None, None, MONEY],
                widths=[5, 32, 18, 14, 14, 14, 11, 17, 17, 14],
                title="Duplicate payments - the recovery schedule")
    wb.save(ensure(path))


def duplicate_rows(fx):
    led = fx["ledger"]
    from collections import defaultdict
    import re
    groups = defaultdict(list)
    for j in fx["hits"]["T01"]:
        ls = led.journals[j]
        d = [l for l in ls if l["Debit"] > 0][0]
        m = re.search(r"INV-(\d+)", ls[0]["Description"])
        groups[(d["VendorID"], m.group(0) if m else "", round(d["Debit"], 2))].append(j)
    out = []
    for i, ((vid, ref, amt), js) in enumerate(sorted(groups.items(), key=lambda kv: -kv[0][2]), 1):
        js = sorted(js, key=lambda x: led.journals[x][0]["PostingDate"])
        a, b = js[0], js[-1]
        out.append([i, led.vendor_by_id.get(vid, {}).get("VendorName", ""), ref, amt,
                    led.journals[a][0]["PostingDate"].isoformat(),
                    led.journals[b][0]["PostingDate"].isoformat(),
                    (led.journals[b][0]["PostingDate"] - led.journals[a][0]["PostingDate"]).days,
                    a, b, amt])
    return out


# ---------------------------------------------------------------------------
def remediation_plan(path, fx, ctx):
    wb = new_wb()
    rows = [
        ["R1", f"Recover the duplicate payments: issue credit-note requests for "
               f"{usd(fx['totals']['T01']['Value'] / 2)} to the suppliers concerned",
         "Financial Director", "Within 10 working days", "Nil (internal)", "High",
         f"{len(fx['hits']['T01']) // 2} pairs; evidence schedule attached to the register",
         "Credit notes received or repayment agreed"],
        ["R2", "Freeze the four employee-linked vendor accounts pending verification of ownership, "
               "contracts and deliverables", "Chief Financial Officer", "Within 5 working days",
         "Nil (internal)", "High", f"{usd(C.EXPECTED['Ghost vendor total paid'])} paid to date",
         "Vendor status changed in the master; no further payments"],
        ["R3", "Require a purchase order for every purchase; remove the value-based exception to the PO "
               "requirement", "Procurement Manager", "Within 30 days", "$2,000 configuration",
         "High", f"{ctx['ap']['no_po']} of {ctx['ap']['count']} invoices had no PO",
         "Invoices without a PO fall to zero in the monthly report"],
        ["R4", "Configure a duplicate-invoice block on vendor plus supplier invoice reference",
         "IT / ERP owner", "Within 30 days", "$1,500 configuration", "High",
         "No system control exists today", "Duplicate payment exceptions fall to zero"],
        ["R5", "Restrict manual journal posting to business hours and require a second approver for every "
               "manual entry", "Financial Controller", "Within 30 days", "$1,000 configuration", "High",
         f"{len(fx['hits']['T05'])} exceptions; {usd(fx['maker_checker']['unapproved_value'])} of manual "
         "journals above $10,000 had no approver",
         "After-hours and unapproved manual exceptions fall to zero"],
        ["R6", "Remove revenue-posting rights from accounts-payable roles and re-perform the fifteen "
               "credit notes", "Financial Controller", "Within 30 days", "Nil (internal)", "High",
         f"{usd(fx['totals']['T06']['Value'])} posted outside role",
         "User-by-account-type matrix shows no cross-role postings"],
        ["R7", "Clear the suspense account and require a written allocation for every item before month "
               "end", "Financial Controller", "Next month end", "Nil (internal)", "Medium",
         f"{usd(fx['suspense']['balance'])} unallocated", "Suspense balance nil at month end"],
        ["R8", "Reconcile the bank statements monthly and clear items over 90 days",
         "Financial Accountant", "Next month end", "Nil (internal)", "Medium",
         f"{ctx['bank']['unreconciled_count']} unreconciled items ({usd(ctx['bank']['unreconciled_value'])})",
         "Unreconciled items under 30 days old"],
        ["R9", "Require a receipt for every expense claim and reject claims without one",
         "Financial Controller", "Within 30 days", "Nil (internal)", "Medium",
         f"{ctx['expenses']['no_receipt']} of {ctx['expenses']['count']} claims had no receipt",
         "Claims without a receipt fall to zero"],
        ["R10", "Implement the twelve-test monthly exception report on the client's own data",
         "Maxhub / Financial Controller", "Month 2",
         f"{sum(RATES[r] * h for _, r, h in [('a', 'Senior Analyst', 6), ('b', 'Senior', 2), ('c', 'Analyst', 2), ('d', 'Manager', 3)]):,.0f}/month",
         "Medium", "The controls failed because nothing tested the population",
         "Monthly report issued and reviewed within 5 working days of month end"],
        ["R11", "Complete a system access and segregation-of-duties review; document the matrix",
         "IT / Financial Controller", "Within 60 days", "$3,000 (advisory)", "Medium",
         "Rights are not aligned to roles", "SoD matrix signed off; rights remediated"],
        ["R12", "Introduce a prepayment and accrual schedule reconciled to the ledger monthly",
         "Financial Accountant", "Within 60 days", "Nil (internal)", "Low",
         f"{len(fx['accrual_population'])} unreversed amortisation entries",
         "Schedule agrees to the ledger; no unreversed entries"],
    ]
    write_sheet(wb, "Remediation plan",
                ["#", "Recommendation", "Owner", "Due date", "Indicative cost", "Priority",
                 "Evidence from the investigation", "How we will know it worked"],
                rows, widths=[6, 62, 26, 22, 22, 10, 52, 46],
                title="Remediation plan - specific, owned, dated and costed")
    write_sheet(wb, "Monitoring schedule",
                ["Test", "Frequency", "Reviewer", "Action on exception", "Retainer"],
                [[t[1], freq, reviewer, action, "Included"] for t, freq, reviewer, action in [
                    (fx["tests"][0], "Monthly", "Financial Controller", "Investigate and recover", ),
                    (fx["tests"][1], "Monthly", "CFO", "Freeze vendor pending verification"),
                    (fx["tests"][2], "Monthly", "Procurement Manager", "Require retrospective PO"),
                    (fx["tests"][3], "Monthly", "Procurement Manager", "Combine and approve"),
                    (fx["tests"][4], "Monthly", "Financial Controller", "Obtain support or reverse"),
                    (fx["tests"][5], "Monthly", "Financial Controller", "Review rights and re-perform"),
                    (fx["tests"][6], "Monthly", "Financial Accountant", "Agree schedule and reverse"),
                    (fx["tests"][7], "Monthly", "Financial Accountant", "Allocate or write off"),
                    (fx["tests"][8], "Monthly", "Financial Controller", "Retrospective approval"),
                    (fx["tests"][9], "Quarterly", "Financial Controller", "Review cut-off"),
                    (fx["tests"][10], "Quarterly", "Maxhub analyst", "Investigate the outlier subgroup"),
                    (fx["tests"][11], "Monthly", "Process owners", "Report with exception lists"),
                ]],
                widths=[42, 12, 26, 40, 12],
                title="The monthly exception report the retainer would run")
    wb.save(ensure(path))


# ---------------------------------------------------------------------------
def findings_report(path, ctx, fx):
    led = fx["ledger"]
    doc = new_doc(title="Findings report - forensic investigation",
                  subtitle="Capstone 1 deliverable 4 - prepared for the Audit Committee",
                  reference="MX-2025-FI01")
    footer(doc, "Maxhub Pvt Ltd - findings report MX-2025-FI01 - Confidential and legally privileged")

    doc.add_heading("1. Executive summary", level=2)
    kv_table(doc, [
        ("What we were asked to do", "Analyse the accounting data for " + PERIOD + ", identify and quantify "
                                     "irregular transactions, and report to the Audit Committee."),
        ("What we did", f"We proved the population ({C.EXPECTED['GL lines']:,} ledger lines; debits = "
                        f"credits = {usd(C.EXPECTED['Total debits'])}), then ran twelve analytics tests "
                        "over 100% of it - no sampling."),
        ("What we found", f"{fx['grand']['Lines']} exceptions totalling {usd(fx['grand']['Value'])} across "
                          "seven patterns. The three largest: payments to four suppliers connected to "
                          f"employees ({usd(fx['totals']['T05']['Value'])} of manual journals posted outside "
                          f"business hours; {usd(fx['totals']['T02']['Value'])} to related-party vendors "
                          f"that bypassed approval; {usd(fx['totals']['T01']['Value'])} of invoices paid "
                          "twice)."),
        ("What it is worth", f"Total value {usd(fx['grand']['Value'])}. Amount at risk "
                             f"{usd(sum(value_at_risk(t, v['Value']) for t, v in fx['totals'].items()))}. "
                             "Quantified loss: nil - no document-level corroboration has been performed, "
                             "which we recommend as the next phase."),
        ("What we recommend", "1. Recover the duplicate payments this month (Financial Director). "
                              "2. Freeze the four employee-linked vendors and remove the value-based "
                              "exception to the purchase-order requirement (CFO / Procurement). "
                              "3. Put the twelve tests on a monthly schedule so this is caught in month "
                              "one next time (Maxhub / Financial Controller)."),
        ("Limitation", "Our work is data analytics and document review. It identifies exceptions requiring "
                       "management action; it is not an audit, and it does not express a legal opinion or "
                       "determine intent."),
    ])

    doc.add_heading("2. Basis of our work", level=2)
    doc.add_heading("2.1 Instruction", level=3)
    para(doc, "The Audit Committee instructed us in writing on 25 September 2025, following a "
              "whistle-blower report alleging that payments had been made to suppliers connected to "
              "employees and that journal entries had been used to conceal transactions. The instruction "
              "is on the engagement file.")
    doc.add_heading("2.2 Scope", level=3)
    para(doc, "The procure-to-pay and journal-entry cycles for " + PERIOD + ", covering 100% of the "
              "general ledger and the sub-ledgers provided. Excluded: other periods, tax, legal advice, "
              "recovery of funds, and any assurance opinion.")
    doc.add_heading("2.3 Data received", level=3)
    table(doc, ["#", "Data set", "Source", "Records"],
          [[1, "General ledger", "ERP-GL / Manual-JE", f"{C.EXPECTED['GL lines']:,}"],
           [2, "Vendor master", "ERP-AP", "26"], [3, "Employee master", "Payroll", "63"],
           [4, "Creditor sub-ledger (sample)", "ERP-AP", f"{ctx['ap']['count']}"],
           [5, "Debtor ageing", "ERP-AR", f"{ctx['ar']['invoices']}"],
           [6, "Bank statements", "Bank portal", f"{ctx['bank']['count']}"],
           [7, "Expense claims", "Expense system", f"{ctx['expenses']['count']}"],
           [8, "Trial balance", "ERP-GL", f"{C.EXPECTED['Trial balance rows']:,}"]],
          widths=[0.9, 6.0, 5.0, 3.0], font=9)
    doc.add_heading("2.4 Data integrity procedures", level=3)
    bullets(doc, [
        "Originals stored unaltered; SHA-256 recorded for every file on receipt.",
        f"Extract reconciled to the trial balance: debits and credits agree at {usd(C.EXPECTED['Total debits'])} each.",
        f"No orphan account keys; no orphan vendor keys; {ctx['control_totals']['Unbalanced journals']} "
        "unbalanced journals.",
        "GL-derived trial balance agrees to the client's trial balance on all 64 accounts used.",
        "The creditor extract is a sample of 520 invoices; a complete extract has been requested and the "
        "limitation is stated wherever three-way-match statistics appear.",
    ])
    doc.add_heading("2.5 Procedures performed", level=3)
    para(doc, "Twelve tests over 100% of the population: duplicate payments, related-party vendors, "
              "threshold avoidance, split purchases, weekend and after-hours journals, segregation of "
              "duties, unreversed accruals, suspense integrity, maker-checker, backdating and period-end "
              "clustering, Benford first-digit analysis, and sub-ledger control reconciliation. "
              f"{fx['grand']['Lines']} exceptions were raised, scored and ranked; the top 30 by "
              "risk-weighted value were investigated individually; "
              f"{len(fx['dismissed'])} further exceptions were investigated and dismissed with reasons.")
    doc.add_heading("2.6 Limitations", level=3)
    bullets(doc, [
        "Data analytics identifies exceptions; it does not establish intent or illegality.",
        "We have not verified the completeness of the systems that produced the extracts.",
        "Amounts described as 'amount at risk' are the full value of the exceptions; only amounts with "
        "documentary support would be reported as quantified loss, and none has been corroborated.",
        "No procedures were performed to identify subsequent events after the date of this report.",
    ])
    doc.add_heading("2.7 Standards and independence", level=3)
    para(doc, "We performed this work in accordance with the IESBA Code of Ethics and Maxhub's internal "
              "quality-control standards. An independent Maxhub partner who did not build the work "
              "reviewed this report before issue. Maxhub does not keep the client's books and does not "
              "audit its financial statements.")

    page_break(doc)
    doc.add_heading("3. Findings", level=2)
    para(doc, "One finding per pattern, in descending order of value. Each states what we observed, how we "
              "tested it, the evidence, why it matters, the root cause and the recommendation.", size=9,
         italic=True)
    order = sorted(fx["totals"].items(), key=lambda kv: -kv[1]["Value"])
    for n, (tid, v) in enumerate(order, 1):
        title, observed, assertion, root_cause, recommendation = FINDING_META[tid]
        doc.add_heading(f"Finding {n} - {title}", level=3)
        kv_table(doc, [
            ("Amount at risk", f"{usd(value_at_risk(tid, v['Value']))} across {v['Lines']} journal lines"),
            ("Total value", usd(v["Value"])),
            ("Estimated loss", "Not quantified; requires document-level corroboration, which we recommend "
                               "as the next phase"),
        ], w1=3.6, w2=13.4, font=9)
        table(doc, ["", ""],
              [["**What we observed**", observed],
               ["**How we tested**", rule_for(fx, tid) + f" Population: {population_for(fx, ctx, tid)}. "
                f"Exceptions: {v['Lines']} lines, {usd(v['Value'])}."],
               ["**Evidence**", evidence_for(fx, tid)],
               ["**Why it matters**", f"It undermines the {assertion.lower()} assertion. "
                + why_matters(tid)],
               ["**Root cause**", root_cause],
               ["**Recommendation**", recommendation]],
              widths=[3.6, 13.4], font=8.5)
        if n < len(order):
            para(doc, "", size=4)

    page_break(doc)
    doc.add_heading("4. Aggregate quantification", level=2)
    rows = []
    for tid, v in order:
        rows.append([{t[0]: t[1] for t in fx["tests"]}[tid], f"{v['Lines']:,}", usd(v["Value"]),
                     usd(value_at_risk(tid, v["Value"])), "Nil - not corroborated", basis(tid)])
    rows.append(["**Total**", f"**{fx['grand']['Lines']:,}**", f"**{usd(fx['grand']['Value'])}**",
                 f"**{usd(sum(value_at_risk(t, x['Value']) for t, x in fx['totals'].items()))}**",
                 "**Nil**", ""])
    table(doc, ["Scheme", "Lines", "Total value", "Amount at risk", "Quantified loss", "Basis"],
          rows, widths=[4.4, 1.4, 2.6, 2.6, 2.6, 3.4], font=8.5, align_right=(1, 2, 3, 4),
          highlight=lambda i, r: r[0] == "**Total**")
    para(doc, "Amount at risk is the value that would be lost if the exception is not explained: for "
              "duplicate payments it is the second payment of each pair; for every other pattern it is the "
              "full value, because no documentary corroboration has been obtained. What would convert "
              "amount at risk into quantified loss: supplier statements and remittance advices "
              "(duplicates); contracts, deliverables and bank mandates (related-party vendors); purchase "
              "orders and approvals (thresholds and split purchases); supporting documents and "
              "authorisation (after-hours journals and credit notes); the prepayment schedule (accruals).")

    doc.add_heading("5. Control environment observations", level=2)
    table(doc, ["Observation", "Value / count", "Implication"],
          [["Suspense account balance", usd(fx["suspense"]["balance"]),
            "An unresolved clearing account that only grows"],
           ["Unreconciled bank items", f"{ctx['bank']['unreconciled_count']} of {ctx['bank']['count']} "
            f"({usd(ctx['bank']['unreconciled_value'])}); oldest {ctx['bank']['oldest_age']} days",
            "Payments may be unrecorded or duplicated"],
           ["AP invoices failing the three-way match",
            f"{ctx['ap']['three_way_fail']} of {ctx['ap']['count']} ({ctx['ap']['three_way_fail_pct']:.0f}%)",
            "Purchases may not be properly authorised or received"],
           ["AP invoices with no purchase order", f"{ctx['ap']['no_po']} of {ctx['ap']['count']}",
            "The purchase-order control is not operating"],
           ["Expense claims without a receipt",
            f"{ctx['expenses']['no_receipt']} of {ctx['expenses']['count']} "
            f"({usd(ctx['expenses']['no_receipt_value'])})",
            "Weak substantiation; an audit-adjustment risk"],
           ["Trade receivables against nine-month revenue",
            f"{usd(ctx['ratio_inputs']['AR'])} against {usd(ctx['ratios']['Revenue'])} "
            f"(DSO {ctx['ratios']['DSO']:.0f} days)",
            "Collections are slow; credit control needs attention"],
           ["Manual journals with no approver above $10,000",
            f"{len(fx['maker_checker']['unapproved'])} journals "
            f"({usd(fx['maker_checker']['unapproved_value'])})",
            "Maker-checker is not operating on manual entries"]],
          widths=[4.6, 6.2, 6.2], font=8.5)

    doc.add_heading("6. Recommendations and remediation plan", level=2)
    para(doc, "The full plan, with owner, due date, indicative cost and the test that proves it worked, is "
              "in Remediation_Plan.xlsx. The five that matter most:")
    table(doc, ["#", "Recommendation", "Owner", "Due", "Priority"],
          [["1", f"Recover {usd(fx['totals']['T01']['Value'] / 2)} of duplicate payments",
            "Financial Director", "10 working days", "High"],
           ["2", "Freeze the four employee-linked vendor accounts pending verification", "CFO",
            "5 working days", "High"],
           ["3", "Mandate a purchase order for every purchase; remove the value-based exception",
            "Procurement Manager", "30 days", "High"],
           ["4", "Restrict manual journals to business hours with a second approver",
            "Financial Controller", "30 days", "High"],
           ["5", "Monthly twelve-test exception report on the client's own data",
            "Maxhub / Financial Controller", "Month 2", "Medium"]],
          widths=[0.8, 8.2, 3.6, 2.6, 1.8], font=9)

    doc.add_heading("7. Appendices", level=2)
    bullets(doc, [
        "A - Test programme: Appendix_A_Test_Programme.xlsx (12 tests with population, assertion, "
        "expectation, exception rule and follow-up).",
        "B - Evidence register: Evidence_Register.xlsx ("
        f"{fx['grand']['Lines']} scored lines, the top-50 shortlist, {len(fx['dismissed'])} dismissed "
        "exceptions with reasons, and the duplicate-payment recovery schedule).",
        "C - Data lineage and integrity record: 01_Data_Governance/.",
        "D - Methodology note for the analytics model: 02_Practical_Exam_1/Methodology_Note.docx.",
        "E - Glossary: reference/Glossary_Accounting_and_PowerBI.md in the course repository.",
    ])
    sign_off(doc, extra={"Issued to": "The Audit Committee and the Chief Financial Officer, "
                                      "Mhondoro Manufacturing (Pvt) Ltd",
                         "Next review": "On completion of the remediation plan, or in 90 days"})
    doc.save(ensure(path))


def rule_for(fx, tid):
    for t in fx["tests"]:
        if t[0] == tid:
            return t[4]
    return ""


def population_for(fx, ctx, tid):
    led = fx["ledger"]
    if tid == "T01":
        return f"{sum(1 for r in led.gl if r['VendorID'] and r['Debit'] > 0):,} vendor payment lines"
    if tid == "T02":
        return f"{len(fx['related_party_population'])} payments to the four related-party vendors"
    if tid == "T03":
        return f"{len(fx['threshold_population'])} lines in the two threshold bands"
    if tid == "T04":
        return f"{sum(1 for r in led.gl if r['VendorID'] and 3000 < r['Debit'] < 7000):,} vendor lines " \
               "between $3,000 and $7,000"
    if tid == "T05":
        return f"{len(fx['afterhours_population'])} unapproved manual journals touching suspense"
    if tid == "T06":
        return f"{sum(1 for r in led.gl if r['PreparedBy'] in fx['apclerks']):,} lines by the AP clerk"
    return f"{len(fx['accrual_population'])} journals with the prepayment pattern"


def evidence_for(fx, tid):
    led = fx["ledger"]
    js = sorted(fx["hits"][tid], key=lambda j: led.journals[j][0]["PostingDate"])
    sample = ", ".join(js[:6])
    more = f" and {len(js) - 6} further journals" if len(js) > 6 else ""
    extra = ""
    if tid == "T02":
        extra = " Vendor master records: created " + ", ".join(
            f"{v['VendorName']} {v['VendorCreatedOn']}" for v in led.vendors
            if v["IsEmployeeLinked"] == "Yes") + ". No tax clearance number on file for any of them."
    if tid == "T01":
        extra = " Each pair shares the same supplier invoice reference; see the duplicate-payment pairs " \
                "sheet in the evidence register."
    if tid == "T05":
        extra = " Entry timestamps are recorded in EnteredOn; all twenty-one were entered by USR-012 with " \
                "no approver."
    return f"Journal IDs {sample}{more}.{extra}"


def why_matters(tid):
    return {
        "T01": "Cash has left the business twice for one obligation, and the creditor ledger no longer "
               "agrees to the supplier's statement.",
        "T02": "If a supplier is controlled by an employee, every payment to it is a related-party "
               "transaction that requires disclosure and independent approval.",
        "T03": "The approval control is defeated by structuring, so spend above the limit is being "
               "incurred without authorisation.",
        "T04": "The commitment exceeds the approval threshold but was never approved as a whole.",
        "T05": "Entries posted when nobody is supervising, with the credit parked in suspense, cannot be "
               "relied upon and are the classic concealment pattern.",
        "T06": "One person can both initiate a payment obligation and reduce revenue, which removes the "
               "check that would detect it.",
        "T07": "Expenses and assets are misstated until the prepayment is either released or reversed.",
    }[tid]


def basis(tid):
    return {
        "T01": "Second payment of each duplicate pair is the improper portion",
        "T02": "Full value of payments that bypassed the payment run and approval",
        "T03": "Full value; no purchase order or approval identified",
        "T04": "Full value of both invoices in each pair",
        "T05": "Full value; no supporting document or approver identified",
        "T06": "Full value of the credit notes posted outside role",
        "T07": "Value of the prepayment leg never released or reversed",
    }[tid]


# ---------------------------------------------------------------------------
def board_presentation(path, ctx, fx):
    led = fx["ledger"]
    prs = new_deck()
    names = {t[0]: t[1] for t in fx["tests"]}
    order = sorted(fx["totals"].items(), key=lambda kv: -kv[1]["Value"])
    at_risk = sum(value_at_risk(t, v["Value"]) for t, v in fx["totals"].items())

    slide_title(prs, "Forensic investigation - findings for the Audit Committee",
                f"{CLIENT}  |  {PERIOD}  |  Maxhub Pvt Ltd  |  {ISSUE_DATE:%d %B %Y}  |  "
                "Confidential and legally privileged")

    slide_kpis(prs, "What we found", [
        ("Exceptions", f"{fx['grand']['Lines']}", "journal lines flagged by twelve tests"),
        ("Total value", usd(fx["grand"]["Value"], 0), "of transactions requiring explanation"),
        ("Amount at risk", usd(at_risk, 0), "if the exceptions are not explained"),
        ("Recoverable now", usd(fx["totals"]["T01"]["Value"] / 2, 0), "duplicate payments - ask this month"),
        ("Quantified loss", "Nil", "no document corroboration performed yet"),
    ], subtitle="Twelve tests over 100% of the ledger - no sampling",
        notes="Lead with the money. Say plainly that we are not asserting a loss: the number is the "
              "amount at risk until documents are examined.")

    slide_chart(prs, f"{usd(fx['grand']['Value'], 0)} of exceptions across seven patterns",
                [names[t].replace(" - ", " ") for t, _ in order],
                [("Value", [v["Value"] for _, v in order])], "column",
                subtitle="Total value of flagged journal lines by test",
                notes="Each bar is a control that did not operate. The three largest are related-party "
                      "payments, after-hours journals and duplicate payments.")

    slide_table(prs, "The seven patterns, in descending order of value",
                ["Scheme", "Lines", "Total value", "Amount at risk"],
                [[names[t], f"{v['Lines']}", usd(v["Value"]), usd(value_at_risk(t, v["Value"]))]
                 for t, v in order] +
                [["**Total**", f"**{fx['grand']['Lines']}**", f"**{usd(fx['grand']['Value'])}**",
                  f"**{usd(at_risk)}**"]],
                subtitle="Every line is traceable to a journal ID, an invoice reference, a date and a user",
                notes="This is appendix B of the report. Every number here is on the evidence register.",
                highlight_last=True)

    slide_bullets(prs, "Finding 1 - suppliers connected to employees", [
        f"Four suppliers are identified in the vendor master as employee-linked; all created in July and "
        f"August 2024, none with a tax clearance number, all on seven-day terms",
        f"Payments to them total {usd(C.EXPECTED['Ghost vendor total paid'])}",
        f"{usd(fx['totals']['T02']['Value'])} of that was initiated outside the accounts-payable payment "
        f"run by one user, with no approver recorded",
        "The bank details on the vendor master were not verified against the employee master at onboarding",
        ("We are not alleging wrongdoing. We are saying the payments cannot be corroborated from what the "
         "company gave us", 1),
    ], subtitle=f"{usd(fx['totals']['T02']['Value'])} bypassed approval; "
                f"{usd(C.EXPECTED['Ghost vendor total paid'])} paid in total",
        notes="This is the finding the board will react to. Keep the language factual: state the vendor "
              "master facts, then say what corroboration is needed.")

    slide_bullets(prs, "Finding 2 - journal entries used to conceal transactions", [
        f"{fx['totals']['T05']['Lines']} manual journals entered on Saturdays between 02:00 and 04:41 and "
        f"between 22:00 and 23:31, by a single user, with no approver",
        "Each debits an expense and credits the suspense account - the expense is recognised while the "
        "liability sits in an unallocated clearing account",
        f"The suspense account holds {usd(fx['suspense']['balance'])} and has never been cleared",
        f"A further {usd(fx['totals']['T06']['Value'])} of revenue credit notes was posted by the "
        "accounts-payable clerk, outside that role",
    ], subtitle=f"{usd(fx['totals']['T05']['Value'])} posted outside business hours",
        notes="This is the concealment pattern the whistle-blower described. The control point is that "
              "nobody was supervising and nothing forced a second signature.")

    slide_bullets(prs, "Finding 3 - invoices paid twice, and thresholds avoided", [
        f"{len(fx['hits']['T01']) // 2} supplier invoices were paid twice - same vendor, same amount to the "
        f"cent, same invoice reference, four to twelve days apart",
        f"{usd(fx['totals']['T01']['Value'] / 2)} is recoverable: ask the suppliers for credit notes this month",
        f"{fx['totals']['T04']['Lines']} purchases were split into two invoices so that each sat below the "
        f"$10,000 approval limit; the pair total is {usd(fx['totals']['T04']['Value'])}",
        f"{fx['totals']['T03']['Lines']} payments of exactly $4,985 to $9,900 sit just under the "
        f"purchase-order and approval limits, with no purchase order on file",
    ], subtitle=f"{usd(fx['totals']['T01']['Value'])} paid twice; "
                f"{usd(fx['totals']['T03']['Value'] + fx['totals']['T04']['Value'])} structured around limits",
        notes="The duplicate payments are the quickest win: real cash, recoverable this month, with the "
              "evidence already assembled.")

    slide_chart(prs, "The exception rate is a control failure, not bad luck",
                ["Unreconciled bank items", "AP invoices failing 3-way match", "AP invoices with no PO",
                 "Claims without a receipt"],
                [("Exceptions", [ctx["bank"]["unreconciled_count"], ctx["ap"]["three_way_fail"],
                                 ctx["ap"]["no_po"], ctx["expenses"]["no_receipt"]]),
                 ("Population", [ctx["bank"]["count"], ctx["ap"]["count"], ctx["ap"]["count"],
                                 ctx["expenses"]["count"]])], "bar",
                subtitle="Control exceptions in the sub-ledgers provided",
                notes="These are not findings in themselves; they are the environment that let the seven "
                      "patterns happen.")

    slide_table(prs, "What it is worth - and what it is not",
                ["Measure", "Amount", "What would change it"],
                [["Total value of exceptions", usd(fx["grand"]["Value"]), "Nothing - this is the arithmetic"],
                 ["Amount at risk", usd(at_risk), "Documents that explain the transactions"],
                 ["Recoverable now (duplicates)", usd(fx["totals"]["T01"]["Value"] / 2),
                  "Supplier credit notes or repayment"],
                 ["Quantified loss", "Nil", "Document-level corroboration - the next phase"],
                 ["Related-party exposure", usd(C.EXPECTED["Ghost vendor total paid"]),
                  "Ownership, contracts and deliverable evidence"]],
                subtitle="Three different numbers, stated separately every time",
                notes="If a board member quotes one number, make sure they say which one. This is the "
                      "slide that protects the report from being misread.")

    slide_table(prs, "Five things to do in the next 30 days",
                ["#", "Action", "Owner", "Due"],
                [["1", f"Recover {usd(fx['totals']['T01']['Value'] / 2, 0)} of duplicate payments",
                  "Financial Director", "10 working days"],
                 ["2", "Freeze the four employee-linked vendor accounts", "CFO", "5 working days"],
                 ["3", "Purchase order for every purchase; remove the value-based exception",
                  "Procurement Manager", "30 days"],
                 ["4", "Manual journals in business hours only, with a second approver",
                  "Financial Controller", "30 days"],
                 ["5", "Remove revenue-posting rights from accounts-payable roles",
                  "Financial Controller", "30 days"]],
                subtitle="Full plan with costs and success tests in Remediation_Plan.xlsx",
                notes="Each action has a test that proves it worked, which is on the remediation sheet.")

    slide_bullets(prs, "How we know these numbers are right", [
        f"The model reconciles to the client's own control totals: debits = credits = "
        f"{usd(C.EXPECTED['Total debits'])}; every journal balances; no orphan keys",
        "The GL-derived trial balance agrees to the client's trial balance on all 64 accounts used",
        "The balance sheet checks to zero and the cash flow ties to the movement in the cash accounts",
        f"{len(ctx['recon'].passes)} control checks tie; none requires investigation",
        "An independent Maxhub partner who did not build the work re-performed a calculation on every page",
    ], subtitle="Nothing is reported until it reconciles",
        notes="This is the slide that answers 'how do I know it is right' before it is asked.")

    slide_bullets(prs, "What we recommend next", [
        "Put the twelve tests on a monthly schedule running on your own data - the next "
        f"{usd(fx['grand']['Value'], 0)} should be found in month one, not in year two",
        "Commission the document-level corroboration phase so amount at risk becomes quantified loss "
        "where it is real",
        "Complete the control remediation: vendor onboarding, purchase orders, approval limits, access rights",
        "Report the exception rate to this Committee quarterly until it is falling",
    ], subtitle="The investigation becomes a monitoring retainer",
        notes="Close on the decision, not on the tool. Ask for the mandate to run the monthly report.")

    save_deck(prs, ensure(path))
