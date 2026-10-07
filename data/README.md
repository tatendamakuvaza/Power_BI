# The practice data

Two fictional businesses, both accounting-realistic, both generated deterministically so every number in
the course can be reproduced.

| Business | What it is | Files | Used in |
|---|---|---|---|
| **Mhondoro Manufacturing (Pvt) Ltd** | Harare/Bulawayo light manufacturer; 1 Jan 2024 – 30 Sep 2025; USD; 15% VAT; **seven fraud schemes hidden in the ledger** | `data/raw/*.csv`, `data/xlsx/Mhondoro_Accounting_Data.xlsx` | Modules 1–10, Capstones 1–3 |
| **Maxhub Pvt Ltd** | Your own firm: engagements, utilisation, pipeline, churn | `data/raw/maxhub_*.csv`, `data/xlsx/Maxhub_Firm_Financials.xlsx` | Module 11, Capstone 4 |

> ⚠️ **`data/raw/InjectionLog.csv` is the answer key.** Do not open it until you have completed Lab 09
> and written your own evidence register. Looking early destroys the central learning exercise.

---

## 1. Load order (do this once, properly)

1. **Dictionaries first:** `data/dictionary/DataDictionary.csv` — 267 fields, every column of every
   table explained (source, meaning, how to use it, quirks).
2. **Dimensions:** `DimAccount`, `DimDate`, `DimCostCentre`, `DimUser`, `DimVendor`, `DimCustomer`,
   `DimEmployee`, `DimFXRate`.
3. **Facts:** `FactGLJournal` (the core), then the sub-ledgers and supporting facts.
4. **The answer key last.**

## 2. Row counts (know these — they are your reconciliation targets)

| Table | Rows | Grain |
|---|---|---|
| `FactGLJournal` | **13,929** | One row per ledger line (5,504 journals) |
| `DimAccount` | 71 | One row per account; 64 are actually used |
| `DimDate` | 1,461 | One row per calendar day (2024-01-01 → 2027-12-31) |
| `DimCostCentre` | 9 | One per cost centre |
| `DimUser` | 12 | One per system user |
| `DimVendor` | 26 | One per supplier (4 are employee-linked ghost vendors) |
| `DimCustomer` | 18 | One per customer |
| `DimEmployee` | 63 | One per employee |
| `DimFXRate` | 84 | Month-end rates for 7 currencies |
| `FactTrialBalance` | 1,323 | Account × month |
| `FactARAgeing` | 420 | Customer × ageing bucket |
| `FactAPInvoices` | 520 | One per supplier invoice |
| `FactBankTransactions` | 1,400 | One per bank statement line |
| `FactExpenseClaims` | 650 | One per claim |
| `FactSalesOrders` | 900 | One per sales order line |
| `FactBudget` | 1,299 | Account × cost centre × month |
| `FactFixedAssets` | 120 | One per asset |
| `MaxhubEngagements.csv` | 160 | One per engagement |
| `InjectionLog.csv` | 171 | One per **injected** journal (the answer key) |

## 3. Control totals (your model must reproduce these)

| Check | Value |
|---|---|
| Total debits | **$122,878,886.54** |
| Total credits | **$122,878,886.54** |
| Difference | **0.00** |
| Flagged forensic value | **$1,945,536.55** across 171 journals |
| Suspense account (1990) | **$51,058.87** |
| FY2024 result | **$447,052 profit** |
| FY2025 result (9 months) | **−$61,867 (small loss)** |
| Balance sheet check A − (L + E) | **−61,867 = the FY2025 result** |

## 4. What is deliberately wrong with the data

This is the point of the dataset: real clients' data is dirty, and your job is to *disclose* the dirt,
not hide it.

