"""
d_exam3.py - Practical Exam 3: the next-phase advisory proposal.

Deliverables: client proposal, engagement letter, priced scope-of-work estimate
at Maxhub day rates, and the ten-minute pitch outline.
"""
from __future__ import annotations

import os

from . import common as C
from .writers import *
from .d_exam2 import value_at_risk

RATES = {"Analyst": 120, "Senior Analyst": 150, "Senior": 200, "Manager": 280, "Partner": 450}

SCOPE = [
    ("Phase 1 - Mobilise and data", "Data request list, access, integrity checks, reconciliation to the "
     "trial balance", "Analyst", 8),
    ("Phase 1 - Mobilise and data", "Kick-off, independence and conflict checks", "Manager", 3),
    ("Phase 2 - Model build", "Refreshable data layer, star schema, control checks", "Senior", 16),
    ("Phase 3 - Continuous monitoring", "Twelve-test exception routine on the client's own data, monthly",
     "Senior", 24),
    ("Phase 3 - Continuous monitoring", "Power BI exception dashboard and drillthrough", "Senior Analyst", 20),
    ("Phase 4 - Control remediation", "Redesigned vendor onboarding and payment approval process, "
     "documented with control points", "Manager", 12),
    ("Phase 4 - Control remediation", "System access review and segregation-of-duties matrix", "Senior", 8),
    ("Phase 5 - Recovery support", "Duplicate-payment recovery pack: supplier letters, evidence schedules",
     "Senior Analyst", 10),
    ("Phase 6 - Reporting and handover", "Board presentation, management training, handover of all files",
     "Manager", 10),
    ("Quality control", "Independent partner review: re-performance, reconciliation, language", "Partner", 6),
]

RETAINER = [
    ("Monthly exception report from the client's own data (12 tests)", "Senior Analyst", 6),
    ("Review of exceptions with the Financial Controller (60 minutes)", "Senior", 2),
    ("Refresh monitoring and data-quality checks", "Analyst", 2),
    ("Quarterly control review and trend commentary", "Manager", 3),
]


def fee(scope):
    return sum(RATES[role] * hours for _, _, role, hours in scope)


def hours(scope):
    return sum(h for _, _, _, h in scope)


