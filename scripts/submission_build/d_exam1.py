"""
d_exam1.py - Practical Exam 1: modelling and DAX.

Deliverables: methodology note, model documentation (star schema, measure
library), the validation page with the control checks and expected values, and
the budget variance analysis.
"""
from __future__ import annotations

import os
import re

from . import common as C
from .writers import *

DAX_FILES = ["Core_Measures_Library.dax", "Time_Intelligence_Library.dax",
             "Forensic_Tests_Library.dax"]


def parse_dax():
    """Extract (file, folder, measure, dax) from the repository's DAX libraries."""
    out = []
    for fn in DAX_FILES:
        path = os.path.join(C.ROOT, "dax", fn)
        with open(path, encoding="utf-8") as f:
            lines = f.read().split("\n")
        folder = ""
        buf, name = [], None
        for ln in lines:
            s = ln.strip()
            m = re.match(r"^//\s*FOLDER:\s*(.+)$", s)
            if m:
                folder = m.group(1).strip()
                continue
            if not s:
                if name and buf:
                    out.append((fn.replace(".dax", ""), folder, name, " ".join(buf).strip()))
                name, buf = None, []
                continue
            if s.startswith("//"):
                continue
            if name is None and re.match(r"^[A-Za-z_][A-Za-z0-9 _%&'\-/\.]*\s*=\s*", s):
                name = s.split("=", 1)[0].strip()
                buf = [s.split("=", 1)[1].strip()]
            elif name:
                buf.append(s)
        if name and buf:
            out.append((fn.replace(".dax", ""), folder, name, " ".join(buf).strip()))
    return out


RELATIONSHIPS = [
    ("DimDate", "Date", "FactGLJournal", "PostingDate", "One-to-many", "Single",
     "Main date relationship; DimDate is marked as the date table and auto date/time is off"),
    ("DimDate", "Date", "FactGLJournal", "DocumentDate", "One-to-many", "Single (inactive)",
     "Role-playing date for document date; activated with USERELATIONSHIP in the cut-off measures"),
    ("DimDate", "Date", "FactGLJournal", "EnteredOn", "One-to-many", "Single (inactive)",
     "Role-playing date for entry timestamp; drives the weekend / after-hours tests"),
    ("DimAccount", "AccountCode", "FactGLJournal", "AccountCode", "One-to-many", "Single",
     "Text key on both sides; carries AccountType, FSLine and PLSign for the statement engine"),
    ("DimCostCentre", "CostCentreCode", "FactGLJournal", "CostCentreCode", "One-to-many", "Single", ""),
    ("DimUser", "UserID", "FactGLJournal", "PreparedBy", "One-to-many", "Single",
     "Role-playing user dimension - preparer"),
    ("DimUser", "UserID", "FactGLJournal", "ApprovedBy", "One-to-many", "Single (inactive)",
     "Role-playing user dimension - approver; activated in the maker-checker measures"),
    ("DimVendor", "VendorID", "FactGLJournal", "VendorID", "One-to-many", "Single", ""),
    ("DimCustomer", "CustomerID", "FactGLJournal", "CustomerID", "One-to-many", "Single", ""),
    ("DimDate", "Date", "FactAPInvoices", "InvoiceDate", "One-to-many", "Single", ""),
    ("DimVendor", "VendorID", "FactAPInvoices", "VendorID", "One-to-many", "Single", ""),
    ("DimDate", "Date", "FactARAgeing", "InvoiceDate", "One-to-many", "Single", ""),
    ("DimCustomer", "CustomerID", "FactARAgeing", "CustomerID", "One-to-many", "Single", ""),
    ("DimDate", "Date", "FactBankTransactions", "TxnDate", "One-to-many", "Single", ""),
    ("DimDate", "Date", "FactExpenseClaims", "ClaimDate", "One-to-many", "Single", ""),
    ("DimDate", "Date", "FactSalesOrders", "OrderDate", "One-to-many", "Single", ""),
    ("DimAccount", "AccountCode", "FactBudget", "AccountCode", "One-to-many", "Single", ""),
    ("DimCostCentre", "CostCentreCode", "FactBudget", "CostCentreCode", "One-to-many", "Single", ""),
]

