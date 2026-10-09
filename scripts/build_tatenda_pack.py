#!/usr/bin/env python3
"""Build the two-file learner ZIP from checked-in CSVs and the workbook manuscript.
Requires reportlab; validation additionally uses pypdf. Run from any directory.
"""
from pathlib import Path
import csv, hashlib, zipfile, re, json
from decimal import Decimal
from collections import defaultdict, Counter
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.graphics.shapes import Drawing, String, Rect, Line

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'/'Tatenda_Makuvaza_Power_BI'
OUT.mkdir(parents=True,exist_ok=True)
DATA={p.stem:list(csv.DictReader(p.open(encoding='utf-8-sig',newline=''))) for p in sorted((ROOT/'data/raw').glob('*.csv'))}
INJ=DATA.pop('InjectionLog')
# Do not give away investigation labels in the practice population.
for row in DATA['FactGLJournal']: row.pop('AnomalyLabel',None)
FIELDS={k:list(v[0]) for k,v in DATA.items()}
columns=['RecordType','RecordID']+list(dict.fromkeys(c for cs in FIELDS.values() for c in cs))
csvpath=OUT/'Tatenda_Makuvaza_Practice_Data.csv'
with csvpath.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=columns); w.writeheader()
    for name,rows in DATA.items():
        for i,row in enumerate(rows,1): w.writerow(dict(RecordType=name,RecordID=f'{name}:{i:06}',**row))
D=lambda x:Decimal(str(x or '0'))
def total(rows,c): return sum((D(r[c]) for r in rows),Decimal(0))
def money(x): return f'{x:,.2f}'
gl=DATA['FactGLJournal']; accounts={r['AccountCode']:r for r in DATA['DimAccount']}
movement=[r for r in gl if r['EntryType'] not in ('Opening','Closing')]
def pl(rows,line=None):
    return sum((D(r['Credit'])-D(r['Debit']) for r in rows if accounts[r['AccountCode']]['IsPL']=='Yes' and (line is None or accounts[r['AccountCode']]['FSLine']==line)),Decimal(0))
checks=[]
def ck(n,v): checks.append([n,str(v)])
ck('CSV records (all types)',f'{sum(map(len,DATA.values())):,}')
ck('CSV columns (including routing keys)',len(columns))
ck('Distinct GL journals',len({r['JournalID'] for r in gl}))
ck('Total GL debits / credits (each)',money(total(gl,'Debit')))
ck('GL debit minus credit',money(total(gl,'Debit')-total(gl,'Credit')))
for y in ['2024','2025']:
    rr=[r for r in movement if r['PostingDate'].startswith(y)]
    ck(y+' revenue (no opening/closing)',money(pl(rr,'Revenue')))
    ck(y+' P&L result (credit minus debit)',money(pl(rr)))
