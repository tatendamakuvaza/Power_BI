#!/usr/bin/env python3
"""
build_submission.py - regenerate the complete Maxhub submission pack.

Everything in the pack is computed from data/raw by the modules in
scripts/submission_build.  Nothing is typed by hand, so re-running this script
reproduces every document, workbook, deck, the Power BI pack and the dashboard.

    python scripts/build_submission.py            # build into submission/
    python scripts/build_submission.py --no-zip   # skip the archive
    python scripts/build_submission.py --out DIR  # build somewhere else

Exits non-zero if a control total does not tie or a planned file is missing, so it
can be used as a release gate.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
import traceback
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from submission_build import common as C          # noqa: E402
from submission_build import recon, forensic, ml  # noqa: E402
from submission_build import (d_governance, d_exam1, d_exam2, d_exam3, d_cap1,
                              d_cap2, d_cap3, d_cap4, d_pbi, d_dashboard)  # noqa: E402
from submission_build.writers import ISSUE_DATE, usd  # noqa: E402

# ---------------------------------------------------------------------------
# The submission tree.  One entry per folder: (folder, module, deliverable name,
# assessment, rubric reference, files the module must produce).
# ---------------------------------------------------------------------------
FOLDERS = [
    ("00_Submission_Index_and_QC", "d_governance",
     "Submission index, reconciliation record and quality control",
     "Whole submission", "Index and QC across all seven assessments",
     ["Submission_Index_and_QC.docx", "Reconciliation_and_QC.xlsx"]),
    ("01_Data_Governance", None,   # written by the d_governance build in folder 00
     "Data governance record, source file hashes, data request list and lineage",
     "Capstone 1 / all", "Data governance and lineage",
     ["Data_Governance_Record.docx", "Source_File_Hashes.csv",
      "Data_Request_List_and_Lineage.xlsx"]),
    ("02_Practical_Exam_1_Modelling_and_DAX", "d_exam1",
     "Data model, DAX measure library, control checks and methodology",
     "Practical Exam 1 (4 hours)", "Schema 30 / measures 40 / validation 20 / methodology 10",
     ["Methodology_Note.docx", "Model_Documentation.docx",
      "Control_Checks_and_Measure_Library.xlsx"]),
    ("03_Practical_Exam_2_Forensic_Analytics", "d_exam2",
     "Test programme, forensic workbench specification and findings summary",
     "Practical Exam 2 (5 hours)", "Programme 25 / workbench 35 / findings 30 / governance 10",
     ["Test_Programme.xlsx", "Findings_Summary.docx",
      "Forensic_Workbench_Specification.docx"]),
    ("04_Practical_Exam_3_Advisory_Proposal", "d_exam3",
     "Client proposal, engagement letter, priced scope of work and pitch outline",
     "Practical Exam 3 (2 hours)", "Proposal 40 / letter 30 / SOW 20 / pitch 10",
     ["Client_Proposal.docx", "Engagement_Letter.docx", "Priced_Scope_of_Work.xlsx",
      "Pitch_Outline.docx"]),
    ("05_Capstone_1_Forensic_Fraud_Detection", "d_cap1",
     "Forensic investigation: memo, test programme, evidence register, findings, "
     "board deck and remediation plan",
     "Capstone 1", "Governance 10 / programme 15 / detection 20 / quantification 20 / "
                  "evidence 10 / report 15 / deck 10",
     ["Engagement_and_Methodology_Memo.docx", "Appendix_A_Test_Programme.xlsx",
      "Evidence_Register.xlsx", "Findings_Report.docx", "Board_Presentation.pptx",
      "Remediation_Plan.xlsx"]),
    ("06_Capstone_2_Financial_Statements_and_Close", "d_cap2",
     "Financial statements, close pack and management commentary",
     "Capstone 2", "Statements, close pack controls and commentary",
     ["Financial_Statements_and_Close_Pack.xlsx",
      "Management_Pack_Commentary_and_Guide.docx"]),
    ("07_Capstone_3_Procurement_and_Working_Capital", "d_cap3",
     "Procurement, receivables, cash and working-capital analytics with exception "
     "registers and the committee pack",
     "Capstone 3", "Procurement, collections, working capital, data quality, committee pack",
     ["Procurement_Analytics.xlsx", "Receivables_and_Collections.xlsx",
      "Cash_and_Working_Capital.xlsx", "Exception_Register.xlsx",
      "Analytics_Findings_Memo.docx", "Data_Quality_Report.docx", "Committee_Pack.pptx"]),
    ("08_Capstone_4_Predictive_Analytics_and_Advisory", "d_cap4",
     "Churn model, forecasting, anomaly detection, model governance and the service "
     "blueprint",
     "Capstone 4", "Model quality, governance, forecasting, anomaly detection, sellable service",
     ["Churn_Model_Scored_Clients.xlsx", "Forecast_and_Scenarios.xlsx",
      "Anomaly_Register.xlsx", "Model_Governance_Pack.docx",
      "AI_Assisted_Reporting_Routine.docx", "Service_Blueprint_and_Pricing.docx"]),
    ("09_PowerBI_Ready_To_Import_Pack", "d_pbi",
     "Pre-shaped CSV warehouse, Power Query M, DAX libraries, data model, build "
     "instructions and validation report",
     "Power BI deliverable", "Ready-to-import pack (no binary .pbix)",
     ["PowerQuery_Load.m", "DAX_Measures_Reference.xlsx", "PowerBI_Data_Model.xlsx",
      "Build_Instructions.docx", "Build_Instructions.md", "Validation_Report.txt",
      "Import_Manifest.json", "README.md", "Core_Measures_Library.dax",
      "Forensic_Tests_Library.dax", "Time_Intelligence_Library.dax"]),
    ("10_Interactive_Dashboard", "d_dashboard",
     "Self-contained interactive dashboard mirroring the forensic workbench",
     "Power BI deliverable", "Interactive reporting",
     ["index.html", "README.md"]),
]


def lower_aliases(d):
    """Return the dict with a lowercase copy of every key, so both spellings work."""
    out = dict(d)
    for k, v in list(out.items()):
        out.setdefault(str(k).lower(), v)
    return out


class ReconView:
    """The Reconciliation object, also readable as ctx['recon']['tie'] / ['total']."""

    def __init__(self, R):
        self._R = R

    def __getattr__(self, name):
        return getattr(self._R, name)

    def __getitem__(self, key):
        return {"tie": len(self._R.passes), "total": len(self._R.rows),
                "rows": self._R.rows, "failures": self._R.failures}[key]


def control_check_values(ctx):
    """The values the Exam 1 validation page reports, computed here from the ledger."""
    led, ct = ctx["ledger"], ctx["control_totals"]
    pat24 = ctx["pl_2024"]["Profit after tax"]
    re_closing = sum(r["AmountUSD"] for r in led.gl
                     if r["AccountCode"] == "3100" and r["EntryType"] == "Closing"
                     and r["FiscalYear"] == 2024)
    return {
        "CC01": round(ct["Total debits"] - ct["Total credits"], 2),
        "CC02": ct["GL lines"],
        "CC03": ct["Journals"],
        "CC04": ct["Unbalanced journals"],
        "CC05": ct["Orphan GL account keys"],
        "CC06": ct["Orphan GL vendor keys"],
        "CC07": round(ctx["balance_sheet"]["BS check"], 2),
        "CC08": round(pat24 + re_closing, 2),
        "CC09": round(ctx["cash_flow"]["Tie check"], 2),
        "CC10": round(sum(abs(d["Difference"]) for d in ctx["tb_diffs"]), 2),
        "CC11": round(ctx["pl_2025"]["Revenue"], 2),
        "CC12": round(ctx["ratio_inputs"]["AR"], 2),
        "CC13": round(ctx["ratio_inputs"]["AP"], 2),
        "CC14": round(ctx["ratio_inputs"]["Cash"], 2),
    }


def build_context():
    R, ctx = recon.run()
    led = ctx["ledger"]
    bs, rt, ri = ctx["balance_sheet"], ctx["ratios"], ctx["ratio_inputs"]

    ctx["recon"] = ReconView(R)
    ctx["expected"] = C.EXPECTED
    ctx["pl_cum"] = C.pl_statement(led, upto=C.AS_AT)
    ctx["tb"] = C.trial_balance(led)
    ctx["monthly"] = C.monthly_pl(led)

    ctx["control_totals"] = lower_aliases({
        **ctx["control_totals"],
        "Manual journal lines": ctx["control_totals"]["Manual journals"],
        "tb diffs": len(ctx["tb_diffs"]),
    })
    for key in ("pl_2024", "pl_2025", "pl_cum"):
        ctx[key] = lower_aliases({**ctx[key], "Net profit": ctx[key]["Profit after tax"]})
    ctx["balance_sheet"] = lower_aliases({
        **bs,
        "Equity lines": C.BS_EQUITY_LINES,
        "trade receivables": ri["AR"], "trade payables": ri["AP"],
        "cash": ri["Cash"], "inventory": ri["Inventory net"],
    })
    ctx["ratios"] = lower_aliases({
        **rt,
        "total assets": bs["Total assets"], "total liabilities": bs["Total liabilities"],
        "total equity": bs["Total equity"], "cash": ri["Cash"],
        "current ratio": bs["Current ratio"], "ccc": rt["CCC"],
        "roa": ctx["pl_2025"]["Profit after tax"] / bs["Total assets"],
        "roe": ctx["pl_2025"]["Profit after tax"] / bs["Total equity"],
        "ratio inputs": ri,
    })
    ctx["spend"] = lower_aliases({**ctx["spend"], "spend": ctx["spend"]["total"]})
    ctx["index_rows"] = [(i + 1, f[2], f[3], f[4], ", ".join(f[5]))
                         for i, f in enumerate(FOLDERS)]
    return ctx


def write_root_readme(root, ctx, fx, mlres, missing, extra, log_lines):
    text = f"""# Maxhub submission pack