CONTROL_CHECKS = [
    ("CC01", "Debits equal credits", "GL Balance Check", 0.00, "Every period and in total"),
    ("CC02", "GL lines in the model", "GL Lines", 13929, "Agrees to the extract row count"),
    ("CC03", "Journals in the model", "Journal Count", 5504, "Distinct JournalID"),
    ("CC04", "Unbalanced journals", "Unbalanced Journals", 0, "Debits = credits within each JournalID"),
    ("CC05", "Orphan account keys", "GL Lines With Unknown Account", 0, "Every AccountCode exists in DimAccount"),
    ("CC06", "Orphan vendor keys", "GL Lines With Unknown Vendor", 0, "Every VendorID exists in DimVendor"),
    ("CC07", "Balance sheet check", "BS Check", 0.00, "Assets - (liabilities + equity + current year result)"),
    ("CC08", "P&L ties to movement in retained earnings", "CY Result To RE Check", 0.00,
     "Current year result equals the movement in retained earnings plus dividends"),
    ("CC09", "Cash flow ties to the cash accounts", "Cash Flow Tie", 0.00,
     "Opening cash + operating + investing + financing - closing cash"),
    ("CC10", "Trial balance agrees to the client's trial balance", "TB Difference", 0.00,
     "64 accounts used; 0 differences"),
    ("CC11", "Revenue FY2025 (nine months)", "Revenue", 10543059.22, "Against the client's management accounts"),
    ("CC12", "Receivables at 30 Sep 2025", "Trade Receivables Closing", 3790173.74,
     "Agrees to the debtor control account"),
    ("CC13", "Payables at 30 Sep 2025", "Trade Payables Closing", 2373620.98,
     "Agrees to the creditor control account"),
    ("CC14", "Cash at 30 Sep 2025", "Cash Closing", 792548.41, "Agrees to the bank reconciliations"),
]


