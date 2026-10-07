#!/usr/bin/env python3
"""
Builds the Excel workbooks used in the labs:
  data/xlsx/Mhondoro_Accounting_Data.xlsx  - the full practice data warehouse (hands-on labs)
  data/xlsx/PowerBI_Practice_Workbook.xlsx - exercise tables (simple charts, cleaning drills, DAX practice)
  data/xlsx/Maxhub_Firm_Financials.xlsx    - Maxhub Pvt Ltd internal data (advisory / ML capstones)
"""
import csv
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
XLSX = os.path.join(ROOT, "data", "xlsx")
os.makedirs(XLSX, exist_ok=True)

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
NOTE_FONT = Font(italic=True, color="595959", size=10)


def read_csv(name):
    with open(os.path.join(RAW, name), newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def add_sheet(wb, title, rows, note="", widths=None, freeze=True):
    ws = wb.create_sheet(title[:31])
    r0 = 1
    if note:
        ws.cell(row=1, column=1, value=note).font = NOTE_FONT
        r0 = 3
    for j, h in enumerate(rows[0], start=1):
        c = ws.cell(row=r0, column=j, value=h)
        c.fill, c.font = HEADER_FILL, HEADER_FONT
        c.alignment = Alignment(horizontal="center")
    for i, row in enumerate(rows[1:], start=r0 + 1):
        for j, v in enumerate(row, start=1):
            ws.cell(row=i, column=j, value=coerce(v))
    if widths:
        for j, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(j)].width = w
    else:
        for j in range(1, len(rows[0]) + 1):
            ws.column_dimensions[get_column_letter(j)].width = 16
    if freeze:
        ws.freeze_panes = ws.cell(row=r0 + 1, column=1)
    return ws


def coerce(v):
    if v in ("", None):
        return None
    try:
        if "." in v:
            return float(v)
        return int(v)
    except (ValueError, TypeError):
        return v


MESSY_NOTE = ("Deliberately messy: text still wrapped in quotes, mixed case, dates as text. "
              "Your job in the Power Query modules is to clean it.")

