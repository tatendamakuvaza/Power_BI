# Welcome, Tatenda | Start here
This book is for learning by doing. You do not need to know programming before you start. We will begin with opening a file and making a simple chart. Later, you will learn how to calculate profit, compare months, check suspicious transactions and share a report safely.
A chart in Power BI is called a visual. A page with several charts is part of a report. We will explain other new words as we use them. The names you see inside formulas must match the names in Power BI, so those names stay exactly as they appear in your files.
## What is in your download?
Your folder contains this PDF and a folder called CSV_Tables. Inside CSV_Tables are 22 separate CSV files. Each file holds just one kind of record, such as customers, sales orders or accounting entries. A CSV is a simple table saved as a file. It cannot have worksheet tabs like an Excel workbook, so each of your tables now has its own file.
There is no longer one large mixed CSV to split up. You can open each file separately in Excel or import it straight into Power BI. Keep the first row: it contains the column names. Do not combine all 22 files into one table.
## What you need
Use Power BI Desktop on a Windows computer. It is the program used to build the reports in this book. If you use a Mac, you need access to a suitable Windows computer or Windows virtual machine. A virtual machine is a Windows computer running inside another computer.
The main exercises can be done in Desktop. Sharing online, some AI tools and automatic online updates may need an account, a licence and permission from your organisation. If you cannot use an online feature, complete the local exercise and read its explanation instead.
## How to work through a lesson
Read the short explanation. Follow the numbered steps. Make the suggested chart. Check your answer. If it differs, check your filters and data types before changing the formula. Save often using a name such as Tatenda_PowerBI_Practice.pbix. A .pbix file is your saved Power BI report.
Allow about six hours a week and work at a comfortable pace. The full course and projects may take about 110-140 hours. There is no need to finish everything in one sitting.
Use the PDF's bookmarks to jump to a lesson. Keep the final investigation answer key closed until you have tried the investigation yourself.
# Your learning plan | Twelve lessons
Module 01: Open a file, make your first chart and save your report.
Module 02: Clean your tables and tell Power BI which columns contain text, dates or money.
Module 03: Connect related tables, such as customers and their sales.
Module 04: Write formulas for totals, revenue, profit and percentages.
Module 05: Compare months and years, and calculate balances at a chosen date.
Module 06: Build a profit report, a balance sheet and a cash movement report.
Module 07: Make a report easy to read and easy to use.
Module 08: Compare actual results with plans and review unpaid bills and work hours.
Module 09: Find transactions that deserve a closer look.
Module 10: Investigate a flagged transaction without jumping to conclusions.
Module 11: Try forecasting and simple AI exercises, and understand their limits.
Module 12: Share and protect a report, keep it updated and price a reporting job.
After the lessons, choose a final project. These projects help you put the lessons together and show what you can do.
## A few helpful names
Dim means a reference list. For example, DimCustomer lists customers and their details. Fact means a table of events or amounts. FactSalesOrders lists sales orders. You do not need to memorise these words; use the file guide on the next page.
GL means general ledger: the main accounting record. AP means accounts payable: bills owed to suppliers. AR means accounts receivable: amounts customers owe the business. USD means US dollars.
A measure is a calculation, such as total sales, that Power BI works out for the part of the data currently being shown. A slicer is an on-screen filter, such as a list of years you can click.
# File guide | What each file contains
Every row below refers to one separate CSV in CSV_Tables. Import only the files needed for the lesson you are doing. “One row means” tells you what each record stands for, so you do not accidentally count the same thing twice.
@MANIFEST
# Know your practice data | Important warnings
These are made-up records for two practice businesses. Mhondoro is a manufacturer. Maxhub is a consulting business. The records are designed to give you plenty to explore, not to prove anything about real people or companies.
## Dates and money
The main accounting entries run from January 2024 to September 2025. Therefore, 2025 has only nine months of entries. Do not compare those nine months with all twelve months of 2024 and call it a fair yearly comparison.
Most amounts are already in US dollars. A column ending in USD is already a dollar amount. Do not convert it again using an exchange rate. The tax rates and exchange rates in these practice records are not advice about today's rules.
The supplied DimDate.csv lists dates from 2023 to 2026. Some other tables use earlier years. In Module 03 you will make a fresh calendar covering 2021-2026. Do not rely on the supplied FiscalPeriodEnd column to mean the last day of a month: inspect it first.
## Not every table adds up to the same total
The trial balance was calculated from the main accounting entries. Those two should agree. The supplier bills, customer bills, sales orders, bank transactions and asset list are separate practice examples. They are not complete matching copies of the main accounting records. Report their totals separately; do not force them to agree by adding an unexplained adjustment.
GrossAmountUSD in the sales orders already includes the discount. Despite its name, do not deduct the discount a second time. DiscountPct = 15 means 15%, so formulas divide it by 100. The same rule applies to MarginPct and ProbabilityPct.
A balance is an amount at one date. For example, money owed at the end of September is a balance. Adding the August and September balances usually counts some of the same money twice. You will learn to select one date rather than add every month's balance.
The bank table's BalanceUSD follows the order in which the practice records were made. Do not treat it as a checked, date-ordered bank statement balance.
## What to do if you get stuck
Clear all slicers. Check whether a chart has its own filter. Check the table name and the column's data type. Compare with the answer tables near the end. A blank means there may be no matching data; it does not always mean zero.
# Module 01 | Make your first report
## What you will learn
You will open the main accounting file, add two large number displays and make a chart. A large number display is called a Card in Power BI.
## Follow these steps
1. Unzip the download into a folder you will keep. Open Power BI Desktop and choose a blank report. Save it as Tatenda_PowerBI_Practice.pbix.
2. Click Home > Get data > Text/CSV. Open CSV_Tables/FactGLJournal.csv. Choose comma as the separator and UTF-8 as the text encoding if asked. Click Transform Data rather than Load.
3. The window that opens is called Power Query. Think of it as the place where you prepare your tables before drawing charts. Check that the query name is FactGLJournal. If not, rename it using the box on the right.
4. Click the small type symbol beside PostingDate and choose Date. Set Debit and Credit to Fixed decimal number. Set LineID, JournalID and AccountCode to Text. The column guide near the end gives types for the other columns.
5. Click Close & Apply. Power BI returns to the report. Select New measure and enter each formula below separately. A formula starts with the name you want to give it, followed by an equals sign.
```
Debit USD = SUM(FactGLJournal[Debit])
Credit USD = SUM(FactGLJournal[Credit])
Balance Check = [Debit USD] - [Credit USD]
```
6. Add a Card and drag Debit USD into it. Add two more cards for Credit USD and Balance Check. In the Format panel set display units to None so you see the full number rather than “122.88M”.
7. Add a line chart. Put PostingDate on the horizontal axis and Debit USD on the vertical axis. Use the actual PostingDate field, not the automatic date hierarchy. A hierarchy is a built-in year/month/day grouping.
8. Add a Slicer with PostingDate. Try narrowing the dates, then clear the slicer. Save the report.
## What you should see
With no filters, Debit USD and Credit USD should each be 122,878,886.54. Balance Check should be 0.00. The line chart shows how debit entries change over time. It is not yet a sales chart.
## Questions and answers
Q1. Does a zero difference prove that every entry is correct? No. An incorrect or dishonest entry can still have matching debits and credits.
Q2. Is one row a whole transaction? Not here. One row is one accounting line. JournalID groups the lines belonging to the same journal entry. LineID identifies one line.
Q3. What have I saved? A .pbix report file. It contains your report design and model. Keep your original CSV files unchanged so you can start again if needed.
# Module 02 | Get the tables ready
## What you will learn
You will import separate files, fix types and spot problems without deleting useful records. A data type tells Power BI how to read a value: as text, a date or a number.
## Follow these steps
1. Keep the FactGLJournal table from Module 01. Do not import it a second time. For each extra file, use Home > Get data > Text/CSV, choose that file and select Transform Data.
2. Start with DimAccount.csv, DimCostCentre.csv, DimCustomer.csv, DimVendor.csv, DimUser.csv and FactBudget.csv. Later lessons will tell you which other files to add. Name each query exactly like its filename, without .csv.
3. Use the column guide to choose types. Account codes, IDs and bank account numbers are Text, even when they look like numbers. This keeps leading zeros and stops Power BI trying to add them up. Money can normally use Fixed decimal number; hours, rates and model inputs may need Decimal number.
4. For dates, choose Date. For EnteredOn, choose Date/Time because it includes a time of day. If a date or decimal gives an error, use Change Type > Using Locale and check the format of the source value. These files use year-month-day dates and a dot for decimals.
5. Under View, turn on Column quality and Column profile. At the bottom, change profiling from the first 1,000 rows to the entire dataset. This makes the check look at all the rows.
6. Compare the row count of each imported table with the file guide. Do not delete rows just because ApprovedBy or VendorID is empty. Some missing values are allowed; others are part of the investigation exercises.
7. Click Close & Apply and save. Repeat these steps when importing later files. Each file becomes its own table. Do not use Combine Files on the whole CSV_Tables folder: these files do not all have the same columns.
## Questions and answers
Q1. What is the right number of GL rows? 13,929. If you get twice that number, check whether you imported or appended the same data twice.
Q2. Should I replace every blank with zero? No. A missing approver is not the number zero. Keep it blank and investigate what it means.
Q3. What if my automatic Changed Type step guessed wrongly? Delete that step and assign the types yourself. A type change should not silently remove rows or alter money totals.
# Module 02 | Practise cleaning and combining
## Three words made simple
Reference creates another query that starts from an existing query. Merge puts matching details beside a row, like adding a supplier's name to its bill. Append stacks similar rows underneath one another, like putting January and February bills in one list.
## Follow these steps
1. Right-click DimVendor in Power Query and choose Duplicate. Name it VendorPractice. Turn off Enable load for this practice copy so it does not add another table to the report.
2. Select VendorName > Transform > Format > Trim, then Clean. Trim removes unwanted spaces at the ends. Clean removes certain invisible characters. Keep the original file unchanged.
3. Import FactAPInvoices.csv. Make a practice reference of it. Select Merge Queries and match its VendorID to DimVendor[VendorID]. Choose Left Outer: this keeps every supplier bill, even if a match is missing. Expand only VendorName and Category.
4. Check the row count before and after the merge. Both should be 520. If it grows, more than one supplier row probably matched a bill. Fix the supplier list rather than accepting duplicated bills.
5. Make a reference of FactGLJournal. Select Group By > Advanced. Group by JournalID. Add sums of Debit and Credit and a Count Rows result. Add a custom column called Difference using [TotalDebit] - [TotalCredit], using the names you gave the two sum columns.
6. Filter Difference to values greater than 0.01 or less than -0.01. You should get no rows. Before that filter there should be 5,504 journal groups.
7. For an Append exercise, make two references of the GL: filter one to 2024 and the other to 2025 using PostingDate. Append them as a new practice query. The result should have 13,929 rows, not twice that number.
8. For a reshaping exercise, group FactBudget by Period and sum BudgetUSD. Pivot Period using that sum. Pivot turns the months into columns. Select those month columns and choose Unpivot Columns to turn them back into rows. The total amount must stay the same. Disable load for all practice copies.
## What you should see
A small quality-check table can show: table name, expected rows, actual rows and problems found. The correct result is not “make every warning disappear”. It is “understand and explain every warning”.
# Module 03 | Connect the tables
## The idea
Imagine a customer list and a list of sales. A sale contains a customer number. Power BI uses that number to find the customer's name in the customer list. That connection is called a relationship.
The customer list should have one row for each customer number. The sales table can have many rows for that number. Power BI calls this one-to-many, written 1:*. Use Single filter direction for these exercises. This means choosing a customer filters their sales, without making every table filter every other table.
## Make a calendar
A calendar gives all your charts the same dates. Skip importing DimDate.csv into the report; you will create a better-fitting date table here. If you already imported it, rename it SourceDate and turn off Enable load.
1. Turn off Auto date/time in the options for this file. Go to Modeling > New table and enter the formula below. This is DAX, Power BI's formula language.
```
DimDate =
ADDCOLUMNS(
    CALENDAR(DATE(2021,1,1), DATE(2026,12,31)),
    "Year", YEAR([Date]),
    "MonthNo", MONTH([Date]),
    "Month", FORMAT([Date], "MMM"),
    "YearMonth", FORMAT([Date], "yyyy-MM"),
    "YearMonthSort", YEAR([Date]) * 100 + MONTH([Date])
)
```
2. Select DimDate and choose Mark as date table, using Date. Select Month and use Sort by column > MonthNo. Sort YearMonth by YearMonthSort. There should be 2,191 dates.
3. In Model view, connect DimDate[Date] to FactGLJournal[PostingDate]. Choose one-to-many and Single direction. This connection should be active, shown as a solid line.
4. Connect DimAccount[AccountCode] to FactGLJournal[AccountCode]. Connect DimCostCentre[CostCentreCode] to the GL column with that name. Make the same connections for VendorID and CustomerID using their matching reference lists.
5. Connect DimUser[UserID] to FactGLJournal[PreparedBy]. This lets you group entries by the person who prepared them.
## Questions and answers
Q1. Why not connect tables using AmountUSD? Many unrelated rows have the same amount. An amount is not a reliable record identifier.
Q2. Why use YearMonth rather than Month? “January” alone puts January 2024 and January 2025 together. “2025-01” identifies one particular month.
Q3. Should I accept many-to-many if Power BI suggests it? Not automatically. Check for repeated IDs in the table that should contain one row per ID.
# Module 03 | Add the other useful connections
Add these connections as you import the later files. You do not need every table on the first day. “A -> B” below means match the named column in A to the named column in B, using 1:* and Single direction.
## Money and business tables
DimAccount[AccountCode] -> FactBudget[AccountCode] and FactTrialBalance[AccountCode].
DimCostCentre[CostCentreCode] -> FactBudget[CostCentreCode] and FactSalesOrders[CostCentreCode].
DimVendor[VendorID] -> FactAPInvoices[VendorID].
DimCustomer[CustomerID] -> FactARAgeing[CustomerID] and FactSalesOrders[CustomerID].
DimEmployee[EmployeeID] -> FactExpenseClaims[EmployeeID]. Import DimEmployee when doing this.
## Date connections
In FactBudget, use Power Query > Add Column > Custom Column. Name it BudgetDate and enter Date.FromText([Period] & "-01"). Set it to Date. This turns a month such as 2025-09 into 1 September 2025.
Connect DimDate[Date] to BudgetDate, FactTrialBalance[PeriodEnd], FactAPInvoices[InvoiceDate], FactSalesOrders[OrderDate], FactExpenseClaims[ClaimDate] and FactBankTransactions[TxnDate] in their separate tables.
For consulting work, connect DimDate[Date] to MaxhubEngagements[StartDate], maxhub_billable_hours[Month] and maxhub_service_line_financials[Month]. Set those columns to Date first.
For unpaid customer balances, connect DimDate[Date] to FactARAgeing[AsAtDate]. This is the date the unpaid amounts were measured, not the date the bill was created.
Leave the asset list, exchange-rate table, opportunity list and churn table separate until you need a specific connection. They do not all describe events on the same kind of date.
## Test the model
1. Make a Matrix visual with DimAccount[AccountType] as Rows and Debit USD as Values. A matrix is a table that can group and total figures.
2. Add a slicer using DimDate[Year]. Choosing 2024 should change the totals. If not, check the date relationship and whether PostingDate was set to Date.
3. In Power Query, group each reference list by its ID and count rows. No ID should appear more than once. A Left Anti merge finds rows with no match. Try GL AccountCode against DimAccount: there should be no unmatched account codes.
Answer: a relationship is working when the right totals change after you select a year, account or customer. A neat-looking diagram alone is not enough.
# Module 04 | Write useful calculations
## What a measure does
A measure is a formula that answers a question for whatever is selected. Total revenue for all years changes to revenue for 2024 when you click 2024. The selections affecting a calculation are called its filter context. Think “which rows are currently included?”
Enter each formula below separately using New measure. Keep the three measures from Module 01. SUM adds a column. CALCULATE changes which rows a measure uses. DIVIDE divides safely when the bottom number is zero or missing.
```
GL Lines = COUNTROWS(FactGLJournal)
Journals = DISTINCTCOUNT(FactGLJournal[JournalID])
Net Debit = [Debit USD] - [Credit USD]
Activity Net Debit =
CALCULATE([Net Debit],
    FactGLJournal[EntryType] <> "Opening",
    FactGLJournal[EntryType] <> "Closing")
Revenue =
-CALCULATE([Activity Net Debit], DimAccount[FSLine] = "Revenue")
Cost of Sales =
CALCULATE([Activity Net Debit], DimAccount[FSLine] = "Cost of sales")
Gross Profit = [Revenue] - [Cost of Sales]
Gross Margin = DIVIDE([Gross Profit], [Revenue])
Operating Expenses =
CALCULATE([Activity Net Debit], DimAccount[FSLine] = "Operating expenses")
Finance Costs =
CALCULATE([Activity Net Debit], DimAccount[FSLine] = "Finance costs")
Operating Profit = [Gross Profit] - [Operating Expenses]
PL Result =
-CALCULATE([Activity Net Debit], DimAccount[IsPL] = "Yes")
Net Margin = DIVIDE([PL Result], [Revenue])
PL Signed = -[Activity Net Debit]
```
## Why those rules matter
Revenue usually sits on the credit side, so the minus sign turns it into a positive reported amount. Cost of Sales is shown as a positive cost. Gross Profit subtracts that cost from revenue. Gross Margin tells you what share of revenue is left after those costs. Format the margin measures as percentages.
Opening entries bring in starting balances. Closing entries move the year's result into retained earnings, which is accumulated profit kept in the business. Exclude these entries when measuring the year's trading performance. Include them when calculating account balances.
## Check your work
Make a matrix with DimDate[Year] in Rows and Revenue and PL Result in Values. For 2024, revenue should be USD 13,786,572.99 and profit USD 447,052.47. For January-September 2025, revenue should be USD 10,543,059.22 and the result a loss of USD 61,866.98.
Question: why not average the profit percentage on each row? Answer: that gives a small sale the same importance as a large sale. Divide total profit by total revenue for the proper overall percentage.
# Module 04 | Sales, bills and consulting work
Import the files named in these formulas if you have not already done so. SUMX means “do this calculation for each row, then add the answers”.
```
Order Value = SUM(FactSalesOrders[GrossAmountUSD])
Units = SUM(FactSalesOrders[Quantity])
Order Margin USD =
SUMX(FactSalesOrders,
    FactSalesOrders[GrossAmountUSD] * FactSalesOrders[MarginPct] / 100)
Order Margin % = DIVIDE([Order Margin USD], [Order Value])
AR Outstanding =
SUMX(FactARAgeing,
    FactARAgeing[AmountUSD] - FactARAgeing[AmountReceivedUSD])
AP Invoices = COUNTROWS(FactAPInvoices)
AP Exceptions =
CALCULATE([AP Invoices], FactAPInvoices[ThreeWayMatch] <> "Matched")
AP Exception % = DIVIDE([AP Exceptions], [AP Invoices])
Net Fees =
SUM(MaxhubEngagements[FeeUSD]) - SUM(MaxhubEngagements[WriteOffUSD])
Fee per Hour = DIVIDE([Net Fees], SUM(MaxhubEngagements[ActualHours]))
Utilisation =
DIVIDE(SUM(maxhub_billable_hours[BillableHours]),
    SUM(maxhub_billable_hours[AvailableHours]))
Weighted Pipeline =
SUMX(maxhub_pipeline,
    maxhub_pipeline[ExpectedFeeUSD] * maxhub_pipeline[ProbabilityPct] / 100)
```
## Follow these steps
1. Make a bar chart with ProductFamily and Order Value. Each bar shows the value of orders in one product group. All bars together should total USD 33,948,013.24 with no filters.
2. Make a Card with AR Outstanding. With no filters it should be USD 9,781,168.34: amounts billed less amounts received.
3. Make a Card with AP Exception %. It should be 32.31%. A three-way match compares a supplier bill, purchase order and goods-received record. An exception means something did not match; it does not prove theft.
4. Make a matrix with MaxhubEngagements[ServiceLine], Net Fees and Fee per Hour. Make a separate utilisation chart using the billable-hours table. Utilisation means the share of available hours spent on chargeable work; the total should be 55.56%.
5. For a calculated-column exercise, choose FactSalesOrders > New column and enter: Discount Band = IF(FactSalesOrders[DiscountPct] >= 10, "10% or more", "Below 10%"). Unlike a measure, this adds a stored label to each row. Clicking a slicer does not recalculate those stored labels.
Question: is Weighted Pipeline money already earned? No. It estimates possible future work using each opportunity's stated chance of success. Do not add it to earned revenue.
# Module 05 | Compare months and years
## Follow these steps
1. Use New measure to enter the formulas below. PY means previous year. YTD means from 1 January up to the selected date. YoY means compared with the same time in the previous year.
```
Revenue YTD = TOTALYTD([Revenue], DimDate[Date])
Revenue PY =
CALCULATE([Revenue], SAMEPERIODLASTYEAR(DimDate[Date]))
Revenue YoY = [Revenue] - [Revenue PY]
Revenue YoY % = DIVIDE([Revenue YoY], [Revenue PY])
Revenue Rolling 3M =
CALCULATE([Revenue],
    DATESINPERIOD(DimDate[Date], MAX(DimDate[Date]), -3, MONTH))
Revenue Share of CC =
DIVIDE([Revenue], CALCULATE([Revenue], REMOVEFILTERS(DimCostCentre)))
CC Revenue Rank =
RANKX(ALL(DimCostCentre[CostCentreName]), [Revenue], , DESC, DENSE)
```
2. Make a matrix with DimDate[YearMonth] in Rows and Revenue, Revenue YTD and Revenue PY in Values. Filter the dates to January 2024-September 2025. Compare each month with the Monthly answers section.
3. For a fair yearly comparison, select 1 January-30 September 2025 using DimDate[Date]. Revenue PY should be USD 9,931,338.13 and Revenue YoY % should be 6.16%.
4. Make a cost-centre bar chart with Revenue. A cost centre is a department or location used to group costs and activity. Add Revenue Share of CC as a tooltip. The formula removes the cost-centre selection from the bottom part of the fraction but keeps the date selection. This answers “what share of total revenue is this centre?”
## Questions and answers
Q1. Why is October 2025 blank? The accounting data ends in September. A missing month is not proof that the business earned nothing.
Q2. What is a rolling three-month amount? The total over the three-month window ending at the chosen date. Use month-end selections when comparing full months.
Q3. Why use the calendar slicer? These formulas use DimDate. A separate filter directly on the GL's Period column can remain in place and give an unexpected result. Use the calendar fields consistently.
# Module 05 | Balances and what-if questions
A balance answers “how much was there by this date?” rather than “how much happened during this month?” These measures add GL movements from the beginning through the selected date.
```
Closing Net Debit =
VAR Cutoff = MAX(DimDate[Date])
RETURN
CALCULATE([Net Debit],
    FILTER(ALL(DimDate), DimDate[Date] <= Cutoff))
```
## Check the balance against the trial balance
The trial balance is a month-end list of account balances. In this file, some balances are stored in the opposite sign from Debit minus Credit. The following formula changes them to the same sign before comparing. RELATED looks up the account's normal side in DimAccount. NormalBalance tells you whether a debit or credit normally increases the account.
```
TB Closing Debit Signed =
VAR Cutoff = MAX(DimDate[Date])
VAR LastSnapshot =
    CALCULATE(MAX(FactTrialBalance[PeriodEnd]),
        REMOVEFILTERS(DimDate), REMOVEFILTERS(DimAccount),
        FactTrialBalance[PeriodEnd] <= Cutoff)
RETURN
CALCULATE(
    SUMX(FactTrialBalance,
        FactTrialBalance[ClosingBalance] *
        IF(RELATED(DimAccount[NormalBalance]) = "Debit", 1, -1)),
    REMOVEFILTERS(DimDate), FactTrialBalance[PeriodEnd] = LastSnapshot)
TB Reconciliation = [Closing Net Debit] - [TB Closing Debit Signed]
```
1. Import FactTrialBalance and add the relationships in Module 03. Make a matrix with AccountCode, Closing Net Debit, TB Closing Debit Signed and TB Reconciliation.
2. Select 30 September 2025. Each account's difference should be zero, allowing one cent for rounding. Repeat for 31 December 2024. Reconciliation simply means checking that two records agree.
3. Do not apply a vendor or cost-centre filter during this comparison: the trial balance does not have that level of detail. Also do not expect a mid-month GL balance to equal the previous month's trial balance.
## Try a what-if slider
Choose Modeling > New parameter > Numeric range. Name it Price Change. Use minimum -0.20, maximum 0.20, step 0.01 and default 0. Format it as a percentage and add its slicer. Power BI usually creates a measure called Price Change Value. Use that exact generated name in these formulas.
```
Scenario Revenue = [Revenue] * (1 + [Price Change Value])
Scenario Profit = [PL Result] + ([Scenario Revenue] - [Revenue])
```
Answer: moving the slider to 10% makes estimated revenue 1.10 times actual revenue. Estimated profit rises by 10% of revenue only because this example assumes sales quantity and costs stay unchanged. It is an assumption test, not a prediction.
# Module 05 | Optional: two different dates
An entry can have a document date and a posting date. The document date is on the original document. The posting date is when the entry belongs in the accounting records. You may want to report using either date.
1. In Model view, add a second relationship from DimDate[Date] to FactGLJournal[DocumentDate]. Leave it inactive. Inactive means Power BI will not use it unless a formula asks for it. The usual PostingDate relationship remains active.
2. Create this measure and compare it with Debit USD by YearMonth.
```
Document Date Debit =
CALCULATE([Debit USD],
    USERELATIONSHIP(DimDate[Date], FactGLJournal[DocumentDate]))
```
Expected result: some monthly totals may move because the dates differ. With no date filters, both measures include all GL debit amounts and should equal USD 122,878,886.54.
The same idea applies to PreparedBy and ApprovedBy. One person enters a transaction; another may approve it. If you need two independent on-screen lists of people, make a separate reference copy of DimUser called Approver and connect it to ApprovedBy. Do not casually turn on several competing filter routes.
Question: why not make every possible relationship active? Answer: Power BI could have more than one route for deciding which records to include. That can create errors or confusing totals. Add a connection only when you can explain what question it answers.
# Module 06 | Show profit and financial position
## Make the profit report
1. Add a page called Profit Report. Add a matrix with DimAccount[FSLine] and AccountName in Rows, YearMonth in Columns and PL Signed in Values.
2. In the visual's filters choose DimAccount[IsPL] = Yes. IsPL means the account belongs in profit or loss. This filter matters: without it you include balance-sheet accounts too.
3. Add cards for Revenue, Gross Profit, Gross Margin and PL Result. PL Signed shows income as positive and expenses as negative, so the matrix total gives profit or loss.
## Make the balance sheet
A balance sheet shows what the business owns, owes and has left for its owners at a particular date. Assets are what it owns. Liabilities are what it owes. Equity is the owners' remaining interest.
```
Assets =
CALCULATE([Closing Net Debit], DimAccount[AccountType] = "Asset")
Liabilities =
-CALCULATE([Closing Net Debit], DimAccount[AccountType] = "Liability")
Equity Posted =
-CALCULATE([Closing Net Debit], DimAccount[AccountType] = "Equity")
Unclosed PL =
-CALCULATE([Closing Net Debit], DimAccount[IsPL] = "Yes")
BS Check = [Assets] - [Liabilities] - [Equity Posted] - [Unclosed PL]
```
1. Add a Balance Sheet page and a date slicer. Choose 30 September 2025. Make cards for these measures.
2. Assets should be USD 8,949,384.37; liabilities USD 4,756,698.88; recorded equity USD 4,254,552.47. Unclosed PL should be a loss of USD 61,866.98. BS Check should be 0.00.
3. Add an account table with Closing Net Debit. Credit balances show as negative in this table. Label that clearly because the liability and equity cards above switch them to positive presentation amounts.
## Questions and answers
Q1. Why include Unclosed PL? The current result has not yet been transferred into equity by a year-end closing entry. It still belongs in the balance-sheet check.
Q2. Can I turn every negative balance positive? No. Some negative asset accounts reduce asset values, such as accumulated depreciation. Changing every sign makes the balance sheet wrong.
Q3. Is this a complete legal set of financial statements? No. It is a learning report. Real financial statements need appropriate policies, notes, tax treatment and professional review.
# Module 06 | Follow the cash
Profit is not the same as cash. A sale can earn revenue before the customer pays. A cash report answers how cash changed over a period.
```
Cash Movement =
CALCULATE([Net Debit], DimAccount[IsCashAccount] = "Yes")
Cash Closing =
CALCULATE([Closing Net Debit], DimAccount[IsCashAccount] = "Yes")
Cash Opening =
VAR StartDate = MIN(DimDate[Date])
RETURN
CALCULATE([Cash Movement],
    FILTER(ALL(DimDate), DimDate[Date] < StartDate))
Cash Bridge Check = [Cash Opening] + [Cash Movement] - [Cash Closing]
```
1. Make a Cash page and select the whole period 1 January-30 September 2025. Add cards for the four measures. Use a continuous date range with no extra account filters.
2. Expected answers: opening USD 925,427.08; movement minus USD 132,878.67; closing USD 792,548.41; check 0.00. A minus movement means cash fell.
3. Make monthly columns for Cash Movement and a separate line chart for Cash Closing. One shows changes; the other shows the running balance.
4. For an advanced cash-flow exercise, inspect the other accounts in each cash journal and label its purpose as day-to-day operations, asset investment, financing or transfer between cash accounts. Transfers between the business's own bank accounts are not new external cash. Put uncertain items on a review list.
## Assets and foreign currency
Import FactFixedAssets. Make a table with AssetClass, CostUSD, AccumulatedDepreciationUSD and NBVUSD. Depreciation is the recorded use-up of an asset's cost. NBV means cost less accumulated depreciation. Across the list, NBVUSD should total USD 2,563,109.24. Do not assume this separate practice list agrees with the GL asset accounts.
Import DimFXRate for inspection. Show currency, month, AverageRate and ClosingRate in a table. Rates are not amounts to add together. If a rate means “USD for one foreign unit”, multiply a foreign amount by it to get USD. Do not apply it again to an amount already marked USD.
Question: have you made a full cash-flow statement? Not yet. You have checked opening cash plus movement equals closing cash. A full statement also needs checked classifications and the appropriate accounting rules.
# Module 07 | Make your report easy to read
## Pick a chart that suits the question
Use a line for change over time, bars for comparisons, a matrix for exact figures and a table for transaction details. A scatter chart places each item using two numbers, such as hours worked and fees earned. It helps you spot unusual combinations.
Use a few clear colours. Label dollars and percentages. Do not rely only on red and green, because some people cannot distinguish them easily. Avoid crowded pie charts and tiny text.
## Build your front page
1. Set the page to widescreen, usually 16:9. Add a title: “Mhondoro performance to September 2025”.
2. Across the top, place Revenue, Gross Profit, Gross Margin and PL Result cards. Under them, add the monthly revenue line on the left and cost-centre revenue bars on the right.
3. Add Year and CostCentreName slicers. Check that the cards and charts respond correctly. Add a note saying that 2025 contains January-September only.
4. Make separate pages for financial reports, operations, investigations and Maxhub consulting work. Do not make the front page show every transaction.
## Add useful ways to explore
A tooltip is the small information box shown when you hover. Add Revenue PY and Revenue YoY % to the revenue chart's tooltip fields.
Drill-through means opening a detail page for an item you clicked. Create a new page, place JournalID in its drill-through field and add a table containing LineID, AccountCode, Debit, Credit, PreparedBy and ApprovedBy. Add a Back button. From a JournalID table on the main page, right-click a journal and use Drill through.
A bookmark remembers a report view. Use View > Bookmarks to save an Overview and a Detail view. For navigation-only bookmarks, turn off the Data option so the bookmark does not unexpectedly change slicers. For a Reset Filters bookmark, deliberately save the starting filter settings.
Use Edit interactions to decide which charts affect one another. Use Mobile layout to put important cards above charts for phone users. Add alt text, which describes a visual for a screen reader, and check the tab order for keyboard users.
Question: what should the drill-through page show? The chosen journal's accounting lines under the current filters. Show its JournalID in the page so the reader knows what they are looking at.
# Visual example | Your revenue chart
@CHART
This chart was drawn from the data to show the shape your revenue results should have. It is not a screenshot of Power BI. You can make a line chart instead of columns; the monthly amounts should be identical.
1. Choose a line chart. Put DimDate[YearMonth] on the horizontal axis and Revenue on the vertical axis.
2. Sort months from earliest to latest. Keep January 2024 through September 2025. Do not display later empty months as if they were actual zero sales.
3. Turn on a clear axis title: Revenue (USD). Add previous-year revenue to the tooltip.
4. Compare each point with Monthly answers. If one month differs, check whether you included closing entries or clicked a cost-centre filter.
Expected result: 21 monthly revenue amounts. The answer is about matching the numbers and labelling them clearly, not copying a particular colour or font.
# Module 08 | Compare actual results with the plan
A budget is a plan. A variance is the difference between actual and planned amounts. More revenue than planned is usually favourable. More spending than planned is usually unfavourable.
```
Budget USD = SUM(FactBudget[BudgetUSD])
Revenue Budget =
CALCULATE([Budget USD], DimAccount[FSLine] = "Revenue")
Revenue Variance = [Revenue] - [Revenue Budget]
Revenue Variance % = DIVIDE([Revenue Variance], [Revenue Budget])
Cost Budget =
CALCULATE([Budget USD], DimAccount[FSLine] = "Cost of sales")
Cost Variance = [Cost of Sales] - [Cost Budget]
```
1. Check the budget relationships from Module 03. Make a matrix with YearMonth, Revenue, Revenue Budget and Revenue Variance. Select January-September 2025.
2. Make a clustered column chart: put actual and budget revenue beside one another for each month. Add a waterfall chart using cost centre and Revenue Variance. A waterfall shows which groups add to or reduce the overall difference.
3. Expected answers: revenue budget USD 10,559,589.34; actual revenue USD 10,543,059.22; difference minus USD 16,530.12, or -0.16%. Actual revenue is slightly below plan.
4. Compare full months. Budget rows use the first day of each month. Selecting only 15-30 September excludes the September budget row. Do not divide the monthly budget across days unless you clearly state the rule you are using.
Question: should every positive variance be green? No. Positive revenue variance is normally good; positive cost variance means overspending. Use a label as well as colour.
## Look at work hours
Make a line chart with maxhub_billable_hours[Month] and Utilisation. Add a consultant-name slicer. The overall calculation is total billable hours divided by total available hours, not the average of the displayed percentages.
Make a scatter chart with MaxhubEngagements[ActualHours] on the horizontal axis, FeeUSD on the vertical axis and EngagementID in the detail/category field. Each point is one job. Investigate a high-hours, low-fee job by comparing planned hours, actual hours and write-offs before recommending a price change.
# Module 08 | Check unpaid amounts and other problems
## Unpaid customer bills
1. Import FactARAgeing and connect CustomerID and AsAtDate as explained earlier. Ageing means grouping unpaid amounts by how overdue they are.
2. Select 30 September 2025 as the measurement date. Make a bar chart with AgeingBucket and AR Outstanding. Put the buckets in time order, not alphabetical order, using a small helper sort column if necessary.
3. Make a table with CustomerName and AR Outstanding. Sort the largest amount first. Add these measures for overdue bills.
```
Overdue AR =
CALCULATE([AR Outstanding], FactARAgeing[DaysOverdue] > 0)
Overdue % = DIVIDE([Overdue AR], [AR Outstanding])
```
4. Look at DisputedFlag separately. A disputed bill may need a different action from an ordinary late payment. The full outstanding amount is USD 9,781,168.34 with no customer filters.
## Supplier, expense and bank checks
Make a table of AP bills where ThreeWayMatch is not Matched. Expected: 168 of 520 bills, or 32.31%. Make another table where PONumber is blank: 109 bills. These two lists can overlap, so do not add their counts as if all bills were different.
Import FactExpenseClaims and filter ReceiptAttached = No. Expected: 81 of 650 claims, or 12.46%. Import FactBankTransactions and filter ReconciledFlag = No. Expected: 129 of 1,400 rows, or 9.21%. Reconciled means matched or checked against the other relevant record; an unmatched bank item needs investigation, not an automatic fraud label.
## Questions and answers
Q1. Can I calculate a reliable “days to collect cash” figure here? Not without matching average receivables and credit sales for the same period. DSO, days sales outstanding, is average trade receivables divided by period credit sales, multiplied by days in the period. A single balance from an independent practice table is not enough for a checked figure.
Q2. What is DPO? Days payable outstanding: average trade payables divided by period credit purchases, multiplied by days in the period. It has the same need for matching inputs.
Q3. Does a large customer balance mean the customer is dishonest? No. Check terms, payment history, disputes and timing before deciding what action is needed.
# Module 09 | Find items that need a closer look
A flag is a warning to check something, not a verdict. Many normal transactions will trigger simple rules. Keep the original CSV files unchanged and write down exactly what each test looks for.
The GL file does not include the hidden answer labels. The final PDF pages list the deliberately planted cases. Some other files contain review flags; treat those as clues, not proof.
## Six supplier and payment tests
1. Possible duplicates: in a GL reference query keep Debit > 0 and VendorID not blank. Group by VendorID and Debit; count rows and keep All Rows. Keep groups with more than one row. Expand the detail and compare dates within 30 days and invoice references inside Description. The same supplier and amount alone are not enough to prove a duplicate.
2. Shared bank details: import DimEmployee. Merge DimVendor with it on BankAccount, using Text on both sides and an Inner join. Inner means keep only matches. Inspect the employee and vendor names. Four vendors have the supplied employee-link flag. Check the independent bank matches rather than trusting that flag alone.
3. Amounts just below approval limits: filter positive Debit values from 4,900 up to but not including 5,000. Also inspect 9,500 up to but not including 10,000. Make a histogram, which groups amounts into size bands, using USD 100 bands. Ask whether those approval limits actually apply to the transactions.
4. Split purchases: group positive-debit supplier rows by VendorID and PostingDate. Keep groups with at least two rows, each debit below 5,000 but the group total above 5,000. Inspect invoices and descriptions. Several ordinary purchases on one day may be legitimate.
5. Round amounts: on positive-debit rows use a Power Query custom column: Number.Mod([Debit], 1000) = 0. Filter Debit > 5000. This finds amounts exactly divisible by 1,000. Compare users and purposes rather than labelling every round amount suspicious.
6. Newly added suppliers: merge VendorCreatedOn onto supplier GL rows. Add Duration.Days([PostingDate] - [VendorCreatedOn]). Review values from 0 to 30 days. Separately investigate negative values: they mean a posting predates the recorded supplier creation date.
## What to show and how to check
Build a supplier table with name, matching employee bank details, candidate JournalID and debit amount. Add the amount-band chart and a way to open journal details.
The planted duplicate case contains 21 pairs, or 42 journals. Their combined value is USD 368,023.48. If one entry in each pair is an unnecessary payment, the possible excess is USD 184,011.74. Your candidate list can be larger because normal repeated amounts may also match the rule.
Question: does the GL prove that cash left twice? No. You also need payment and bank-clearing evidence. Two accounting entries are not automatically two cash payments.
# Module 09 | Check journal entries and approvals
## Six more checks
1. Manual and weekend entries: filter EntryType = Manual. In Power Query add Date.DayOfWeek([PostingDate], Day.Monday) >= 5. True means Saturday or Sunday. For late-night entry, inspect the time in EnteredOn: before 07:00 or from 20:00 onwards. Posting date and entry time answer different questions; state which one you used.
2. Missing or self approval: look for ApprovedBy that is null or empty after trimming spaces. For self approval, require a nonblank ApprovedBy equal to PreparedBy. A blank preparer and approver must not count as self approval. For money totals, count only positive-debit lines so you do not add both sides twice.
3. Late or backdated entries: calculate Duration.Days([PostingDate] - [DocumentDate]) and review gaps of at least 10 days. Also compare Date.From([EnteredOn]) with PostingDate. A date gap may have an innocent explanation; request supporting evidence.
4. Unusual duties: merge user details on PreparedBy and account details on AccountCode. Review USR-002 entries on Revenue accounts. This user is an accounts-payable clerk. Check the person's actual authority before deciding a rule was broken.
5. Unbalanced or rare entries: repeat Module 02's journal balance check; expected unbalanced journals above one cent: zero. Separately group by PreparedBy and AccountCode and inspect combinations with fewer than three lines. Rare means uncommon, not automatically wrong.
6. Missing reversals: find accrual entries, which record costs or income before the final bill/payment, then search the next period for the expected reversing entry. Compare amount, account, date and description. You cannot prove an October reversal is absent from a file ending in September.
## Exact answers for selected rules
The table below uses all GL rows and precisely the rules printed in its first column. It shows line counts, not distinct journal counts. “Sum Debit” adds only the Debit column of the selected lines.
@RULES
Do not compare your custom test with this answer unless the dates, thresholds and row rules are the same. Two tests can flag the same journal. To count unique cases across tests, count distinct JournalID values rather than adding the test counts.
# Module 09 | Number patterns and review priorities
## A careful Benford exercise
Benford's law describes how first digits can be distributed in some naturally occurring amounts. It is not a rule that every honest dataset must follow. Prices set in bands, assigned IDs and small samples are poor choices for strong conclusions.
1. Make a reference of the GL. Keep Debit >= 10. Use only the debit side, not both debit and credit.
2. Add a custom column called FirstDigit using the expression below. It takes the first whole-number digit of each amount.
```
Number.FromText(
    Text.Start(Text.From(Number.RoundDown([Debit]), "en-US"), 1))
```
3. Group by FirstDigit and count rows. Divide each digit's count by the total number of selected rows. Create a small 1-to-9 digit table with Enter Data so missing digits can still be shown as zero.
4. Add expected percentages: digit 1 = 30.10%, 2 = 17.61%, 3 = 12.49%, 4 = 9.69%, 5 = 7.92%, 6 = 6.69%, 7 = 5.80%, 8 = 5.12%, 9 = 4.58%. The formula is LOG10(1 + 1 / digit).
5. Make clustered columns comparing actual and expected percentages. This practice data deliberately uses bounded amounts and repeated price bands. Differences do not prove fraud. The exercise teaches the method and its limits.
## Give your review list a score
Make one row per JournalID. Add five yes/no flags: duplicate candidate, missing approval, weekend posting, self approval and supplier-employee bank link. Give them weights 30, 20, 15, 15 and 20 respectively. Add a weight once per journal when the flag is true.
Answer: the score ranges from 0 to 100. Sort the highest score first, then the highest positive-debit journal value. It is a way to decide what to check first, not the percentage chance that someone committed fraud. These weights are your stated judgement, not a scientific law.
Question: why not multiply every flagged line's value by its score and call that the loss? A journal can appear on several lines and in several tests. Scores prioritise review; they do not establish loss.
# Module 10 | Investigate without jumping to conclusions
## Follow one case from start to finish
1. Choose one possible duplicate pair and one supplier-bank match from your own results. Do this before reading the answer key.
2. Keep a note of the source filename, date range, query steps, JournalID and LineID. Save an unchanged copy of the data. A file hash is an optional digital fingerprint used to check whether a file changed; these are listed at the end.
3. Write down two possible explanations. For the duplicate: an accidental repeat, or two valid purchases with the same amount. For the bank match: an undisclosed employee connection, or an authorised shared account.
4. Use Enter Data to make a review table with CaseID, JournalID, TestName, AmountToCheck, Status, Owner, EvidenceNeeded, Finding and Reviewer. This is your evidence register: a list of what you checked and what supports your conclusion.
5. Ask for the invoice, purchase order, delivery/receipt record, approval record and bank payment proof. For supplier links, ask for ownership and account-authorisation evidence through an approved process. In this fictional exercise those documents are not supplied, so say “not provided”. Do not invent them.
6. Write a short finding using the example below. Separate what you observed from what you suspect. Ask someone else to review it.
## Example of a careful finding
“Two journals have the same supplier, amount and invoice description within the review period. They may be duplicate entries. Bank payment evidence has not been provided, so two payments have not been confirmed. The possible extra amount is one repeated entry, not the sum of both. The payment owner should compare the invoice, delivery record and bank settlement before deciding whether correction or recovery is needed.”
## Questions and answers
Q1. Is the full planted value of USD 1,945,536.55 a proven loss? No. It is the one-side value of the 171 planted journals. It includes both entries of duplicate pairs and other different issues. A flag total is not a confirmed cash loss.
Q2. What would change the possible loss? A valid second purchase, an unpaid invoice, a reversal, a recovery or overlap with another case. Check these before making a money claim.
Q3. What should management receive? A short summary of the period checked, tests used, facts found, amounts needing review, missing evidence, recommended action and the person responsible.
Your completed work should include the report, the review list and two short case write-ups. After finishing, compare your JournalIDs with the final answer key. Explain missed cases and false alarms instead of quietly changing the test until it matches.
# Module 11 | Forecasting and AI in simple terms
Forecasting estimates future results. AI tools can help look for patterns or draft explanations. Neither guarantees the future or proves why something happened. Always compare a clever method with a simple starting method, called a baseline.
## Try a simple sales forecast first
1. Find July, August and September 2025 Revenue in Monthly answers. Add them and divide by three.
2. Your answer should be USD 1,275,666.48. Use that as an illustrative estimate for each of October, November and December 2025. Make a small table with Enter Data and label it “three-month average estimate”, not actual revenue.
3. To test a forecasting method fairly, pretend you stopped in June. Use data only through June to estimate July-September, then compare those estimates with the actual answers. This is called backtesting.
4. Calculate each error as estimate minus actual. MAE means average absolute error: ignore the minus signs and average the error sizes. RMSE squares each error, averages the squares and takes a square root, giving larger misses more weight.
## Optional built-in forecast
Make a single-series line chart using monthly dates on a continuous date axis and Revenue as the value. Keep data through September 2025. In the Analytics pane, look for Forecast and choose three months and a 95% interval. This shaded interval shows model uncertainty, not a promise. Menu availability depends on the chart setup and your version.
If Forecast is unavailable, the simple average exercise above is sufficient. There are only 21 months of GL data, so do not make confident claims about a long annual pattern.
## Try Key influencers
A Key influencers visual looks for factors associated with an outcome. Import AP invoices and related vendor details. Add a column called HasPO that says Yes when PONumber is present and No when it is blank. Use ThreeWayMatch as the outcome and amount, supplier category, payment terms and HasPO as possible explaining factors.
Do not use invoice IDs or the answer labels as explaining factors. Read any result as “these things appear together”, not “one definitely caused the other”. Missing purchase-order information may already be part of how a failed match is defined. A grouped chart of failure rate by HasPO is a simpler alternative.
Question: what exact influencer multiplier should you find? There is no guaranteed number. Filters and software versions can change results. Write down the actual output and sample size; do not copy an invented result.
# Module 11 | Which clients may leave?
Churn means a client leaves. In maxhub_client_churn.csv, Stayed = 1 means the client stayed and Stayed = 0 means the client left. One row represents one client in one year, so the same client can appear more than once.
## Follow these steps
1. Import maxhub_client_churn.csv. Set Year and Stayed to Whole number. Create a column: Churn = 1 - maxhub_client_churn[Stayed]. Now Churn = 1 means the outcome you are trying to detect: leaving.
2. Create reference queries for training years 2021-2023, practice-check year 2024 and final-test year 2025. Training data helps develop a method. The practice-check set, normally called validation data, helps choose settings. Keep the final-test set untouched until the method is fixed.
@TRAIN
3. Start with a deliberately simple rule: predict that every 2025 client leaves, because leaving is the most common outcome in the training years. Add a calculated column Baseline Prediction = 1 if you want to draw this rule in Power BI.
4. Make a matrix, filtered to Year = 2025, with actual Churn as Rows, Baseline Prediction as Columns and Count of ClientID as Values. Counting rows is appropriate here because each client occurs once in the selected year. Turn on the row totals.
5. The baseline gets 18 of 30 test rows correct: 60%. It catches all 18 clients who leave, but also wrongly flags the 12 who stay. Predicting everyone will leave is not a useful retention plan just because it catches every departure.
6. Try a second fixed rule: Predict leaving when NPS <= 6. NPS here is the supplied client satisfaction input; do not confuse a row-level score with an overall net promoter percentage. Create: NPS Prediction = IF(maxhub_client_churn[NPS] <= 6, 1, 0). Repeat the matrix.
## Read the results in plain language
For the NPS rule, among 2025 rows: 3 leavers are correctly flagged, 4 stayers are wrongly flagged, 8 stayers are correctly left unflagged and 15 leavers are missed. Accuracy is 11/30 = 36.67%, worse than the simple baseline.
Precision asks “of those we flagged, how many really left?” Here it is 3/7 = 42.86%. Recall asks “of all who left, how many did we catch?” Here it is 3/18 = 16.67%. A confusion matrix is simply the table showing these right and wrong predictions.
Question: can we now sell this rule as a reliable future prediction? No. The same-year satisfaction scores may not have been available before departure. That would use future information by mistake, called leakage. A real project needs clearly dated inputs, later outcomes and a much stronger check.
# Module 11 | Optional modelling and safe AI use
## If you want to go further
A trained model learns a rule from examples. Logistic regression is one relatively simple model that estimates the chance of a yes/no outcome. Python and R are programming languages that can run such models; you do not need them for the core exercises above.
1. Define the moment of prediction and the later outcome period. For example, use only information known by the end of one year to predict departure in the following year.
2. Match prior-year inputs to next-year outcomes for each client. This reduces the available rows. Record how many remain. Do not use a final payment date to predict an outcome that happened before that payment date was known.
3. Fit missing-value replacements and scaling using training data only. Scaling puts differently sized numbers onto comparable ranges. Train a simple model and choose its decision cutoff using validation data, not test data.
4. Evaluate on the held-out test year once. Compare accuracy, precision and recall with the baseline. Report the cost of false alarms and missed departures. The same clients appear across years here, so this tests later outcomes of existing clients, not performance on completely new clients.
5. AUC checks whether probability scores tend to rank real leavers above stayers. Calibration checks whether, for example, items given a 30% risk actually have an outcome rate near 30%. Neither can be claimed from an untested model.
AutoML automates some model-building steps. Copilot can help draft content or formulas. Their availability depends on licences, capacity and tenant settings. Check what your organisation permits; do not assume they are included with Desktop. The simple local rules above complete the required practical work.
## Use AI as an assistant, not a decision-maker
Ask an approved tool: “Give three possible explanations for this grouped exception rate, and say what evidence would test each one. Do not accuse anyone or invent records.” Use made-up or authorised information only. Check every suggested calculation against the answer totals.
For an invoice-reading exercise, draw this process: receive document -> extract fields -> check amounts and dates -> match supplier -> human review -> approve. OCR means software reading text from a document image. This pack contains no invoice images, so this is a design exercise, not a claim that you ran OCR.
Expected answer: low-confidence or inconsistent fields go to a person for review. Keep the original document reference and any corrections. A document's own text must not be allowed to instruct the system to bypass approvals or change payment details.
Question: what should you report if a model performs badly? Say so. Recommending better data or no deployment is a valid result. Do not invent an accuracy score to make a project look successful.
# Module 12 | Share and protect your work
## What sharing means
Desktop builds the report. The Power BI Service is the online place where people can view shared reports. A report can contain several pages. A Service dashboard is a separate screen made from pinned items. Publishing a report and creating a dashboard are not the same action.
## Follow these steps
1. Save a backup of your .pbix. If your account permits it, publish to a private training workspace, which is an online area for a team. Only synthetic data should be used for this lesson.
2. Decide who should see which records. Row-level security, called RLS, restricts rows for a viewer. Hiding a column from the field list is not security.
3. In Desktop choose Manage roles, create HarareOnly and add this filter to DimCostCentre: [CostCentreCode] = "CC200". Choose View as and test the role.
4. Check GL, budget and sales results: they should match a normal CC200 cost-centre filter. Also inspect other tables. The role will not automatically restrict unrelated tables such as client churn. Do not share all tables with this role and assume everything is protected.
5. In the Service, assign the role to the intended viewer or group and test as an actual Viewer. People with powerful workspace permissions may not behave like ordinary viewers. Check each person's effective access.
## Keep the data updated
Refresh means reading the source files again. Desktop can read files from your computer. Online refresh usually cannot read your computer's private folder without a configured gateway, which is a secure bridge to the data source. An approved cloud-file source may be an alternative.
Check paths, source access and credentials, trigger a refresh, then compare row counts and money totals. A green “refresh succeeded” message does not prove the new data is correct. Do not put passwords into the report notes.
Question: should I use Publish to web for private financial reports? No. It is intended for public access, not confidential sharing. Use approved private sharing and permissions instead.
# Module 12 | Speed, handover and pricing
## Make the report easier to maintain
Use Performance Analyzer to record how long visuals take. Remove unused columns and unnecessary charts. Avoid displaying thousands of long descriptions on the front page. Keep a list of your measures and what each one means.
Import mode copies source data into the model, which suits these CSV files. DirectQuery asks a supported source for results when needed; it is not a way to query a local CSV directly. Incremental refresh updates selected time periods rather than everything, but a CSV may still need to be read broadly. For that advanced topic, plan a suitable database source rather than claiming this file setup proves a fast production solution.
Keep development changes separate from the report people rely on. A release checklist should include totals, date filters, permissions, refresh and clear labels. Give the owner written steps for changing file paths, checking failures and contacting support.
## Price a small reporting job
1. Write the business question, users, dates and files included. Example: monthly profit reporting and payment checks for a finance manager.
2. List what you will deliver: prepared tables, calculations, six report pages, permission checks, refresh instructions and a training session. Say what is not included, such as a legal fraud opinion or fixing the client's accounting system.
3. Estimate work: understanding the request 6 hours, preparing data 12, calculations and connections 16, charts 10, testing/security 8 and training/handover 4. Total: 56 hours.
4. At an illustrative USD 50 per hour, the base price is USD 2,800. Add an openly stated 15% allowance for uncertainty: USD 420. Total quote: USD 3,220 before tax and licences. These are practice assumptions, not a claim about market rates.
5. Example payments: 30% at the start = USD 966; 40% after the report is accepted = USD 1,288; 30% at handover = USD 966. Put timing and conditions in writing.
6. Define acceptance: agreed totals match, the right users see the right rows, refresh works, and the client understands the main calculations. Agree in writing before adding new files, companies or pages outside the scope.
Question: what makes a good handover? Someone else can update the report, check it and understand its limits without guessing what you did.
# Four final projects | Put the lessons together
## Project 1: Investigate possible duplicate payments
Build the supplier tests and journal tests. Choose ten different JournalIDs for review, write up two cases and make a review table. Show a supplier chart, amount bands and journal details.
Expected result: no unbalanced journals; a clear list of 4 employee-linked supplier review labels, compared with your bank-match test; and duplicate candidates compared with the 21 planted pairs. Do not describe the total flagged amount as proven loss. Use the final answer key only after trying your own rules.
Mark your work out of 100: correct records and source notes 20, repeatable tests 25, correct amounts 20, evidence and alternative explanations 20, clear charts 15. If you called every flag a proven fraud, revise the conclusion.
## Project 2: Build a financial reporting pack
Report January-September 2025 with the same months of 2024 for comparison. Add a profit page, a 30 September 2025 balance sheet, a cash page and a trial-balance check.
Expected result: monthly amounts agree with the answer table; balance-sheet and cash checks are zero; account balances match the trial balance to within one cent at month ends. Do not label your cash-change chart a complete statutory cash-flow statement without doing the classification work.
Marks: correct signs and exclusions 25, fair date comparison 15, agreement between records 30, explanation 15, readable design 15.
## Project 3: Recommend useful business actions
Build pages for budget differences, overdue customer bills, supplier matching problems and consulting work hours. Keep the two practice businesses clearly labelled.
Expected result: supplier matching exceptions 168/520 = 32.31%; claims without receipts 81/650 = 12.46%; unmatched bank records 129/1,400 = 9.21%. Each recommendation should have an owner and a next step, such as asking the accounts team to obtain missing receipts.
Marks: clear definitions 25, correct use of each table 25, useful recommendations 20, working filters 15, checks and limits 15.
## Project 4: Assess a client-retention idea
Explain the outcome, split the years, reproduce the two fixed prediction rules and draw their right/wrong prediction tables. Suggest what extra data a better model would need.
Expected result: 150 client-year rows for 30 clients, with 86 leaving outcomes overall. In 2025 the majority baseline is 60% accurate and the fixed NPS rule is 36.67% accurate. Neither is a proven future prediction service. A reasoned “not ready to deploy” conclusion is acceptable.
Marks: correctly dated inputs/outcomes 25, fair data split and baseline 20, explanation of results 20, privacy and limits 20, sensible proposal 15.
# Test yourself | Short practical exams
## Exam A: Build from scratch (about four hours)
Without using your old report, import the main accounting entries and the needed reference files. Make the calendar and relationships. Calculate revenue, profit, previous-year revenue and closing balances. Show a year comparison and a month-end account check.
Answer checklist: 13,929 GL rows; 5,504 journals; debits and credits each USD 122,878,886.54; performance ignores Opening and Closing; balances include them; relationships match unique reference IDs; month-end trial balance differences are within one cent. Award 20 marks each for importing, connections, formulas, dates and checks. Aim for 70/100 with no unexplained balance difference.
## Exam B: Find and explain exceptions (about five hours)
Test duplicates, shared supplier/employee bank accounts, near-limit payments, weekend manual entries, missing approvals and self approvals. Make a review list and explain what further evidence you need.
Answer checklist: state exact rules; do not treat blank approvals as self approval; distinguish row counts from journal counts; avoid adding both debit and credit as two losses; compare the fixed-rule table only for matching rules. Award 30 for repeatable tests, 25 for money calculations, 25 for evidence and 20 for plain explanations.
## Exam C: Write a short proposal (about two hours)
Use the 56-hour worked plan and USD 50 hourly assumption. State the deliverables, limits, price, tests and handover plan.
Answer: USD 2,800 base plus USD 420 allowance = USD 3,220 before tax/licences. Milestones are USD 966, USD 1,288 and USD 966. Award 25 each for clear scope, correct arithmetic, acceptance checks and handover.
## Ten quick questions and answers
1. Can a measure change when I click a year? Yes. It recalculates for the selected rows.
2. Does a stored calculated column change with each slicer click? No. It is calculated when the model is updated, not separately for each visual selection.
3. Can a reference-list ID repeat on the “one” side? It should not. Check duplicates before connecting it.
4. Can I add all monthly closing balances? Usually not: that repeats amounts held across months.
5. Does 2025 contain twelve GL months? No, only January-September.
6. Can I discount sales-order GrossAmountUSD again? No. The discount is already included.
7. Does a balanced journal prove honesty? No. It only shows matching debit and credit totals.
8. Does a shared bank account prove a false supplier? No. It needs ownership and authorisation checks.
9. Should I tune my model using the final-test answers? No. Keep that test for the final fair check.
10. Does hiding a table protect it? No. Set and test proper access restrictions.
# Answer totals | Check your calculations
These figures are calculated from the actual files in this pack. Unless the label says otherwise, clear all filters before checking. A 2025 GL answer covers January-September only.
Some totals are just import checks. For example, adding all budget rows mixes planned income and planned costs; it is not the business's expected profit. “Debit minus credit” uses a sign convention where debit balances are positive and credit balances negative.
@CONTROLS
Allow a one-cent difference for money rounding. Counts should match exactly. If a total is wrong, inspect filters, types, duplicate imports and relationships. Do not enter an extra adjustment simply to copy the answer.
# Monthly answers | Revenue and profit
Use YearMonth in the matrix rows. Revenue means credits less debits on Revenue accounts. Profit/loss means credits less debits on accounts marked IsPL = Yes. Both calculations exclude Opening and Closing entries. A minus profit figure means a loss.
@MONTHLY
Use July-September 2025 revenue for the three-month-average forecast exercise. The estimate for each later month is USD 1,275,666.48. An estimated amount must never be labelled as an actual result.
# More answers | Balances, budget and prediction checks
The financial checks below use the dates printed in each row. They are the expected answers for Modules 05, 06 and 08.
For the prediction table, “positive” means predicted leaving. TP means correctly flagged a leaver. FP means wrongly flagged someone who stayed. TN means correctly left a stayer unflagged. FN means missed a leaver. The plain-language explanation is in Module 11.
@EXTENDED
# When something goes wrong | Simple fixes
My total is twice as large: check for a duplicate import, an extra loaded practice query, or a merge that matched two reference rows to each transaction.
My 2024 revenue disappeared: you may have included the year-end closing entries. Use Activity Net Debit to exclude Opening and Closing when calculating performance.
My budget vanishes when I select part of a month: budget rows use the first day of each month. Compare full months or deliberately build a daily allocation rule.
My date slicer does nothing: use DimDate fields, make sure the connection is active, and check both columns are Date rather than one being text or a date with a time.
My months are alphabetical: sort Month by MonthNo. Use YearMonth for charts covering more than one year.
A supplier name is blank: inspect the VendorID. A GL row may legitimately have no supplier. For a nonblank ID, check whether it matches the vendor list exactly.
Profit does not equal cash movement: customers may pay later, bills may be unpaid and depreciation does not involve a current cash payment. Profit and cash answer different questions.
My balance-sheet assets are too large: do not turn all negatives into positives. Some accounts reduce assets. Compare account by account with the trial balance.
My online viewer sees too much: check their workspace permissions and each table's security coverage. A rule on cost centre does not secure unrelated records.
The forecast or AI option is missing: check the chart setup, version, account and permissions. Use the simple local alternative rather than inventing an output.
I moved the CSV folder and refresh failed: in Power Query, use the source settings or the Source step's settings button to change the file path for each imported query. Check access and rerun the totals afterward.
## Before you call your report finished
[ ] Each file was imported as its own table, with the expected row count.
[ ] IDs are text; dates and money have suitable types; errors have been explained.
[ ] Reference IDs are unique and filters change the intended charts.
[ ] Revenue/profit formulas exclude closing entries, but balance formulas include them.
[ ] GL, trial balance, balance sheet and cash checks agree at the stated dates.
[ ] Titles show the period and currency, and charts have clear labels.
[ ] Review flags are not called proven fraud or loss.
[ ] Model estimates have honest limits; no accuracy or evidence was invented.
[ ] Sharing permissions, refresh and the handover instructions have been tested.
# Helpful words | Plain meanings
Account: a category used to record money, such as bank, sales or rent. AccountCode identifies the category; AccountName describes it.
Journal: a set of accounting lines recording an event. JournalID groups them; LineID identifies one line.
Debit and credit: the two sides of accounting entries. They do not simply mean bad and good. The appropriate side depends on the account.
Reference table / dimension: a list describing things, such as customers or accounts. The file names often begin Dim.
Transaction or fact table: a table containing events or amounts. The file names often begin Fact.
Grain: what one row represents, such as one invoice or one account at month end.
Relationship: a connection telling Power BI how rows in separate tables match.
Filter context: the selections deciding which records a measure includes. Row context: the current row when a formula works through rows one by one.
Context transition: when a DAX calculation turns the current row into filters. This matters in advanced formulas; use the supplied tested patterns before experimenting.
Query: a set of steps used to read and prepare a table. Query folding: those steps being passed to a capable source system to do the work. Local CSV files do not fold to a database.
Snapshot: records showing a situation at one date, like unpaid balances at month end. Semi-additive means you can add some groups but should not add repeated snapshots across time.
Reconciliation: checking that two records agree and explaining any difference.
Variance: actual minus planned or comparison amount. Favourable means helpful to the business; a positive cost variance is not normally favourable.
Exposure: money that may be affected under your stated assumptions. Confirmed loss: an amount supported by evidence, after considering valid explanations and recoveries.
False positive: a warning about something that turns out not to be the target issue. False negative: an issue the test missed.
Baseline: a simple starting method used to judge whether a more complicated method is worth using.
Leakage: a model accidentally learning from information that would not have been available when making the prediction.
RLS: row-level security, restricting which rows a viewer can see. OLS: object-level security, restricting access to tables or columns. Hiding something in the field list is neither.
## Where to learn more
For changing Power BI menus, sharing rules and licences, check Microsoft's official help: learn.microsoft.com/power-bi/ and learn.microsoft.com/dax/ . This workbook follows your repository's twelve-topic learning plan but explains it in simpler language.
The source amounts and answer checks were verified using Python. Power BI Desktop and online permissions were not run in the build environment. You must still test your actual report and sharing setup. The reference chart is drawn from the data, not a screenshot of an executed Power BI file.
# Column guide | How to read the separate files
The following pages list the columns in each CSV. You do not need to learn every column before starting. Look up a file when you import it.
Text means labels or codes that must not be added. Date is a calendar date. Date/Time includes a clock time. Whole number has no fraction. Decimal number allows fractions. Use Fixed decimal number for most money columns when building the report, and Decimal number for rates or model inputs that need more than four decimal places.
A listed example helps you recognise the field; it is not every possible value. Yes and No remain text unless you deliberately change them. Keep useful blank columns: missing values can be part of an exercise.
@DICTIONARY
# File fingerprints | Optional advanced check
You can skip this page while learning the reports. In a real investigation, retaining an unchanged source matters. A fingerprint, or SHA-256 hash, helps show whether a file was changed after it was saved. Use a trusted hash-checking tool to compare a file with the printed value.
@HASH
# Answer key | Read after your investigation
This section reveals the deliberately planted practice cases. It is not a list of proven real fraud. The 171 journal cases cover 342 GL lines because each journal has two sides in the planted records. Their labels are removed from your GL CSV so you can attempt the tests first.
The totals below count one debit side per planted journal. They do not add debit and credit together. The 42 duplicate journals include both members of 21 pairs. Their possible excess, under the assumptions explained earlier, is USD 184,011.74 rather than the full pair value.
@FORENSIC
GHOST-VENDOR is the practice label for suspicious supplier records linked to employees. SOD-RARE-COMBO means an unusual user/account combination that may conflict with assigned duties. UNREVERSED-ACCRUAL means a planted accrual for which an expected reversal is missing. The other labels describe repeated payments, near-limit amounts, split purchases and unusual posting times.
Use these labels to check your exercise, not to accuse someone. Candidate-rule results can include valid transactions as well as planted cases. Check each case and keep your rule definitions visible.
# Answer key | Every planted journal
Find these IDs in FactGLJournal[JournalID]. If you add a case-review table to your report, store one review row per journal. Do not repeat the case amount for every accounting line and then add it again.
@JOURNALS
# Your next step | One lesson at a time
Tatenda, start with FactGLJournal.csv and Module 01. You do not have to import or understand all 22 files on day one. Each lesson builds on the earlier work.
Keep a short note after every session: what you built, what went wrong, how you checked it and what you learned. Save your report files and screenshots in a separate working folder so the original CSVs stay unchanged.
You are ready to present your work when you can explain, in ordinary words: what one row means, which records your calculation includes, why the answer is correct and what the report cannot prove.
