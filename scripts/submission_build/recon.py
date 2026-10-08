"""
recon.py - the reconciliation harness.

Runs every control check the submission depends on and returns a
`Reconciliation` object.  This is the evidence behind the close-pack pages, the
data-governance record and the QC checklist: no number is reported anywhere in
the pack unless it appears here as "Ties".

Usage:  python3 scripts/build_submission.py --recon
"""
from __future__ import annotations

from . import common as C


def run(led=None):
    led = led or C.Ledger()
    R = C.Reconciliation()

    ct = C.control_totals(led)
    for k in ["GL lines", "Journals", "Unbalanced journals",
              "Orphan GL account keys", "Orphan GL vendor keys"]:
        R.check("Control totals", k, ct[k], C.EXPECTED[k], 0)
    R.check("Control totals", "Total debits", ct["Total debits"], C.EXPECTED["Total debits"])
    R.check("Control totals", "Total credits", ct["Total credits"], C.EXPECTED["Total credits"])
    R.check("Control totals", "Debits less credits", ct["Total debits"] - ct["Total credits"], 0.0)

    p24 = C.pl_statement(led, fiscal_year=2024)
    p25 = C.fy2025(led)
    R.check("Profit or loss", "Revenue FY2024", round(p24["Revenue"], 2), C.EXPECTED["Revenue FY2024"], 1.0)
    R.check("Profit or loss", "Revenue FY2025 (9 months)", round(p25["Revenue"], 2),
            C.EXPECTED["Revenue FY2025 9M"], 1.0)
    R.check("Profit or loss", "Gross margin FY2024 %", round(p24["Gross margin pct"], 1),
            C.EXPECTED["Gross margin FY2024 pct"], 0.06)
    R.check("Profit or loss", "Gross margin FY2025 %", round(p25["Gross margin pct"], 1),
            C.EXPECTED["Gross margin FY2025 pct"], 0.06)
    R.check("Profit or loss", "Profit after tax FY2024", round(p24["Profit after tax"], 2),
            C.EXPECTED["PAT FY2024"], 1.0)
    R.check("Profit or loss", "Profit after tax FY2025 (9 months)",
            round(p25["Profit after tax"], 2), C.EXPECTED["PAT FY2025 9M"], 1.0)

    bs = C.balance_sheet(led)
    ri = C.ratio_inputs(led)
    rt = C.ratios(led)
    R.check("Balance sheet", "Trade receivables (1100)", round(ri["AR"], 2), C.EXPECTED["AR at 30 Sep 2025"], 1.0)
    R.check("Balance sheet", "Trade payables (2000)", round(ri["AP"], 2), C.EXPECTED["AP at 30 Sep 2025"], 1.0)
    R.check("Balance sheet", "Inventories net of provision", round(ri["Inventory net"], 2),
            C.EXPECTED["Inventory at 30 Sep 2025"], 1.0)
    R.check("Balance sheet", "Cash and cash equivalents", round(ri["Cash"], 2),
            C.EXPECTED["Cash at 30 Sep 2025"], 1.0)
    R.check("Balance sheet", "Suspense account credit balance", round(bs["Suspense (credit balance)"], 2),
            C.EXPECTED["Suspense at 30 Sep 2025"])
    R.check("Balance sheet", "Current assets", round(bs["Current assets"], 2), C.EXPECTED["Current assets"], 1.0)
    R.check("Balance sheet", "Current liabilities", round(bs["Current liabilities"], 2),
            C.EXPECTED["Current liabilities"], 1.0)
    R.check("Balance sheet", "Current ratio", round(bs["Current ratio"], 2), C.EXPECTED["Current ratio"], 0.005)
    R.check("Balance sheet", "Balance sheet check  A - (L + E + CYR)", round(bs["BS check"], 2), 0.0, 0.02)

    for k in ["DSO", "DPO", "DIO", "CCC"]:
        R.check("Ratios", k, round(rt[k]), C.EXPECTED[f"{k} days"], 0.5)

    cf = C.cash_flow(led)
    R.check("Cash flow", "Opening cash 31 Dec 2024", round(cf["Cash at beginning of period"], 2),
            C.EXPECTED["Cash prior year end"], 1.0)
    R.check("Cash flow", "Closing cash 30 Sep 2025", round(cf["Cash at end of period"], 2),
            C.EXPECTED["Cash at 30 Sep 2025"], 1.0)
    R.check("Cash flow", "Net movement ties to cash accounts", round(cf["Tie check"], 2), 0.0, 0.02)

    sp = C.spend_analytics(led)
    R.check("Procurement", "Total supplier spend (GL)", round(sp["total"], 2),
            C.EXPECTED["Total supplier spend"], 1.0)
    R.check("Procurement", "Vendors paid", sp["vendors"], C.EXPECTED["Vendors"], 0)
    R.check("Procurement", "Largest vendor share %", round(sp["top1_pct"], 1),
            C.EXPECTED["Top vendor share pct"], 0.06)
    R.check("Procurement", "Top five vendors share %", round(sp["top5_pct"], 1),
            C.EXPECTED["Top5 vendor share pct"], 0.06)
    R.check("Procurement", "Vendors to reach 80% of spend", sp["vendors_to_80"],
            C.EXPECTED["Vendors to 80 pct"], 0)

    ap = C.ap_analytics(led)
    R.check("Sub-ledgers", "AP invoices in extract", ap["count"], C.EXPECTED["AP invoices"], 0)
    R.check("Sub-ledgers", "AP invoices failing three-way match", ap["three_way_fail"],
            C.EXPECTED["AP 3-way match failures"], 0)
    R.check("Sub-ledgers", "AP invoices with no purchase order", ap["no_po"],
            C.EXPECTED["AP invoices without PO"], 0)
    R.check("Sub-ledgers", "AP invoices flagged duplicate", ap["duplicate_suspected"],
            C.EXPECTED["AP duplicate suspected"], 0)

    ar = C.ar_analytics(led)
    R.check("Sub-ledgers", "AR ageing rows", ar["invoices"], C.EXPECTED["AR ageing rows"], 0)
    R.check("Sub-ledgers", "Disputed customer accounts", ar["disputed"], C.EXPECTED["Disputed accounts"], 0)

    bk = C.bank_analytics(led)
    R.check("Sub-ledgers", "Bank transactions", bk["count"], C.EXPECTED["Bank transactions"], 0)
    R.check("Sub-ledgers", "Unreconciled bank items", bk["unreconciled_count"],
            C.EXPECTED["Unreconciled bank items"], 0)
    R.check("Sub-ledgers", "Unreconciled bank value", round(bk["unreconciled_value"], 2),
            C.EXPECTED["Unreconciled bank value"], 1.0)
    R.check("Sub-ledgers", "Unreconciled items over 90 days", bk["over_90_days"],
            C.EXPECTED["Unreconciled over 90 days"], 0)
    R.check("Sub-ledgers", "Oldest unmatched item (days)", bk["oldest_age"],
            C.EXPECTED["Oldest unmatched age days"], 0)

    ex = C.expense_analytics(led)
    R.check("Sub-ledgers", "Expense claims", ex["count"], C.EXPECTED["Expense claims"], 0)
    R.check("Sub-ledgers", "Claims without a receipt", ex["no_receipt"],
            C.EXPECTED["Claims without receipt"], 0)

    # forensic headline - recomputed by forensic.py and asserted there too
    fl = [r for r in led.gl if r["AnomalyLabel"]]
    journals = {r["JournalID"] for r in fl}
    value = sum(r["Debit"] for r in fl if r["Debit"] > 0)
    R.check("Forensic", "Flagged journals (per extract label)", len(journals),
            C.EXPECTED["Flagged journals"], 0)
    R.check("Forensic", "Flagged GL lines (both sides)", len(fl), C.EXPECTED["Flagged GL lines"], 0)
    R.check("Forensic", "Flagged value (debit side)", round(value, 2), C.EXPECTED["Flagged value"])

    ghosts = [v for v in led.vendors if v["IsEmployeeLinked"] == "Yes"]
    ghost_total = sum(r["Debit"] for r in led.gl if r["VendorID"] in {g["VendorID"] for g in ghosts})
    R.check("Forensic", "Employee-linked vendors", len(ghosts), C.EXPECTED["Employee linked vendors"], 0)
    R.check("Forensic", "Total paid to employee-linked vendors", round(ghost_total, 2),
            C.EXPECTED["Ghost vendor total paid"])

    # row counts of every table used, so the data request list can be proved
    tables = {
        "Trial balance rows": len(led.tb), "Budget rows": len(led.budget),
        "Sales order rows": len(led.sales_orders), "Fixed assets": len(led.fixed_assets),
        "Employees": len(led.employees), "Users": len(led.users),
        "Customers": len(led.customers), "Cost centres": len(led.cost_centres),
        "Date rows": len(led.dates), "FX rows": len(led.fx),
    }
    for k, v in tables.items():
        R.check("Data inventory", k, v, C.EXPECTED[k], 0)

    diffs = C.reconcile_trial_balance(led)
    R.check("Reconciliation", "Accounts differing from delivered trial balance",
            len(diffs), 0, 0)
    return R, {"ledger": led, "control_totals": ct, "pl_2024": p24, "pl_2025": p25,
               "balance_sheet": bs, "ratio_inputs": ri, "ratios": rt,
               "cash_flow": cf, "spend": sp, "ap": ap, "ar": ar, "bank": bk,
               "expenses": ex, "tb_diffs": diffs}


if __name__ == "__main__":
    R, ctx = run()
    print(R.markdown())
    print(f"\n{len(R.passes)} checks tie; {len(R.failures)} require investigation")
    for f in R.failures:
        print("  INVESTIGATE:", f)
