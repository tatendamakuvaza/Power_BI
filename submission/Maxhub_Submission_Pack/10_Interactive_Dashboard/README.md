# Interactive dashboard

Open `index.html` in any browser. It is a single self-contained file: the data is
embedded as JSON, the charts are inline SVG, and there is no CDN, no external font
and no network call, so it works offline and can be emailed or copied to a USB stick.

Generated 08 October 2025. Data as at 2025-09-30.
Population 13,929 ledger lines across 5,504 journals.

## What is on it

1. **Performance** - revenue, gross profit, operating profit and profit after tax by
   month; the balance sheet by statement line; the six headline ratios.
2. **Fraud and exceptions** - the seven schemes with injected against detected, the
   risk-band split, the twelve tests, and the full 171-line register, filterable by
   scheme, risk band and test, sortable on any column.
3. **Procurement and payables** - supplier spend with the cumulative Pareto line, the
   three-way-match split and the exception counts.
4. **Receivables and cash** - the ageing profile, disputed balances and the bank
   reconciliation position.

Every figure on the page is computed from `data/raw` by the same scripts that produce
the Word and Excel deliverables. Nothing is typed by hand, so the dashboard cannot
disagree with the reports.

## Rebuilding it

`python scripts/build_submission.py` regenerates the whole submission pack, including
this file. To regenerate only the dashboard, import
`scripts.submission_build.d_dashboard` and call `build(out, ctx, fx)`.
