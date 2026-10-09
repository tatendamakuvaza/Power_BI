# Tatenda Makuvaza — downloadable Power BI learning pack

The requested folder is delivered as a ZIP containing **exactly two documents**:

- [Download the complete ZIP](../deliverables/Tatenda_Makuvaza_Power_BI_Learning_Pack.zip)
- [Read the personalised PDF workbook](../deliverables/Tatenda_Makuvaza_Power_BI/Tatenda_Makuvaza_Power_BI_Workbook.pdf)
- [Get the single practice CSV](../deliverables/Tatenda_Makuvaza_Power_BI/Tatenda_Makuvaza_Practice_Data.csv)

## Contents

The 66-page workbook follows the repository's 12-module syllabus. It includes
step-by-step labs, DAX and Power Query examples, expected visual specifications,
computed controls, monthly answers, four capstones, practical exams, a field
reference, and the complete 171-journal synthetic investigation answer key.

The UTF-8 CSV has **23,416 records, 213 columns and 22 logical populations**.
`RecordType` distinguishes tables; `RecordID` is a unique transport key. Blank
fields outside a row's population are intentional. Module 02 explains how to
split the single file into properly typed model tables. Never aggregate the
unsplit bundle as a single fact table.

Source records come from `data/raw/`. The GL's `AnomalyLabel` and separate
`InjectionLog` are withheld from the CSV; the latter supplies the PDF answer key.
All other source fields are preserved. Financial controls are independently
computed, not copied from repository prose. The workbook documents source
limitations and distinguishes synthetic subledger populations from the
GL-derived trial balance.

## Rebuild and verify

```bash
python3 -m venv .venv
.venv/bin/pip install -r learning_pack/requirements.txt
.venv/bin/python scripts/build_tatenda_pack.py
.venv/bin/python scripts/verify_tatenda_pack.py
```

Edit `workbook.md` for the narrative. The builder expands `@...` directives into
computed tables and a reference chart, creates PDF bookmarks, and packages only
the CSV and PDF. The build does not modify the original datasets.

Verification checks source-field fidelity, unique bundle keys, row counts,
debit/credit equality, every journal's balance, every account/month trial-balance
reconciliation, sales and asset arithmetic, expected PDF sections and answer-key
IDs, the published Python baseline exercise, PDF text boundaries, and ZIP
integrity. Core financial logic has been checked with Python; a Windows Power BI
Desktop or Service session was **not** available to execute DAX, inspect native
visuals or test publishing/tenant security. The workbook explicitly asks the
learner to perform those acceptance tests.

Generated deliverables are intentionally retained because they are the user's
requested downloadable documents; temporary renders and build environments are
not included in the ZIP.
