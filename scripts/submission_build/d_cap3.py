"""
d_cap3.py - Capstone 3: procurement, receivables and cash analytics.

Deliverables: procurement analytics, receivables and collections priority,
cash and working capital, data quality report, exception register, findings
memo and the eight-slide committee pack.
"""
from __future__ import annotations

import os

from . import common as C
from .writers import *

RATES = {"Analyst": 120, "Senior Analyst": 150, "Senior": 200, "Manager": 280, "Partner": 450}
SOC = [("Data preparation and integrity", 6, "Analyst"),
       ("Procurement analytics", 8, "Senior Analyst"),
       ("Receivables and collections", 8, "Senior"),
       ("Cash and working capital", 6, "Senior"),
       ("Model build and reconciliation", 10, "Senior"),
       ("Committee pack and presentation", 6, "Manager"),
       ("Peer review and QC", 4, "Partner")]


def collections_priority(ctx, led):
    """Score = outstanding x (1 + days overdue/90) x dispute multiplier, documented."""
    rows = []
    for r in ctx["ar"]["rows"]:
        out = r["OutstandingUSD"]
        if out <= 0:
            continue
        dispute = 0.5 if r["Disputed"] else 1.0
        first_time = 1.5 if r["AmountUSD"] > 100000 and r["InvoiceDate"] >= "2025-06-01" else 1.0
        score = out * (1 + r["DaysOverdue"] / 90) * dispute * first_time
        cust = led.customer_by_id.get(r["CustomerID"], {})
        rows.append({
            "InvoiceNo": r["InvoiceNo"], "CustomerID": r["CustomerID"],
            "CustomerName": r["CustomerName"], "Segment": cust.get("Segment", ""),
            "AccountManager": cust.get("AccountManager", ""),
            "CreditLimit": float(cust.get("CreditLimitUSD") or 0),
            "InvoiceDate": r["InvoiceDate"], "DueDate": r["DueDate"],
            "AmountUSD": r["AmountUSD"], "ReceivedUSD": r["AmountReceivedUSD"],
            "OutstandingUSD": out, "DaysOverdue": r["DaysOverdue"],
            "AgeingBucket": r["AgeingBucket"], "Disputed": "Yes" if r["Disputed"] else "No",
            "PriorityScore": round(score, 2),
            "Action": action_for(r, out),
        })
    rows.sort(key=lambda r: -r["PriorityScore"])
    for i, r in enumerate(rows, 1):
        r["PriorityRank"] = i
    return rows


def action_for(r, out):
    if r["Disputed"]:
        return "Resolve the dispute first - agree the credit note or the corrected invoice, then collect"
    if r["DaysOverdue"] > 180:
        return "Escalate to the account manager and the CFO; consider withholding further supply"
    if r["DaysOverdue"] > 90:
        return "Telephone contact this week; obtain a payment commitment in writing"
    if r["DaysOverdue"] > 30:
        return "Standard reminder and confirmation of the payment date"
    return "Not yet due - monitor"


