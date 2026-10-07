# Data request list — [CLIENT NAME]

**Engagement:** [title and reference] · **Period:** [start] to [end]
**Issued:** [date] · **Required by:** [date] · **Issued to:** [client contact]
**Issued by:** [Maxhub contact, email, phone]

> Send this within 24 hours of the kick-off call. An engagement that stalls in week one almost always
> stalled on data. Agree one named person who owns the request, and confirm each item as it arrives.

---

## Instructions for the client

1. Extracts must be **as at a single agreed date**; state that date when you send them.
2. Send the **rawest** format available (a CSV or Excel export, not a PDF or a screenshot).
3. Do not clean, adjust or re-key anything. If something looks wrong or blank, leave it — we would
   rather see the real data than a tidy version, and we will report the quality issues we find.
4. Include the header row exactly as the system exports it. Do not rename columns.
5. Where a report is generated from a system, send the **report definition** or a description of how it
   was generated, so we can document the data lineage.
6. Password-protect any file containing personal data and send the password by a separate channel.
7. Mark each file name with the item number below (e.g. `01_GL_extract_2024-01-01_2025-09-30.csv`).

## A. Financial ledger

| # | Item | Format | Period | Priority |
|---|---|---|---|---|
| 01 | General ledger detail (account, journal ID, date, debit, credit, description, preparer, approver, source) | CSV/XLSX | [period] | **Must have** |
| 02 | Chart of accounts with FS line mapping and normal balance | CSV/XLSX | current | **Must have** |
| 03 | Trial balance by account and month | CSV/XLSX | [period] | **Must have** |
| 04 | Year-end close and consolidation journals | CSV/XLSX | [period] | Must have |
| 05 | Opening balances as at [start] (with the audit file reference) | CSV/XLSX | opening | Must have |

## B. Transaction cycles

| # | Item | Format | Period | Priority |
|---|---|---|---|---|
| 06 | Creditor master: name, tax number, bank details, date created, created by, status | CSV/XLSX | current | **Must have** |
| 07 | Creditor invoices with purchase order, goods received note, payment date, approval and three-way match status | CSV/XLSX | [period] | **Must have** |
| 08 | Payments listing (payment run, amount, method, bank reference, approver) | CSV/XLSX | [period] | **Must have** |
| 09 | Debtor master and ageing by customer and invoice | CSV/XLSX | [period] | Must have |
| 10 | Bank statements for every account (all pages, including any closed account) | CSV/PDF | [period] | **Must have** |
| 11 | Cash book / bank reconciliation for the last 3 months | XLSX | [period] | Must have |
| 12 | Expense claims with approval and receipt-attachment status | CSV/XLSX | [period] | Must have |
| 13 | Credit notes and write-offs, with the reason and authorisation | CSV/XLSX | [period] | Must have |
| 14 | Petty cash and cash-drawer reconciliations | XLSX | [period] | If applicable |

## C. Master data and systems

| # | Item | Format | Period | Priority |
|---|---|---|---|---|
| 15 | User list with roles, permissions and last login | CSV/XLSX | current | **Must have** |
| 16 | Segregation-of-duties / access matrix by user and module | CSV/XLSX | current | Must have |
| 17 | Employee master (payroll number, department, start/leave dates, bank details) | CSV/XLSX | current | Must have |
| 18 | Journal approval workflow configuration and limits | Screenshot/PDF | current | Must have |
| 19 | Approval limits and delegation of authority schedule | PDF | current | **Must have** |
| 20 | Fixed asset register and depreciation run | XLSX | [period] | If in scope |
| 21 | Budget with version history and board approval | XLSX/PDF | [period] | If reporting scope |
| 22 | Inventory valuation and stock-count records | XLSX | [period] | If in scope |

## D. Governance and context

| # | Item | Format | Period | Priority |
|---|---|---|---|---|
| 23 | Finance delegations, procurement policy, credit policy and any recent amendments | PDF | current | **Must have** |
| 24 | Prior-year audit file, management letter and management responses | PDF | last FY | Must have |
| 25 | Any prior fraud/whistle-blower reports and the outcome | PDF | [period] | Must have |
| 26 | The whistle-blower allegation or instruction in writing | PDF | — | **Must have** |
| 27 | Organisational chart of the finance function, and who does what | PDF | current | Must have |
| 28 | Reports the client already uses (as free-format examples) | XLSX/PDF | current | Useful |

## E. Access and people

| # | Item | Detail | Needed by |
|---|---|---|---|
| 29 | Read-only access to the ERP reporting database (or a full extract) | [system name] | [date] |
| 30 | Contact list of the people who know each process | Names, roles, availability | [date] |
| 31 | Interview slots: [process owner 1], [process owner 2], [CFO] | 60 minutes each | [week] |
| 32 | Secure file-transfer method (SFTP, secure link, or agreed cloud folder) | — | Before item 01 |

## Sign-off and tracking

| # | Received | Date | File name | Checked (opens? period correct? totals tie?) | Notes |
|---|---|---|---|---|---|
| 01 | ☐ | | | ☐ | |
| 02 | ☐ | | | ☐ | |
| … | ☐ | | | ☐ | |

**On receipt of everything, Maxhub will:**

1. Record the file hash and extraction date of each extract in the data lineage log.
2. Reconcile the ledger extract to the trial balance and to the opening balances before analysing.
3. Report in writing any material differences, gaps or quality issues, and state how they affect the
   conclusions — this becomes section 2.4 of the report.

**Escalation:** if item 01 has not arrived by [date], the engagement schedule and fee assumptions are
affected; we will notify you in writing before committing further time.