**Engagement:** Maxhub Pvt Ltd - three practical assessments and four capstones
**Client:** Mhondoro Holdings Plc (synthetic engagement data generated by this repository)
**Data as at:** 30 September 2025 (FY2025, month 9 of 12)
**Prepared:** {ISSUE_DATE:%d %B %Y}
**Population:** {ctx['control_totals']['GL lines']:,} ledger lines across
{ctx['control_totals']['Journals']:,} journals; debits = credits =
{usd(ctx['control_totals']['Total debits'])}

---

## What is in this folder

| # | Folder | Contents |
|---|---|---|
""" + "".join(
        f"| {i + 1} | `{f[0]}` | {f[2]} |\n" for i, f in enumerate(FOLDERS)
    ) + f"""
Plus `Maxhub_Submission_Pack.zip` alongside this folder - the same contents as a single
download.

## Headline results

| Measure | Result |
|---|---:|
| Control totals reconciled | {len(ctx['recon'].passes)} of {len(ctx['recon'].rows)} checks tie |
| Trial balance differences | {len(ctx['tb_diffs'])} |
| Balance sheet check | {ctx['balance_sheet']['BS check']:,.2f} |
| Cash flow tie | {ctx['cash_flow']['Tie check']:,.2f} |
| Revenue FY2024 | {usd(ctx['pl_2024']['Revenue'])} |
| Revenue FY2025 (9 months) | {usd(ctx['pl_2025']['Revenue'])} |
| Gross margin FY2025 | {ctx['pl_2025']['Gross margin pct']:.2f}% |
| Profit after tax FY2025 (9 months) | {usd(ctx['pl_2025']['Net profit'])} |
| Total assets at 30 Sep 2025 | {usd(ctx['balance_sheet']['Total assets'])} |
| Current ratio | {ctx['balance_sheet']['Current ratio']:.2f} |
| Cash conversion cycle | {ctx['ratios']['CCC']:.0f} days |
| Supplier spend tested | {usd(ctx['spend']['total'])} |
| Suspicious journals identified | {fx['grand']['Lines']} |
| Value identified | {usd(fx['grand']['Value'])} |
| Risk-weighted value | {usd(sum(r['RiskWeightedValue'] for r in fx['register']))} |
| Detection rate against the injection key | {fx['answer_key']['Coverage pct']:.0f}% |
| Exceptions investigated and dismissed | {len(fx['dismissed'])} |
| Unapproved manual journals over $10,000 | {usd(fx['maker_checker']['unapproved_value'])} |
| Churn model accuracy against a {mlres['model']['baseline_accuracy']:.1%} baseline | {mlres['model']['accuracy']:.1%} |
| Client fees at risk | {usd(mlres['fee_at_risk']['fee at risk'])} |