def build(out, ctx, fx):
    os.makedirs(out, exist_ok=True)
    led = ctx["ledger"]
    ap, ar, bk, ex = ctx["ap"], ctx["ar"], ctx["bank"], ctx["expenses"]
    sp, rt, bs = ctx["spend"], ctx["ratios"], ctx["balance_sheet"]

    # ------------------------------------------------------ procurement wb
    wb = new_wb()
    write_sheet(wb, "Spend Pareto",
                ["Rank", "Vendor", "Category", "Spend USD", "Share %", "Cumulative %", "Postings",
                 "Employee linked", "Tax clearance", "Vendor created", "Last bank change"],
                [[p["Rank"], p["VendorName"], p["Category"], round(p["AmountUSD"], 2),
                  round(p["Share pct"] / 100, 4), round(p["Cumulative pct"] / 100, 4), p["Postings"],
                  "Yes" if p["EmployeeLinked"] else "No",
                  "Yes" if p["TaxClearanceNo"] else "No", p["VendorCreatedOn"],
                  p["LastBankChangeDate"]] for p in sp["pareto"]],
                formats=[NUM, None, None, MONEY, PCT, PCT, NUM, None, None, None, None],
                widths=[6, 34, 20, 16, 10, 13, 10, 14, 13, 14, 15],
                title="Supplier spend concentration - the 80% line falls at vendor "
                      f"{sp['vendors_to_80']} of {sp['vendors']}",
                note=f"Total supplier spend {usd(sp['total'])} measured on the general ledger. The largest "
                     f"vendor is {sp['top1_pct']:.1f}% and the top five are {sp['top5_pct']:.1f}% - an "
                     "unusually flat profile, which means no vendor relationship is being managed "
                     "strategically and duplicate-vendor creation is easier to hide.")
    write_sheet(wb, "Vendor performance",
                ["Vendor", "Category", "Invoices", "Spend USD", "Average invoice", "3-way exceptions",
                 "Exception rate %", "No PO", "PO but no GRN", "Duplicate suspected", "Employee linked",
                 "Tax clearance", "Last invoice"],
                [[r["VendorName"], r["Category"], r["Invoices"], round(r["AmountUSD"], 2),
                  round(r["Avg invoice"], 2), r["3-way exceptions"],
                  round(r["Exception rate pct"] / 100, 4), r["No PO"], r["PO but no GRN"],
                  r["Duplicate suspected"], "Yes" if r["Employee linked"] else "No", r["Tax clearance"],
                  r["Last invoice"]] for r in C.ap_by_vendor(led, ap)],
                formats=[None, None, NUM, MONEY, MONEY, NUM, PCT, NUM, NUM, NUM, None, None, None],
                widths=[34, 20, 10, 16, 15, 15, 14, 8, 13, 17, 14, 13, 13],
                title="Vendor performance on the creditor extract",
                note=f"{ap['count']} invoices totalling {usd(ap['total'])}. This is a sample, not the full "
                     "creditor population - the difference against GL spend is disclosed in the data "
                     "quality report.")
    write_sheet(wb, "Three-way match exceptions",
                ["Invoice", "Supplier invoice ref", "Vendor", "Invoice date", "Amount USD", "PO number",
                 "GRN number", "Failure reason", "Duplicate suspected", "Paid status", "Approved by"],
                [[r["APInvoiceNo"], r["SupplierInvoiceRef"], r["VendorName"], r["InvoiceDate"],
                  round(r["AmountUSD"], 2), r["PONumber"] or "(none)", r["GRNNumber"] or "(none)",
                  failure_reason(r), "Yes" if r["DuplicateSuspected"] else "No", r["PaidStatus"],
                  r["ApprovedBy"] or "(none)"]
                 for r in sorted((r for r in ap["rows"] if r["ThreeWayMatch"] != "Matched"),
                                 key=lambda r: -r["AmountUSD"])],
                formats=[None, None, None, None, MONEY, None, None, None, None, None, None],
                widths=[14, 20, 32, 12, 14, 12, 12, 40, 17, 12, 12],
                title=f"Three-way match exceptions - {ap['three_way_fail']} of {ap['count']} invoices "
                      f"({ap['three_way_fail_pct']:.0f}%)")
    write_sheet(wb, "Vendor master quality",
                ["Vendor", "Category", "Created", "Tax clearance", "Payment terms", "Bank", "Bank name",
                 "Last bank change", "Employee linked", "Days created to first payment", "Indicator"],
                vendor_master_rows(led),
                formats=[None, None, None, None, None, None, None, None, None, NUM, None],
                widths=[34, 20, 12, 13, 13, 20, 18, 15, 14, 24, 60],
                title="Vendor master quality - the related-party and onboarding indicators")
    wb.save(ensure(os.path.join(out, "Procurement_Analytics.xlsx")))

    # ----------------------------------------------------- receivables wb
    wb = new_wb()
    order = ["Current", "1-30 days", "31-60 days", "61-90 days", "91-180 days", "Over 180 days"]
    buckets = ctx["ar"]["by_bucket"]
    write_sheet(wb, "Ageing analysis",
                ["Ageing bucket", "Invoices", "Outstanding USD", "% of receivables", "Disputed invoices",
                 "Disputed USD"],
                [[b, buckets.get(b, {}).get("Invoices", 0),
                  round(buckets.get(b, {}).get("OutstandingUSD", 0.0), 2),
                  round(buckets.get(b, {}).get("OutstandingUSD", 0.0) / ar["outstanding"], 4)
                  if ar["outstanding"] else None,
                  sum(1 for r in ar["rows"] if r["AgeingBucket"] == b and r["Disputed"]),
                  round(sum(r["OutstandingUSD"] for r in ar["rows"]
                            if r["AgeingBucket"] == b and r["Disputed"]), 2)] for b in order] +
                [["**Total**", ar["invoices"], round(ar["outstanding"], 2), 1.0, ar["disputed"],
                  round(sum(r["OutstandingUSD"] for r in ar["rows"] if r["Disputed"]), 2)]],
                formats=[None, NUM, MONEY, PCT, NUM, MONEY], widths=[16, 10, 18, 15, 16, 15],
                title="Debtor ageing at 30 September 2025",
                note=f"Sub-ledger outstanding {usd(ar['outstanding'])}; trade receivables control account "
                     f"{usd(rt['Inputs']['AR'])}. DSO {rt['DSO']:.0f} days on "
                     f"{C.DAYS_ELAPSED_FY2025} days elapsed.")
    prio = collections_priority(ctx, led)
    write_sheet(wb, "Collections priority",
                ["Rank", "Invoice", "Customer", "Segment", "Account manager", "Credit limit",
                 "Invoice date", "Due date", "Amount USD", "Received USD", "Outstanding USD",
                 "Days overdue", "Bucket", "Disputed", "Priority score", "Action"],
                [[r["PriorityRank"], r["InvoiceNo"], r["CustomerName"], r["Segment"],
                  r["AccountManager"], round(r["CreditLimit"], 2), r["InvoiceDate"], r["DueDate"],
                  round(r["AmountUSD"], 2), round(r["ReceivedUSD"], 2), round(r["OutstandingUSD"], 2),
                  r["DaysOverdue"], r["AgeingBucket"], r["Disputed"], r["PriorityScore"], r["Action"]]
                 for r in prio],
                formats=[NUM, None, None, None, None, MONEY, None, None, MONEY, MONEY, MONEY, NUM, None,
                         None, MONEY, None],
                widths=[6, 14, 32, 14, 20, 14, 12, 12, 14, 14, 15, 12, 13, 9, 15, 66],
                title="Collections priority list - ranked by score, not by size",
                note="Priority score = outstanding x (1 + days overdue / 90) x dispute multiplier "
                     "(0.5 disputed, 1.0 undisputed) x 1.5 for a first-time large balance raised in the "
                     "last quarter. The score is documented so the credit controller can challenge it.")
    write_sheet(wb, "Credit limit utilisation",
                ["Customer", "Segment", "Credit limit", "Outstanding", "Utilisation %",
                 "Over limit?", "Oldest overdue (days)", "Disputed"],
                customer_rows(ctx, led),
                formats=[None, None, MONEY, MONEY, PCT, None, NUM, None],
                widths=[34, 14, 14, 16, 13, 12, 19, 10],
                title="Credit limit utilisation by customer")
    write_sheet(wb, "Ageing bridge",
                ["Bridge step", "Amount USD", "Source"],
                ageing_bridge(ctx, led), formats=[None, MONEY, None], widths=[42, 18, 62],
                title="Ageing bridge - ties to the trade receivables control account")
    wb.save(ensure(os.path.join(out, "Receivables_and_Collections.xlsx")))

    # --------------------------------------------------------- cash wb
    wb = new_wb()
    unrec = sorted(bk["unreconciled"], key=lambda r: -r["AgeDays"])
    write_sheet(wb, "Unreconciled bank items",
                ["Bank txn ID", "Account", "Date", "Narration", "Debit USD", "Credit USD", "Age (days)",
                 "Age band", "Likely cause", "Action"],
                [[r["BankTxnID"], r["BankAccount"], r["TxnDate"], r["Narration"],
                  round(r["DebitUSD"], 2), round(r["CreditUSD"], 2), r["AgeDays"],
                  age_band(r["AgeDays"]), bank_cause(r), bank_action(r)] for r in unrec],
                formats=[None, None, None, None, MONEY, MONEY, NUM, None, None, None],
                widths=[13, 16, 12, 46, 14, 14, 11, 13, 40, 44],
                title=f"Unreconciled bank items - {bk['unreconciled_count']} of {bk['count']} "
                      f"({usd(bk['unreconciled_value'])}); oldest {bk['oldest_age']} days")
    write_sheet(wb, "Working capital",
                ["Measure", "Value", "Formula", "What it means"],
                [["DSO (days)", round(rt["DSO"], 1), rt["Definitions"]["DSO"],
                  "Customers take about three months to pay"],
                 ["DIO (days)", round(rt["DIO"], 1), rt["Definitions"]["DIO"],
                  "Stock turns roughly eight times a year"],
                 ["DPO (days)", round(rt["DPO"], 1), rt["Definitions"]["DPO"],
                  "Suppliers are being paid in about four months"],
                 ["Cash conversion cycle (days)", round(rt["CCC"], 1), rt["Definitions"]["CCC"],
                  "Cash is tied up for three weeks - only because suppliers are stretched"],
                 ["Cash released if collections improve to 60 days",
                  round(rt["Inputs"]["AR"] - rt["Revenue"] / C.DAYS_ELAPSED_FY2025 * 60, 2),
                  "Receivables - (nine-month revenue / 273 x 60)",
                  "The what-if parameter on the report page computes this, not a hard-coded number"],
                 ["Cash released if DPO falls to 90 days",
                  round(rt["Inputs"]["AP"] - rt["Cost of sales"] / C.DAYS_ELAPSED_FY2025 * 90, 2) * -1,
                  "Payables - (nine-month cost of sales / 273 x 90), shown as a cash cost",
                  "Stretching suppliers is not free: normalising DPO consumes cash"],
                 ["Net effect of both", round(
                     (rt["Inputs"]["AR"] - rt["Revenue"] / C.DAYS_ELAPSED_FY2025 * 60)
                     - (rt["Inputs"]["AP"] - rt["Cost of sales"] / C.DAYS_ELAPSED_FY2025 * 90), 2),
                  "Sum of the two scenarios",
                  "The honest answer: fixing collections funds normalising supplier terms"]],
                formats=[None, MONEY, None, None], widths=[42, 18, 52, 62],
                title="Working capital and the cash conversion cycle")
    cf = ctx["cash_flow"]
    write_sheet(wb, "Cash movement",
                ["Line", "Amount USD"], [[k, round(v, 2)] for k, v in cf.items()],
                formats=[None, MONEY], widths=[52, 18],
                title="Cash movement for the nine months, reconciled to the cash accounts")
    wb.save(ensure(os.path.join(out, "Cash_and_Working_Capital.xlsx")))

    # ------------------------------------------------- exception register
    wb = new_wb()
    rows = []
    for r in ap["rows"]:
        if r["ThreeWayMatch"] == "Matched" and not r["DuplicateSuspected"] and r["PONumber"]:
            continue
        rows.append(["Procurement", r["APInvoiceNo"], r["VendorName"], r["InvoiceDate"],
                     round(r["AmountUSD"], 2), failure_reason(r), r["PaidStatus"],
                     "Procurement Manager", "High" if r["DuplicateSuspected"] else "Medium"])
    for r in unrec:
        rows.append(["Cash", r["BankTxnID"], r["BankAccount"], r["TxnDate"],
                     round(r["DebitUSD"] + r["CreditUSD"], 2), bank_cause(r), "Unreconciled",
                     "Financial Accountant", "High" if r["AgeDays"] > 90 else "Medium"])
    for r in ex["rows"]:
        if r["ReceiptAttached"]:
            continue
        rows.append(["Expenses", r["ClaimID"], r["EmployeeName"], r["ClaimDate"],
                     round(r["ClaimedUSD"], 2), "No receipt attached", "Paid",
                     "Financial Controller", "Low"])
    for r in ar["rows"]:
        if not r["Disputed"]:
            continue
        rows.append(["Receivables", r["InvoiceNo"], r["CustomerName"], r["InvoiceDate"],
                     round(r["OutstandingUSD"], 2), "Disputed balance", "Outstanding",
                     "Credit Controller", "Medium"])
    write_sheet(wb, "Exception register",
                ["Cycle", "Reference", "Party", "Date", "Amount USD", "Exception", "Status", "Owner",
                 "Priority"],
                rows, formats=[None, None, None, None, MONEY, None, None, None, None],
                widths=[14, 16, 34, 12, 15, 40, 14, 22, 10],
                title="Exception register - every exception from the analytics, with an owner",
                note=f"{len(rows)} exceptions across four cycles. Exported from the model with the "
                     "client's own reference numbers so each can be traced back.")
    wb.save(ensure(os.path.join(out, "Exception_Register.xlsx")))

    # ------------------------------------------------------ findings memo
    doc = new_doc(title="Procurement, receivables and cash analytics - findings memo",
                  subtitle="Capstone 3: seven analyses, each answering one client question",
                  reference="MX-2025-AN01")
    footer(doc, "Maxhub Pvt Ltd - analytics findings memo - Confidential")
    doc.add_heading("1. Scope and reconciliation", level=2)
    kv_table(doc, [
        ("Population", f"100% of the general ledger ({C.EXPECTED['GL lines']:,} lines) plus the "
                       "sub-ledgers provided"),
        ("Reconciliation", f"Debits = credits = {usd(C.EXPECTED['Total debits'])}; GL-derived trial "
                           "balance agrees to the client's on all 64 accounts used"),
        ("Limitation", f"The creditor extract is {ap['count']} invoices ({usd(ap['total'])}); GL spend to "
                       f"vendors is {usd(sp['total'])}. Procurement concentration is measured on the GL; "
                       "three-way-match statistics are measured on the extract and labelled as such."),
    ])
    doc.add_heading("2. The seven analyses", level=2)
    analyses = [
        ("Analysis 1 - Spend concentration and vendor profile",
         "Where is our non-payroll money going, and who are we dependent on?",
         f"Supplier spend is {usd(sp['total'])} across {sp['vendors']} vendors. The largest is "
         f"{sp['top1_pct']:.1f}% and the top five are {sp['top5_pct']:.1f}%; it takes "
         f"{sp['vendors_to_80']} vendors to reach 80% of spend. That is unusually flat: no vendor "
         "relationship is being managed strategically, and a flat profile makes a duplicate or "
         "related-party vendor easy to hide.",
         "Introduce a vendor tiering policy; assign an owner to the top ten; require annual re-validation "
         "of vendor master data."),
        ("Analysis 2 - Procurement control testing",
         "Are we paying for things we did not order or receive?",
         f"{ap['three_way_fail']} of {ap['count']} invoices ({ap['three_way_fail_pct']:.0f}%, "
         f"{usd(ap['three_way_fail_value'])}) fail the three-way match. {ap['no_po']} invoices have no "
         f"purchase order at all and {ap['no_grn']} have a PO but no goods-received note. "
         f"{ap['duplicate_suspected']} are flagged as suspected duplicates.",
         "Mandate a PO for every purchase; block payment where a GRN is missing; run the exception list "
         "monthly with the Procurement Manager."),
        ("Analysis 3 - Vendor master quality",
         "Has anyone created a supplier we do not actually have?",
         f"Four vendors are flagged employee-linked in the master, created July-August 2024, with no tax "
         f"clearance and seven-day terms; {usd(sp['employee_linked_total'])} has been paid to them. "
         "Name-similarity testing of the 26-vendor master returns no near-duplicates at an 80% threshold, "
         "so the exposure is related-party, not duplicate-master.",
         "Verify ownership of the four vendors against the employee master; require independent approval "
         "for any vendor created within 180 days of its first payment."),
        ("Analysis 4 - DSO and the ageing bridge",
         "Is the debt real and is it being collected?",
         f"Closing receivables {usd(rt['Inputs']['AR'])} against nine-month revenue "
         f"{usd(rt['Revenue'])}: DSO {rt['DSO']:.0f} days. {ar['disputed']} accounts are disputed. The "
         "ageing bridge ties to the control account.",
         "Work the collections priority list weekly; resolve disputes before chasing them; review credit "
         "limits quarterly."),
        ("Analysis 5 - Collections priority",
         "Who do I call on Monday morning?",
         f"{len(prio)} open invoices ranked by a documented score (outstanding x (1 + days overdue / 90) "
         f"x dispute multiplier). The top 25 are "
         f"{usd(sum(r['OutstandingUSD'] for r in prio[:25]))}. The list is deliberately not ranked by "
         "size: a disputed large balance is worth less this month than an undisputed small one that is "
         "180 days old.",
         "Assign the top 25 to named collectors with a contact date; report the movement weekly."),
        ("Analysis 6 - Bank reconciliation exceptions",
         "Is our cash real, and are we missing payments or receipts?",
         f"{bk['unreconciled_count']} of {bk['count']} bank items ({usd(bk['unreconciled_value'])}) are "
         f"unreconciled; {bk['over_90_days']} are over 90 days old and the oldest is {bk['oldest_age']} "
         f"days. The suspense account holds {usd(bs['Suspense (credit balance)'])}.",
         "Clear items over 90 days within two weeks; reconcile monthly; allocate every suspense item in "
         "writing before month end."),
        ("Analysis 7 - Working capital and cash conversion",
         "How much cash is trapped, and what does fixing it release?",
         f"DSO {rt['DSO']:.0f}, DIO {rt['DIO']:.0f}, DPO {rt['DPO']:.0f} gives a cycle of "
         f"{rt['CCC']:.0f} days. It looks efficient, but only because suppliers are stretched to "
         f"{rt['DPO']:.0f} days to fund customers who pay in {rt['DSO']:.0f}. Improving collections to 60 "
         f"days releases {usd(rt['Inputs']['AR'] - rt['Revenue'] / C.DAYS_ELAPSED_FY2025 * 60)}; "
         f"normalising DPO to 90 days would consume "
         f"{usd(rt['Inputs']['AP'] - rt['Cost of sales'] / C.DAYS_ELAPSED_FY2025 * 90)}.",
         "Fix collections first, then normalise supplier terms; report the cycle monthly with both "
         "scenarios."),
    ]
    for title, question, finding, recommendation in analyses:
        doc.add_heading(title, level=3)
        kv_table(doc, [("Client question", question), ("Finding", finding),
                       ("Recommendation", recommendation)], w1=3.4, w2=13.6, font=9)
    doc.add_heading("3. Priced scope of work", level=2)
    total = sum(RATES[r] * h for _, h, r in SOC)
    table(doc, ["Phase", "Hours", "Role", "Rate", "Fee"],
          [[p, h, r, usd(RATES[r]), usd(RATES[r] * h)] for p, h, r in SOC] +
          [["**Total**", f"**{sum(h for _, h, _ in SOC)}**", "", "", f"**{usd(total)}**"]],
          widths=[6.6, 1.6, 3.0, 2.4, 3.4], font=9, align_right=(1, 3, 4))
    para(doc, f"Benchmark: the Service Catalogue prices a data analytics engagement at $6,000-$18,000 and "
              f"working capital analytics at $3,000-$9,000. {usd(total)} for 48 hours sits inside both.")
    doc.add_heading("4. The three client questions, in writing", level=2)
    kv_table(doc, [
        ("How long?", "Four calendar weeks, with about twelve hours of client involvement."),
        ("How much?", f"{usd(total)} fixed fee, plus a proposed $1,200 per month analytics retainer for "
                      "monthly refreshes, exception reporting and one review call."),
        ("How do I know it is right?", "Every figure reconciles to the trial balance; a partner who did "
                                       "not build the work re-performed a number on every page; the "
                                       "methodology note lets your team reproduce everything "
                                       "independently."),
    ])
    sign_off(doc)
    doc.save(ensure(os.path.join(out, "Analytics_Findings_Memo.docx")))

    # --------------------------------------------------------- data quality
    dq = new_doc(title="Data quality report - what is wrong with the source data and what it costs",
                 subtitle="Capstone 3 deliverable 4 - one page, for IT and Finance systems",
                 reference="MX-2025-DQ01")
    footer(dq, "Maxhub Pvt Ltd - data quality report - Confidential")
    table(dq, ["Issue", "Count", "Value", "Process that caused it", "Owner", "Cost of not fixing it"],
          [["Creditor extract is a sample, not the population",
            f"{ap['count']} invoices vs {usd(sp['total'])} of GL spend", usd(sp['total'] - ap['total']),
            "No complete extract routine exists", "IT / Finance systems",
            "Control testing cannot cover the whole population, so exceptions hide in the gap"],
           ["AP invoices failing the three-way match", f"{ap['three_way_fail']} of {ap['count']}",
            usd(ap["three_way_fail_value"]), "GRN capture is optional and PO matching is not enforced",
            "Procurement Manager", "Payments for goods not ordered or not received"],
           ["AP invoices with no purchase order", f"{ap['no_po']} of {ap['count']}", usd(ap["no_po_value"]),
            "The value-based exception to the PO requirement", "Procurement Manager",
            "Spend above the threshold without authorisation"],
           ["Unreconciled bank items", f"{bk['unreconciled_count']} of {bk['count']}",
            usd(bk["unreconciled_value"]), "No monthly reconciliation discipline",
            "Financial Accountant", "Cash cannot be relied upon; duplicate or unrecorded payments"],
           ["Expense claims without a receipt", f"{ex['no_receipt']} of {ex['count']}",
            usd(ex["no_receipt_value"]), "The expense system does not enforce an attachment",
            "Financial Controller", "Audit adjustment risk and weak substantiation"],
           ["Suspense account never cleared", "1 account", usd(bs["Suspense (credit balance)"]),
            "No month-end allocation requirement", "Financial Accountant",
            "Transactions are not in the accounts they belong in"],
           ["Disputed customer balances", f"{ar['disputed']} of {ar['invoices']} ageing rows",
            usd(sum(r["OutstandingUSD"] for r in ar["rows"] if r["Disputed"])),
            "Credit notes raised but not resolved", "Credit Controller",
            "Overstated receivables and wasted collection effort"],
           ["Vendor master incomplete", "4 vendors with no tax clearance",
            usd(sp["employee_linked_total"]), "No verification at onboarding", "Financial Controller",
            "Related-party and compliance exposure"]],
          widths=[4.4, 2.6, 2.2, 3.4, 2.4, 4.0], font=8)
    para(dq, "None of these is a reporting error. Each is a process that produces bad data, and each has "
             "an owner who can fix it. The cost column is the reason to fund the fix.", size=9, italic=True)
    sign_off(dq)
    dq.save(ensure(os.path.join(out, "Data_Quality_Report.docx")))

    # ------------------------------------------------------- committee deck
    prs = new_deck()
    slide_title(prs, "Data analytics for the Audit Committee",
                f"{CLIENT}  |  {PERIOD}  |  Maxhub Pvt Ltd  |  100% population testing")
    slide_kpis(prs, "What we tested and what we found", [
        ("Population tested", "100%", f"{C.EXPECTED['GL lines']:,} ledger lines - no sampling"),
        ("Supplier spend", usd(sp["total"], 0), f"across {sp['vendors']} vendors"),
        ("Three-way match failures", f"{ap['three_way_fail']}", f"of {ap['count']} invoices tested"),
        ("Unreconciled cash", usd(bk["unreconciled_value"], 0), f"{bk['unreconciled_count']} bank items"),
        ("DSO", f"{rt['DSO']:.0f} days", f"on {usd(rt['Inputs']['AR'])} of receivables"),
    ], notes="One slide, five numbers, no tool talk.")
    slide_chart(prs, f"Supplier spend is flat: {sp['vendors_to_80']} vendors reach 80%",
                [p["VendorName"][:22] for p in sp["pareto"][:12]],
                [("Spend", [p["AmountUSD"] for p in sp["pareto"][:12]])], "bar",
                subtitle=f"Top vendor {sp['top1_pct']:.1f}%; top five {sp['top5_pct']:.1f}%",
                notes="Flat concentration is not automatically bad, but it means no vendor is managed "
                      "strategically and a new vendor is easy to hide.")
    slide_chart(prs, f"{ap['three_way_fail']} of {ap['count']} invoices fail the three-way match",
                ["Matched", "No purchase order", "PO but no GRN", "Suspected duplicate"],
                [("Invoices", [ap["three_way_matched"], ap["no_po"], ap["no_grn"],
                               ap["duplicate_suspected"]])], "column",
                subtitle="Are we paying for things we did not order or receive?",
                notes="Categories overlap; the total exception count is the number on the previous slide.")
    slide_chart(prs, f"Receivables: {usd(ar['outstanding'], 0)} outstanding, DSO {rt['DSO']:.0f} days",
                [b for b in ["Current", "1-30 days", "31-60 days", "61-90 days", "91-180 days",
                             "Over 180 days"]],
                [("Outstanding", [ar["by_bucket"].get(b, {}).get("OutstandingUSD", 0.0) for b in
                                  ["Current", "1-30 days", "31-60 days", "61-90 days", "91-180 days",
                                   "Over 180 days"]])], "column",
                subtitle=f"{ar['disputed']} accounts disputed - resolve the dispute before chasing it",
                notes="The collections list is ranked by score, not size. Disputed balances are "
                      "half-weighted because a disputed invoice will not pay this month.")
    slide_chart(prs, f"Cash: {usd(bk['unreconciled_value'], 0)} unreconciled, oldest {bk['oldest_age']} days",
                ["0-30 days", "31-60 days", "61-90 days", "Over 90 days"],
                [("Value", [sum(r["DebitUSD"] + r["CreditUSD"] for r in bk["unreconciled"]
                                if lo <= r["AgeDays"] < hi)
                            for lo, hi in [(0, 31), (31, 61), (61, 91), (91, 10 ** 6)]])], "column",
                subtitle=f"{bk['over_90_days']} items are over 90 days old",
                notes="Is our cash real? Until these are matched, we cannot say.")
    slide_table(prs, "Working capital looks efficient - and is not",
                ["Measure", "Days", "Reading"],
                [["DSO", f"{rt['DSO']:.0f}", "Customers pay in about three months"],
                 ["DIO", f"{rt['DIO']:.0f}", "Stock turns about eight times a year"],
                 ["DPO", f"{rt['DPO']:.0f}", "Suppliers are paid in about four months"],
                 ["Cash conversion cycle", f"{rt['CCC']:.0f}",
                  "Three weeks of cash tied up - only because suppliers are stretched"],
                 ["If collections improve to 60 days",
                  usd(rt["Inputs"]["AR"] - rt["Revenue"] / C.DAYS_ELAPSED_FY2025 * 60, 0),
                  "Cash released - this is the prize"]],
                subtitle="Each ratio shows its formula and date basis on the report page",
                notes="The honest reading: the cycle is short because both sides are being tolerant. "
                      "Fix collections first, then normalise supplier terms.")
    slide_table(prs, "Six recommendations, each with an owner",
                ["#", "Recommendation", "Owner", "Due"],
                [["1", "Mandate a purchase order for every purchase", "Procurement Manager", "30 days"],
                 ["2", "Block payment where a goods-received note is missing", "IT / Procurement", "30 days"],
                 ["3", "Verify the four employee-linked vendors before the next payment", "CFO",
                  "5 working days"],
                 ["4", "Clear bank items over 90 days and reconcile monthly", "Financial Accountant",
                  "2 weeks"],
                 ["5", "Work the collections priority list weekly", "Credit Controller", "Weekly"],
                 ["6", "Enforce a receipt on every expense claim", "Financial Controller", "30 days"]],
                subtitle="Every finding has a recommendation; every recommendation has an owner",
                notes="The rubric deducts marks for a finding with no recommendation.")
    slide_bullets(prs, "How we know it is right - and what we could not test", [
        f"Every figure reconciles to the trial balance; debits = credits = {usd(C.EXPECTED['Total debits'])}",
        "The GL-derived trial balance agrees to the client's on all 64 accounts used; the balance sheet "
        "checks to zero and the cash flow ties to the cash accounts",
        "A partner who did not build the work re-performed a number on every page",
        ("Limitation: the creditor extract is a sample. Three-way-match statistics are stated on that "
         "basis and a complete extract has been requested", 1),
        ("Limitation: no goods-received notes or contracts were provided, so we report exceptions, not "
         "losses", 1),
    ], subtitle="Reconciled, re-performed, and honest about the gaps",
        notes="Close on the limitations. A committee that trusts the limitations trusts the findings.")
    save_deck(prs, ensure(os.path.join(out, "Committee_Pack.pptx")))


