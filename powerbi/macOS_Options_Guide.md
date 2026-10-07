# Power BI on macOS — what actually works

Power BI Desktop is **Windows-only**. There is no Mac version, and no announced plan for one. This is
not a problem for learning the course — but you have to choose a route, and the right route depends on
whether you are learning or delivering client work.

---

## Quick decision

| Your situation | Recommended route |
|---|---|
| Learning, following the labs on your own | **Route 1 — Windows VM** (best fidelity) or **Route 2 — Fabric in the browser** |
| Delivering to clients | **Route 1 — Windows VM** or a Windows PC. Do not deliver from a Mac-only setup. |
| Just exploring | **Route 3 — Parallels/cloud PC**, then decide |

---

## Route 1 — Windows virtual machine (recommended)

**On Apple silicon (M1/M2/M3/M4):** Parallels Desktop + Windows 11 ARM. Power BI Desktop runs under
x86-64 emulation; it works but is slower on large models. Allocate **8 GB RAM and 60 GB disk**.

**On Intel Macs:** VirtualBox (free) or VMware Fusion + Windows 11 x64, or Boot Camp if the Mac supports it.
Allocate at least 4 GB RAM and 40 GB disk.

Steps:

1. Install the hypervisor, then Windows 11 (a licence is required; Windows 11 ARM is licensed through
   Parallels for Apple silicon).
2. Inside Windows, install Power BI Desktop per
   [`Windows_Install_Guide.md`](Windows_Install_Guide.md).
3. Turn off auto date/time immediately (Options ▸ Data Load).
4. Share a folder between macOS and Windows (Parallels "Shared Profile", or a cloud folder) and keep
   your course data there so you can open the same files from both sides.
5. Practical tips: give the VM 8 GB RAM and 4 CPUs; don't run the budget calc in Excel at the same
   time; take a snapshot before big model work.

## Route 2 — Power BI Service / Fabric in a browser (no Windows needed)

The browser experience now covers more than it used to:

| Capability | Browser (Service/Fabric) | Desktop |
|---|---|---|
| View and interact with reports | ✅ | ✅ |
| Edit existing reports | ✅ (edit in the Service) | ✅ |
| Build a semantic model from a lakehouse/warehouse | ✅ (Fabric) | ✅ |
| Build a semantic model from a local CSV/Excel file | ⚠️ Limited — upload to OneDrive/SharePoint first, or use a Fabric lakehouse | ✅ Directly |
| Full Power Query (M) editing | ⚠️ Partial | ✅ |
| DAX query view | ⚠️ Available in Fabric | ✅ |
| Python/R visuals, custom connectors, external tools | ❌ | ✅ |

**Verdict:** you can follow most of the *concepts* and the DAX/Power Query libraries in the browser, but
you cannot do the full Module 2–5 lab work from a browser alone. Try it yourself: upload
`data/xlsx/PowerBI_Practice_Workbook.xlsx` to OneDrive, create a report in the Service, and see what
you can and cannot do.

To get a Microsoft Fabric trial: sign up at <https://app.fabric.microsoft.com> with a work/school
account and start the 60-day trial (capacity is provisioned automatically). Then you can create a
lakehouse, load the CSVs from this repo, and build the model in the browser.

## Route 3 — Cloud Windows PC

If you need Windows occasionally rather than daily:

| Option | Notes |
|---|---|
| **Azure Virtual Desktop / Windows 365** | Pay per month; real Windows, accessible from macOS; heavier setup |
| **AWS WorkSpaces / Amazon AppStream** | Similar; hourly/monthly pricing |
| **Shadow / Paperspace / MacStadium** | Consumer/developer cloud PCs; check licensing terms |
| **A cheap Windows mini-PC or laptop** | Often cheaper than a subscription over two years, and always available |

Cloud PCs are the best answer if you travel or have an older Mac: install Power BI Desktop there, and
open it from Safari or the Windows App.

## What genuinely does not work

- **Power BI Desktop for Mac** — does not exist. Any "Mac version" you find online is a VM guide or a
  third-party tool (e.g. Power BI Desktop in Parallels), not a Microsoft product.
- **Parallels + Windows ARM** for very large models — works, but 5-million-row models will crawl.
- **Editing `.pbix` files in any Mac application** — nothing on macOS opens `.pbix`. You may open the
  extracted files, but not the packaged model.
- **Tabular Editor / DAX Studio** — Windows-only (DAX Studio has no Mac build; Tabular Editor 3 has a
  macOS build but requires a Windows-hosted Analysis Services endpoint to be useful).

## Working cross-platform (the practical routine)

1. Keep all source data in a shared folder that both macOS and Windows can see.
2. Do the modelling, Power Query and DAX work in the Windows VM.
3. Do the documentation, methodology notes, proposals and reports on macOS — this repo's Markdown files
   are written for that.
4. Export working papers to Excel from the VM and file them with the engagement documents.
5. Version the `.pbix` like any other client file: `Client_Report_vX.Y.pbix`, and keep a change log.
6. If you collaborate with Windows users, agree on the exact Power BI Desktop version so the model does
   not upgrade underneath them (newer builds upgrade the file format silently).

## Verifying your Mac setup

- [ ] I can open Power BI Desktop (in a VM or cloud PC) and import a CSV from this repo.
- [ ] I can build a chart, publish to My workspace, and open the report in Safari on macOS.
- [ ] I can complete Lab 01 end to end.
- [ ] My data folder is shared so my working files are not trapped inside the VM.
- [ ] I know which route I will use for client delivery, and it is Windows.

If the last box is not ticked, do not take on client delivery yet: a report you cannot refresh, publish
or hand over from your own machine is a liability, not a service.
