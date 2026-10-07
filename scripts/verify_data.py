#!/usr/bin/env python3
"""
verify_data.py - control checks on the Mhondoro practice dataset.

Run this after generating data (or after a client extract) and reconcile the
output to the expected results printed in the labs. This is the same discipline
you apply on an engagement: prove the population before you report on it.

Usage: python3 scripts/verify_data.py
"""
import csv
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")

EXPECTED = {
    "Total debits": 122878886.54,
    "Total credits": 122878886.54,
    "GL lines": 13929,
    "Flagged anomaly lines": 171,
    "Flagged anomaly value": 1945536.55,
}

failures = []


def load(name):
    path = os.path.join(RAW, name)
    if not os.path.exists(path):
        print(f"!! missing file: {name} - run scripts/generate_data.py first")
        sys.exit(1)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def check(label, actual, expected, tolerance=0.01):
    ok = abs(actual - expected) <= tolerance if isinstance(expected, float) else actual == expected
    mark = "OK  " if ok else "FAIL"
    print(f"  [{mark}] {label:<38}{actual:>18,.2f}   expected {expected:>18,.2f}")
    if not ok:
        failures.append(label)


def main():
    print("\nMhondoro Manufacturing - data verification\n")

    gl = load("FactGLJournal.csv")
    acct = {a["AccountCode"]: a for a in load("DimAccount.csv")}
    inj = load("InjectionLog.csv")
    vendors = load("DimVendor.csv")

    debits = sum(float(r["Debit"]) for r in gl)
    credits = sum(float(r["Credit"]) for r in gl)
    check("GL lines", len(gl), EXPECTED["GL lines"])
    check("Total debits", debits, EXPECTED["Total debits"])
    check("Total credits", credits, EXPECTED["Total credits"])

    flagged = [r for r in gl if r["AnomalyLabel"]]
    flagged_journals = {r["JournalID"] for r in flagged}
    flag_value = sum(float(r["Debit"]) for r in flagged if float(r["Debit"]) > 0)
    check("Flagged anomaly journals", len(flagged_journals), EXPECTED["Flagged anomaly lines"])
    print(f"         (flagged GL lines including both sides of each entry: {len(flagged)})")
    check("Flagged anomaly value", flag_value, EXPECTED["Flagged anomaly value"])

    print("\n  Journal-level balance test (every JournalID must balance):")
    jdr, jcr = defaultdict(float), defaultdict(float)
    for r in gl:
        jdr[r["JournalID"]] += float(r["Debit"])
        jcr[r["JournalID"]] += float(r["Credit"])
    unbal = [j for j in jdr if abs(jdr[j] - jcr.get(j, 0.0)) > 0.005]
    print(f"  [{'OK  ' if not unbal else 'FAIL'}] unbalanced journals: {len(unbal)}")
    if unbal:
        failures.append("unbalanced journals")
        for j in unbal[:5]:
            print(f"        {j}: Dr {jdr[j]:,.2f} vs Cr {jcr.get(j,0):,.2f}")

    print("\n  Orphan key test (fact rows with no matching dimension row):")
    codes = set(acct)
    orphans = {r["AccountCode"] for r in gl} - codes
    print(f"  [{'OK  ' if not orphans else 'FAIL'}] GL account codes not in DimAccount: {len(orphans)}")
    if orphans:
        failures.append("orphan account codes")
        print("        ", sorted(orphans))

    vids = {v["VendorID"] for v in vendors}
    vorp = {r["VendorID"] for r in gl if r["VendorID"]} - vids
    print(f"  [{'OK  ' if not vorp else 'FAIL'}] GL vendor IDs not in DimVendor: {len(vorp)}")

    print("\n  Forensic test preview (what Module 9 should find):")
    by_type = defaultdict(lambda: [0, 0.0])
    for r in flagged:
        if float(r["Debit"]) > 0:
            by_type[r["AnomalyLabel"]][0] += 1
            by_type[r["AnomalyLabel"]][1] += float(r["Debit"])
    for t, (n, v) in sorted(by_type.items()):
        print(f"        {t:<24}{n:>4} lines   ${v:>13,.2f}")

    ghost = [v for v in vendors if v["IsEmployeeLinked"] == "Yes"]
    ghost_spend = sum(float(r["Debit"]) for r in gl if r["VendorID"] in {g["VendorID"] for g in ghost})
    print(f"\n  Employee-linked (ghost) vendors: {len(ghost)}  | total paid: ${ghost_spend:,.2f}")
    suspense = sum(float(r["Credit"]) - float(r["Debit"]) for r in gl if r["AccountCode"] == "1990")
    print(f"  Suspense account balance: ${suspense:,.2f}")

    print("\n  Data quality observations (report, do not hide):")
    bank = load("FactBankTransactions.csv")
    unrecon = sum(1 for r in bank if r["ReconciledFlag"] == "No")
    print(f"        unreconciled bank transactions: {unrecon} of {len(bank)}")
    ap = load("FactAPInvoices.csv")
    nomatch = sum(1 for r in ap if r["ThreeWayMatch"] == "Exception")
    print(f"        AP invoices failing 3-way match: {nomatch} of {len(ap)}")
    claims = load("FactExpenseClaims.csv")
    noreceipt = sum(1 for r in claims if r["ReceiptAttached"] == "No")
    print(f"        expense claims without a receipt: {noreceipt} of {len(claims)}")

    print()
    if failures:
        print(f"  RESULT: {len(failures)} check(s) FAILED - investigate before continuing.\n")
        sys.exit(1)
    print("  RESULT: all control checks passed. The population is fit to report on.\n")


if __name__ == "__main__":
    main()