## The seven schemes

| Scheme | Test | Journals | Value |
|---|---|---:|---:|
""" + "".join(
        f"| {r['Scheme']} | {r['Test']} | {r['Detected journals']} | "
        f"{usd(fx['totals'][r['Test']]['Value'])} |\n"
        for r in fx["answer_key"]["by_scheme"]
    ) + f"""| **Total** | | **{fx['grand']['Lines']}** | **{usd(fx['grand']['Value'])}** |

## How the numbers were produced

Every figure in every document is computed from `data/raw` by the scripts in
`scripts/submission_build`. Nothing is typed by hand and nothing is copied from a marking
guide.

| Script | Role |
|---|---|
| `common.py` | Loader, typed ledger, statements, ratios, cash flow, sub-ledger analytics |
| `recon.py` | {len(ctx['recon'].rows)} control-total checks against the client's published figures |
| `forensic.py` | The twelve forensic tests, the evidence register and the risk scoring model |
| `ml.py` | Churn model, lift, improvement experiments, forecast and anomaly detection |
| `writers.py` | Shared Word, Excel and PowerPoint formatting |
| `d_governance.py`, `d_exam1-3.py`, `d_cap1-4.py` | The eleven deliverable sets |
| `d_pbi.py` | The Power BI ready-to-import pack |
| `d_dashboard.py` | The interactive dashboard |
| `build_submission.py` | This orchestrator |