# --------------------------------------------------------------------------
# 1. Mhondoro Accounting Data (full warehouse)
# --------------------------------------------------------------------------
def build_main():
    wb = Workbook()
    wb.remove(wb.active)

    ws = wb.create_sheet("READ ME")
    lines = [
        ("Mhondoro Manufacturing (Pvt) Ltd - practice data warehouse", True),
        ("", False),
        ("Built for the Maxhub Pvt Ltd Power BI course.", False),
        ("All companies, people, bank accounts and transactions are fictional.", False),
        ("Fictional client: Mhondoro Manufacturing (Pvt) Ltd - a Harare/Bulawayo light manufacturer.", False),
        ("Reporting period: 1 January 2024 - 30 September 2025. Functional currency: USD. VAT 15%.", False),
        ("", False),
        ("TABLES (dims = lookup tables, facts = transaction tables)", True),
        ("DimAccount / DimCostCentre / DimUser / DimDate / DimVendor / DimCustomer / DimEmployee", False),
        ("FactGLJournal - the general ledger: every debit and credit line", False),
        ("FactTrialBalance - monthly opening / movement / closing balance per account", False),
        ("FactARAgeing - debtor invoice ageing as at 30 Sep 2025", False),
        ("FactAPInvoices - creditor invoices with 3-way match status", False),
        ("FactSalesOrders - order-level sales with product family and rep", False),
        ("FactBudget - board approved monthly budget by account and cost centre", False),
        ("FactBankTransactions - bank statement lines", False),
        ("FactExpenseClaims - employee expense claims", False),
        ("FactFixedAssets - fixed asset register", False),
        ("DimFXRate - monthly average and closing exchange rates", False),
        ("InjectionLog - HIDDEN SHEET: the answers to the forensic labs. Right-click a sheet tab >", True),
        ("Unhide only after you have completed Lab 09 and written your own evidence register.", True),
        ("", False),
        ("CONTROL TOTALS: total debits = total credits in FactGLJournal.", True),
        ("", False),
        ("Tip: in Power BI use Get Data > Excel Workbook and tick the tables you need.", False),
    ]
    for i, (text, bold) in enumerate(lines, start=1):
        c = ws.cell(row=i, column=1, value=text)
        c.font = Font(bold=bold, size=13 if i == 1 else 11,
                      color="1F4E79" if bold else "333333")
    ws.column_dimensions["A"].width = 110

    dims = [
        ("DimAccount.csv", "Chart of accounts with FS line mapping", 18),
        ("DimCostCentre.csv", "Cost centres, departments and budgets", 24),
        ("DimUser.csv", "ERP users and their entitlements", 20),
        ("DimDate.csv", "Continuous date table 2023-2026 with fiscal columns", 14),
        ("DimVendor.csv", "Vendor master (text wrapped in quotes on purpose)", 26),
        ("DimCustomer.csv", "Customer master", 26),
        ("DimEmployee.csv", "Payroll / employee master", 20),
        ("FactGLJournal.csv", "General ledger journal lines", 18),
        ("FactTrialBalance.csv", "Monthly trial balance extract", 18),
        ("FactARAgeing.csv", "Accounts receivable ageing", 18),
        ("FactAPInvoices.csv", "Accounts payable invoices", 18),
        ("FactSalesOrders.csv", "Sales orders", 18),
        ("FactBudget.csv", "Budget by account, cost centre and month", 16),
        ("FactBankTransactions.csv", "Bank statement", 20),
        ("FactExpenseClaims.csv", "Expense claims", 18),
        ("FactFixedAssets.csv", "Fixed asset register", 18),
        ("DimFXRate.csv", "Monthly FX rates", 16),
        ("InjectionLog.csv", "ANSWER KEY - fraudulent entries (do not open early)", 40),
    ]
    for f, note, w in dims:
        rows = read_csv(f)
        ws = add_sheet(wb, f.replace(".csv", ""), rows, note=note, widths=[w] * len(rows[0]))
        if f == "InjectionLog.csv":
            # Soft gate: keep the answer key out of sight until Module 10.
            # To reveal it: right-click any sheet tab > Unhide. The READ ME says when.
            ws.sheet_state = "hidden"
    wb.save(os.path.join(XLSX, "Mhondoro_Accounting_Data.xlsx"))
    print("  Mhondoro_Accounting_Data.xlsx")