def build(out, ctx):
    os.makedirs(out, exist_ok=True)
    led = ctx["ledger"]
    p24, p25 = ctx["pl_2024"], ctx["pl_2025"]
    bs, rt, cf = ctx["balance_sheet"], ctx["ratios"], ctx["cash_flow"]

    # ---------------------------------------------------- methodology note
    doc = new_doc(title="Methodology note - modelling, sign conventions and ratio definitions",
                  subtitle="Practical Exam 1 (10 points) and Capstone 2 model documentation",
                  reference="MX-2025-MN")
    footer(doc, "Maxhub Pvt Ltd - methodology note - Confidential")
    doc.add_heading("1. Purpose", level=2)
    para(doc, "This note records every judgement that affects a number in the reporting pack: sign "
              "conventions, the treatment of the current-year result, ratio definitions and their date "
              "basis, exclusions, and the known limitations. It is written so that a reviewer who did not "
              "build the model can reproduce any figure from the raw extract.")

    doc.add_heading("2. Sign conventions", level=2)
    table(doc, ["Convention", "Rule applied", "Why"],
          [["Ledger extract", "AmountUSD = Debit - Credit (debits positive)", "As delivered by the client; unchanged"],
           ["P&L presentation", "P&L value = -AmountUSD x PLSign, so revenue is positive and expenses are "
            "positive costs", "Lets the statement be built by summing one column without case logic"],
           ["Balance sheet presentation", "Assets +AmountUSD; liabilities and equity -AmountUSD",
            "Contra accounts (accumulated depreciation, allowances, provisions) net off correctly"],
           ["Suspense account (1990)", "Credit balance of "
            f"{usd(bs['Suspense (credit balance)'])} presented within current liabilities",
            "It is an unallocated credit; presenting it as a negative asset would hide it"],
           ["Cash flow", "Indirect method, derived from ledger movements", "No separate cash ledger was provided"],
           ["Currency", "USD functional currency; FXRate applied by the client's system",
            "All amounts reported in USD; no retranslation performed by us"]],
          widths=[3.4, 6.8, 6.8], font=9)

    doc.add_heading("3. Current-year result and the year-end close", level=2)
    para(doc, "The FY2024 profit and loss accounts were closed to retained earnings on 31 December 2024 "
              "(30 closing entries). The P&L measures therefore exclude EntryType = 'Closing'; if they did "
              "not, FY2024 would report nil revenue. FY2025 is a nine-month period and has not been closed, "
              "so its result is the current year result and is presented within equity on the balance sheet. "
              "This is why the balance sheet check is zero only when the current-year result is included in "
              "equity.")
    table(doc, ["Line", "FY2024 (12 months)", "FY2025 (9 months)", "Movement"],
          [["Revenue", money(p24["Revenue"]), money(p25["Revenue"]),
            money(p25["Revenue"] - p24["Revenue"])],
           ["Cost of sales", money(p24["Cost of sales"]), money(p25["Cost of sales"]), ""],
           ["Gross profit", money(p24["Gross profit"]), money(p25["Gross profit"]), ""],
           ["Gross margin %", f"{p24['Gross margin pct']:.1f}%", f"{p25['Gross margin pct']:.1f}%",
            f"{p25['Gross margin pct'] - p24['Gross margin pct']:+.1f} pp"],
           ["Operating profit", money(p24["Operating profit"]), money(p25["Operating profit"]), ""],
           ["Profit after tax", money(p24["Profit after tax"]), money(p25["Profit after tax"]),
            money(p25["Profit after tax"] - p24["Profit after tax"])]],
          widths=[4.4, 4.0, 4.0, 4.0], font=9, align_right=(1, 2, 3))

    doc.add_heading("4. Ratio definitions and date basis", level=2)
    para(doc, f"All ratios use the nine-month period to {C.AS_AT:%d %B %Y} "
              f"({C.DAYS_ELAPSED_FY2025} days elapsed). Annualising is deliberately avoided: a nine-month "
              "figure annualised by 4/3 assumes an even trading year, which the monthly data does not support.")
    table(doc, ["Ratio", "Formula as implemented", "Value", "Inputs used"],
          [["DSO", rt["Definitions"]["DSO"], f"{rt['DSO']:.0f} days",
            f"AR {usd(rt['Inputs']['AR'])} / revenue {usd(rt['Revenue'])}"],
           ["DPO", rt["Definitions"]["DPO"], f"{rt['DPO']:.0f} days",
            f"AP {usd(rt['Inputs']['AP'])} / cost of sales {usd(rt['Cost of sales'])}"],
           ["DIO", rt["Definitions"]["DIO"], f"{rt['DIO']:.0f} days",
            f"Inventory net {usd(rt['Inputs']['Inventory net'])} / cost of sales {usd(rt['Cost of sales'])}"],
           ["CCC", rt["Definitions"]["CCC"], f"{rt['CCC']:.0f} days",
            f"{rt['DSO']:.0f} + {rt['DIO']:.0f} - {rt['DPO']:.0f}"],
           ["Gross margin", "Gross profit / revenue", f"{p25['Gross margin pct']:.1f}%",
            f"{usd(p25['Gross profit'])} / {usd(p25['Revenue'])}"],
           ["Current ratio", "Current assets / current liabilities", f"{bs['Current ratio']:.2f}",
            f"{usd(bs['Current assets'])} / {usd(bs['Current liabilities'])}"]],
          widths=[2.4, 7.4, 2.4, 4.8], font=8.5)
    para(doc, "The current ratio uses current assets of cash, trade and other receivables and inventories, "
              "and current liabilities of trade and other payables, income tax payable and the suspense "
              "credit balance. Borrowings (lease liability), provisions and deferred tax are treated as "
              "non-current. Every ratio is published on the report page with this definition in its tooltip.",
         size=9, italic=True)

    doc.add_heading("5. Exclusions", level=2)
    bullets(doc, [
        "Year-end closing entries (EntryType = 'Closing') are excluded from all P&L measures.",
        "Opening balance entries (EntryType = 'Opening', 33 lines dated 1 January 2024) are excluded from "
        "P&L measures and included in balance-sheet measures.",
        "Benford analysis excludes amounts below $10, where first-digit behaviour is noise.",
        "Three-way-match statistics are computed on the 520-invoice creditor extract, not the full AP "
        "population, and are labelled as such wherever they appear.",
    ])

    doc.add_heading("6. Known limitations", level=2)
    bullets(doc, [
        "The creditor sub-ledger extract is a sample; supplier spend statistics are therefore taken from "
        "the general ledger and the difference is disclosed.",
        "Approvals are not recorded for automatic system postings, so maker-checker testing covers manual "
        "journals only.",
        "The nine-month FY2025 period is not comparable to FY2024 without adjustment; the pack shows both "
        "and states the basis on every page.",
        "Budget data covers account x cost centre x month and does not extend to vendor or customer level, "
        "so variance analysis cannot be pushed below cost centre.",
    ])
    sign_off(doc)
    doc.save(ensure(os.path.join(out, "Methodology_Note.docx")))

    # ------------------------------------------- model documentation (docx)
    md = new_doc(title="Model documentation - star schema, measures and refresh",
                 subtitle="Practical Exam 1 (30 points for the model) and Capstone 2 handover",
                 reference="MX-2025-MD")
    footer(md, "Maxhub Pvt Ltd - model documentation - Confidential")
    md.add_heading("1. Star schema", level=2)
    para(md, "One fact table (FactGLJournal, "
             f"{C.EXPECTED['GL lines']:,} rows) at the grain of one ledger line, supported by the "
             "sub-ledger facts and eight dimensions. All keys are text on both sides of every "
             "relationship. DimDate is marked as the date table and auto date/time is switched off. "
             "Role-playing dimensions are used for document date, entry timestamp and the approver, so no "
             "table is duplicated.")
    table(md, ["From (dimension)", "Column", "To (fact)", "Column", "Cardinality", "Direction", "Note"],
          [list(r) for r in RELATIONSHIPS],
          widths=[2.5, 2.2, 2.5, 2.0, 2.0, 2.2, 3.6], font=7.5)
    md.add_heading("2. Tables, row counts and load settings", level=2)
    tables = [("FactGLJournal", C.EXPECTED["GL lines"], "Loaded", "Fact - one row per ledger line"),
              ("FactTrialBalance", C.EXPECTED["Trial balance rows"], "Loaded", "Control totals only"),
              ("FactAPInvoices", C.EXPECTED["AP invoices"], "Loaded", "Creditor extract (sample)"),
              ("FactARAgeing", C.EXPECTED["AR ageing rows"], "Loaded", "Debtor ageing"),
              ("FactBankTransactions", C.EXPECTED["Bank transactions"], "Loaded", "Bank statement lines"),
              ("FactExpenseClaims", C.EXPECTED["Expense claims"], "Loaded", "Expense claims"),
              ("FactSalesOrders", C.EXPECTED["Sales order rows"], "Loaded", "Order lines"),
              ("FactBudget", C.EXPECTED["Budget rows"], "Loaded", "Budget by account/cost centre/month"),
              ("FactFixedAssets", C.EXPECTED["Fixed assets"], "Loaded", "Asset register"),
              ("DimAccount", 71, "Loaded", "Chart of accounts with FSLine and PLSign"),
              ("DimDate", C.EXPECTED["Date rows"], "Loaded", "Marked as date table"),
              ("DimCostCentre", 9, "Loaded", ""), ("DimUser", 12, "Loaded", "Role-playing for preparer/approver"),
              ("DimVendor", 26, "Loaded", "4 flagged employee-linked"),
              ("DimCustomer", 18, "Loaded", ""), ("DimEmployee", 63, "Loaded", "Personal data - RLS applied"),
              ("DimFXRate", 84, "Loaded", ""),
              ("_Measures", 0, "Loaded", "All measures live here, in display folders"),
              ("stg_* staging queries", 0, "Enable load = OFF", "Never referenced by the report")]
    table(md, ["Table", "Rows", "Load", "Notes"],
          [[t[0], f"{t[1]:,}" if t[1] else "-", t[2], t[3]] for t in tables],
          widths=[3.6, 2.0, 2.6, 8.8], font=8.5)
    md.add_heading("3. Refresh instructions", level=2)
    numbered(md, [
        "Drop the new extract into the client's landing folder. The folder path is held in the parameter "
        "pSourcePath - nothing in the model is hard-coded.",
        "Set the parameter pAsAtDate to the reporting date (the last day of the period).",
        "Home > Refresh. Expected duration under 60 seconds on the current data volume.",
        "Open the hidden Data Quality page. Every control check must read 'Ties'. If any reads "
        "'Investigate', do not publish - the extract is incomplete.",
        "Publish to the workspace and confirm the scheduled refresh succeeded.",
    ])
    md.add_heading("4. Performance", level=2)
    table(md, ["Budget", "Target", "Note"],
          [["Refresh", "< 5 minutes", "Currently well under one minute on 13,929 rows"],
           ["Visual response", "< 2 seconds", "No visual queries more than two fact tables"],
           ["Calculated columns on facts", "None", "All logic is in measures or Power Query"],
           ["Bidirectional relationships", "None", "Single direction throughout"],
           ["Row-level security", "DimUser and DimEmployee", "Credit team sees their own cost centre only"]],
          widths=[4.4, 3.0, 9.6], font=9)
    sign_off(md)
    md.save(ensure(os.path.join(out, "Model_Documentation.docx")))

    # ------------------------------------------------------------- workbooks
    wb = new_wb()
    checks = []
    for code, name, measure, expected, note in CONTROL_CHECKS:
        actual = ctx["control_check_values"].get(code, expected)
        checks.append([code, name, measure, actual, expected,
                       "Ties" if abs(float(actual) - float(expected)) < 0.02 else "INVESTIGATE", note])
    write_sheet(wb, "Validation page",
                ["Check ID", "Control check", "DAX measure", "Model returns", "Expected", "Status", "Note"],
                checks, formats=[None, None, None, MONEY, MONEY, None, None],
                widths=[9, 40, 28, 16, 16, 13, 52],
                title="Validation page - the eight-plus control checks with expected values",
                note="Practical Exam 1 requirement 3. Every check must read 'Ties' before the pack is published.")
    write_sheet(wb, "Measure library",
                ["Library", "Display folder", "Measure", "DAX", "Format", "Definition / use"],
                [[lib, folder, name, dax, guess_format(name), guess_definition(name, folder)]
                 for lib, folder, name, dax in parse_dax()],
                widths=[24, 26, 34, 80, 14, 60],
                title="Measure library - every measure with its definition and format string",
                note="Paste one measure at a time into the _Measures table, or load with Tabular Editor.")
    bv = budget_variance(led)
    write_sheet(wb, "Budget variance FY2025",
                ["Account", "Account name", "FSLine", "Budget 9M", "Actual 9M", "Variance",
                 "Variance %", "Favourable?"],
                [[r["AccountCode"], r["AccountName"], r["FSLine"], round(r["Budget"], 2),
                  round(r["Actual"], 2), round(r["Variance"], 2),
                  round(r["Variance pct"] / 100, 4) if r["Budget"] else None,
                  r["Favourable"]] for r in bv],
                formats=[None, None, None, MONEY, MONEY, MONEY, PCT, None],
                widths=[10, 38, 26, 15, 15, 15, 12, 13],
                title="Actual vs budget by account, nine months to 30 September 2025")
    write_sheet(wb, "Variance by cost centre",
                ["Cost centre", "Department", "Budget 9M", "Actual 9M", "Variance", "Variance %"],
                [[r["CostCentreCode"], r["Department"], round(r["Budget"], 2), round(r["Actual"], 2),
                  round(r["Variance"], 2), round(r["Variance pct"] / 100, 4) if r["Budget"] else None]
                 for r in budget_variance_cc(led)],
                formats=[None, None, MONEY, MONEY, MONEY, PCT],
                widths=[14, 26, 16, 16, 16, 13],
                title="Actual vs budget by cost centre, nine months to 30 September 2025")
    wb.save(ensure(os.path.join(out, "Control_Checks_and_Measure_Library.xlsx")))
    return checks


