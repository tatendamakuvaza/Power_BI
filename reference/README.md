# reference/ — lookup material, not reading material

## Detailed teaching notes

[Download the teaching-notes PDF](../Maxhub_PowerBI_Modules_01_and_02_Detailed_Teaching_Notes.pdf).
Despite the requested combined filename, this edition contains **Module 2 only**; Module 1 was not supplied.
The editable [Module 2 source](Maxhub_Module_02_Detailed_Teaching_Notes.md) preserves the supplied notes.
To rebuild the PDF, install `reportlab` and run `python scripts/build_teaching_notes_pdf.py` from the repository root
(with DejaVu fonts installed; see the script docstring).

## Lookup material

| File | Use it for |
|---|---|
| [`Cheat_Sheet.md`](Cheat_Sheet.md) | One-page summary: pipeline, DAX patterns, control checks, design rules, the numbers to memorise |
| [`Glossary_Accounting_and_PowerBI.md`](Glossary_Accounting_and_PowerBI.md) | Every term in the course in both languages — accounting and Power BI |
| [`Common_Errors_and_Fixes.md`](Common_Errors_and_Fixes.md) | The error you are looking at right now, and its cause |
| [`Career_and_Portfolio_Guide.md`](Career_and_Portfolio_Guide.md) | Converting the skill into a role, a portfolio and a practice |

**The three-minute diagnostic** (from `Common_Errors_and_Fixes.md`) — when a number is wrong, check in
this order: filter context → relationship path → sign convention → grain → data types → reconciliation.

**The numbers to memorise** (from `Cheat_Sheet.md`): 13,929 ledger lines; debits = credits
$122,878,886.54; FY2024 profit $447,052; FY2025 loss $61,867; AR $3,790,174; AP $2,373,621; cash
$792,548; suspense $51,058.87; flagged forensic value $1,945,536.55 across 171 journals.

If your model does not reproduce those, you have a bug — not a finding.
