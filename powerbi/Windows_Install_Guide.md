# Installing Power BI on Windows

Time: 20 minutes. Everything you need for Modules 1–12 is free.

---

## 1. Check your machine

| Requirement | Minimum | Recommended |
|---|---|---|
| Windows | Windows 10 (64-bit) | Windows 11 |
| RAM | 4 GB | 16 GB or more (the client models get big) |
| Disk | 5 GB free | 50 GB free (client data + working files) |
| Display | 1366 × 768 | 1920 × 1080 or dual monitors |
| Account | Any email | A **work/school (organisational)** account |

> **Use a work or school account if you have one.** Personal Gmail/Yahoo accounts can build and publish
> to their own workspace, but they cannot be licensed for sharing with clients later. If you are
> building Maxhub, use a Maxhub domain account.

## 2. Install Power BI Desktop

**Option A — Microsoft Store (recommended, auto-updates):**

1. Open the Store and search for **"Microsoft Power BI Desktop"**, or open:
   `ms-windows-store://pdp?productId=9NTXR16HNW1T`
2. Install. Updates arrive automatically through the Store.

**Option B — direct download:**

1. Go to <https://powerbi.microsoft.com/desktop/> → **Download free**.
2. Choose the 64-bit installer (always 64-bit).
3. Run the installer and accept the defaults.

Both versions coexist; prefer one to avoid confusion about which build you are using.

## 3. Sign in and configure (do this once, properly)

1. Open Power BI Desktop → top-right avatar → **Sign in**.
2. Then set the options that matter for accounting work:

**File ▸ Options and settings ▸ Options ▸ Global**

| Setting | Value | Why |
|---|---|---|
| Regional settings | English (United Kingdom) or your locale | Controls how dates and decimals are parsed at import |
| Data Load ▸ **Auto date/time** | **Off** | Stops Power BI creating a hidden date table per date column |
| Data Load ▸ Time intelligence ▸ Auto date/time for new files | **Off** | Same reason |
| Preview features | Leave defaults | Avoid half-finished features in client work |

**File ▸ Options ▸ Current File ▸ Regional Settings** can override per file — keep it consistent with
Global unless the client's data demands otherwise.

3. Turn on useful ribbon tabs: **View ▸ Customise the ribbon** → make sure *Model view*, *DAX query view*
   and *Optimize* are visible.

## 4. Optional but strongly recommended tools (all free)

| Tool | What it adds | Get it from |
|---|---|---|
| **Tabular Editor 3** (community/free tier) | Bulk measure editing, Best Practice Analyzer | tabulareditor.com |
| **DAX Studio** | Query tracing, performance, export query results to Excel for working papers | daxstudio.org |
| **Power BI Report Builder** | Paginated reports (statements, invoices) | Microsoft |
| **Notepad++ / VS Code** | Editing `.dax`, `.pqm` and CSV files from this repo | free |

After installing Tabular Editor or DAX Studio, they appear as **External Tools** buttons inside Power BI
Desktop.

## 5. Python (for the ML lab and the data scripts)

1. Install **Python 3.11+** from python.org (tick *Add python.exe to PATH*).
2. Verify in Command Prompt:
   ```bat
   python --version
   pip install pandas numpy openpyxl
   ```
3. In Power BI: **File ▸ Options ▸ Python scripting** → set the Python home directory.
4. The course scripts use only the standard library except `build_workbooks.py` (needs `openpyxl`).

## 6. The Power BI Service

1. Go to <https://app.powerbi.com> and sign in with the same account.
2. You now have a **My workspace** where you can publish.
3. For client work later you will need either:
   - **Fabric Free** with the client's users granted viewer access in their tenant, or
   - **Power BI Pro / Premium Per User** per user, or
   - a **Fabric capacity (F-SKU)** for broad internal distribution and Copilot features.
4. Explore **Settings ▸ Admin portal** only if you are a tenant administrator — the free account has no
   admin portal.

## 7. Verify your install

Create a test file to prove the pipeline works end to end:

1. **Get Data ▸ Excel workbook** ▸ `data/xlsx/PowerBI_Practice_Workbook.xlsx` ▸ **SimpleData**.
2. **Transform Data** → check the columns → **Close & Apply**.
3. Build a column chart: Axis `Month`, Values `Sales`.
4. **Publish ▸ My workspace**, then open the report in the browser.
5. Save the file as `Maxhub_Setup_Test.pbix`.

If all five steps worked, your environment is ready for Module 1.

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| Installer blocked by IT policy | Ask IT for the Microsoft Store app, or run the direct installer with admin rights |
| "Sign-in failed" / cannot sign in | You may need an organisational account; personal account sign-in is allowed but limited |
| Power BI is slow | Check RAM usage; close Excel; reduce the model (fewer columns, no calculated columns on facts) |
| Cannot find *Transform data* | Ensure you are on the **Home** ribbon tab in Report view |
| Store version and download version differ | Pick one; the Store version updates faster |
| External Tools tab missing | Install Tabular Editor / DAX Studio, then restart Desktop |
| Python visuals error | Set the Python home directory in Options and install the required modules |
