#!/usr/bin/env python3
"""
Maxhub Pvt Ltd - Power BI Course Practice Data Generator
========================================================
Creates a realistic, IFRS-flavoured accounting data warehouse for the fictional
client "Mhondoro Manufacturing (Pvt) Ltd" (FY2024 full year + FY2025 to September).

Deliberate fraud / anomaly patterns are injected so that the forensic accounting
modules and Capstone 1 can be solved. The ground truth is written to
data/raw/InjectionLog.csv so learners can mark their own work -- hide that file
until the end of Module 10.

Dependencies: Python 3.8+ standard library ONLY (no pandas needed).
Usage:        python3 scripts/generate_data.py
Output:       data/raw/*.csv
"""

import csv
import os
import random
from datetime import datetime, timedelta, date

SEED = 20251007
random.seed(SEED)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "raw")
os.makedirs(OUT, exist_ok=True)

CLIENT = "Mhondoro Manufacturing (Pvt) Ltd"
FUNCTIONAL_CCY = "USD"
FY_START = date(2024, 1, 1)
FY_END = date(2025, 9, 30)
APPROVAL_THRESHOLD = 10000.00   # payments above this need CFO sign-off
PO_THRESHOLD = 5000.00          # purchases above this need a purchase order

PERIODS = []
d = date(2024, 1, 1)
while d <= FY_END:
    PERIODS.append(d)
    # step one month
    d = date(d.year + (d.month // 12), (d.month % 12) + 1, 1)

MONTH_END = {
    date(2024, 1, 1): date(2024, 1, 31), date(2024, 2, 1): date(2024, 2, 29),
    date(2024, 3, 1): date(2024, 3, 31), date(2024, 4, 1): date(2024, 4, 30),
    date(2024, 5, 1): date(2024, 5, 31), date(2024, 6, 1): date(2024, 6, 30),
    date(2024, 7, 1): date(2024, 7, 31), date(2024, 8, 1): date(2024, 8, 31),
    date(2024, 9, 1): date(2024, 9, 30), date(2024, 10, 1): date(2024, 10, 31),
    date(2024, 11, 1): date(2024, 11, 30), date(2024, 12, 1): date(2024, 12, 31),
    date(2025, 1, 1): date(2025, 1, 31), date(2025, 2, 1): date(2025, 2, 28),
    date(2025, 3, 1): date(2025, 3, 31), date(2025, 4, 1): date(2025, 4, 30),
    date(2025, 5, 1): date(2025, 5, 31), date(2025, 6, 1): date(2025, 6, 30),
    date(2025, 7, 1): date(2025, 7, 31), date(2025, 8, 1): date(2025, 8, 31),
    date(2025, 9, 1): date(2025, 9, 30),
}


def write_csv(name, rows, header=None):
    path = os.path.join(OUT, name)
    if header is None:
        header = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"  {name:<34} {len(rows):>7,} rows")


def money(x):
    return round(float(x), 2)


# ----------------------------------------------------------------------------
# 1. CHART OF ACCOUNTS
# ----------------------------------------------------------------------------
COA_ROWS = [
    # code, name, type, normal balance, FS line, statement, cash flag, is_control, is_suspense
    ("1000", "Cash on Hand", "Asset", "Debit", "Cash and cash equivalents", "BS", True, False, False),
    ("1010", "Bank - CBZ USD Current", "Asset", "Debit", "Cash and cash equivalents", "BS", True, False, False),
    ("1015", "Bank - Stanbic ZAR", "Asset", "Debit", "Cash and cash equivalents", "BS", True, False, False),
    ("1020", "Petty Cash - Plant", "Asset", "Debit", "Cash and cash equivalents", "BS", True, False, False),
    ("1100", "Trade Receivables", "Asset", "Debit", "Trade and other receivables", "BS", False, True, False),
    ("1110", "Allowance for Expected Credit Losses", "Asset", "Credit", "Trade and other receivables", "BS", False, False, False),
    ("1120", "Other Receivables", "Asset", "Debit", "Trade and other receivables", "BS", False, True, False),
    ("1130", "Employee Advances", "Asset", "Debit", "Trade and other receivables", "BS", False, False, False),
    ("1200", "Inventory - Raw Materials", "Asset", "Debit", "Inventories", "BS", False, False, False),
    ("1210", "Inventory - Work in Progress", "Asset", "Debit", "Inventories", "BS", False, False, False),
    ("1220", "Inventory - Finished Goods", "Asset", "Debit", "Inventories", "BS", False, False, False),
    ("1230", "Inventory - Provision for Obsolescence", "Asset", "Credit", "Inventories", "BS", False, False, False),
    ("1300", "Prepayments", "Asset", "Debit", "Trade and other receivables", "BS", False, False, False),
    ("1310", "VAT Receivable", "Asset", "Debit", "Trade and other receivables", "BS", False, False, False),
    ("1400", "Plant and Machinery - Cost", "Asset", "Debit", "Property, plant and equipment", "BS", False, False, False),
    ("1410", "Motor Vehicles - Cost", "Asset", "Debit", "Property, plant and equipment", "BS", False, False, False),
    ("1420", "Office Equipment - Cost", "Asset", "Debit", "Property, plant and equipment", "BS", False, False, False),
    ("1430", "Right-of-Use Asset", "Asset", "Debit", "Property, plant and equipment", "BS", False, False, False),
    ("1440", "Accumulated Depreciation - P&M", "Asset", "Credit", "Property, plant and equipment", "BS", False, False, False),
    ("1450", "Accumulated Depreciation - MV", "Asset", "Credit", "Property, plant and equipment", "BS", False, False, False),
    ("1460", "Accumulated Depreciation - OE", "Asset", "Credit", "Property, plant and equipment", "BS", False, False, False),
    ("1500", "Investment Property", "Asset", "Debit", "Investment property", "BS", False, False, False),
    ("1600", "Deferred Tax Asset", "Asset", "Debit", "Deferred tax", "BS", False, False, False),
    ("1990", "Suspense Account", "Asset", "Debit", "Suspense - to be cleared", "BS", False, False, True),
    ("2000", "Trade Payables", "Liability", "Credit", "Trade and other payables", "BS", False, True, False),
    ("2010", "Accruals", "Liability", "Credit", "Trade and other payables", "BS", False, False, False),
    ("2020", "Other Payables", "Liability", "Credit", "Trade and other payables", "BS", False, False, False),
    ("2100", "VAT Payable", "Liability", "Credit", "Trade and other payables", "BS", False, False, False),
    ("2110", "PAYE / Withholding Tax Payable", "Liability", "Credit", "Trade and other payables", "BS", False, False, False),
    ("2120", "Pension Contributions Payable", "Liability", "Credit", "Trade and other payables", "BS", False, False, False),
    ("2130", "Income Tax Payable", "Liability", "Credit", "Taxation", "BS", False, False, False),
    ("2200", "Bank Overdraft", "Liability", "Credit", "Borrowings", "BS", False, False, False),
    ("2300", "Lease Liability (IFRS 16)", "Liability", "Credit", "Borrowings", "BS", False, False, False),
    ("2400", "Deferred Tax Liability", "Liability", "Credit", "Deferred tax", "BS", False, False, False),
    ("2500", "Provisions - Legal Claims", "Liability", "Credit", "Provisions", "BS", False, False, False),
    ("3000", "Share Capital", "Equity", "Credit", "Share capital", "BS", False, False, False),
    ("3100", "Retained Earnings", "Equity", "Credit", "Retained earnings", "BS", False, False, False),
    ("3200", "Dividends Declared", "Equity", "Debit", "Retained earnings", "BS", False, False, False),
    ("3300", "Revaluation Reserve", "Equity", "Credit", "Other reserves", "BS", False, False, False),
    ("4000", "Revenue - Manufactured Goods", "Revenue", "Credit", "Revenue", "PL", False, False, False),
    ("4010", "Revenue - Trading / Resale", "Revenue", "Credit", "Revenue", "PL", False, False, False),
    ("4020", "Revenue - Service and Maintenance", "Revenue", "Credit", "Revenue", "PL", False, False, False),
    ("4090", "Sales Returns and Discounts", "Revenue", "Debit", "Revenue", "PL", False, False, False),
    ("5000", "Cost of Sales - Materials", "Expense", "Debit", "Cost of sales", "PL", False, False, False),
    ("5010", "Cost of Sales - Direct Labour", "Expense", "Debit", "Cost of sales", "PL", False, False, False),
    ("5020", "Cost of Sales - Manufacturing Overhead", "Expense", "Debit", "Cost of sales", "PL", False, False, False),
    ("5030", "Inventory Write-down", "Expense", "Debit", "Cost of sales", "PL", False, False, False),
    ("6000", "Salaries and Wages", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6010", "Employee Pension Contributions", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6020", "Staff Welfare and Training", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6030", "Depreciation", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6040", "Repairs and Maintenance", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6050", "Fuel and Motor Vehicle Costs", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6060", "Electricity and Water", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6070", "Rent and Rates", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6080", "Insurance", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6090", "Professional and Consulting Fees", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6100", "Travel and Accommodation", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6110", "Marketing and Advertising", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6120", "Telecommunications and Internet", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6130", "Security Services", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6140", "Consumables and Packaging", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6150", "Bank Charges", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6160", "Expected Credit Loss Impairment", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6170", "Fines and Penalties", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6180", "Donations", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6190", "Sundry Expenses", "Expense", "Debit", "Operating expenses", "PL", False, False, False),
    ("6200", "Consulting Income - Advisory", "Revenue", "Credit", "Revenue", "PL", False, False, False),
    ("7000", "Interest Expense - Borrowings", "Expense", "Debit", "Finance costs", "PL", False, False, False),
    ("7010", "Interest Expense - Leases", "Expense", "Debit", "Finance costs", "PL", False, False, False),
    ("8000", "Income Tax Expense", "Expense", "Debit", "Taxation", "PL", False, False, False),
]


def build_accounts():
    rows = []
    for (code, name, typ, norm, fs, stmt, cash, ctrl, susp) in COA_ROWS:
        rows.append({
            "AccountCode": code, "AccountName": name, "AccountType": typ,
            "NormalBalance": norm, "FSLine": fs, "Statement": stmt,
            "IsCashAccount": "Yes" if cash else "No",
            "IsControlAccount": "Yes" if ctrl else "No",
            "IsSuspense": "Yes" if susp else "No",
            "IsPL": "Yes" if stmt == "PL" else "No",
            "PLSign": "1" if stmt == "PL" and typ == "Revenue" else ("-1" if stmt == "PL" else "0"),
        })
    return rows


# ----------------------------------------------------------------------------
# 2. DIMENSIONS: cost centres, departments, employees/users, vendors, customers
# ----------------------------------------------------------------------------
COST_CENTRES = [
    ("CC100", "Head Office Finance", "Finance", 180000),
    ("CC110", "Head Office Admin", "Administration", 240000),
    ("CC200", "Harare Plant", "Manufacturing", 650000),
    ("CC210", "Bulawayo Plant", "Manufacturing", 420000),
    ("CC300", "Sales - Domestic", "Sales and Marketing", 380000),
    ("CC310", "Sales - Export", "Sales and Marketing", 150000),
    ("CC400", "Logistics and Distribution", "Supply Chain", 260000),
    ("CC500", "IT and Systems", "Information Technology", 195000),
    ("CC900", "Advisory Services Unit", "Professional Services", 90000),
]

USERS = [
    ("USR-001", "T. Makuvaza", "Financial Controller", "Finance", "Controller"),
    ("USR-002", "R. Chikafu", "Accounts Payable Clerk", "Finance", "Clerk"),
    ("USR-003", "M. Nyathi", "Accounts Receivable Clerk", "Finance", "Clerk"),
    ("USR-004", "K. Dube", "Payroll Officer", "Finance", "Clerk"),
    ("USR-005", "S. Moyo", "Management Accountant", "Finance", "Accountant"),
    ("USR-006", "L. Sibanda", "Chief Financial Officer", "Finance", "Approver"),
    ("USR-007", "P. Gumbo", "Procurement Officer", "Supply Chain", "Officer"),
    ("USR-008", "A. Banda", "Systems Administrator", "IT", "Admin"),
    ("USR-009", "J. Marufu", "Internal Auditor", "Governance", "Auditor"),
    ("USR-010", "N. Zhou", "Inventory Clerk", "Manufacturing", "Clerk"),
    ("USR-011", "B. Ncube", "Sales Manager", "Sales", "Manager"),
    ("USR-012", "D. Mutasa", "Shared Services Clerk", "Finance", "Clerk"),
]

FIRST = ["Ryan", "Tariro", "Moses", "Kudzai", "Simba", "Linda", "Panashe", "Alois", "Joshua",
         "Nyasha", "Bright", "Daniel", "Rudo", "Tendai", "Farai", "Chiedza", "Munyaradzi",
         "Grace", "Tatenda", "Wellington", "Blessing", "Anesu", "Ropafadzo", "Vimbai"]
LAST = ["Chikafu", "Nyathi", "Dube", "Moyo", "Sibanda", "Gumbo", "Banda", "Marufu", "Zhou",
        "Ncube", "Mutasa", "Mhlanga", "Chirwa", "Mudimu", "Zvobgo", "Mapfumo", "Kanyemba",
        "Rusike", "Chinamasa", "Mupfumi", "Gwenzi", "Mabhena"]

VENDOR_NAMES = [
    ("STEELSUP", "Steel Supplies Zimbabwe (Pvt) Ltd", "Raw materials"),
    ("POLYPLAS", "PolyPlas Holdings (Pvt) Ltd", "Raw materials"),
    ("CHEMPRO", "ChemPro Industrial Chemicals", "Raw materials"),
    ("PACKRITE", "PackRite Packaging Solutions", "Packaging"),
    ("LOGIWIN", "Logistics Windward Freight", "Logistics"),
    ("POWERCO", "PowerCo Utilities Zimbabwe", "Utilities"),
    ("TELSTAR", "TelStar Communications", "Telecoms"),
    ("SECUREG", "SecureGuard Security Services", "Security"),
    ("FUELMAX", "FuelMax Petroleum", "Fuel"),
    ("INSUREC", "InsureCorp Brokers", "Insurance"),
    ("LEGALVL", "LegalVault Attorneys", "Professional services"),
    ("AUDITAX", "Auditax Chartered Accountants", "Professional services"),
    ("TRAINCO", "TrainCo Skills Institute", "Training"),
    ("ITSUPP", "IT Support Partners (Pvt) Ltd", "IT services"),
    ("OFFICEQ", "OfficeQuip Stationers", "Office supplies"),
    ("MAINTEK", "MainTek Engineering Services", "Maintenance"),
    ("CLEANSER", "CleanServ Facilities", "Facilities"),
    ("ADVERTS", "AdvertStar Media", "Marketing"),
    ("RENTPROP", "RentPro Properties", "Rent"),
    ("SPAREPO", "SparePart Outfitters", "Spare parts"),
    ("SOFTPRO", "SoftPro Licensing Africa", "Software"),
    ("MEDICALX", "MediCareX Health Services", "Medical"),
]

CUSTOMER_NAMES = [
    ("ZIMGRAIN", "Zimbabwe Grain Millers (Pvt) Ltd", "Wholesale", "USD"),
    ("SAFRET", "Safret Traders CC", "Export - ZA", "ZAR"),
    ("UKBUILD", "UK Builder Depot Ltd", "Export - UK", "GBP"),
    ("DEUTSCHT", "Deutsch Technik GmbH", "Export - DE", "EUR"),
    ("MININGCO", "Great Dyke Mining Corporation", "Mining", "USD"),
    ("AGRIHUB", "AgriHub Cooperative", "Agriculture", "USD"),
    ("RETAILZ", "RetailZ Supermarkets", "Retail", "USD"),
    ("BUILDMART", "BuildMart Hardware", "Retail", "USD"),
    ("SADCIND", "SADC Industrial Supplies", "Export - Region", "USD"),
    ("HOSPITALS", "Sunrise Hospitals Group", "Healthcare", "USD"),
    ("UNIVTRUST", "University Trust Procurement", "Public sector", "USD"),
    ("MUNICIPALY", "Municipality of Kadoma", "Public sector", "USD"),
    ("TRANSCO", "TransContinental Haulage", "Logistics", "USD"),
    ("FARMSUP", "FarmSupply Depot", "Agriculture", "USD"),
    ("PLASTICF", "PlastiCorp Factory", "Manufacturing", "USD"),
    ("PRINTWORKS", "PrintWorks Limited", "Services", "GBP"),
    ("ENERGYAF", "EnergyAfrica Distributors", "Energy", "USD"),
    ("FOODPROC", "FoodProcessors Alliance", "Food", "USD"),
]


def build_cost_centres():
    rows = []
    for code, name, dept, budget in COST_CENTRES:
        rows.append({"CostCentreCode": code, "CostCentreName": name, "Department": dept,
                     "AnnualBudgetUSD": budget})
    return rows


def build_users():
    return [{"UserID": u[0], "UserName": u[1], "JobTitle": u[2], "Department": u[3],
             "Role": u[4], "CanPostManualJE": "Yes" if u[4] in ("Controller", "Accountant", "Clerk") else "No",
             "CanApprovePayment": "Yes" if u[4] in ("Approver", "Controller") else "No",
             "SystemAccess": "Finance ERP" if u[3] == "Finance" else "Operational module",
             "StartDate": "2021-03-01"} for u in USERS]


def build_vendors():
    rows = []
    for i, (code, name, cat) in enumerate(VENDOR_NAMES, start=1):
        rows.append({
            "VendorID": f"V{1000 + i}", "VendorCode": code, "VendorName": name,
            "Category": cat,
            "BankAccount": f"10{random.randint(100000, 999999)}{random.randint(10, 99)}",
            "BankName": random.choice(["CBZ Bank", "Stanbic Bank", "FBC Bank", "Steward Bank", "Nedbank"]),
            "TaxClearanceNo": f"TCL{random.randint(100000, 999999)}",
            "Address": f"{random.randint(1, 200)} {random.choice(['Samora Machel Ave', 'Kwame Nkrumah Ave', 'Jason Moyo St', 'Fife St', 'Boshoff Dr'])}, {random.choice(['Harare', 'Bulawayo', 'Mutare', 'Gweru'])}",
            "PaymentTerms": random.choice([30, 30, 30, 45, 60, 14]),
            "VendorCreatedOn": (date(2019, 1, 1) + timedelta(days=random.randint(0, 2000))).isoformat(),
            "LastBankChangeDate": (date(2024, 1, 1) + timedelta(days=random.randint(0, 600))).isoformat(),
            "IsEmployeeLinked": "No", "IsActive": "Yes",
        })
    # ---- FRAUD PATTERN: ghost / related-party vendors (employee-linked) ----
    ghost = [
        ("SUP-771", "R Chikafu Trading Enterprises", "Professional services", "R. Chikafu", "10 4471 8823 01"),
        ("SUP-772", "Zhou Logistics & Advisory", "Logistics", "N. Zhou", "10 5512 7741 09"),
        ("SUP-773", "Gumbo General Suppliers", "Office supplies", "P. Gumbo", "10 3390 2214 77"),
        ("SUP-774", "Meridian Consulting Group", "Professional services", "unknown director", "10 9911 0045 12"),
    ]
    for i, (code, name, cat, link, bank) in enumerate(ghost, start=1):
        created = (date(2024, 6, 1) + timedelta(days=random.randint(0, 120))).isoformat()
        rows.append({
            "VendorID": f"V{2000 + i}", "VendorCode": code, "VendorName": name, "Category": cat,
            "BankAccount": bank.replace(" ", ""), "BankName": "Steward Bank",
            "TaxClearanceNo": "", "Address": "Suite 12, Cecil House, Harare",
            "PaymentTerms": 7, "VendorCreatedOn": created,
            "LastBankChangeDate": created, "IsEmployeeLinked": "Yes",
            "IsActive": "Yes",
        })
    return rows


def build_customers():
    rows = []
    for i, (code, name, seg, ccy) in enumerate(CUSTOMER_NAMES, start=1):
        rows.append({
            "CustomerID": f"C{3000 + i}", "CustomerCode": code, "CustomerName": name,
            "Segment": seg, "Currency": ccy,
            "CreditLimitUSD": random.choice([25000, 50000, 75000, 100000, 150000, 250000]),
            "PaymentTerms": random.choice([30, 30, 45, 60, 30]),
            "Country": {"USD": random.choice(["Zimbabwe", "Zimbabwe", "South Africa"]),
                        "ZAR": "South Africa", "GBP": "United Kingdom", "EUR": "Germany"}[ccy],
            "AccountManager": random.choice(["B. Ncube", "T. Makuvaza", "S. Moyo"]),
            "CustomerSince": (date(2016, 1, 1) + timedelta(days=random.randint(0, 2600))).isoformat(),
        })
    return rows


# ----------------------------------------------------------------------------
# 3. GENERAL LEDGER JOURNAL ENTRIES (with injected anomalies)
# ----------------------------------------------------------------------------
ANOMALIES = []          # ground-truth log
GL = []
LINE_ID = [0]


def next_je(period_start, n=[0]):
    n[0] += 1
    return f"JE{period_start.year}{period_start.month:02d}-{n[0]:05d}"


def add_entry(je_id, posting_dt, account, desc, debit, credit, cc_code, user_id,
              source="ERP-GL", entry_type="Automatic", doc_date=None, entered_on=None,
              approved_by="", ccy="USD", fx=1.0, reversal=False, vendor="", customer="",
              anomaly=""):
    LINE_ID[0] += 1
    debit, credit = money(debit), money(credit)
    GL.append({
        "LineID": f"L{LINE_ID[0]:07d}",
        "JournalID": je_id,
        "LineNo": 1,
        "AccountCode": account,
        "PostingDate": posting_dt.isoformat(),
        "DocumentDate": (doc_date or posting_dt).isoformat(),
        "Period": f"{posting_dt.year}-{posting_dt.month:02d}",
        "FiscalYear": posting_dt.year,
        "Description": desc,
        "Debit": debit,
        "Credit": credit,
        "AmountUSD": money(debit - credit),  # signed: debit positive, credit negative
        "AbsAmountUSD": money(max(debit, credit) * fx),
        "Currency": ccy,
        "FXRate": fx,
        "CostCentreCode": cc_code,
        "PreparedBy": user_id,
        "ApprovedBy": approved_by,
        "SourceSystem": source,
        "EntryType": entry_type,
        "EnteredOn": (entered_on or datetime.combine(posting_dt, datetime.min.time())
                      + timedelta(hours=random.randint(8, 17), minutes=random.randint(0, 59))).isoformat(sep=" "),
        "IsReversal": "Yes" if reversal else "No",
        "VendorID": vendor,
        "CustomerID": customer,
        "AnomalyLabel": anomaly,
    })


def acct_desc(code, extra=""):
    name = dict((c[0], c[1]) for c in COA_ROWS)[code]
    return f"{name}{(' - ' + extra) if extra else ''}"


def pick_user(role_pref=None):
    if role_pref:
        cand = [u for u in USERS if u[4] == role_pref]
        if cand:
            return random.choice(cand)[0]
    return random.choice(USERS)[0]


MANUAL_ACCOUNTS = ["6190", "6020", "6100", "6090", "2010", "1300", "1120", "1990", "6180", "6170"]


def generate_gl(vendors, customers):
    vendor_ids = [v["VendorID"] for v in vendors]
    customer_ids = [c["CustomerID"] for c in customers]
    cc_list = [c[0] for c in COST_CENTRES]

    for p in PERIODS:
        m_end = MONTH_END[p]
        paye_month = 0.0
        pension_month = 0.0
        season = 1.0 + 0.12 * ((p.month % 3) - 1)          # mild seasonality
        growth = 1.0 + 0.01 * ((p.year - 2024) * 12 + p.month - 1)

        # ---------- Sales invoices ----------
        sales_total = 0.0
        output_vat = 0.0
        for i in range(random.randint(52, 68)):
            day = random.randint(1, m_end.day)
            pd = m_end.replace(day=day)
            cust = random.choice(customer_ids)
            rev_acct = random.choice(["4000", "4000", "4000", "4010", "4020"])
            base = random.choice([4200, 6800, 11500, 15400, 22000, 31500, 48000]) * season * growth
            amt = money(base * random.uniform(0.85, 1.15))        # VAT-inclusive invoice value
            sales_total += amt
            net = money(amt / 1.15)
            vat = money(amt - net)
            output_vat += vat
            cc = random.choice(["CC300", "CC310", "CC300"])
            je = next_je(p)
            add_entry(je, pd, "1100", f"Sales invoice to {cust} (VAT incl.)", amt, 0, cc, "USR-003",
                      customer=cust, doc_date=pd - timedelta(days=random.randint(0, 3)))
            add_entry(je, pd, rev_acct, f"Sales invoice to {cust} (net of VAT)", 0, net, cc, "USR-003",
                      customer=cust, doc_date=pd - timedelta(days=random.randint(0, 3)))
            add_entry(je, pd, "2100", f"Output VAT 15% on invoice to {cust}", 0, vat, cc, "USR-003",
                      customer=cust, doc_date=pd - timedelta(days=random.randint(0, 3)))

        # ---------- Cash receipts (approx. 90% of the month's billings collected) ----------
        target = sales_total * random.uniform(0.86, 0.94)
        n_rec = random.randint(52, 70)
        weights = [random.uniform(0.6, 1.4) for _ in range(n_rec)]
        wsum = sum(weights)
        for i in range(n_rec):
            day = random.randint(1, m_end.day)
            pd = m_end.replace(day=day)
            cust = random.choice(customer_ids)
            amt = money(target * weights[i] / wsum)
            je = next_je(p)
            add_entry(je, pd, "1010", f"Receipt from customer {cust}", amt, 0, "CC300", "USR-003", customer=cust)
            add_entry(je, pd, "1100", f"Receipt from customer {cust}", 0, amt, "CC300", "USR-003", customer=cust)

        # ---------- Purchase invoices ----------
        purch_total = 0.0
        input_vat = 0.0
        for i in range(random.randint(38, 50)):
            day = random.randint(1, m_end.day)
            pd = m_end.replace(day=day)
            v = random.choice(vendor_ids[:len(vendor_ids) - 4] if random.random() > 0.06 else vendor_ids)
            # A manufacturer buys raw materials with most of its spend: weight the expense account
            # accordingly so the gross margin is realistic (~40%), not 70%.
            exp = random.choices(
                ["5000", "5000", "5000", "5000", "5000", "5000", "5000",
                 "6140", "6140", "6040", "6050", "6060", "6070", "6080", "6090",
                 "6110", "6120", "6130", "6150", "6190", "6020"],
                weights=[14, 12, 10, 8, 6, 4, 3, 5, 4, 5, 4, 4, 3, 2, 3, 3, 2, 2, 2, 2, 2])[0]
            base = random.choice([1800, 3400, 5600, 8900, 14200, 19500, 27600, 38000]) * season * growth
            amt = money(base * random.uniform(0.88, 1.12))        # VAT-inclusive
            purch_total += amt
            net = money(amt / 1.15)
            vat = money(amt - net)
            input_vat += vat
            cc = random.choice(cc_list)
            je = next_je(p)
            add_entry(je, pd, exp, f"Purchase invoice from {v} (net of VAT)", net, 0, cc, "USR-002", vendor=v)
            add_entry(je, pd, "1310", f"Input VAT 15% on invoice from {v}", vat, 0, cc, "USR-002", vendor=v)
            add_entry(je, pd, "2000", f"Purchase invoice from {v} (VAT incl.)", 0, amt, cc, "USR-002", vendor=v)

        # ---------- Payment runs (approx. 93% of the month's purchases settled) ----------
        target = purch_total * random.uniform(0.88, 0.98)
        n_pay = random.randint(44, 58)
        weights = [random.uniform(0.6, 1.4) for _ in range(n_pay)]
        wsum = sum(weights)
        for i in range(n_pay):
            day = random.randint(1, m_end.day)
            pd = m_end.replace(day=day)
            v = random.choice(vendor_ids)
            amt = money(target * weights[i] / wsum)
            je = next_je(p)
            approver = "USR-006" if amt >= APPROVAL_THRESHOLD else random.choice(["", "USR-001", "USR-006"])
            add_entry(je, pd, "2000", f"Payment to vendor {v}", amt, 0, "CC100", "USR-002",
                      approved_by=approver, vendor=v)
            add_entry(je, pd, "1010", f"Payment to vendor {v}", 0, amt, "CC100", "USR-002",
                      approved_by=approver, vendor=v)

        # ---------- Payroll ----------
        for cc, cname, dept, _ in COST_CENTRES:
            gross = money({"CC100": 9800, "CC110": 12400, "CC200": 96000, "CC210": 61000,
                           "CC300": 24000, "CC310": 9800, "CC400": 18500, "CC500": 14200,
                           "CC900": 21000}[cc] * random.uniform(0.97, 1.04))
            paye = money(gross * 0.28)
            pension = money(gross * 0.06)
            net = money(gross - paye - pension)
            pd = m_end
            paye_month += paye
            pension_month += pension
            je = next_je(p)
            sal_acct = "5010" if cc in ("CC200", "CC210") else "6000"
            add_entry(je, pd, sal_acct, f"Salaries {cname}", gross, 0, cc, "USR-004")
            add_entry(je, pd, "2110", f"PAYE {cname}", 0, paye, cc, "USR-004")
            add_entry(je, pd, "2120", f"Pension {cname}", 0, pension, cc, "USR-004")
            add_entry(je, pd, "1010", f"Net pay {cname}", 0, net, cc, "USR-004")
            if random.random() < 0.35:
                ot = money(random.choice([450, 820, 1250, 2100]) * random.uniform(0.9, 1.1))
                add_entry(je, pd, sal_acct, f"Overtime {cname}", ot, 0, cc, "USR-004")
                add_entry(je, pd, "1010", f"Overtime payment {cname}", 0, ot, cc, "USR-004")

        # ---------- Current tax charge for the period ----------
        tax = money(random.uniform(18000, 34000) * (1 + 0.06 * (p.year - 2024)))
        je = next_je(p)
        add_entry(je, m_end, "8000", "Current tax charge for the period", tax, 0, "CC100", "USR-005",
                  source="Tax computation")
        add_entry(je, m_end, "2130", "Current tax charge for the period", 0, tax, "CC100", "USR-005",
                  source="Tax computation")

        # ---------- Statutory remittances and other cash outflows ----------
        je = next_je(p)
        vat_output_cleared = money(output_vat * random.uniform(0.95, 1.02))
        vat_input_cleared = money(input_vat * random.uniform(0.95, 1.02))
        vat_cash = money(vat_output_cleared - vat_input_cleared)
        add_entry(je, m_end, "2100", "VAT return - output VAT cleared", vat_output_cleared, 0, "CC100", "USR-005")
        add_entry(je, m_end, "1310", "VAT return - input VAT claimed", 0, vat_input_cleared, "CC100", "USR-005")
        if vat_cash >= 0:
            add_entry(je, m_end, "1010", "VAT paid to ZIMRA", 0, vat_cash, "CC100", "USR-005")
        else:
            add_entry(je, m_end, "1010", "VAT refund received from ZIMRA", -vat_cash, 0, "CC100", "USR-005")

        paye_pay = money(paye_month * random.uniform(0.92, 1.0))
        pen_pay = money(pension_month * random.uniform(0.90, 1.0))
        je = next_je(p)
        add_entry(je, m_end, "2110", "PAYE remitted to ZIMRA", paye_pay, 0, "CC100", "USR-004")
        add_entry(je, m_end, "2120", "Pension contributions remitted", pen_pay, 0, "CC100", "USR-004")
        add_entry(je, m_end, "1010", "Statutory remittances", 0, money(paye_pay + pen_pay), "CC100", "USR-004")
        tax_pay = money(tax * random.uniform(0.85, 1.05)) if p.month in (4, 6, 9, 12) else 0.0
        if tax_pay:
            je = next_je(p)
            add_entry(je, m_end, "2130", "Provisional tax paid to ZIMRA", tax_pay, 0, "CC100", "USR-005")
            add_entry(je, m_end, "1010", "Provisional tax paid to ZIMRA", 0, tax_pay, "CC100", "USR-005")
        je = next_je(p)
        claims_pay = money(random.uniform(28000, 52000))
        add_entry(je, m_end, "6190", "Staff expense claim reimbursements", claims_pay, 0, "CC110", "USR-012")
        add_entry(je, m_end, "1010", "Staff expense claim reimbursements", 0, claims_pay, "CC110", "USR-012")
        if p.month in (6, 12):
            je = next_je(p)
            div = money(random.choice([120000, 180000, 250000]))
            add_entry(je, m_end, "3200", "Interim dividend declared and paid", div, 0, "CC100", "USR-001", approved_by="USR-006")
            add_entry(je, m_end, "1010", "Interim dividend paid to shareholders", 0, div, "CC100", "USR-001", approved_by="USR-006")

        # ---------- Depreciation ----------
        je = next_je(p)
        dep = money(84000 / 12 * random.uniform(0.99, 1.01))
        add_entry(je, m_end, "6030", "Monthly depreciation charge", dep, 0, "CC200", "USR-005", source="Fixed Asset Ledger")
        add_entry(je, m_end, "1440", "Monthly depreciation charge", 0, dep, "CC200", "USR-005", source="Fixed Asset Ledger")

        # ---------- Accruals & prepayments ----------
        je = next_je(p)
        acc = money(random.uniform(3000, 22000))
        add_entry(je, m_end, "6190", "Accrual for unbilled services", acc, 0, "CC110", "USR-005",
                  entry_type="Manual", source="Manual-JE")
        add_entry(je, m_end, "2010", "Accrual for unbilled services", 0, acc, "CC110", "USR-005",
                  entry_type="Manual", source="Manual-JE")
        if random.random() < 0.8:   # unreversed accrual -> anomaly
            add_entry(je, m_end, "1300", "Prepaid insurance amortisation", money(2400), 0, "CC110", "USR-005",
                      entry_type="Manual", source="Manual-JE")
            add_entry(je, m_end, "6080", "Prepaid insurance amortisation", 0, money(2400), "CC110", "USR-005",
                      entry_type="Manual", source="Manual-JE")
        else:
            add_entry(je, m_end, "1300", "Prepaid insurance - not reversed", money(2400), 0, "CC110", "USR-005",
                      entry_type="Manual", source="Manual-JE", anomaly="UNREVERSED-ACCRUAL")
            add_entry(je, m_end, "6080", "Prepaid insurance - not reversed", 0, money(2400), "CC110", "USR-005",
                      entry_type="Manual", source="Manual-JE", anomaly="UNREVERSED-ACCRUAL")
            ANOMALIES.append({"EntryID": je, "AnomalyType": "UNREVERSED-ACCRUAL",
                              "AmountUSD": 2400.00, "PreparedBy": "USR-005",
                              "ExpectedDetection": "Manual accruals with no matching reversal in the following period",
                              "Description": "Prepayment amortisation posted but never reversed"})

        # ---------- Manufacturing overhead absorption (reclass of factory costs) ----------
        je = next_je(p)
        oh = money(random.uniform(46000, 62000))
        split = [0.42, 0.26, 0.18, 0.14]
        from_accts = ["6040", "6060", "6050", "6020"]
        parts = [money(oh * x) for x in split]
        parts[-1] = money(oh - sum(parts[:-1]))
        add_entry(je, m_end, "5020", "Absorption of factory overheads to cost of sales", oh, 0, "CC200",
                  "USR-005", entry_type="Manual", source="Manual-JE")
        for fa, amt in zip(from_accts, parts):
            add_entry(je, m_end, fa, "Reclassification of factory costs to cost of sales", 0, amt, "CC200",
                      "USR-005", entry_type="Manual", source="Manual-JE")

        # ---------- Inventory obsolescence & ECL (quarterly) ----------
        if p.month in (3, 6, 9, 12):
            je = next_je(p)
            wd = money(random.uniform(9000, 26000))
            add_entry(je, m_end, "5030", "Inventory write-down to net realisable value", wd, 0, "CC200",
                      "USR-005", entry_type="Manual", source="Manual-JE")
            add_entry(je, m_end, "1230", "Inventory write-down to net realisable value", 0, wd, "CC200",
                      "USR-005", entry_type="Manual", source="Manual-JE")
            ecl = money(random.uniform(7000, 18000))
            add_entry(je, m_end, "6160", "Expected credit loss charge for the quarter", ecl, 0, "CC100",
                      "USR-005", entry_type="Manual", source="Manual-JE")
            add_entry(je, m_end, "1110", "Expected credit loss charge for the quarter", 0, ecl, "CC100",
                      "USR-005", entry_type="Manual", source="Manual-JE")

        # ---------- Advisory services income ----------
        for i in range(random.randint(1, 4)):
            dte = m_end.replace(day=random.randint(5, 27))
            amt = money(random.choice([3500, 6800, 12000, 19500, 28000]) * random.uniform(0.9, 1.1))
            je = next_je(p)
            add_entry(je, dte, "1100", "Advisory services invoiced", amt, 0, "CC900", "USR-005", customer="C3006")
            add_entry(je, dte, "6200", "Advisory services invoiced", 0, amt, "CC900", "USR-005", customer="C3006")

        # ---------- Interest, tax, FX ----------
        je = next_je(p)
        interest = money(random.uniform(4200, 8900))
        add_entry(je, m_end, "7000", "Interest on borrowings", interest, 0, "CC100", "USR-005", source="Loan schedule")
        add_entry(je, m_end, "1010", "Interest on borrowings", 0, interest, "CC100", "USR-005", source="Loan schedule")

        # ---------- Manual journals (about 18 per month) ----------
        for i in range(random.randint(12, 20)):
            day = random.randint(1, m_end.day)
            pd = m_end.replace(day=day)
            acct = random.choice(MANUAL_ACCOUNTS)
            counter = random.choice(["1010", "2000", "1100", "2010", "1120", "2020"])
            amt = money(random.choice([850, 1450, 2300, 3800, 6400, 9200, 12800, 18500]) * random.uniform(0.8, 1.2))
            user = random.choice(["USR-001", "USR-005", "USR-002", "USR-012", "USR-010"])
            je = next_je(p)
            add_entry(je, pd, acct, f"Manual reallocation {random.choice(['reclass', 'correction', 'adjustment', 'journal'])}",
                      amt, 0, random.choice(cc_list), user, entry_type="Manual", source="Manual-JE")
            add_entry(je, pd, counter, f"Manual reallocation {random.choice(['reclass', 'correction', 'adjustment', 'journal'])}",
                      0, amt, random.choice(cc_list), user, entry_type="Manual", source="Manual-JE")

        # ---------- INJECTED FRAUD PATTERNS ----------
        inject(periods_so_far=None, p=p, m_end=m_end, vendors=vendors)

    print(f"  (GL lines: {len(GL):,}, injected anomalies: {len(ANOMALIES)})")


def inject(periods_so_far, p, m_end, vendors):
    """Inject one or two forensic anomalies per month."""

    # 1. DUPLICATE PAYMENT: same vendor, same amount, same invoice ref, 4-12 days apart
    v = random.choice([x["VendorID"] for x in vendors[:18]])
    amt = money(random.choice([4200, 7600, 11800]) * random.uniform(0.95, 1.05))
    d1 = m_end.replace(day=random.randint(3, 12))
    d2 = d1 + timedelta(days=random.randint(4, 12))
    inv = f"INV-{random.randint(20000, 29999)}"
    for dte in (d1, d2):
        je = next_je(p)
        add_entry(je, dte, "6090", f"Professional fees per invoice {inv} vendor {v}", amt, 0, "CC110",
                  "USR-012", vendor=v, anomaly="DUPLICATE-PAYMENT")
        add_entry(je, dte, "1010", f"Payment of invoice {inv} vendor {v}", 0, amt, "CC110",
                  "USR-012", vendor=v, anomaly="DUPLICATE-PAYMENT")
        ANOMALIES.append({"EntryID": je, "AnomalyType": "DUPLICATE-PAYMENT", "AmountUSD": amt,
                          "PreparedBy": "USR-012",
                          "ExpectedDetection": "Duplicate test on VendorID + Amount + Invoice reference within 30 days",
                          "Description": f"Same invoice {inv} paid twice to {v}"})

    # 2. ROUND NUMBER / THRESHOLD AVOIDANCE: just below R10,000 approval limit
    for i in range(random.randint(1, 2)):
        v = random.choice([x["VendorID"] for x in vendors[:18]])
        amt = money(random.choice([4990, 4985, 9750, 9900, 4995]))
        dte = m_end.replace(day=random.randint(5, 25))
        je = next_je(p)
        add_entry(je, dte, "6140", f"Supply of consumables vendor {v}", amt, 0, "CC200", "USR-002",
                  vendor=v, anomaly="ROUND-NUMBER-THRESHOLD")
        add_entry(je, dte, "1010", f"Payment vendor {v}", 0, amt, "CC200", "USR-002",
                  vendor=v, anomaly="ROUND-NUMBER-THRESHOLD")
        ANOMALIES.append({"EntryID": je, "AnomalyType": "ROUND-NUMBER-THRESHOLD", "AmountUSD": amt,
                          "PreparedBy": "USR-002",
                          "ExpectedDetection": f"Payments siting just below the ${APPROVAL_THRESHOLD:,.0f} approval limit; round-number test",
                          "Description": f"Payment {amt:,.2f} to {v} avoids CFO approval"})

    # 3. GHOST / RELATED-PARTY VENDOR PAYMENT
    if p.month in (1, 3, 5, 7, 9, 11) or p.year == 2025:
        ghost = [x for x in vendors if x["IsEmployeeLinked"] == "Yes"]
        if ghost:
            v = random.choice(ghost)
            amt = money(random.choice([15000, 22500, 34000, 48000]) * random.uniform(0.9, 1.1))
            dte = m_end.replace(day=random.randint(8, 26))
            je = next_je(p)
            add_entry(je, dte, "6090", f"Consulting services vendor {v['VendorID']}", amt, 0, "CC900",
                      "USR-001", vendor=v["VendorID"], anomaly="GHOST-VENDOR")
            add_entry(je, dte, "1010", f"Consulting fees {v['VendorName']}", 0, amt, "CC900",
                      "USR-001", vendor=v["VendorID"], anomaly="GHOST-VENDOR")
            ANOMALIES.append({"EntryID": je, "AnomalyType": "GHOST-VENDOR", "AmountUSD": amt,
                              "PreparedBy": "USR-001",
                              "ExpectedDetection": "Join vendor master to payroll/employee list on bank account or name; vendor created within 6 months",
                              "Description": f"Payment to employee-linked vendor {v['VendorName']} ({v['VendorCode']})"})

    # 4. WEEKEND / AFTER-HOURS MANUAL JE
    weekend_days = [p.replace(day=d) for d in range(1, m_end.day + 1)
                    if p.replace(day=d).weekday() >= 5]
    dte = random.choice(weekend_days) if weekend_days else m_end
    amt = money(random.choice([7400, 12800, 21500, 33000]))
    je = next_je(p)
    entry_ts = datetime.combine(dte, datetime.min.time()) + timedelta(hours=random.choice([2, 4, 22, 23]),
                                                                      minutes=random.randint(0, 59))
    add_entry(je, dte, "6190", "Year-end / period adjustment (weekend post)", amt, 0, "CC110", "USR-012",
              entry_type="Manual", source="Manual-JE", entered_on=entry_ts, anomaly="WEEKEND-AFTERHOURS")
    add_entry(je, dte, "1990", "Suspense clearing (weekend post)", 0, amt, "CC110", "USR-012",
              entry_type="Manual", source="Manual-JE", entered_on=entry_ts, anomaly="WEEKEND-AFTERHOURS")
    ANOMALIES.append({"EntryID": je, "AnomalyType": "WEEKEND-AFTERHOURS", "AmountUSD": amt,
                      "PreparedBy": "USR-012",
                      "ExpectedDetection": "EnteredOn weekday/time analysis vs posting date; period already closed",
                      "Description": f"Manual JE of {amt:,.2f} posted on {dte} ({dte.strftime('%A')}) at {entry_ts.hour:02d}:00 - outside business hours"})

    # 5. SPLIT PURCHASE to stay below PO threshold
    v = random.choice([x["VendorID"] for x in vendors[:18]])
    total = money(random.uniform(9000, 13000))
    parts = [money(total / 2), money(total - total / 2)]
    base_day = random.randint(2, 18)
    for i, part in enumerate(parts):
        dte = m_end.replace(day=base_day + i * 2)
        je = next_je(p)
        add_entry(je, dte, "6040", f"Engineering spares part {i+1}/2 vendor {v}", part, 0, "CC210", "USR-002",
                  vendor=v, anomaly="SPLIT-PURCHASE")
        add_entry(je, dte, "2000", f"Engineering spares part {i+1}/2 vendor {v}", 0, part, "CC210", "USR-002",
                  vendor=v, anomaly="SPLIT-PURCHASE")
        ANOMALIES.append({"EntryID": je, "AnomalyType": "SPLIT-PURCHASE", "AmountUSD": part,
                          "PreparedBy": "USR-002",
                          "ExpectedDetection": f"Multiple invoices just below the ${PO_THRESHOLD:,.0f} PO threshold, same vendor, same period",
                          "Description": f"Purchase split into {len(parts)} invoices totalling {total:,.2f} to avoid a PO"})

    # 6. UNUSUAL USER / ACCOUNT COMBINATION (segregation of duties breach)
    if random.random() < 0.5:
        amt = money(random.choice([9800, 16400, 27500]))
        dte = m_end.replace(day=random.randint(10, 27))
        je = next_je(p)
        add_entry(je, dte, "4010", "Credit note / revenue reclass by AP clerk", amt, 0, "CC300", "USR-002",
                  entry_type="Manual", source="Manual-JE", anomaly="SOD-RARE-COMBO")
        add_entry(je, dte, "1100", "Credit note / revenue reclass by AP clerk", 0, amt, "CC300", "USR-002",
                  entry_type="Manual", source="Manual-JE", anomaly="SOD-RARE-COMBO")
        ANOMALIES.append({"EntryID": je, "AnomalyType": "SOD-RARE-COMBO", "AmountUSD": amt,
                          "PreparedBy": "USR-002",
                          "ExpectedDetection": "User-account posting matrix: AP clerk posting to revenue/credit notes",
                          "Description": "AP clerk posted a revenue credit note - segregation of duties breach"})


def post_opening_balances():
    """Opening balance sheet at 1 January 2024 (source: prior-year audited accounts)."""
    ob = [
        ("1010", 420000.00), ("1020", 3500.00), ("1100", 985000.00), ("1110", -68000.00),
        ("1120", 42000.00), ("1200", 512000.00), ("1210", 168000.00), ("1220", 396000.00),
        ("1230", -52000.00), ("1300", 96000.00), ("1310", 74000.00), ("1400", 2850000.00),
        ("1410", 640000.00), ("1420", 210000.00), ("1430", 480000.00), ("1440", -1120000.00),
        ("1450", -328000.00), ("1460", -96000.00), ("1500", 850000.00), ("1600", 55000.00),
        ("2000", -742000.00), ("2010", -138000.00), ("2020", -64000.00), ("2100", -112000.00),
        ("2110", -46000.00), ("2120", -32000.00), ("2130", -96000.00), ("2300", -402000.00),
        ("2400", -168000.00), ("2500", -90000.00), ("3000", -1000000.00), ("3300", -180000.00),
    ]
    total = sum(v for _, v in ob)
    ob.append(("3100", money(-total)))          # retained earnings = balancing figure
    je = "JE202401-00001"
    d = date(2024, 1, 1)
    for code, amt in ob:
        add_entry(je, d, code, "Opening balance - prior year audited accounts",
                  amt if amt > 0 else 0.0, -amt if amt < 0 else 0.0, "CC100", "USR-001",
                  entry_type="Opening", source="Opening Balance Upload", approved_by="USR-006")
    return ob


def close_fy2024():
    """Year-end close: transfer the FY2024 result to retained earnings (31 Dec 2024)."""
    pl_balances = {}
    for r in GL:
        if r["PostingDate"][:4] != "2024":
            continue
        acct = r["AccountCode"]
        if not acct.startswith(("4", "5", "6", "7", "8")):
            continue
        pl_balances[acct] = pl_balances.get(acct, 0.0) + float(r["Debit"]) - float(r["Credit"])
    je = "JE202412-CLOSE"
    d = date(2024, 12, 31)
    total = 0.0
    for acct, bal in sorted(pl_balances.items()):
        if abs(bal) < 0.005:
            continue
        total += bal
        add_entry(je, d, acct, "FY2024 year-end close to retained earnings",
                  0.0 if bal > 0 else -bal, bal if bal > 0 else 0.0, "CC100", "USR-001",
                  entry_type="Closing", source="Year-End Close", approved_by="USR-006")
    add_entry(je, d, "3100", "FY2024 result transferred to retained earnings",
              total if total > 0 else 0.0, -total if total < 0 else 0.0, "CC100", "USR-001",
              entry_type="Closing", source="Year-End Close", approved_by="USR-006")
    return -total


# ----------------------------------------------------------------------------
# 4. TRIAL BALANCE (monthly, by account)
# ----------------------------------------------------------------------------
def build_trial_balance(accounts):
    """Monthly trial balance derived from the GL flow, presented as opening/movement/closing."""
    flow = {}
    for r in GL:
        key = (r["Period"], r["AccountCode"])
        dr = flow.setdefault(key, [0.0, 0.0])
        dr[0] += r["Debit"]
        dr[1] += r["Credit"]

    rows = []
    opening = {}
    periods = sorted({r["Period"] for r in GL})
    for period in periods:
        for a in accounts:
            code = a["AccountCode"]
            dr, cr = flow.get((period, code), [0.0, 0.0])
            sign = 1 if a["NormalBalance"] == "Debit" else -1
            movement = (dr - cr) * sign
            op = opening.get(code, 0.0)
            close = op + movement
            if abs(dr) < 0.005 and abs(cr) < 0.005 and abs(close) < 0.005:
                continue
            rows.append({
                "PeriodEnd": MONTH_END[datetime.strptime(period + "-01", "%Y-%m-%d").date()].isoformat(),
                "Period": period,
                "FiscalYear": int(period[:4]),
                "AccountCode": code,
                "DebitMovement": money(dr),
                "CreditMovement": money(cr),
                "NetMovementSigned": money(movement),
                "OpeningBalance": money(op),
                "ClosingBalance": money(close),
            })
            opening[code] = close
    return rows


# ----------------------------------------------------------------------------
# 5. AR / AP / SALES / BUDGET / PAYROLL / FIXED ASSETS / BANK / FX / EXPENSES
# ----------------------------------------------------------------------------
def build_ar_aging(customers):
    rows = []
    as_at = date(2025, 9, 30)
    for i in range(420):
        c = random.choice(customers)
        inv_date = as_at - timedelta(days=random.randint(5, 260))
        terms = c["PaymentTerms"]
        due = inv_date + timedelta(days=terms)
        amt = money(random.choice([4200, 8500, 13400, 19800, 26500, 42000, 68000]) * random.uniform(0.85, 1.2))
        days_over = (as_at - due).days
        bucket = ("Current" if days_over <= 0 else "1-30 days" if days_over <= 30 else
                  "31-60 days" if days_over <= 60 else "61-90 days" if days_over <= 90 else
                  "91-180 days" if days_over <= 180 else "Over 180 days")
        rows.append({
            "InvoiceNo": f"SI-{2024 + (inv_date.year - 2024)}{i:05d}",
            "CustomerID": c["CustomerID"],
            "InvoiceDate": inv_date.isoformat(),
            "DueDate": due.isoformat(),
            "Currency": c["Currency"],
            "AmountUSD": amt,
            "AmountReceivedUSD": money(0 if days_over > 60 else amt * random.choice([0, 0, 0.35, 0.6, 1.0])),
            "DaysOverdue": max(days_over, 0),
            "AgeingBucket": bucket,
            "DisputedFlag": "Yes" if random.random() < 0.05 else "No",
            "AsAtDate": as_at.isoformat(),
        })
    return rows


def build_ap_invoices(vendors):
    rows = []
    for i in range(520):
        v = random.choice(vendors)
        inv_date = date(2025, 9, 30) - timedelta(days=random.randint(3, 220))
        amt = money(random.choice([1200, 2800, 4600, 7300, 9900, 15400, 22800, 36400]) * random.uniform(0.85, 1.2))
        has_po = random.random() > 0.22
        grn = random.random() > 0.18
        dup = random.random() < 0.04
        rows.append({
            "APInvoiceNo": f"PI-{i:05d}",
            "SupplierInvoiceRef": f"INV-{random.randint(10000, 39999)}",
            "VendorID": v["VendorID"],
            "InvoiceDate": inv_date.isoformat(),
            "DueDate": (inv_date + timedelta(days=v["PaymentTerms"])).isoformat(),
            "AmountUSD": amt,
            "PONumber": f"PO-{random.randint(5000, 6999)}" if has_po else "",
            "GRNNumber": f"GRN-{random.randint(7000, 8999)}" if grn else "",
            "ThreeWayMatch": "Matched" if (has_po and grn) else "Exception",
            "DuplicateSuspected": "Yes" if dup else "No",
            "ApprovedBy": random.choice(["", "USR-001", "USR-006", "USR-002"]),
            "PaidStatus": random.choice(["Paid", "Paid", "Paid", "Outstanding"]),
            "PaymentDate": (inv_date + timedelta(days=random.randint(20, 75))).isoformat(),
        })
    return rows


def build_sales_orders(customers, cost_centres):
    rows = []
    for i in range(900):
        c = random.choice(customers)
        od = date(2024, 1, 1) + timedelta(days=random.randint(0, 638))
        rows.append({
            "OrderNo": f"SO-{i:05d}",
            "CustomerID": c["CustomerID"],
            "OrderDate": od.isoformat(),
            "Period": f"{od.year}-{od.month:02d}",
            "ProductFamily": random.choice(["Fabricated Steel", "Polymer Components", "Industrial Chemicals",
                                            "Packaging Materials", "Spares", "Service Contract"]),
            "ProductLine": random.choice(["PS-100", "PS-200", "PS-300", "PC-10", "PC-20", "IC-5", "SP-9"]),
            "Quantity": random.randint(1, 480),
            "UnitPriceUSD": money(random.uniform(12, 320)),
            "GrossAmountUSD": 0,
            "DiscountPct": random.choice([0, 0, 0, 2.5, 5, 7.5, 10, 15]),
            "CostCentreCode": "CC300" if c["Currency"] == "USD" else "CC310",
            "SalesRep": random.choice(["B. Ncube", "T. Makuvaza", "S. Moyo", "A. Banda"]),
            "Status": random.choice(["Invoiced", "Invoiced", "Invoiced", "Open", "Cancelled"]),
            "MarginPct": money(random.uniform(8, 42)),
        })
        r = rows[-1]
        r["GrossAmountUSD"] = money(r["Quantity"] * r["UnitPriceUSD"] * (1 - r["DiscountPct"] / 100))
    return rows


def build_budget(accounts, gl_rows):
    """Monthly budget by P&L account and cost centre, derived from the ledger with an
    uplift/trim so variances are a realistic mix of favourable and adverse.

    Uses its own Random instance so the rest of the dataset is unaffected."""
    rnd = random.Random(4242)
    pl_accounts = {a["AccountCode"] for a in accounts if a["Statement"] == "PL"}
    actual = {}
    for r in gl_rows:
        if r["AccountCode"] not in pl_accounts or r["SourceSystem"] == "Year-End Close":
            continue
        key = (r["Period"], r["AccountCode"], r["CostCentreCode"])
        actual[key] = actual.get(key, 0.0) + float(r["Credit"]) - float(r["Debit"])

    rows = []
    for (period, account, cc), signed in sorted(actual.items()):
        magnitude = abs(signed)
        if magnitude < 500:            # do not budget trivial amounts
            continue
        factor = rnd.uniform(0.90, 1.10)
        rows.append({
            "Period": period,
            "FiscalYear": int(period[:4]),
            "MonthNum": int(period[5:7]),
            "AccountCode": account,
            "CostCentreCode": cc,
            "BudgetUSD": money(magnitude * factor),
            "BudgetVersion": "V1-Board Approved",
        })
    return rows


def build_payroll(users):
    rows = []
    emp_names = [u["UserName"] for u in users] + [f"{random.choice(FIRST)} {random.choice(LAST)}" for _ in range(48)]
    for i, name in enumerate(emp_names, start=1):
        emp_id = f"EMP{1000 + i}"
        base = money(random.choice([950, 1250, 1650, 2200, 3100, 4200, 5600, 7800]) * random.uniform(0.9, 1.15))
        dept = random.choice([c[2] for c in COST_CENTRES])
        rows.append({
            "EmployeeID": emp_id,
            "EmployeeName": name,
            "Department": dept,
            "JobTitle": random.choice(["Operator", "Artisan", "Clerk", "Supervisor", "Manager", "Analyst", "Driver"]),
            "GradeLevel": random.choice(["A2", "B1", "B2", "C1", "C2", "D1"]),
            "MonthlyGrossUSD": base,
            "DateOfBirth": (date(1975, 1, 1) + timedelta(days=random.randint(0, 9000))).isoformat(),
            "HireDate": (date(2015, 1, 1) + timedelta(days=random.randint(0, 3600))).isoformat(),
            "BankAccount": f"10{random.randint(1000000, 9999999)}",
            "NationalIDPresent": "No" if random.random() < 0.05 else "Yes",
            "TerminationDate": "",
            "IsFlaggedForReview": "No",
        })
    # ghost employee pattern
    for j in range(3):
        base = money(random.choice([1450, 2100, 2650]))
        e = {
            "EmployeeID": f"EMP9{j+1:02d}", "EmployeeName": f"{random.choice(FIRST)} {random.choice(LAST)}",
            "Department": random.choice(["Manufacturing", "Administration"]),
            "JobTitle": "Operator", "GradeLevel": "A2", "MonthlyGrossUSD": base,
            "DateOfBirth": "1988-06-15", "HireDate": "2024-07-01",
            "BankAccount": f"10{random.randint(1000000, 9999999)}",
            "NationalIDPresent": "No", "TerminationDate": "", "IsFlaggedForReview": "Yes",
        }
        rows.append(e)
    # terminated but still paid
    for j in range(2):
        rows[-1 - j]["TerminationDate"] = "2025-03-31"
    return rows


def build_fixed_assets():
    rows = []
    classes = [("Plant and Machinery", "1400", "1440", 10), ("Motor Vehicles", "1410", "1450", 5),
               ("Office Equipment", "1420", "1460", 4)]
    for i in range(120):
        cls, cost_acct, accdep, life = random.choice(classes)
        cost = money(random.choice([8500, 18000, 34000, 62000, 145000, 310000]) * random.uniform(0.9, 1.1))
        acq = date(2016, 1, 1) + timedelta(days=random.randint(0, 3300))
        dep_charge = cost / life / 12
        months = max((date(2025, 9, 1).year - acq.year) * 12 + date(2025, 9, 1).month - acq.month, 0)
        months = min(months, life * 12)
        rows.append({
            "AssetID": f"FA-{1000 + i}", "AssetDescription": f"{cls.split()[0]} unit {i+1:03d}",
            "AssetClass": cls, "CostAccountCode": cost_acct, "AccDepAccountCode": accdep,
            "LocationCode": random.choice([c[0] for c in COST_CENTRES]),
            "AcquisitionDate": acq.isoformat(),
            "CostUSD": cost,
            "UsefulLifeYears": life,
            "MonthlyDepreciationUSD": money(dep_charge),
            "AccumulatedDepreciationUSD": money(dep_charge * months),
            "NBVUSD": money(cost - dep_charge * months),
            "DisposalDate": (date(2025, 4, 12).isoformat() if random.random() < 0.05 else ""),
            "Custodian": random.choice(["N. Zhou", "P. Gumbo", "A. Banda", "K. Dube"]),
        })
    return rows


def build_bank_transactions():
    rows = []
    bal = 420000.0
    for i in range(1400):
        dt = date(2024, 1, 1) + timedelta(days=random.randint(0, 638))
        amt = money(random.choice([-1, 1]) * random.choice([850, 2200, 5400, 9800, 16400, 27500, 48000]) * random.uniform(0.7, 1.3))
        bal += amt
        rows.append({
            "BankTxnID": f"BTX{i:06d}",
            "BankAccount": "Bank - CBZ USD Current",
            "TxnDate": dt.isoformat(),
            "ValueDate": (dt + timedelta(days=random.randint(0, 2))).isoformat(),
            "Narration": random.choice(["TRF FROM CUSTOMER", "PAYMENT VENDOR", "SALARY PAYMENT", "BANK CHARGES",
                                        "VAT PAYMENT", "DIRECT DEBIT", "CASH DEPOSIT", "FX CONVERSION",
                                        "INTEREST CREDIT", "MOBILE PAYMENT"]),
            "DebitUSD": money(-amt) if amt < 0 else 0.0,
            "CreditUSD": money(amt) if amt > 0 else 0.0,
            "BalanceUSD": money(bal),
            "ReconciledFlag": "Yes" if random.random() > 0.08 else "No",
            "UnmatchedItemsAgeDays": random.choice([0, 0, 0, 3, 12, 46, 93, 210]),
        })
    return rows


def build_fx():
    rows = []
    rates = {"USD": 1.0, "ZAR": 0.054, "GBP": 1.27, "EUR": 1.08, "ZWG": 0.036}
    for p in PERIODS:
        for ccy, base in rates.items():
            if ccy == "USD":
                continue
            drift = 1 + random.uniform(-0.03, 0.03)
            rows.append({
                "Period": f"{p.year}-{p.month:02d}",
                "PeriodEndDate": MONTH_END[p].isoformat(),
                "FromCurrency": ccy,
                "ToCurrency": "USD",
                "AverageRate": money(base * drift),
                "ClosingRate": money(base * drift * random.uniform(0.99, 1.01)),
            })
    return rows


def build_expense_claims(users):
    rows = []
    for i in range(650):
        u = random.choice(users)
        dt = date(2024, 1, 1) + timedelta(days=random.randint(0, 638))
        amt = money(random.choice([45, 120, 260, 480, 950, 1500, 2750, 4800]) * random.uniform(0.8, 1.25))
        rows.append({
            "ClaimID": f"EXP-{i:05d}",
            "EmployeeID": f"EMP{random.randint(1000, 1050):04d}",
            "EmployeeName": u["UserName"],
            "ClaimDate": dt.isoformat(),
            "Period": f"{dt.year}-{dt.month:02d}",
            "ExpenseCategory": random.choice(["Travel - Air", "Travel - Mileage", "Accommodation", "Meals",
                                              "Client Entertainment", "Training", "Communication", "Fuel"]),
            "ClaimedUSD": amt,
            "ReceiptAttached": "No" if random.random() < 0.14 else "Yes",
            "ApprovedBy": random.choice(["USR-001", "USR-006", "USR-011"]),
            "PaidDate": (dt + timedelta(days=random.randint(7, 40))).isoformat(),
            "DuplicateSuspected": "Yes" if random.random() < 0.03 else "No",
            "WeekendClaim": "Yes" if dt.weekday() >= 5 else "No",
        })
    return rows


def build_date_dimension():
    rows = []
    d = date(2023, 1, 1)
    while d <= date(2026, 12, 31):
        fy = d.year if d.month >= 1 else d.year - 1
        rows.append({
            "Date": d.isoformat(),
            "DateKey": int(d.strftime("%Y%m%d")),
            "DayName": d.strftime("%A"),
            "DayNameShort": d.strftime("%a"),
            "DayOfMonth": d.day,
            "DayOfWeekNumber": d.isoweekday(),
            "IsWeekend": "Yes" if d.weekday() >= 5 else "No",
            "WeekNumberISO": int(d.isocalendar()[1]),
            "MonthNumber": d.month,
            "MonthName": d.strftime("%B"),
            "MonthShort": d.strftime("%b"),
            "MonthYear": d.strftime("%b %Y"),
            "Quarter": f"Q{((d.month - 1) // 3) + 1}",
            "QuarterYear": f"{d.year} Q{((d.month - 1) // 3) + 1}",
            "FiscalYear": f"FY{d.year}",
            "FiscalPeriod": f"{d.year}-{d.month:02d}",
            "FiscalPeriodEnd": MONTH_END.get(date(d.year, d.month, 1), d).isoformat(),
            "IsMonthEnd": "Yes" if (d + timedelta(days=1)).month != d.month else "No",
            "IsCurrentFY": "Yes" if d.year == 2025 else "No",
        })
        d += timedelta(days=1)
    return rows


def build_engagement_log():
    """Maxhub's own advisory engagement pipeline - for Capstone 4 (AI & advisory services)."""
    services = ["Forensic investigation", "Fraud risk assessment", "Data analytics build",
                "Power BI dashboard", "Machine learning model", "IFRS advisory",
                "Internal audit co-sourcing", "Tax analytics", "CFO advisory retainer"]
    clients = ["Mhondoro Manufacturing", "Great Dyke Mining", "AgriHub Cooperative", "RetailZ Supermarkets",
               "Sunrise Hospitals", "Municipality of Kadoma", "TransContinental Haulage", "FoodProcessors Alliance",
               "SADC Industrial Supplies", "UnivTrust Procurement"]
    rows = []
    for i in range(160):
        st = date(2024, 1, 1) + timedelta(days=random.randint(0, 638))
        fee = money(random.choice([4500, 9500, 15000, 28000, 45000, 75000, 120000]) * random.uniform(0.85, 1.15))
        rows.append({
            "EngagementID": f"MX-{2024 + (st.year - 2024)}{i:04d}",
            "ClientName": random.choice(clients),
            "ServiceLine": random.choice(services),
            "EngagementManager": random.choice(["T. Makuvaza", "S. Moyo", "J. Marufu"]),
            "StartDate": st.isoformat(),
            "Period": f"{st.year}-{st.month:02d}",
            "PlannedHours": random.choice([24, 40, 80, 120, 200, 320]),
            "ActualHours": random.choice([24, 40, 80, 120, 200, 320]) * random.uniform(0.8, 1.45),
            "FeeUSD": fee,
            "WriteOffUSD": money(fee * random.uniform(0, 0.18)) if random.random() < 0.3 else 0.0,
            "Status": random.choice(["Completed", "Completed", "In progress", "Proposal", "Lost"]),
            "NetPromoterScore": random.choice([7, 8, 9, 9, 10, 10, 6]),
        })
    return rows


# ----------------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------------
def main():
    print(f"\nGenerating Maxhub Power BI course data for {CLIENT}")
    print(f"Period: {FY_START} to {FY_END}   Functional currency: {FUNCTIONAL_CCY}\n")

    accounts = build_accounts()
    centres = build_cost_centres()
    users = build_users()
    vendors = build_vendors()
    customers = build_customers()
    dates = build_date_dimension()
    payroll = build_payroll(users)
    assets = build_fixed_assets()
    fx = build_fx()

    ob = post_opening_balances()
    generate_gl(vendors, customers)
    fy24 = close_fy2024()
    print(f"  FY2024 result closed to retained earnings: {fy24:,.2f}")
    tb = build_trial_balance(accounts)
    ar = build_ar_aging(customers)
    ap = build_ap_invoices(vendors)
    so = build_sales_orders(customers, centres)
    budget = build_budget(accounts, GL)
    bank = build_bank_transactions()
    claims = build_expense_claims(users)
    engagements = build_engagement_log()

    write_csv("DimAccount.csv", accounts)
    write_csv("DimCostCentre.csv", centres)
    write_csv("DimUser.csv", users)
    write_csv("DimDate.csv", dates)
    write_csv("DimVendor.csv", vendors)
    write_csv("DimCustomer.csv", customers)
    write_csv("DimEmployee.csv", payroll)
    write_csv("FactGLJournal.csv", GL)
    write_csv("FactTrialBalance.csv", tb)
    write_csv("FactARAgeing.csv", ar)
    write_csv("FactAPInvoices.csv", ap)
    write_csv("FactSalesOrders.csv", so)
    write_csv("FactBudget.csv", budget)
    write_csv("FactBankTransactions.csv", bank)
    write_csv("FactExpenseClaims.csv", claims)
    write_csv("FactFixedAssets.csv", assets)
    write_csv("DimFXRate.csv", fx)
    write_csv("MaxhubEngagements.csv", engagements)
    write_csv("InjectionLog.csv", ANOMALIES)

    # integrity checks
    dr = round(sum(r["Debit"] for r in GL), 2)
    cr = round(sum(r["Credit"] for r in GL), 2)
    print(f"\n  Control check  Total debits {dr:,.2f} | Total credits {cr:,.2f} | Difference {dr - cr:,.2f}")
    print(f"  Anomaly types: {sorted({a['AnomalyType'] for a in ANOMALIES})}")
    print(f"\nOutput folder: {OUT}\n")


if __name__ == "__main__":
    main()