| Issue | Count | Where to look |
|---|---|---|
| Unreconciled bank items | 129 of 1,400 ($1,884,271; 27 over 90 days) | `FactBankTransactions` |
| AP invoices failing the three-way match | 168 of 520 | `FactAPInvoices` |
| AP invoices with no purchase order | 109 of 520 | `FactAPInvoices` |
| Suspected duplicate AP invoices | 18 of 520 | `FactAPInvoices` (`DuplicateSuspected`) |
| Expense claims without receipts | 81 of 650 | `FactExpenseClaims` |
| Disputed customer accounts | 11 of 420 | `FactARAgeing` |
| Unallocated amounts in suspense | $51,058.87 | GL account 1990 |

## 5. The seven hidden fraud schemes (do not read this until Lab 09 is finished)

<details>
<summary>Click only after you have written your own evidence register</summary>

| Code | What it is | Injected value | Pattern to spot |
|---|---|---|---|
| `DUPLICATE-PAYMENT` | The same invoice paid twice, 21 pairs | $368,023.48 (overpayment ≈ $184,011.74) | Identical amount and vendor within a few days |
| `GHOST-VENDOR` | 4 suppliers linked to employees (SUP-771 to SUP-774) | $445,568.39 injected; $2,773,799.20 paid in total | Vendor created shortly before first payment, single preparer, bank details matching an employee |
| `ROUND-NUMBER-THRESHOLD` | Payments deliberately just below the $5,000 PO and $10,000 approval limits ($4,985–$4,995, $9,750–$9,900) | $207,720.00 | Round amounts clustering under a threshold |
| `SOD-RARE-COMBO` | AP clerk (USR-002) posting revenue credit notes | $279,600.00 | A user posting to accounts outside their normal role |
| `SPLIT-PURCHASE` | One purchase split into two invoices to avoid approval, 21 pairs | $223,924.68 | Same vendor and day, two amounts just under the limit |
| `UNREVERSED-ACCRUAL` | Accruals posted with no reversal | $14,400.00 | Debit with no matching reversal in the following period |
| `WEEKEND-AFTERHOURS` | Manual journals posted at 02:00–04:00 and on weekends (USR-012), credited to suspense | $406,300.00 | Timestamps outside business hours with a suspense counterpart |

**Total: $1,945,536.55 across 171 flagged journals.**

</details>

## 6. Files, formats and regeneration

| Folder | Contents |
|---|---|
| `data/raw/` | 17 Mhondoro CSVs + 4 Maxhub CSVs + `InjectionLog.csv` |
| `data/xlsx/` | `Mhondoro_Accounting_Data.xlsx` (READ ME + 18 tables; **`InjectionLog` is a hidden sheet** — right-click a tab ▸ Unhide only after Lab 09), `PowerBI_Practice_Workbook.xlsx`, `Maxhub_Firm_Financials.xlsx` |
| `data/dictionary/` | `DataDictionary.csv` — 267 fields documented |
| `data/practice/` | Small teaching extracts, e.g. `VendorName_Matching_Practice.csv` for the fuzzy-matching exercise |
| `data/scored/` | Model output: `maxhub_client_churn_scored.csv`, `vendor_match_candidates.csv` |

Regenerate (the seed is fixed, so you get identical data):

```bash
python3 scripts/generate_data.py          # Mhondoro (stdlib only)
python3 scripts/generate_maxhub_data.py   # Maxhub firm data
python3 scripts/build_workbooks.py        # Excel workbooks (needs openpyxl)
python3 scripts/build_dictionary.py       # data dictionary
python3 scripts/verify_data.py            # control checks - must print "all control checks passed"
```

**Warning:** if you change anything in the generator, every number in this repository changes with it.
Re-run `scripts/verify_data.py` and update the lab expected-results tables if you do.

## 7. Ethics of using generated data

- Never present generated data as a real client's data, in a portfolio or a pitch. Label it
  "simulated engagement data".
- The fraud schemes are modelled on real published patterns (duplicate payments, ghost vendors,
  threshold avoidance, journal-entry manipulation). Studying them is legitimate professional training.
- When you do work on real client data, the rules in [`../reference/Cheat_Sheet.md`](../reference/Cheat_Sheet.md) §7
  apply from the first minute: hash the original, work on a copy, document every decision.
