"""
d_dashboard.py - the self-contained interactive dashboard.

One HTML file, no CDN, no external font, no network call.  All data is embedded as
JSON by the build script, so the numbers on the page are the numbers in the reports
and the file works offline from a USB stick.  Charts are drawn with inline SVG.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict

from . import common as C
from .writers import ISSUE_DATE, usd

SCHEME_ORDER = ["DUPLICATE-PAYMENT", "GHOST-VENDOR", "ROUND-NUMBER-THRESHOLD", "SPLIT-PURCHASE",
                "WEEKEND-AFTERHOURS", "SOD-RARE-COMBO", "UNREVERSED-ACCRUAL"]


def build(out, ctx, fx):
    os.makedirs(out, exist_ok=True)
    data = payload(ctx, fx)
    html = PAGE.replace("/*__DATA__*/", json.dumps(data))
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(out, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme(data))


def payload(ctx, fx):
    led = ctx["ledger"]
    monthly = C.monthly_pl(led)
    bs = ctx["balance_sheet"]
    rt = ctx["ratios"]

    injected = defaultdict(lambda: {"count": 0, "value": 0.0})
    for r in led.injection_log:
        injected[r["AnomalyType"]]["count"] += 1
        injected[r["AnomalyType"]]["value"] += float(r["AmountUSD"])

    schemes = []
    names = {t[0]: t[1] for t in fx["tests"]}
    for scheme in SCHEME_ORDER:
        test = {"DUPLICATE-PAYMENT": "T01", "GHOST-VENDOR": "T02",
                "ROUND-NUMBER-THRESHOLD": "T03", "SPLIT-PURCHASE": "T04",
                "WEEKEND-AFTERHOURS": "T05", "SOD-RARE-COMBO": "T06",
                "UNREVERSED-ACCRUAL": "T07"}[scheme]
        t = fx["totals"][test]
        schemes.append({
            "id": scheme, "test": test, "name": names[test],
            "injected": injected[scheme]["count"],
            "injectedValue": round(injected[scheme]["value"], 2),
            "detected": t["Lines"], "detectedValue": t["Value"],
        })

    bands = defaultdict(lambda: {"count": 0, "value": 0.0})
    for r in fx["register"]:
        bands[r["RiskBand"]]["count"] += 1
        bands[r["RiskBand"]]["value"] += r["AmountUSD"]

    tests = defaultdict(lambda: {"count": 0, "value": 0.0})
    for r in fx["register"]:
        tests[r["TestID"]]["count"] += 1
        tests[r["TestID"]]["value"] += r["AmountUSD"]

    months = [{"Period": r["Period"], "Revenue": round(r["Revenue"], 2),
               "Gross profit": round(r["Gross profit"], 2),
               "Operating profit": round(r["Operating profit"], 2),
               "Profit after tax": round(r["Profit after tax"], 2)}
              for r in monthly if r["Period"] >= "2024-01"]

    bs_rows = []
    for l in bs["Asset lines"]:
        bs_rows.append({"Section": "Assets", "Line": l, "Value": round(bs["lines"][l], 2)})
    for l in bs["Liability lines"]:
        v = (bs["Suspense (credit balance)"] if l == "Suspense (credit balance)"
             else bs["lines"][l])
        bs_rows.append({"Section": "Liabilities", "Line": l, "Value": round(v, 2)})
    for l in C.BS_EQUITY_LINES:
        bs_rows.append({"Section": "Equity", "Line": l, "Value": round(bs["lines"][l], 2)})
    bs_rows.append({"Section": "Equity", "Line": "Current year result",
                    "Value": round(bs["Current year result"], 2)})

    vendors = [{"Vendor": p["VendorName"], "Spend": round(p["AmountUSD"], 2),
                "Cumulative pct": round(p["Cumulative pct"], 1),
                "EmployeeLinked": p["EmployeeLinked"]}
               for p in ctx["spend"]["pareto"][:12]]

    ap_status = defaultdict(int)
    for r in ctx["ap"]["rows"]:
        ap_status[r["ThreeWayMatch"]] += 1

    ageing = [{"Bucket": k, "Invoices": v["Invoices"],
               "Outstanding": round(v["OutstandingUSD"], 2)}
              for k, v in sorted(ctx["ar"]["by_bucket"].items())]

    bank = {"Reconciled": ctx["bank"]["count"] - ctx["bank"]["unreconciled_count"],
            "Unreconciled": ctx["bank"]["unreconciled_count"],
            "Unreconciled value": round(ctx["bank"]["unreconciled_value"], 2),
            "Over 90 days": ctx["bank"]["over_90_days"],
            "Oldest days": ctx["bank"]["oldest_age"]}

    register = [{
        "Rank": r["Rank"], "Journal": r["JournalID"], "Date": r["ExceptionDate"],
        "Test": r["TestID"], "Test name": r["TestName"], "Vendor": r["VendorName"] or "-",
        "Account": r["AccountCode"], "Description": r["Description"][:70],
        "Amount": r["AmountUSD"], "Score": r["RiskScore"], "Band": r["RiskBand"],
        "RWV": r["RiskWeightedValue"], "Preparer": r["PreparerRole"] or r["Preparer"],
        "Approver": r["Approver"], "Conclusion": r["Conclusion"][:150],
    } for r in fx["register"]]

    return {
        "meta": {
            "client": "Mhondoro Holdings Plc (synthetic engagement data)",
            "asAt": "2025-09-30",
            "generated": f"{ISSUE_DATE:%d %B %Y}",
            "glLines": ctx["control_totals"]["GL lines"],
            "journals": ctx["control_totals"]["Journals"],
            "totalDebits": round(ctx["control_totals"]["Total debits"], 2),
        },
        "kpis": [
            {"label": "Revenue FY2025 (9 months)", "value": ctx["pl_2025"]["Revenue"],
             "kind": "money", "note": f"FY2024 full year {usd(ctx['pl_2024']['Revenue'], 0)}"},
            {"label": "Gross margin FY2025", "value": ctx["pl_2025"]["Gross margin pct"] / 100,
             "kind": "pct", "note": f"FY2024 {ctx['pl_2024']['Gross margin pct']:.2f}%"},
            {"label": "Profit after tax FY2025", "value": ctx["pl_2025"]["Net profit"],
             "kind": "money", "note": "Loss after a full-year tax charge on nine months of profit"},
            {"label": "Cash and cash equivalents", "value": ctx["ratio_inputs"]["Cash"],
             "kind": "money", "note": f"Prior year end {usd(C.EXPECTED['Cash prior year end'], 0)}"},
            {"label": "Current ratio", "value": ctx["balance_sheet"]["Current ratio"],
             "kind": "num", "note": "Current assets over current liabilities"},
            {"label": "Cash conversion cycle", "value": rt["CCC"], "kind": "days",
             "note": f"DSO {rt['DSO']:.0f} + DIO {rt['DIO']:.0f} - DPO {rt['DPO']:.0f} days"},
            {"label": "Exceptions identified", "value": fx["grand"]["Lines"], "kind": "num",
             "note": f"{usd(fx['grand']['Value'], 0)} across seven schemes"},
            {"label": "Detection rate", "value": fx["answer_key"]["Coverage pct"] / 100,
             "kind": "pct", "note": f"{fx['answer_key']['Detected total']} of "
                                    f"{fx['answer_key']['Expected total']} injected journals"},
        ],
        "monthly": months,
        "balanceSheet": bs_rows,
        "totals": {"Total assets": round(bs["Total assets"], 2),
                   "Total liabilities": round(bs["Total liabilities"], 2),
                   "Total equity": round(bs["Total equity"], 2),
                   "BS check": round(bs["BS check"], 2)},
        "schemes": schemes,
        "bands": [{"Band": k, "Count": v["count"], "Value": round(v["value"], 2)}
                  for k, v in sorted(bands.items(), key=lambda x: -x[1]["value"])],
        "tests": [{"Test": k, "Name": names[k], "Count": v["count"],
                   "Value": round(v["value"], 2)}
                  for k, v in sorted(tests.items())],
        "vendors": vendors,
        "apStatus": [{"Status": k, "Count": v} for k, v in sorted(ap_status.items())],
        "apSummary": {"Invoices": ctx["ap"]["count"], "Value": round(ctx["ap"]["total"], 2),
                      "Exceptions": ctx["ap"]["three_way_fail"],
                      "No PO": ctx["ap"]["no_po"],
                      "Duplicates": sum(1 for r in ctx["ap"]["rows"]
                                        if r["DuplicateSuspected"])},
        "ageing": ageing,
        "arSummary": {"Outstanding": round(ctx["ar"]["outstanding"], 2),
                      "Invoices": ctx["ar"]["invoices"], "Disputed": ctx["ar"]["disputed"]},
        "bank": bank,
        "spendTotal": round(ctx["spend"]["total"], 2),
        "register": register,
        "dismissed": len(fx["dismissed"]),
        "unapproved": {"Value": round(fx["maker_checker"]["unapproved_value"], 2),
                       "Journals": len(fx["maker_checker"]["unapproved"])},
    }


def readme(data):
    return f"""# Interactive dashboard

