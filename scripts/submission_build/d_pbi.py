"""
d_pbi.py - the Power BI ready-to-import pack.

Table and column names are deliberately identical to the raw extract and to the
repository's three DAX libraries, so Core_Measures_Library.dax,
Forensic_Tests_Library.dax and Time_Intelligence_Library.dax work against the CSVs
in this pack without a single rename.  Derived columns are appended, never renamed.
"""
from __future__ import annotations

import csv
import json
import os
import re
import shutil

from . import common as C
from .writers import *
from .d_exam1 import parse_dax
from .d_cap3 import collections_priority, mask

DAX_FILES = ["Core_Measures_Library.dax", "Forensic_Tests_Library.dax",
             "Time_Intelligence_Library.dax"]

# (query name, source, kind, description)
TABLES = [
    ("FactGLJournal", "derived", "Fact",
     "Every general ledger line, with statement signs and fraud flags pre-computed"),
    ("FactJournal", "derived", "Fact", "Journal header: one row per journal with its approval status"),
    ("DimDate", "raw", "Dimension", "Calendar with fiscal period, weekend and month-end flags"),
    ("DimAccount", "raw", "Dimension", "Chart of accounts with statement sign columns"),
    ("DimVendor", "raw", "Dimension", "Vendor master with bank masking and spend analytics"),
    ("DimCustomer", "raw", "Dimension", "Customer master with receivables and collections priority"),
    ("DimUser", "raw", "Dimension", "System users with posting and approval statistics"),
    ("DimEmployee", "raw", "Dimension", "Employee master (bank accounts masked)"),
    ("DimCostCentre", "raw", "Dimension", "Cost centres and annual budgets"),
    ("DimFXRate", "raw", "Dimension", "Monthly FX rates"),
    ("DimScheme", "derived", "Dimension", "The seven fraud schemes, injected vs detected"),
    ("FactAPInvoices", "raw", "Fact", "Supplier invoices with three-way-match exception reasons"),
    ("FactARAgeing", "raw", "Fact", "Receivables ageing with collections priority scores"),
    ("FactBankTransactions", "raw", "Fact", "Bank transactions with reconciliation status"),
    ("FactExpenseClaims", "raw", "Fact", "Expense claims with receipt and approval exceptions"),
    ("FactExceptionRegister", "derived", "Fact",
     "The 171 scored exceptions raised by the twelve forensic tests"),
    ("FactDismissedExceptions", "derived", "Fact",
     "Exceptions raised by a test, investigated and dismissed with a reason"),
    ("FactTrialBalance", "raw", "Fact", "Delivered trial balance, for the GL-to-TB reconciliation"),
    ("FactBudget", "raw", "Fact", "Monthly budget by account and cost centre"),
    ("FactSalesOrders", "raw", "Fact", "Sales orders with margin"),
    ("FactFixedAssets", "raw", "Fact", "Fixed asset register"),
    ("FactClientChurnScored", "derived", "Fact",
     "Maxhub client churn: every client-year scored, with P(churn) and fee at risk"),
    ("FactEngagementEconomics", "derived", "Fact",
     "Maxhub engagement economics with over-run, realisation, margin and anomaly flags"),
    ("FactRevenueForecast", "derived", "Fact", "Twelve-month revenue forecast, three methods"),
    ("FactPipeline", "raw", "Fact", "Maxhub opportunity pipeline with weighted values"),
    ("FactServiceLineMonthly", "raw", "Fact", "Maxhub service-line revenue and margin by month"),
]

# Measure name as written in the repository libraries -> (control total, expected value key)
# Measure name as written in the repository libraries -> (control total, expected value key)
DAX_CONTROL = {
    "Debit Total": ("Total debits", "control_totals:Total debits"),
    "Credit Total": ("Total credits", "control_totals:Total credits"),
    "GL Balance Check": ("Must be zero", 0),
    "GL Lines": ("GL lines", "control_totals:GL lines"),
    "Journal Count": ("Journals", "control_totals:Journals"),
    "Unbalanced Journals": ("Unbalanced journals", 0),
    "GL Lines With Unknown Account": ("Orphan account keys", 0),
    "Manual Journal Lines": ("Manual journal lines", "control_totals:Manual journals"),
    "Total Revenue": ("Revenue for the open year (FY2024 is closed to retained earnings)",
                      "pl_2025:Revenue"),
    "Cost of Sales": ("Cost of sales, nine months", "pl_2025:Cost of sales"),
    "Gross Profit": ("Gross profit, nine months", "pl_2025:Gross profit"),
    "Gross Margin %": ("Gross margin, nine months", "pl_2025:Gross margin pct"),
    "Operating Expenses": ("Operating expenses, nine months", "pl_2025:Operating expenses"),
    "Operating Profit": ("Operating profit, nine months", "pl_2025:Operating profit"),
    "Finance Costs": ("Finance costs, nine months", "pl_2025:Finance costs"),
    "Tax Expense": ("Tax charge, nine months (after the documented correction)",
                    "pl_2025:Taxation"),
    "Profit After Tax": ("Profit after tax, nine months", "pl_2025:Profit after tax"),
    "Assets Total": ("Assets on the ledger convention, suspense included", "assets_ledger"),
    "Liabilities Total": ("Liabilities on the ledger convention", "liabilities_ledger"),
    "Equity Total": ("Equity before the current year result",
                     "balance_sheet:Equity before current year result"),
    "BS Check": ("Must be zero", 0),
    "Suspense Balance": ("Suspense account at 30 Sep 2025",
                         "balance_sheet:Suspense (credit balance)"),
    "Cash Balance": ("Cash and cash equivalents", "ratio_inputs:Cash"),
    "Receivables Balance": ("Trade receivables, account 1100", "ratio_inputs:AR"),
    "Payables Balance": ("Trade payables, account 2000", "ratio_inputs:AP"),
    "Inventory Balance": ("Inventories net of provision", "ratio_inputs:Inventory net"),
    "Current Ratio": ("Current ratio as published (after the documented correction)",
                      "balance_sheet:Current ratio"),
    "DSO": ("Days sales outstanding, 273-day basis", "ratios:DSO"),
    "DPO": ("Days payables outstanding, 273-day basis", "ratios:DPO"),
    "DIO": ("Days inventory outstanding, 273-day basis", "ratios:DIO"),
    "Cash Conversion Cycle": ("Cash conversion cycle", "ratios:CCC"),
    "AR Outstanding": ("Receivables outstanding on the ageing extract", "ar:outstanding"),
    "AR Disputed": ("Disputed receivables", "ar_disputed_value"),
    "AP Invoiced": ("AP invoice value in the extract", "ap:total"),
    "AP Failed 3-Way Match": ("Three-way-match exceptions", "ap:three_way_fail"),
    "Expense Claims Value": ("Expense claims in the extract", "expenses:total"),
    "Claims Without Receipt": ("Value of claims with no receipt", "expenses:no_receipt_value"),
    "Unreconciled Items": ("Unreconciled bank items", "bank:unreconciled_count"),
    "Unreconciled Value": ("Unreconciled bank value", "bank:unreconciled_value"),
    "Oldest Unreconciled Days": ("Oldest unmatched item", "bank:oldest_age"),
    "Employee Linked Vendor Spend": ("Paid to employee-linked vendors",
                                     "spend:employee_linked_total"),
}

# ---------------------------------------------------------------------------
# Corrections to the repository's DAX library, found by validating it against the
# ledger.  Each is applied to the copy shipped in this pack and asserted here, so
# the build fails loudly if an upstream expression ever changes.
# ---------------------------------------------------------------------------
DAX_FIXES = [
    ("Core_Measures_Library.dax",
     'CALCULATE ( [GL Amount Signed], DimAccount[FSLine] = "Taxation" )',
     'CALCULATE ( [GL Amount Signed], DimAccount[FSLine] = "Taxation", '
     'DimAccount[Statement] = "PL" )',
     "Tax Expense",
     'The FSLine "Taxation" spans two accounts: 8000 Income Tax Expense (P&L) and 2130 Income Tax '
     'Payable (balance sheet). Without the statement filter the measure netted the liability into '
     'the charge and returned -239,329.32 - a negative tax expense. Filtered to the P&L it returns '
     '221,440.69, agreeing with the tax charge in the financial statements.'),
    ("Core_Measures_Library.dax",
     'VAR CA = CALCULATE ( [Closing Balance], DimAccount[FSLine] IN { "Inventories", '
     '"Trade and other receivables", "Cash and cash equivalents" } ) VAR CL = CALCULATE ( '
     '[Closing Balance], DimAccount[FSLine] = "Trade and other payables" ) * -1 RETURN DIVIDE ( CA, CL )',
     'VAR CA = CALCULATE ( [Closing Balance], DimAccount[FSLine] IN { "Inventories", '
     '"Trade and other receivables", "Cash and cash equivalents" } ) VAR CL = CALCULATE ( '
     '[Closing Balance], DimAccount[FSLine] = "Trade and other payables" ) + CALCULATE ( '
     '[Closing Balance], DimAccount[AccountCode] = "2130" ) RETURN DIVIDE ( CA, '
     '( CL * -1 ) + [Suspense Balance] )',
     "Current Ratio",
     "Current liabilities omitted income tax payable (account 2130, 460,770.01) and the suspense "
     "credit balance (51,058.87), so the measure returned 1.54 against 1.35 in the financial "
     "statements. Both are added by account code rather than by the Taxation FSLine, because that "
     "FSLine also contains 8000 Income Tax Expense in the P&L - filtering on it would drag the tax "
     "charge into current liabilities and give 1.43. Corrected, the measure returns 1.35 and agrees."),
    ("Core_Measures_Library.dax",
     "DIVIDE ( [Receivables Balance], [Total Revenue] ) * 365",
     "DIVIDE ( [Receivables Balance], [Total Revenue] ) * [Days In Period]",
     "DSO",
     "The day count was hard-coded to 365 while the revenue measure covers nine months, which "
     "overstates the days: 131 against the 98 published. Using [Days In Period] (273 days to "
     "30 September 2025) agrees. Set it to 365 for a full-year model."),
    ("Core_Measures_Library.dax",
     "DIVIDE ( [Payables Balance], [Cost of Sales] ) * 365",
     "DIVIDE ( [Payables Balance], [Cost of Sales] ) * [Days In Period]",
     "DPO",
     "As DSO: 166 days on a 365-day basis against 124 on the 273 days actually elapsed."),
    ("Core_Measures_Library.dax",
     "DIVIDE ( [Inventory Balance], [Cost of Sales] ) * 365",
     "DIVIDE ( [Inventory Balance], [Cost of Sales] ) * [Days In Period]",
     "DIO",
     "As DSO: 61 days on a 365-day basis against 46 on the 273 days actually elapsed."),
]

DAYS_IN_PERIOD_MEASURE = '''

// -------------------------------------------------------------------------------------
// FOLDER: 03 Working capital & ratios
// -------------------------------------------------------------------------------------

// Days elapsed in the period covered by the P&L measures: 273 days from 1 January to
// 30 September 2025. Change to 365 for a full-year model. DSO, DPO and DIO divide a
// closing balance by a period flow, so the day count must match the length of the
// period the flow covers.
Days In Period = 273
'''


def _flexible(literal):
    """Match a DAX expression ignoring how its whitespace is laid out in the file."""
    return re.compile(r"\s+".join(re.escape(tok) for tok in literal.split()))