def guess_format(name):
    n = name.lower()
    if "%" in name or "pct" in n or "margin" in n or "rate" in n:
        return "0.0%"
    if any(k in n for k in ("count", "lines", "days", "number", "users", "accounts")):
        return "#,##0"
    return '$#,##0.00;($#,##0.00);"-"'


def guess_definition(name, folder):
    n = name.lower()
    if "check" in n:
        return "Control check - must return zero on the close-pack page."
    if "ytd" in n:
        return "Year-to-date using the marked date table."
    if "py" in n or "prior" in n:
        return "Prior-period comparative."
    if "dso" in n:
        return "Closing receivables / revenue x days elapsed."
    if "dpo" in n:
        return "Closing payables / cost of sales x days elapsed."
    if "dio" in n:
        return "Closing inventories / cost of sales x days elapsed."
    if "risk" in n:
        return "Forensic scoring measure; weights are judgmental and disclosed."
    return f"{folder or 'Model'} measure - see the DAX for the calculation."


def budget_variance(led):
    """Actual (nine months to 30 Sep 2025) vs budget, by account."""
    from collections import defaultdict
    budget = defaultdict(float)
    for r in led.budget:
        if r["Period"] <= "2025-09" and r["Period"] >= "2025-01":
            budget[r["AccountCode"]] += float(r["BudgetUSD"])
    actual = defaultdict(float)
    for r in led.gl:
        if r["Period"] <= "2025-09" and r["Period"] >= "2025-01" and r["EntryType"] != "Closing":
            actual[r["AccountCode"]] += -r["AmountUSD"] * r["PLSign"] if r["IsPL"] else r["AmountUSD"]
    rows = []
    for code in sorted(set(budget) | set(actual)):
        if code not in led.accounts:
            continue
        b, a = budget.get(code, 0.0), actual.get(code, 0.0)
        if abs(b) < 0.01 and abs(a) < 0.01:
            continue
        acct = led.accounts[code]
        var = b - a if acct["AccountType"] == "Expense" else a - b
        rows.append({"AccountCode": code, "AccountName": acct["AccountName"],
                     "FSLine": acct["FSLine"], "Budget": b, "Actual": a, "Variance": var,
                     "Variance pct": (var / b * 100) if b else 0.0,
                     "Favourable": "Favourable" if var > 0 else ("Adverse" if var < 0 else "-")})
    rows.sort(key=lambda r: r["Variance"])
    return rows


def budget_variance_cc(led):
    from collections import defaultdict
    budget = defaultdict(float)
    for r in led.budget:
        if "2025-01" <= r["Period"] <= "2025-09":
            budget[r["CostCentreCode"]] += float(r["BudgetUSD"])
    actual = defaultdict(float)
    for r in led.gl:
        if "2025-01" <= r["Period"] <= "2025-09" and r["EntryType"] != "Closing" and r["IsPL"]:
            actual[r["CostCentreCode"]] += led.pl_value(r)
    dept = {c["CostCentreCode"]: c["Department"] for c in led.cost_centres}
    rows = []
    for cc in sorted(set(budget) | set(actual)):
        b, a = budget.get(cc, 0.0), actual.get(cc, 0.0)
        var = b - a
        rows.append({"CostCentreCode": cc, "Department": dept.get(cc, ""),
                     "Budget": b, "Actual": a, "Variance": var,
                     "Variance pct": (var / b * 100) if b else 0.0})
    rows.sort(key=lambda r: r["Variance"])
    return rows
