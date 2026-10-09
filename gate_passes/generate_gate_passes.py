#!/usr/bin/env python3
"""
Tererai Trent International School - Student Gate Pass generator.

Builds a printable A4 PDF of student gate passes (4 per page) for every
student who paid something towards their invoice, for both the Primary
and the Secondary school registers.  No fees / amounts appear on the
passes.  The official school logo (school-logo.png) is used as-is.

Usage:  python3 generate_gate_passes.py
Output: Tererai_Trent_Gate_Passes.pdf  (same folder)
"""

import os

from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

# --------------------------------------------------------------------------
# Data transcribed from the school payment registers (Term 3).
# Only students with an amount paid are included.  No amounts are printed.
# --------------------------------------------------------------------------

# (register no, first name, surname, class)
PRIMARY_PAID = [
    (1, "Anashe", "Mbasera", "Grade 4"),
    (2, "Alayna", "Lupahla", "Grade 4"),
    (3, "Mufudziwashe", "Moyosvi", "Grade 3"),
    (7, "Luyanda", "Nkau", "Grade 2"),
    (12, "Aitaishe", "Mbasera", "ECD"),
    (13, "Damian", "Pfumbi", "Grade 1"),
    (14, "Preston", "Sakuhuni", "Grade 4"),
    (15, "Chloe", "Sakuhuni", "Grade 5"),
    (16, "Chanel", "Sakuhuni", "Grade 2"),
    (17, "Bradley", "Tivatye", "Grade 5"),
]

SECONDARY_PAID = [
    (1, "Tanaka", "Gomo", "Form 2"),
    (2, "Tinaye", "Nhondova", "Form 5"),
    (3, "Munopa", "Rusere", "Form 1"),
    (4, "Katlego", "Mbanga", "Form 1"),
    (5, "Mutsawashe", "Chando", "Form 1"),
    (6, "Matthew", "Boka", "Form 1"),
    (8, "Crystal", "Manjeya", "Form 3"),
    (9, "Chantelle", "Manjeya", "Form 3"),
    (10, "Danai", "Motsi", "Form 6"),
    (12, "Matipaishe", "Moyosvi", "Form 3"),
    (13, "Keith", "Moyosvi", "Form 3"),
    (14, "Innocent", "Matanhire", "Form 1"),
    (15, "Malvern", "Matanhire", "Form 1"),
    (16, "Chenai", "Muchanyuka", "Form 1"),
    (17, "Eric", "Roberts", "Form 1"),
    (19, "Gemma", "Matereke", "Form 1"),
    (20, "Holly", "Matereke", "Form 1"),
    (21, "Conelius", "Mzenda", "Form 3"),
    (22, "Ethan", "Mutyanda", "Form 1"),
    (23, "Mirandah", "Mutyanda", "Form 2"),
    (24, "Cosmopolitan", "Bvekwa", "Form 1"),
    (25, "Rutendo T", "Garanehama", "Form 1"),
]

# --------------------------------------------------------------------------
# Brand colours
# --------------------------------------------------------------------------
BLUE = HexColor(0x2B5DA8)
BLUE_DK = HexColor(0x1E4784)
ORANGE = HexColor(0xF0821E)
GREY = HexColor(0x8A8F98)
LIGHT = HexColor(0xF7F9FC)

MM = 72.0 / 25.4  # mm -> points

VALIDITY = "12 – 16 OCTOBER 2026"

_HERE = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(_HERE, "school-logo.png")

_logo_reader = None


def draw_logo(cv, cx, top, h):
    """Draw the official school logo centred on cx, top edge at top."""
    global _logo_reader
    if _logo_reader is None:
        _logo_reader = ImageReader(LOGO_PATH)
    iw, ih = _logo_reader.getSize()
    w = h * iw / float(ih)
    cv.drawImage(_logo_reader, cx - w / 2.0, top - h, width=w, height=h,
                 mask="auto", preserveAspectRatio=True)