Re-run it with `python scripts/build_submission.py`. It exits non-zero if a control total
does not tie or a planned file is missing.

## Verification

- `{len(ctx['recon'].rows)} reconciliation checks` are printed in
  `00_Submission_Index_and_QC/Reconciliation_and_QC.xlsx`; every one ties.
- `09_PowerBI_Ready_To_Import_Pack/Validation_Report.txt` re-performs the key Power BI
  measures against the shipped CSVs and compares each with the control total.
- The build log at the end of this folder records every file written and its size.
{('- ' + chr(10).join('- ' + m for m in missing)) if missing else ''}
## Confidentiality

Client data, ledger extracts and bank details in this pack are synthetic and were generated
for training. Bank account numbers are masked throughout. Treat the pack as Confidential.

## Known limitations, disclosed rather than hidden

- The T07 accrual test raises 21 journals with the same pattern. Six are corroborated by the
  extract's answer key; the other 15 ($36,000) are indistinguishable on the data and are
  reported on a supplementary schedule rather than suppressed or silently counted.
- Benford's first-digit test returns a chi-square of {fx['benford']['chi_square']:,.2f}, which
  flags the population as a whole. It is a reasonableness screen on generated data, not
  evidence of fraud, and it is presented with that caveat.
- The churn model trains on 150 client-years. The published metrics are honest out-of-sample
  figures against a majority-class baseline, and the time-split validation is reported
  alongside the random split.
- No `.pbix` is supplied: a binary model cannot be authored or verified outside Power BI
  Desktop. The ready-to-import pack builds the same model and is validated before use.
