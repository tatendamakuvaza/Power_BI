#!/usr/bin/env python3
"""Independently validate the two-file delivery. Requires pypdf (optional layout check: pymupdf)."""
from pathlib import Path
import csv, zipfile, hashlib, re
from collections import Counter, defaultdict
from decimal import Decimal as D
from datetime import date
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'deliverables/Tatenda_Makuvaza_Power_BI'
csvpath=folder/'Tatenda_Makuvaza_Practice_Data.csv'
pdfpath=folder/'Tatenda_Makuvaza_Power_BI_Workbook.pdf'
with csvpath.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f); fields=reader.fieldnames; rows=list(reader)
assert len(rows)==23416 and len(fields)==213
assert len({r['RecordID'] for r in rows})==len(rows)
assert 'AnomalyLabel' not in fields
bundle=defaultdict(list)
for r in rows:
    assert None not in r
    bundle[r['RecordType']].append(r)
assert len(bundle)==22
for p in sorted((ROOT/'data/raw').glob('*.csv')):
    if p.stem=='InjectionLog':continue
    raw=list(csv.DictReader(p.open(encoding='utf-8-sig',newline='')))
    assert len(raw)==len(bundle[p.stem])
    for source,delivered in zip(raw,bundle[p.stem]):
        source.pop('AnomalyLabel',None)
        assert all(delivered[k]==v for k,v in source.items())
        assert all(not v for k,v in delivered.items() if k not in source and k not in ('RecordType','RecordID'))
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
assert hashlib.sha256(csvpath.read_bytes()).hexdigest() in text
assert len(pdf.outline)>40
for r in csv.DictReader((ROOT/'data/raw/InjectionLog.csv').open()):assert r['EntryID'] in text
# Execute the published standalone Python exercise against the delivered CSV.
manuscript=(ROOT/'learning_pack/workbook.md').read_text()
block=next(b for b in re.findall(r'```\n(.*?)\n```',manuscript,re.S) if b.startswith('import csv'))
import os
prior=os.getcwd();os.chdir(folder)
try:exec(compile(block,'PDF baseline lab','exec'),{})
finally:os.chdir(prior)
zpath=folder.parent/'Tatenda_Makuvaza_Power_BI_Learning_Pack.zip'
with zipfile.ZipFile(zpath) as z:
    assert len(z.namelist())==2 and z.testzip() is None
    for p in [csvpath,pdfpath]:assert z.read(folder.name+'/'+p.name)==p.read_bytes()
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