# --------------------------------------------------------------------------
# One gate pass
# --------------------------------------------------------------------------
def draw_pass(cv, x, y, w, h, name, section, klass, reg_no, pass_no):
    """x,y = bottom-left of the pass cell in points."""
    # dashed cut line
    cv.saveState()
    cv.setStrokeColor(GREY)
    cv.setLineWidth(0.6)
    cv.setDash(3, 3)
    cv.rect(x, y, w, h)
    cv.restoreState()

    ix, iy, iw, ih = x + 2.5 * MM, y + 2.5 * MM, w - 5 * MM, h - 5 * MM
    # card background + border
    cv.setFillColor(LIGHT)
    cv.setStrokeColor(BLUE)
    cv.setLineWidth(1.4)
    cv.roundRect(ix, iy, iw, ih, 6, stroke=1, fill=1)
    cv.setStrokeColor(ORANGE)
    cv.setLineWidth(0.8)
    cv.roundRect(ix + 1.6 * MM, iy + 1.6 * MM, iw - 3.2 * MM, ih - 3.2 * MM, 4,
                 stroke=1, fill=0)

    cx = ix + iw / 2.0
    top = iy + ih - 3 * MM
    draw_logo(cv, cx, top, 40 * MM)

    # title banner
    bw, bh = 52 * MM, 7 * MM
    by = top - 40 * MM - 3 * MM
    cv.setFillColor(BLUE)
    cv.roundRect(cx - bw / 2, by, bw, bh, 2.5 * MM, stroke=0, fill=1)
    cv.setFillColor(white)
    cv.setFont("Helvetica-Bold", 11)
    cv.drawCentredString(cx, by + 2.3 * MM, "STUDENT GATE PASS")

    # fields
    fy = by - 8 * MM
    cv.setFillColor(black)
    label_x = ix + 8 * MM
    val_x = ix + 28 * MM
    full_end = ix + iw - 8 * MM

    cv.setFont("Helvetica-Bold", 8.5)
    cv.setFillColor(BLUE_DK)
    cv.drawString(label_x, fy, "NAME :")
    cv.setFont("Helvetica-Bold", 10.5)
    cv.setFillColor(black)
    cv.drawString(val_x, fy, f"{name[0].upper()} {name[1].upper()}")
    cv.setStrokeColor(GREY)
    cv.setLineWidth(0.5)
    cv.line(val_x, fy - 1.6 * MM, full_end, fy - 1.6 * MM)
    fy -= 8 * MM

    # photo box (right-hand side, beside the remaining fields)
    pb_w, pb_h = 25 * MM, 28 * MM
    pb_x = ix + iw - 8 * MM - pb_w
    pb_y = fy - 4 * MM - pb_h
    cv.setStrokeColor(GREY)
    cv.setLineWidth(0.7)
    cv.setDash(2.5, 2)
    cv.rect(pb_x, pb_y, pb_w, pb_h)
    cv.setDash()
    cv.setFillColor(GREY)
    cv.setFont("Helvetica-Bold", 7.5)
    cv.drawCentredString(pb_x + pb_w / 2, pb_y + pb_h / 2 - 1 * MM, "PHOTO")
    cv.setFont("Helvetica", 6.2)
    cv.drawCentredString(pb_x + pb_w / 2, pb_y + pb_h / 2 - 4 * MM, "(affix recent photo)")

    line_end = pb_x - 4 * MM

    def field(label, value, vfont="Helvetica-Bold", vsize=10):
        nonlocal fy
        cv.setFont("Helvetica-Bold", 8.5)
        cv.setFillColor(BLUE_DK)
        cv.drawString(label_x, fy, label)
        cv.setFont(vfont, vsize)
        cv.setFillColor(black)
        cv.drawString(val_x, fy, value)
        cv.setStrokeColor(GREY)
        cv.setLineWidth(0.5)
        cv.line(val_x, fy - 1.6 * MM, line_end, fy - 1.6 * MM)
        fy -= 9 * MM

    field("SECTION :", section)
    field("CLASS :", klass.upper())
    field("PASS No :", pass_no)

    # validity line (full width, below the photo box)
    fy = pb_y - 6 * MM
    cv.setFont("Helvetica-Bold", 8.5)
    cv.setFillColor(BLUE_DK)
    cv.drawString(label_x, fy, "VALID :")
    cv.setFont("Helvetica-Bold", 10)
    cv.setFillColor(black)
    cv.drawString(val_x, fy, VALIDITY)
    cv.setStrokeColor(GREY)
    cv.setLineWidth(0.5)
    cv.line(val_x, fy - 1.6 * MM, full_end, fy - 1.6 * MM)

    # office-use box
    ob_h = 9 * MM
    ob_y = fy - 5 * MM - ob_h
    cv.setStrokeColor(GREY)
    cv.setLineWidth(0.6)
    cv.rect(label_x, ob_y, iw - 16 * MM, ob_h)
    cv.setFont("Helvetica-Bold", 6.4)
    cv.setFillColor(GREY)
    cv.drawString(label_x + 1.5 * MM, ob_y + ob_h - 2.6 * MM, "FOR OFFICE USE")

    # signature / date
    sy = iy + 11 * MM
    cv.setStrokeColor(black)
    cv.setLineWidth(0.7)
    cv.line(label_x, sy, label_x + 34 * MM, sy)
    cv.line(ix + iw - 9 * MM - 24 * MM, sy, ix + iw - 9 * MM, sy)
    cv.setFont("Helvetica", 7)
    cv.setFillColor(black)
    cv.drawString(label_x, sy - 3 * MM, "Authorised Signature / Stamp")
    cv.drawString(ix + iw - 9 * MM - 24 * MM, sy - 3 * MM, "Date")

    cv.setFont("Helvetica-Oblique", 6.6)
    cv.setFillColor(GREY)
    cv.drawCentredString(cx, iy + 3.2 * MM,
                         "This pass must be presented at the school gate.")


# --------------------------------------------------------------------------
# Build the PDF
# --------------------------------------------------------------------------
def main():
    out = os.path.join(_HERE, "Tererai_Trent_Gate_Passes.pdf")
    cv = canvas.Canvas(out, pagesize=A4)
    cv.setTitle("Tererai Trent International School - Student Gate Passes")

    pw, ph = A4
    passes = (
        [("PRIMARY", r, f"{n} {sn}", k, f"TTIS-P-{i:03d}")
         for i, (r, n, sn, k) in enumerate(PRIMARY_PAID, 1)]
        +
        [("SECONDARY", r, f"{n} {sn}", k, f"TTIS-S-{i:03d}")
         for i, (r, n, sn, k) in enumerate(SECONDARY_PAID, 1)]
    )

    margin, gap = 8 * MM, 5 * MM
    cw = (pw - 2 * margin - gap) / 2.0
    ch = (ph - 2 * margin - gap) / 2.0
    cells = [(margin, ph - margin - ch),
             (margin + cw + gap, ph - margin - ch),
             (margin, margin),
             (margin + cw + gap, margin)]

    for i, (section, reg_no, name, klass, pass_no) in enumerate(passes):
        if i and i % 4 == 0:
            cv.showPage()
        x, y = cells[i % 4]
        draw_pass(cv, x, y, cw, ch, (name.split(" ")[0], name.split(" ", 1)[1]),
                  section, klass, reg_no, pass_no)
    cv.showPage()
    cv.save()
    print(f"Wrote {out}  ({len(passes)} passes, {(len(passes) + 3) // 4} pages)")


if __name__ == "__main__":
    main()
