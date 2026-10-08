"""
common.py - shared data access, control totals and financial statement engine
for the Maxhub submission pack.

Every figure in the submission folder is computed from `data/raw/*.csv` by this
module and its siblings.  Nothing is typed in by hand.

Sign conventions (documented again in the methodology notes):

* ``AmountUSD = Debit - Credit``  (debit positive), as delivered in the extract.
* P&L value = ``-AmountUSD * PLSign`` so that revenue is positive and expenses
  are positive costs.  P&L excludes ``EntryType = 'Closing'`` (the FY2024
  year-end transfer of result to retained earnings).
* Balance sheet value = ``+AmountUSD`` for Asset accounts and ``-AmountUSD``
  for Liability and Equity accounts, so contra accounts (accumulated
  depreciation, allowances, provisions) net off correctly.
* The suspense account (1990) carries a credit balance of 51,058.87 and is
  presented inside current liabilities, per the engagement's presentation basis.
* Ratio definitions use control accounts: AR = 1100, AP = 2000,
  inventory net = 1200 + 1210 + 1220 - 1230.
"""
from __future__ import annotations

import csv
import hashlib
import os
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw")
XLSX = os.path.join(ROOT, "data", "xlsx")

AS_AT = date(2025, 9, 30)
PYE = date(2024, 12, 31)
PERIOD_START = date(2024, 1, 1)
DAYS_ELAPSED_FY2025 = (AS_AT - PYE).days  # 273

AR_ACCOUNT = "1100"
AP_ACCOUNT = "2000"
INVENTORY_ACCOUNTS = ("1200", "1210", "1220", "1230")
ACC_DEP_ACCOUNTS = ("1440", "1450", "1460")
SUSPENSE_ACCOUNT = "1990"

# ---------------------------------------------------------------------------
# Published control totals (data/README.md, Capstones 1-3, Practical Assessments)
# ---------------------------------------------------------------------------
EXPECTED = {
    "GL lines": 13929,
    "Journals": 5504,
    "Total debits": 122878886.54,
    "Total credits": 122878886.54,
    "Unbalanced journals": 0,
    "Orphan GL account keys": 0,
    "Orphan GL vendor keys": 0,
    "Flagged journals": 171,
    "Flagged GL lines": 342,
    "Flagged value": 1945536.55,
    "Revenue FY2024": 13786573,
    "Revenue FY2025 9M": 10543059,
    "Gross margin FY2024 pct": 49.3,
    "Gross margin FY2025 pct": 50.5,
    "PAT FY2024": 447052,
    "PAT FY2025 9M": -61867,
    "AR at 30 Sep 2025": 3790174,
    "AP at 30 Sep 2025": 2373621,
    "Inventory at 30 Sep 2025": 871343,
    "Cash at 30 Sep 2025": 792548,
    "Cash prior year end": 925427,
    "Suspense at 30 Sep 2025": 51058.87,
    "Current assets": 5606400,
    "Current liabilities": 4147758,
    "Current ratio": 1.35,
    "DSO days": 98,
    "DPO days": 124,
    "DIO days": 46,
    "CCC days": 20,
    "Total supplier spend": 30505968,
    "Top vendor share pct": 5.3,
    "Top5 vendor share pct": 24.6,
    "Vendors to 80 pct": 19,
    "Vendors": 26,
    "AP invoices": 520,
    "AP 3-way match failures": 168,
    "AP invoices without PO": 109,
    "AP duplicate suspected": 18,
    "Bank transactions": 1400,
    "Unreconciled bank items": 129,
    "Unreconciled bank value": 1884271,
    "Unreconciled over 90 days": 27,
    "Oldest unmatched age days": 210,
    "Expense claims": 650,
    "Claims without receipt": 81,
    "AR ageing rows": 420,
    "Disputed accounts": 11,
    "Employee linked vendors": 4,
    "Ghost vendor total paid": 2773799.20,
    "Ghost vendor injected": 445568.39,
    "Duplicate lines": 42,
    "Duplicate value": 368023.48,
    "Duplicate overpayment": 184011.74,
    "Threshold lines": 30,
    "Threshold value": 207720.00,
    "Split lines": 42,
    "Split value": 223924.68,
    "Weekend lines": 21,
    "Weekend value": 406300.00,
    "SoD lines": 15,
    "SoD value": 279600.00,
    "Accrual lines": 6,
    "Accrual value": 14400.00,
    "Churn observations": 150,
    "Churn baseline pct": 51.1,
    "Churn accuracy pct": 68.9,
    "Churn precision pct": 71.4,
    "Churn recall pct": 65.2,
    "Churn specificity pct": 72.7,
    "Churn TP": 15,
    "Churn TN": 16,
    "Churn FP": 6,
    "Churn FN": 8,
    "Trial balance rows": 1323,
    "Budget rows": 1299,
    "Sales order rows": 900,
    "Fixed assets": 120,
    "Employees": 63,
    "Users": 12,
    "Customers": 18,
    "Cost centres": 9,
    "Date rows": 1461,
    "FX rows": 84,
    "Engagements": 160,
    "Churn rows": 150,
    "Pipeline rows": 240,
    "Billable hours rows": 330,
    "Service line rows": 231,
}