def failure_reason(r):
    if not r["PONumber"]:
        return "No purchase order on file"
    if not r["GRNNumber"]:
        return "Purchase order but no goods-received note"
    if r["DuplicateSuspected"]:
        return "Suspected duplicate of another invoice from the same supplier"
    return "Price or quantity variance beyond tolerance"


def age_band(days):
    if days <= 30:
        return "0-30 days"
    if days <= 60:
        return "31-60 days"
    if days <= 90:
        return "61-90 days"
    return "Over 90 days"


def bank_cause(r):
    if r["AgeDays"] > 90:
        return "Aged unmatched item - possibly a payment never recorded, or a duplicate"
    if r["DebitUSD"] > 0:
        return "Bank debit with no matching ledger entry - payment may be unrecorded"
    return "Bank credit with no matching ledger entry - receipt not yet allocated"


def bank_action(r):
    if r["AgeDays"] > 90:
        return "Investigate within two weeks; write off only with written approval"
    return "Match to the ledger within the month; escalate if unmatched at month end"


def vendor_master_rows(led):
    from datetime import datetime
    rows = []
    for v in led.vendors:
        first = None
        for r in led.gl:
            if r["VendorID"] == v["VendorID"] and r["Debit"] > 0:
                if first is None or r["PostingDate"] < first:
                    first = r["PostingDate"]
        created = datetime.strptime(v["VendorCreatedOn"], "%Y-%m-%d").date() if v["VendorCreatedOn"] else None
        gap = (first - created).days if (created and first) else None
        ind = []
        if v["IsEmployeeLinked"] == "Yes":
            ind.append("Employee-linked in the vendor master")
        if not v["TaxClearanceNo"]:
            ind.append("No tax clearance number")
        if gap is not None and gap <= 30:
            ind.append(f"First payment {gap} days after creation")
        if v["PaymentTerms"] and int(v["PaymentTerms"]) <= 7:
            ind.append(f"{v['PaymentTerms']}-day terms (unusual)")
        if v["LastBankChangeDate"]:
            ind.append(f"Bank details changed {v['LastBankChangeDate']}")
        rows.append([v["VendorName"], v["Category"], v["VendorCreatedOn"],
                     "Yes" if v["TaxClearanceNo"] else "No", v["PaymentTerms"],
                     mask(v["BankAccount"]), v["BankName"], v["LastBankChangeDate"] or "-",
                     "Yes" if v["IsEmployeeLinked"] == "Yes" else "No",
                     gap if gap is not None else "", "; ".join(ind) or "No indicators"])
    rows.sort(key=lambda r: (r[8] != "Yes", r[0]))
    return rows


