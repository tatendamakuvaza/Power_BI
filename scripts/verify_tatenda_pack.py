#!/usr/bin/env python3
"""Independently validate the separate-CSV delivery. Requires pypdf (optional layout check: pymupdf)."""
from pathlib import Path
import csv, zipfile, hashlib, re
from collections import Counter, defaultdict
from decimal import Decimal as D
from datetime import date
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'deliverables/Tatenda_Makuvaza_Power_BI'
csvdir=folder/'CSV_Tables'
pdfpath=folder/'Tatenda_Makuvaza_Power_BI_Workbook.pdf'
files=sorted(csvdir.glob('*.csv'))
assert len(files)==22
assert not (folder/'Tatenda_Makuvaza_Practice_Data.csv').exists()
bundle={}
for path in files:
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        assert 'RecordType' not in reader.fieldnames
        assert 'RecordID' not in reader.fieldnames
        assert 'AnomalyLabel' not in reader.fieldnames
        bundle[path.stem]=list(reader)
    raw=list(csv.DictReader((ROOT/'data/raw'/path.name).open(encoding='utf-8-sig',newline='')))
    for row in raw:row.pop('AnomalyLabel',None)
    assert bundle[path.stem]==raw, path.name
    assert reader.fieldnames==list(raw[0]), path.name
rows=[r for table in bundle.values() for r in table]
assert len(rows)==23416
gl=bundle['FactGLJournal']; account={r['AccountCode']:r for r in bundle['DimAccount']}
assert sum(D(r['Debit']) for r in gl)==D('122878886.54')
assert sum(D(r['Credit']) for r in gl)==D('122878886.54')
journal=defaultdict(D)
for r in gl:journal[r['JournalID']]+=D(r['Debit'])-D(r['Credit'])
assert len(journal)==5504 and all(v==0 for v in journal.values())
# Reconcile every source TB account/month, restoring debit-positive signs.
by_month=defaultdict(lambda:defaultdict(D))
for r in gl:by_month[r['Period']][r['AccountCode']]+=D(r['Debit'])-D(r['Credit'])
rolling=defaultdict(D)
for period in sorted(by_month):
    for a,v in by_month[period].items():rolling[a]+=v
    tb={r['AccountCode']:r for r in bundle['FactTrialBalance'] if r['Period']==period}
    for a in account:
        expected=D(tb[a]['ClosingBalance'])*(1 if account[a]['NormalBalance']=='Debit' else -1) if a in tb else D(0)
        assert abs(rolling[a]-expected)<=D('.01'),(period,a,rolling[a],expected)
for table,key in [('DimAccount','AccountCode'),('DimCostCentre','CostCentreCode'),('DimVendor','VendorID'),('DimUser','UserID'),('DimEmployee','EmployeeID'),('DimCustomer','CustomerID')]:
    assert len({r[key] for r in bundle[table]})==len(bundle[table])
for r in bundle['FactSalesOrders']:
    amount=D(r['Quantity'])*D(r['UnitPriceUSD'])*(1-D(r['DiscountPct'])/100)
    assert abs(amount-D(r['GrossAmountUSD']))<=D('.01')
for r in bundle['FactFixedAssets']:
    assert abs(D(r['CostUSD'])-D(r['AccumulatedDepreciationUSD'])-D(r['NBVUSD']))<=D('.01')
assert (date(2026,12,31)-date(2021,1,1)).days+1==2191
pdf=PdfReader(pdfpath)
text='\n'.join(p.extract_text() for p in pdf.pages)
for i in range(1,13):assert f'Module {i:02}' in text
assert 'Tatenda Makuvaza' in text
for file in files:assert hashlib.sha256(file.read_bytes()).hexdigest() in text
assert len(pdf.outline)>40
for r in csv.DictReader((ROOT/'data/raw/InjectionLog.csv').open()):assert r['EntryID'] in text
# Check the fixed prediction examples printed in the revised beginner lesson.
test=[r for r in bundle['maxhub_client_churn'] if r['Year']=='2025']
assert len(test)==30
assert sum(r['Stayed']=='0' for r in test)==18
counts=Counter((1-int(r['Stayed']),int(D(r['NPS'])<=6)) for r in test)
assert [counts[k] for k in [(1,1),(0,1),(0,0),(1,0)]]==[3,4,8,15]
for phrase in ['Edition 2', '22 separate CSV files', 'CSV_Tables/FactGLJournal.csv',
               '36.67%', '60.00%']:
    assert phrase in text,phrase
assert 'filtering RecordType' not in text
zpath=folder.parent/'Tatenda_Makuvaza_Power_BI_Learning_Pack.zip'
with zipfile.ZipFile(zpath) as z:
    assert len(z.namelist())==23 and z.testzip() is None
    for p in [*files,pdfpath]:
        assert z.read(folder.name+'/'+str(p.relative_to(folder)))==p.read_bytes()
try:
    import pymupdf
    doc=pymupdf.open(pdfpath)
    for i,page in enumerate(doc):
        for word in page.get_text('words'):
            assert word[0]>=45 and word[2]<=550,(i+1,word)
            assert word[1]>=20 and word[3]<=825,(i+1,word)
    print('PDF text geometry: PASS')
except ImportError:print('PDF geometry check skipped (install pymupdf to enable)')
print(f'PASS: {len(rows):,} CSV records, {len(bundle)} tables, {len(pdf.pages)} PDF pages; source fidelity, journal/TB, sales/asset, answer key and ZIP checks passed.')
