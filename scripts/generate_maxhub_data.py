#!/usr/bin/env python3
"""
Maxhub Pvt Ltd - internal management data for the advisory / ML / AI capstones.
Creates the firm's own numbers: service-line financials, consultant utilisation,
pipeline, and a client-churn dataset suitable for a classification model.

Output: data/raw/maxhub_*.csv  (plus MaxhubEngagements.csv from generate_data.py)
"""
import csv
import math
import os
import random
from datetime import date, timedelta

random.seed(7712)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "raw")
os.makedirs(OUT, exist_ok=True)

SERVICE_LINES = ["Forensic Accounting", "Data Analytics", "Machine Learning & AI",
                 "IFRS & Technical Advisory", "Internal Audit", "Tax Analytics", "CFO Advisory"]
SERVICE_WEIGHT = [0.22, 0.20, 0.13, 0.16, 0.15, 0.06, 0.08]

CONSULTANTS = [
    ("MX-C01", "T. Makuvaza", "Partner", 2), ("MX-C02", "S. Moyo", "Senior Manager", 3),
    ("MX-C03", "J. Marufu", "Manager", 4), ("MX-C04", "R. Chikafu", "Senior Consultant", 5),
    ("MX-C05", "N. Zhou", "Consultant", 6), ("MX-C06", "K. Dube", "Data Analyst", 5),
    ("MX-C07", "P. Gumbo", "Consultant", 6), ("MX-C08", "A. Banda", "ML Engineer", 4),
    ("MX-C09", "L. Sibanda", "Director", 2), ("MX-C10", "B. Ncube", "Consultant", 7),
]

CLIENTS = [
    "Mhondoro Manufacturing", "Great Dyke Mining", "AgriHub Cooperative", "RetailZ Supermarkets",
    "Sunrise Hospitals", "Municipality of Kadoma", "TransContinental Haulage", "FoodProcessors Alliance",
    "SADC Industrial Supplies", "UnivTrust Procurement", "EnergyAfrica Distributors", "PrintWorks Limited",
    "PlastiCorp Factory", "FarmSupply Depot", "BuildMart Hardware",
]

INDUSTRIES = {"Mhondoro Manufacturing": "Manufacturing", "Great Dyke Mining": "Mining",
              "AgriHub Cooperative": "Agriculture", "RetailZ Supermarkets": "Retail",
              "Sunrise Hospitals": "Healthcare", "Municipality of Kadoma": "Public sector",
              "TransContinental Haulage": "Logistics", "FoodProcessors Alliance": "Manufacturing",
              "SADC Industrial Supplies": "Wholesale", "UnivTrust Procurement": "Public sector",
              "EnergyAfrica Distributors": "Energy", "PrintWorks Limited": "Services",
              "PlastiCorp Factory": "Manufacturing", "FarmSupply Depot": "Agriculture",
              "BuildMart Hardware": "Retail"}


def write(name, rows):
    path = os.path.join(OUT, name)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"  {name:<32}{len(rows):>7,} rows")