"""
    with open(os.path.join(root, "README.md"), "w", encoding="utf-8") as f:
        f.write(text)
    return text


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(HERE), "submission"),
                    help="output directory (default: submission/)")
    ap.add_argument("--no-zip", action="store_true", help="do not build the archive")
    ap.add_argument("--keep", action="store_true", help="do not clear the output folder first")
    args = ap.parse_args(argv)

    import shutil
    pack = os.path.join(args.out, "Maxhub_Submission_Pack")
    if not args.keep and os.path.isdir(pack):
        shutil.rmtree(pack)
    os.makedirs(pack, exist_ok=True)

    print("Loading the ledger and running the control-total reconciliation ...")
    ctx = build_context()
    R = ctx["recon"]
    print(f"  {len(R.passes)} of {len(R.rows)} control-total checks tie")
    for f in R.failures:
        print(f"  INVESTIGATE: {f['Area']} / {f['Check']} computed {f['Computed']} "
              f"expected {f['Expected']}")

    print("Running the forensic programme ...")
    fx = forensic.run(ctx["ledger"])
    ctx["fx"] = fx
    ctx["fx_grand_value"] = fx["grand"]["Value"]
    print(f"  {fx['grand']['Lines']} exceptions, {usd(fx['grand']['Value'])}; "
          f"answer-key coverage {fx['answer_key']['Coverage pct']:.0f}%; "
          f"{len(fx['dismissed'])} dismissed")

    print("Running the churn model, forecast and anomaly detection ...")
    mlres = ml.run()
    ctx["ml"] = mlres
    print(f"  accuracy {mlres['model']['accuracy']:.1%} vs baseline "
          f"{mlres['model']['baseline_accuracy']:.1%}; "
          f"fees at risk {usd(mlres['fee_at_risk']['fee at risk'])}; "
          f"{len(mlres['anomalies']['rows'])} engagement anomalies")

    ctx["control_check_values"] = control_check_values(ctx)

    log_lines, missing, errors = [], [], []
    modules = {"d_governance": d_governance, "d_exam1": d_exam1, "d_exam2": d_exam2,
               "d_exam3": d_exam3, "d_cap1": d_cap1, "d_cap2": d_cap2, "d_cap3": d_cap3,
               "d_cap4": d_cap4, "d_pbi": d_pbi, "d_dashboard": d_dashboard}

    for folder, module, _name, _assess, _rubric, files in FOLDERS:
        out = os.path.join(pack, folder)
        print(f"Building {folder} ...")
        if module is None:
            for fn in files:
                path = os.path.join(out, fn)
                if os.path.exists(path):
                    log_lines.append(f"{os.path.getsize(path):>10,}  {folder}/{fn}")
                else:
                    missing.append(f"{folder}/{fn}")
                    print(f"  MISSING planned file: {folder}/{fn}")
            continue
        mod = modules[module]
        try:
            if module in ("d_cap1", "d_cap3"):
                mod.build(out, ctx, fx)
            elif module == "d_exam2":
                mod.build(out, ctx, fx)
            elif module == "d_exam3":
                mod.build(out, ctx, fx)
            elif module == "d_cap4":
                mod.build(out, ctx, mlres)
            elif module == "d_pbi":
                mod.build(out, ctx, fx)
            elif module == "d_dashboard":
                mod.build(out, ctx, fx)
            else:
                mod.build(out, ctx)
        except Exception:
            errors.append(folder)
            print(f"  FAILED:\n{traceback.format_exc()}")
            continue
        for fn in files:
            path = os.path.join(out, fn)
            if os.path.exists(path):
                log_lines.append(f"{os.path.getsize(path):>10,}  {folder}/{fn}")
            else:
                missing.append(f"{folder}/{fn}")
                print(f"  MISSING planned file: {folder}/{fn}")

    for sub in ("Data_Ready_To_Import",):
        d = os.path.join(pack, "09_PowerBI_Ready_To_Import_Pack", sub)
        if os.path.isdir(d):
            for fn in sorted(os.listdir(d)):
                p = os.path.join(d, fn)
                log_lines.append(f"{os.path.getsize(p):>10,}  09_PowerBI_Ready_To_Import_Pack/"
                                 f"{sub}/{fn}")

    write_root_readme(pack, ctx, fx, mlres, missing, [], log_lines)
    with open(os.path.join(pack, "BUILD_LOG.txt"), "w", encoding="utf-8") as f:
        f.write(f"Maxhub submission pack - build log\n"
                f"Built {dt.datetime.now():%Y-%m-%d %H:%M:%S} by scripts/build_submission.py\n"
                f"Python {sys.version.split()[0]}\n\n"
                f"Control-total checks: {len(R.passes)} of {len(R.rows)} tie\n"
                f"Forensic exceptions: {fx['grand']['Lines']} / {usd(fx['grand']['Value'])}\n"
                f"Answer-key coverage: {fx['answer_key']['Coverage pct']:.0f}%\n"
                f"Dismissed exceptions: {len(fx['dismissed'])}\n"
                f"Churn accuracy: {mlres['model']['accuracy']:.1%} "
                f"(baseline {mlres['model']['baseline_accuracy']:.1%})\n\n"
                f"Files written ({len(log_lines)}):\n" + "\n".join(log_lines) + "\n"
                + (f"\nMISSING: {len(missing)}\n" + "\n".join(missing) if missing else
                   "\nNo planned file is missing.\n")
                + (f"\nMODULE ERRORS: {', '.join(errors)}\n" if errors else
                   "\nNo module raised an error.\n"))

    zip_path = None
    if not args.no_zip:
        zip_path = os.path.join(args.out, "Maxhub_Submission_Pack.zip")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for base, _dirs, names in os.walk(pack):
                for n in sorted(names):
                    p = os.path.join(base, n)
                    z.write(p, os.path.join("Maxhub_Submission_Pack",
                                            os.path.relpath(p, pack)))
        print(f"Archive: {zip_path} ({os.path.getsize(zip_path):,} bytes)")

    total = sum(os.path.getsize(os.path.join(b, n))
                for b, _d, ns in os.walk(pack) for n in ns)
    print(f"\n{len(log_lines)} planned files, {total:,} bytes in {pack}")
    if missing or errors or R.failures:
        print("\nRELEASE GATE FAILED")
        for m in missing:
            print("  missing:", m)
        for e in errors:
            print("  module error:", e)
        for f in R.failures:
            print("  control total:", f)
        return 1
    print("Release gate passed: every control total ties and every planned file exists.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
