#!/usr/bin/env python3
"""
Tererai Trent International School - Student Gate Pass generator.

Builds a printable A4 PDF of student gate passes (4 per page) for every
student who paid something towards their invoice, for both the Primary
and the Secondary school registers.  No fees / amounts appear on the
passes.

Usage:  python3 generate_gate_passes.py
Output: Tererai_Trent_Gate_Passes.pdf  (same folder)
"""

import math
import os

from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth

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
    (14, "Innocent", "Matanhira", "Form 1"),
    (15, "Malvern", "Matanhira", "Form 1"),
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
# Brand colours (sampled from the school crest)
# --------------------------------------------------------------------------
ORANGE = HexColor(0xF0821E)
BLUE = HexColor(0x2B5DA8)
BLUE_DK = HexColor(0x1E4784)
TEAL = HexColor(0x35B28A)
TEAL_DK = HexColor(0x177E63)
RED = HexColor(0xD42A1E)
YELLOW = HexColor(0xF5B70A)
GREY = HexColor(0x8A8F98)
LIGHT = HexColor(0xF7F9FC)

MM = 72.0 / 25.4  # mm -> points

SCHOOL_LINE1 = "TERERAI TRENT INTERNATIONAL"
SCHOOL_LINE2 = "SCHOOL"
CAMPUS = "MANDARA CAMPUS"
MOTTO = "TINOGONA"
VALIDITY = "12 – 16 OCTOBER 2026"