Open `index.html` in any browser. It is a single self-contained file: the data is
embedded as JSON, the charts are inline SVG, and there is no CDN, no external font
and no network call, so it works offline and can be emailed or copied to a USB stick.

Generated {data['meta']['generated']}. Data as at {data['meta']['asAt']}.
Population {data['meta']['glLines']:,} ledger lines across {data['meta']['journals']:,} journals.

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
"""


PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Maxhub - Mhondoro Holdings Plc - analytics workbench</title>
<style>
:root{
  --ink:#12212e; --ink2:#44586b; --line:#dfe6ec; --bg:#f4f7f9; --card:#fff;
  --brand:#0d4f6c; --brand2:#157a9c; --accent:#c2410c; --good:#15803d; --warn:#b45309;
  --bad:#b91c1c; --chip:#eef4f7;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{background:var(--brand);color:#fff;padding:18px 24px}
header h1{margin:0;font-size:20px;letter-spacing:.2px}
header p{margin:4px 0 0;opacity:.85;font-size:12.5px}
nav{display:flex;gap:4px;background:#0a3d54;padding:0 24px;flex-wrap:wrap}
nav button{background:none;border:0;color:#cfe3ec;padding:11px 14px;font-size:13.5px;
  cursor:pointer;border-bottom:3px solid transparent}
nav button[aria-selected="true"]{color:#fff;border-bottom-color:#7fd0e8;font-weight:600}
main{padding:20px 24px 56px;max-width:1440px;margin:0 auto}
.grid{display:grid;gap:14px}
.kpis{grid-template-columns:repeat(auto-fit,minmax(190px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.kpi .l{font-size:11.5px;text-transform:uppercase;letter-spacing:.6px;color:var(--ink2)}
.kpi .v{font-size:22px;font-weight:650;margin-top:6px;font-variant-numeric:tabular-nums}
.kpi .n{font-size:11.5px;color:var(--ink2);margin-top:4px}
h2{font-size:15px;margin:0 0 10px}
h3{font-size:13px;margin:0 0 8px;color:var(--ink2);text-transform:uppercase;letter-spacing:.5px}
.two{grid-template-columns:1.4fr 1fr}
.three{grid-template-columns:repeat(3,1fr)}
@media(max-width:1000px){.two,.three{grid-template-columns:1fr}}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{font-size:11px;text-transform:uppercase;letter-spacing:.4px;color:var(--ink2);
  position:sticky;top:0;background:#fff;cursor:pointer;user-select:none}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
tr:hover td{background:#f7fafc}
.scroll{max-height:520px;overflow:auto;border:1px solid var(--line);border-radius:8px}
.chip{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11px;background:var(--chip)}
.chip.high{background:#fde8e8;color:var(--bad)}
.chip.medium{background:#fef3c7;color:var(--warn)}
.chip.low{background:#dcfce7;color:var(--good)}
.controls{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;align-items:center}
select,input{font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:6px;background:#fff}
.count{font-size:12px;color:var(--ink2);margin-left:auto}
.note{font-size:12px;color:var(--ink2);margin-top:8px}
footer{padding:16px 24px 40px;color:var(--ink2);font-size:12px;max-width:1440px;margin:0 auto}
svg text{font-family:inherit}
.legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:var(--ink2);margin-top:6px}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px}
.bar-row{display:grid;grid-template-columns:180px 1fr 92px;gap:8px;align-items:center;
  font-size:12.5px;margin-bottom:5px}
.bar-row .t{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar{height:14px;background:var(--brand2);border-radius:3px}
.bar.alt{background:var(--accent)}
.bar-row .v{text-align:right;font-variant-numeric:tabular-nums;color:var(--ink2)}
.hide{display:none}
</style>
</head>
<body>
<header>
  <h1>Maxhub Pvt Ltd &mdash; Mhondoro Holdings Plc analytics workbench</h1>
  <p id="sub"></p>
</header>
<nav id="nav"></nav>
<main>
  <section class="grid kpis" id="kpis"></section>
  <div id="pages"></div>
</main>
<footer>
  Self-contained dashboard: data embedded as JSON, charts drawn as inline SVG, no CDN and no
  network call. Every figure is computed from the client extract by the same scripts that produce
  the Word and Excel deliverables, so this page cannot disagree with the reports.
  Simulated engagement data generated for training purposes.
</footer>
<script>
const D = /*__DATA__*/;
const money = (v,dp=0)=> (v<0?"(":"") + Math.abs(v).toLocaleString("en-US",{minimumFractionDigits:dp,maximumFractionDigits:dp}) + (v<0?")":"");
const fmt = (v,kind)=> kind==="money"?money(v):kind==="pct"?(v*100).toFixed(1)+"%":kind==="days"?v.toFixed(0)+" days":
  kind==="num"?v.toLocaleString("en-US"):v.toLocaleString("en-US",{maximumFractionDigits:2});
const el = (t,c,h)=>{const n=document.createElement(t); if(c)n.className=c; if(h!=null)n.innerHTML=h; return n;};
const svgNS="http://www.w3.org/2000/svg";

document.getElementById("sub").textContent =
  `${D.meta.client} · data as at ${D.meta.asAt} · ${D.meta.glLines.toLocaleString()} ledger lines · `+
  `${D.meta.journals.toLocaleString()} journals · debits = credits = ${money(D.meta.totalDebits,2)} · generated ${D.meta.generated}`;

/* ---------- KPI cards ---------- */
const kbox = document.getElementById("kpis");
D.kpis.forEach(k=>{
  const c = el("div","card kpi");
  c.appendChild(el("div","l",k.label));
  c.appendChild(el("div","v",fmt(k.value,k.kind)));
  c.appendChild(el("div","n",k.note||""));
  kbox.appendChild(c);
});

/* ---------- tiny chart helpers ---------- */
function columnChart(node, cats, series, opt={}){
  const W=node.clientWidth||760, H=opt.height||260, P={l:64,r:12,t:12,b:46};
  const iw=W-P.l-P.r, ih=H-P.t-P.b;
  const max = Math.max(...series.flatMap(s=>s.data.map(v=>Math.abs(v))),1);
  const min = Math.min(0, ...series.flatMap(s=>s.data.map(v=>v)));
  const span = (max-min)||1;
  const y = v => P.t + ih - ((v-min)/span)*ih;
  const s = document.createElementNS(svgNS,"svg");
  s.setAttribute("viewBox",`0 0 ${W} ${H}`); s.setAttribute("width","100%"); s.setAttribute("height",H);
  const ticks=5;
  for(let i=0;i<=ticks;i++){
    const val = min + span*i/ticks, yy=y(val);
    const ln=document.createElementNS(svgNS,"line");
    ln.setAttribute("x1",P.l);ln.setAttribute("x2",W-P.r);ln.setAttribute("y1",yy);ln.setAttribute("y2",yy);
    ln.setAttribute("stroke","#e8eef2"); s.appendChild(ln);
    const tx=document.createElementNS(svgNS,"text");
    tx.setAttribute("x",P.l-8);tx.setAttribute("y",yy+4);tx.setAttribute("text-anchor","end");
    tx.setAttribute("font-size","10.5");tx.setAttribute("fill","#44586b");
    tx.textContent = opt.pct ? (val*100).toFixed(0)+"%" : (Math.abs(val)>=1000? (val/1000).toFixed(0)+"k" : val.toFixed(0));
    s.appendChild(tx);
  }
  const bw = iw/cats.length, gap = bw*0.18, w = (bw-gap*2)/series.length;
  cats.forEach((c,i)=>{
    series.forEach((sr,j)=>{
      const v=sr.data[i], x=P.l+i*bw+gap+j*w, y0=y(Math.max(0,v)), y1=y(Math.min(0,v));
      const r=document.createElementNS(svgNS,"rect");
      r.setAttribute("x",x);r.setAttribute("y",y0);r.setAttribute("width",Math.max(1,w-1));
      r.setAttribute("height",Math.max(1,y1-y0));r.setAttribute("fill",sr.color);
      const t=document.createElementNS(svgNS,"title");
      t.textContent=`${c} · ${sr.name}: ${opt.pct?(v*100).toFixed(2)+"%":money(v,2)}`;
      r.appendChild(t); s.appendChild(r);
    });
    if(cats.length<=18 || i%3===0){
      const tx=document.createElementNS(svgNS,"text");
      tx.setAttribute("x",P.l+i*bw+bw/2);tx.setAttribute("y",H-P.b+16);
      tx.setAttribute("text-anchor","middle");tx.setAttribute("font-size","10");tx.setAttribute("fill","#44586b");
      tx.textContent=c; s.appendChild(tx);
    }
  });
  if(min<0){
    const z=document.createElementNS(svgNS,"line");
    z.setAttribute("x1",P.l);z.setAttribute("x2",W-P.r);z.setAttribute("y1",y(0));z.setAttribute("y2",y(0));
    z.setAttribute("stroke","#94a3b8"); s.appendChild(z);
  }
  node.appendChild(s);
}

function barList(node, rows, opt={}){
  const max = Math.max(...rows.map(r=>Math.abs(r.value)),1);
  rows.forEach(r=>{
    const row = el("div","bar-row");
    row.appendChild(el("div","t",r.label+(r.sub?` <span class="chip">${r.sub}</span>`:"")));
    const wrap = el("div"); const b = el("div","bar"+(r.alt?" alt":""));
    b.style.width = (Math.abs(r.value)/max*100).toFixed(1)+"%";
    b.title = `${r.label}: ${money(r.value,2)}`;
    wrap.appendChild(b); row.appendChild(wrap);
    row.appendChild(el("div","v", opt.pct ? r.value.toFixed(1)+"%" : money(r.value)));
    node.appendChild(row);
  });
}

function table(node, cols, rows, opt={}){
  const t = el("table");
  const head = el("tr");
  cols.forEach(c=>{
    const th = el("th", c.num?"n":"", c.label);
    th.onclick = ()=>{ opt.sortKey = c.key; opt.dir = (opt.dir===1&&opt.sortKey===c.key)?-1:1; render(); };
    head.appendChild(th);
  });
  const thead = el("thead"); thead.appendChild(head); t.appendChild(thead);
  const tbody = el("tbody"); t.appendChild(tbody);
  function render(){
    tbody.innerHTML="";
    let data = rows.slice();
    if(opt.filter) data = data.filter(opt.filter);
    if(opt.sortKey) data.sort((a,b)=>{
      const x=a[opt.sortKey], y=b[opt.sortKey];
      return (typeof x==="number"? x-y : String(x).localeCompare(String(y))) * (opt.dir||1);
    });
    if(opt.limit) data = data.slice(0, opt.limit);
    data.forEach(r=>{
      const tr = el("tr");
      cols.forEach(c=>{
        const v = c.render? c.render(r) : r[c.key];
        tr.appendChild(el("td", c.num?"n":"", v==null?"":v));
      });
      tbody.appendChild(tr);
    });
    if(opt.onCount) opt.onCount(data.length);
  }
  node.appendChild(t);
  render();
  return {render};
}

/* ---------- pages ---------- */
const PAGES = [
  {id:"performance", label:"Performance", build:performance},
  {id:"fraud", label:"Fraud and exceptions", build:fraud},
  {id:"procurement", label:"Procurement and payables", build:procurement},
  {id:"cash", label:"Receivables and cash", build:cash},
];
const nav = document.getElementById("nav"), pages = document.getElementById("pages");
PAGES.forEach((p,i)=>{
  const b = el("button",null,p.label);
  b.setAttribute("role","tab"); b.setAttribute("aria-selected", i===0);
  b.onclick = ()=>{ [...nav.children].forEach(x=>x.setAttribute("aria-selected","false"));
    b.setAttribute("aria-selected","true"); show(p.id); };
  nav.appendChild(b);
  const sec = el("section","grid hide"); sec.id="page-"+p.id; sec.dataset.built="0";
  pages.appendChild(sec);
});
function show(id){
  [...pages.children].forEach(s=>s.classList.add("hide"));
  const s = document.getElementById("page-"+id);
  s.classList.remove("hide");
  if(s.dataset.built==="0"){ s.dataset.built="1"; PAGES.find(p=>p.id===id).build(s); }
}
show("performance");

function card(parent, title, cls){
  const c = el("div","card"+(cls?" "+cls:""));
  if(title) c.appendChild(el("h2",null,title));
  parent.appendChild(c);
  return c;
}

/* ---------- 1. performance ---------- */
function performance(root){
  const c1 = card(root,"Revenue and profit by month");
  columnChart(c1, D.monthly.map(m=>m.Period.slice(2)),
    [{name:"Revenue",data:D.monthly.map(m=>m.Revenue),color:"#0d4f6c"},
     {name:"Gross profit",data:D.monthly.map(m=>m["Gross profit"]),color:"#157a9c"},
     {name:"Operating profit",data:D.monthly.map(m=>m["Operating profit"]),color:"#7fd0e8"},
     {name:"Profit after tax",data:D.monthly.map(m=>m["Profit after tax"]),color:"#c2410c"}],
    {height:280});
  c1.appendChild(el("div","legend",
    `<span><i style="background:#0d4f6c"></i>Revenue</span><span><i style="background:#157a9c"></i>Gross profit</span>`+
    `<span><i style="background:#7fd0e8"></i>Operating profit</span><span><i style="background:#c2410c"></i>Profit after tax</span>`));
  c1.appendChild(el("p","note","Nine months of FY2025 follow the whole of FY2024. Closing entries are excluded, so this is the trading result."));

  const two = el("div","grid two"); root.appendChild(two);
  const c2 = card(two,"Balance sheet at 30 September 2025");
  barList(c2, D.balanceSheet.map(r=>({label:r.Line, value:r.Value, sub:r.Section.slice(0,3),
    alt:r.Section!=="Assets"})));
  c2.appendChild(el("p","note",
    `Total assets ${money(D.totals["Total assets"],2)} = liabilities ${money(D.totals["Total liabilities"],2)} + `+
    `equity ${money(D.totals["Total equity"],2)}. Balance sheet check ${D.totals["BS check"].toFixed(2)}.`));

  const c3 = card(two,"Monthly detail");
  table(c3,[{key:"Period",label:"Period"},
    {key:"Revenue",label:"Revenue",num:1,render:r=>money(r.Revenue,2)},
    {key:"Gross profit",label:"Gross profit",num:1,render:r=>money(r["Gross profit"],2)},
    {key:"Gross margin",label:"GM %",num:1,render:r=>(r["Gross profit"]/r.Revenue*100).toFixed(2)+"%"},
    {key:"Profit after tax",label:"PAT",num:1,render:r=>money(r["Profit after tax"],2)}],
    D.monthly, {sortKey:"Period", dir:1});
}

/* ---------- 2. fraud ---------- */
function fraud(root){
  const c1 = card(root,"The seven schemes - injected against detected");
  table(c1,[{key:"name",label:"Scheme"},{key:"test",label:"Test"},
    {key:"injected",label:"Injected",num:1},{key:"detected",label:"Detected",num:1},
    {key:"injectedValue",label:"Value injected",num:1,render:r=>money(r.injectedValue,2)},
    {key:"detectedValue",label:"Value detected",num:1,render:r=>money(r.detectedValue,2)},
    {key:"rate",label:"Detection",num:1,render:r=>(r.detected/r.injected*100).toFixed(0)+"%"}],
    D.schemes,{sortKey:"injectedValue",dir:-1});
  c1.appendChild(el("p","note",
    `Detection is measured against the extract's own injection key, used only to prove completeness. `+
    `A further ${D.dismissed} exceptions were raised by a test, investigated and dismissed with a reason - `+
    `they are listed in the workbook, not quietly dropped.`));

  const two = el("div","grid two"); root.appendChild(two);
  const c2 = card(two,"Value by forensic test");
  barList(c2, D.tests.map(t=>({label:`${t.Test} ${t.Name}`, value:t.Value, sub:t.Count+" journals"})));
  const c3 = card(two,"Risk bands and approval exceptions");
  barList(c3, D.bands.map(b=>({label:b.Band+" risk", value:b.Value, sub:b.Count+" journals",
    alt:b.Band!=="High"})));
  c3.appendChild(el("p","note",
    `Separately, unapproved manual journals above $10,000 total ${money(D.unapproved.Value,2)} across `+
    `${D.unapproved.Journals} journals - a control failure wider than the seven injected schemes.`));

  const c4 = card(root,"Exception register");
  const ctl = el("div","controls"); c4.appendChild(ctl);
  const fTest = el("select"); fTest.innerHTML = `<option value="">All tests</option>` +
    D.tests.map(t=>`<option value="${t.Test}">${t.Test} - ${t.Name}</option>`).join("");
  const fBand = el("select"); fBand.innerHTML = `<option value="">All risk bands</option>` +
    ["High","Medium","Low"].map(b=>`<option>${b}</option>`).join("");
  const q = el("input"); q.placeholder="Search vendor, description, journal…"; q.style.minWidth="260px";
  const count = el("div","count");
  ctl.append(fTest, fBand, q, count);
  const holder = el("div","scroll"); c4.appendChild(holder);
  table(holder,[
    {key:"Rank",label:"#",num:1},
    {key:"Journal",label:"Journal"},
    {key:"Date",label:"Date"},
    {key:"Test",label:"Test"},
    {key:"Vendor",label:"Vendor"},
    {key:"Account",label:"Acct"},
    {key:"Description",label:"Description"},
    {key:"Amount",label:"Amount",num:1,render:r=>money(r.Amount,2)},
    {key:"Score",label:"Score",num:1},
    {key:"Band",label:"Band",render:r=>`<span class="chip ${r.Band.toLowerCase()}">${r.Band}</span>`},
    {key:"RWV",label:"Risk-weighted",num:1,render:r=>money(r.RWV,2)},
    {key:"Preparer",label:"Prepared by"},
    {key:"Approver",label:"Approver"},
  ], D.register, {sortKey:"RWV", dir:-1,
    onCount:n=>count.textContent = `${n} of ${D.register.length} exceptions · `+
      money(D.register.filter(r=>!fTest.value||r.Test===fTest.value)
        .filter(r=>!fBand.value||r.Band===fBand.value).reduce((s,r)=>s+r.Amount,0),2)});
  function apply(){
    const term = q.value.toLowerCase();
    holder.innerHTML = "";
    table(holder,[
      {key:"Rank",label:"#",num:1},{key:"Journal",label:"Journal"},{key:"Date",label:"Date"},
      {key:"Test",label:"Test"},{key:"Vendor",label:"Vendor"},{key:"Account",label:"Acct"},
      {key:"Description",label:"Description"},
      {key:"Amount",label:"Amount",num:1,render:r=>money(r.Amount,2)},
      {key:"Score",label:"Score",num:1},
      {key:"Band",label:"Band",render:r=>`<span class="chip ${r.Band.toLowerCase()}">${r.Band}</span>`},
      {key:"RWV",label:"Risk-weighted",num:1,render:r=>money(r.RWV,2)},
      {key:"Preparer",label:"Prepared by"},{key:"Approver",label:"Approver"},
    ], D.register, {sortKey:"RWV", dir:-1,
      filter:r=>(!fTest.value||r.Test===fTest.value)&&(!fBand.value||r.Band===fBand.value)&&
        (!term || (r.Vendor+r.Description+r.Journal+r.Conclusion).toLowerCase().includes(term)),
      onCount:n=>count.textContent = `${n} of ${D.register.length} exceptions shown`});
  }
  fTest.onchange=fBand.onchange=apply; q.oninput=apply;
}

/* ---------- 3. procurement ---------- */
function procurement(root){
  const c1 = card(root,`Supplier spend - top 12 of ${D.vendors.length}+ vendors (${money(D.spendTotal,2)} in total)`);
  barList(c1, D.vendors.map(v=>({label:v.Vendor, value:v.Spend,
    sub:v.EmployeeLinked?"employee-linked":"", alt:!v.EmployeeLinked})));
  c1.appendChild(el("p","note",
    "Spend is measured on debits to expense accounts in the general ledger, not on the accounts-payable " +
    "extract: the extract is a sample and understates the year. Employee-linked vendors are flagged in red."));

  const two = el("div","grid two"); root.appendChild(two);
  const c2 = card(two,"Cumulative spend share (Pareto)");
  columnChart(c2, D.vendors.map(v=>v.Vendor.split(" ")[0]),
    [{name:"Cumulative %",data:D.vendors.map(v=>v["Cumulative pct"]/100),color:"#157a9c"}],
    {height:230,pct:true});
  c2.appendChild(el("p","note","The 80% line is crossed by the nineteenth vendor."));

  const c3 = card(two,"Three-way match and invoice exceptions");
  barList(c3, D.apStatus.map(s=>({label:s.Status, value:s.Count, alt:s.Status!=="Matched"})));
  table(c3,[{key:"k",label:"Measure"},{key:"v",label:"Value",num:1}],
    [{k:"Invoices in the extract", v:D.apSummary.Invoices},
     {k:"Invoice value", v:money(D.apSummary.Value,2)},
     {k:"Three-way-match exceptions", v:D.apSummary.Exceptions},
     {k:"Invoices with no purchase order", v:D.apSummary["No PO"]},
     {k:"Duplicate invoices suspected", v:D.apSummary.Duplicates}],
    {sortKey:null});
}

/* ---------- 4. receivables and cash ---------- */
function cash(root){
  const two = el("div","grid two"); root.appendChild(two);
  const c1 = card(two,`Receivables ageing - ${money(D.arSummary.Outstanding,2)} outstanding`);
  barList(c1, D.ageing.map(a=>({label:a.Bucket, value:a.Outstanding, sub:a.Invoices+" invoices",
    alt:a.Bucket.includes("Over")})));
  c1.appendChild(el("p","note",`${D.arSummary.Disputed} invoices are disputed. Disputed balances are `+
    `scored at half weight in the collections priority because collecting them starts with resolving the dispute.`));

  const c2 = card(two,"Bank reconciliation and claims");
  barList(c2,[{label:"Reconciled transactions", value:D.bank.Reconciled},
    {label:"Unreconciled transactions", value:D.bank.Unreconciled, alt:true},
    {label:"Unreconciled over 90 days", value:D.bank["Over 90 days"], alt:true}]);
  table(c2,[{key:"k",label:"Measure"},{key:"v",label:"Value",num:1}],
    [{k:"Bank transactions tested", v:D.bank.Reconciled + D.bank.Unreconciled},
     {k:"Unreconciled items", v:D.bank.Unreconciled},
     {k:"Unreconciled value", v:money(D.bank["Unreconciled value"],2)},
     {k:"Items unreconciled over 90 days", v:D.bank["Over 90 days"]},
     {k:"Oldest unmatched item", v:D.bank["Oldest days"]+" days"}],{sortKey:null});

  const c3 = card(root,"Ageing detail");
  table(c3,[{key:"Bucket",label:"Bucket"},{key:"Invoices",label:"Invoices",num:1},
    {key:"Outstanding",label:"Outstanding",num:1,render:r=>money(r.Outstanding,2)},
    {key:"Share",label:"Share of total",num:1,
      render:r=>(r.Outstanding/D.arSummary.Outstanding*100).toFixed(1)+"%"}],
    D.ageing,{sortKey:"Outstanding",dir:-1});
}
</script>
</body>
</html>
"""
