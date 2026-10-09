# Maxhub Pvt Ltd — Power BI for Forensic Accounting, Data Analytics, ML & AI Advisory

A complete, self-contained learning course built for **Maxhub Pvt Ltd's** consulting practice.
You learn Power BI on **real accounting data** (a fictional audit client with genuine fraud
patterns hidden inside it), then you learn how to sell, scope, deliver and price that skill as a
professional service.

> **Who this is for:** an accountant or auditor who wants to move into forensic accounting,
> data analytics, machine learning/AI services and advisory — using Power BI as the delivery
> platform, not as a hobby.

---

## 1. Start here

**Tatenda Makuvaza's revised practice pack:** [Download the ZIP](deliverables/Tatenda_Makuvaza_Power_BI_Learning_Pack.zip) — 22 separate CSV tables (23,416 rows in total) and a 69-page PDF rewritten in plain, beginner-friendly language. Includes all 12 modules, step-by-step tasks, chart instructions and checked answers. See [pack details and rebuild instructions](learning_pack/README.md).

| If you want to… | Open this |
|---|---|
| Know what you will be able to do | [`course/Course_Syllabus.md`](course/Course_Syllabus.md) |
| Install Power BI today | [`powerbi/Windows_Install_Guide.md`](powerbi/Windows_Install_Guide.md) |
| Learn on a Mac | [`powerbi/macOS_Options_Guide.md`](powerbi/macOS_Options_Guide.md) |
| Understand the data you will use | [`data/README.md`](data/README.md) |
| Preview the course on one page | [`course/Course_Preview.html`](course/Course_Preview.html) |
| Track your progress | [`course/Progress_Tracker.csv`](course/Progress_Tracker.csv) |
| See how the files fit together | Section 5 of this page |
| Check the data pipeline is healthy | run `python3 scripts/run_all.py` (see [`scripts/README.md`](scripts/README.md)) |

**Rule one:** every module ends with a lab. Do the lab before moving on. Reading about
CALCULATE is not the same as writing it.

---

## 2. The 12 modules

| # | Module | You will be able to… |
|---|---|---|
| 1 | [Getting Started with Power BI](modules/01_Getting_Started_with_PowerBI.md) | Install, navigate Desktop, build and publish your first report |
| 2 | [Connecting & Shaping Data (Power Query)](modules/02_Connecting_and_Shaping_Data_PowerQuery.md) | Import accounting extracts and clean them properly, every time |
| 3 | [Data Modelling & the Star Schema](modules/03_Data_Modelling_Star_Schema.md) | Design a chart-of-accounts model that scales from 10k to 10m rows |
| 4 | [DAX Fundamentals](modules/04_DAX_Fundamentals.md) | Write measures confidently, not by copying from the internet |
| 5 | [Advanced DAX: Time, Balance & Context](modules/05_Advanced_DAX_Time_Balance_Context.md) | YTD/MTD, opening & closing balances, accountant-grade calculations |
| 6 | [Financial Statement Design](modules/06_Financial_Statement_Design.md) | Build a live P&L, balance sheet and cash flow in Power BI |
| 7 | [Visualisation & Dashboard Design](modules/07_Visualisation_and_Dashboard_Design.md) | Build dashboards a CFO or a court will actually read |
| 8 | [Analytics, KPIs & Discovery](modules/08_Analytics_KPIs_and_Discovery.md) | Variance, margin, DSO/DPO, trend and exception analysis |
| 9 | [Forensic Accounting Analytics](modules/09_Forensic_Accounting_Analytics.md) | Benford, duplicates, ghost vendors, threshold tests, JE risk scoring |
| 10 | [Fraud Investigation Project](modules/10_Fraud_Investigation_Project.md) | Run an investigation end-to-end on the Mhondoro data and write it up |
| 11 | [Machine Learning & AI in Power BI](modules/11_Machine_Learning_and_AI_in_PowerBI.md) | AutoML, Key Influencers, anomaly detection, forecasting, Copilot |
| 12 | [The Advisory Practice](modules/12_Advisory_Practice_and_Consulting.md) | Package, price, propose and deliver these services through Maxhub |

Supporting material:

- **Labs:** [`labs/Lab_Index.md`](labs/Lab_Index.md) — step-by-step exercises with expected results
- **DAX library:** [`dax/Core_Measures_Library.dax`](dax/Core_Measures_Library.dax) and friends
- **Power Query library:** [`powerquery/M_Query_Library.pqm`](powerquery/M_Query_Library.pqm)
- **Capstones:** [`capstones/`](capstones/) — four client-ready portfolio projects
- **Business templates:** [`business/`](business/) — proposals, engagement letters, build standard
- **Assessments:** [`assessments/`](assessments/) — quizzes, practical exams, rubrics
- **Reference:** [`reference/`](reference/) — glossary, cheat sheet, common errors, career guide

---

## 3. Your practice data: Mhondoro Manufacturing (Pvt) Ltd

A Harare/Bulawayo light manufacturer. Two financial years of data
(1 Jan 2024 – 30 Sep 2025), USD functional currency, 15% VAT, and **seven fraud schemes
deliberately hidden in the ledger** for you to find in Modules 9–10.