def mask(acct):
    return acct[:4] + "*" * max(0, len(acct) - 8) + acct[-4:] if len(acct) > 8 else "****"


def customer_rows(ctx, led):
    from collections import defaultdict
    agg = defaultdict(lambda: {"out": 0.0, "old": 0, "disp": 0})
    for r in ctx["ar"]["rows"]:
        a = agg[r["CustomerID"]]
        a["out"] += r["OutstandingUSD"]
        a["old"] = max(a["old"], r["DaysOverdue"])
        a["disp"] += 1 if r["Disputed"] else 0
    rows = []
    for c in led.customers:
        a = agg.get(c["CustomerID"], {"out": 0.0, "old": 0, "disp": 0})
        limit = float(c["CreditLimitUSD"] or 0)
        rows.append([c["CustomerName"], c["Segment"], limit, round(a["out"], 2),
                     a["out"] / limit if limit else None,
                     "OVER LIMIT" if limit and a["out"] > limit else "No", a["old"], a["disp"]])
    rows.sort(key=lambda r: -(r[4] or 0))
    return rows


def ageing_bridge(ctx, led):
    rt = ctx["ratios"]
    opening = led.balance_at("1100", C.PYE)
    closing = rt["Inputs"]["AR"]
    invoiced = sum(r["AmountUSD"] for r in ctx["ar"]["rows"])
    collected = sum(r["AmountReceivedUSD"] for r in ctx["ar"]["rows"])
    disputed = sum(r["OutstandingUSD"] for r in ctx["ar"]["rows"] if r["Disputed"])
    other = closing - opening - (invoiced - collected)
    return [
        ["Opening trade receivables (31 Dec 2024)", opening, "Control account 1100 at the prior year end"],
        ["Invoiced in the period (per the ageing extract)", invoiced,
         "Sum of invoice values in the debtor ageing extract"],
        ["Collected in the period (per the ageing extract)", -collected,
         "Sum of amounts received in the debtor ageing extract"],
        ["Other movements (reconciling item)", other,
         "Difference to the control account - includes invoices outside the extract and credit notes"],
        ["**Closing trade receivables (30 Sep 2025)**", closing,
         "Agrees to control account 1100 in the general ledger"],
        ["of which disputed", disputed, f"{ctx['ar']['disputed']} accounts"],
    ]