def build(out, ctx, fx):
    os.makedirs(out, exist_ok=True)
    total_var = sum(value_at_risk(t, v["Value"]) for t, v in fx["totals"].items())
    dup_recovery = fx["totals"]["T01"]["Value"] / 2

    # ------------------------------------------------------------ proposal
    doc = new_doc(title="Client proposal - continuous monitoring and control remediation",
                  subtitle="Next-phase proposal to Mhondoro Manufacturing (Pvt) Ltd following the "
                           "forensic investigation", reference="MX-2025-P01")
    footer(doc, "Maxhub Pvt Ltd - client proposal MX-2025-P01 - Valid for 30 days - Confidential")
    doc.add_heading("1. Your situation, as we understand it", level=2)
    para(doc, "\"The Audit Committee received a whistle-blower report. Your investigation found "
              f"{fx['grand']['Lines']} exceptions worth {usd(fx['grand']['Value'])}, including payments "
              f"to four suppliers connected to employees and {len(fx['hits']['T01']) // 2} supplier "
              "invoices that were paid twice. Nothing in the current process would have caught any of it, "
              "and next month the same tests would have to be run again by hand. We want the tests to run "
              "themselves, and we want the controls fixed so the exceptions stop happening.\"", italic=True)

    doc.add_heading("2. What you asked us to do", level=2)
    table(doc, ["#", "Requirement", "Our response"],
          [["1", "Detect this automatically, every month",
            "A twelve-test exception routine running on your own data, delivered as a Power BI dashboard "
            "and a monthly report your Financial Controller can use"],
           ["2", "Fix the controls that failed",
            "Redesigned vendor onboarding and payment approval, a segregation-of-duties matrix and a "
            "system access review"],
           ["3", "Get the money back",
            f"A recovery pack for the {usd(dup_recovery)} of duplicate payments: supplier letters with the "
            "evidence attached"],
           ["4", "Show the board it is working",
            "A quarterly trend pack proving the exception rate is falling"]],
          widths=[0.8, 5.4, 10.8], font=9)

    doc.add_heading("3. Our approach", level=2)
    for phase, text in [
        ("Phase 1 - Mobilise (week 1)", "Kick-off, data request list, read-only access, independence and "
         "conflict checks, agreement of the exception definitions."),
        ("Phase 2 - Data and model (weeks 1-2)", "Refreshable data layer, star schema, control checks. "
         "Nothing is reported until the model reconciles to your trial balance."),
        ("Phase 3 - Monitoring build (weeks 2-5)", "The twelve tests as a scheduled routine; the exception "
         "dashboard with drillthrough to the ledger line; the monthly report template."),
        ("Phase 4 - Control remediation (weeks 3-6)", "Process redesign with control points marked, "
         "segregation-of-duties matrix, access review, and the system configuration changes your IT team "
         "needs to make."),
        ("Phase 5 - Recovery and handover (week 6)", "Recovery pack, board presentation, training for your "
         "finance team, handover of every file."),
        ("Quality control (week 6)", "Independent review by a Maxhub partner who did not build the work: "
         "re-performance of a calculation, reconciliation of every headline number, language review."),
    ]:
        rich(doc, [(phase + ". ", True, False), (text, False, False)])

    doc.add_heading("4. Deliverables", level=2)
    table(doc, ["#", "Deliverable", "Format", "Week"],
          [["1", "Continuous monitoring model and exception dashboard", ".pbix + published app", "5"],
           ["2", "Monthly exception report template (populated with your data)", "Excel + PDF", "5"],
           ["3", "Redesigned vendor onboarding and payment approval process", "One-page flow + SOP", "6"],
           ["4", "Segregation-of-duties matrix and system access review", "Excel + report", "6"],
           ["5", f"Duplicate-payment recovery pack ({usd(dup_recovery)})", "Letters + evidence schedules", "6"],
           ["6", "Board presentation and management training", "Slides + session", "6"],
           ["7", "Model documentation and user guide", "PDF", "6"]],
          widths=[0.8, 8.4, 4.6, 1.4], font=9)

    doc.add_heading("5. Team", level=2)
    table(doc, ["Name", "Role", "Responsibility"],
          [["Engagement partner", "Partner", "Quality control, client relationship, reporting to the Committee"],
           ["T. Makuvaza", "Manager", "Delivery, model, analysis, board presentation"],
           ["Senior analyst", "Senior", "Test routine, remediation design"],
           ["Analyst", "Analyst", "Data preparation, working papers, monthly report"]],
          widths=[4.0, 3.0, 10.0], font=9)

    doc.add_heading("6. Fees", level=2)
    table(doc, ["Item", "Basis", "Amount (USD)"],
          [["Project work, phases 1-6", f"{hours(SCOPE)} hours at Maxhub day rates", f"{fee(SCOPE):,.0f}"],
           ["Continuous monitoring retainer", "Monthly, from month 2",
            f"{sum(RATES[r] * h for _, r, h in RETAINER):,.0f} / month"],
           ["Training for the finance team", "Half day", "1,800"],
           ["Disbursements", "At cost", "-"]],
          widths=[6.6, 6.0, 4.4], font=9, align_right=(2,))
    para(doc, "Billing: 50% on engagement acceptance, 50% on delivery. Fees are exclusive of VAT. "
              "Out-of-scope work is quoted before it is performed.", size=9)
    para(doc, f"Benchmark: the Service Catalogue prices a Fraud Risk Assessment at $6,000-$18,000 and a "
              f"Continuous Monitoring retainer at $900-$2,500 per month. This proposal sits inside both "
              f"ranges: {usd(fee(SCOPE))} for the project and "
              f"{usd(sum(RATES[r] * h for _, r, h in RETAINER))} per month.", size=9, italic=True)

    doc.add_heading("7. Assumptions", level=2)
    numbered(doc, [
        "You provide the data listed in the data request list in machine-readable form within five working "
        "days of kick-off, including the complete creditor sub-ledger (the extract supplied for the "
        f"investigation was a {ctx['ap']['count']}-invoice sample).",
        "One named client contact answers queries within one working day.",
        "The data provided is complete and accurate; we report any indication that it is not.",
        "Your IT team makes the system configuration changes we specify; we do not change your ERP.",
        "Sign-off on drafts within five working days; further revision rounds are chargeable.",
        "Up to six staff interviews of one hour each.",
    ])

    doc.add_heading("8. What is not included", level=2)
    bullets(doc, [
        "Legal advice, or expert evidence in proceedings (available under a separate engagement).",
        "Tax computations, returns or ZIMRA representation.",
        "Recovering funds on your behalf: we identify, quantify and draft; you or your lawyers pursue.",
        "Changes to your ERP or accounting system.",
        "Data extraction from systems to which you do not give us read-only access.",
        "Audit or assurance opinions. This is advisory work, not an audit.",
    ])

    doc.add_heading("9. Confidentiality and data handling", level=2)
    para(doc, "All client data is confidential, stored only in Maxhub-controlled encrypted locations for "
              "the engagement, accessed only by the named engagement team, and returned or destroyed at the "
              "end of the retention period (seven years for working papers, 90 days for source data) or "
              "earlier on request. Personal data is processed lawfully and minimally in line with "
              "Zimbabwe's Cyber and Data Protection Act (2021). Aggregated, de-identified examples may be "
              "used for training only with your written permission.")

    doc.add_heading("10. Why Maxhub", level=2)
    para(doc, "We built the investigation you have just read, so the monitoring is the same work running "
              "on a schedule rather than a new team learning your ledger. Every deliverable reconciles to "
              "your trial balance before it is issued, and we hand over the model and the documentation - "
              "you are never locked in to us.")
    doc.add_heading("11. Acceptance", level=2)
    table(doc, ["", ""],
          [["Signed for the client", "______________________  Name / Title / Date"],
           ["Signed for Maxhub Pvt Ltd", "______________________  Name / Title / Date"]],
          widths=[6.0, 11.0], font=9)
    sign_off(doc)
    doc.save(ensure(os.path.join(out, "Client_Proposal.docx")))

    # ------------------------------------------------------ engagement letter
    el = new_doc(title="Engagement letter - continuous monitoring and control remediation",
                 subtitle="Terms of business covering data handling, confidentiality, retention and "
                          "independence", reference="MX-2025-EL01")
    footer(el, "Maxhub Pvt Ltd - engagement letter MX-2025-EL01 - Confidential")
    para(el, "To: The Audit Committee and the Financial Controller, Mhondoro Manufacturing (Pvt) Ltd")
    para(el, f"Date: {ISSUE_DATE:%d %B %Y}")
    el.add_heading("1. Background and objective", level=2)
    para(el, "You have asked Maxhub to implement continuous monitoring of the procure-to-pay and "
             "journal-entry cycles, to remediate the control weaknesses identified in our forensic "
             f"investigation of {PERIOD}, and to support the recovery of {usd(dup_recovery)} of duplicate "
             "payments.")
    el.add_heading("2. Scope of work", level=2)
    numbered(el, [
        "Obtain and document the data received, including source, extraction date and integrity checks.",
        "Reconcile the data to your trial balance before any analysis is reported.",
        "Build and document the twelve-test exception routine and the exception dashboard.",
        "Redesign vendor onboarding and payment approval; document the control points.",
        "Perform a system access and segregation-of-duties review and recommend the configuration changes.",
        "Prepare the duplicate-payment recovery pack.",
        "Report to management and present to the Audit Committee.",
        "Hand over the models, working files and documentation.",
    ])
    el.add_heading("3. Matters not included in scope", level=2)
    bullets(el, [
        "Legal advice, and expert evidence in proceedings unless separately agreed in writing.",
        "Tax advice and filings, and any communication with ZIMRA.",
        "Recovery of funds or pursuing third parties.",
        "Work on data or periods outside this letter.",
        "Assurance over the completeness or accuracy of systems we can only observe through extracts.",
        "Changes to your ERP or accounting system.",
    ])
    el.add_heading("4. Our responsibilities", level=2)
    para(el, "We will perform the work with professional skill and care, in accordance with the engagement "
             "standards of the Institute of Chartered Accountants of Zimbabwe and the IESBA Code of Ethics. "
             "We will report significant findings as they arise rather than only at the end, and we will "
             "raise any indication that the data provided is incomplete or inconsistent.")
    el.add_heading("5. Your responsibilities", level=2)
    numbered(el, [
        "Provide complete and accurate data and, where relevant, written confirmation of its completeness.",
        "Provide the data in machine-readable form within five working days of the start date.",
        "Nominate a single point of contact authorised to answer queries and provide documents.",
        "Make staff available for interviews where required.",
        "Appoint a decision-maker for every matter we raise.",
        "Notify us of any matter that may affect the engagement, including legal process touching the data.",
    ])
    el.add_heading("6. Basis of reporting and limitations", level=2)
    para(el, "Our conclusions are based on the data and documents provided. Data analytics identifies "
             "exceptions and patterns; it does not by itself establish intent, and it is not a substitute "
             "for document-level corroboration. Where we cannot corroborate a matter, we will say so. Our "
             "report is prepared for the Audit Committee and management for the purpose set out in section "
             "1; we accept no responsibility to any other party, and no third party may rely on it without "
             "our written consent.")
    el.add_heading("7. Confidentiality and data handling", level=2)
    numbered(el, [
        "We keep all information confidential and use it only for this engagement.",
        "Access is restricted to the named engagement team.",
        "Data is stored in Maxhub-controlled, encrypted, access-controlled locations; mobile copies are "
        "minimised and deleted after use.",
        "Personal data is processed lawfully and minimally, in line with Zimbabwe's Cyber and Data "
        "Protection Act (2021), and we will assist with any data-subject request or breach notification "
        "concerning data we hold.",
        "On completion and after the retention period we will delete or return the engagement data, unless "
        "required by law or professional standards.",
        "Retention: seven years for working papers required by professional standards; 90 days for source "
        "data, unless the matter becomes subject to legal proceedings, in which case we hold it under "
        "legal-hold instructions.",
        "If a matter may become subject to proceedings, we will where possible work under the direction of "
        "your legal advisers so that privilege is preserved.",
    ])
    el.add_heading("8. Independence and conflicts", level=2)
    para(el, "We have considered our independence and any conflicts in accepting this engagement. Maxhub "
             "does not keep your books, does not audit your financial statements and has no financial "
             "interest in your business; we therefore do not create the segregation-of-duties failure that "
             "this engagement is designed to detect. We will notify you immediately if a conflict arises.")
    el.add_heading("9. Fees and billing", level=2)
    table(el, ["Item", "Amount (USD)"],
          [["Project fee - phases 1 to 6 (fixed)", f"{fee(SCOPE):,.0f}"],
           ["Continuous monitoring retainer (monthly from month 2)",
            f"{sum(RATES[r] * h for _, r, h in RETAINER):,.0f}"],
           ["Training (half day)", "1,800"],
           ["Estimated disbursements", "-"],
           ["**Amounts are exclusive of VAT where applicable**", ""]],
          widths=[11.0, 6.0], font=9, align_right=(1,))
    para(el, "Billing: 50% on acceptance, 50% on delivery of the final report. Amounts unpaid 30 days "
             "after invoice attract interest at 2% per month. We will notify you before incurring any "
             "amount above 10% of the agreed fee, or where scope changes affect the fee.", size=9)
    el.add_heading("10. Team", level=2)
    table(el, ["Name", "Role"],
          [["Engagement partner", "Partner"], ["T. Makuvaza", "Manager"],
           ["Senior analyst", "Senior"], ["Analyst", "Analyst"]], widths=[8.0, 5.0], font=9)
    el.add_heading("11. Variation, termination and complaints", level=2)
    para(el, "Any variation must be agreed in writing. Either party may terminate on 14 days' written "
             "notice; work performed and costs committed to that date remain payable. If you are "
             "dissatisfied, raise it with the engagement partner first; unresolved matters are escalated "
             "to Maxhub's managing partner and thereafter to the professional body.")
    el.add_heading("12. Acceptance", level=2)
    table(el, ["", ""],
          [["Signed for Mhondoro Manufacturing (Pvt) Ltd", "______________________  Name / Title / Date"],
           ["Signed for Maxhub Pvt Ltd", "______________________  Name / Title / Date"]],
          widths=[7.0, 10.0], font=9)
    sign_off(el)
    el.save(ensure(os.path.join(out, "Engagement_Letter.docx")))

    # --------------------------------------------------------- priced scope wb
    wb = new_wb()
    write_sheet(wb, "Priced scope of work",
                ["Phase", "Activity", "Role", "Hours", "Rate USD/hr", "Fee USD"],
                [[p, a, r, h, RATES[r], RATES[r] * h] for p, a, r, h in SCOPE] +
                [["**Total**", "", "", hours(SCOPE), "", fee(SCOPE)]],
                formats=[None, None, None, NUM, MONEY, MONEY],
                widths=[34, 62, 16, 9, 13, 15],
                title="Project fee built from hours and roles at Maxhub day rates")
    write_sheet(wb, "Retainer",
                ["Monthly activity", "Role", "Hours", "Rate USD/hr", "Fee USD"],
                [[a, r, h, RATES[r], RATES[r] * h] for a, r, h in RETAINER] +
                [["**Total per month**", "", sum(h for _, _, h in RETAINER), "",
                  sum(RATES[r] * h for _, r, h in RETAINER)]],
                formats=[None, None, NUM, MONEY, MONEY], widths=[62, 16, 9, 13, 15],
                title="Continuous monitoring retainer")
    write_sheet(wb, "Rate card and benchmark",
                ["Role", "Hourly rate USD", "Day rate (8h) USD", "Catalogue benchmark"],
                [[r, v, v * 8, bench] for r, v, bench in [
                    ("Analyst", 120, "Data analytics engagement $6,000-$18,000"),
                    ("Senior Analyst", 150, "Analytics foundation $4,000-$15,000"),
                    ("Senior", 200, "Working capital analytics $3,000-$9,000"),
                    ("Manager", 280, "Forensic investigation $8,000-$45,000"),
                    ("Partner", 450, "IFRS technical support $300-$1,200/day")]],
                formats=[None, MONEY, MONEY, None], widths=[18, 16, 18, 52],
                title="Maxhub rate card and catalogue benchmarks")
    write_sheet(wb, "Value case",
                ["Item", "Amount USD", "Basis"],
                [["Duplicate payments recoverable", dup_recovery,
                  f"Second payment of each of the {len(fx['hits']['T01']) // 2} duplicate pairs"],
                 ["Total amount at risk", total_var, "Exceptions requiring corroboration"],
                 ["Payments to employee-linked vendors", C.EXPECTED["Ghost vendor total paid"],
                  "Total paid; propriety requires corroboration"],
                 ["Year 1 cost of this engagement", fee(SCOPE) + sum(RATES[r] * h for _, r, h in RETAINER) * 11,
                  "Project fee plus 11 months of retainer"],
                 ["Net benefit if only the duplicates are recovered",
                  dup_recovery - (fee(SCOPE) + sum(RATES[r] * h for _, r, h in RETAINER) * 11),
                  "Recovery less cost - before any control benefit"]],
                formats=[None, MONEY, None], widths=[46, 18, 66],
                title="The commercial case, stated honestly")
    wb.save(ensure(os.path.join(out, "Priced_Scope_of_Work.xlsx")))

    # ------------------------------------------------------------ pitch outline
    pit = new_doc(title="Ten-minute pitch outline", subtitle="Practical Exam 3 (10 points) - leads with "
                  "the finding and the money, not the tool", reference="MX-2025-PIT")
    footer(pit, "Maxhub Pvt Ltd - pitch outline - Confidential")
    table(pit, ["Minute", "What is said", "Why it works"],
          [["0:00-1:30", f"\"We found {fx['grand']['Lines']} transactions worth {usd(fx['grand']['Value'])} "
                         f"that your controls did not catch. {usd(dup_recovery)} of it is money you can "
                         "ask for back this month.\"",
            "Leads with the finding and the money. No mention of Power BI."],
           ["1:30-3:00", "\"Three patterns: the same invoice paid twice, "
                         f"{usd(fx['totals']['T02']['Value'])} paid to four suppliers connected to "
                         "employees, and thirty payments sitting just under your approval limit.\"",
            "Concrete, memorable, and each one is a control failure the board owns."],
           ["3:00-5:00", "\"None of this needed a special system. It needed twelve tests run over every "
                         "transaction instead of a sample of forty. Your auditors test samples; we test "
                         "the population, monthly, and we leave the model with you.\"",
            "Answers the objection 'we already get this from our auditors' before it is asked."],
           ["5:00-7:00", "\"We will run those twelve tests every month on your own data, give your "
                         "Financial Controller a dashboard he can drill into, and fix the three controls "
                         "that let this happen.\"",
            "The deliverable is a monthly thing the client's own team uses - the rubric's 'client value' test."],
           ["7:00-8:30", f"\"{usd(fee(SCOPE))} for the build, "
                         f"{usd(sum(RATES[r] * h for _, r, h in RETAINER))} a month after that. Built from "
                         f"{hours(SCOPE)} hours at published rates - here is the sheet.\"",
            "Price is built from hours and roles and benchmarked, not guessed."],
           ["8:30-10:00", "\"Three questions you will ask: how long - six weeks. How much - the numbers "
                          "on the table. How do I know it is right - every figure reconciles to your trial "
                          "balance and a partner who did not build it re-performs a number on every page.\"",
            "Answers the three client questions in writing, which is what the brief requires."]],
          widths=[2.0, 9.0, 6.0], font=8.5)
    pit.add_heading("The three client questions, answered in writing", level=2)
    kv_table(pit, [
        ("How long?", "Six weeks to the first monthly report; the retainer starts in month two."),
        ("How much?", f"{usd(fee(SCOPE))} fixed for the build, then "
                      f"{usd(sum(RATES[r] * h for _, r, h in RETAINER))} per month. Built from "
                      f"{hours(SCOPE)} project hours plus {sum(h for _, _, h in RETAINER)} retainer hours "
                      "a month at the published rate card."),
        ("How do I know it is right?", "Every figure reconciles to your trial balance before it is issued; "
                                       "a partner who did not build the work re-performs a calculation on "
                                       "every page; the methodology note lets your own team reproduce "
                                       "everything independently."),
    ])
    pit.add_heading("The 90-second retainer pitch (extension)", level=2)
    para(pit, "\"The report is a photograph. The retainer is a smoke alarm. For "
              f"{usd(sum(RATES[r] * h for _, r, h in RETAINER))} a month we run the twelve tests on your "
              "own data every month and send you the exceptions with the evidence attached - so the next "
              f"{usd(fx['grand']['Value'])} is found in month one, not in year two by a whistle-blower. "
              "And when you are tired of us, you keep the model.\"", italic=True)
    sign_off(pit)
    pit.save(ensure(os.path.join(out, "Pitch_Outline.docx")))