class Reconciliation:
    """Collects check results so every deliverable can print its own proof."""

    def __init__(self):
        self.rows = []

    def check(self, area, label, actual, expected, tolerance=0.01):
        ok = abs(float(actual) - float(expected)) <= tolerance
        self.rows.append({
            "Area": area, "Check": label, "Computed": actual,
            "Expected": expected, "Status": "Ties" if ok else "INVESTIGATE",
        })
        return ok

    @property
    def failures(self):
        return [r for r in self.rows if r["Status"] != "Ties"]

    @property
    def passes(self):
        return [r for r in self.rows if r["Status"] == "Ties"]

    def markdown(self):
        out = ["| Area | Check | Computed | Expected | Status |",
               "|---|---|---:|---:|:--:|"]
        for r in self.rows:
            def fmt(v):
                return f"{v:,.2f}" if isinstance(v, float) else f"{v:,}"
            out.append(f"| {r['Area']} | {r['Check']} | {fmt(r['Computed'])} | "
                       f"{fmt(r['Expected'])} | {r['Status']} |")
        return "\n".join(out)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------
def _num(s):
    s = (s or "").strip()
    return float(s) if s not in ("", "-") else 0.0


def read_csv(name):
    with open(os.path.join(RAW, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class Ledger:
    """The Mhondoro dataset, loaded once and typed once."""

    def __init__(self):
        self.accounts = {a["AccountCode"]: a for a in read_csv("DimAccount.csv")}
        self.vendors = read_csv("DimVendor.csv")
        self.vendor_by_id = {v["VendorID"]: v for v in self.vendors}
        self.customers = read_csv("DimCustomer.csv")
        self.customer_by_id = {c["CustomerID"]: c for c in self.customers}
        self.users = {u["UserID"]: u for u in read_csv("DimUser.csv")}
        self.employees = read_csv("DimEmployee.csv")
        self.cost_centres = read_csv("DimCostCentre.csv")
        self.dates = read_csv("DimDate.csv")
        self.tb = read_csv("FactTrialBalance.csv")
        self.ap = read_csv("FactAPInvoices.csv")
        self.ar = read_csv("FactARAgeing.csv")
        self.bank = read_csv("FactBankTransactions.csv")
        self.expenses = read_csv("FactExpenseClaims.csv")
        self.sales_orders = read_csv("FactSalesOrders.csv")
        self.budget = read_csv("FactBudget.csv")
        self.fixed_assets = read_csv("FactFixedAssets.csv")
        self.fx = read_csv("DimFXRate.csv")
        self.injection_log = read_csv("InjectionLog.csv")
        self.gl_raw = read_csv("FactGLJournal.csv")

        self.gl = []
        for r in self.gl_raw:
            acct = self.accounts[r["AccountCode"]]
            self.gl.append({
                "LineID": r["LineID"],
                "JournalID": r["JournalID"],
                "LineNo": r["LineNo"],
                "AccountCode": r["AccountCode"],
                "AccountName": acct["AccountName"],
                "AccountType": acct["AccountType"],
                "FSLine": acct["FSLine"],
                "Statement": acct["Statement"],
                "IsPL": acct["IsPL"] == "Yes",
                "PLSign": int(acct["PLSign"]),
                "IsCash": acct["IsCashAccount"] == "Yes",
                "IsSuspense": acct["IsSuspense"] == "Yes",
                "PostingDate": datetime.strptime(r["PostingDate"], "%Y-%m-%d").date(),
                "DocumentDate": datetime.strptime(r["DocumentDate"], "%Y-%m-%d").date(),
                "EnteredOn": datetime.strptime(r["EnteredOn"], "%Y-%m-%d %H:%M:%S"),
                "Period": r["Period"],
                "FiscalYear": int(r["FiscalYear"]),
                "Description": r["Description"],
                "Debit": _num(r["Debit"]),
                "Credit": _num(r["Credit"]),
                "AmountUSD": _num(r["AmountUSD"]),
                "AbsAmountUSD": _num(r["AbsAmountUSD"]),
                "CostCentreCode": r["CostCentreCode"],
                "PreparedBy": r["PreparedBy"],
                "ApprovedBy": r["ApprovedBy"],
                "SourceSystem": r["SourceSystem"],
                "EntryType": r["EntryType"],
                "IsReversal": r["IsReversal"] == "Yes",
                "VendorID": r["VendorID"],
                "CustomerID": r["CustomerID"],
                "AnomalyLabel": r["AnomalyLabel"],
                "Currency": r["Currency"],
                "FXRate": _num(r["FXRate"]),
            })
        self._journals = None

    # -- structure ----------------------------------------------------------
    @property
    def journals(self):
        if self._journals is None:
            j = defaultdict(list)
            for r in self.gl:
                j[r["JournalID"]].append(r)
            self._journals = j
        return self._journals

    def pl_value(self, r):
        """Revenue positive, expenses positive as costs."""
        return -r["AmountUSD"] * r["PLSign"]

    def bs_sign(self, code):
        return 1 if self.accounts[code]["AccountType"] == "Asset" else -1

    def balance_at(self, code, as_at=AS_AT):
        """Closing balance of one account in natural presentation sign."""
        return sum(r["AmountUSD"] for r in self.gl
                   if r["AccountCode"] == code and r["PostingDate"] <= as_at) * self.bs_sign(code)

    def fsline_at(self, fsline, as_at=AS_AT, statement="BS"):
        return sum(r["AmountUSD"] * self.bs_sign(r["AccountCode"])
                   for r in self.gl
                   if r["FSLine"] == fsline and r["Statement"] == statement
                   and r["PostingDate"] <= as_at)

    def accounts_at(self, codes, as_at=AS_AT):
        return sum(self.balance_at(c, as_at) for c in codes)

    def movement(self, code, start, end):
        return sum(r["AmountUSD"] * self.bs_sign(code) for r in self.gl
                   if r["AccountCode"] == code and start <= r["PostingDate"] <= end)


# ---------------------------------------------------------------------------
# Financial statements
# ---------------------------------------------------------------------------
def pl_by_fsline(led, fiscal_year=None, period=None, upto=None, exclude_entry_types=("Closing",)):
    out = defaultdict(float)
    for r in led.gl:
        if not r["IsPL"]:
            continue
        if exclude_entry_types and r["EntryType"] in exclude_entry_types:
            continue
        if fiscal_year is not None and r["FiscalYear"] != fiscal_year:
            continue
        if period is not None and r["Period"] != period:
            continue
        if upto is not None and r["PostingDate"] > upto:
            continue
        out[r["FSLine"]] += led.pl_value(r)
    return out


def pl_statement(led, fiscal_year=None, period=None, upto=None):
    pl = pl_by_fsline(led, fiscal_year=fiscal_year, period=period, upto=upto)
    revenue = pl["Revenue"]
    cos = pl["Cost of sales"]
    gross = revenue - cos
    opex = pl["Operating expenses"]
    operating = gross - opex
    finance = pl["Finance costs"]
    pre_tax = operating - finance
    tax = pl["Taxation"]
    deferred = pl["Deferred tax"]
    return {
        "Revenue": revenue, "Cost of sales": cos, "Gross profit": gross,
        "Operating expenses": opex, "Operating profit": operating,
        "Finance costs": finance, "Profit before tax": pre_tax,
        "Taxation": tax, "Deferred tax": deferred,
        "Profit after tax": pre_tax - tax - deferred,
        "Gross margin pct": (gross / revenue * 100) if revenue else 0.0,
        "Operating margin pct": (operating / revenue * 100) if revenue else 0.0,
    }


def fy2025(led, as_at=AS_AT):
    """Nine-month FY2025 = cumulative to date less the FY2024 full year."""
    cum = pl_statement(led, upto=as_at)
    prior = pl_statement(led, fiscal_year=2024)
    keys = ["Revenue", "Cost of sales", "Gross profit", "Operating expenses",
            "Operating profit", "Finance costs", "Profit before tax",
            "Taxation", "Deferred tax", "Profit after tax"]
    out = {k: cum[k] - prior[k] for k in keys}
    out["Gross margin pct"] = out["Gross profit"] / out["Revenue"] * 100 if out["Revenue"] else 0
    out["Operating margin pct"] = out["Operating profit"] / out["Revenue"] * 100 if out["Revenue"] else 0
    return out


BS_ASSET_LINES = ["Cash and cash equivalents", "Trade and other receivables",
                  "Inventories", "Property, plant and equipment",
                  "Investment property"]
BS_CURRENT_ASSETS = ["Cash and cash equivalents", "Trade and other receivables",
                     "Inventories"]
BS_LIAB_LINES = ["Trade and other payables", "Taxation", "Borrowings",
                 "Provisions", "Deferred tax liability"]
BS_CURRENT_LIAB_LINES = ["Trade and other payables", "Taxation"]
BS_EQUITY_LINES = ["Share capital", "Other reserves", "Retained earnings"]
DTA_ACCOUNT, DTL_ACCOUNT = "1600", "2400"


def balance_sheet(led, as_at=AS_AT):
    lines = {l: led.fsline_at(l, as_at) for l in
             BS_ASSET_LINES + BS_EQUITY_LINES}
    # the 'Deferred tax' FSLine spans one asset and one liability account
    lines["Deferred tax asset"] = led.balance_at(DTA_ACCOUNT, as_at)
    lines["Deferred tax liability"] = led.balance_at(DTL_ACCOUNT, as_at)
    for l in ["Trade and other payables", "Taxation", "Borrowings", "Provisions"]:
        lines[l] = led.fsline_at(l, as_at)
    suspense_credit = -led.balance_at(SUSPENSE_ACCOUNT, as_at)  # credit balance, positive
    asset_lines = BS_ASSET_LINES + ["Deferred tax asset"]
    total_assets = sum(lines[l] for l in asset_lines)
    current_assets = sum(lines[l] for l in BS_CURRENT_ASSETS)
    total_liabs = sum(lines[l] for l in BS_LIAB_LINES) + suspense_credit
    current_liabs = sum(lines[l] for l in BS_CURRENT_LIAB_LINES) + suspense_credit
    equity = sum(lines[l] for l in BS_EQUITY_LINES)
    cy_result = fy2025(led, as_at)["Profit after tax"]
    check = total_assets - (total_liabs + equity + cy_result)
    return {
        "lines": lines,
        "Asset lines": asset_lines,
        "Liability lines": BS_LIAB_LINES + ["Suspense (credit balance)"],
        "Suspense (credit balance)": suspense_credit,
        "Total assets": total_assets,
        "Current assets": current_assets,
        "Non-current assets": total_assets - current_assets,
        "Total liabilities": total_liabs,
        "Current liabilities": current_liabs,
        "Non-current liabilities": total_liabs - current_liabs,
        "Equity before current year result": equity,
        "Current year result": cy_result,
        "Total equity": equity + cy_result,
        "Total liabilities and equity": total_liabs + equity + cy_result,
        "BS check": check,
        "Current ratio": current_assets / current_liabs if current_liabs else 0.0,
    }


def ratio_inputs(led, as_at=AS_AT):
    return {
        "AR": led.balance_at(AR_ACCOUNT, as_at),
        "AP": led.balance_at(AP_ACCOUNT, as_at),
        "Inventory gross": led.accounts_at(("1200", "1210", "1220"), as_at),
        "Inventory provision": led.balance_at("1230", as_at),
        "Inventory net": led.accounts_at(INVENTORY_ACCOUNTS, as_at),
        "Cash": led.fsline_at("Cash and cash equivalents", as_at),
    }


def ratios(led, as_at=AS_AT, days_elapsed=DAYS_ELAPSED_FY2025):
    ri = ratio_inputs(led, as_at)
    p = fy2025(led, as_at)
    revenue, cos = p["Revenue"], p["Cost of sales"]
    dso = ri["AR"] / revenue * days_elapsed if revenue else 0
    dpo = ri["AP"] / cos * days_elapsed if cos else 0
    dio = ri["Inventory net"] / cos * days_elapsed if cos else 0
    return {
        "Inputs": ri, "Revenue": revenue, "Cost of sales": cos,
        "Days elapsed": days_elapsed,
        "DSO": dso, "DPO": dpo, "DIO": dio, "CCC": dso + dio - dpo,
        "Gross margin pct": p["Gross margin pct"],
        "Definitions": {
            "DSO": f"Closing trade receivables (1100) / nine-month revenue x {days_elapsed} days elapsed",
            "DPO": f"Closing trade payables (2000) / nine-month cost of sales x {days_elapsed} days elapsed",
            "DIO": f"Closing inventories net of provision (1200+1210+1220-1230) / nine-month cost of sales x {days_elapsed} days elapsed",
            "CCC": "DSO + DIO - DPO",
        },
    }


def monthly_pl(led):
    out = defaultdict(lambda: defaultdict(float))
    for r in led.gl:
        if r["IsPL"] and r["EntryType"] != "Closing":
            out[r["Period"]][r["FSLine"]] += led.pl_value(r)
    rows = []
    for period in sorted(out):
        pl = out[period]
        rev, cos = pl["Revenue"], pl["Cost of sales"]
        gross = rev - cos
        rows.append({
            "Period": period, "Revenue": rev, "Cost of sales": cos,
            "Gross profit": gross, "Operating expenses": pl["Operating expenses"],
            "Operating profit": gross - pl["Operating expenses"],
            "Finance costs": pl["Finance costs"],
            "Taxation": pl["Taxation"] + pl["Deferred tax"],
            "Profit after tax": gross - pl["Operating expenses"] - pl["Finance costs"]
                               - pl["Taxation"] - pl["Deferred tax"],
            "Gross margin pct": (gross / rev * 100) if rev else 0.0,
        })
    return rows


def monthly_balances(led, fsline, statement="BS"):
    movements = defaultdict(float)
    for r in led.gl:
        if r["FSLine"] == fsline and r["Statement"] == statement:
            movements[r["Period"]] += r["AmountUSD"] * led.bs_sign(r["AccountCode"])
    rows, opening = [], 0.0
    for period in sorted(movements):
        mv = movements[period]
        rows.append({"Period": period, "Opening": opening, "Movement": mv,
                     "Closing": opening + mv})
        opening += mv
    return rows


def cash_flow(led, as_at=AS_AT, start=None):
    """Indirect cash-flow statement built from the ledger movements; ties to the
    movement in cash by construction (checked by the reconciliation)."""
    start = start or date(2025, 1, 1)
    window = [r for r in led.gl if start <= r["PostingDate"] <= as_at]

    def move(pred):
        return sum(r["AmountUSD"] * led.bs_sign(r["AccountCode"])
                   for r in window if pred(r))

    pat = sum(led.pl_value(r) * r["PLSign"] for r in window if r["IsPL"])
    dep = -move(lambda r: r["AccountCode"] in ACC_DEP_ACCOUNTS)
    ppe = -move(lambda r: r["FSLine"] == "Property, plant and equipment"
                and r["AccountCode"] not in ACC_DEP_ACCOUNTS)
    inv_prop = -move(lambda r: r["FSLine"] == "Investment property")
    borrow = move(lambda r: r["FSLine"] == "Borrowings")
    equity_move = move(lambda r: r["FSLine"] in ("Share capital", "Other reserves",
                                                 "Retained earnings"))
    d_receiv = -move(lambda r: r["FSLine"] == "Trade and other receivables")
    d_invent = -move(lambda r: r["FSLine"] == "Inventories")
    d_payab = move(lambda r: r["FSLine"] == "Trade and other payables")
    d_tax = move(lambda r: r["FSLine"] == "Taxation" and r["Statement"] == "BS")
    d_prov = move(lambda r: r["FSLine"] == "Provisions")
    d_susp = -move(lambda r: r["FSLine"] == "Suspense - to be cleared")
    d_deftax = move(lambda r: r["FSLine"] == "Deferred tax" and r["Statement"] == "BS")
    operating = pat + dep + d_receiv + d_invent + d_payab + d_tax + d_prov \
        + d_susp + d_deftax
    investing = ppe + inv_prop
    financing = borrow + equity_move
    opening_cash = led.fsline_at("Cash and cash equivalents", start - timedelta(days=1))
    closing_cash = led.fsline_at("Cash and cash equivalents", as_at)
    return {
        "Profit after tax": pat,
        "Depreciation (non-cash)": dep,
        "(Increase)/decrease in trade and other receivables": d_receiv,
        "(Increase)/decrease in inventories": d_invent,
        "Increase/(decrease) in trade and other payables": d_payab,
        "Increase/(decrease) in taxation payable": d_tax,
        "Movement in provisions": d_prov,
        "Movement in suspense account": d_susp,
        "Movement in deferred tax": d_deftax,
        "Net cash from operating activities": operating,
        "Purchase of property, plant and equipment": ppe,
        "Movement in investment property": inv_prop,
        "Net cash used in investing activities": investing,
        "Movement in borrowings": borrow,
        "Movement in equity (dividends, reserves, share capital)": equity_move,
        "Net cash from financing activities": financing,
        "Net movement in cash": operating + investing + financing,
        "Cash at beginning of period": opening_cash,
        "Cash at end of period": closing_cash,
        "Tie check": (opening_cash + operating + investing + financing) - closing_cash,
    }


# ---------------------------------------------------------------------------
# Sub-ledger and control analytics
# ---------------------------------------------------------------------------
def control_totals(led):
    jdr, jcr = defaultdict(float), defaultdict(float)
    for r in led.gl:
        jdr[r["JournalID"]] += r["Debit"]
        jcr[r["JournalID"]] += r["Credit"]
    unbalanced = {j: (jdr[j], jcr[j]) for j in jdr if abs(jdr[j] - jcr[j]) > 0.005}
    acct_keys = set(led.accounts)
    vendor_keys = set(led.vendor_by_id)
    orphan_acct = {r["LineID"] for r in led.gl if r["AccountCode"] not in acct_keys}
    orphan_vendor = {r["LineID"] for r in led.gl
                     if r["VendorID"] and r["VendorID"] not in vendor_keys}
    return {
        "GL lines": len(led.gl),
        "Journals": len(jdr),
        "Total debits": sum(r["Debit"] for r in led.gl),
        "Total credits": sum(r["Credit"] for r in led.gl),
        "Unbalanced journals": len(unbalanced),
        "Orphan GL account keys": len(orphan_acct),
        "Orphan GL vendor keys": len(orphan_vendor),
        "Periods covered": len({r["Period"] for r in led.gl}),
        "First posting": min(r["PostingDate"] for r in led.gl),
        "Last posting": max(r["PostingDate"] for r in led.gl),
        "Manual journals": sum(1 for r in led.gl if r["EntryType"] == "Manual"),
        "Automatic lines": sum(1 for r in led.gl if r["EntryType"] == "Automatic"),
    }


def trial_balance(led, as_at=AS_AT):
    """Account-level trial balance at a date, reconciling to the sub-ledger."""
    rows = []
    for code in sorted(led.accounts):
        a = led.accounts[code]
        opening = sum(r["AmountUSD"] for r in led.gl
                      if r["AccountCode"] == code and r["PostingDate"] < PERIOD_START)
        dr = sum(r["Debit"] for r in led.gl
                 if r["AccountCode"] == code and r["PostingDate"] <= as_at)
        cr = sum(r["Credit"] for r in led.gl
                 if r["AccountCode"] == code and r["PostingDate"] <= as_at)
        closing = dr - cr
        rows.append({
            "AccountCode": code, "AccountName": a["AccountName"],
            "AccountType": a["AccountType"], "FSLine": a["FSLine"],
            "Statement": a["Statement"],
            "Opening": opening, "Debit": dr, "Credit": cr,
            "Closing": closing,
            "Closing (presentation sign)": closing * led.bs_sign(code),
        })
    return rows


def reconcile_trial_balance(led):
    """Our GL-derived TB vs the delivered FactTrialBalance closing balances.
    The delivered file states balances in natural normal-balance sign (a credit
    balance on a credit-normal account is positive), so we compare on that basis."""
    delivered = {(r["AccountCode"], r["Period"]): _num(r["ClosingBalance"]) for r in led.tb}
    diffs = []
    for r in trial_balance(led):
        key = (r["AccountCode"], "2025-09")
        if key in delivered:
            natural = r["Closing"] * (1 if led.accounts[r["AccountCode"]]["NormalBalance"] == "Debit" else -1)
            diff = natural - delivered[key]
            if abs(diff) > 0.01:
                diffs.append({"AccountCode": key[0], "GL derived": natural,
                              "Delivered": delivered[key], "Difference": diff})
    return diffs


def spend_analytics(led):
    """Supplier spend measured on the general ledger (debits to vendor accounts).
    This is the population Capstone 3 quotes ($30,505,968 across 26 vendors);
    the 520-line AP invoice extract is a partial sub-ledger sample and is
    reported separately with the difference disclosed."""
    spend, invoices = defaultdict(float), defaultdict(set)
    for r in led.gl:
        if r["VendorID"] and r["Debit"] > 0:
            spend[r["VendorID"]] += r["Debit"]
            invoices[r["VendorID"]].add(r["Description"])
    total = sum(spend.values())
    ranked = sorted(spend.items(), key=lambda kv: -kv[1])
    cum, pareto = 0.0, []
    for i, (vid, amt) in enumerate(ranked, 1):
        cum += amt
        v = led.vendor_by_id.get(vid, {})
        pareto.append({
            "Rank": i, "VendorID": vid, "VendorName": v.get("VendorName", ""),
            "Category": v.get("Category", ""), "AmountUSD": amt,
            "Postings": len(invoices[vid]),
            "Share pct": amt / total * 100, "Cumulative pct": cum / total * 100,
            "EmployeeLinked": v.get("IsEmployeeLinked") == "Yes",
            "LastBankChangeDate": v.get("LastBankChangeDate", ""),
            "BankName": v.get("BankName", ""),
            "TaxClearanceNo": v.get("TaxClearanceNo", ""),
            "VendorCreatedOn": v.get("VendorCreatedOn", ""),
        })
    vendors_to_80 = next(p["Rank"] for p in pareto if p["Cumulative pct"] >= 80)
    return {
        "pareto": pareto, "total": total, "vendors": len(pareto),
        "top1_pct": pareto[0]["Share pct"],
        "top5_pct": sum(p["Share pct"] for p in pareto[:5]),
        "vendors_to_80": vendors_to_80,
        "employee_linked": [p for p in pareto if p["EmployeeLinked"]],
        "employee_linked_total": sum(p["AmountUSD"] for p in pareto if p["EmployeeLinked"]),
    }


def ap_analytics(led):
    rows = []
    for r in led.ap:
        rows.append({
            "APInvoiceNo": r["APInvoiceNo"],
            "SupplierInvoiceRef": r["SupplierInvoiceRef"],
            "VendorID": r["VendorID"],
            "VendorName": led.vendor_by_id.get(r["VendorID"], {}).get("VendorName", ""),
            "InvoiceDate": r["InvoiceDate"],
            "AmountUSD": _num(r["AmountUSD"]),
            "PONumber": r["PONumber"],
            "GRNNumber": r["GRNNumber"],
            "ThreeWayMatch": r["ThreeWayMatch"],
            "DuplicateSuspected": r["DuplicateSuspected"] == "Yes",
            "ApprovedBy": r["ApprovedBy"],
            "PaidStatus": r["PaidStatus"],
            "PaymentDate": r["PaymentDate"],
            "EmployeeLinked": led.vendor_by_id.get(r["VendorID"], {}).get("IsEmployeeLinked") == "Yes",
        })
    total = sum(r["AmountUSD"] for r in rows)
    by_vendor = defaultdict(lambda: {"AmountUSD": 0.0, "Invoices": 0})
    for r in rows:
        by_vendor[r["VendorID"]]["AmountUSD"] += r["AmountUSD"]
        by_vendor[r["VendorID"]]["Invoices"] += 1
    ranked = sorted(by_vendor.items(), key=lambda kv: -kv[1]["AmountUSD"])
    cum, pareto = 0.0, []
    for i, (vid, v) in enumerate(ranked, 1):
        cum += v["AmountUSD"]
        pareto.append({"Rank": i, "VendorID": vid,
                       "VendorName": led.vendor_by_id.get(vid, {}).get("VendorName", ""),
                       "AmountUSD": v["AmountUSD"], "Invoices": v["Invoices"],
                       "Share pct": v["AmountUSD"] / total * 100,
                       "Cumulative pct": cum / total * 100})
    return {
        "rows": rows, "pareto": pareto, "total": total,
        "count": len(rows),
        "three_way_fail": sum(1 for r in rows if r["ThreeWayMatch"] != "Matched"),
        "three_way_matched": sum(1 for r in rows if r["ThreeWayMatch"] == "Matched"),
        "three_way_fail_value": sum(r["AmountUSD"] for r in rows
                                    if r["ThreeWayMatch"] != "Matched"),
        "three_way_fail_pct": sum(1 for r in rows if r["ThreeWayMatch"] != "Matched") / len(rows) * 100,
        "no_po": sum(1 for r in rows if not r["PONumber"]),
        "no_po_value": sum(r["AmountUSD"] for r in rows if not r["PONumber"]),
        "no_grn": sum(1 for r in rows if r["PONumber"] and not r["GRNNumber"]),
        "duplicate_suspected": sum(1 for r in rows if r["DuplicateSuspected"]),
        "duplicate_suspected_value": sum(r["AmountUSD"] for r in rows if r["DuplicateSuspected"]),
        "outstanding": sum(r["AmountUSD"] for r in rows if r["PaidStatus"] == "Outstanding"),
        "outstanding_count": sum(1 for r in rows if r["PaidStatus"] == "Outstanding"),
        "employee_linked_value": sum(r["AmountUSD"] for r in rows if r["EmployeeLinked"]),
        "vendors_to_80_ap": next(p["Rank"] for p in pareto if p["Cumulative pct"] >= 80),
    }


def ap_by_vendor(led, ap):
    """Three-way-match and control performance per vendor, on the AP extract."""
    agg = defaultdict(lambda: {"Invoices": 0, "AmountUSD": 0.0, "Exceptions": 0,
                               "NoPO": 0, "NoGRN": 0, "DuplicateSuspected": 0})
    for r in ap["rows"]:
        a = agg[r["VendorID"]]
        a["Invoices"] += 1
        a["AmountUSD"] += r["AmountUSD"]
        if r["ThreeWayMatch"] != "Matched":
            a["Exceptions"] += 1
        if not r["PONumber"]:
            a["NoPO"] += 1
        elif not r["GRNNumber"]:
            a["NoGRN"] += 1
        if r["DuplicateSuspected"]:
            a["DuplicateSuspected"] += 1
    out = []
    for vid, a in sorted(agg.items(), key=lambda kv: -kv[1]["AmountUSD"]):
        v = led.vendor_by_id.get(vid, {})
        out.append({
            "VendorID": vid, "VendorName": v.get("VendorName", ""),
            "Category": v.get("Category", ""),
            "Invoices": a["Invoices"], "AmountUSD": a["AmountUSD"],
            "Avg invoice": a["AmountUSD"] / a["Invoices"] if a["Invoices"] else 0,
            "3-way exceptions": a["Exceptions"],
            "Exception rate pct": a["Exceptions"] / a["Invoices"] * 100 if a["Invoices"] else 0,
            "No PO": a["NoPO"], "PO but no GRN": a["NoGRN"],
            "Duplicate suspected": a["DuplicateSuspected"],
            "Employee linked": v.get("IsEmployeeLinked") == "Yes",
            "Tax clearance": "Yes" if v.get("TaxClearanceNo") else "No",
            "Last invoice": max((r["InvoiceDate"] for r in ap["rows"]
                                 if r["VendorID"] == vid), default=""),
        })
    return out


def ar_analytics(led):
    rows = []
    for r in led.ar:
        amt, rec = _num(r["AmountUSD"]), _num(r["AmountReceivedUSD"])
        rows.append({
            "InvoiceNo": r["InvoiceNo"], "CustomerID": r["CustomerID"],
            "CustomerName": led.customer_by_id.get(r["CustomerID"], {}).get("CustomerName", ""),
            "InvoiceDate": r["InvoiceDate"], "DueDate": r["DueDate"],
            "AmountUSD": amt, "AmountReceivedUSD": rec, "OutstandingUSD": amt - rec,
            "DaysOverdue": int(float(r["DaysOverdue"] or 0)),
            "AgeingBucket": r["AgeingBucket"],
            "Disputed": r["DisputedFlag"] == "Yes",
            "AsAtDate": r["AsAtDate"],
        })
    by_bucket = defaultdict(lambda: {"Invoices": 0, "OutstandingUSD": 0.0})
    for r in rows:
        by_bucket[r["AgeingBucket"]]["Invoices"] += 1
        by_bucket[r["AgeingBucket"]]["OutstandingUSD"] += r["OutstandingUSD"]
    return {"rows": rows, "by_bucket": dict(by_bucket),
            "outstanding": sum(r["OutstandingUSD"] for r in rows),
            "disputed": sum(1 for r in rows if r["Disputed"]),
            "invoices": len(rows)}


def bank_analytics(led):
    rows = []
    for r in led.bank:
        rows.append({
            "BankTxnID": r["BankTxnID"], "BankAccount": r["BankAccount"],
            "TxnDate": r["TxnDate"], "Narration": r["Narration"],
            "DebitUSD": _num(r["DebitUSD"]), "CreditUSD": _num(r["CreditUSD"]),
            "Reconciled": r["ReconciledFlag"] == "Yes",
            "AgeDays": int(float(r["UnmatchedItemsAgeDays"] or 0)),
        })
    unrec = [r for r in rows if not r["Reconciled"]]
    return {
        "rows": rows, "unreconciled": unrec,
        "count": len(rows),
        "unreconciled_count": len(unrec),
        "unreconciled_value": sum(r["DebitUSD"] + r["CreditUSD"] for r in unrec),
        "over_90_days": sum(1 for r in unrec if r["AgeDays"] > 90),
        "oldest_age": max((r["AgeDays"] for r in unrec), default=0),
    }


def expense_analytics(led):
    rows = [{"ClaimID": r["ClaimID"], "EmployeeName": r["EmployeeName"],
             "ClaimDate": r["ClaimDate"], "Period": r["Period"],
             "ExpenseCategory": r["ExpenseCategory"],
             "ClaimedUSD": _num(r["ClaimedUSD"]),
             "ReceiptAttached": r["ReceiptAttached"] == "Yes",
             "ApprovedBy": r["ApprovedBy"],
             "DuplicateSuspected": r["DuplicateSuspected"] == "Yes",
             "WeekendClaim": r["WeekendClaim"] == "Yes"} for r in led.expenses]
    return {"rows": rows, "count": len(rows),
            "no_receipt": sum(1 for r in rows if not r["ReceiptAttached"]),
            "no_receipt_value": sum(r["ClaimedUSD"] for r in rows if not r["ReceiptAttached"]),
            "weekend": sum(1 for r in rows if r["WeekendClaim"]),
            "total": sum(r["ClaimedUSD"] for r in rows)}