# --------------------------------------------------------------------------
# 2. Practice workbook (module exercises)
# --------------------------------------------------------------------------
def build_practice():
    wb = Workbook()
    wb.remove(wb.active)

    ws = wb.create_sheet("Instructions")
    txt = [
        ("Power BI Course - Practice Workbook", True),
        ("", False),
        ("Sheet 'Sales2019-2021'  : build your first line, column, bar, pie, donut, treemap, funnel, gauge, card, KPI and map visuals.", False),
        ("Sheet 'SimpleData'      : a 24-row table for the 'which visual for which data' lab.", False),
        ("Sheet 'PracticeFinance' : a compact P&L extract for your first DAX measures.", False),
        ("Sheet 'MessyData'       : cleaning drills for Power Query (text, dates, decimals, duplicates).", False),
        ("Sheet 'BudgetVsActual'  : variance and bridge-chart practice.", False),
        ("", False),
        ("Import each sheet with Get Data > Excel Workbook > select the sheet > Transform Data.", False),
    ]
    for i, (t, b) in enumerate(txt, start=1):
        ws.cell(row=i, column=1, value=t).font = Font(bold=b, size=13 if i == 1 else 11,
                                                      color="1F4E79" if b else "333333")
    ws.column_dimensions["A"].width = 110

    # Classic month/region/product sales table used for chart drills
    regions = ["Harare", "Bulawayo", "Mutare", "Gweru", "Masvingo"]
    products = ["Laptops", "Desktops", "Tablets", "Monitors", "Printers", "Keyboards"]
    import random
    random.seed(11)
    rows = [["Month", "Sales", "Region", "Product", "Units", "Cost"]]
    for m in range(1, 13):
        for r in regions:
            for p in products:
                if random.random() < 0.35:
                    continue
                units = random.randint(3, 90)
                price = random.uniform(60, 900)
                sales = round(units * price, 2)
                rows.append([f"2019-{m:02d}-01" if m <= 12 else "", sales, r, p, units,
                             round(sales * random.uniform(0.55, 0.82), 2)])
    add_sheet(wb, "Sales2019-2021", rows, note="Practice table for the visualisation labs.")

    simple = [["Month", "Sales", "Region", "Product", "Units", "Cost"]]
    for m, s, r, p, u, c in [
        ("January", 125000, "North", "Laptops", 410, 90000), ("February", 148000, "North", "Laptops", 445, 101000),
        ("March", 172000, "South", "Desktops", 388, 120000), ("April", 131000, "South", "Tablets", 512, 88000),
        ("May", 165000, "East", "Monitors", 640, 99000), ("June", 189000, "East", "Printers", 355, 121000),
        ("July", 143000, "West", "Keyboards", 980, 78000), ("August", 158000, "West", "Laptops", 402, 104000),
        ("September", 176000, "North", "Tablets", 588, 110000), ("October", 196000, "South", "Desktops", 470, 129000),
        ("November", 212000, "East", "Monitors", 712, 132000), ("December", 238000, "West", "Printers", 398, 148000),
    ]:
        simple.append([m, s, r, p, u, c])
    add_sheet(wb, "SimpleData", simple, note="Twelve rows. Perfect for learning which visual fits which question.")

    pl = [["AccountCode", "AccountName", "AccountType", "FY2024USD", "FY2025USD"]]
    for a in [
        ("4000", "Revenue - Manufactured Goods", "Revenue", 11800000, 9450000),
        ("4010", "Revenue - Trading / Resale", "Revenue", 1250000, 1080000),
        ("4020", "Revenue - Service and Maintenance", "Revenue", 460000, 385000),
        ("5000", "Cost of Sales - Materials", "Expense", 6250000, 5100000),
        ("5010", "Cost of Sales - Direct Labour", "Expense", 1880000, 1540000),
        ("5020", "Cost of Sales - Overheads", "Expense", 640000, 612000),
        ("6000", "Salaries and Wages", "Expense", 1240000, 1010000),
        ("6030", "Depreciation", "Expense", 84000, 63000),
        ("6050", "Fuel and Motor Vehicle Costs", "Expense", 310000, 268000),
        ("6060", "Electricity and Water", "Expense", 402000, 366000),
        ("6070", "Rent and Rates", "Expense", 288000, 216000),
        ("6090", "Professional and Consulting Fees", "Expense", 176000, 214000),
        ("6100", "Travel and Accommodation", "Expense", 142000, 118000),
        ("6150", "Bank Charges", "Expense", 46000, 39000),
        ("7000", "Interest Expense - Borrowings", "Expense", 96000, 74000),
        ("8000", "Income Tax Expense", "Expense", 310000, 246000),
    ]:
        pl.append([a[0], a[1], a[2], a[3], a[4]])
    add_sheet(wb, "PracticeFinance", pl, note="Your first DAX measures live here: Total Revenue, Total Cost, Gross Profit, Margin %.")

    messy = [["Sale ID", "Sale Date", "Customer", "Amount", "Region ", "Units"]]
    messy += [
        ["1", "01/03/2021", "Acme Corp", "1,250.00", "Harare", "12"],
        ["2", "2021-03-02", "acme corp", "R 2 500.50", "harare ", "30"],
        ["2", "2021-03-02", "acme corp", "R 2 500.50", "harare ", "30"],
        ["3", "03-03-2021", "Beta Ltd", "$3,100", "Bulawayo", "n/a"],
        ["4", "4 March 2021", "BETA LTD.", "2350", "Bulawayo", "8"],
        ["5", "05/03/2021", "Gamma (Pvt) Ltd", "4 800.75", "Mutare", "44"],
        ["6", "06/03/2021", "gamma pvt ltd", "5100", "Mutare", "51"],
        ["7", "07/03/2021", "Delta Traders", "6,250.00", "Gweru", "62"],
        ["8", "08/03/2021", "Delta Traders ", "0007500", "Gweru", "75"],
        ["9", "09/03/2021", "Epsilon Inc", "8,900", "Harare", "89"],
        ["10", "10/03/2021", "EPSILON INC", "9,100", "Harare", "91"],
        ["11", "11/03/2021", "Zeta Supplies", "10,250", "Masvingo", "102"],
        ["12", "2021/03/12", "Zeta Supplies", "11,300", "Masvingo", "113"],
        ["13", "13/03/2021", "Eta Works", "", "Masvingo", "121"],
        ["14", "", "Eta Works", "12,450", "", "124"],
    ]
    add_sheet(wb, "MessyData", messy, note=MESSY_NOTE)

    bva = [["CostCentre", "AccountName", "BudgetUSD", "ActualUSD"]]
    for cc, an, b, a in [
        ("CC200 Harare Plant", "Cost of Sales - Materials", 520000, 561000),
        ("CC200 Harare Plant", "Electricity and Water", 34000, 41500),
        ("CC210 Bulawayo Plant", "Cost of Sales - Direct Labour", 128000, 121000),
        ("CC300 Sales - Domestic", "Marketing and Advertising", 46000, 39800),
        ("CC310 Sales - Export", "Travel and Accommodation", 18000, 26400),
        ("CC110 Head Office Admin", "Professional and Consulting Fees", 22000, 47800),
        ("CC500 IT and Systems", "Telecommunications and Internet", 9500, 8800),
        ("CC400 Logistics", "Fuel and Motor Vehicle Costs", 31000, 36900),
    ]:
        bva.append([cc, an, b, a])
    add_sheet(wb, "BudgetVsActual", bva, note="Variance lab: waterfall, KPI and conditional formatting.")

    wb.save(os.path.join(XLSX, "PowerBI_Practice_Workbook.xlsx"))
    print("  PowerBI_Practice_Workbook.xlsx")


