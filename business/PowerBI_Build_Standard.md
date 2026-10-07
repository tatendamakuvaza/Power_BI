# Maxhub Power BI Build Standard

Every `.pbix` that leaves Maxhub is built to this standard. It exists so that a different consultant can
pick up any client file and understand it in ten minutes, and so that quality control is a checklist
rather than an opinion.

---

## 1. Naming conventions

| Object | Convention | Example |
|---|---|---|
| Fact tables | `Fact` + business object | `FactGLJournal`, `FactAPInvoices` |
| Dimension tables | `Dim` + business object | `DimVendor`, `DimCostCentre` |
| Measure home table | `_Measures` (underscore sorts it to the top) | `_Measures` |
| Supporting/technical tables | `Ref` or `Map` | `RefApprovalLimits`, `MapFSLines` |
| Staging queries (not loaded) | `stg_` prefix | `stg_GL_Raw` |
| Measures | Title Case, no prefixes, no abbreviations | `Gross Margin %`, not `GM%` or `M_GM` |
| Columns | Title Case, business meaning | `PostingDate`, `AmountSigned` |
| Display folders | Numbered | `01 Base`, `02 P&L`, `03 Balance Sheet` |
| Hidden objects | Keys and technical columns hidden in report view | `AccountCode` hidden, `AccountName` visible |
| Report pages | Audience-oriented | `Executive`, `Financials`, `Forensic`, `Data Quality` |

## 2. Data layer (Power Query)

- [ ] All paths and periods come from **parameters** or a configuration table — nothing hard-coded.
- [ ] Codes are **text**; dates are date; amounts are decimal.
- [ ] Staging queries have **Enable load = off**, and are never referenced by the report.
- [ ] Every cleaning step is renamed to say *why* it exists.
- [ ] Data-quality flags are **added as columns**, never silently fixed (dup flags, null counts).
- [ ] The source extract is retained in its original form and a hash recorded in the working papers.
- [ ] Refresh runs in under 5 minutes on the client's machine.

## 3. Model

- [ ] Star schema: dimensions filter facts; one-to-many; single direction by default.
- [ ] One date table, **marked as a date table**, auto date/time off.
- [ ] No calculated columns on large fact tables unless unavoidable and documented.
- [ ] No bidirectional relationships without a documented reason.
- [ ] All keys are text on both sides of every relationship; no orphan rows.
- [ ] Every measure and every table has a **description**.
- [ ] Measures organised in the `_Measures` table with display folders.
- [ ] Format strings set in the model (`$#,##0.00`, `0.0%`, `#,##0`), zero shown as `-` where appropriate.

## 4. Report

- [ ] Every visual has a **sentence title** containing a number, plus a source/period footnote.
- [ ] One question per visual; no dual axes; no decorative colour.
- [ ] Theme imported from [`../assets/PowerBI_Course_Theme.json`](../assets/PowerBI_Course_Theme.json)
      (or the client's brand variant).
- [ ] Slicers synchronised across pages; a "Reset filters" bookmark exists.
- [ ] Drillthrough to transaction detail exists and is tested.
- [ ] An "About this report" page: purpose, source, refresh frequency, definitions, contacts.
- [ ] A hidden **Data Quality** page: debits vs credits, BS check, orphan keys, unbalanced journals.
- [ ] Alt text on visuals; font ≥ 10 pt; not colour-dependent.
- [ ] Mobile layout checked for any page an executive will open on a phone.

## 5. Reconciliation (non-negotiable)

Every deliverable proves itself before it is issued:

| Check | Target |
|---|---|
| Total debits = total credits | 0.00 difference |
| Model total = client's trial balance | 0.00 difference |
| Balance sheet check (A − L − E − current result) | 0.00 |
| P&L result = movement in retained earnings | ties |
| Orphan keys in every relationship | 0 |
| Journals out of balance | 0 |
| Ageing sub-ledger = GL control account | ties |

If a check cannot be made to tie, the reason is documented in the report — never silently ignored.

## 6. Documentation pack (delivered with every build)

1. **Model documentation** — a one-page diagram, table list with grain, measure list with definitions.
2. **Methodology note** — sign conventions, ratio definitions, exclusions, known limitations.
3. **Data dictionary** — table, column, description, source (use `data/dictionary/DataDictionary.csv`
   as the template).
4. **User guide** — one page: how to use slicers, drill through, refresh, who to call.
5. **Handover** — recorded walkthrough, and the `.pbix` handed over. **The client owns their model.**

## 7. Quality control before issue

The reviewer (a different person from the builder) must:

- [ ] Re-perform one calculation end-to-end from the raw data.
- [ ] Tie every headline number to the client's records.
- [ ] Open every page and read every title as the client would.
- [ ] Check that no personal or confidential information is exposed where it should not be.
- [ ] Confirm the documentation pack is complete and versioned.
- [ ] Sign and date the QC checklist (kept in the engagement file).

## 8. Versioning and file management

- File name: `Client_ReportName_vX.Y.pbix` (e.g. `Mhondoro_ReportingPack_v1.2.pbix`).
- A change log in the working papers: version, date, author, change, reason.
- Client data is stored per client, access-controlled, and deleted per the engagement letter.
- Never email a `.pbix` containing personal data outside agreed secure channels.

## 9. Performance budgets (on a client laptop, not yours)

| Item | Budget |
|---|---|
| Refresh | < 5 minutes |
| Page load | < 3 seconds |
| Any single visual | < 2 seconds |
| Model size | < 300 MB unless justified and agreed with the client |

If a visual exceeds the budget, use Performance Analyzer, then fix the model (avoid `FILTER` over facts,
reduce columns, aggregate earlier) rather than hiding the problem.
