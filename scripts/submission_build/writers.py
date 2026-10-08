"""
writers.py - formatting helpers so every Word, Excel and PowerPoint file in the
submission pack looks like it came from one firm.
"""
from __future__ import annotations

import os
from datetime import date

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.oxml import OxmlElement
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.dml.color import RGBColor as PRGBColor
from pptx.util import Inches, Pt as PPt

NAVY = RGBColor(0x0B, 0x2E, 0x4F)
TEAL = RGBColor(0x00, 0x8B, 0x8B)
GREY = RGBColor(0x59, 0x59, 0x59)
RED = RGBColor(0xB0, 0x1B, 0x1B)
HEX_NAVY = "0B2E4F"

# python-pptx has its own RGBColor class; the docx one is not accepted by its setters
PNAVY = PRGBColor(0x0B, 0x2E, 0x4F)
PTEAL = PRGBColor(0x00, 0x8B, 0x8B)
PGREY = PRGBColor(0x59, 0x59, 0x59)
PWHITE = PRGBColor(0xFF, 0xFF, 0xFF)
PLIGHT = PRGBColor(0xE4, 0xF2, 0xF2)
PBAND = PRGBColor(0xF5, 0xF8, 0xFA)
PBOX = PRGBColor(0xEA, 0xF1, 0xF6)
HEX_TEAL = "008B8B"
HEX_LIGHT = "EAF1F6"
HEX_BAND = "F5F8FA"
HEX_BAD = "FDECEA"

FIRM = "Maxhub Pvt Ltd"
FIRM_TAG = "Forensic Accounting  |  Data Analytics  |  Machine Learning & AI  |  Advisory Services"
CLIENT = "Mhondoro Manufacturing (Pvt) Ltd"
PERIOD = "1 January 2024 to 30 September 2025"
ISSUE_DATE = date(2025, 10, 8)
PREPARER = "T. Makuvaza, Engagement Manager"
REVIEWER = "Independent QC partner (Maxhub)"


# ---------------------------------------------------------------------------
# Word
# ---------------------------------------------------------------------------
def new_doc(landscape=False, title=None, subtitle=None, reference=None):
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(10.5)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.08
    sec = doc.sections[0]
    if landscape:
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = sec.page_height, sec.page_width
    sec.left_margin = sec.right_margin = Cm(2.0)
    sec.top_margin = sec.bottom_margin = Cm(1.8)
    for i, (size, color, bold) in enumerate(
            [(17, NAVY, True), (13, NAVY, True), (11.5, TEAL, True), (10.5, NAVY, True)], start=1):
        s = doc.styles[f"Heading {i}"]
        s.font.name = "Calibri"
        s.font.size = Pt(size)
        s.font.color.rgb = color
        s.font.bold = bold
    if title:
        p = doc.add_paragraph()
        r = p.add_run(FIRM.upper())
        r.font.size = Pt(9)
        r.font.color.rgb = TEAL
        r.font.bold = True
        h = doc.add_heading(title, level=1)
        h.paragraph_format.space_after = Pt(2)
        if subtitle:
            para(doc, subtitle, size=11, color=GREY, italic=True)
        meta = doc.add_paragraph()
        meta.paragraph_format.space_before = Pt(4)
        r = meta.add_run(f"Client: {CLIENT}    |    Period: {PERIOD}    |    "
                         f"Issued: {ISSUE_DATE:%d %B %Y}    |    Reference: {reference or 'MX-2025-01'}    |    "
                         f"Classification: Confidential")
        r.font.size = Pt(8.5)
        r.font.color.rgb = GREY
        rule(doc)
    return doc