# --------------------------------------------------------------------------
# 3. Maxhub firm financials
# --------------------------------------------------------------------------
def build_maxhub():
    wb = Workbook()
    wb.remove(wb.active)
    ws = wb.create_sheet("READ ME")
    lines = [
        ("Maxhub Pvt Ltd - internal management pack", True),
        ("", False),
        ("This is YOUR firm's data. You are the analyst, the client is your own practice.", False),
        ("Use it in Capstone 4 (AI and advisory services) and the machine-learning module.", False),
        ("", False),
        ("ServiceLineFinancials - monthly revenue, cost and profit by service line", False),
        ("BillableHours        - consultant utilisation and realisation", False),
        ("Pipeline             - business development opportunities", False),
        ("ClientChurn          - client-year features with a 'Stayed' label for a classification model", False),
        ("Engagements          - engagement-level fee, hours and write-off detail", False),
    ]
    for i, (t, b) in enumerate(lines, start=1):
        ws.cell(row=i, column=1, value=t).font = Font(bold=b, size=13 if i == 1 else 11,
                                                      color="1F4E79" if b else "333333")
    ws.column_dimensions["A"].width = 100

    for f, note, w in [
        ("maxhub_service_line_financials.csv", "Monthly P&L by service line", 22),
        ("maxhub_billable_hours.csv", "Consultant utilisation", 18),
        ("maxhub_pipeline.csv", "Business development pipeline", 20),
        ("maxhub_client_churn.csv", "Client retention modelling dataset", 18),
        ("MaxhubEngagements.csv", "Engagement profitability", 22),
    ]:
        add_sheet(wb, f.replace(".csv", "").replace("maxhub_", "").title()[:31], read_csv(f), note=note)
    wb.save(os.path.join(XLSX, "Maxhub_Firm_Financials.xlsx"))
    print("  Maxhub_Firm_Financials.xlsx")


if __name__ == "__main__":
    print("\nBuilding Excel workbooks")
    build_main()
    build_practice()
    build_maxhub()
    print("Done. Files in data/xlsx/\n")