| File | What it is |
|---|---|
| `data/xlsx/Mhondoro_Accounting_Data.xlsx` | The full data warehouse — 18 tables ready for Power BI (`InjectionLog` is a hidden sheet until Module 10) |
| `data/xlsx/PowerBI_Practice_Workbook.xlsx` | Simple exercise tables for the visualisation and cleaning labs |
| `data/xlsx/Maxhub_Firm_Financials.xlsx` | Your own firm's numbers — advisory, pipeline, utilisation, churn model |
| `data/raw/*.csv` | The same data as CSV, for the folder-and-CSV import exercises |
| `data/dictionary/DataDictionary.csv` | 267 fields documented: what each column means and how to use it |
| `data/raw/InjectionLog.csv` | **The answer key. Do not open until Module 10.** |

---

## 4. The four capstones (this is what you show clients)

| Capstone | Deliverable | Sellable as |
|---|---|---|
| [1 — Forensic Investigation](capstones/Capstone_1_Forensic_Investigation.md) | Fraud findings pack, quantified loss, evidence register | Forensic investigation engagement |
| [2 — Financial Reporting Pack](capstones/Capstone_2_Financial_Reporting_Pack.md) | Live P&L, BS, cash flow, variance commentary | CFO / management reporting retainer |
| [3 — Data Analytics Engagement](capstones/Capstone_3_Data_Analytics_Engagement.md) | Procurement, AR and cash analytics suite | Internal audit & data analytics engagement |
| [4 — AI & Advisory Service](capstones/Capstone_4_AI_Advisory_Service.md) | Churn model, forecasting, AI-assisted reporting, service blueprint | Machine learning / advisory retainer |

---

## 5. How the repository is organised

```
Power_BI/
├── README.md                  <- you are here
├── course/                    syllabus, instructor guide, progress tracker
├── modules/                   01-12, the teaching material
├── labs/                      hands-on exercises with expected results
├── dax/                       copy-paste DAX libraries + report theme
├── powerquery/                Power Query (M) library and notes
├── powerbi/                   install/flighting guides (Windows and Mac)
├── capstones/                 four portfolio projects
├── business/                  Maxhub templates: proposals, engagement letters, standards
├── assessments/               quizzes, practical exams, self-assessment
├── reference/                 glossary, cheat sheet, errors, career guide
├── data/                      practice data warehouse (xlsx, raw csv, dictionary)
├── scripts/                   generators, verifier, churn model, vendor matcher (see scripts/README.md)
├── .github/workflows/         CI: regenerates the data and proves the results still tie
└── assets/                    report theme and brand guidelines
```

Everything is plain text (Markdown, DAX, M, Python) so you can edit it, extend it and, when
ready, re-brand it for a client. Regenerate the data at any time:

```bash
python3 scripts/generate_data.py           # Mhondoro client data (stdlib only)
python3 scripts/generate_maxhub_data.py    # Maxhub firm data
python3 scripts/build_workbooks.py         # Excel workbooks  (needs openpyxl)
python3 scripts/build_dictionary.py        # data dictionary
python3 scripts/verify_data.py             # control-total checks
python3 scripts/run_all.py                 # or: everything above, in the right order
```

> The data is deterministic **and reproducible**: the same seed always produces the same transactions
> and the workbooks rebuild to identical bytes, so your numbers will match the expected results printed
> in the labs. CI (`.github/workflows/verify-data.yml`) proves this on every push.

---

## 6. Tools you need

| Tool | Cost | Notes |
|---|---|---|
| Power BI Desktop (Windows) | Free | The main tool. Install from the Microsoft Store or powerbi.microsoft.com |
| Power BI Desktop — Mac users | Free | Use a Windows VM / Parallels / Windows 365, or build in the Service. See [`powerbi/macOS_Options_Guide.md`](powerbi/macOS_Options_Guide.md) |
| Power BI Service account | Free (Fabric free trial for sharing) | Needed for publishing, dashboards, apps and Copilot |
| Excel | You have it | Used to open the practice workbooks |
| Python 3 | Free | Only for regenerating data and the optional ML labs |
| Tabular Editor / DAX Studio | Free | Optional but recommended from Module 5 onward |

A 5-day-a-week learner finishes the 12 modules in about **8 weeks**. A weekend learner,
about **16 weeks**. The schedule for both is in the syllabus.

---

## 7. Ethics and professional standards (read once, apply always)

This course teaches techniques used in fraud investigations. Power BI is a tool; the
professional standards are what make the output admissible and defensible.

- Work only on data you are authorised to analyse, under an engagement letter or written instruction.
- Preserve evidence: keep the original extract, hash it if it may be used in proceedings, and never
  edit the source file. Analyse a copy.
- Document every step so a third party can reproduce your result — that is what a working paper is.
- Report facts and exceptions, not accusations. Findings are for management and, where relevant, counsel.
- Mind independence: an analyst who both keeps the books and audits them creates the very
  segregation-of-duties failure this course teaches you to find.

Module 12 covers the Maxhub professional standards, quality control checklist and engagement files.

---

*Maxhub Pvt Ltd — Forensic Accounting | Data Analytics | Machine Learning & AI | Advisory Services*

*All data in this repository is fictional and generated for training purposes.*