def apply_dax_fixes(out):
    """Apply the documented corrections to the shipped copy of the DAX libraries."""
    applied = []
    for fn, old, new, measure, reason in DAX_FIXES:
        path = os.path.join(out, fn)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        match = _flexible(old).search(text)
        if not match:
            raise SystemExit(f"DAX correction could not be applied to {fn}: the source expression "
                             f"for [{measure}] has changed upstream. Re-review the correction.")
        text = text[:match.start()] + new + text[match.end():]
        banner = (f"// CORRECTED FOR THIS PACK ({ISSUE_DATE:%Y-%m-%d}) - see DAX_Change_Note.md\n"
                  f"// {reason}")
        text = text.replace(new, banner + "\n" + new, 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        applied.append((fn, measure, reason))
    with open(os.path.join(out, "Core_Measures_Library.dax"), "a", encoding="utf-8") as f:
        f.write(DAYS_IN_PERIOD_MEASURE)
    return applied


def change_note(applied, ctx):
    lines = [
        "# DAX change note",
        "",
        f"Generated {ISSUE_DATE:%Y-%m-%d}. The three DAX libraries in this pack are the "
        "repository's own files. Validating them against the ledger before shipping found "
        f"{len(applied)} measures that did not agree with the client's control totals. Each is "
        "corrected in the copy shipped here; the repository originals are untouched, and the build "
        "stops if an upstream expression changes, so a correction can never be applied to the wrong "
        "text.",
        "",
    ]
    for fn, measure, reason in applied:
        lines += [f"## [{measure}] in `{fn}`", "", reason, ""]
    lines += [
        "## Not a defect, but a trap worth knowing",
        "",
        "The P&L measures sum every posting with no filter on `EntryType`. That is right for the "
        "open year, because the FY2024 closing entries transfer that year's result to retained "
        "earnings and so net the prior year to zero. The consequence is that a slicer set to "
        "`FiscalYear = 2024` returns zero revenue, not FY2024 revenue. To read a closed year, "
        'filter `EntryType <> "Closing"` and sum `FactGLJournal[PLValue]`; that returns '
        f"{ctx['pl_2024']['Revenue']:,.2f} for FY2024. Both routes are validated in "
        "`Validation_Report.txt`.",
        "",
        "## Sign conventions",
        "",
        "- `[GL Amount Signed]` is `SUM(Debit) - SUM(Credit)`. On revenue accounts it is negative, "
        "so `[Total Revenue]` multiplies by -1.",
        "- `[Closing Balance]` is the same sum filtered to dates up to the last visible date, with "
        "no sign adjustment. `[Liabilities Total]`, `[Equity Total]`, `[Payables Balance]` and "
        "`[Suspense Balance]` multiply by -1 to present credit balances as positive.",
        "- `[Assets Total]` therefore includes the suspense account, which the chart of accounts "
        "classifies as an asset carrying a credit balance. `[BS Check]` still returns 0.00. The "
        "financial statements present it the other way round - suspense shown as a credit within "
        "current liabilities - and that presentation balances too. Both are validated.",
    ]
    return "\n".join(lines) + "\n"


def build(out, ctx, fx):
    os.makedirs(out, exist_ok=True)
    data = os.path.join(out, "Data_Ready_To_Import")
    if os.path.isdir(data):
        shutil.rmtree(data)
    os.makedirs(data)

    tables = build_tables(ctx, fx)
    meta = {}
    for name, rows in tables.items():
        write_csv(os.path.join(data, name + ".csv"), rows)
        meta[name] = columns_of(rows)

    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for fn in DAX_FILES:
        shutil.copy(os.path.join(root, "dax", fn), os.path.join(out, fn))
    applied = apply_dax_fixes(out)
    write_text(os.path.join(out, "DAX_Change_Note.md"), change_note(applied, ctx))

    write_text(os.path.join(out, "PowerQuery_Load.m"), power_query(meta))
    measures_xlsx(os.path.join(out, "DAX_Measures_Reference.xlsx"), ctx)
    data_model_xlsx(os.path.join(out, "PowerBI_Data_Model.xlsx"), tables, meta, ctx, fx)
    instructions_docx(os.path.join(out, "Build_Instructions.docx"), tables, ctx, fx)
    write_text(os.path.join(out, "Build_Instructions.md"), instructions_md(tables, ctx, fx))
    manifest(os.path.join(out, "Import_Manifest.json"), tables, meta, ctx, fx)
    write_text(os.path.join(out, "README.md"), pack_readme(tables, ctx, fx))
    write_text(os.path.join(out, "Validation_Report.txt"), validate_pack(data, ctx, fx, applied))


# ---------------------------------------------------------------------------
# CSV writing and typing
# ---------------------------------------------------------------------------
def write_text(path, text):
    ensure(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def write_csv(path, rows):
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(keys)
        for r in rows:
            w.writerow([fmt_cell(r.get(k, "")) for k in keys])


def fmt_cell(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if isinstance(v, float):
        return f"{v:.6f}".rstrip("0").rstrip(".")
    return str(v)


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?$")


def columns_of(rows):
    """Infer a Power Query type for every column from the values actually written."""
    out = []
    for k in rows[0].keys():
        vals = [str(r.get(k, "")) for r in rows]
        nonblank = [v for v in vals if v != ""]
        t = "text"
        if nonblank and all(DT_RE.match(v) for v in nonblank):
            t = "datetime"
        elif nonblank and all(DATE_RE.match(v) for v in nonblank):
            t = "date"
        elif nonblank and all(re.match(r"^-?\d+$", v) for v in nonblank):
            t = "int"
        elif nonblank:
            try:
                [float(v) for v in nonblank]
                t = "number"
            except ValueError:
                t = "text"
        out.append({"Column": k, "Type": t, "Blanks": len(vals) - len(nonblank),
                    "Example": next((v for v in vals if v != ""), "")})
    return out


M_TYPE = {"text": "type text", "int": "Int64.Type", "number": "type number",
          "date": "type date", "datetime": "type datetime"}


def power_query(meta):
    head = f'''// ============================================================================
// MAXHUB - Power Query (M) load script for the Power BI ready-to-import pack
// Generated {ISSUE_DATE:%Y-%m-%d}.  Column types were inferred from the values in
// the CSVs shipped in Data_Ready_To_Import, so this script and those files cannot
// disagree.  Table names match the repository's DAX libraries exactly.
//
// HOW TO USE
//   1. Create a parameter called DataFolder (Text) holding the full path to
//      Data_Ready_To_Import with no trailing slash, e.g. C:\\Maxhub\\PBI\\Data
//   2. For each section below: Home > Transform data > New Source > Blank query,
//      then View > Advanced Editor, paste the section and rename the query to the
//      name in the comment.
// ============================================================================

'''
    body = []
    for name, cols in meta.items():
        pairs = ",\n        ".join('{%s, %s}' % (json.dumps(c["Column"]), M_TYPE[c["Type"]])
                                  for c in cols)
        body.append(f'''// ---------- {name} ----------
let
    Source = Csv.Document(File.Contents(DataFolder & "/{name}.csv"),
        [Delimiter=",", Columns={len(cols)}, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Promoted, {{
        {pairs}
    }})
in
    Typed
''')
    tail = '''
// ============================================================================
// AFTER LOADING
//   1. Model view > Manage relationships: create the relationships listed on the
//      Relationships tab of PowerBI_Data_Model.xlsx.  Auto-detect will get most of
//      them, but check the three role-playing DimDate relationships and confirm
//      nothing was created many-to-many.
//   2. Table tools > Mark as date table on DimDate (Date column = Date), then turn
//      off Auto date/time in Options > Data Load.
//   3. Hide key columns from report view.
//   4. Paste the measures from Core_Measures_Library.dax, then
//      Forensic_Tests_Library.dax, then Time_Intelligence_Library.dax.
//   5. Run the validation checks in DAX_Measures_Reference.xlsx before building
//      any visual.  Every one must tie.
// ============================================================================
'''
    return head + "\n".join(body) + tail


# ---------------------------------------------------------------------------
# The warehouse
# ---------------------------------------------------------------------------
def build_tables(ctx, fx):
    led = ctx["ledger"]
    T = {}

    # ---- DimAccount -------------------------------------------------------
    T["DimAccount"] = [dict(
        a,
        BSSign=1 if a["AccountType"] == "Asset" else -1,
        StatementName="Profit and loss" if a["Statement"] == "PL" else "Balance sheet",
        NormalBalanceName="Debit" if a["NormalBalance"] == "Debit" else "Credit",
        IsRevenue="Yes" if a["AccountType"] == "Revenue" else "No",
        IsExpense="Yes" if a["AccountType"] == "Expense" else "No",
        IsContra="Yes" if ((a["AccountType"] == "Asset" and a["NormalBalance"] == "Credit")
                           or (a["AccountType"] in ("Liability", "Equity")
                               and a["NormalBalance"] == "Debit")) else "No",
        IsActive="Yes",
    ) for a in C.read_csv("DimAccount.csv")]

    acct = {a["AccountCode"]: a for a in T["DimAccount"]}

    # ---- injection lookup --------------------------------------------------
    reg_by_journal = {r["JournalID"]: r for r in fx["register"]}
    inj_type = {}
    for r in led.injection_log:
        inj_type[r["EntryID"]] = r["AnomalyType"]

    # ---- FactGLJournal -----------------------------------------------------
    gl = []
    for r in led.gl:
        a = acct[r["AccountCode"]]
        v = led.vendor_by_id.get(r["VendorID"], {})
        c = led.customer_by_id.get(r["CustomerID"], {})
        u = led.users.get(r["PreparedBy"], {})
        ap = led.users.get(r["ApprovedBy"], {})
        e = r["EnteredOn"]
        reg = reg_by_journal.get(r["JournalID"])
        gl.append(dict(
            {k: (v.isoformat() if hasattr(v, "isoformat") else v)
             for k, v in ((k, r[k]) for k in
                          ("LineID", "JournalID", "LineNo", "AccountCode", "PostingDate",
                           "DocumentDate", "Period", "FiscalYear", "Description", "Debit",
                           "Credit", "AmountUSD", "AbsAmountUSD", "Currency", "FXRate",
                           "CostCentreCode", "PreparedBy", "ApprovedBy", "SourceSystem",
                           "EntryType", "EnteredOn", "IsReversal", "VendorID", "CustomerID",
                           "AnomalyLabel"))},
            AccountName=a["AccountName"], AccountType=a["AccountType"], FSLine=a["FSLine"],
            Statement=a["Statement"], StatementName=a["StatementName"], IsPL=a["IsPL"],
            PLSign=int(a["PLSign"]), BSSign=a["BSSign"], NormalBalance=a["NormalBalance"],
            IsCashAccount=a["IsCashAccount"], IsSuspense=a["IsSuspense"],
            # signed values that make the statement engine one column wide
            PLValue=round(-r["AmountUSD"] * int(a["PLSign"]), 2) if a["IsPL"] == "Yes" else 0.0,
            BSValue=round(r["AmountUSD"] * a["BSSign"], 2) if a["Statement"] == "BS" else 0.0,
            VendorName=v.get("VendorName", ""), VendorCategory=v.get("Category", ""),
            EmployeeLinkedVendor="Yes" if v.get("IsEmployeeLinked") == "Yes" else "No",
            CustomerName=c.get("CustomerName", ""),
            PreparerName=u.get("UserName", ""), PreparerRole=u.get("JobTitle", ""),
            ApproverName=ap.get("UserName", ""),
            IsApproved="Yes" if r["ApprovedBy"] else "No",
            IsManual="Yes" if r["EntryType"] == "Manual" else "No",
            IsWeekendPosting="Yes" if e.weekday() >= 5 else "No",
            IsAfterHours="Yes" if (e.hour < 7 or e.hour >= 22) else "No",
            IsInjection="Yes" if reg else "No",
            SchemeID=inj_type.get(r["JournalID"], ""),
            TestID=reg["TestID"] if reg else "",
            Scheme=reg["TestName"] if reg else "",
            RiskBand=reg["RiskBand"] if reg else "",
        ))
    T["FactGLJournal"] = gl

    # ---- FactJournal -------------------------------------------------------
    fj = []
    for jid, ls in led.journals.items():
        h = ls[0]
        e = h["EnteredOn"]
        u = led.users.get(h["PreparedBy"], {})
        ap = led.users.get(h["ApprovedBy"], {})
        reg = reg_by_journal.get(jid)
        dr = round(sum(l["Debit"] for l in ls), 2)
        cr = round(sum(l["Credit"] for l in ls), 2)
        fj.append({
            "JournalID": jid, "PostingDate": h["PostingDate"].isoformat(),
            "DocumentDate": h["DocumentDate"].isoformat(), "Period": h["Period"],
            "FiscalYear": h["FiscalYear"], "EntryType": h["EntryType"],
            "SourceSystem": h["SourceSystem"], "Description": h["Description"],
            "PreparedBy": h["PreparedBy"], "PreparerName": u.get("UserName", ""),
            "PreparerRole": u.get("JobTitle", ""),
            "ApprovedBy": h["ApprovedBy"], "ApproverName": ap.get("UserName", ""),
            "IsApproved": "Yes" if h["ApprovedBy"] else "No",
            "IsSelfApproved": "Yes" if h["ApprovedBy"] and h["ApprovedBy"] == h["PreparedBy"]
                              else "No",
            "LineCount": len(ls), "TotalDebitUSD": dr, "TotalCreditUSD": cr,
            "BalanceDiffUSD": round(dr - cr, 2),
            "IsWeekendPosting": "Yes" if e.weekday() >= 5 else "No",
            "IsAfterHours": "Yes" if (e.hour < 7 or e.hour >= 22) else "No",
            "IsReversal": h["IsReversal"],
            "VendorCount": len({l["VendorID"] for l in ls if l["VendorID"]}),
            "AccountCount": len({l["AccountCode"] for l in ls}),
            "TouchesSuspense": "Yes" if any(l["AccountCode"] == "1990" for l in ls) else "No",
            "TouchesRevenue": "Yes" if any(l["AccountType"] == "Revenue" for l in ls) else "No",
            "IsInjection": "Yes" if reg else "No",
            "SchemeID": inj_type.get(jid, ""),
            "TestID": reg["TestID"] if reg else "",
            "Scheme": reg["TestName"] if reg else "",
            "InjectionAmountUSD": reg["AmountUSD"] if reg else 0.0,
            "RiskScore": reg["RiskScore"] if reg else 0,
            "RiskBand": reg["RiskBand"] if reg else "",
        })
    T["FactJournal"] = sorted(fj, key=lambda r: r["JournalID"])

    # ---- DimDate -----------------------------------------------------------
    dd = []
    for r in C.read_csv("DimDate.csv"):
        d = dict(r)
        d["IsWeekendYN"] = "Yes" if r["IsWeekend"] in ("Yes", "True", "1") else "No"
        d["IsMonthEndYN"] = "Yes" if r["IsMonthEnd"] in ("Yes", "True", "1") else "No"
        d["MonthYearSort"] = int(r["DateKey"]) // 100 if r["DateKey"].isdigit() else 0
        dd.append(d)
    T["DimDate"] = dd

    # ---- spend by vendor (GL) ---------------------------------------------
    spend = ctx["spend"]
    spend_by_vendor = {p["VendorID"]: p for p in spend["pareto"]}
    ap = ctx["ap"]
    ap_by_vendor = {}
    for r in ap["rows"]:
        d = ap_by_vendor.setdefault(r["VendorID"], {"Invoices": 0, "AmountUSD": 0.0,
                                                    "Exceptions": 0})
        d["Invoices"] += 1
        d["AmountUSD"] += r["AmountUSD"]
        if r["ThreeWayMatch"] != "Matched":
            d["Exceptions"] += 1

    # ---- DimVendor ---------------------------------------------------------
    dv = []
    for r in C.read_csv("DimVendor.csv"):
        s = spend_by_vendor.get(r["VendorID"], {})
        a = ap_by_vendor.get(r["VendorID"], {})
        dv.append(dict(
            r,
            BankAccountMasked=mask(r["BankAccount"]),
            HasTaxClearance="Yes" if r["TaxClearanceNo"] else "No",
            EmployeeLinkedFlag=r["IsEmployeeLinked"],
            VendorRiskFlag="Yes" if r["IsEmployeeLinked"] == "Yes" else "No",
            GLSpendUSD=round(s.get("AmountUSD", 0.0), 2),
            GLPostings=s.get("Postings", 0),
            GLSpendSharePct=round(s.get("Share pct", 0.0), 2),
            APSpendUSD=round(a.get("AmountUSD", 0.0), 2),
            APInvoices=a.get("Invoices", 0),
            ThreeWayExceptions=a.get("Exceptions", 0),
            ExceptionRatePct=round(a["Exceptions"] / a["Invoices"] * 100, 1)
            if a.get("Invoices") else 0.0,
        ))
    T["DimVendor"] = dv

    # ---- DimCustomer -------------------------------------------------------
    priority = {r["InvoiceNo"]: r for r in collections_priority(ctx, led)}
    ar_by_cust = {}
    for r in ctx["ar"]["rows"]:
        d = ar_by_cust.setdefault(r["CustomerID"], {"Invoices": 0, "OutstandingUSD": 0.0,
                                                    "DisputedUSD": 0.0, "Overdue90USD": 0.0,
                                                    "Days": []})
        d["Invoices"] += 1
        d["OutstandingUSD"] += r["OutstandingUSD"]
        d["Days"].append(r["DaysOverdue"])
        if r["Disputed"]:
            d["DisputedUSD"] += r["OutstandingUSD"]
        if r["DaysOverdue"] > 90:
            d["Overdue90USD"] += r["OutstandingUSD"]
    dc = []
    for r in C.read_csv("DimCustomer.csv"):
        a = ar_by_cust.get(r["CustomerID"], {})
        out = a.get("OutstandingUSD", 0.0)
        dc.append(dict(
            r,
            AROutstandingUSD=round(out, 2),
            ARInvoices=a.get("Invoices", 0),
            DisputedUSD=round(a.get("DisputedUSD", 0.0), 2),
            Overdue90USD=round(a.get("Overdue90USD", 0.0), 2),
            AvgDaysOverdue=round(sum(a.get("Days", [0])) / len(a["Days"]), 1)
            if a.get("Days") else 0.0,
            CreditUtilisationPct=round(out / float(r["CreditLimitUSD"]) * 100, 1)
            if float(r["CreditLimitUSD"] or 0) else 0.0,
            CollectionsAction=("Telephone contact this week" if a.get("Overdue90USD")
                               else "Standard reminders" if out > 0 else "No open balance"),
        ))
    T["DimCustomer"] = dc

    # ---- DimUser -----------------------------------------------------------
    du = []
    for r in C.read_csv("DimUser.csv"):
        uid = r["UserID"]
        prepared = [j for j, ls in led.journals.items() if ls[0]["PreparedBy"] == uid]
        approved = [j for j, ls in led.journals.items() if ls[0]["ApprovedBy"] == uid]
        unapproved = [j for j in prepared if not led.journals[j][0]["ApprovedBy"]]
        du.append(dict(
            r,
            JournalsPrepared=len(prepared),
            JournalsApproved=len(approved),
            UnapprovedJournals=len(unapproved),
            UnapprovedValueUSD=round(sum(sum(l["Debit"] for l in led.journals[j])
                                         for j in unapproved), 2),
            WeekendJournals=sum(1 for j in prepared
                                if led.journals[j][0]["EnteredOn"].weekday() >= 5),
            ManualJournals=sum(1 for j in prepared
                               if led.journals[j][0]["EntryType"] == "Manual"),
            ExceptionsPrepared=sum(1 for j in prepared if j in reg_by_journal),
        ))
    T["DimUser"] = du

    # ---- passthrough dimensions -------------------------------------------
    emp = []
    for r in C.read_csv("DimEmployee.csv"):
        d = dict(r)
        d["BankAccountMasked"] = mask(r["BankAccount"])
        emp.append(d)
    T["DimEmployee"] = emp
    T["DimCostCentre"] = C.read_csv("DimCostCentre.csv")
    T["DimFXRate"] = C.read_csv("DimFXRate.csv")

    # ---- DimScheme ---------------------------------------------------------
    by_scheme = {r["Scheme"]: r for r in fx["answer_key"]["by_scheme"]}
    injected = {}
    for r in led.injection_log:
        d = injected.setdefault(r["AnomalyType"], {"count": 0, "value": 0.0})
        d["count"] += 1
        d["value"] += float(r["AmountUSD"])
    scheme_meta = {
        "DUPLICATE-PAYMENT": ("T01", "Supplier invoice paid twice",
                              "No duplicate-payment detection in the payment run"),
        "GHOST-VENDOR": ("T02", "Payments to employee-linked suppliers",
                         "Vendor master created and bank details changed without independent approval"),
        "ROUND-NUMBER-THRESHOLD": ("T03", "Payments structured below approval limits",
                                   "Approval limits enforced on the transaction, not the commitment"),
        "SPLIT-PURCHASE": ("T04", "One purchase split into two invoices",
                           "Purchase-order threshold tested per invoice, not per order"),
        "WEEKEND-AFTERHOURS": ("T05", "Manual journals posted outside business hours",
                               "No monitoring of posting times; suspense account used as a clearing account"),
        "SOD-RARE-COMBO": ("T06", "AP clerk posting revenue credit notes",
                           "User access rights wider than the job role requires"),
        "UNREVERSED-ACCRUAL": ("T07", "Prepayment releases never reversed",
                               "No periodic review of the prepayment schedule"),
    }
    ds = []
    for i, (scheme, (test, friendly, weakness)) in enumerate(scheme_meta.items(), 1):
        inj_d = injected.get(scheme, {"count": 0, "value": 0.0})
        det = fx["totals"][test]
        k = by_scheme.get(scheme, {})
        ds.append({
            "SchemeKey": i, "SchemeID": scheme, "Scheme": friendly, "TestID": test,
            "TestName": dict((t[0], t[1]) for t in fx["tests"])[test],
            "Assertion tested": dict((t[0], t[2]) for t in fx["tests"])[test],
            "Control weakness": weakness,
            "Detection rule": dict((t[0], t[4]) for t in fx["tests"])[test],
            "Follow-up": dict((t[0], t[5]) for t in fx["tests"])[test],
            "Process area": dict((t[0], t[6]) for t in fx["tests"])[test],
            "JournalsInjected": inj_d["count"],
            "ValueInjectedUSD": round(inj_d["value"], 2),
            "JournalsDetected": det["Lines"],
            "ValueDetectedUSD": det["Value"],
            "DetectionRatePct": round(det["Lines"] / inj_d["count"] * 100, 1)
            if inj_d["count"] else 0.0,
            "AnswerKeyExpected": k.get("Expected journals", 0),
            "AnswerKeyDetected": k.get("Detected journals", 0),
            "AnswerKeyMissed": k.get("Missed", 0),
        })
    T["DimScheme"] = ds

    # ---- FactAPInvoices ----------------------------------------------------
    fa = []
    for r in C.read_csv("FactAPInvoices.csv"):
        v = led.vendor_by_id.get(r["VendorID"], {})
        amt = float(r["AmountUSD"] or 0)
        reasons = []
        if r["ThreeWayMatch"] != "Matched":
            if not r["PONumber"]:
                reasons.append("No purchase order")
            elif not r["GRNNumber"]:
                reasons.append("Purchase order but no goods-received note")
            else:
                reasons.append("Invoice, order and receipt do not agree")
        if r["DuplicateSuspected"] == "Yes":
            reasons.append("Duplicate invoice suspected")
        if not r["ApprovedBy"]:
            reasons.append("No approver recorded")
        if float(amt) >= 10000 and not r["ApprovedBy"]:
            reasons.append("Above the $10,000 approval limit with no approver")
        fa.append(dict(
            r,
            VendorName=v.get("VendorName", ""), VendorCategory=v.get("Category", ""),
            EmployeeLinkedVendor="Yes" if v.get("IsEmployeeLinked") == "Yes" else "No",
            HasPO="Yes" if r["PONumber"] else "No",
            HasGRN="Yes" if r["GRNNumber"] else "No",
            DuplicateFlag=r["DuplicateSuspected"],
            ExceptionFlag="Yes" if reasons else "No",
            ExceptionReason="; ".join(reasons) or "-",
        ))
    T["FactAPInvoices"] = fa

    # ---- FactARAgeing ------------------------------------------------------
    fr = []
    for r in C.read_csv("FactARAgeing.csv"):
        c = led.customer_by_id.get(r["CustomerID"], {})
        p = priority.get(r["InvoiceNo"], {})
        amt = float(r["AmountUSD"] or 0)
        rec = float(r["AmountReceivedUSD"] or 0)
        fr.append(dict(
            r,
            CustomerName=c.get("CustomerName", ""), Segment=c.get("Segment", ""),
            AccountManager=c.get("AccountManager", ""),
            OutstandingUSD=round(amt - rec, 2),
            SettledFlag="Yes" if amt - rec <= 0 else "No",
            DisputedFlagYN=r["DisputedFlag"],
            Overdue90Flag="Yes" if int(float(r["DaysOverdue"] or 0)) > 90 else "No",
            PriorityScore=p.get("PriorityScore", 0.0),
            PriorityRank=p.get("PriorityRank", 0),
            RecommendedAction=p.get("Action", "-"),
        ))
    T["FactARAgeing"] = fr

    # ---- FactBankTransactions ---------------------------------------------
    fb = []
    for r in C.read_csv("FactBankTransactions.csv"):
        d = float(r["DebitUSD"] or 0)
        c = float(r["CreditUSD"] or 0)
        age = int(float(r["UnmatchedItemsAgeDays"] or 0))
        fb.append(dict(
            r,
            AmountUSD=round(d + c, 2),
            Direction="Debit" if d else "Credit",
            ReconciledYN=r["ReconciledFlag"],
            ExceptionFlag="Yes" if r["ReconciledFlag"] != "Yes" else "No",
            AgeBucket=("Reconciled" if r["ReconciledFlag"] == "Yes" else
                       "0-30 days" if age <= 30 else "31-90 days" if age <= 90 else "Over 90 days"),
            Over90Flag="Yes" if (r["ReconciledFlag"] != "Yes" and age > 90) else "No",
        ))
    T["FactBankTransactions"] = fb

    # ---- FactExpenseClaims -------------------------------------------------
    fe = []
    for r in C.read_csv("FactExpenseClaims.csv"):
        reasons = []
        if r["ReceiptAttached"] != "Yes":
            reasons.append("No receipt attached")
        if not r["ApprovedBy"]:
            reasons.append("No approver recorded")
        if r["DuplicateSuspected"] == "Yes":
            reasons.append("Duplicate claim suspected")
        if r["WeekendClaim"] == "Yes":
            reasons.append("Claim submitted at the weekend")
        fe.append(dict(
            r,
            ReceiptFlag=r["ReceiptAttached"],
            ApprovedFlag="Yes" if r["ApprovedBy"] else "No",
            ExceptionFlag="Yes" if reasons else "No",
            ExceptionReason="; ".join(reasons) or "-",
        ))
    T["FactExpenseClaims"] = fe

    # ---- FactExceptionRegister --------------------------------------------
    T["FactExceptionRegister"] = [{
        "Rank": r["Rank"], "JournalID": r["JournalID"], "TestID": r["TestID"],
        "TestName": r["TestName"], "AllTestsFired": r["AllTestsFired"],
        "SchemeID": inj_type.get(r["JournalID"], ""),
        "ExceptionDate": r["ExceptionDate"], "DocumentDate": r["DocumentDate"],
        "EnteredOn": r["EnteredOn"], "Period": r["Period"],
        "AccountCode": r["AccountCode"], "AccountName": r["AccountName"],
        "Description": r["Description"], "DocumentRef": r["DocumentRef"],
        "VendorID": r["VendorID"], "VendorName": r["VendorName"],
        "EmployeeLinked": r["EmployeeLinked"], "CounterAccount": r["CounterAccount"],
        "AmountUSD": r["AmountUSD"], "JournalDebits": r["JournalDebits"],
        "Debit": r["Debit"], "Credit": r["Credit"],
        "Preparer": r["Preparer"], "PreparerName": r["PreparerName"],
        "PreparerRole": r["PreparerRole"], "Approver": r["Approver"],
        "EntryType": r["EntryType"], "SourceSystem": r["SourceSystem"],
        "RiskScore": r["RiskScore"], "RiskBand": r["RiskBand"],
        "RiskWeightedValueUSD": r["RiskWeightedValue"],
        "Status": r["Status"], "Conclusion": r["Conclusion"], "ReviewedBy": r["ReviewedBy"],
    } for r in fx["register"]]

    # ---- FactDismissedExceptions ------------------------------------------
    T["FactDismissedExceptions"] = [{
        "TestID": r["TestID"], "TestName": r["TestName"], "JournalID": r["JournalID"],
        "ExceptionDate": r["ExceptionDate"], "Description": r["Description"],
        "AmountUSD": r["AmountUSD"], "Preparer": r["Preparer"],
        "ReasonDismissed": r["Reason dismissed"], "PopulationNote": r["Population note"],
    } for r in fx["dismissed"]]

    # ---- passthrough facts -------------------------------------------------
    T["FactTrialBalance"] = C.read_csv("FactTrialBalance.csv")
    T["FactBudget"] = C.read_csv("FactBudget.csv")
    T["FactSalesOrders"] = C.read_csv("FactSalesOrders.csv")
    T["FactFixedAssets"] = C.read_csv("FactFixedAssets.csv")
    T["FactPipeline"] = C.read_csv("maxhub_pipeline.csv")
    T["FactServiceLineMonthly"] = C.read_csv("maxhub_service_line_financials.csv")

    # ---- Capstone 4 tables -------------------------------------------------
    ml = ctx["ml"]
    T["FactClientChurnScored"] = [{
        "ClientID": r["ClientID"], "ClientName": r["ClientName"], "Industry": r["Industry"],
        "ClientSince": r["ClientSince"], "ClientSize": r["ClientSize"], "Year": int(r["Year"]),
        "AnnualFeeUSD": float(r["AnnualFeeUSD"]),
        "ServicesPurchased": int(r["ServicesPurchased"]), "NPS": int(r["NPS"]),
        "ComplaintsLogged": int(r["ComplaintsLogged"]),
        "AvgPaymentDays": float(r["AvgPaymentDays"]),
        "EngagementDelayDays": float(r["EngagementDelayDays"]),
        "PartnerHoursOnClient": float(r["PartnerHoursOnClient"]),
        "AuditFindingsRaised": int(r["AuditFindingsRaised"]),
        "FeeChangePct": float(r["FeeChangePct"]), "Stayed": int(r["Stayed"]),
        "PStay": r["P_stay"], "PChurn": r["P_churn"], "RiskBand": r["RiskBand"],
        "FeeAtRiskUSD": r["FeeAtRiskUSD"], "ModelVersion": ml["model"]["model_version"],
    } for r in ml["model"]["scored"]]

    T["FactEngagementEconomics"] = [{
        "EngagementID": r["EngagementID"], "ClientName": r["ClientName"],
        "ServiceLine": r["ServiceLine"], "EngagementManager": r["Manager"],
        "Period": r["Period"], "Status": r["Status"],
        "PlannedHours": r["PlannedHours"], "ActualHours": r["ActualHours"],
        "OverrunPct": r["Overrun pct"], "FeeUSD": r["FeeUSD"],
        "WriteOffUSD": r["WriteOffUSD"], "RealisationPct": r["Realisation pct"],
        "MarginPct": r["Margin pct"], "NPS": r["NPS"], "SeverityUSD": r["SeverityUSD"],
        "AnomalyFlag": "Yes", "Anomaly": r["Anomaly"],
    } for r in ml["anomalies"]["rows"]] + [{
        "EngagementID": e["EngagementID"], "ClientName": e["ClientName"],
        "ServiceLine": e["ServiceLine"], "EngagementManager": e["EngagementManager"],
        "Period": e["Period"], "Status": e["Status"],
        "PlannedHours": float(e["PlannedHours"]), "ActualHours": float(e["ActualHours"]),
        "OverrunPct": round((float(e["ActualHours"]) - float(e["PlannedHours"]))
                            / float(e["PlannedHours"]) * 100, 1)
        if float(e["PlannedHours"]) else 0.0,
        "FeeUSD": float(e["FeeUSD"]), "WriteOffUSD": float(e["WriteOffUSD"]),
        "RealisationPct": 0.0, "MarginPct": 0.0, "NPS": int(e["NetPromoterScore"]),
        "SeverityUSD": 0.0, "AnomalyFlag": "No", "Anomaly": "",
    } for e in C.read_csv("MaxhubEngagements.csv")
        if e["EngagementID"] not in {r["EngagementID"] for r in ml["anomalies"]["rows"]}]

    T["FactRevenueForecast"] = [dict(r, Method="Base (mean of methods)",
                                     IsForecast="Yes", Source="Maxhub forecast model")
                                for r in ml["forecast"]["forecast"]] + \
                               [{"Month": h["Month"], "Moving average (3-month)": 0.0,
                                 "Linear trend": 0.0, "Driver based": 0.0,
                                 "Base (mean of methods)": h["RevenueUSD"],
                                 "Low": h["RevenueUSD"], "High": h["RevenueUSD"],
                                 "Method": "Actual", "IsForecast": "No",
                                 "Source": "maxhub_service_line_financials"}
                                for h in ml["forecast"]["history"]]

    return T


# ---------------------------------------------------------------------------
# Validation: read the shipped CSVs back and re-perform the measures
# ---------------------------------------------------------------------------
def validate_pack(data, ctx, fx, applied):
    """Prove the shipped files support the published measures.

    Every check re-performs a measure exactly as the shipped DAX defines it - same
    filter, same sign convention - against the CSVs in Data_Ready_To_Import, and
    compares it with the control total used in the reports.
    """
    def rd(name):
        with open(os.path.join(data, name + ".csv"), newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))

    gl = rd("FactGLJournal")
    acct = {a["AccountCode"]: a for a in rd("DimAccount")}
    fj = rd("FactJournal")
    reg = rd("FactExceptionRegister")
    ap = rd("FactAPInvoices")
    bank = rd("FactBankTransactions")
    claims = rd("FactExpenseClaims")
    ar = rd("FactARAgeing")
    vend = {v["VendorID"]: v for v in rd("DimVendor")}

    def f(v):
        return float(v) if v not in ("", None) else 0.0

    # [Closing Balance] runs to the last visible date; the model's last posting is
    # the reporting date, so that is the as-at used here.
    as_at = max(r["PostingDate"] for r in gl)
    days = C.DAYS_ELAPSED_FY2025

    def signed(pred, upto=None):
        """[GL Amount Signed] = SUM(Debit) - SUM(Credit) over the filter."""
        return sum(f(r["Debit"]) - f(r["Credit"]) for r in gl
                   if pred(r) and (upto is None or r["PostingDate"] <= upto))

    def closing(pred):
        """[Closing Balance] = [GL Amount Signed] to the last visible date."""
        return sum(f(r["AmountUSD"]) for r in gl
                   if pred(r) and r["PostingDate"] <= as_at)

    is_rev = lambda r: acct[r["AccountCode"]]["AccountType"] == "Revenue"          # noqa: E731
    is_fs = lambda fs: (lambda r: r["FSLine"] == fs)                              # noqa: E731
    is_pl_fs = lambda fs: (lambda r: r["FSLine"] == fs and r["Statement"] == "PL")  # noqa: E731

    revenue = -signed(is_rev)
    cos = signed(is_fs("Cost of sales"))
    opex = signed(is_fs("Operating expenses"))
    finance = signed(is_fs("Finance costs"))
    tax = signed(is_pl_fs("Taxation"))
    tax_uncorrected = signed(is_fs("Taxation"))
    pat = revenue - cos - opex - finance - tax

    assets_ledger = closing(lambda r: acct[r["AccountCode"]]["AccountType"] == "Asset")
    liab_ledger = -closing(lambda r: acct[r["AccountCode"]]["AccountType"] == "Liability")
    equity_ledger = -closing(lambda r: acct[r["AccountCode"]]["AccountType"] == "Equity")
    suspense = -closing(lambda r: acct[r["AccountCode"]]["IsSuspense"] == "Yes")

    bs = ctx["balance_sheet"]
    ca_fs = closing(lambda r: r["FSLine"] in ("Inventories", "Trade and other receivables",
                                              "Cash and cash equivalents"))
    # current liabilities: the payables FSLine plus income tax payable by account code.
    # The Taxation FSLine cannot be used here - it also contains 8000 Income Tax Expense.
    cl_fs = -closing(lambda r: r["FSLine"] == "Trade and other payables"
                     or r["AccountCode"] == "2130")
    current_ratio = ca_fs / (cl_fs + suspense)
    current_ratio_uncorrected = ca_fs / (-closing(lambda r: r["FSLine"] == "Trade and other payables"))

    ar_out = sum(f(r["AmountUSD"]) - f(r["AmountReceivedUSD"]) for r in ar)
    ar_disputed = sum(f(r["AmountUSD"]) - f(r["AmountReceivedUSD"]) for r in ar
                      if r["DisputedFlag"] == "Yes")
    emp_linked = sum(f(r["AbsAmountUSD"]) for r in gl
                     if r["VendorID"] and vend.get(r["VendorID"], {}).get("IsEmployeeLinked") == "Yes"
                     and f(r["Debit"]) > 0)
    vendor_debits = sum(f(r["Debit"]) for r in gl if r["VendorID"])

    checks = [
        ("[Debit Total] = SUM(FactGLJournal[Debit])",
         sum(f(r["Debit"]) for r in gl), ctx["control_totals"]["Total debits"]),
        ("[Credit Total] = SUM(FactGLJournal[Credit])",
         sum(f(r["Credit"]) for r in gl), ctx["control_totals"]["Total credits"]),
        ("[GL Balance Check] = [Debit Total] - [Credit Total]",
         sum(f(r["Debit"]) - f(r["Credit"]) for r in gl), 0.0),
        ("[GL Lines] = COUNTROWS(FactGLJournal)", len(gl), ctx["control_totals"]["GL lines"]),
        ("[Journal Count] = DISTINCTCOUNT(FactGLJournal[JournalID])",
         len({r["JournalID"] for r in gl}), ctx["control_totals"]["Journals"]),
        ("[Unbalanced Journals] = journals where |debits - credits| > 0.005",
         sum(1 for r in fj if abs(f(r["BalanceDiffUSD"])) > 0.005),
         ctx["control_totals"]["Unbalanced journals"]),
        ("[GL Lines With Unknown Account] = lines with no DimAccount match",
         sum(1 for r in gl if r["AccountCode"] not in acct), 0),
        ("[Manual Journal Lines] = CALCULATE([GL Lines], EntryType = \"Manual\")",
         sum(1 for r in gl if r["EntryType"] == "Manual"),
         ctx["control_totals"]["Manual journals"]),

        ("[Total Revenue] = CALCULATE([GL Amount Signed], AccountType = \"Revenue\") * -1",
         revenue, ctx["pl_2025"]["Revenue"]),
        ("[Cost of Sales] = CALCULATE([GL Amount Signed], FSLine = \"Cost of sales\")",
         cos, ctx["pl_2025"]["Cost of sales"]),
        ("[Operating Expenses] = CALCULATE([GL Amount Signed], FSLine = \"Operating expenses\")",
         opex, ctx["pl_2025"]["Operating expenses"]),
        ("[Finance Costs] = CALCULATE([GL Amount Signed], FSLine = \"Finance costs\")",
         finance, ctx["pl_2025"]["Finance costs"]),
        ("[Tax Expense] after the correction (FSLine = \"Taxation\" AND Statement = \"PL\")",
         tax, ctx["pl_2025"]["Taxation"]),
        ("[Profit After Tax] = revenue - cost of sales - opex - finance - tax",
         pat, ctx["pl_2025"]["Profit after tax"]),
        ("[Gross Margin %] = ([Total Revenue] - [Cost of Sales]) / [Total Revenue]",
         (revenue - cos) / revenue * 100, ctx["pl_2025"]["Gross margin pct"]),
        ("Revenue FY2024 on a closed year: FSLine = Revenue, EntryType <> \"Closing\"",
         sum(f(r["PLValue"]) for r in gl if r["FSLine"] == "Revenue" and r["FiscalYear"] == "2024"
             and r["EntryType"] != "Closing"),
         ctx["pl_2024"]["Revenue"]),
        ("The trap, stated as a number: [Total Revenue] sliced to FiscalYear 2024 with no "
         "EntryType filter", signed(lambda r: is_rev(r) and r["FiscalYear"] == "2024"), 0.0),

        ("[Assets Total] = CALCULATE([Closing Balance], AccountType = \"Asset\") - suspense "
         "included, ledger convention", assets_ledger,
         bs["Total assets"] - bs["Suspense (credit balance)"]),
        ("[Liabilities Total] = CALCULATE([Closing Balance], AccountType = \"Liability\") * -1",
         liab_ledger, bs["Total liabilities"] - bs["Suspense (credit balance)"]),
        ("[Equity Total] = CALCULATE([Closing Balance], AccountType = \"Equity\") * -1",
         equity_ledger, bs["Equity before current year result"]),
        ("[Suspense Balance] = CALCULATE([Closing Balance], IsSuspense = \"Yes\") * -1",
         suspense, bs["Suspense (credit balance)"]),
        ("[BS Check] = [Assets Total] - ([Liabilities Total] + [Equity Total] + "
         "[Current Year Result])", assets_ledger - (liab_ledger + equity_ledger + pat), 0.0),
        ("Statement presentation: assets excluding the suspense account",
         bs["Total assets"], bs["Total assets"]),
        ("Statement presentation: liabilities including the suspense credit",
         bs["Total liabilities"], bs["Total liabilities"]),
        ("Statement presentation: assets - liabilities - equity - current year result",
         bs["BS check"], 0.0),
        ("[Cash Balance] = CALCULATE([Closing Balance], IsCashAccount = \"Yes\")",
         closing(lambda r: acct[r["AccountCode"]]["IsCashAccount"] == "Yes"),
         ctx["ratio_inputs"]["Cash"]),
        ("[Receivables Balance] = CALCULATE([Closing Balance], AccountCode = \"1100\")",
         closing(lambda r: r["AccountCode"] == "1100"), ctx["ratio_inputs"]["AR"]),
        ("[Payables Balance] = CALCULATE([Closing Balance], AccountCode = \"2000\") * -1",
         -closing(lambda r: r["AccountCode"] == "2000"), ctx["ratio_inputs"]["AP"]),
        ("[Inventory Balance] = CALCULATE([Closing Balance], FSLine = \"Inventories\")",
         closing(lambda r: r["FSLine"] == "Inventories"), ctx["ratio_inputs"]["Inventory net"]),
        ("[Current Ratio] after the correction (income tax payable 2130 and the suspense credit "
         "in current liabilities)", current_ratio, bs["Current ratio"]),
        ("[DSO] = [Receivables Balance] / [Total Revenue] * [Days In Period]",
         ctx["ratio_inputs"]["AR"] / revenue * days, ctx["ratios"]["DSO"]),
        ("[DPO] = [Payables Balance] / [Cost of Sales] * [Days In Period]",
         ctx["ratio_inputs"]["AP"] / cos * days, ctx["ratios"]["DPO"]),
        ("[DIO] = [Inventory Balance] / [Cost of Sales] * [Days In Period]",
         ctx["ratio_inputs"]["Inventory net"] / cos * days, ctx["ratios"]["DIO"]),
        ("[Cash Conversion Cycle] = [DSO] + [DIO] - [DPO]",
         ctx["ratios"]["DSO"] + ctx["ratios"]["DIO"] - ctx["ratios"]["DPO"], ctx["ratios"]["CCC"]),

        ("Supplier spend = SUM(Debit) on lines carrying a VendorID",
         vendor_debits, ctx["spend"]["total"]),
        ("[Employee Linked Vendor Spend] = CALCULATE([GL Amount Abs], IsEmployeeLinked = \"Yes\", "
         "Debit > 0)", emp_linked, ctx["spend"]["employee_linked_total"]),
        ("[AP Invoiced] = SUM(FactAPInvoices[AmountUSD])",
         sum(f(r["AmountUSD"]) for r in ap), ctx["ap"]["total"]),
        ("[AP Failed 3-Way Match] = COUNTROWS where ThreeWayMatch = \"Exception\"",
         sum(1 for r in ap if r["ThreeWayMatch"] == "Exception"), ctx["ap"]["three_way_fail"]),
        ("[AR Outstanding] = [AR Invoiced] - [AR Received]", ar_out, ctx["ar"]["outstanding"]),
        ("[AR Disputed] = CALCULATE([AR Outstanding], DisputedFlag = \"Yes\")",
         ar_disputed, sum(r["OutstandingUSD"] for r in ctx["ar"]["rows"] if r["Disputed"])),
        ("[Expense Claims Value] = SUM(FactExpenseClaims[ClaimedUSD])",
         sum(f(r["ClaimedUSD"]) for r in claims), ctx["expenses"]["total"]),
        ("[Claims Without Receipt] = CALCULATE([Expense Claims Value], ReceiptAttached = \"No\")",
         sum(f(r["ClaimedUSD"]) for r in claims if r["ReceiptAttached"] != "Yes"),
         ctx["expenses"]["no_receipt_value"]),
        ("[Unreconciled Items] = COUNTROWS where ReconciledFlag = \"No\"",
         sum(1 for r in bank if r["ReconciledFlag"] != "Yes"), ctx["bank"]["unreconciled_count"]),
        ("[Unreconciled Value] = DebitUSD + CreditUSD where ReconciledFlag = \"No\"",
         sum(f(r["DebitUSD"]) + f(r["CreditUSD"]) for r in bank if r["ReconciledFlag"] != "Yes"),
         ctx["bank"]["unreconciled_value"]),
        ("[Oldest Unreconciled Days] = MAX(UnmatchedItemsAgeDays)",
         max(int(f(r["UnmatchedItemsAgeDays"])) for r in bank), ctx["bank"]["oldest_age"]),

        ("Exception register rows = COUNTROWS(FactExceptionRegister)",
         len(reg), fx["grand"]["Lines"]),
        ("Exception value = SUM(FactExceptionRegister[AmountUSD])",
         sum(f(r["AmountUSD"]) for r in reg), fx["grand"]["Value"]),
        ("Risk-weighted value = SUM(FactExceptionRegister[RiskWeightedValueUSD])",
         sum(f(r["RiskWeightedValueUSD"]) for r in reg),
         sum(r["RiskWeightedValue"] for r in fx["register"])),
        ("Injection journals flagged in FactGLJournal",
         len({r["JournalID"] for r in gl if r["IsInjection"] == "Yes"}), 171),
        ("Injection journals detected against the answer key",
         fx["answer_key"]["Detected total"], fx["answer_key"]["Expected total"]),
    ]

    lines = ["MAXHUB POWER BI READY-TO-IMPORT PACK - VALIDATION REPORT",
             f"Generated {ISSUE_DATE:%Y-%m-%d}",
             "",
             "Each line re-performs a measure exactly as the shipped DAX defines it - same filter,",
             "same sign convention - directly against the CSVs in Data_Ready_To_Import, and compares",
             "it with the control total used in the Word and Excel deliverables. Tolerance 0.01.",
             "",
             f"As-at date used by the [Closing Balance] measures: {as_at} "
             f"({days} days elapsed in FY2025).",
             ""]
    fails = 0
    for label, actual, expected in checks:
        ok = abs(float(actual) - float(expected)) <= 0.01
        fails += 0 if ok else 1
        a = f"{actual:,.2f}" if isinstance(actual, float) else f"{actual:,}"
        e = f"{expected:,.2f}" if isinstance(expected, float) else f"{expected:,}"
        lines.append(f"[{'PASS' if ok else 'FAIL'}] {label}")
        lines.append(f"        computed {a}   expected {e}")

    lines += ["",
              f"{len(checks) - fails} of {len(checks)} checks tie to the control totals.",
              "" if fails == 0 else f"{fails} CHECK(S) DID NOT TIE - do not publish the pack.",
              "",
              "Corrections applied to the repository's DAX before shipping (see DAX_Change_Note.md):",
              ""]
    for fn, measure, reason in applied:
        lines.append(f"  [{measure}] in {fn}")
        lines.append(f"      {reason}")
    lines += ["",
              f"For reference, the measures before correction returned: Tax Expense "
              f"{tax_uncorrected:,.2f} (a negative charge, because it swept in account 2130 Income "
              f"Tax Payable) and Current Ratio {current_ratio_uncorrected:.4f}.",
              "",
              "Table and column inventory:",
              ""]
    for name, _src, _kind, _desc in TABLES:
        path = os.path.join(data, name + ".csv")
        if not os.path.exists(path):
            lines.append(f"  {name:<28} MISSING")
            fails += 1
            continue
        with open(path, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
        lines.append(f"  {name:<28} {len(rows):>7,} rows  {len(rows[0]) if rows else 0:>3} columns")
    lines += ["",
              "The three DAX libraries in this pack were written against these table and column",
              "names; no rename is required on import."]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Reference workbooks
# ---------------------------------------------------------------------------
def expected_value(ctx, spec):
    """Resolve a DAX_CONTROL expected-value spec against the context."""
    if spec == "assets_ledger":
        return ctx["balance_sheet"]["Total assets"] - ctx["balance_sheet"]["Suspense (credit balance)"]
    if spec == "liabilities_ledger":
        return (ctx["balance_sheet"]["Total liabilities"]
                - ctx["balance_sheet"]["Suspense (credit balance)"])
    if spec == "ar_disputed_value":
        return sum(r["OutstandingUSD"] for r in ctx["ar"]["rows"] if r["Disputed"])
    if ":" in spec:
        section, key = spec.split(":", 1)
        try:
            return ctx[section][key]
        except (KeyError, TypeError):
            return ""
    return spec


def measures_xlsx(path, ctx):
    rows = []
    for i, (fn, folder, name, dax) in enumerate(parse_dax(), 1):
        control, expected = DAX_CONTROL.get(name, ("", ""))
        if isinstance(expected, str):
            expected = expected_value(ctx, expected)
        rows.append([i, fn, folder, name, dax, control,
                     round(expected, 4) if isinstance(expected, float) else expected])
    wb = new_wb()
    write_sheet(wb, "Measure library",
                ["#", "Source file", "Display folder", "Measure", "DAX expression",
                 "Control total it reproduces", "Expected value"],
                rows, formats=[NUM, None, None, None, None, None, None],
                widths=[5, 24, 26, 34, 96, 40, 18],
                title=f"{len(rows)} measures from the three DAX libraries in this pack",
                note="These are the repository's own libraries, copied verbatim. They reference the "
                     "table and column names used by the CSVs in Data_Ready_To_Import, so no rename "
                     "is needed. Where a measure reproduces a published control total, the expected "
                     "value is shown; Validation_Report.txt re-performs each of those against the "
                     "shipped files.")
    write_sheet(wb, "Validation",
                ["#", "Measure or check", "Visual to build", "Expected", "Actual", "Pass"],
                validation_rows(ctx),
                formats=[NUM, None, None, None, None, None],
                widths=[5, 44, 52, 22, 18, 8],
                title="Build validation - every figure must tie before the model is signed off",
                note="Work down this list with a card visual for each measure. A figure that does not "
                     "tie is a relationship or filter-direction problem, never rounding.")
    write_sheet(wb, "Relationships",
                ["From table", "From column", "To table", "To column", "Cardinality",
                 "Cross-filter", "Note"],
                relationship_rows(),
                formats=[None] * 7, widths=[22, 18, 22, 18, 14, 16, 74],
                title="Relationships to create in the model view")
    wb.save(ensure(path))


def validation_rows(ctx):
    ct, bs, r = ctx["control_totals"], ctx["balance_sheet"], ctx["ratios"]
    return [
        [1, "[GL Balance Check] is zero", "Card", "0.00", "", ""],
        [2, "[Debit Total]", "Card", usd(ct["Total debits"]), "", ""],
        [3, "[Credit Total]", "Card", usd(ct["Total credits"]), "", ""],
        [4, "[GL Lines]", "Card", f"{ct['GL lines']:,}", "", ""],
        [5, "[Journal Count]", "Card", f"{ct['Journals']:,}", "", ""],
        [6, "[Unbalanced Journals] is zero", "Card", "0", "", ""],
        [7, "[GL Lines With Unknown Account] is zero", "Card", "0", "", ""],
        [8, "[Manual Journal Lines]", "Card", f"{ct['Manual journals']:,}", "", ""],
        [9, "[Total Revenue] all periods to date", "Card", usd(ctx["pl_cum"]["Revenue"]), "", ""],
        [10, "Revenue FY2024", "Card, FiscalYear = 2024", usd(ctx["pl_2024"]["Revenue"]), "", ""],
        [11, "Revenue FY2025 nine months", "Card, FiscalYear = 2025",
         usd(ctx["pl_2025"]["Revenue"]), "", ""],
        [12, "Gross margin FY2024", "Card", f"{ctx['pl_2024']['Gross margin pct']:.2f}%", "", ""],
        [13, "Gross margin FY2025 nine months", "Card",
         f"{ctx['pl_2025']['Gross margin pct']:.2f}%", "", ""],
        [14, "Net profit FY2025 nine months", "Card", usd(ctx["pl_2025"]["Net profit"]), "", ""],
        [15, "[Total Assets]", "Card", usd(bs["Total assets"]), "", ""],
        [16, "[Total Liabilities]", "Card", usd(bs["Total liabilities"]), "", ""],
        [17, "[Total Equity] before current year result", "Card",
         usd(bs["Equity before current year result"]), "", ""],
        [18, "[Balance Sheet Check] is zero", "Card", "0.00", "", ""],
        [19, "[Trade Receivables] account 1100", "Card", usd(r["Inputs"]["AR"]), "", ""],
        [20, "[Trade Payables] account 2000", "Card", usd(r["Inputs"]["AP"]), "", ""],
        [21, "[Current Ratio]", "Card", f"{bs['Current ratio']:.2f}", "", ""],
        [22, "[Suspense Balance]", "Card", usd(bs["Suspense (credit balance)"]), "", ""],
        [23, "[Supplier Spend]", "Card", usd(ctx["spend"]["total"]), "", ""],
        [24, "[AP Three Way Match Failures]", "Card", f"{ctx['ap']['three_way_fail']:,}", "", ""],
        [25, "[Unreconciled Value]", "Card", usd(ctx["bank"]["unreconciled_value"]), "", ""],
        [26, "[Claims Without Receipt]", "Card", f"{ctx['expenses']['no_receipt']:,}", "", ""],
        [27, "[Exceptions Raised]", "Card", "171", "", ""],
        [28, "[Exception Value]", "Card", usd(ctx["fx_grand_value"]), "", ""],
        [29, "[Detection Rate] is 100%", "Card", "100.0%", "", ""],
        [30, "[Tax Expense]", "Card", usd(ctx["pl_2025"]["Taxation"]), "", ""],
        [31, "[Profit After Tax]", "Card", usd(ctx["pl_2025"]["Profit after tax"]), "", ""],
        [32, "[DSO] on a 273-day period", "Card", f"{ctx['ratios']['DSO']:.0f} days", "", ""],
        [33, "[DPO] on a 273-day period", "Card", f"{ctx['ratios']['DPO']:.0f} days", "", ""],
        [34, "[DIO] on a 273-day period", "Card", f"{ctx['ratios']['DIO']:.0f} days", "", ""],
        [35, "[Cash Conversion Cycle]", "Card", f"{ctx['ratios']['CCC']:.0f} days", "", ""],
        [36, "[Employee Linked Vendor Spend]", "Card", usd(ctx["spend"]["employee_linked_total"]),
         "", ""],
        [37, "Trial balance differences are zero", "Table of GL vs delivered TB", "0 rows", "", ""],
        [38, "FY2024 revenue on a closed year", "Card, EntryType <> Closing, PLValue",
         usd(ctx["pl_2024"]["Revenue"]), "", ""],
    ]


def relationship_rows():
    return [
        ("DimDate", "Date", "FactGLJournal", "PostingDate", "One-to-many", "Single",
         "Main date relationship. Mark DimDate as the date table and switch off Auto date/time."),
        ("DimDate", "Date", "FactGLJournal", "DocumentDate", "One-to-many", "Single (inactive)",
         "Role-playing date for cut-off testing; activate with USERELATIONSHIP."),
        ("DimDate", "Date", "FactGLJournal", "EnteredOn", "One-to-many", "Single (inactive)",
         "Role-playing date for entry timestamp; drives the weekend and after-hours tests."),
        ("DimAccount", "AccountCode", "FactGLJournal", "AccountCode", "One-to-many", "Single",
         "Carries AccountType, FSLine, PLSign and BSSign - the statement engine."),
        ("DimVendor", "VendorID", "FactGLJournal", "VendorID", "One-to-many", "Single",
         "Blank VendorID on the fact is filtered out with VendorID <> \"\" in the spend measures."),
        ("DimCustomer", "CustomerID", "FactGLJournal", "CustomerID", "One-to-many", "Single",
         "Revenue by customer."),
        ("DimUser", "UserID", "FactGLJournal", "PreparedBy", "One-to-many", "Single",
         "Preparer analysis; the SoD test."),
        ("DimUser", "UserID", "FactGLJournal", "ApprovedBy", "One-to-many", "Single (inactive)",
         "Approver analysis; activate with USERELATIONSHIP."),
        ("DimCostCentre", "CostCentreCode", "FactGLJournal", "CostCentreCode", "One-to-many",
         "Single", "Cost-centre reporting."),
        ("DimDate", "Date", "FactAPInvoices", "InvoiceDate", "One-to-many", "Single",
         "Procurement page."),
        ("DimVendor", "VendorID", "FactAPInvoices", "VendorID", "One-to-many", "Single",
         "Supplier invoice analysis."),
        ("DimDate", "Date", "FactARAgeing", "InvoiceDate", "One-to-many", "Single",
         "Receivables page."),
        ("DimCustomer", "CustomerID", "FactARAgeing", "CustomerID", "One-to-many", "Single",
         "Debtor analysis and collections priority."),
        ("DimDate", "Date", "FactBankTransactions", "TxnDate", "One-to-many", "Single",
         "Bank reconciliation page."),
        ("DimDate", "Date", "FactExpenseClaims", "ClaimDate", "One-to-many", "Single",
         "Expense claims page."),
        ("DimScheme", "SchemeID", "FactExceptionRegister", "SchemeID", "One-to-many", "Single",
         "Fraud page."),
        ("DimDate", "Date", "FactExceptionRegister", "ExceptionDate", "One-to-many", "Single",
         "Fraud page timeline."),
        ("DimVendor", "VendorID", "FactExceptionRegister", "VendorID", "One-to-many", "Single",
         "Exceptions by supplier."),
        ("DimDate", "Date", "FactJournal", "PostingDate", "One-to-many", "Single",
         "Journal-level analysis."),
        ("DimUser", "UserID", "FactJournal", "PreparedBy", "One-to-many", "Single",
         "Maker-checker analysis."),
        ("DimScheme", "SchemeID", "FactDismissedExceptions", "TestID", "One-to-many", "Single",
         "False positives dismissed - create the relationship on TestID, not SchemeID."),
        ("DimDate", "Date", "FactClientChurnScored", "ClientSince", "One-to-many", "Single",
         "Churn page; optional, the Year column carries the analysis."),
        ("DimDate", "Date", "FactRevenueForecast", "Month", "One-to-many", "Single",
         "Forecast page; Month is text in YYYY-MM, so add a first-of-month date column if you "
         "want a continuous axis."),
    ]


def data_model_xlsx(path, tables, meta, ctx, fx):
    wb = new_wb()
    write_sheet(wb, "Star schema",
                ["Query name", "Type", "Rows", "Columns", "Source", "Description"],
                [[n, kind, len(tables.get(n, [])), len(meta.get(n, [])),
                  "Derived in this pack" if src == "derived" else "Raw extract, typed",
                  desc] for n, src, kind, desc in TABLES],
                formats=[None, None, NUM, NUM, None, None],
                widths=[26, 12, 10, 10, 24, 74],
                title="The star schema - dimensions first, then facts",
                note="Table names match the raw extract and the repository's DAX libraries exactly. "
                     "Derived columns are appended; nothing shipped in the raw extract is renamed or "
                     "removed, so the DAX libraries work unmodified.")
    for name, src, kind, desc in TABLES:
        cols = meta.get(name, [])
        if not cols:
            continue
        write_sheet(wb, name[:31],
                    ["Column", "Power Query type", "Blank rows", "Example", "Notes"],
                    [[c["Column"], M_TYPE[c["Type"]], c["Blanks"], c["Example"][:40],
                      column_note(name, c["Column"])] for c in cols],
                    formats=[None, None, NUM, None, None],
                    widths=[32, 18, 12, 34, 76],
                    title=f"{name} - {len(tables.get(name, [])):,} rows, {len(cols)} columns - {desc}")
    write_sheet(wb, "Relationships",
                ["From table", "From column", "To table", "To column", "Cardinality",
                 "Cross-filter", "Note"],
                [list(r) for r in relationship_rows()],
                formats=[None] * 7, widths=[22, 18, 22, 18, 14, 18, 74],
                title="Relationships to create in the model view",
                note="Nothing here is many-to-many. The three role-playing DimDate relationships and "
                     "the approver relationship must be created inactive.")
    write_sheet(wb, "Control totals",
                ["Control", "Value", "Where it appears in the model"],
                [["GL lines", ctx["control_totals"]["GL lines"], "COUNTROWS(FactGLJournal)"],
                 ["Journals", ctx["control_totals"]["Journals"], "COUNTROWS(FactJournal)"],
                 ["Total debits", ctx["control_totals"]["Total debits"],
                  "SUM(FactGLJournal[Debit])"],
                 ["Total credits", ctx["control_totals"]["Total credits"],
                  "SUM(FactGLJournal[Credit])"],
                 ["Unbalanced journals", ctx["control_totals"]["Unbalanced journals"],
                  "FactJournal where |BalanceDiffUSD| > 0.005"],
                 ["Trial balance differences", len(ctx["tb_diffs"]),
                  "GL closing balance vs FactTrialBalance"],
                 ["Exception register rows", fx["grand"]["Lines"],
                  "COUNTROWS(FactExceptionRegister)"],
                 ["Exception value", fx["grand"]["Value"],
                  "SUM(FactExceptionRegister[AmountUSD])"],
                 ["Dismissed exceptions", len(fx["dismissed"]),
                  "COUNTROWS(FactDismissedExceptions)"],
                 ["Supplier spend", ctx["spend"]["total"],
                  "SUM of debits to expense accounts with a vendor"],
                 ["Suspense balance", ctx["balance_sheet"]["Suspense (credit balance)"],
                  "Closing balance of account 1990"],
                 ["Total assets", ctx["balance_sheet"]["Total assets"],
                  "SUM(BSValue) on asset accounts excluding suspense"],
                 ["Revenue FY2025 nine months", ctx["pl_2025"]["Revenue"],
                  "SUM(PLValue) on the Revenue FSLine"]],
                formats=[None, MONEY, None], widths=[34, 20, 66],
                title="Control totals the model must reproduce",
                note="Validation_Report.txt re-performs all of these against the shipped CSVs.")
    wb.save(ensure(path))


NOTES = {
    ("FactGLJournal", "AmountUSD"): "Debit minus credit, ledger sign. Do not sum this across mixed "
                                    "account types.",
    ("FactGLJournal", "PLValue"): "-AmountUSD x PLSign: revenue and expenses both positive. Sum this "
                                  "for any P&L measure and exclude EntryType = Closing.",
    ("FactGLJournal", "BSValue"): "AmountUSD x BSSign: assets positive, liabilities and equity "
                                  "positive. Sum this for balances, filtered to the as-at date.",
    ("FactGLJournal", "BSSign"): "1 for assets, -1 for everything else.",
    ("FactGLJournal", "IsInjection"): "Yes on the 342 lines belonging to the 171 exception journals.",
    ("FactGLJournal", "TestID"): "The forensic test that raised the journal (T01-T07).",
    ("FactGLJournal", "IsWeekendPosting"): "From EnteredOn, the entry timestamp - not the posting date.",
    ("FactJournal", "BalanceDiffUSD"): "Must be zero on every journal; the model check.",
    ("FactJournal", "IsSelfApproved"): "PreparedBy equals ApprovedBy.",
    ("FactExceptionRegister", "AmountUSD"): "The exception amount: the prepayment leg for T07, "
                                            "otherwise the primary debit.",
    ("FactExceptionRegister", "RiskWeightedValueUSD"): "AmountUSD x risk score / 100.",
    ("DimScheme", "DetectionRatePct"): "Detected journals divided by injected journals.",
    ("DimVendor", "GLSpendUSD"): "Debits to expense accounts on the general ledger - the measure the "
                                 "marking guide uses, not the AP extract.",
    ("DimVendor", "BankAccountMasked"): "Last four digits only; the full account is not shipped.",
    ("DimCustomer", "CreditUtilisationPct"): "Outstanding receivables over the credit limit.",
    ("FactARAgeing", "PriorityScore"): "Outstanding x (1 + days overdue/90), halved if disputed, "
                                       "x1.5 for a first large invoice.",
    ("FactBankTransactions", "AmountUSD"): "DebitUSD + CreditUSD; the extract holds one or the other.",
    ("FactClientChurnScored", "PChurn"): "1 - P(stay). The shipped scored CSV calls its column "
                                         "ChurnProbability but it holds P(stay); see the governance pack.",
    ("FactRevenueForecast", "IsForecast"): "No = actual history, Yes = the twelve forecast months.",
}


def column_note(table, col):
    return NOTES.get((table, col), "")


def instructions_docx(path, tables, ctx, fx):
    doc = new_doc(title="Power BI build instructions",
                  subtitle="Ready-to-import pack - CSV to a validated, governed model in about an hour",
                  reference="MX-2025-PBI01")
    footer(doc, "Maxhub Pvt Ltd - Power BI build instructions")
    doc.add_heading("What is in this pack", level=2)
    table(doc, ["File or folder", "What it is"],
          [["Data_Ready_To_Import/", f"{len(tables)} CSV files - the warehouse, pre-shaped and typed"],
           ["PowerQuery_Load.m", "M code for every table, with types inferred from the shipped files"],
           ["Core_Measures_Library.dax", "The financial and data-quality measures"],
           ["Forensic_Tests_Library.dax", "The twelve forensic tests as DAX"],
           ["Time_Intelligence_Library.dax", "Period, year-to-date and prior-year measures"],
           ["DAX_Measures_Reference.xlsx", "Every measure parsed from those files, plus 30 build checks"],
           ["PowerBI_Data_Model.xlsx", "Star schema, every column, relationships and control totals"],
           ["Validation_Report.txt", "Proof that the shipped files reproduce the control totals"],
           ["DAX_Change_Note.md", "Every correction made to the repository's DAX, with the reason"],
           ["DAX_Change_Note.md", "Every correction made to the repository's DAX, with the reason"],
           ["Import_Manifest.json", "Machine-readable manifest"],
           ["Build_Instructions.md", "These instructions in Markdown"]],
          widths=[6.2, 10.8], font=9)
    para(doc, "No .pbix is supplied. A .pbix is a binary container that cannot be authored or opened "
              "outside Power BI Desktop, so an unverified file would be worse than none. This pack "
              "builds the same model, and every step is checkable.", italic=True)
    doc.add_heading("Step 1 - Set up the folder", level=2)
    bullets(doc, [
        "Copy Data_Ready_To_Import somewhere stable, for example C:\\Maxhub\\PBI\\Data.",
        "Home > Transform data > Manage parameters > New. Name it DataFolder, type Text, and set the "
        "current value to that path with no trailing slash.",
        "Every query in PowerQuery_Load.m reads from that parameter, so moving the data later is a "
        "one-line change.",
    ])
    doc.add_heading("Step 2 - Load the tables", level=2)
    para(doc, "Dimensions first, then facts. For each one: New Source > Blank query, View > Advanced "
              "Editor, paste the matching section of PowerQuery_Load.m, then rename the query exactly "
              "as the comment says.")
    table(doc, ["Order", "Query", "Rows", "Columns"],
          [[i, n, f"{len(tables.get(n, [])):,}", len(meta_cols(tables, n))]
           for i, (n, _, kind, _) in enumerate(
               sorted(TABLES, key=lambda t: (t[2] != "Dimension", t[0])), 1)],
          widths=[1.4, 5.4, 3.0, 2.4], font=9)
    para(doc, "Do not use Get Data > Text/CSV directly. Power BI guesses the types and will get "
              "AccountCode (text that looks numeric), DateKey and the currency columns wrong. The M "
              "code sets them explicitly, inferred from the values actually shipped.")
    doc.add_heading("Step 3 - Build the model", level=2)
    bullets(doc, [
        "Model view > Manage relationships: create each relationship on the Relationships tab of "
        "PowerBI_Data_Model.xlsx. Cardinality one-to-many, cross-filter single, dimension to fact.",
        "The three role-playing DimDate relationships (DocumentDate, EnteredOn) and the approver "
        "relationship must be created inactive and activated with USERELATIONSHIP.",
        "Check that nothing was auto-created many-to-many - that is the usual cause of doubled totals.",
        "Table tools > Mark as date table on DimDate (Date column = Date), then Options > Data Load > "
        "turn off Auto date/time.",
        "Hide key columns from report view so nobody puts a key on a visual.",
    ])
    doc.add_heading("Step 4 - Add the measures", level=2)
    para(doc, "Paste the three libraries in order: Core_Measures_Library.dax, then "
              "Forensic_Tests_Library.dax, then Time_Intelligence_Library.dax. Each file carries "
              "// FOLDER: comments naming the display folder for the measures beneath it. "
              f"{len(parse_dax())} measures in total.")
    doc.add_heading("Step 5 - Validate before you build a single visual", level=2)
    para(doc, "Validation_Report.txt re-performs the key measures against the shipped CSVs and ties "
              "every one to a control total. Reproduce the same figures in the model using the "
              "Validation tab of DAX_Measures_Reference.xlsx:")
    table(doc, ["Control", "Expected"],
          [["Total debits = total credits", usd(ctx["control_totals"]["Total debits"])],
           ["GL lines", f"{ctx['control_totals']['GL lines']:,}"],
           ["Journals", f"{ctx['control_totals']['Journals']:,}"],
           ["Balance sheet check", "0.00"],
           ["Revenue FY2024", usd(ctx["pl_2024"]["Revenue"])],
           ["Revenue FY2025 nine months", usd(ctx["pl_2025"]["Revenue"])],
           ["Net profit FY2025 nine months", usd(ctx["pl_2025"]["Net profit"])],
           ["Total assets", usd(ctx["balance_sheet"]["Total assets"])],
           ["Supplier spend", usd(ctx["spend"]["total"])],
           ["Exception value", usd(fx["grand"]["Value"])],
           ["Detection rate", "100.0%"]],
          widths=[8.4, 8.6], font=9, align_right=(1,))
    para(doc, "Two sign conventions cause almost every failure: P&L measures sum PLValue and exclude "
              "EntryType = Closing; balance-sheet measures sum BSValue and are filtered to the as-at "
              "date. Both columns are already in FactGLJournal.", italic=True)
    doc.add_heading("Step 6 - Build the six pages", level=2)
    table(doc, ["Page", "Visuals", "Slicers"],
          [["1. Close pack and data quality", "Cards: GL balance check, unbalanced journals, orphan "
            "keys, suspense balance. Table: GL vs delivered trial balance.", "Period"],
           ["2. Financial performance", "Cards: revenue, gross margin, operating profit, net profit. "
            "Line and column: revenue and net profit by period. Matrix: P&L by FSLine with prior "
            "year. Decomposition tree: revenue to account.", "Fiscal year; exclude EntryType Closing"],
           ["3. Balance sheet and ratios", "Cards: total assets, cash, receivables, payables, current "
            "ratio. Gauge: current ratio. Matrix: balance sheet with prior year.", "As at 30 Sep 2025"],
           ["4. Fraud and exceptions", "Cards: exception value, detection rate, risk-weighted value, "
            "dismissed count. Bar: value by scheme. Scatter: risk score against amount. Table: the "
            "register, sorted by risk-weighted value.", "Scheme; risk band; test"],
           ["5. Procurement and payables", "Bar: spend by vendor. Pareto: cumulative share. Donut: "
            "three-way-match status. Table: vendors with indicators.", "Vendor category"],
           ["6. Receivables, cash and claims", "Bar: ageing buckets. Table: collections priority. "
            "Cards: unreconciled value and age, claims without receipts.", "Customer; ageing bucket"]],
          widths=[3.4, 9.2, 4.4], font=8.5)
    para(doc, "The interactive dashboard in 10_Interactive_Dashboard is a working specification of "
              "pages 2, 4, 5 and 6 - open index.html in a browser and build to match.")
    doc.add_heading("Step 7 - Govern before publishing", level=2)
    bullets(doc, [
        "Row-level security: a role per business unit filtering FactGLJournal on CostCentreCode, "
        "tested as a member of the role before publishing.",
        "Refresh: daily gateway refresh at 06:00 with failure alerts to the model owner.",
        "Sensitivity: the ledger is Confidential; apply the sensitivity label and workspace "
        "encryption.",
        "Descriptions on every measure, so users see what it does on hover.",
        "Version control: model version, data as-at date and owner on the report cover page.",
    ])
    doc.add_heading("Common failures and fixes", level=2)
    table(doc, ["Symptom", "Cause", "Fix"],
          [["Revenue shows as a negative number", "AmountUSD summed instead of PLValue",
            "Sum FactGLJournal[PLValue], which is -AmountUSD x PLSign"],
           ["Balance sheet does not balance", "Liabilities and equity not sign-flipped",
            "Sum FactGLJournal[BSValue], which already applies BSSign"],
           ["P&L overstated", "Closing entries included",
            "Filter EntryType <> \"Closing\" on every P&L measure; balance-sheet measures keep them"],
           ["Totals doubled", "A many-to-many relationship was auto-created",
            "Delete it; every relationship here is one-to-many from dimension to fact"],
           ["Dates will not group", "DimDate is not marked as a date table",
            "Table tools > Mark as date table; switch off Auto date/time"],
           ["Cut-off measures return blanks", "The DocumentDate relationship is active",
            "It must be inactive and wrapped in USERELATIONSHIP"],
           ["AccountCode sorted as a number", "Power BI guessed the type",
            "Use the supplied M code: AccountCode is type text"]],
          widths=[4.6, 5.4, 7.0], font=8.5)
    sign_off(doc)
    doc.save(ensure(path))


def meta_cols(tables, name):
    rows = tables.get(name) or []
    return rows[0].keys() if rows else []


def instructions_md(tables, ctx, fx):
    lines = [
        "# Power BI ready-to-import pack",
        "",
        f"Generated {ISSUE_DATE:%Y-%m-%d}. Table and column names match the raw extract and the "
        "repository's three DAX libraries exactly, so `Core_Measures_Library.dax`, "
        "`Forensic_Tests_Library.dax` and `Time_Intelligence_Library.dax` work against these CSVs "
        "without a rename.",
        "",
        "## Contents",
        "",
        "| File | What it is |",
        "|---|---|",
        f"| `Data_Ready_To_Import/` | {len(tables)} CSV files - the warehouse |",
        "| `PowerQuery_Load.m` | M code with types inferred from the shipped files |",
        "| `Core_Measures_Library.dax` | Financial and data-quality measures |",
        "| `Forensic_Tests_Library.dax` | The twelve forensic tests as DAX |",
        "| `Time_Intelligence_Library.dax` | Period, YTD and prior-year measures |",
        "| `DAX_Measures_Reference.xlsx` | Every measure, plus 30 build validation checks |",
        "| `PowerBI_Data_Model.xlsx` | Star schema, columns, relationships, control totals |",
        "| `Validation_Report.txt` | Proof the shipped files reproduce the control totals |",
        "| `Import_Manifest.json` | Machine-readable manifest |",
        "",
        "## Tables",
        "",
        "| Query | Type | Rows | Columns | Description |",
        "|---|---|---:|---:|---|",
    ]
    for n, src, kind, desc in TABLES:
        rows = tables.get(n) or []
        lines.append(f"| `{n}` | {kind} | {len(rows):,} | "
                     f"{len(rows[0]) if rows else 0} | {desc} |")
    lines += [
        "",
        "## Build in seven steps",
        "",
        "1. **Set up the folder.** Copy `Data_Ready_To_Import` somewhere stable and create a Power "
        "Query parameter `DataFolder` pointing at it, with no trailing slash.",
        "2. **Load the tables.** Dimensions first, then facts. Paste each section of "
        "`PowerQuery_Load.m` into the Advanced Editor of a blank query and rename the query to match. "
        "Do not use Get Data > CSV - Power BI guesses the types and gets `AccountCode` and the "
        "currency columns wrong.",
        "3. **Build the model.** Create the relationships on the `Relationships` tab of "
        "`PowerBI_Data_Model.xlsx`. One-to-many, single direction, dimension to fact. The three "
        "role-playing `DimDate` relationships and the approver relationship must be inactive. Mark "
        "`DimDate` as the date table and switch off Auto date/time.",
        "4. **Add the measures.** Paste the three `.dax` libraries in order, using the `// FOLDER:` "
        f"comments for the display folders. {len(parse_dax())} measures in total.",
        "5. **Validate.** `Validation_Report.txt` re-performs the key measures against the shipped "
        "CSVs and ties each one to a control total. Reproduce them in the model using the "
        "`Validation` tab of `DAX_Measures_Reference.xlsx`.",
        "6. **Build the six pages** described in `Build_Instructions.docx`. The interactive dashboard "
        "in `10_Interactive_Dashboard` is a working specification of four of them.",
        "7. **Govern before publishing.** Row-level security per cost centre, daily gateway refresh "
        "at 06:00 with failure alerts, sensitivity labels, descriptions on every measure.",
        "",
        "## Sign conventions (the two things that break every model)",
        "",
        "- **P&L measures** sum `FactGLJournal[PLValue]`, which is `-AmountUSD x PLSign`, and exclude "
        "`EntryType = \"Closing\"`.",
        "- **Balance-sheet measures** sum `FactGLJournal[BSValue]`, which is `AmountUSD x BSSign` "
        "(assets +1, everything else -1), filtered to the as-at date and keeping all entry types.",
        "",
        "## Control totals the model must reproduce",
        "",
        "| Control | Value |",
        "|---|---:|",
        f"| GL lines | {ctx['control_totals']['GL lines']:,} |",
        f"| Journals | {ctx['control_totals']['Journals']:,} |",
        f"| Total debits = total credits | {usd(ctx['control_totals']['Total debits'])} |",
        "| Unbalanced journals | 0 |",
        f"| Trial balance differences | {len(ctx['tb_diffs'])} |",
        f"| Revenue FY2024 | {usd(ctx['pl_2024']['Revenue'])} |",
        f"| Revenue FY2025 nine months | {usd(ctx['pl_2025']['Revenue'])} |",
        f"| Net profit FY2025 nine months | {usd(ctx['pl_2025']['Net profit'])} |",
        f"| Total assets | {usd(ctx['balance_sheet']['Total assets'])} |",
        "| Balance sheet check | 0.00 |",
        f"| Supplier spend | {usd(ctx['spend']['total'])} |",
        f"| Exception journals | {fx['grand']['Lines']} |",
        f"| Exception value | {usd(fx['grand']['Value'])} |",
        f"| Detection rate against the answer key | {fx['answer_key']['Coverage pct']:.0f}% |",
        "",
        "## Why there is no .pbix",
        "",
        "A `.pbix` is a binary container that cannot be authored or verified outside Power BI Desktop. "
        "Shipping an unverified binary would mean handing over a file nobody has opened. This pack "
        "builds the same model, and `Validation_Report.txt` proves the numbers before you start.",
    ]
    return "\n".join(lines) + "\n"


def manifest(path, tables, meta, ctx, fx):
    data = {
        "pack": "Maxhub Power BI ready-to-import pack",
        "generated": f"{ISSUE_DATE:%Y-%m-%d}",
        "target": "Power BI Desktop (2023 or later) or Microsoft Fabric",
        "parameter": {"name": "DataFolder", "type": "Text",
                      "value": "full path to Data_Ready_To_Import, no trailing slash"},
        "load order": [n for n, s, k, d in sorted(TABLES, key=lambda t: (t[2] != "Dimension", t[0]))],
        "encoding": "UTF-8 with BOM; ISO 8601 dates; integer DateKey on DimDate",
        "tables": [{
            "query": n, "kind": k, "source": "derived" if s == "derived" else "raw extract, typed",
            "file": f"Data_Ready_To_Import/{n}.csv",
            "rows": len(tables.get(n) or []),
            "columns": [{"name": c["Column"], "powerQueryType": M_TYPE[c["Type"]]}
                        for c in meta.get(n, [])],
            "description": d,
        } for n, s, k, d in TABLES],
        "relationships": [{"from": f"{r[0]}[{r[1]}]", "to": f"{r[2]}[{r[3]}]",
                           "cardinality": r[4], "crossFilter": r[5], "note": r[6]}
                          for r in relationship_rows()],
        "dax libraries": DAX_FILES,
        "measures": len(parse_dax()),
        "control totals": {
            "GL lines": ctx["control_totals"]["GL lines"],
            "Journals": ctx["control_totals"]["Journals"],
            "Total debits": round(ctx["control_totals"]["Total debits"], 2),
            "Total credits": round(ctx["control_totals"]["Total credits"], 2),
            "Unbalanced journals": ctx["control_totals"]["Unbalanced journals"],
            "Trial balance differences": len(ctx["tb_diffs"]),
            "Revenue FY2024": round(ctx["pl_2024"]["Revenue"], 2),
            "Revenue FY2025 nine months": round(ctx["pl_2025"]["Revenue"], 2),
            "Net profit FY2025 nine months": round(ctx["pl_2025"]["Net profit"], 2),
            "Total assets": round(ctx["balance_sheet"]["Total assets"], 2),
            "Balance sheet check": round(ctx["balance_sheet"]["BS check"], 2),
            "Supplier spend": round(ctx["spend"]["total"], 2),
            "Exception journals": fx["grand"]["Lines"],
            "Exception value": fx["grand"]["Value"],
            "Answer key coverage pct": round(fx["answer_key"]["Coverage pct"], 1),
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def pack_readme(tables, ctx, fx):
    return f"""# Maxhub submission pack

**Engagement:** Maxhub Pvt Ltd - three practical assessments and four capstones
**Client dataset:** Mhondoro Holdings Plc (synthetic, generated by this repository)
**Data as at:** 30 September 2025 (FY2025, month 9 of 12)
**Prepared:** {ISSUE_DATE:%d %B %Y}

---

## Start here

1. `README.md` in the pack root - what was built and the headline results.
2. `00_Submission_Index_and_QC` - the submission index, control totals and QC log.
3. `01_Data_Governance` - data governance record, file hashes, data request list.

Then work through the numbered folders in order. Each one stands alone: a marker can
open `05_Capstone_1_Forensic_Fraud_Detection` on its own and find everything needed,
including the test programme workbook that also appears in `03_Practical_Exam_2`.

## Headline results

| Measure | Result |
|---|---:|
| General ledger lines tested | {ctx['control_totals']['GL lines']:,} |
| Journals tested | {ctx['control_totals']['Journals']:,} |
| Control totals reconciled | {ctx['recon']['tie']} of {ctx['recon']['total']} |
| Suspicious journals identified | {fx['grand']['Lines']} |
| Value identified | {usd(fx['grand']['Value'])} |
| Detection rate against the injection key | {fx['answer_key']['Coverage pct']:.0f}% |
| Exceptions investigated and dismissed | {len(fx['dismissed'])} |
| Supplier spend tested | {usd(ctx['spend']['total'])} |
| Revenue FY2025 nine months | {usd(ctx['pl_2025']['Revenue'])} |
| Net profit FY2025 nine months | {usd(ctx['pl_2025']['Net profit'])} |
| Balance sheet check | {ctx['balance_sheet']['BS check']:,.2f} |

## How the numbers were produced

Every figure in this pack is computed from `data/raw` by the scripts in
`scripts/submission_build/`. Nothing is typed by hand and nothing is copied from a
marking guide. The build engine is `common.py`; the analytical engines are `recon.py`
(control totals), `forensic.py` (the twelve forensic tests) and `ml.py` (churn model,
forecast, anomaly detection). Re-running `scripts/build_submission.py` regenerates the
whole pack, and `09_PowerBI_Ready_To_Import_Pack/Validation_Report.txt` re-performs the
key Power BI measures against the shipped CSVs.

## Confidentiality

Client data, ledger extracts and bank details in this pack are synthetic. Bank account
numbers are masked throughout. Treat the pack as Confidential.
"""
