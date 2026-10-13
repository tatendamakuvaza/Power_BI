"""Build the supplied Module 2 notes as the requested teaching-notes PDF.

Install: python -m pip install reportlab
Run from the repository root: python scripts/build_teaching_notes_pdf.py
Requires DejaVu Sans and DejaVu Sans Mono in /usr/share/fonts/truetype/dejavu/.
The requested combined filename is retained; the cover documents Module 2-only scope.
"""
from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'reference/Maxhub_Module_02_Detailed_Teaching_Notes.md'
OUTPUT = ROOT / 'Maxhub_PowerBI_Modules_01_and_02_Detailed_Teaching_Notes.pdf'
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
for name, filename in [
    ('DV', 'DejaVuSans.ttf'), ('DV-Bold', 'DejaVuSans-Bold.ttf'),
    ('DV-Mono', 'DejaVuSansMono.ttf'),
]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily('DV', normal='DV', bold='DV-Bold', italic='DV', boldItalic='DV-Bold')

NAVY = colors.HexColor('#14324C')
TEAL = colors.HexColor('#007E87')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle('BodyNotes', fontName='DV', fontSize=9.5, leading=14.5,
                          textColor=NAVY, spaceAfter=7, splitLongWords=True))
styles.add(ParagraphStyle('SectionNotes', parent=styles['BodyNotes'], fontName='DV-Bold',
                          fontSize=15, leading=20, textColor=TEAL,
                          spaceBefore=17, spaceAfter=9, keepWithNext=True))
styles.add(ParagraphStyle('SubsectionNotes', parent=styles['SectionNotes'],
                          fontSize=11.5, leading=16, spaceBefore=12, spaceAfter=7))
styles.add(ParagraphStyle('BulletNotes', parent=styles['BodyNotes'],
                          leftIndent=13, firstLineIndent=0, bulletIndent=0, spaceAfter=4))
styles.add(ParagraphStyle('CodeNotes', fontName='DV-Mono', fontSize=8.2, leading=12,
                          backColor=colors.HexColor('#EDF4F6'), borderPadding=9,
                          spaceBefore=5, spaceAfter=13))
styles.add(ParagraphStyle('CoverTitle', fontName='DV-Bold', fontSize=30, leading=38,
                          textColor=NAVY, spaceAfter=23))
styles.add(ParagraphStyle('CoverSub', parent=styles['BodyNotes'], fontSize=16,
                          leading=24, textColor=TEAL, spaceAfter=25))
styles.add(ParagraphStyle('CoverLabel', parent=styles['BodyNotes'], fontName='DV-Bold',
                          fontSize=10, textColor=TEAL, spaceAfter=18))


def inline(text):
    """Render only the inline Markdown syntax used in the supplied notes."""
    tokens = re.split(r'(`[^`]*`|\*\*.*?\*\*)', text)
    result = []
    for token in tokens:
        if token.startswith('`') and token.endswith('`'):
            result.append('<font name="DV-Mono" size="8.2">' + escape(token[1:-1]) + '</font>')
        elif token.startswith('**') and token.endswith('**'):
            result.append('<b>' + escape(token[2:-2]) + '</b>')
        else:
            result.append(escape(token))
    return ''.join(result)


def footer(canvas, doc):
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor('#CFDDE5'))
    canvas.line(45, 42, width - 45, 42)
    canvas.setFont('DV', 8)
    canvas.setFillColor(NAVY)
    canvas.drawString(45, 28, 'MAXHUB | Power BI teaching notes | Module 2')
    canvas.drawRightString(width - 45, 28, str(doc.page))
    canvas.restoreState()


def build():
    story = [
        Spacer(1, 65),
        Paragraph('MAXHUB • POWER BI', styles['CoverLabel']),
        Paragraph('Detailed<br/>Teaching Notes', styles['CoverTitle']),
        Paragraph('Module 2 — Connecting and Shaping Accounting Data with Power Query', styles['CoverSub']),
        Spacer(1, 25),
        Paragraph('<b>Scope of this edition</b>', styles['BodyNotes']),
        Paragraph('This PDF contains the Module 2 notes supplied by the user. '
                  'Module 1 content was not supplied and is not included. '
                  'The requested filename refers to Modules 01 and 02; '
                  'that filename does not indicate that Module 1 is present.', styles['BodyNotes']),
        Spacer(1, 16),
        Paragraph('The teaching instructions, field types, row counts, controls and '
                  'Power Query examples are reproduced from the supplied notes. '
                  'Dataset-specific values are teaching targets, not independently verified results.', styles['BodyNotes']),
        PageBreak(),
    ]
    lines = SOURCE.read_text(encoding='utf-8').splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith('```'):
            code = []
            index += 1
            while index < len(lines) and not lines[index].startswith('```'):
                code.append(lines[index])
                index += 1
            story.append(Preformatted('\n'.join(code), styles['CodeNotes']))
        elif line.startswith('# '):
            story.append(Paragraph(inline(line[2:]), styles['SectionNotes']))
        elif line.startswith('## '):
            story.append(Paragraph(inline(line[3:]), styles['SectionNotes']))
        elif line.startswith('### '):
            story.append(Paragraph(inline(line[4:]), styles['SubsectionNotes']))
        elif line.startswith('- '):
            story.append(Paragraph(inline(line[2:]), styles['BulletNotes'], bulletText='•'))
        elif re.match(r'^\d+\. ', line):
            number, text = line.split('. ', 1)
            story.append(Paragraph(inline(text), styles['BulletNotes'], bulletText=number + '.'))
        else:
            story.append(Paragraph(inline(line), styles['BodyNotes']))
        index += 1
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=45, leftMargin=45,
                            topMargin=43, bottomMargin=57,
                            title='Maxhub Power BI — Module 2 Detailed Teaching Notes',
                            author='Maxhub', subject='User-supplied Module 2 notes; Module 1 not included')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == '__main__':
    build()
