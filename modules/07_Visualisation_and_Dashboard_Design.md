# Module 7 — Visualisation & Dashboard Design

**Time:** 8 hours · **Lab:** [Lab 07](../labs/Lab_Index.md#lab-07--executive-dashboard-to-spec) · **Prerequisite:** Module 6

> A forensic finding that nobody understands is worthless. A dashboard a CFO cannot read in 30 seconds
> does not get renewed. This module is about being *understood*.

---

## 7.1 The one rule

**Every visual must answer a question someone actually asked.**

Before you drag a field, write the question in the report's design notes:

| Question | Visual |
|---|---|
| How did revenue move over the year? | Line chart, month axis |
| Are we over or under budget, and where? | Matrix with variance columns + conditional formatting |
| Which five vendors take most of the spend? | Bar chart, sorted, top-N filter |
| Which debtors are older than 90 days? | Table with ageing bucket, red formatting |
| Does the trial balance balance? | Card with a check measure |

If you cannot write the question, do not build the visual.

---

## 7.2 Chart choice for accounting work

| Visual | Use it for | Do not use it for |
|---|---|---|
| **Line / area** | Trends over time (revenue, cash, DSO) | Categories |
| **Clustered column** | Comparing few categories, 2–3 series | Long category lists |
| **Stacked column** | Composition over time (revenue by product family) | Precise comparison of middle segments |
| **Bar (horizontal)** | Ranked lists (top vendors, top customers) | 100+ categories |
| **Waterfall** | Bridges: budget → actual, opening cash → closing cash | Time series |
| **Matrix** | Statements, cross-tabs, variance tables | Headline numbers |
| **Card / KPI** | Single number + target + trend | Anything with more than 2 dimensions |
| **Scatter** | Relationships (e.g. fee vs hours in Module 11) | Time trends |
| **Treemap** | Composition when there are many categories | Comparison of small differences |
| **Gauge** | Almost nothing. Use a KPI or a bullet chart instead | Anything a professional will read |
| **Decomposition tree** | Ad-hoc root-cause drill (great for variance) | A finished report page |
| **Map** | Geographic distribution (only if geography is a real driver) | When a bar chart is clearer |
| **Ribbon chart** | Rank changes over time | Most things |

**Number formatting rules for finance:** currency with thousands separators, decimals only when they
change a decision, negatives in brackets or with a colour convention, percentages to 0.0% or 0.00%,
zero shown as `-` (use a format string like `$#,##0;($#,##0);"-"`).

---

## 7.3 Layout: the 30-second rule

Design each page so that the eye travels: **headline → context → detail**.

```
┌──────────────────────────────────────────────────────────────────┐
│  Report title + period (driven by measures, not typed)           │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│ KPI cards (4-6) - the answer in numbers                          │
├──────────────┴──────────────┴──────────────┴────────────────────┤
│ Main trend chart (revenue / cash / profit)   │ Top-5 exceptions  │
├──────────────────────────────────────────────┴────────────────────┤
│ Detail matrix or table (the evidence)                             │
└──────────────────────────────────────────────────────────────────┘
Slicers: top-right or in a collapsible pane (View ▸ Bookmarks toggling a group)
```

Rules that make the difference between a consultant's report and an intern's:

1. **Title as a sentence**, with the number in it. "Revenue $10.54m for the nine months; DSO 98 days and cash down to $0.79m".
2. **One idea per chart.** Two y-axes are a confession of confusion.
3. **Sort everything** that has a natural order (by value, by statement order — never alphabetical
   unless alphabetical *is* the order, e.g. account codes).
4. **Fewest possible colours.** Actual = dark blue, budget = grey, favourable = green, adverse = red.
   Nothing decorative.
5. **Alignment.** Use View ▸ Snap to grid and align/distribute. Misaligned dashboards read as sloppy work.
6. **White space is not waste.** 8–12 pt of padding around each visual.
7. **Consistent period labels** everywhere: `DimDate[MonthYear]` (e.g. `Sep 2025`), never a mix of
   `2025-09`, `Sep-25` and `9/2025`.
8. **Slicers reflect, don't confuse:** use "Select all" defaults, and add a "Reset" bookmark.

---

## 7.4 Theming: make it look like Maxhub, in one file

Create `assets/PowerBI_Course_Theme.json` (already in this repo) and import it:
**View ▸ Themes ▸ Browse for themes**. A theme sets colours, fonts and default visual formatting for
the whole report — so every page is consistent without manual work.

```json
{
  "name": "Maxhub Consulting",
  "dataColors": ["#1F4E79","#2E75B6","#9DC3E6","#C55A11","#548235","#BF9000","#7030A0","#7F7F7F"],
  "background": "#FFFFFF",
  "foreground": "#252525",
  "tableAccent": "#1F4E79",
  "good": "#548235",
  "neutral": "#BF9000",
  "bad": "#C00000",
  "textClasses": {
    "title":    {"fontFace": "Segoe UI Semibold", "fontSize": 16, "color": "#1F4E79"},
    "header":   {"fontFace": "Segoe UI Semibold", "fontSize": 12, "color": "#252525"},
    "label":    {"fontFace": "Segoe UI", "fontSize": 10, "color": "#404040"},
    "callout":  {"fontFace": "Segoe UI Light", "fontSize": 36, "color": "#1F4E79"}
  }
}
```

**Brand rule for client work:** load the client's logo and primary colour into the theme and title page.
They must feel that the report is *theirs*.

---

## 7.5 Interactivity that earns its place

| Feature | How | Why an accountant needs it |
|---|---|---|
| **Slicers** | Date, cost centre, statement line | Segment the analysis without rebuilding |
| **Sync slicers** | View ▸ Sync slicers (Align slicers across pages) | One filter applies to P&L, BS and cash flow |
| **Drill-down** | Add a hierarchy to an axis (FY → Quarter → Month) | Move from summary to evidence |
| **Drillthrough** | Create a "Transaction detail" page, then *Drillthrough ▸ Add fields* (`AccountCode`, `VendorID`) | Right-click a number → see the ledger lines behind it. **This is the single most valued feature in an audit context.** |
| **Tooltips** | Drag measures into *Tooltips* well; or build a report-page tooltip | Extra context without clutter |
| **Bookmarks** | A "Reset filters" bookmark, or a narrative walkthrough | Present findings in a controlled sequence |
| **Buttons + navigation** | Insert ▸ Buttons ▸ Navigator | A multi-page pack feels like an application |
| **Conditional formatting** | Format ▸ Cells/Background ▸ Field value | RAG status, exception highlighting |
| **Field parameters** | Modeling ▸ New parameter ▸ Fields | Let the client choose which measure/dimension the chart shows |
| **Smart narrative** | Insert ▸ Smart narrative (preview) | First draft commentary, human-reviewed |

### Drillthrough page pattern (build it in every engagement)

1. Create a page named `Transaction Detail`. Hide it (right-click page tab ▸ Hide page) — it stays
   reachable by drillthrough.
2. Add fields to the **Drillthrough** well: `DimAccount[AccountCode]`, `DimAccount[AccountName]`,
   `DimVendor[VendorName]`, `DimDate[FiscalPeriod]`.
3. Add a table with `PostingDate`, `JournalID`, `Description`, `Debit`, `Credit`, `PreparedBy`,
   `SourceSystem`.
4. Tick **Keep all filters** on, add a back button (Insert ▸ Buttons ▸ Back).
5. In the main report, right-click any value ▸ *Drill through ▸ Transaction Detail*.

An auditor who can right-click $3.79m of receivables and land on the individual invoices will trust
everything else on the page.

---

## 7.6 Accessibility and the professional standard

- Font ≥ 10 pt; do not put white text on a mid-tone colour.
- Do not rely on colour alone: add an arrow, a sign or a label (colour-blind readers are ~8% of men).
- Alt text on every visual (Format ▸ General ▸ Alt text) — required by many public-sector clients.
- Tab order (Selection pane ▸ Tab order) so keyboard users can navigate.
- Check the mobile layout (View ▸ Mobile layout) for the executive who reads on a phone.
- Contrast: use the theme colours, not the default pastel palette on white.

---

## 7.7 The three audiences (design for the one in the room)

| Audience | Wants | Page shape |
|---|---|---|
| **Executive / board** | The answer, the trend, the exception | 4–6 KPIs, one trend, one exception table, one page |
| **Management / finance team** | Variance, drivers, drilldown | Statement matrices, bridges, drillthrough |
| **Auditor / investigator** | Complete evidence, reproducible filters | Detail tables, exception registers, control-check cards |

Do not try to satisfy all three on one page. Build a pack: `Executive`, `Financials`, `Analytics`,
`Forensic`, `Data Quality (hidden)`.

---

## 7.8 Performance and polish checklist

- [ ] Every visual has a sentence title and a source/period footnote
- [ ] Every number has a format string; zero shows as `-`
- [ ] Conditional formatting only where a decision follows (RAG, exceptions)
- [ ] Theme imported; no default Microsoft blue anywhere
- [ ] Sync slicers across pages; a Reset bookmark exists
- [ ] Drillthrough page built, hidden, and tested
- [ ] Mobile layout checked for the executive page
- [ ] Page is legible when printed to PDF (clients still print)
- [ ] Alt text on visuals; contrast and colour rules observed
- [ ] Performance Analyzer run: no visual taking over 2 seconds on a 13k-row model

---

## 7.9 Module 7 checklist

- [ ] You can justify every visual on every page with a question it answers
- [ ] Theme imported; palette documented for the client
- [ ] Drillthrough to transaction detail working
- [ ] At least one report-page tooltip and one bookmark
- [ ] A written page-by-page design spec exists **before** you build (template in Module 12)

**Next:** [Module 8 — Analytics, KPIs & Discovery](08_Analytics_KPIs_and_Discovery.md).

---

## Related material

- [../labs/Lab_Index.md#lab-07--executive-dashboard-to-spec](../labs/Lab_Index.md#lab-07--executive-dashboard-to-spec)
- [../reference/Glossary_Accounting_and_PowerBI.md](../reference/Glossary_Accounting_and_PowerBI.md)

**Next:** [Module 8 — Analytics, KPIs & Discovery](08_Analytics_KPIs_and_Discovery.md)