def months():
    out, d = [], date(2023, 1, 1)
    while d <= date(2025, 9, 1):
        out.append(d)
        d = date(d.year + (d.month // 12), (d.month % 12) + 1, 1)
    return out


def build_financials():
    rows = []
    for m in months():
        growth = 1 + 0.011 * ((m.year - 2023) * 12 + m.month)
        for sl, wt in zip(SERVICE_LINES, SERVICE_WEIGHT):
            revenue = random.uniform(9000, 26000) * wt / 0.15 * growth
            direct = revenue * random.uniform(0.42, 0.58)
            rows.append({
                "Month": m.isoformat(), "Period": f"{m.year}-{m.month:02d}", "FiscalYear": m.year,
                "ServiceLine": sl,
                "RevenueUSD": round(revenue, 2),
                "DirectStaffCostUSD": round(direct, 2),
                "RechargeableExpensesUSD": round(revenue * random.uniform(0.02, 0.07), 2),
                "OverheadAllocatedUSD": round(revenue * random.uniform(0.16, 0.26), 2),
                "GrossProfitUSD": round(revenue - direct, 2),
                "EngagementsDelivered": random.randint(2, 11),
                "ProposalsSubmitted": random.randint(1, 6),
                "ProposalsWon": random.randint(0, 4),
            })
    return rows


def build_billable_hours():
    rows = []
    for m in months():
        for cid, name, grade, std_rate in CONSULTANTS:
            available = 21 * 8
            hours = random.gauss(available * 0.72, available * 0.09)
            hours = max(40.0, min(hours, available))
            billable = hours * random.uniform(0.62, 0.92)
            rows.append({
                "Period": f"{m.year}-{m.month:02d}", "Month": m.isoformat(),
                "ConsultantID": cid, "ConsultantName": name, "Grade": grade,
                "AvailableHours": available,
                "WorkedHours": round(hours, 1),
                "BillableHours": round(billable, 1),
                "UtilisationPct": round(billable / available * 100, 1),
                "StandardRateUSD": std_rate * 40,
                "RealisedRateUSD": round(std_rate * 40 * random.uniform(0.72, 1.02), 2),
            })
    return rows


def build_pipeline():
    rows = []
    stages = ["Lead", "Qualified", "Proposal", "Negotiation", "Won", "Lost"]
    for i in range(240):
        st = date(2023, 1, 1) + timedelta(days=random.randint(0, 980))
        client = random.choice(CLIENTS)
        rows.append({
            "OpportunityID": f"OPP-{i:04d}",
            "ClientName": client,
            "Industry": INDUSTRIES[client],
            "ServiceLine": random.choices(SERVICE_LINES, SERVICE_WEIGHT)[0],
            "OpenedDate": st.isoformat(),
            "Period": f"{st.year}-{st.month:02d}",
            "Stage": random.choice(stages),
            "ProbabilityPct": random.choice([10, 25, 40, 55, 70, 90, 100, 0]),
            "ExpectedFeeUSD": round(random.choice([4500, 9000, 18000, 32000, 54000, 96000, 140000])
                                    * random.uniform(0.85, 1.15), 2),
            "Source": random.choice(["Referral", "Tender", "Website", "LinkedIn", "Existing client", "Partner network"]),
            "DecisionTargetDate": (st + timedelta(days=random.randint(20, 150))).isoformat(),
        })
    return rows


def build_client_churn():
    """One row per client-year: features plus the label "Stayed" (1 = bought again next year).
    Built for a binary classification model in Module 11 - the signal is real but noisy,
    exactly like a real client-retention dataset."""
    clients_detail = [
        ("CL-01", "Mhondoro Manufacturing", "Manufacturing", 2021, 285000, "Large"),
        ("CL-02", "Great Dyke Mining", "Mining", 2020, 512000, "Large"),
        ("CL-03", "AgriHub Cooperative", "Agriculture", 2022, 96000, "Medium"),
        ("CL-04", "RetailZ Supermarkets", "Retail", 2019, 348000, "Large"),
        ("CL-05", "Sunrise Hospitals", "Healthcare", 2021, 152000, "Medium"),
        ("CL-06", "Municipality of Kadoma", "Public sector", 2020, 210000, "Medium"),
        ("CL-07", "TransContinental Haulage", "Logistics", 2022, 78000, "Small"),
        ("CL-08", "FoodProcessors Alliance", "Manufacturing", 2019, 402000, "Large"),
        ("CL-09", "SADC Industrial Supplies", "Wholesale", 2021, 64000, "Small"),
        ("CL-10", "UnivTrust Procurement", "Public sector", 2023, 118000, "Medium"),
        ("CL-11", "EnergyAfrica Distributors", "Energy", 2020, 226000, "Large"),
        ("CL-12", "PrintWorks Limited", "Services", 2022, 52000, "Small"),
        ("CL-13", "PlastiCorp Factory", "Manufacturing", 2021, 88000, "Medium"),
        ("CL-14", "FarmSupply Depot", "Agriculture", 2023, 44000, "Small"),
        ("CL-15", "BuildMart Hardware", "Retail", 2019, 134000, "Medium"),
        ("CL-16", "Highveld Cement Works", "Manufacturing", 2020, 268000, "Large"),
        ("CL-17", "Kariba Energy Services", "Energy", 2022, 176000, "Medium"),
        ("CL-18", "Nyanga Tea Estates", "Agriculture", 2018, 94000, "Medium"),
        ("CL-19", "Midlands Steel Fabricators", "Manufacturing", 2021, 142000, "Medium"),
        ("CL-20", "Victoria Falls Resorts", "Hospitality", 2019, 205000, "Medium"),
        ("CL-21", "Chinhoyi Poultry Group", "Agriculture", 2023, 58000, "Small"),
        ("CL-22", "Bulawayo Textiles", "Manufacturing", 2020, 112000, "Medium"),
        ("CL-23", "Zambezi Fisheries", "Agriculture", 2022, 66000, "Small"),
        ("CL-24", "Harare Pharmaceuticals", "Healthcare", 2021, 188000, "Medium"),
        ("CL-25", "Mutare Timber Products", "Manufacturing", 2019, 124000, "Medium"),
        ("CL-26", "Gweru Motor Assemblies", "Manufacturing", 2022, 246000, "Large"),
        ("CL-27", "Kwekwe Alloys", "Mining", 2018, 368000, "Large"),
        ("CL-28", "Masvingo Grain Traders", "Wholesale", 2023, 72000, "Small"),
        ("CL-29", "Chiredzi Sugar Estates", "Agriculture", 2020, 158000, "Medium"),
        ("CL-30", "Kadoma Paper Mills", "Manufacturing", 2021, 132000, "Medium"),
    ]
    rows = []
    for cid, name, industry, since, annual_fee, size in clients_detail:
        # a stable, client-specific "relationship strength" not visible as a column -
        # this is the unobserved reality every real model has to work around
        hidden_strength = random.gauss(0, 0.8)
        for year in range(2021, 2026):
            fee = round(annual_fee * random.uniform(0.8, 1.2), 2)
            if year >= 2025:
                fee = round(fee * 0.9, 2)
            nps = random.choice([4, 5, 6, 7, 7, 8, 8, 9, 9, 10])
            complaints = random.choices([0, 1, 2, 3], [0.55, 0.27, 0.12, 0.06])[0]
            payment_days = int(random.gauss(46, 16))
            delay = random.randint(0, 45)
            partner_hours = round(random.gauss(26, 10), 1)
            findings = random.choices([0, 1, 2, 3, 4], [0.32, 0.29, 0.21, 0.12, 0.06])[0]
            services = random.randint(1, 5)
            fee_change = round(random.uniform(-18, 22), 1)

            logit = (
                hidden_strength
                + 0.55 * (nps - 7) / 1.5
                - 0.75 * complaints
                - 0.55 * (payment_days - 46) / 16
                + 0.45 * (partner_hours - 26) / 10
                + 0.40 * (services - 2) / 1.2
                - 0.35 * delay / 22
                + 0.20 * findings
            )
            p_stay = 1 / (1 + math.exp(-logit))
            stayed = 1 if random.random() < p_stay else 0
            rows.append({
                "ClientID": cid, "ClientName": name, "Industry": industry, "ClientSince": since,
                "ClientSize": size, "Year": year,
                "AnnualFeeUSD": fee,
                "ServicesPurchased": services,
                "NPS": nps,
                "ComplaintsLogged": complaints,
                "AvgPaymentDays": payment_days,
                "EngagementDelayDays": delay,
                "PartnerHoursOnClient": partner_hours,
                "AuditFindingsRaised": findings,
                "FeeChangePct": fee_change,
                "Stayed": stayed,
            })
    return rows


if __name__ == "__main__":
    print("\nGenerating Maxhub Pvt Ltd internal datasets\n")
    write("maxhub_service_line_financials.csv", build_financials())
    write("maxhub_billable_hours.csv", build_billable_hours())
    write("maxhub_pipeline.csv", build_pipeline())
    write("maxhub_client_churn.csv", build_client_churn())
    print("\n  Files written to data/raw/\n")
