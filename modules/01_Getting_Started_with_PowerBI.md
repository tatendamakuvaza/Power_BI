# Module 1 — Getting Started with Power BI

**Time:** 4 hours · **Lab:** [Lab 01](../labs/Lab_Index.md#lab-01--first-report-in-40-minutes) · **Next:** [Module 2](02_Connecting_and_Shaping_Data_PowerQuery.md)

> You will finish this module with a published report built from your own practice data. It will
> not be good. That is the point — you need to see the whole pipeline once before the details land.

---

## 1.1 What Power BI actually is (in accounting language)

Think of Power BI as a **three-stage close process for data**:

| Stage | Power BI name | Accounting analogy |
|---|---|---|
| Capture | **Power Query** | Bookkeeping — get the source documents, clean, code, post |
| Organise | **Data model** | The ledger and trial balance structure — one place where everything ties |
| Report | **Visuals / reports** | The management pack and the financial statements |

Four components you will hear about:

| Component | What it is | Do you need it now? |
|---|---|---|
| **Power BI Desktop** | The Windows app where you build. Free. | Yes — this is where 95% of your work happens |
| **Power BI Service** (`app.powerbi.com`) | The cloud where you publish, share and schedule refresh | Yes — a free account is enough to start |
| **Power BI Mobile** | Phone/tablet app for consuming reports | Later, for clients |
| **Power BI Report Server** | On-premises server for clients who cannot use the cloud | For bank/state clients later |

**Fabric** is Microsoft's newer name for the cloud platform that now hosts Power BI; you do not need
to learn it to do this course. When a client asks "is it Power BI or Fabric?", the honest answer is
"Power BI is the reporting layer inside Fabric; the licence you need depends on how much data and
governance you want in the cloud."

---

## 1.2 Install

Follow [`../powerbi/Windows_Install_Guide.md`](../powerbi/Windows_Install_Guide.md). Summary:

1. Install **Power BI Desktop** — Microsoft Store version is easiest to keep updated
   (`ms-windows-store://pdp?productId=9NTXR16HNW1T`) or download from <https://powerbi.microsoft.com/desktop/>.
2. Create a free account, or use a work/school ("organisational") account. Personal Gmail/Yahoo
   accounts work for learning but cannot be licensed for sharing later; use a work account if you have one.
3. Sign in: **File ▸ Account settings** (top-right avatar ▸ Sign in).
4. Set your options once, properly:
   - **File ▸ Options ▸ Global ▸ Regional settings** → English (United Kingdom or Zimbabwe context).
     This controls how dates and numbers are interpreted at import. Set it **before** you import anything.
   - **File ▸ Options ▸ Global ▸ Data Load** → *Auto date/time* **OFF** (Microsoft calls this
     "Auto date/time for new files"). It silently creates a date table per column; it bloats your model
     and confuses auditors. You will build a proper date table in Module 3.
   - **File ▸ Options ▸ Global ▸ Preview features** → leave defaults except *Power BI Report Server* if needed.
5. Turn on the **file view ribbon**: **View ▸ Customise the ribbon** and make sure *Model view* and
   *DAX query view* are visible — DAX query view is the closest thing to a live ledger query tool you have.

---

## 1.3 The interface, mapped to an accountant's workflow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Ribbon  (Home / Insert / Modeling / View / Optimize / Help)                  │
├───────────────┬──────────────────────────────────────────────────────────────┤
│ VIEWS (left)  │                 CANVAS (report page)                        │
│  ▣ Report     │                                                              │
│  ▤ Table      │                                                              │
│  ⧉ Model      │                                                              │
│  <> DAX query │                                                              │
├───────────────┴──────────────────────────────────────────────────────────────┤
│ Visualizations │ Fields (tables & columns) │ Filters (visual/page/all)       │
└──────────────────────────────────────────────────────────────────────────────┘
```

| View | Use it for |
|---|---|
| **Report** | Building pages, visuals, bookmarks, drillthrough |
| **Table** | Inspecting imported data column by column (your "browse" screen) |
| **Model** | Relationships, cardinality, filter direction — see Module 3 |
| **DAX query view** | Running EVALUATE queries against your model — the tool auditors love |

---

## 1.4 Your first import (10 minutes)

1. **Home ▸ Get Data ▸ Excel workbook** → choose `data/xlsx/PowerBI_Practice_Workbook.xlsx`
2. In Navigator, tick **SimpleData** only → **Transform Data** (not *Load*).
3. In Power Query you will see 12 rows. Look at the **Applied Steps** pane on the right — this is
   the audit trail of every change you make. Nothing is destructive; you can always go back.
4. Click **Close & Apply**. You now have a table in your model.
5. Build the mandatory four visuals:

| Visual | Field setup | Question it answers |
|---|---|---|
| Line chart | Axis `Month`, Values `Sales` | Is the trend up? |
| Clustered column chart | Axis `Region`, Values `Sales` | Where is the revenue? |
| Matrix | Rows `Region`, Columns `Product`, Values `Sales` | The classic cross-tab |
| Card | `Sales`, `Units` | Headline numbers |

6. Add a slicer (**Visualisations ▸ Slicer**) on `Month` and a **Pie chart** of `Sales` by `Product`.
   You have now built the same visual vocabulary you will use on every engagement.

---

## 1.5 Save, publish, and know the difference between the two objects

- **File ▸ Save as** → `Maxhub_Lab01.pbix`. A `.pbix` is a single file containing data model +
  report + Power Query. This is your deliverable to clients.
- **Home ▸ Publish** → choose *My workspace*. This moves a copy to the cloud.
- In the Service (`app.powerbi.com`):
  - A **report** is the thing with visuals.
  - A **dashboard** is a canvas of pinned tiles from one or more reports. Clients who "want a dashboard"
    often mean the report; clarify early.
  - An **app** is the packaged bundle of reports + dashboards you distribute to a client's team.
- **Dataset settings ▸ Scheduled refresh** is where a client's report becomes "live" — you will use this
  in Module 12 for a management-reporting retainer.

> **Licence reality check:** the free account lets you publish to your own workspace and share a
> `.pbix` file with anyone for free (they must install Desktop to open it). Sharing an interactive
> report with someone else's login requires a Fabric Free with viewer permission in the same tenant,
> or a paid per-user/premium capacity. Plan this with clients up front — see Module 12.

---

## 1.6 Ten habits to build from day one

1. **Name things like an accountant.** `FactGLJournal`, `DimAccount`, `Total Revenue` — not "Table1", "sum of Amt2".
2. **One measure, one definition.** Never write `SUM(Sales)` in five different visuals.
3. **Reconcile to a control total.** Your model must tie to the trial balance. If it does not, you have a bug.
4. **Keep the source extract separate.** Never analyse the file you were given; analyse a copy, and keep the original untouched.
5. **Document as you go.** A one-line description on every measure (the *Description* box in the Data pane).
6. **Do not colour for decoration.** Colour means something (actual vs budget, above vs below target).
7. **Number formats set in the model**, not on each visual. Set once, in the measure's format string.
8. **Smallest model that answers the question.** Every extra table is a refresh, a risk and a cost.
9. **Version your file**: `Mhondoro_Forensic_v01.pbix` … never "final_FINAL_v3".
10. **Write the methodology note while you build.** It is the difference between a technician and an advisor.

---

## 1.7 Exercises (do these before the lab)

1. Import `Sales2019-2021` from the practice workbook and create each of these visuals once:
   line, area, clustered column, stacked column, bar, pie, donut, treemap, funnel, gauge, KPI, card,
   table, matrix, scatter, map, waterfall, ribbon, decomposition tree, Q&A.
   Give each one a title that is a *sentence* ("Revenue grew 12% into Q4" beats "Sales by Month").
2. Switch to **DAX query view** and run `EVALUATE SimpleData`. Note that everything in Power BI is
   ultimately a table. This single fact is what makes it possible to audit a model.
3. Open **Model view**. You will see a single table with no relationships. Write down in your notebook
   why a single table cannot answer "sales by region by month by product *and also* budget vs actual".

---

## 1.8 Module 1 checklist

- [ ] Desktop installed, regional settings set, auto date/time off
- [ ] Imported an Excel sheet through Power Query, applied a change, closed and applied
- [ ] Built at least 8 different visual types
- [ ] Saved a `.pbix` and published to the Service
- [ ] Ran an `EVALUATE` query in DAX query view
- [ ] Know the difference between a report, a dashboard and an app

**Next:** [Module 2 — Connecting & Shaping Data](02_Connecting_and_Shaping_Data_PowerQuery.md) —
where you learn why 70% of a consultant's billable time is Power Query, not visuals.

---

## Related material

- [../labs/Lab_Index.md#lab-01--first-report-in-40-minutes](../labs/Lab_Index.md#lab-01--first-report-in-40-minutes)
- [../powerbi/Windows_Install_Guide.md](../powerbi/Windows_Install_Guide.md)
- [../powerbi/macOS_Options_Guide.md](../powerbi/macOS_Options_Guide.md)
- [../data/README.md](../data/README.md)

**Next:** [Module 2 — Connecting & Shaping Data](02_Connecting_and_Shaping_Data_PowerQuery.md)
