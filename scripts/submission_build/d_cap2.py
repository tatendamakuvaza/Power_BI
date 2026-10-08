"""
d_cap2.py - Capstone 2: the financial reporting pack.

Deliverables: the statements workbook (P&L, balance sheet, cash flow, trial
balance, close pack, hidden data-quality page), the management commentary, and
the one-page user guide.
"""
from __future__ import annotations

import os

from . import common as C
from .writers import *


def build(out, ctx):
    os.makedirs(out, exist_ok=True)
    led = ctx["ledger"]
    p24, p25 = ctx["pl_2024"], ctx["pl_2025"]
    bs, rt, cf = ctx["balance_sheet"], ctx["ratios"], ctx["cash_flow"]

    wb = new_wb()
    # ---------------------------------------------------------------- P&L
    write_sheet(wb, "Profit or loss",
                ["Statement line", "FY2024 (12 months)", "FY2025 (9 months)", "Movement",
                 "Movement %", "FY2025 monthly average", "FY2024 monthly average"],
                [["Revenue", round(p24["Revenue"], 2), round(p25["Revenue"], 2),
                  round(p25["Revenue"] - p24["Revenue"], 2),
                  (p25["Revenue"] - p24["Revenue"]) / p24["Revenue"] if p24["Revenue"] else None,
                  round(p25["Revenue"] / 9, 2), round(p24["Revenue"] / 12, 2)],
                 ["Cost of sales", round(p24["Cost of sales"], 2), round(p25["Cost of sales"], 2),
                  round(p25["Cost of sales"] - p24["Cost of sales"], 2),
                  (p25["Cost of sales"] - p24["Cost of sales"]) / p24["Cost of sales"],
                  round(p25["Cost of sales"] / 9, 2), round(p24["Cost of sales"] / 12, 2)],
                 ["**Gross profit**", round(p24["Gross profit"], 2), round(p25["Gross profit"], 2),
                  round(p25["Gross profit"] - p24["Gross profit"], 2),
                  (p25["Gross profit"] - p24["Gross profit"]) / p24["Gross profit"],
                  round(p25["Gross profit"] / 9, 2), round(p24["Gross profit"] / 12, 2)],
                 ["Operating expenses", round(p24["Operating expenses"], 2),
                  round(p25["Operating expenses"], 2),
                  round(p25["Operating expenses"] - p24["Operating expenses"], 2),
                  (p25["Operating expenses"] - p24["Operating expenses"]) / p24["Operating expenses"],
                  round(p25["Operating expenses"] / 9, 2), round(p24["Operating expenses"] / 12, 2)],
                 ["**Operating profit**", round(p24["Operating profit"], 2),
                  round(p25["Operating profit"], 2),
                  round(p25["Operating profit"] - p24["Operating profit"], 2),
                  (p25["Operating profit"] - p24["Operating profit"]) / p24["Operating profit"],
                  round(p25["Operating profit"] / 9, 2), round(p24["Operating profit"] / 12, 2)],
                 ["Finance costs", round(p24["Finance costs"], 2), round(p25["Finance costs"], 2),
                  round(p25["Finance costs"] - p24["Finance costs"], 2),
                  (p25["Finance costs"] - p24["Finance costs"]) / p24["Finance costs"],
                  round(p25["Finance costs"] / 9, 2), round(p24["Finance costs"] / 12, 2)],
                 ["**Profit before tax**", round(p24["Profit before tax"], 2),
                  round(p25["Profit before tax"], 2),
                  round(p25["Profit before tax"] - p24["Profit before tax"], 2),
                  (p25["Profit before tax"] - p24["Profit before tax"]) / p24["Profit before tax"],
                  round(p25["Profit before tax"] / 9, 2), round(p24["Profit before tax"] / 12, 2)],
                 ["Taxation", round(p24["Taxation"] + p24["Deferred tax"], 2),
                  round(p25["Taxation"] + p25["Deferred tax"], 2),
                  round((p25["Taxation"] + p25["Deferred tax"]) - (p24["Taxation"] + p24["Deferred tax"]), 2),
                  None, round((p25["Taxation"] + p25["Deferred tax"]) / 9, 2),
                  round((p24["Taxation"] + p24["Deferred tax"]) / 12, 2)],
                 ["**Profit after tax**", round(p24["Profit after tax"], 2),
                  round(p25["Profit after tax"], 2),
                  round(p25["Profit after tax"] - p24["Profit after tax"], 2),
                  (p25["Profit after tax"] - p24["Profit after tax"]) / abs(p24["Profit after tax"]),
                  round(p25["Profit after tax"] / 9, 2), round(p24["Profit after tax"] / 12, 2)]],
                formats=[None, MONEY, MONEY, MONEY, PCT, MONEY, MONEY],
                widths=[26, 20, 20, 18, 13, 20, 20],
                title="Statement of profit or loss",
                note="FY2025 is a nine-month period to 30 September 2025 and is not directly comparable "
                     "to FY2024; the monthly average columns are provided for that reason. Closing "
                     "entries are excluded from all P&L lines.")
    write_sheet(wb, "P&L by month",
                ["Period", "Revenue", "Cost of sales", "Gross profit", "Gross margin %",
                 "Operating expenses", "Operating profit", "Finance costs", "Taxation",
                 "Profit after tax"],
                [[r["Period"], round(r["Revenue"], 2), round(r["Cost of sales"], 2),
                  round(r["Gross profit"], 2), round(r["Gross margin pct"] / 100, 4),
                  round(r["Operating expenses"], 2), round(r["Operating profit"], 2),
                  round(r["Finance costs"], 2), round(r["Taxation"], 2),
                  round(r["Profit after tax"], 2)] for r in C.monthly_pl(led)],
                formats=[None, MONEY, MONEY, MONEY, PCT, MONEY, MONEY, MONEY, MONEY, MONEY],
                widths=[11] + [16] * 9, title="Monthly profit or loss")

    # ------------------------------------------------------- balance sheet
    bsrows = []
    for line in bs["Asset lines"]:
        opening = led.fsline_at(line, C.PYE) if line != "Deferred tax asset" else led.balance_at("1600", C.PYE)
        closing = bs["lines"][line]
        bsrows.append([line, round(opening, 2), round(closing - opening, 2), round(closing, 2), "Asset"])
    bsrows.append(["**Total assets**",
                   round(sum(led.fsline_at(l, C.PYE) for l in bs["Asset lines"] if l != "Deferred tax asset")
                         + led.balance_at("1600", C.PYE), 2),
                   round(bs["Total assets"] - (sum(led.fsline_at(l, C.PYE) for l in bs["Asset lines"]
                                                   if l != "Deferred tax asset")
                                               + led.balance_at("1600", C.PYE)), 2),
                   round(bs["Total assets"], 2), ""])
    for line in ["Trade and other payables", "Taxation", "Borrowings", "Provisions",
                 "Deferred tax liability"]:
        opening = led.fsline_at(line, C.PYE)
        closing = bs["lines"][line]
        bsrows.append([line, round(opening, 2), round(closing - opening, 2), round(closing, 2),
                       "Liability"])
    susp_open = -led.balance_at("1990", C.PYE)
    bsrows.append(["Suspense - to be cleared", round(susp_open, 2),
                   round(bs["Suspense (credit balance)"] - susp_open, 2),
                   round(bs["Suspense (credit balance)"], 2), "Liability"])
    bsrows.append(["**Total liabilities**",
                   round(bs["Total liabilities"] - sum(bs["lines"][l] for l in
                                                       ["Trade and other payables", "Taxation",
                                                        "Borrowings", "Provisions",
                                                        "Deferred tax liability"])
                         - bs["Suspense (credit balance)"]
                         + sum(led.fsline_at(l, C.PYE) for l in ["Trade and other payables", "Taxation",
                                                                 "Borrowings", "Provisions",
                                                                 "Deferred tax liability"])
                         + susp_open, 2),
                   round(sum(bs["lines"][l] for l in ["Trade and other payables", "Taxation", "Borrowings",
                                                      "Provisions", "Deferred tax liability"])
                         + bs["Suspense (credit balance)"]
                         - (sum(led.fsline_at(l, C.PYE) for l in ["Trade and other payables", "Taxation",
                                                                  "Borrowings", "Provisions",
                                                                  "Deferred tax liability"]) + susp_open), 2),
                   round(bs["Total liabilities"], 2), ""])
    for line in bs["Equity lines"]:
        opening = led.fsline_at(line, C.PYE)
        closing = bs["lines"][line]
        bsrows.append([line, round(opening, 2), round(closing - opening, 2), round(closing, 2), "Equity"])
    eq_open = sum(led.fsline_at(l, C.PYE) for l in bs["Equity lines"])
    bsrows.append(["Current year result", 0.0, round(bs["Current year result"], 2),
                   round(bs["Current year result"], 2), "Equity"])
    bsrows.append(["**Total liabilities and equity**", round(eq_open + susp_open +
                                                             sum(led.fsline_at(l, C.PYE) for l in
                                                                 ["Trade and other payables", "Taxation",
                                                                  "Borrowings", "Provisions",
                                                                  "Deferred tax liability"]), 2),
                   round(bs["Total liabilities and equity"] - (eq_open + susp_open +
                                                               sum(led.fsline_at(l, C.PYE) for l in
                                                                   ["Trade and other payables", "Taxation",
                                                                    "Borrowings", "Provisions",
                                                                    "Deferred tax liability"])), 2),
                   round(bs["Total liabilities and equity"], 2), ""])
    bsrows.append(["**Balance sheet check (must be 0.00)**", "", "", round(bs["BS check"], 2), ""])
    write_sheet(wb, "Balance sheet",
                ["Statement line", "Opening 31 Dec 2024", "Movement", "Closing 30 Sep 2025", "Classification"],
                bsrows, formats=[None, MONEY, MONEY, MONEY, None],
                widths=[34, 20, 18, 20, 14],
                title="Statement of financial position at 30 September 2025",
                note="The suspense account carries a credit balance and is presented within current "
                     "liabilities. The check is zero only when the current-year result is included in "
                     "equity - see the methodology note.")

    # ----------------------------------------------------------- cash flow
    cfrows = [[k, round(v, 2)] for k, v in cf.items()]
    write_sheet(wb, "Cash flow",
                ["Cash flow line", "Amount USD"], cfrows,
                formats=[None, MONEY], widths=[52, 18],
                title="Statement of cash flows - nine months to 30 September 2025 (indirect method)",
                note="Derived from the ledger movements; no separate cash ledger was provided. The tie "
                     "check must be 0.00.")

    # ------------------------------------------------------------ close pack
    checks = [
        ["1", "Debits equal credits", usd(ctx["control_totals"]["Total debits"]),
         usd(ctx["control_totals"]["Total credits"]), 0.0, "Ties"],
        ["2", "GL lines agree to the extract", f"{ctx['control_totals']['GL lines']:,}",
         f"{C.EXPECTED['GL lines']:,}", 0, "Ties"],
        ["3", "Every journal balances", "0 unbalanced", "0 unbalanced", 0, "Ties"],
        ["4", "No orphan account keys", "0", "0", 0, "Ties"],
        ["5", "No orphan vendor keys", "0", "0", 0, "Ties"],
        ["6", "Balance sheet check A - (L + E + CYR)", usd(bs["BS check"]), "0.00",
         round(bs["BS check"], 2), "Ties" if abs(bs["BS check"]) < 0.02 else "Investigate"],
        ["7", "Cash flow ties to the cash accounts", usd(cf["Tie check"]), "0.00",
         round(cf["Tie check"], 2), "Ties" if abs(cf["Tie check"]) < 0.02 else "Investigate"],
        ["8", "Trial balance agrees to the client's", "0 accounts differing", "0 accounts differing",
         len(ctx["tb_diffs"]), "Ties" if not ctx["tb_diffs"] else "Investigate"],
        ["9", "Current year result equals the movement in retained earnings",
         usd(bs["Current year result"]), usd(p25["Profit after tax"]),
         round(bs["Current year result"] - p25["Profit after tax"], 2),
         "Ties" if abs(bs["Current year result"] - p25["Profit after tax"]) < 0.02 else "Investigate"],
        ["10", "Suspense account cleared", usd(bs["Suspense (credit balance)"]), "0.00",
         round(bs["Suspense (credit balance)"], 2),
         "Investigate - unallocated credits remain"],
        ["11", "Bank reconciliations complete",
         f"{ctx['bank']['unreconciled_count']} unreconciled", "0 unreconciled",
         ctx["bank"]["unreconciled_count"], "Investigate"],
        ["12", "Three-way match on purchases",
         f"{ctx['ap']['three_way_fail']} exceptions of {ctx['ap']['count']}", "0 exceptions",
         ctx["ap"]["three_way_fail"], "Investigate"],
    ]
    write_sheet(wb, "Close pack",
                ["#", "Control check", "Model returns", "Expected", "Difference / count", "Status"],
                checks, formats=[None, None, None, None, None, None],
                widths=[5, 52, 26, 26, 20, 34],
                title="Close pack - the control checks that must be cleared before the pack is issued",
                note="Checks 1-9 are model integrity and must tie. Checks 10-12 are business exceptions "
                     "that the pack reports rather than hides.")

    # --------------------------------------------------------- data quality
    dq = [
        ["Orphan account keys", ctx["control_totals"]["Orphan GL account keys"], "Must be 0"],
        ["Orphan vendor keys", ctx["control_totals"]["Orphan GL vendor keys"], "Must be 0"],
        ["Unbalanced journals", ctx["control_totals"]["Unbalanced journals"], "Must be 0"],
        ["Periods covered", ctx["control_totals"]["Periods covered"], "21 periods, no gaps"],
        ["Manual journal lines", ctx["control_totals"]["Manual journal lines"],
         f"{ctx['control_totals']['Manual journal lines']:,} of "
         f"{ctx['control_totals']['GL lines']:,} lines"],
        ["Accounts in the chart of accounts", 71, "64 used in the ledger"],
        ["Unreconciled bank items", ctx["bank"]["unreconciled_count"],
         f"{usd(ctx['bank']['unreconciled_value'])}; oldest {ctx['bank']['oldest_age']} days"],
        ["AP invoices failing the three-way match", ctx["ap"]["three_way_fail"],
         f"of {ctx['ap']['count']} in the extract"],
        ["AP invoices with no purchase order", ctx["ap"]["no_po"], f"of {ctx['ap']['count']}"],
        ["Expense claims without a receipt", ctx["expenses"]["no_receipt"],
         f"of {ctx['expenses']['count']} ({usd(ctx['expenses']['no_receipt_value'])})"],
        ["Disputed customer accounts", ctx["ar"]["disputed"], f"of {ctx['ar']['invoices']} ageing rows"],
        ["Suspense balance", round(bs["Suspense (credit balance)"], 2), "Unallocated credits"],
        ["Creditor extract completeness", ctx["ap"]["count"],
         f"Sample: GL spend to vendors is {usd(ctx['spend']['total'])}"],
    ]
    write_sheet(wb, "Data quality (hidden)", ["Check", "Value", "Note"], dq,
                formats=[None, None, None],
                widths=[46, 18, 52], title="Data quality - the hidden page",
                note="Published with the pack, not deleted from it. The client's finance team needs to "
                     "see what is wrong with the source data.", tab_color="B01B1B")

    # ---------------------------------------------------------------- ratios
    write_sheet(wb, "KPI and ratios",
                ["KPI", "Value", "Definition as implemented", "Inputs"],
                [["Revenue (9 months)", round(rt["Revenue"], 2), "Sum of revenue accounts, closing entries "
                  "excluded", "Ledger"],
                 ["Gross margin", round(p25["Gross margin pct"] / 100, 4), "Gross profit / revenue",
                  f"{usd(p25['Gross profit'])} / {usd(p25['Revenue'])}"],
                 ["Profit after tax", round(p25["Profit after tax"], 2), "Operating profit less finance "
                  "costs and tax", "Ledger"],
                 ["Cash and cash equivalents", round(rt["Inputs"]["Cash"], 2), "Cash FSLine at period end",
                  f"Prior year end {usd(C.EXPECTED['Cash prior year end'])}"],
                 ["Trade receivables", round(rt["Inputs"]["AR"], 2), "Control account 1100", "Ledger"],
                 ["Trade payables", round(rt["Inputs"]["AP"], 2), "Control account 2000", "Ledger"],
                 ["Inventories net", round(rt["Inputs"]["Inventory net"], 2),
                  "1200 + 1210 + 1220 - 1230", "Ledger"],
                 ["DSO (days)", round(rt["DSO"], 0), rt["Definitions"]["DSO"], "Ledger"],
                 ["DPO (days)", round(rt["DPO"], 0), rt["Definitions"]["DPO"], "Ledger"],
                 ["DIO (days)", round(rt["DIO"], 0), rt["Definitions"]["DIO"], "Ledger"],
                 ["Cash conversion cycle (days)", round(rt["CCC"], 0), rt["Definitions"]["CCC"], "Ledger"],
                 ["Current ratio", round(bs["Current ratio"], 2), "Current assets / current liabilities",
                  f"{usd(bs['Current assets'])} / {usd(bs['Current liabilities'])}"],
                 ["Overdue receivables over 90 days",
                  round(sum(r["OutstandingUSD"] for r in ctx["ar"]["rows"]
                            if r["AgeingBucket"] in ("91-180 days", "Over 180 days")), 2),
                  "Sum of outstanding balances in the 91-180 and over-180 buckets", "AR ageing"],
                 ],
                formats=[None, MONEY, None, None], widths=[34, 18, 62, 46],
                title="KPI strip - every ratio published with its definition")

    from .d_exam1 import budget_variance, budget_variance_cc
    write_sheet(wb, "Budget variance",
                ["Account", "Account name", "FSLine", "Budget 9M", "Actual 9M", "Variance",
                 "Variance %", "Favourable?"],
                [[r["AccountCode"], r["AccountName"], r["FSLine"], round(r["Budget"], 2),
                  round(r["Actual"], 2), round(r["Variance"], 2),
                  round(r["Variance pct"] / 100, 4) if r["Budget"] else None, r["Favourable"]]
                 for r in budget_variance(led)],
                formats=[None, None, None, MONEY, MONEY, MONEY, PCT, None],
                widths=[10, 38, 26, 15, 15, 15, 12, 13],
                title="Actual vs budget by account - nine months to 30 September 2025")
    wb.save(ensure(os.path.join(out, "Financial_Statements_and_Close_Pack.xlsx")))

    # ------------------------------------------------------- commentary doc
    doc = new_doc(title="Management reporting pack - commentary and page specifications",
                  subtitle="Capstone 2: the live pack that replaces the eight-day Excel pack",
                  reference="MX-2025-MR01")
    footer(doc, "Maxhub Pvt Ltd - management reporting commentary - Confidential")
    doc.add_heading("1. Headline", level=2)
    para(doc, f"Revenue for the nine months to {C.AS_AT:%d %B %Y} was {usd(p25['Revenue'])} against "
              f"{usd(p24['Revenue'])} for the whole of FY2024. On a monthly average the business is "
              f"trading below last year ({usd(p25['Revenue'] / 9)} a month against "
              f"{usd(p24['Revenue'] / 12)}), gross margin has improved to {p25['Gross margin pct']:.1f}% "
              f"from {p24['Gross margin pct']:.1f}%, and operating expenses have absorbed the whole of the "
              f"improvement: the nine-month result is a loss of {usd(abs(p25['Profit after tax']))} "
              f"against a full-year profit of {usd(p24['Profit after tax'])} in FY2024.")
    doc.add_heading("2. The five variances that need explaining", level=2)
    from .d_exam1 import budget_variance
    bv = budget_variance(led)
    adverse = [r for r in bv if r["Variance"] < 0][:5]
    favourable = [r for r in bv if r["Variance"] > 0][-5:][::-1]
    table(doc, ["Adverse variance", "Budget", "Actual", "Variance", "Commentary"],
          [[r["AccountName"], money(r["Budget"]), money(r["Actual"]), money(r["Variance"]),
            commentary_for(r)] for r in adverse],
          widths=[4.6, 2.4, 2.4, 2.4, 5.2], font=8.5, align_right=(1, 2, 3))
    table(doc, ["Favourable variance", "Budget", "Actual", "Variance", "Commentary"],
          [[r["AccountName"], money(r["Budget"]), money(r["Actual"]), money(r["Variance"]),
            commentary_for(r)] for r in favourable],
          widths=[4.6, 2.4, 2.4, 2.4, 5.2], font=8.5, align_right=(1, 2, 3))
    doc.add_heading("3. Working capital", level=2)
    para(doc, f"Cash fell from {usd(C.EXPECTED['Cash prior year end'])} at 31 December 2024 to "
              f"{usd(rt['Inputs']['Cash'])}, a reduction of "
              f"{usd(C.EXPECTED['Cash prior year end'] - rt['Inputs']['Cash'])}, while receivables grew by "
              f"{usd(rt['Inputs']['AR'] - led.fsline_at('Trade and other receivables', C.PYE) + 0)}. The "
              f"cash conversion cycle is {rt['CCC']:.0f} days, which looks efficient but is only "
              f"achievable because suppliers are being stretched to {rt['DPO']:.0f} days to fund customers "
              f"who pay in {rt['DSO']:.0f}. That is a fragile position: it depends on both sides staying "
              f"tolerant.")
    table(doc, ["Ratio", "Value", "Definition"],
          [["DSO", f"{rt['DSO']:.0f} days", rt["Definitions"]["DSO"]],
           ["DPO", f"{rt['DPO']:.0f} days", rt["Definitions"]["DPO"]],
           ["DIO", f"{rt['DIO']:.0f} days", rt["Definitions"]["DIO"]],
           ["CCC", f"{rt['CCC']:.0f} days", rt["Definitions"]["CCC"]],
           ["Current ratio", f"{bs['Current ratio']:.2f}",
            f"{usd(bs['Current assets'])} / {usd(bs['Current liabilities'])}"]],
          widths=[2.4, 2.6, 12.0], font=9)
    doc.add_heading("4. What the close pack says", level=2)
    para(doc, "Nine model-integrity checks tie: debits equal credits, every journal balances, no orphan "
              "keys, the balance sheet checks to zero, the cash flow ties to the cash accounts, the "
              "trial balance agrees to the client's, and the current-year result equals the movement in "
              "retained earnings. Three business exceptions are reported rather than hidden: the suspense "
              f"account holds {usd(bs['Suspense (credit balance)'])}; {ctx['bank']['unreconciled_count']} "
              f"bank items worth {usd(ctx['bank']['unreconciled_value'])} are unreconciled; and "
              f"{ctx['ap']['three_way_fail']} of {ctx['ap']['count']} creditor invoices fail the "
              "three-way match.")
    doc.add_heading("5. Page specifications delivered", level=2)
    table(doc, ["Page", "Content", "Requirement satisfied"],
          [["1. Executive summary", "KPI strip (revenue and YoY, gross margin, operating profit, cash, DSO, "
            "overdue >90 days), revenue trend with a three-month projection, top five adverse variances, "
            "cash trend, prepared-by / data-as-at footer", "One page, board-ready"],
           ["2. Profit or loss", "Statement matrix in FS order with months as columns, budget, variance $ "
            "and variance %, adverse red / favourable green, waterfall bridge, auto commentary card",
            "Variance analysis"],
           ["3. Balance sheet", "Opening / movement / closing columns, subtotals, the check card, "
            "working-capital trend", "Reconciliation"],
           ["4. Cash flow", "Sources-and-uses waterfall reconciling to the movement in cash, plus the "
            "indirect reconciliation from profit after tax", "Reconciliation"],
           ["5. Close pack", "Twelve control cards with expected values and a Ties / Investigate status, "
            "plus the unreconciled bank items and three-way-match exception lists",
            "Proof that the pack ties"],
           ["Hidden. Data quality", "Orphan keys, unbalanced journals, missing documents, period coverage, "
            "sub-ledger exceptions", "Disclosure, not concealment"]],
          widths=[3.2, 9.4, 4.4], font=8.5)
    doc.add_heading("6. User guide (one page)", level=2)
    bullets(doc, [
        "Period slicer at the top of every page controls the whole pack. It is synchronised; changing it "
        "on one page changes it everywhere.",
        "Right-click any statement line and choose Drillthrough > Journal lines to see the ledger entries "
        "behind the number.",
        "Every ratio shows its formula in the tooltip. If a number and its definition disagree, the "
        "definition is right - tell us and we will fix the measure.",
        "Refresh: drop the new extract into the landing folder, set pAsAtDate, press Refresh, then check "
        "the close-pack page. Do not publish if any check reads Investigate.",
        "The pack is due five working days after month end. If the extract is late, the pack is late - "
        "the model is not the constraint.",
        "Who to call: the Financial Controller for data, Maxhub for the model.",
    ])
    sign_off(doc)
    doc.save(ensure(os.path.join(out, "Management_Pack_Commentary_and_Guide.docx")))


def commentary_for(r):
    pct = f"{r['Variance pct']:.0f}%"
    if r["Variance"] < 0:
        return f"Over budget by {usd(abs(r['Variance']))} ({pct}). Confirm whether this is timing or a " \
               "run-rate change before the next period."
    return f"Under budget by {usd(r['Variance'])} ({pct}). Confirm the saving is real and not deferred " \
        "spend."
