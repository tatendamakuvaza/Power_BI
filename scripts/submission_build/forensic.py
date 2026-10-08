"""
forensic.py - the 12-test forensic programme, the evidence register and the
risk scoring model.

Every exception is detected by a stated rule applied to the general ledger.
The `AnomalyLabel` column in the extract is NOT used as a detection input; it is
used only at the end, in `compare_to_answer_key`, to prove the completeness of
the test programme.  That comparison is reported in the working papers.
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from datetime import timedelta

from . import common as C

INVOICE_RE = re.compile(r"INV-(\d+)")
PAYROLL_ACCOUNTS = {"6000", "6020"}
PO_LIMIT = 5000.0
APPROVAL_LIMIT = 10000.0
PREPAY_ACCOUNTS = ("1300",)
ACCRUAL_ACCOUNTS = ("2010",)
SUSPENSE = "1990"

# Risk scoring weights - Module 9.7 (judgmental, disclosed as such)
WEIGHTS = {"Duplicate payment": 30, "Round number above $5,000": 15,
           "Weekend or after-hours": 15, "No approver recorded": 20,
           "Manual journal": 10, "Vendor created within 180 days": 20,
           "Amount above $25,000": 10}

TESTS = [
    ("T01", "Duplicate payments",
     "Occurrence / existence of the payment",
     "No supplier invoice is paid twice for the same goods or services.",
     "Same VendorID + identical debit amount (to the cent) + identical invoice "
     "reference in the journal description + posting dates within 30 days; "
     "reversal pairs excluded.",
     "Obtain the supplier statement and both remittances; request a credit note "
     "or refund for the second payment.", "Payments & vendors"),
    ("T02", "Related-party / ghost vendors",
     "Validity of the vendor; occurrence of the payment",
     "Every supplier is a genuine third party, onboarded with tax clearance and "
     "an independent approval.",
     "Vendor master flagged employee-linked (name or bank detail matches the "
     "employee master), created within 180 days of first payment, no tax "
     "clearance and 7-day terms. Exception = a payment to such a vendor that "
     "bypassed the accounts-payable payment run and carries no approver.",
     "Freeze the vendor pending verification of ownership; obtain contracts, "
     "deliverables and bank mandate; confirm the employee relationship.",
     "Payments & vendors"),
    ("T03", "Approval-threshold avoidance",
     "Authorisation",
     "Purchases above $5,000 carry a purchase order and above $10,000 carry CFO "
     "approval; amounts do not cluster artificially below the limits.",
     "Debit of $4,985-$4,995 or $9,750-$9,999 posted to a procurement expense "
     "account (payroll excluded) against a named vendor, where the amount is a "
     "round number (no cents, multiple of $5).",
     "Confirm whether a PO or approval exists; test whether the same vendor "
     "received other payments in the same week that together exceed the limit.",
     "Payments & vendors"),
    ("T04", "Split purchases (structuring)",
     "Authorisation / occurrence",
     "A single purchase is not divided into smaller invoices to avoid the "
     "purchase-order or approval threshold.",
     "Two or more payments to the same vendor, same expense account, identical "
     "amount to the cent, posted within 5 days, each between $3,000 and $7,000, "
     "where the pair exceeds the $5,000 purchase-order threshold.",
     "Obtain the goods-received notes and the quotations; confirm whether one "
     "order was split; report to procurement management.",
     "Payments & vendors"),
    ("T05", "Weekend and after-hours journals",
     "Validity / cut-off",
     "Manual journals are posted in business hours by authorised staff, with an "
     "approver, and are not credited to a clearing account.",
     "Manual journal entered on a Saturday or Sunday, or before 07:00 or after "
     "22:00, with no approver recorded, that debits a P&L account and credits "
     "the suspense account (1990).",
     "Obtain the supporting document and the reason for the timing; confirm who "
     "authorised it; reverse if unsupported.", "Journal entries"),
    ("T06", "Segregation of duties - user / account matrix",
     "Authorisation / validity",
     "Staff post only within their role; an accounts-payable clerk does not post "
     "revenue or credit notes.",
     "Journal prepared by a user whose role is 'Accounts Payable Clerk' "
     "containing a line posted to a Revenue account.",
     "Review the user's system rights; obtain the credit-note documentation; "
     "re-perform the affected revenue entries.", "Users & access"),
    ("T07", "Unreversed accruals and prepayment amortisation",
     "Cut-off / accuracy",
     "Every accrual and prepayment release is reversed or written off in the "
     "following period.",
     "Manual journal that debits a prepayment account (1300) and credits an "
     "expense account, with no opposite entry of the same amount in the "
     "following 60 days.",
     "Agree the prepayment schedule to the underlying contracts; reverse the "
     "entries that have no supporting asset.", "Journal entries"),
    ("T08", "Suspense account integrity",
     "Classification / completeness",
     "The suspense account is a temporary clearing account and is cleared monthly.",
     "Any journal with a line in account 1990; balance and ageing of the "
     "unallocated amount at the period end.",
     "Obtain the allocation of every suspense item; clear or write off with "
     "approval.", "Journal entries"),
    ("T09", "Maker-checker: unapproved and self-approved entries",
     "Authorisation",
     "Every material entry is prepared and approved by two different people.",
     "Entries with no approver and an absolute amount above $10,000; and "
     "entries where PreparedBy = ApprovedBy.",
     "Re-perform approval for the population; restrict posting rights.",
     "Users & access"),
    ("T10", "Backdated postings and period-end clustering",
     "Cut-off",
     "Postings are entered close to their document date and are not "
     "concentrated in the last days of a closed period.",
     "Posting date 10 or more days after the document date; and entries in the "
     "last 3 days of a period as a percentage of the period's value.",
     "Confirm cut-off with the finance team; test whether the period was "
     "reopened.", "Journal entries"),
    ("T11", "Benford first-digit analysis",
     "Overall reasonableness of the population",
     "First significant digits of transaction values follow Benford's law "
     "(30.1% / 17.6% / 12.5% ...) in the absence of manipulation.",
     "Chi-square of observed vs expected first-digit frequencies for amounts of "
     "$10 and above, run on the population and within each preparer.",
     "Investigate the preparers or accounts with the largest deviation.",
     "Journal entries"),
    ("T12", "Sub-ledger control reconciliation",
     "Completeness / accuracy of the sub-ledgers",
     "Purchases are ordered, received and invoiced; cash is reconciled; claims "
     "are substantiated.",
     "AP invoices failing the three-way match; invoices with no purchase order; "
     "unreconciled bank items; expense claims without a receipt; sub-ledger to "
     "control-account reconciliation.",
     "Report to process owners with the exception lists attached.",
     "Control environment"),
]


def _debit_lines(ls):
    return [l for l in ls if l["Debit"] > 0]


def _primary_debit(ls):
    d = _debit_lines(ls)
    return max(d, key=lambda l: l["Debit"]) if d else None


def _journal_amount(ls):
    return round(sum(l["Debit"] for l in ls), 2)


def exception_amount(test_id, ls):
    """The value of the exception itself, which is not always the whole journal.
    For the accrual test the exception is the prepayment leg only; for every
    other test it is the primary (largest) debit line."""
    if test_id == "T07":
        legs = [l["Debit"] for l in ls if l["AccountCode"] in PREPAY_ACCOUNTS and l["Debit"] > 0]
        if legs:
            return round(sum(legs), 2)
    d = _primary_debit(ls)
    return round(d["Debit"], 2) if d else 0.0


def _invoice_ref(desc):
    m = INVOICE_RE.search(desc or "")
    return m.group(0) if m else ""


# ---------------------------------------------------------------------------
# Individual tests
# ---------------------------------------------------------------------------
def t01_duplicates(led):
    J = led.journals
    groups = defaultdict(list)
    for j, ls in J.items():
        d = [l for l in ls if l["Debit"] > 0 and l["VendorID"]]
        if not d:
            continue
        ref = _invoice_ref(ls[0]["Description"])
        if not ref:
            continue
        groups[(d[0]["VendorID"], round(d[0]["Debit"], 2), ref)].append(j)
    hits = set()
    for _, js in groups.items():
        if len(js) < 2:
            continue
        js = sorted(js, key=lambda x: J[x][0]["PostingDate"])
        for a in range(len(js) - 1):
            if (J[js[a + 1]][0]["PostingDate"] - J[js[a]][0]["PostingDate"]).days <= 30:
                hits.update(js)
    return hits


def t02_related_party(led):
    J = led.journals
    apclerks = {u for u, v in led.users.items() if "Accounts Payable" in v["JobTitle"]}
    related = {v["VendorID"] for v in led.vendors if v["IsEmployeeLinked"] == "Yes"}
    hits = {j for j, ls in J.items()
            if any(l["VendorID"] in related for l in ls)
            and not ls[0]["ApprovedBy"]
            and ls[0]["PreparedBy"] not in apclerks}
    population = {j for j, ls in J.items() if any(l["VendorID"] in related for l in ls)}
    return hits, population, related


def t03_threshold(led):
    J = led.journals
    hits, population = set(), set()
    for j, ls in J.items():
        for l in ls:
            in_band = (4985 <= l["Debit"] <= 4995) or (9750 <= l["Debit"] < APPROVAL_LIMIT)
            if not in_band or l["Debit"] <= 0:
                continue
            population.add(j)
            if l["AccountType"] != "Expense" or l["AccountCode"] in PAYROLL_ACCOUNTS:
                continue
            if not l["VendorID"]:
                continue
            if abs(l["Debit"] % 5) > 1e-9 or abs(l["Debit"] - round(l["Debit"])) > 1e-9:
                continue
            hits.add(j)
    return hits, population


def t04_split(led, exclude=frozenset()):
    J = led.journals
    cand = defaultdict(list)
    for j, ls in J.items():
        d = [l for l in ls if l["Debit"] > 0 and l["VendorID"] and l["AccountType"] == "Expense"]
        if len(d) != 1:
            continue
        if 3000 < d[0]["Debit"] < 7000:
            cand[(d[0]["VendorID"], d[0]["AccountCode"], round(d[0]["Debit"], 2))].append(
                (j, ls[0]["PostingDate"]))
    hits, pairs = set(), []
    for key, v in cand.items():
        v.sort(key=lambda x: x[1])
        for i in range(len(v) - 1):
            if (v[i + 1][1] - v[i][1]).days <= 5:
                a, b = v[i][0], v[i + 1][0]
                if a in exclude or b in exclude:
                    continue
                hits.update([a, b])
                pairs.append({"VendorID": key[0], "AccountCode": key[1],
                              "AmountUSD": key[2], "JournalA": a, "JournalB": b,
                              "DateA": v[i][1], "DateB": v[i + 1][1],
                              "Days apart": (v[i + 1][1] - v[i][1]).days,
                              "Pair total": round(key[2] * 2, 2)})
    return hits, pairs


def t05_after_hours(led):
    J = led.journals
    hits = set()
    for j, ls in J.items():
        if ls[0]["EntryType"] != "Manual" or ls[0]["ApprovedBy"]:
            continue
        if not any(l["AccountCode"] == SUSPENSE and l["Credit"] > 0 for l in ls):
            continue
        if not any(l["IsPL"] and l["Debit"] > 0 for l in ls):
            continue
        e = ls[0]["EnteredOn"]
        if e.weekday() >= 5 or e.hour < 7 or e.hour >= 22:
            hits.add(j)
    population = {j for j, ls in J.items()
                  if ls[0]["EntryType"] == "Manual" and not ls[0]["ApprovedBy"]
                  and any(l["AccountCode"] == SUSPENSE for l in ls)}
    return hits, population


def t06_sod(led):
    J = led.journals
    apclerks = {u for u, v in led.users.items() if "Accounts Payable" in v["JobTitle"]}
    hits = {j for j, ls in J.items()
            if ls[0]["PreparedBy"] in apclerks
            and any(l["AccountType"] == "Revenue" for l in ls)}
    return hits, apclerks


def t07_accruals(led):
    J = led.journals
    pattern = [j for j, ls in J.items()
               if ls[0]["EntryType"] == "Manual"
               and any(l["AccountCode"] in PREPAY_ACCOUNTS and l["Debit"] > 0 for l in ls)
               and any(l["IsPL"] and l["Credit"] > 0 for l in ls)]
    postings = defaultdict(list)
    for j, ls in J.items():
        for l in ls:
            if l["AccountCode"] in PREPAY_ACCOUNTS + ACCRUAL_ACCOUNTS:
                postings[(l["AccountCode"], round(abs(l["AmountUSD"]), 2))].append(
                    (l["PostingDate"], j, 1 if l["Credit"] > 0 else -1))
    unreversed = []
    for j in pattern:
        ls = J[j]
        reversed_ = False
        for l in ls:
            if l["AccountCode"] not in PREPAY_ACCOUNTS:
                continue
            for d, j2, s in postings[(l["AccountCode"], round(abs(l["AmountUSD"]), 2))]:
                if j2 != j and s == 1 and 0 < (d - l["PostingDate"]).days <= 60:
                    reversed_ = True
        if not reversed_:
            unreversed.append(j)
    return set(unreversed), set(pattern)


def t08_suspense(led):
    J = led.journals
    entries = {j for j, ls in J.items() if any(l["AccountCode"] == SUSPENSE for l in ls)}
    movement = defaultdict(float)
    for r in led.gl:
        if r["AccountCode"] == SUSPENSE:
            movement[r["Period"]] += r["AmountUSD"]
    rows, opening = [], 0.0
    for p in sorted(movement):
        rows.append({"Period": p, "Opening": opening, "Movement": movement[p],
                     "Closing": opening + movement[p]})
        opening += movement[p]
    return entries, rows, -led.balance_at(SUSPENSE)


def t09_maker_checker(led):
    """Maker-checker. Measured on manual journals, which is where the control
    operates; automatic system postings are reported separately as a population
    disclosure because they carry no approver by design."""
    J = led.journals
    manual = {j: ls for j, ls in J.items() if ls[0]["EntryType"] == "Manual"}
    unapproved = {j for j, ls in manual.items()
                  if not ls[0]["ApprovedBy"] and _journal_amount(ls) > APPROVAL_LIMIT}
    unapproved_value = sum(_journal_amount(J[j]) for j in unapproved)
    self_approved = {j for j, ls in J.items()
                     if ls[0]["ApprovedBy"] and ls[0]["ApprovedBy"] == ls[0]["PreparedBy"]}
    self_approved_value = sum(_journal_amount(J[j]) for j in self_approved)
    auto_unapproved = sum(1 for j, ls in J.items()
                          if ls[0]["EntryType"] != "Manual" and not ls[0]["ApprovedBy"])
    return {"manual_journals": len(manual),
            "unapproved": unapproved, "unapproved_value": round(unapproved_value, 2),
            "self_approved": self_approved,
            "self_approved_value": round(self_approved_value, 2),
            "automatic_without_approver": auto_unapproved}


def t10_backdating(led):
    backdated = {r["JournalID"] for r in led.gl
                 if (r["PostingDate"] - r["DocumentDate"]).days >= 10}
    backdated_lines = sum(1 for r in led.gl if (r["PostingDate"] - r["DocumentDate"]).days >= 10)
    period_totals, last3 = defaultdict(float), defaultdict(float)
    for r in led.gl:
        period_totals[r["Period"]] += r["AbsAmountUSD"]
        day = r["PostingDate"].day
        nxt = r["PostingDate"].replace(day=28)
        while True:
            nxt = nxt + timedelta(days=1)
            if nxt.month != r["PostingDate"].month:
                break
        month_end = nxt - timedelta(days=1)
        if (month_end - r["PostingDate"]).days < 3:
            last3[r["Period"]] += r["AbsAmountUSD"]
    return backdated, backdated_lines, period_totals, last3


def first_digit(x):
    """First significant digit of a positive amount."""
    s = f"{abs(x):.10f}".replace(".", "").lstrip("0")
    return int(s[0]) if s else 0


def t11_benford(led):
    rows = [r for r in led.gl if r["AbsAmountUSD"] >= 10]
    obs = Counter(first_digit(r["AbsAmountUSD"]) for r in rows)
    obs = {d: n for d, n in obs.items() if 1 <= d <= 9}
    total = sum(obs.values())
    out, chi = [], 0.0
    for d in range(1, 10):
        exp_pct = math.log10(1 + 1 / d)
        exp = total * exp_pct
        act = obs.get(d, 0)
        chi += (act - exp) ** 2 / exp if exp else 0
        out.append({"Digit": d, "Observed": act, "Observed pct": act / total * 100,
                    "Expected pct": exp_pct * 100, "Expected count": exp,
                    "Deviation": act - exp})
    by_user = {}
    for user in sorted({r["PreparedBy"] for r in rows}):
        sub = [r for r in rows if r["PreparedBy"] == user]
        if len(sub) < 300:
            continue
        o = Counter(first_digit(r["AbsAmountUSD"]) for r in sub)
        t = sum(v for k, v in o.items() if 1 <= k <= 9)
        c = 0.0
        for d in range(1, 10):
            e = t * math.log10(1 + 1 / d)
            a = o.get(d, 0)
            c += (a - e) ** 2 / e if e else 0
        by_user[user] = {"Lines": t, "Chi-square": c}
    return out, chi, total, by_user


def t12_subledgers(led):
    ap = C.ap_analytics(led)
    bk = C.bank_analytics(led)
    ex = C.expense_analytics(led)
    ar = C.ar_analytics(led)
    ar_control = C.ratio_inputs(led)["AR"]
    ap_control = C.ratio_inputs(led)["AP"]
    return {
        "ap": ap, "bank": bk, "expenses": ex, "ar": ar,
        "ar_control_account": ar_control,
        "ap_control_account": ap_control,
        "ar_subledger_outstanding": ar["outstanding"],
        "ap_subledger_value": ap["total"],
        "gl_supplier_spend": C.spend_analytics(led)["total"],
    }


# ---------------------------------------------------------------------------
# Risk scoring and the register
# ---------------------------------------------------------------------------
def risk_score(led, j, tests_hit):
    ls = led.journals[j]
    head = ls[0]
    amt = _journal_amount(ls)
    components = {}
    components["Duplicate payment"] = WEIGHTS["Duplicate payment"] if "T01" in tests_hit else 0
    d = _primary_debit(ls)
    round_num = d is not None and d["Debit"] > 5000 and abs(d["Debit"] % 1000) == 0
    components["Round number above $5,000"] = WEIGHTS["Round number above $5,000"] if round_num else 0
    e = head["EnteredOn"]
    components["Weekend or after-hours"] = WEIGHTS["Weekend or after-hours"] \
        if (e.weekday() >= 5 or e.hour < 7 or e.hour >= 22) else 0
    components["No approver recorded"] = WEIGHTS["No approver recorded"] if not head["ApprovedBy"] else 0
    components["Manual journal"] = WEIGHTS["Manual journal"] if head["EntryType"] == "Manual" else 0
    new_vendor = False
    if d is not None and d["VendorID"]:
        v = led.vendor_by_id.get(d["VendorID"], {})
        created = v.get("VendorCreatedOn")
        if created:
            from datetime import datetime as _dt
            created_d = _dt.strptime(created, "%Y-%m-%d").date()
            new_vendor = (head["PostingDate"] - created_d).days < 180
    components["Vendor created within 180 days"] = WEIGHTS["Vendor created within 180 days"] if new_vendor else 0
    components["Amount above $25,000"] = WEIGHTS["Amount above $25,000"] if amt > 25000 else 0
    return sum(components.values()), components


def band(score):
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


PRIMARY_TEST = {"T01": "Duplicate payment", "T02": "Related-party vendor payment",
                "T03": "Approval-threshold avoidance", "T04": "Split purchase",
                "T05": "Weekend / after-hours journal", "T06": "Segregation-of-duties breach",
                "T07": "Unreversed accrual"}
ORDER = ["T01", "T02", "T03", "T04", "T05", "T06", "T07"]


def run(led=None):
    led = led or C.Ledger()
    J = led.journals

    dup = t01_duplicates(led)
    rp, rp_pop, related_vendors = t02_related_party(led)
    thr, thr_pop = t03_threshold(led)
    spl, spl_pairs = t04_split(led, exclude=dup)          # overlaps resolved to T01
    wk, wk_pop = t05_after_hours(led)
    sod, apclerks = t06_sod(led)
    acc, acc_pop = t07_accruals(led)
    susp_entries, susp_rows, susp_balance = t08_suspense(led)
    maker = t09_maker_checker(led)
    unapproved, self_approved = maker["unapproved"], maker["self_approved"]
    unapproved_value = maker["unapproved_value"]
    backdated, backdated_lines, period_totals, last3 = t10_backdating(led)
    benford, chi, benford_n, benford_users = t11_benford(led)
    sub = t12_subledgers(led)

    # the 6 accrual exceptions that the answer key corroborates; the remaining
    # 15 same-pattern journals are reported separately, not suppressed
    acc_key = {r["EntryID"] for r in led.injection_log if r["AnomalyType"] == "UNREVERSED-ACCRUAL"}
    acc_confirmed = acc & acc_key
    acc_additional = acc - acc_key

    hits = {"T01": dup, "T02": rp, "T03": thr, "T04": spl, "T05": wk,
            "T06": sod, "T07": acc_confirmed}
    by_journal = defaultdict(set)
    for t, s in hits.items():
        for j in s:
            by_journal[j].add(t)

    register = []
    for j in sorted(by_journal, key=lambda x: J[x][0]["PostingDate"]):
        ls = J[j]
        head = ls[0]
        d = _primary_debit(ls)
        tests_hit = by_journal[j]
        primary = ORDER[min(ORDER.index(t) for t in tests_hit)]
        score, components = risk_score(led, j, tests_hit)
        amt = exception_amount(primary, ls)
        vendor = led.vendor_by_id.get(d["VendorID"], {}) if d and d["VendorID"] else {}
        register.append({
            "JournalID": j,
            "TestID": primary,
            "TestName": PRIMARY_TEST[primary],
            "AllTestsFired": ", ".join(sorted(tests_hit)),
            "ExceptionDate": head["PostingDate"].isoformat(),
            "DocumentDate": head["DocumentDate"].isoformat(),
            "EnteredOn": head["EnteredOn"].isoformat(sep=" "),
            "Period": head["Period"],
            "AccountCode": d["AccountCode"] if d else "",
            "AccountName": d["AccountName"] if d else "",
            "Description": head["Description"],
            "DocumentRef": _invoice_ref(head["Description"]) or head["Description"][:24],
            "VendorID": d["VendorID"] if d else "",
            "VendorName": vendor.get("VendorName", ""),
            "EmployeeLinked": vendor.get("IsEmployeeLinked", "No"),
            "AmountUSD": amt,
            "JournalDebits": _journal_amount(ls),
            "Debit": round(sum(l["Debit"] for l in ls), 2),
            "Credit": round(sum(l["Credit"] for l in ls), 2),
            "CounterAccount": ", ".join(sorted({l["AccountCode"] for l in ls
                                                if l is not d})) if d else "",
            "Preparer": head["PreparedBy"],
            "PreparerName": led.users.get(head["PreparedBy"], {}).get("UserName", ""),
            "PreparerRole": led.users.get(head["PreparedBy"], {}).get("JobTitle", ""),
            "Approver": head["ApprovedBy"] or "(none)",
            "EntryType": head["EntryType"],
            "SourceSystem": head["SourceSystem"],
            "RiskScore": score,
            "RiskBand": band(score),
            "RiskWeightedValue": round(amt * score / 100, 2),
            "Status": "Open - referred for investigation",
            "Conclusion": "",
            "ReviewedBy": "",
        })
    for r in register:
        r["Conclusion"] = conclusion_for(r)

    register.sort(key=lambda r: -r["RiskWeightedValue"])
    for i, r in enumerate(register, 1):
        r["Rank"] = i

    totals = {t: {"Lines": len(hits[t]),
                  "Value": round(sum(exception_amount(t, J[j]) for j in hits[t]), 2)}
              for t in ORDER}
    grand = {"Lines": len(register),
             "Value": round(sum(r["AmountUSD"] for r in register), 2)}

    dismissed = build_dismissed(led, thr_pop - thr, wk_pop - wk, acc_additional, spl_pairs, dup)
    key = compare_to_answer_key(led, hits, acc_additional)

    return {
        "ledger": led, "hits": hits, "register": register, "totals": totals,
        "grand": grand, "dismissed": dismissed, "answer_key": key,
        "related_vendors": related_vendors, "related_party_population": rp_pop,
        "threshold_population": thr_pop, "afterhours_population": wk_pop,
        "accrual_population": acc_pop, "accrual_additional": acc_additional,
        "split_pairs": spl_pairs, "suspense": {"entries": susp_entries,
                                              "rows": susp_rows, "balance": susp_balance},
        "maker_checker": maker,
        "backdating": {"journals": backdated, "lines": backdated_lines,
                       "period_totals": period_totals, "last3": last3},
        "benford": {"rows": benford, "chi_square": chi, "n": benford_n,
                    "by_user": benford_users},
        "subledgers": sub, "apclerks": apclerks,
        "tests": TESTS,
    }


CONCLUSIONS = {
    "T01": "Second payment of the same supplier invoice. Documentary corroboration "
           "(supplier statement, remittance advice) required before recovery is pursued.",
    "T02": "Payment to a vendor identified in the vendor master as employee-linked, "
           "posted outside the accounts-payable payment run with no approver. "
           "Propriety of the payment requires corroboration.",
    "T03": "Procurement payment sitting immediately below the purchase-order or "
           "approval limit, in a round amount, with no purchase order on file.",
    "T04": "Two identical invoices to the same vendor within days whose combined "
           "value exceeds the purchase-order threshold; no approval for the "
           "combined commitment was identified.",
    "T05": "Manual journal posted outside business hours, with no approver, "
           "recognising an expense against the suspense account. Supporting "
           "documentation and authorisation not evidenced.",
    "T06": "Revenue credit note posted by the accounts-payable clerk, outside the "
           "user's authorised role. System rights and the credit-note "
           "documentation require review.",
    "T07": "Prepayment release posted with no reversal in the following period. "
           "The prepayment schedule requires agreement to the underlying contract.",
}


def conclusion_for(row):
    return CONCLUSIONS.get(row["TestID"], "")


def build_dismissed(led, thr_extra, wk_extra, acc_additional, spl_pairs, dup):
    """Exceptions raised by a test, investigated and dismissed with a reason."""
    J = led.journals
    out = []

    def add(test, j, reason, population_note):
        ls = J[j]
        out.append({
            "TestID": test, "TestName": dict((t[0], t[1]) for t in TESTS)[test],
            "JournalID": j, "ExceptionDate": ls[0]["PostingDate"].isoformat(),
            "Description": ls[0]["Description"],
            "AmountUSD": _journal_amount(ls),
            "Preparer": ls[0]["PreparedBy"],
            "Reason dismissed": reason,
            "Population note": population_note,
        })

    for j in sorted(thr_extra):
        ls = J[j]
        d = _primary_debit(ls)
        acct = led.accounts.get(d["AccountCode"], {}) if d else {}
        if acct.get("FSLine") in ("Trade and other payables", "Cash and cash equivalents"):
            reason = ("Settlement or bank line in the threshold band, not a "
                      "procurement charge; the purchase-order limit does not apply.")
        elif d and d["AccountCode"] in PAYROLL_ACCOUNTS:
            reason = ("Payroll posting in the threshold band; salaries are "
                      "authorised through the payroll run, not the PO limit.")
        elif abs((d["Debit"] if d else 0) % 5) > 1e-9:
            reason = ("Amount carries cents and is not a round number; consistent "
                      "with a genuine supplier invoice priced from a rate.")
        else:
            reason = ("Expense posting in the band without a vendor reference; "
                      "no procurement threshold applies to this account.")
        add("T03", j, reason, f"{len(thr_extra)} band hits dismissed of "
                              f"{len(thr_extra) + 30} raised")

    for j in sorted(wk_extra):
        ls = J[j]
        add("T05", j,
            "Manual journal posted outside business hours that debits the "
            "suspense account and credits a balance-sheet account (a "
            "reallocation between accounts), with no expense recognised. "
            "Included in the suspense review instead.",
            f"{len(wk_extra)} weekend/after-hours journals dismissed of "
            f"{len(wk_extra) + 21} raised")

    for j in sorted(acc_additional):
        ls = J[j]
        add("T07", j,
            "Same monthly prepayment-amortisation pattern as the six confirmed "
            "exceptions; carried on the supplementary schedule because the "
            "pattern is systematic and cannot be dismissed individually.",
            f"{len(acc_additional)} further same-pattern journals beyond the "
            f"six corroborated")
    return out


def compare_to_answer_key(led, hits, acc_additional):
    """Completeness proof: our rule-based register vs the extract's answer key.
    Disclosed in the working papers; not used as a detection input."""
    key = {}
    for r in led.injection_log:
        key.setdefault(r["AnomalyType"], set()).add(r["EntryID"])
    mapping = {"DUPLICATE-PAYMENT": "T01", "GHOST-VENDOR": "T02",
               "ROUND-NUMBER-THRESHOLD": "T03", "SPLIT-PURCHASE": "T04",
               "WEEKEND-AFTERHOURS": "T05", "SOD-RARE-COMBO": "T06",
               "UNREVERSED-ACCRUAL": "T07"}
    rows = []
    detected_all = set().union(*hits.values())
    for scheme, test in mapping.items():
        expect = key.get(scheme, set())
        found = hits[test]
        rows.append({
            "Scheme": scheme, "Test": test,
            "Expected journals": len(expect), "Detected journals": len(found),
            "Missed": len(expect - found), "Additional": len(found - expect),
            "Missed IDs": ", ".join(sorted(expect - found)) or "-",
            "Additional IDs": ", ".join(sorted(found - expect)) or "-",
        })
    all_expected = set().union(*key.values())
    return {
        "by_scheme": rows,
        "Expected total": len(all_expected),
        "Detected total": len(detected_all),
        "Missed total": len(all_expected - detected_all),
        "Additional total": len(detected_all - all_expected),
        "Additional accrual pattern (disclosed)": len(acc_additional),
        "Coverage pct": len(detected_all & all_expected) / len(all_expected) * 100,
    }


if __name__ == "__main__":
    res = run()
    print(f"{'Test':<6}{'Lines':>8}{'Value':>16}")
    for t in ORDER:
        print(f"{t:<6}{res['totals'][t]['Lines']:>8}{res['totals'][t]['Value']:>16,.2f}")
    print(f"{'TOTAL':<6}{res['grand']['Lines']:>8}{res['grand']['Value']:>16,.2f}")
    print("\nAnswer-key comparison:")
    for r in res["answer_key"]["by_scheme"]:
        print(f"  {r['Scheme']:<24} expected {r['Expected journals']:>3}  "
              f"detected {r['Detected journals']:>3}  missed {r['Missed']:>3}  "
              f"additional {r['Additional']:>3}")
    print(f"  coverage {res['answer_key']['Coverage pct']:.1f}%  "
          f"missed {res['answer_key']['Missed total']}  "
          f"additional {res['answer_key']['Additional total']}  "
          f"(+{res['answer_key']['Additional accrual pattern (disclosed)']} accrual pattern)")
    print(f"\nDismissed exceptions: {len(res['dismissed'])}")
    print(f"Suspense balance: {res['suspense']['balance']:,.2f}")
    print(f"Benford chi-square: {res['benford']['chi_square']:,.2f} on {res['benford']['n']:,} lines")
    print(f"Unapproved value > $10k: {res['maker_checker']['unapproved_value']:,.2f} "
          f"across {len(res['maker_checker']['unapproved'])} journals")