def rule(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(8)
    pPr = p._p.get_or_add_pPr()
    b = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")
    bottom.set(qn("w:color"), HEX_TEAL)
    b.append(bottom)
    pPr.append(b)


def para(doc, text, size=10.5, bold=False, italic=False, color=None, align=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    r = p.add_run(text)
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    if color is not None:
        r.font.color.rgb = color
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "right":
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    return p


def rich(doc, parts, space_after=6):
    """parts = [(text, bold, italic)]"""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    for t, b, i in parts:
        r = p.add_run(t)
        r.font.bold = b
        r.font.italic = i
        r.font.size = Pt(10.5)
    return p


def bullets(doc, items, style="List Bullet", size=10.5):
    for it in items:
        p = doc.add_paragraph(style=style)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(it)
        r.font.size = Pt(size)


def numbered(doc, items):
    bullets(doc, items, style="List Number")


def table(doc, headers, rows, widths=None, font=8.5, header_font=8.5,
          number_cols=(), align_right=(), highlight=None, caption=None):
    if caption:
        para(doc, caption, size=9, bold=True, color=NAVY, space_after=2)
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        r = p.add_run(str(h))
        r.font.bold = True
        r.font.size = Pt(header_font)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade(hdr[i], HEX_NAVY)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for ci, val in enumerate(row):
            cells[ci].text = ""
            p = cells[ci].paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            txt = val
            bold = False
            if isinstance(val, str) and val.startswith("**") and val.endswith("**"):
                txt, bold = val[2:-2], True
            r = p.add_run("" if txt is None else str(txt))
            r.font.size = Pt(font)
            r.font.bold = bold
            if ci in align_right:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if ri % 2 == 1:
            for c in cells:
                shade(c, HEX_BAND)
        if highlight and highlight(ri, row):
            for c in cells:
                shade(c, HEX_BAD)
    if widths:
        for ci, w in enumerate(widths):
            for row in t.rows:
                row.cells[ci].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def kv_table(doc, pairs, w1=4.6, w2=12.0, font=9.5):
    t = doc.add_table(rows=0, cols=2)
    t.style = "Table Grid"
    for k, v in pairs:
        cells = t.add_row().cells
        cells[0].text = ""
        r = cells[0].paragraphs[0].add_run(k)
        r.font.bold = True
        r.font.size = Pt(font)
        shade(cells[0], HEX_LIGHT)
        cells[1].text = ""
        r = cells[1].paragraphs[0].add_run(str(v))
        r.font.size = Pt(font)
        cells[0].width = Cm(w1)
        cells[1].width = Cm(w2)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)


def page_break(doc):
    doc.add_page_break()


def sign_off(doc, extra=None):
    doc.add_paragraph()
    rule(doc)
    para(doc, f"Prepared by: {PREPARER}    |    Date: {ISSUE_DATE:%d %B %Y}", size=9)
    para(doc, f"Reviewed by (independent QC): {REVIEWER}    |    Date: {ISSUE_DATE:%d %B %Y}", size=9)
    if extra:
        for k, v in extra.items():
            para(doc, f"{k}: {v}", size=9)
    para(doc, "This report is confidential and prepared solely for the addressee for the purpose set out "
              "in section 1. It may not be relied upon by any other party without Maxhub's written consent. "
              "All data analysed is simulated engagement data generated for training purposes.",
         size=8, italic=True, color=GREY)


def footer(doc, text):
    for sec in doc.sections:
        p = sec.footer.paragraphs[0]
        p.text = text
        for r in p.runs:
            r.font.size = Pt(8)
            r.font.color.rgb = GREY


# ---------------------------------------------------------------------------
# Excel
# ---------------------------------------------------------------------------
THIN = Side(style="thin", color="C8D3DC")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
MONEY = '#,##0.00;[Red](#,##0.00);"-"'
MONEY0 = '#,##0;[Red](#,##0);"-"'
PCT = '0.0%'
NUM = '#,##0'


def new_wb():
    wb = Workbook()
    wb.remove(wb.active)
    return wb


def write_sheet(wb, name, headers, rows, formats=None, widths=None, title=None,
                note=None, freeze="A2", autofilter=True, tab_color=HEX_NAVY):
    ws = wb.create_sheet(name[:31])
    ws.sheet_properties.tabColor = tab_color
    r0 = 1
    if title:
        ws.cell(row=1, column=1, value=title).font = Font(bold=True, size=12, color=HEX_NAVY)
        r0 = 2
    if note:
        c = ws.cell(row=r0, column=1, value=note)
        c.font = Font(italic=True, size=9, color="595959")
        r0 += 1
    hdr_row = r0 + (1 if (title or note) else 0)
    if title or note:
        hdr_row = r0
    for ci, h in enumerate(headers, start=1):
        c = ws.cell(row=hdr_row, column=ci, value=h)
        c.font = Font(bold=True, size=9, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=HEX_NAVY)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    for ri, row in enumerate(rows, start=hdr_row + 1):
        for ci, val in enumerate(row, start=1):
            c = ws.cell(row=ri, column=ci, value=val)
            c.font = Font(size=9)
            c.border = BORDER
            if formats and ci - 1 < len(formats) and formats[ci - 1]:
                c.number_format = formats[ci - 1]
            if (ri - hdr_row) % 2 == 0:
                c.fill = PatternFill("solid", fgColor=HEX_BAND)
    if widths:
        for ci, w in enumerate(widths, start=1):
            ws.column_dimensions[get_column_letter(ci)].width = w
    else:
        for ci, h in enumerate(headers, start=1):
            ws.column_dimensions[get_column_letter(ci)].width = max(11, min(34, len(str(h)) + 4))
    if autofilter and rows:
        ws.auto_filter.ref = f"A{hdr_row}:{get_column_letter(len(headers))}{hdr_row + len(rows)}"
    if freeze:
        ws.freeze_panes = f"A{hdr_row + 1}" if freeze == "A2" else freeze
    return ws


def total_row(ws, row_idx, ncols, label="Total", label_col=1, money_cols=()):
    for ci in range(1, ncols + 1):
        c = ws.cell(row=row_idx, column=ci)
        c.font = Font(bold=True, size=9, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=HEX_TEAL)
    ws.cell(row=row_idx, column=label_col, value=label)
    for ci in money_cols:
        col = get_column_letter(ci)
        ws.cell(row=row_idx, column=ci, value=f"=SUM({col}{row_idx - 1 - 100000 + 1}:{col}{row_idx - 1})")


# ---------------------------------------------------------------------------
# PowerPoint
# ---------------------------------------------------------------------------
def new_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def slide_title(prs, title, subtitle=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    box = s.shapes.add_textbox(Inches(0.5), Inches(0.25), Inches(12.3), Inches(0.75))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title
    r.font.size = PPt(26)
    r.font.bold = True
    r.font.color.rgb = PNAVY
    if subtitle:
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = subtitle
        r2.font.size = PPt(12)
        r2.font.color.rgb = PGREY
    bar = s.shapes.add_shape(1, Inches(0.5), Inches(1.15), Inches(12.3), Inches(0.045))
    bar.fill.solid()
    bar.fill.fore_color.rgb = PTEAL
    bar.line.fill.background()
    return s


def slide_bullets(prs, title, items, subtitle=None, notes=None, size=16):
    s = slide_title(prs, title, subtitle)
    box = s.shapes.add_textbox(Inches(0.6), Inches(1.5), Inches(12.1), Inches(5.4))
    tf = box.text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        lvl = 0
        txt = it
        if isinstance(it, tuple):
            txt, lvl = it
        p.level = lvl
        r = p.add_run()
        r.text = ("▪  " if lvl == 0 else "–  ") + txt
        r.font.size = PPt(size if lvl == 0 else size - 3)
        r.font.color.rgb = PNAVY if lvl == 0 else PGREY
        p.space_after = PPt(9)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def slide_table(prs, title, headers, rows, subtitle=None, notes=None, font=10,
                widths=None, highlight_last=False):
    s = slide_title(prs, title, subtitle)
    shape = s.shapes.add_table(len(rows) + 1, len(headers), Inches(0.5), Inches(1.5),
                               Inches(12.3), Inches(0.4 + 0.32 * len(rows)))
    tbl = shape.table
    if widths:
        for i, w in enumerate(widths):
            tbl.columns[i].width = Inches(w)
    for ci, h in enumerate(headers):
        c = tbl.cell(0, ci)
        c.text = str(h)
        c.fill.solid()
        c.fill.fore_color.rgb = PNAVY
        for p in c.text_frame.paragraphs:
            for r in p.runs:
                r.font.size = PPt(font)
                r.font.bold = True
                r.font.color.rgb = PWHITE
    for ri, row in enumerate(rows, start=1):
        last = highlight_last and ri == len(rows)
        for ci, val in enumerate(row):
            c = tbl.cell(ri, ci)
            c.text = "" if val is None else str(val)
            if last:
                c.fill.solid()
                c.fill.fore_color.rgb = PLIGHT
            elif ri % 2 == 0:
                c.fill.solid()
                c.fill.fore_color.rgb = PBAND
            for p in c.text_frame.paragraphs:
                for r in p.runs:
                    r.font.size = PPt(font)
                    r.font.bold = last
                    r.font.color.rgb = PNAVY
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def slide_chart(prs, title, categories, series, chart_type="column", subtitle=None,
                notes=None, number_format='#,##0'):
    s = slide_title(prs, title, subtitle)
    data = CategoryChartData()
    data.categories = categories
    for name, vals in series:
        data.add_series(name, vals)
    ctype = {"column": XL_CHART_TYPE.COLUMN_CLUSTERED,
             "bar": XL_CHART_TYPE.BAR_CLUSTERED,
             "line": XL_CHART_TYPE.LINE_MARKERS,
             "pie": XL_CHART_TYPE.DOUGHNUT}[chart_type]
    gf = s.shapes.add_chart(ctype, Inches(0.6), Inches(1.5), Inches(12.1), Inches(5.4), data)
    ch = gf.chart
    ch.has_legend = len(series) > 1
    if ch.has_legend:
        ch.legend.position = XL_LEGEND_POSITION.BOTTOM
        ch.legend.include_in_layout = False
        ch.legend.font.size = PPt(10)
    for pl in ch.plots:
        pl.has_data_labels = len(categories) <= 12
        if pl.has_data_labels:
            pl.data_labels.font.size = PPt(9)
            pl.data_labels.number_format = number_format
            pl.data_labels.number_format_is_linked = False
    for ax in (ch.category_axis, ch.value_axis):
        ax.tick_labels.font.size = PPt(9)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def slide_kpis(prs, title, kpis, subtitle=None, notes=None):
    """kpis = [(label, value, comment)]"""
    s = slide_title(prs, title, subtitle)
    n = len(kpis)
    cols = min(n, 5)
    w = 12.3 / cols
    for i, (label, value, comment) in enumerate(kpis):
        row, col = divmod(i, cols)
        left = Inches(0.5 + col * w)
        top = Inches(1.6 + row * 2.2)
        box = s.shapes.add_shape(1, left, top, Inches(w - 0.22), Inches(1.9))
        box.fill.solid()
        box.fill.fore_color.rgb = PBOX
        box.line.color.rgb = PTEAL
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        r = p.add_run()
        r.text = label.upper()
        r.font.size = PPt(10)
        r.font.bold = True
        r.font.color.rgb = PGREY
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = str(value)
        r2.font.size = PPt(26)
        r2.font.bold = True
        r2.font.color.rgb = PNAVY
        p3 = tf.add_paragraph()
        r3 = p3.add_run()
        r3.text = comment
        r3.font.size = PPt(10)
        r3.font.color.rgb = PGREY
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def save_deck(prs, path):
    prs.save(path)
    return path


def ensure(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def money(v, dp=2):
    return f"{v:,.{dp}f}"


def usd(v, dp=2):
    return f"${v:,.{dp}f}"
