# Self-assessment checklist

Use this after each module and once at the end of the course. Tick a box only if you could do it
tomorrow, for a paying client, without looking anything up.

## Data foundation

- [ ] I can connect Power BI to Excel, CSV, a folder of files, and a database, and explain the
      difference in refresh behaviour.
- [ ] I can clean a messy accounting extract (dates, currency symbols, duplicates, blanks) with
      documented decisions, and produce a note of what I changed and why.
- [ ] I can unpivot a wide budget/actual table into a fact table.
- [ ] I can parameterise a model so that it serves a different client/period without code changes.
- [ ] I keep codes as text, and can explain why to a finance manager.

## Modelling

- [ ] I can state the grain of every fact table in my model.
- [ ] I build star schemas with one-to-many, single-direction relationships, and I can justify any
      exception.
- [ ] I handle role-playing dimensions without creating ambiguous filter paths.
- [ ] I can build and mark a date table and explain why auto date/time is off.
- [ ] I can prove the model is sound: no orphan keys, journals balance, totals tie to the TB.

## DAX

- [ ] I can explain row context, filter context and context transition with an example.
- [ ] I can write a measure with `VAR` blocks that a reviewer can check line by line.
- [ ] I can explain why gross profit adds (not subtracts) the signed cost of sales, and why a
      presentation measure flips the sign.
- [ ] I can write time intelligence that behaves correctly on a part-month.
- [ ] I can build opening/closing/movement balances for any account and reconcile them.
- [ ] I know when to move heavy work into Power Query rather than DAX.

## Reporting

- [ ] I can build a P&L, balance sheet and cash flow page from raw ledger data, and reconcile each
      to the trial balance.
- [ ] I can build a close-pack page of control checks that proves the numbers.
- [ ] I design pages with sentence titles, correct visual choice, and no decoration.
- [ ] I can build drillthrough, sync slicers, bookmarks and a theme.
- [ ] I can produce a report that is legible on paper and on a phone.

## Analytics

- [ ] I can decompose a variance into price, volume and mix, and present it as a bridge.
- [ ] I can define and compute DSO, DPO, DIO and the cash conversion cycle, and defend the definitions.
- [ ] I can run a Pareto, a Z-score outlier test and a trend/seasonality analysis.
- [ ] I can use the Decomposition tree and Key Influencers to answer a real question.
- [ ] I can write a Finding / Impact / Action block with a quantified impact.

## Forensic

- [ ] I can design a test with population, assertion, expectation, exception and follow-up.
- [ ] I can build duplicate, ghost-vendor, threshold, split-payment and round-number tests in both
      Power Query and DAX.
- [ ] I can run the J1–J10 journal-entry tests and explain what each one catches.
- [ ] I can run Benford's Law and state when it must not be used.
- [ ] I can build a risk score and an evidence register that a reviewer can trace to documents.
- [ ] I can write findings that separate fact, inference and opinion, and never accuse.

## Machine learning & AI

- [ ] I can state the baseline and compare a model against it.
- [ ] I can explain precision, recall, specificity and AUC in client language.
- [ ] I can detect and avoid feature leakage.
- [ ] I can deploy a scored dataset into Power BI with a model-metadata table and a monitoring view.
- [ ] I can describe the governance rules for using AI with client data.

## Practice and commercial

- [ ] I can write a proposal with scope, deliverables, timeline, fees and exclusions.
- [ ] I can draft an engagement letter covering data handling, confidentiality and retention.
- [ ] I can price an engagement from hours and roles, and defend it.
- [ ] I can run an independent quality-control review on someone else's model.
- [ ] I can present findings to a board in ten minutes and answer "how do I know it is right?".

## The honest question

- [ ] If a client gave me their ledger tomorrow and asked for a forensic analytics review, I could
      deliver a defensible, quantified, professional result — and I know exactly what I would do in the
      first four hours.

If that last box is ticked, you are ready. If it is not, go back to Lab 09 — it is the module that
converts the rest of the course into capability.
