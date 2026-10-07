# Maxhub brand guidelines

Short, and deliberately strict: consistency is what makes small firm look established.

## 1. Name and positioning

**Legal name:** Maxhub Pvt Ltd
**Always referred to as:** Maxhub (never "Max Hub", "MaxHub" or "MAXXHUB")
**Positioning line:** *Forensic Accounting · Data Analytics · Machine Learning & AI · Advisory Services*
**One-liner for proposals:** "We find what is wrong in your numbers, prove it, and build the reporting
that stops it happening again."

## 2. Colours

| Role | Hex | Use |
|---|---|---|
| Maxhub Navy (primary) | `#1F4E79` | Headers, actual values, primary series |
| Advisory Blue | `#2E75B6` | Secondary series, prior year |
| Light Blue | `#9DC3E6` | Budget / target, backgrounds of callouts |
| Warm Accent | `#C55A11` | Emphasis, variances needing attention |
| Positive | `#548235` | Favourable variances, "ties", passed checks |
| Caution | `#BF9000` | Watch items, in-progress |
| Adverse | `#C00000` | Adverse variances, exceptions, failed checks |
| Neutral Grey | `#7F7F7F` | Baselines, inactive series, non-data text |
| Canvas | `#F2F6FA` | Report background |
| Purple / Orange (supplementary) | `#7030A0` / `#ED7D31` | Additional series only when the palette above is exhausted |

**Rule:** colour carries meaning. Green means favourable or verified; red means adverse or unreconciled.
Never use red or green decoratively — a CFO must be able to trust what the colour implies.

Use the palette directly in Power BI by importing
[`PowerBI_Course_Theme.json`](PowerBI_Course_Theme.json) (Report ▸ View ▸ Themes ▸ Browse for themes).

## 3. Typography

- **Font:** Segoe UI throughout (ships with Windows; clean in Power BI and Office).
- Titles 14–16 pt semibold; body 10–11 pt; footnotes 8–9 pt. Never below 8 pt in a client report.
- Sentence case for titles, not Title Case or ALL CAPS.
- Numbers: `$#,##0` for whole dollars, `$#,##0.00` only where cents matter, `0.0%` for percentages,
  and `-` for zero in a financial statement.

## 4. Report design signatures

Every Maxhub deliverable carries these, without exception:

1. A cover page: client, deliverable, period, our name, date, version, confidentiality marking.
2. A "how to read this" or methodology page, including ratio definitions and the data period.
3. A control-check page (can be hidden): debits = credits, BS check, orphan keys, unbalanced journals.
4. Sentence titles on visuals — a number in every title.
5. Source and period footnotes on every page.
6. The closing line: *Prepared by Maxhub Pvt Ltd · [date] · Confidential*.

## 5. Writing style

- Lead with the number, then the cause, then the action.
- Active voice: "The company paid 168 invoices without a three-way match", not "Invoices were found to
  have failed to meet the match criteria."
- No accusations, no adjectives about people: report transactions and controls.
- Define every technical term the first time it appears in a client document.
- Distinguish "total value", "value at risk" and "quantified loss" — always, and in that order.

## 6. File naming

`Client_Deliverable_Period_vX.Y.ext`

Examples: `Mhondoro_Forensic_Findings_2025-09_v1.0.pdf`,
`Mhondoro_ReportingPack_v1.2.pbix`, `Maxhub_Proposal_MX-2025-014_v1.0.docx`.

Include the version in the footer of every page; never issue a file called "final_final".

## 7. Confidentiality markings

| Marking | Use |
|---|---|
| Public | Marketing material, published case studies (never client data) |
| Confidential | Normal client delivery |
| Confidential — for named recipients only | Board packs, proposals, anything with personal or commercial detail |
| Confidential and legally privileged | Where the client's legal advisers direct the work |

Nothing leaves Maxhub without one of these markings on the first and last page.