ck('Suspense 1990, all GL movement',money(sum((D(r['Debit'])-D(r['Credit']) for r in gl if r['AccountCode']=='1990'),Decimal(0))))
ck('Sales orders: sum GrossAmountUSD (already discounted)',money(total(DATA['FactSalesOrders'],'GrossAmountUSD')))
ck('AR outstanding (AmountUSD minus received)',money(total(DATA['FactARAgeing'],'AmountUSD')-total(DATA['FactARAgeing'],'AmountReceivedUSD')))
ck('Budget, all rows (unsigned mixed accounts)',money(total(DATA['FactBudget'],'BudgetUSD')))
ck('Fixed assets NBV (register only)',money(total(DATA['FactFixedAssets'],'NBVUSD')))
ck('AP unmatched three-way records',sum(r['ThreeWayMatch']!='Matched' for r in DATA['FactAPInvoices']))
ck('AP missing PO records',sum(not r['PONumber'].strip() for r in DATA['FactAPInvoices']))
ck('AP duplicate-suspected label records',sum(r['DuplicateSuspected']=='Yes' for r in DATA['FactAPInvoices']))
ck('Bank unreconciled records',sum(r['ReconciledFlag']=='No' for r in DATA['FactBankTransactions']))
ck('Expense claims without receipts',sum(r['ReceiptAttached']=='No' for r in DATA['FactExpenseClaims']))
ck('Engagement net fees',money(total(DATA['MaxhubEngagements'],'FeeUSD')-total(DATA['MaxhubEngagements'],'WriteOffUSD')))
ck('Weighted consultant utilisation',f"{100*total(DATA['maxhub_billable_hours'],'BillableHours')/total(DATA['maxhub_billable_hours'],'AvailableHours'):.2f}%")
ck('Pipeline weighted fees',money(sum((D(r['ExpectedFeeUSD'])*D(r['ProbabilityPct'])/100 for r in DATA['maxhub_pipeline']),Decimal(0))))
ck('Client-year churn outcomes (Stayed = 0)',sum(r['Stayed']=='0' for r in DATA['maxhub_client_churn']))
ck('Client-year churn rate',f"{100*sum(r['Stayed']=='0' for r in DATA['maxhub_client_churn'])/len(DATA['maxhub_client_churn']):.2f}%")
# Workbook rendering helpers.
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyX',fontName='Helvetica',fontSize=9.2,leading=12.8,spaceAfter=6,textColor=colors.HexColor('#24364B')))
styles.add(ParagraphStyle(name='SmallX',fontName='Helvetica',fontSize=7.4,leading=10,spaceAfter=4))
styles.add(ParagraphStyle(name='TitleX',fontName='Helvetica-Bold',fontSize=32,leading=37,textColor=colors.HexColor('#102E4A'),spaceAfter=18))
styles.add(ParagraphStyle(name='SubX',fontName='Helvetica',fontSize=15,leading=21,textColor=colors.HexColor('#087E8B'),spaceAfter=16))
styles.add(ParagraphStyle(name='CodeX',fontName='Courier',fontSize=7.3,leading=10,spaceAfter=10,backColor=colors.HexColor('#EFF4F8'),borderPadding=7))
styles['Heading1'].textColor=colors.HexColor('#102E4A'); styles['Heading1'].fontSize=22; styles['Heading1'].leading=27
styles['Heading2'].textColor=colors.HexColor('#087E8B'); styles['Heading2'].spaceBefore=13
story=[]
def p(s,style='BodyX'): return Paragraph(escape(str(s)),styles[style])
def table(rows,widths=None):
    header_style=ParagraphStyle('TH',parent=styles['SmallX'],textColor=colors.white,fontName='Helvetica-Bold')
    flow=[[Paragraph(escape(str(x)),header_style if i==0 else styles['SmallX']) for x in row] for i,row in enumerate(rows)]
    t=Table(flow,colWidths=widths or [490/len(rows[0])]*len(rows[0]),repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#102E4A')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F0F5F8')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),1,colors.HexColor('#10B5A6'))]))
    story.append(t); story.append(Spacer(1,10))
def code(s):
    # Authored snippets fit the print width; fail rather than silently clipping code.
    assert max(map(len,s.splitlines()),default=0)<=103, s
    story.append(Preformatted(s,styles['CodeX']))
def page(title): story.extend([PageBreak(),p(title,'Heading1')])

def chart():
    monthly=defaultdict(Decimal)
    for r in movement:
        if accounts[r['AccountCode']]['FSLine']=='Revenue': monthly[r['Period']]+=D(r['Credit'])-D(r['Debit'])
    vals=sorted(monthly.items()); d=Drawing(490,210); mx=float(max(monthly.values())); w=18
    d.add(String(0,194,'Expected visual: monthly revenue, USD',fontName='Helvetica-Bold',fontSize=11,fillColor=colors.HexColor('#102E4A')))
    for i,(label,v) in enumerate(vals):
        x=40+i*21; h=float(v)/mx*140
        d.add(Rect(x,30,w,h,fillColor=colors.HexColor('#087E8B'),strokeColor=None))
        if i%3==0:d.add(String(x,17,label[2:],fontSize=7))
    d.add(Line(35,30,487,30,strokeColor=colors.grey)); d.add(String(0,172,f'{mx/1e6:.2f}m',fontSize=8)); d.add(String(15,30,'0',fontSize=8))
    story.append(d)

def dynamic(name):
    if name=='CONTROLS': table([['Check (no filters unless stated)','Expected answer']]+checks,[325,165])
    elif name=='MANIFEST':
        table([['RecordType / query name','Rows','Source grain']]+[[k,f'{len(v):,}',GRAINS[k]] for k,v in DATA.items()],[185,45,260])
    elif name=='CHART': chart()
    elif name=='MONTHLY':
        rows=[['Period','Revenue USD','P&L result USD']]
        for period in sorted({r['Period'] for r in movement}):
            rr=[r for r in movement if r['Period']==period]; rows.append([period,money(pl(rr,'Revenue')),money(pl(rr))])
        table(rows,[110,190,190])
    elif name=='FORENSIC':
        groups=defaultdict(list)
        for r in INJ: groups[r['AnomalyType']].append(r)
        table([['Injected scheme','Journals','Debit-side amount USD']]+[[k,len(v),money(total(v,'AmountUSD'))] for k,v in sorted(groups.items())]+[['TOTAL',len(INJ),money(total(INJ,'AmountUSD'))]],[250,65,175])
    elif name=='RULES':
        rules=[('Manual GL lines',lambda r:r['EntryType']=='Manual'),('Manual weekend posting date',lambda r:r['EntryType']=='Manual' and __import__('datetime').date.fromisoformat(r['PostingDate']).weekday()>=5),('Missing approver, positive debit',lambda r:not r['ApprovedBy'].strip() and D(r['Debit'])>0),('Self-approved, positive debit',lambda r:bool(r['ApprovedBy'].strip()) and r['ApprovedBy']==r['PreparedBy'] and D(r['Debit'])>0),('Positive debit 4,900 to below 5,000',lambda r:4900<=D(r['Debit'])<5000),('USR-002 revenue lines',lambda r:r['PreparedBy']=='USR-002' and accounts[r['AccountCode']]['AccountType']=='Revenue')]
        table([['Rule (entire GL population)','Lines','Sum Debit USD']]+[[n,len(rr:=list(filter(fn,gl))),money(total(rr,'Debit'))] for n,fn in rules],[280,50,160])
    elif name=='TRAIN':
        table([['Split / purpose','Client-years','Churn = 0 label count','Stayed = 1 count']]+[[name,len(rr:=[r for r in DATA['maxhub_client_churn'] if lo<=int(r['Year'])<=hi]),sum(r['Stayed']=='0' for r in rr),sum(r['Stayed']=='1' for r in rr)] for name,lo,hi in [('Train 2021-2023',2021,2023),('Validation 2024',2024,2024),('Test 2025',2025,2025)]],[160,80,125,125])
    elif name=='EXTENDED':
        end='2025-09-30'
        rr=[r for r in gl if r['PostingDate']<=end]
        def balance(kind):
            return sum((D(r['Debit'])-D(r['Credit']) for r in rr if accounts[r['AccountCode']]['AccountType']==kind),Decimal(0))
        assets=balance('Asset'); liabilities=-balance('Liability'); equity=-balance('Equity')
        unclosed=-sum((D(r['Debit'])-D(r['Credit']) for r in rr if accounts[r['AccountCode']]['IsPL']=='Yes'),Decimal(0))
        cash=[r for r in rr if accounts[r['AccountCode']]['IsCashAccount']=='Yes']
        net=lambda rows:total(rows,'Debit')-total(rows,'Credit')
        revenue=lambda rows:pl(rows,'Revenue')
        y25=[r for r in movement if '2025-01-01'<=r['PostingDate']<=end]
        y24=[r for r in movement if '2024-01-01'<=r['PostingDate']<='2024-09-30']
        rb=sum((D(r['BudgetUSD']) for r in DATA['FactBudget'] if '2025-01'<=r['Period']<='2025-09' and accounts[r['AccountCode']]['FSLine']=='Revenue'),Decimal(0))
        forecast=revenue([r for r in movement if '2025-07'<=r['Period']<='2025-09'])/3
        pairs=[['2025-09-30 assets',money(assets)],['2025-09-30 liabilities',money(liabilities)],['2025-09-30 posted equity',money(equity)],['2025-09-30 unclosed P&L',money(unclosed)],['BS Check',money(assets-liabilities-equity-unclosed)],['2025 Jan-Sep cash opening',money(net([r for r in cash if r['PostingDate']<'2025-01-01']))],['2025 Jan-Sep cash movement',money(net([r for r in cash if r['PostingDate']>='2025-01-01']))],['2025-09-30 cash closing',money(net(cash))],['2024 Jan-Sep comparable revenue',money(revenue(y24))],['2025 Jan-Sep revenue growth',f'{100*(revenue(y25)/revenue(y24)-1):.2f}%'],['2025 Jan-Sep revenue budget',money(rb)],['2025 Jan-Sep revenue variance',money(revenue(y25)-rb)],['2025 Jan-Sep revenue variance %',f'{100*(revenue(y25)-rb)/rb:.2f}%'],['Flat forecast per month, Oct-Dec 2025',money(forecast)]]
        table([['Financial check (USD unless percentage)','Answer']]+pairs,[330,160])
        churn=DATA['maxhub_client_churn']; train=[r for r in churn if int(r['Year'])<=2023]; test=[r for r in churn if r['Year']=='2025']
        majority=Counter(1-int(r['Stayed']) for r in train).most_common(1)[0][0]
        out=[['2025 test rule','TP / FP / TN / FN','Accuracy / precision / recall']]
        for n,predict in [('Training majority',lambda r:majority),('Fixed NPS <= 6',lambda r:int(D(r['NPS'])<=6))]:
            counts=Counter((1-int(r['Stayed']),predict(r)) for r in test)
            tp,fp,tn,fn=[counts[k] for k in [(1,1),(0,1),(0,0),(1,0)]]
            out.append([n,f'{tp} / {fp} / {tn} / {fn}',f'{(tp+tn)/len(test):.2%} / {tp/(tp+fp):.2%} / {tp/(tp+fn):.2%}'])
        table(out,[150,130,210])
        story.append(p('These are exact results for the fixed teaching rules, not claims about a trained production model. Churn is the positive class. Same-year NPS has not been proven available before the outcome.'))
    elif name=='DICTIONARY':
        desc={(r['Table'],r['Column']):r['Description'] for r in csv.DictReader((ROOT/'data/dictionary/DataDictionary.csv').open())}
        for name,fields in FIELDS.items():
            page('Schema | '+name)
            story.append(p(f'{len(DATA[name]):,} rows. Grain: {GRAINS[name]}. Keep precisely these source columns after filtering RecordType. Routing columns are not needed in the final model.'))
            table([['Field','Suggested type','Meaning / example']]+[[c,typ(c,[r[c] for r in DATA[name]]),desc.get((name,c),'Example: '+next((r[c] for r in DATA[name] if r[c]),'(blank in this extract)'))] for c in fields],[130,80,280])
    elif name=='JOURNALS':
        table([['JournalID','Injected scheme','USD (one side)']]+[[r['EntryID'],r['AnomalyType'],money(D(r['AmountUSD']))] for r in INJ],[130,235,125])
    elif name=='HASH': story.append(p('Practice CSV SHA-256: '+hashlib.sha256(csvpath.read_bytes()).hexdigest(),'SmallX'))
    else: raise ValueError('Unknown workbook directive: '+name)

def typ(c,vs):
    non=[v for v in vs if v!='']
    if c=='EnteredOn':return 'Date/Time'
    if non and all(re.fullmatch(r'\d{4}-\d{2}-\d{2}',v) for v in non):return 'Date'
    if any(k in c for k in ['ID','Code','Account','Number','No','Period','Ref']) or c in ['FiscalYear','BankAccount']:return 'Text'
    try:
        nums=[D(v) for v in non]
        if not nums:return 'Text'
        if all(x==int(x) for x in nums):return 'Whole number'
        return 'Decimal number'
    except Exception:return 'Text'
GRAINS={
'DimAccount':'One chart-of-accounts member','DimCostCentre':'One cost centre','DimCustomer':'One customer','DimDate':'One calendar date','DimEmployee':'One employee','DimFXRate':'One currency / period rate','DimUser':'One posting user','DimVendor':'One vendor',
'FactAPInvoices':'One AP invoice','FactARAgeing':'One receivable invoice at the snapshot date','FactBankTransactions':'One bank statement transaction','FactBudget':'Account / cost centre / month / version','FactExpenseClaims':'One expense claim','FactFixedAssets':'One fixed asset at extract date','FactGLJournal':'One journal line (not one journal)','FactSalesOrders':'One sales order line','FactTrialBalance':'One account / month-end balance',
'MaxhubEngagements':'One consulting engagement','maxhub_billable_hours':'One consultant / month','maxhub_client_churn':'One client / year','maxhub_pipeline':'One sales opportunity','maxhub_service_line_financials':'One service line / month'}
# Cover
story.extend([Spacer(1,55),p('THE POWER BI\nPRACTICE WORKBOOK'.replace('\n',' '),'TitleX'),p('Accounting • Analytics • Forensics • AI • Advisory','SubX'),Spacer(1,20),p('Prepared for','BodyX'),p('Tatenda Makuvaza','TitleX'),p('A complete, hands-on companion to your 12-module learning path.','SubX'),Spacer(1,22)])
table([['YOUR PRACTICE LAB','WHAT YOU RECEIVE'],['22 typed populations in one CSV','A reusable financial and consulting analytics dataset'],['12 modules + 4 capstones','Notes, build steps, visual specifications and worked answers'],['Computed reconciliation controls','Monthly results and a full forensic journal answer key']],[245,245])
story.extend([Spacer(1,25),p('Edition 1 • 9 October 2026','BodyX'),p('Synthetic training records only. USD reporting unless stated. No real customer, employee or bank information. This is a learning pack, not an audit opinion or a completed Power BI report.','SmallX')])
text=(ROOT/'learning_pack/workbook.md').read_text()
in_code=False; buf=[]
for line in text.splitlines():
    if line.startswith('```'):
        if in_code:code('\n'.join(buf));buf=[]
        in_code=not in_code;continue
    if in_code:buf.append(line);continue
    if not line.strip():continue
    if line.startswith('@'):dynamic(line[1:].strip());continue
    if line.startswith('# '):page(line[2:]);continue
    if line.startswith('## '):story.append(p(line[3:],'Heading2'));continue
    if line.startswith('|'):
        # Markdown tables deliberately not used; generated tables carry dynamic values.
        raise ValueError(line)
    story.append(p(line))
assert not in_code
pdfpath=OUT/'Tatenda_Makuvaza_Power_BI_Workbook.pdf'
def footer(canvas,doc):
    canvas.saveState();canvas.setStrokeColor(colors.HexColor('#10B5A6'));canvas.line(52,42,543,42);canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#526579'));canvas.drawString(52,29,'TATENDA MAKUVAZA  /  POWER BI PRACTICE WORKBOOK');canvas.drawRightString(543,29,str(doc.page));canvas.restoreState()
class WorkbookDoc(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == 'Heading1':
            key = 'section-' + str(self.page)
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(flowable.getPlainText(), key, level=0)

doc=WorkbookDoc(str(pdfpath),pagesize=(595.28,841.89),rightMargin=52,leftMargin=52,topMargin=48,bottomMargin=58,title='Power BI Practice Workbook - Tatenda Makuvaza',author='Prepared for Tatenda Makuvaza')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
zip_path=OUT.parent/'Tatenda_Makuvaza_Power_BI_Learning_Pack.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for f in [csvpath,pdfpath]:z.write(f,OUT.name+'/'+f.name)
print(json.dumps({'csv_records':sum(map(len,DATA.values())),'csv_columns':len(columns),'pdf':str(pdfpath),'zip':str(zip_path),'checks':checks},indent=2))
