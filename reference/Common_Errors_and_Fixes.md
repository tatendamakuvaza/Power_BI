# Common errors and fixes

The problems you will actually hit, in the order you will hit them.

---

## Power Query

| Symptom | Cause | Fix |
|---|---|---|
| `Column1, Column2…` as headers | Headers not promoted | Home ▸ Use First Row as Headers (check *Use original column name as prefix*) |
| Numbers appear as text, sums are wrong | Type never changed, or locale mismatch | Change type to Decimal Number; set the correct locale for thousands separators |
| Join returns blanks even though values look identical | Trailing spaces, case, or text vs number | Trim + Proper-case both sides; force both keys to text |
| `"0110"` became `110` | Code converted to a number | Re-type as text **in the source step**, before any other transformation |
| Dates shift by days | Ambiguous `dd/mm` interpreted as `mm/dd` | Set the locale on conversion; check a known date against the source |
| Refresh fails after a client adds a file | The folder query picked up `~$` lock files or a differently-shaped file | Filter the file list on prefix/suffix and exclude lock files |
| Query is slow on a big table | A custom column broke query folding before the filter | Move filters/removals before any fold-breaking step (index, complex custom column) |
| Hidden tables appear in the model | Staging queries left with load enabled | Right-click ▸ untick Enable load, prefix with `stg_` |

---

## Data model

| Symptom | Cause | Fix |
|---|---|---|
| A slicer does nothing to a visual | No relationship path, or the filter crosses a single-direction relationship backwards | Fix the model (add a dimension or a bridge) — do not reach for bidirectional filters |
| Relationship shows many-to-many | The "one" side key is not unique | Investigate duplicates in the dimension; if legitimate, create a bridge table |
| Totals are right per row but wrong overall | Non-additive value (a rate, a %, a balance) summed | Use a ratio of sums, or the semi-additive pattern |
| `TOTALYTD` returns nonsense | Date table not marked, or auto date/time is on | Mark `DimDate` as the date table; turn auto date/time off |
| Two date relationships cause double filtering | Both active | Keep one active; use `USERELATIONSHIP` or a duplicated dimension |
| Time intelligence is blank | Date column is text, or `DimDate` has gaps | Convert to a real date type; rebuild a contiguous table |
| Model size balloons after adding a column | A calculated column on a large fact table | Compute in Power Query (compressed), or use a measure |

---

## DAX

| Symptom | Cause | Fix |
|---|---|---|
| Revenue shows negative | Revenue is a credit balance; the sign flip is missing | `CALCULATE ( …, DimAccount[AccountType] = "Revenue" ) * -1` |
| Gross profit is huge | Subtracted a negative cost of sales | Add the signed cost of sales: `Revenue + CostOfSales` |
| `#DIV/0!` in a card | Used `/` instead of `DIVIDE` | Wrap in `DIVIDE ( numerator, denominator )` |
| A `CALCULATE` filter seems ignored | The column is on the wrong side of a unidirectional relationship | Filter the dimension column, or restructure the model |
| Measure slow / times out on a client model | `FILTER` over a fact table, or nested iterators | Filter a column/dimension instead; aggregate before iterating |
| Numbers differ between DAX query view and a visual | The visual has a filter, top-N or a hidden page-level filter you forgot | Check the Filters pane and the visual-level filters |
| Closing balance repeats in every month | Total was computed once and the date filter replaced | Use the `MAX(DimDate[Date])` cumulative pattern |
| Rank is wrong inside groups | `RANKX` over the whole table rather than the visible subset | Use `ALLSELECTED` on the axis column |

---

## Report design

| Symptom | Cause | Fix |
|---|---|---|
| Numbers unreadable | Format set per visual instead of in the model | Set the format string on each measure; use `$#,##0;($#,##0);"-"` |
| Chart is meaningless to a CFO | Title is a label ("Revenue by Month"), not a finding | Write the sentence: "Revenue fell 12.2% vs prior year" |
| Colours imply meaning that is not there | Decorative palette | Use theme colours with agreed meanings; green favourable, red adverse |
| Page is slow to render | Too many visuals, or a heavy visual on a big table | Reduce visuals per page, use Performance Analyzer, optimise the heaviest |
| Report is unusable on a phone | No mobile layout | View ▸ Mobile layout; build a KPI-only layout for the executive page |
| Print-to-PDF cuts content | Canvas larger than A4 landscape proportions | Design at 16:9 and check the PDF; keep a print-friendly page |

---

## Publishing and sharing

| Symptom | Cause | Fix |
|---|---|---|
| Client cannot open the report | Shared a `.pbix` and they lack Desktop, or licence mismatch | Share the file (they install Desktop) or use a workspace/app with appropriate licences |
| Scheduled refresh fails | Credentials not stored, or the source gateway is missing | Dataset settings ▸ Data source credentials; install a gateway for on-premises sources |
| Refreshed data looks stale | The client replaced the file but kept the old name/headers | Agree a stable extract convention; validate headers on refresh |
| A user sees data they should not | No row-level security | Define roles in Desktop, map users in the Service, test with "View as role" |
| Report published to the wrong workspace | Careless publish step | Confirm workspace before publishing; use deployment pipelines for production |

---

## Methodology and review

| Symptom | Cause | Fix |
|---|---|---|
| A reviewer cannot reproduce your number | Undocumented transformation or measure | Add descriptions, rename steps, keep the methodology note current |
| Two analysts get different DSOs | Different definitions (averages vs closing balances, 365 vs days elapsed) | Publish the definitions in the methodology note and use them consistently |
| Findings challenged as unfair | Report mixes fact and inference, or implies intent | Separate the three; report transactions and controls, not people |
| Client data leaked | File emailed or stored outside the agreed locations | Follow the data-handling clause: agreed locations only, access-limited, deleted on schedule |

---

## The three-minute diagnostic

When a number is wrong, check in this order:

1. **Filter context:** what is on the visual (rows, columns, slicers, page filters)?
2. **Model path:** is there an active relationship from each dimension to the fact?
3. **Sign convention:** is this measure presentation or ledger convention?
4. **Grain:** is the fact table at the grain you think it is (duplicated keys)?
5. **Data type:** are the keys text on both sides, and dates real dates?
6. **Reconciliation:** does the control check (debits = credits) pass at this level?

Nine times out of ten the answer is in steps 1, 2 or 5.
