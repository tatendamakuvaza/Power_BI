# Tatenda Makuvaza — Power BI learning pack, edition 2

## Download

- [Complete ZIP folder](../deliverables/Tatenda_Makuvaza_Power_BI_Learning_Pack.zip)
- [Beginner-friendly PDF workbook](../deliverables/Tatenda_Makuvaza_Power_BI/Tatenda_Makuvaza_Power_BI_Workbook.pdf)
- [Browse the 22 separate CSV files](../deliverables/Tatenda_Makuvaza_Power_BI/CSV_Tables)

The revised ZIP contains **22 CSV files and one 69-page PDF**. Each CSV holds
one record type, with only that table's own columns. There is no mixed master
CSV and no need to filter a `RecordType` column. The original combined file has
been removed from the current delivery.

```text
Tatenda_Makuvaza_Power_BI/
  Tatenda_Makuvaza_Power_BI_Workbook.pdf
  CSV_Tables/
    DimAccount.csv
    DimCustomer.csv
    FactGLJournal.csv
    FactSalesOrders.csv
    ... (22 separate tables in total)
```

Start with **Module 01** and **CSV_Tables/FactGLJournal.csv**. Add the other files
as the lessons call for them. In Power BI, use **Get data > Text/CSV** for each
file. Do not use Combine Files on the whole folder: these tables have different
columns and purposes. CSV files cannot have Excel-style worksheet tabs; the
requested record types are separate files instead.

## What changed

- One separate UTF-8 CSV per table: **23,416 rows across 22 files**.
- The PDF was rewritten in plain, beginner-friendly language, not just retitled.
- Technical words are explained before use; file names and formula names stay
  unchanged so the learner can find them in Power BI.
- All twelve modules, formulas, practical steps, expected charts, answer totals,
  four final projects, assessments and investigation answers remain covered.
- Import instructions now refer to individual CSV files; no bundle-splitting
  steps or mixed-table routing columns remain.

The source data is fictional. It comes from `data/raw/`. The GL's `AnomalyLabel`
column and `InjectionLog` are intentionally withheld from the CSVs so the
investigation exercises are not spoiled. The PDF includes the full answer key.
All other source fields and values are preserved. Separate practice subledgers
are not assumed to reconcile to the main ledger; the PDF explains this in plain
language.

## Rebuild and verify

```bash
python3 -m venv .venv
.venv/bin/pip install -r learning_pack/requirements.txt
.venv/bin/python scripts/build_tatenda_pack.py
.venv/bin/python scripts/verify_tatenda_pack.py
```

Edit `workbook.md` for the lesson text. The builder fills in computed answer
tables, a reference chart, PDF bookmarks and per-file fingerprints, then writes
the ZIP. It does not modify `data/raw/`.

Validation checks all 22 table schemas and source values, row counts, the
absence of the old combined file, all journal balances, account/month trial
balance agreement, sales and asset arithmetic, the fixed client-prediction
examples, PDF sections, every planted journal ID, file fingerprints, PDF text
boundaries and all 23 ZIP members.

The amounts and examples are checked in Python. Windows Power BI Desktop and
Service permissions were not available to execute the actual DAX, inspect native
visuals or test online sharing. The PDF tells the learner to carry out those
checks in their own report. Generated practice files and the PDF are retained
because they are the requested download; the virtual environment and temporary
page images are not delivered.