# --------------------------------------------------------------------------
# Crest drawing (vector reproduction of the school logo)
# Local design space: 100 x 100, y-up.  (0,0)=bottom-left of crest box.
# --------------------------------------------------------------------------
def draw_crest(cv, cx_pt, top_pt, h_pt):
    """Draw the crest centred horizontally on cx_pt; top edge at top_pt."""
    s = h_pt / 100.0
    bottom = top_pt - h_pt

    def X(lx):
        return cx_pt + (lx - 50.0) * s

    def Y(ly):
        return bottom + ly * s

    def P(lx, ly):
        return (X(lx), Y(ly))

    cv.saveState()

    # ---- arched school name ------------------------------------------------
    def arc_text(text, radius, font, size, spread=None):
        cv.setFont(font, size * s)
        widths = [stringWidth(ch, font, size * s) for ch in text]
        total = sum(widths) + size * s * 0.12 * (len(text) - 1)
        ang_total = math.degrees(total / (radius * s))
        theta = 90.0 + ang_total / 2.0
        for ch, w in zip(text, widths):
            step = math.degrees((w + size * s * 0.12) / (radius * s))
            theta_mid = theta - step / 2.0
            cv.saveState()
            cv.translate(X(50), Y(40))
            cv.rotate(theta_mid - 90.0)
            cv.drawCentredString(0, radius * s, ch)
            cv.restoreState()
            theta -= step

    cv.setFillColor(black)
    arc_text(SCHOOL_LINE1, 46, "Times-Bold", 4.6)
    cv.setFont("Times-Bold", 5.6 * s)
    cv.drawCentredString(X(50), Y(79.5), SCHOOL_LINE2)
    cv.setFont("Times-Bold", 4.4 * s)
    cv.drawCentredString(X(50), Y(73.5), CAMPUS)

    # ---- shield body --------------------------------------------------------
    shield = cv.beginPath()
    x0, x1 = 31, 69
    shield.moveTo(*P(x0, 68))
    shield.curveTo(*P(x0 + 0.5, 71.5), *P(x0 + 2.5, 72.2), *P(x0 + 5, 72.2))
    shield.curveTo(*P(43, 72.2), *P(47, 71.4), *P(50, 71.4))
    shield.curveTo(*P(53, 71.4), *P(57, 72.2), *P(x1 - 5, 72.2))
    shield.curveTo(*P(x1 - 2.5, 72.2), *P(x1 - 0.5, 71.5), *P(x1, 68))
    shield.lineTo(*P(x1, 47))
    shield.curveTo(*P(x1, 37.5), *P(63, 31.5), *P(57, 28.8))
    shield.curveTo(*P(54.5, 27.7), *P(52, 27.2), *P(50, 27.2))
    shield.curveTo(*P(48, 27.2), *P(45.5, 27.7), *P(43, 28.8))
    shield.curveTo(*P(37, 31.5), *P(x0, 37.5), *P(x0, 47))
    shield.close()

    cv.setFillColor(white)
    cv.setStrokeColor(black)
    cv.setLineWidth(2.2 * s)
    cv.drawPath(shield, stroke=1, fill=1)

    # bottom-right quadrant: green with flame lily
    quad = cv.beginPath()
    quad.moveTo(*P(50, 47.5))
    quad.lineTo(*P(x1 - 1.2, 47.5))
    quad.lineTo(*P(x1 - 1.2, 47))
    quad.curveTo(*P(x1 - 1.2, 38), *P(62.5, 32.2), *P(56.7, 29.6))
    quad.curveTo(*P(54.4, 28.6), *P(52, 28.2), *P(50, 28.2))
    quad.close()
    cv.setFillColor(TEAL)
    cv.drawPath(quad, stroke=0, fill=1)

    # cross dividers
    cv.setStrokeColor(black)
    cv.setLineWidth(1.6 * s)
    p = cv.beginPath()
    p.moveTo(*P(50, 71.2))
    p.lineTo(*P(50, 27.6))
    p.moveTo(*P(31.6, 47.5))
    p.lineTo(*P(68.4, 47.5))
    cv.drawPath(p, stroke=1, fill=0)

    # ---- top-left: open book -------------------------------------------------
    bx, by = 40.5, 59.5
    cv.setFillColor(ORANGE)
    cov = cv.beginPath()
    cov.moveTo(*P(bx - 8, by - 2.5))
    cov.lineTo(*P(bx, by + 0.6))
    cov.lineTo(*P(bx + 8, by - 2.5))
    cov.lineTo(*P(bx + 8, by - 0.6))
    cov.lineTo(*P(bx, by + 2.4))
    cov.lineTo(*P(bx - 8, by - 0.6))
    cov.close()
    cv.drawPath(cov, stroke=0, fill=1)
    cv.setFillColor(white)
    for sgn in (-1, 1):
        pg = cv.beginPath()
        pg.moveTo(*P(bx + sgn * 7.2, by - 2.0))
        pg.lineTo(*P(bx, by + 0.9))
        pg.lineTo(*P(bx, by + 4.6))
        pg.lineTo(*P(bx + sgn * 7.2, by + 1.6))
        pg.close()
        cv.drawPath(pg, stroke=0, fill=1)
    cv.setStrokeColor(GREY)
    cv.setLineWidth(0.5 * s)
    for sgn in (-1, 1):
        for i in range(4):
            yy = by - 0.6 + i * 1.4
            ln = cv.beginPath()
            ln.moveTo(*P(bx + sgn * 6.2, yy))
            ln.lineTo(*P(bx + sgn * 1.0, yy + 2.2))
            cv.drawPath(ln, stroke=1, fill=0)

    # ---- top-right: dove ------------------------------------------------------
    dx, dy = 59.5, 59.5
    cv.setFillColor(ORANGE)
    body = cv.beginPath()
    body.moveTo(*P(dx - 4.5, dy - 0.5))
    body.curveTo(*P(dx - 4.0, dy + 2.6), *P(dx + 0.5, dy + 3.4), *P(dx + 2.6, dy + 2.2))
    body.curveTo(*P(dx + 3.6, dy + 1.6), *P(dx + 4.2, dy + 0.6), *P(dx + 4.4, dy - 0.4))
    body.curveTo(*P(dx + 3.0, dy - 1.8), *P(dx - 1.0, dy - 2.2), *P(dx - 4.5, dy - 0.5))
    body.close()
    cv.drawPath(body, stroke=0, fill=1)
    cv.circle(X(dx + 3.6), Y(dy + 3.4), 1.7 * s, stroke=0, fill=1)  # head
    beak = cv.beginPath()  # beak
    beak.moveTo(*P(dx + 5.1, dy + 3.8))
    beak.lineTo(*P(dx + 6.8, dy + 3.2))
    beak.lineTo(*P(dx + 5.1, dy + 2.8))
    beak.close()
    cv.drawPath(beak, stroke=0, fill=1)
    tail = cv.beginPath()  # tail
    tail.moveTo(*P(dx - 4.0, dy - 0.2))
    tail.lineTo(*P(dx - 7.6, dy - 2.6))
    tail.lineTo(*P(dx - 6.6, dy + 0.8))
    tail.lineTo(*P(dx - 4.2, dy + 1.0))
    tail.close()
    cv.drawPath(tail, stroke=0, fill=1)
    cv.setStrokeColor(ORANGE)
    cv.setLineWidth(0.7 * s)
    legs = cv.beginPath()  # legs
    legs.moveTo(*P(dx - 0.5, dy - 2.0))
    legs.lineTo(*P(dx - 0.7, dy - 4.2))
    legs.lineTo(*P(dx + 0.6, dy - 4.4))
    legs.moveTo(*P(dx + 1.6, dy - 1.9))
    legs.lineTo(*P(dx + 1.6, dy - 4.1))
    legs.lineTo(*P(dx + 2.9, dy - 4.3))
    cv.drawPath(legs, stroke=1, fill=0)

    # ---- bottom-left: spiral motif -------------------------------------------
    sx, sy = 40.5, 37.5
    cv.setStrokeColor(TEAL_DK)
    cv.setLineWidth(1.1 * s)
    sp = cv.beginPath()
    steps = 60
    for i in range(steps + 1):
        t = i / steps
        ang = t * 3.0 * 2 * math.pi
        r = 0.6 + t * 4.4
        px = sx + r * math.cos(ang)
        py = sy + r * math.sin(ang) * 0.95
        if i == 0:
            sp.moveTo(*P(px, py))
        else:
            sp.lineTo(*P(px, py))
    cv.drawPath(sp, stroke=1, fill=0)
    for i in range(14):  # petal ring
        ang = i / 14.0 * 2 * math.pi
        r0, r1 = 5.6, 7.6
        a2 = ang + 0.16
        a3 = ang - 0.16
        tri = cv.beginPath()
        tri.moveTo(*P(sx + r0 * math.cos(a2), sy + r0 * math.sin(a2) * 0.95))
        tri.lineTo(*P(sx + r1 * math.cos(ang), sy + r1 * math.sin(ang) * 0.95))
        tri.lineTo(*P(sx + r0 * math.cos(a3), sy + r0 * math.sin(a3) * 0.95))
        tri.close()
        cv.setFillColor(TEAL if i % 2 == 0 else TEAL_DK)
        cv.drawPath(tri, stroke=0, fill=1)

    # ---- bottom-right: flame lily ---------------------------------------------
    fx, fy = 59.5, 38.0
    cv.setStrokeColor(TEAL_DK)
    cv.setLineWidth(0.8 * s)
    stem = cv.beginPath()
    stem.moveTo(*P(fx, fy - 0.5))
    stem.curveTo(*P(fx - 0.6, fy - 3.0), *P(fx + 0.6, fy - 5.0), *P(fx, fy - 7.0))
    cv.drawPath(stem, stroke=1, fill=0)
    for sgn in (-1, 1):  # leaves
        lf = cv.beginPath()
        lf.moveTo(*P(fx, fy - 4.0))
        lf.curveTo(*P(fx + sgn * 3.4, fy - 4.2), *P(fx + sgn * 4.6, fy - 6.0),
                   *P(fx + sgn * 5.4, fy - 7.4))
        lf.curveTo(*P(fx + sgn * 3.0, fy - 6.6), *P(fx + sgn * 1.4, fy - 5.6),
                   *P(fx, fy - 4.0))
        lf.close()
        cv.setFillColor(TEAL_DK)
        cv.drawPath(lf, stroke=0, fill=1)
    for i, ang in enumerate((-125, -80, -40, 0, 40, 80, 125)):  # petals
        a = math.radians(ang + 90)
        pet = cv.beginPath()
        pet.moveTo(*P(fx, fy))
        pet.curveTo(*P(fx + 2.2 * math.cos(a - 0.5), fy + 2.2 * math.sin(a - 0.5)),
                    *P(fx + 5.0 * math.cos(a - 0.25), fy + 5.0 * math.sin(a - 0.25)),
                    *P(fx + 6.2 * math.cos(a), fy + 6.2 * math.sin(a)))
        pet.curveTo(*P(fx + 5.0 * math.cos(a + 0.25), fy + 5.0 * math.sin(a + 0.25)),
                    *P(fx + 2.2 * math.cos(a + 0.5), fy + 2.2 * math.sin(a + 0.5)),
                    *P(fx, fy))
        pet.close()
        cv.setFillColor(RED)
        cv.drawPath(pet, stroke=0, fill=1)
    cv.setStrokeColor(YELLOW)
    cv.setLineWidth(0.5 * s)
    st = cv.beginPath()  # stamens
    for ang in (-60, -20, 20, 60):
        a = math.radians(ang + 90)
        st.moveTo(*P(fx, fy))
        st.lineTo(*P(fx + 7.0 * math.cos(a), fy + 7.0 * math.sin(a)))
    cv.drawPath(st, stroke=1, fill=0)

    # ---- laurel branches -------------------------------------------------------
    for sgn in (-1, 1):
        for i in range(9):
            t = i / 8.0
            lx = 50 + sgn * (21 + 6.5 * math.sin(t * math.pi * 0.9))
            ly = 20 + t * 34
            lean = sgn * (28 - 14 * t)
            cv.saveState()
            cv.translate(X(lx), Y(ly))
            cv.rotate(-lean)
            cv.setFillColor(BLUE)
            cv.ellipse(-1.3 * s, -3.0 * s, 1.3 * s, 3.0 * s, stroke=0, fill=1)
            cv.restoreState()

    # ---- stars ------------------------------------------------------------------
    def star(cx, cy, r):
        pts = []
        for i in range(10):
            ang = math.pi / 2 + i * math.pi / 5
            rr = r if i % 2 == 0 else r * 0.45
            pts.append(P(cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        sp2 = cv.beginPath()
        sp2.moveTo(*pts[0])
        for q in pts[1:]:
            sp2.lineTo(*q)
        sp2.close()
        cv.setFillColor(BLUE)
        cv.drawPath(sp2, stroke=0, fill=1)

    star(41.5, 18.5, 2.6)
    star(50, 19.0, 4.2)
    star(58.5, 18.5, 2.6)

    # ---- ribbon ------------------------------------------------------------------
    cv.setFillColor(BLUE)
    for sgn in (-1, 1):  # tails
        tl = cv.beginPath()
        tl.moveTo(*P(50 + sgn * 19, 12.6))
        tl.lineTo(*P(50 + sgn * 27, 12.6))
        tl.lineTo(*P(50 + sgn * 24.5, 10.1))
        tl.lineTo(*P(50 + sgn * 27, 7.6))
        tl.lineTo(*P(50 + sgn * 19, 7.6))
        tl.close()
        cv.drawPath(tl, stroke=0, fill=1)
    cv.setFillColor(BLUE_DK)
    for sgn in (-1, 1):  # folds
        fd = cv.beginPath()
        fd.moveTo(*P(50 + sgn * 19, 12.6))
        fd.lineTo(*P(50 + sgn * 21, 13.6))
        fd.lineTo(*P(50 + sgn * 19, 13.6))
        fd.close()
        cv.drawPath(fd, stroke=0, fill=1)
    ban = cv.beginPath()
    ban.moveTo(*P(30, 7.6))
    ban.lineTo(*P(70, 7.6))
    ban.lineTo(*P(70, 13.6))
    ban.lineTo(*P(30, 13.6))
    ban.close()
    cv.setFillColor(BLUE)
    cv.drawPath(ban, stroke=0, fill=1)
    cv.setFillColor(ORANGE)
    cv.setFont("Helvetica-Bold", 3.6 * s)
    # letter-spaced motto
    motto = "  ".join(MOTTO)
    cv.drawCentredString(X(50), Y(9.2), motto)

    cv.restoreState()


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
    top = iy + ih - 4 * MM
    draw_crest(cv, cx, top, 36 * MM)

    # title banner
    bw, bh = 52 * MM, 7 * MM
    by = top - 36 * MM - 4 * MM
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
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "Tererai_Trent_Gate_Passes.pdf")
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
