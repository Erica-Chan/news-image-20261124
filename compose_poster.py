#!/usr/bin/env python3
"""Compose the news-image-20261124 entry poster (1024x1024 PNG).

Newspaper front page, 38 stories / 9 regions: huge serif masthead, a
by-the-numbers panel, a UTC timeline strip, 3 large lead cards with
code-drawn flat vector illustrations, 13 medium cards each with a small
drawn illustration and a certainty badge, an also-on list with certainty
dots, a world map with numbered pins, and a date-check box naming
stories left out because they happened on earlier days. Every story is
dated Tuesday 24 November 2026 (UTC) and sourced; data lives in
stories.json. All drawing is PIL: deterministic, no network, no AI
images. Run:
    python3 compose_poster.py   # writes entry.png next to this file
"""
import hashlib
import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
CREAM = (247, 243, 227)
PAPER = (252, 249, 238)
NAVY = (20, 38, 77)
NAVY2 = (12, 22, 48)
RED = (178, 44, 32)
GOLD = (232, 184, 74)
INK = (24, 28, 36)
GREY = (82, 88, 98)
CARD = (255, 255, 255)
LINE = (205, 198, 178)
SKY = (214, 230, 240)
SEA = (16, 42, 74)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BADGE = {
    "CONFIRMED": (30, 125, 50),
    "OFFICIAL": (23, 90, 160),
    "REPORTED": (178, 106, 0),
    "CLAIM": (178, 60, 23),
    "PENDING": (91, 107, 124),
    "FORECAST": (106, 76, 160),
}


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def badge(d, x, y, label, fnt):
    """Certainty badge; returns width."""
    w = int(d.textlength(label, font=fnt)) + 12
    h = fnt.size + 8
    d.rounded_rectangle([x, y, x + w, y + h], radius=3,
                        fill=BADGE[label])
    d.text((x + 6, y + 4), label, font=fnt, fill=(255, 255, 255))
    return w


# --------------------------------------------------------------------------
# Flat vector illustrations (each draws inside a box of given size).
# --------------------------------------------------------------------------



def ill_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 245, 233))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(27, 94, 32))
    pts = [(0.04, 0.78), (0.18, 0.66), (0.30, 0.70), (0.44, 0.52),
           (0.58, 0.56), (0.72, 0.34), (0.86, 0.26), (0.97, 0.12)]
    for i in range(len(pts) - 1):
        d.line([x + w * pts[i][0], y + h * pts[i][1],
                x + w * pts[i + 1][0], y + h * pts[i + 1][1]],
               fill=(27, 94, 32), width=5)
    for px, py in pts[1:]:
        d.ellipse([x + w * px - 4, y + h * py - 4, x + w * px + 4,
                   y + h * py + 4], fill=(255, 255, 255),
                  outline=(27, 94, 32), width=2)
    # chip
    cx, cy, s = x + w * 0.16, y + h * 0.30, 26
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=(20, 38, 77),
                outline=(232, 184, 74), width=3)
    d.rectangle([cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2],
                fill=(232, 184, 74))
    for k in (-1, 0, 1):
        d.line([cx + k * 12, cy - s - 8, cx + k * 12, cy - s], fill=GOLD,
               width=2)
        d.line([cx + k * 12, cy + s, cx + k * 12, cy + s + 8], fill=GOLD,
               width=2)


def ill_tower(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 224, 200))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(120, 96, 74))
    # buildings
    for bx, bw, bh in [(0.04, 0.20, 0.34), (0.28, 0.16, 0.46),
                       (0.74, 0.22, 0.30)]:
        d.rectangle([x + w * bx, y + h * (0.62 - bh), x + w * (bx + bw),
                     y + h * 0.62], fill=(90, 82, 96))
    # telecom tower
    tx = x + w * 0.56
    d.polygon([(tx - 20, y + h * 0.62), (tx + 20, y + h * 0.62),
               (tx + 5, y + h * 0.12), (tx - 5, y + h * 0.12)],
              fill=(60, 60, 70))
    d.line([tx - 15, y + h * 0.20, tx + 15, y + h * 0.20], fill=(200, 60, 40),
           width=3)
    d.ellipse([tx - 4, y + h * 0.08 - 4, tx + 4, y + h * 0.08 + 4],
              fill=(200, 60, 40))
    # smoke + fire
    for cx, cy, r, col in [(0.58, 0.16, 11, (120, 120, 120)),
                           (0.62, 0.10, 8, (150, 150, 150)),
                           (0.52, 0.42, 10, (255, 170, 40)),
                           (0.55, 0.48, 7, (230, 80, 30))]:
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=col)


def ill_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 32, 56))
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(52, 58, 74))
    d.rectangle([x + w * 0.10, y + h * 0.18, x + w * 0.62, y + h * 0.72],
                fill=(140, 120, 90))
    for r in range(4):
        for c in range(4):
            wx = x + w * (0.16 + c * 0.12)
            wy = y + h * (0.24 + r * 0.12)
            col = (255, 190, 80) if (r + c) % 3 else (40, 44, 56)
            d.rectangle([wx, wy, wx + 10, wy + 8], fill=col)
    d.polygon([(x + w * 0.62, y + h * 0.18), (x + w * 0.62, y + h * 0.72),
               (x + w * 0.86, y + h * 0.72)], fill=(90, 76, 60))
    d.ellipse([x + w * 0.72 - 12, y + h * 0.16 - 12, x + w * 0.72 + 12,
               y + h * 0.16 + 12], fill=(150, 150, 150))
    d.ellipse([x + w * 0.80 - 8, y + h * 0.28 - 8, x + w * 0.80 + 8,
               y + h * 0.28 + 8], fill=(255, 170, 40))


def ill_eu(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
    cx, cy, r = x + w * 0.32, y + h * 0.52, h * 0.34
    import math
    for k in range(12):
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.polygon([(sx, sy - 5), (sx + 1.5, sy - 1.5), (sx + 5, sy),
                   (sx + 1.5, sy + 1.5), (sx, sy + 5), (sx - 1.5, sy + 1.5),
                   (sx - 5, sy), (sx - 1.5, sy - 1.5)], fill=(255, 204, 0))
    d.rectangle([x + w * 0.58, y + h * 0.20, x + w * 0.94, y + h * 0.80],
                fill=(255, 255, 255))
    d.rectangle([x + w * 0.58, y + h * 0.20, x + w * 0.94, y + h * 0.32],
                fill=(178, 44, 32))
    for i in range(3):
        yy = y + h * (0.44 + i * 0.12)
        d.line([x + w * 0.62, yy, x + w * 0.90, yy], fill=(150, 150, 160),
               width=2)


def ill_talks(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 214))
    d.ellipse([x + w * 0.5 - 52, y + h * 0.30 - 16, x + w * 0.5 + 52,
               y + h * 0.30 + 16], fill=(140, 100, 60))
    d.rectangle([x + w * 0.5 - 52, y + h * 0.30, x + w * 0.5 + 52,
                 y + h * 0.62], fill=(120, 84, 48))
    for fx, col in [(0.18, (20, 38, 77)), (0.38, (178, 44, 32)),
                    (0.62, (27, 94, 32)), (0.82, (120, 90, 20))]:
        fx0 = x + w * fx
        d.ellipse([fx0 - 9, y + h * 0.08 - 9, fx0 + 9, y + h * 0.08 + 9],
                  fill=(232, 196, 160))
        d.polygon([(fx0 - 12, y + h * 0.20), (fx0 + 12, y + h * 0.20),
                   (fx0 + 8, y + h * 0.30), (fx0 - 8, y + h * 0.30)],
                  fill=col)
    d.rectangle([x + w * 0.44, y + h * 0.26, x + w * 0.56, y + h * 0.34],
                fill=(255, 255, 255))




def ill_chips(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 240, 220))
    pts = [(0.05, 0.30), (0.22, 0.42), (0.38, 0.36), (0.55, 0.55),
           (0.72, 0.62), (0.95, 0.85)]
    for i in range(len(pts) - 1):
        d.line([x + w * pts[i][0], y + h * pts[i][1],
                x + w * pts[i + 1][0], y + h * pts[i + 1][1]],
               fill=(178, 44, 32), width=4)
    d.polygon([(x + w * 0.95, y + h * 0.85), (x + w * 0.88, y + h * 0.85),
               (x + w * 0.95, y + h * 0.72)], fill=(178, 44, 32))
    cx, cy, s = x + w * 0.22, y + h * 0.72, 13
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=(20, 38, 77),
                outline=(232, 184, 74), width=2)
    d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=(232, 184, 74))






def ill_capitol(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 230, 240))
    d.rectangle([x + w * 0.10, y + h * 0.62, x + w * 0.90, y + h * 0.86],
                fill=(240, 240, 235))
    d.rectangle([x + w * 0.42, y + h * 0.30, x + w * 0.58, y + h * 0.62],
                fill=(240, 240, 235))
    d.ellipse([x + w * 0.38, y + h * 0.08, x + w * 0.62, y + h * 0.40],
              fill=(240, 240, 235))
    d.rectangle([x + w * 0.48, y + h * 0.02, x + w * 0.52, y + h * 0.10],
                fill=(120, 120, 120))
    for i in range(5):
        xx = x + w * (0.16 + i * 0.15)
        d.rectangle([xx, y + h * 0.66, xx + 8, y + h * 0.86],
                    fill=(180, 180, 175))













def ill_trophy(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 125, 50))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(20, 90, 36))
    # cup
    cx = x + w * 0.5
    d.polygon([(cx - 26, y + h * 0.12), (cx + 26, y + h * 0.12),
               (cx + 16, y + h * 0.52), (cx - 16, y + h * 0.52)],
              fill=(232, 184, 74))
    d.arc([cx - 38, y + h * 0.12, cx - 14, y + h * 0.40], 90, 270,
          fill=(232, 184, 74), width=4)
    d.arc([cx + 14, y + h * 0.12, cx + 38, y + h * 0.40], 270, 90,
          fill=(232, 184, 74), width=4)
    d.rectangle([cx - 4, y + h * 0.52, cx + 4, y + h * 0.62],
                fill=(232, 184, 74))
    d.rectangle([cx - 18, y + h * 0.62, cx + 18, y + h * 0.70],
                fill=(232, 184, 74))
    d.text((cx - 5, y + h * 0.22), "1", font=font(SANS_B, 16),
           fill=(120, 90, 20))


def ill_satellite(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 10, 28))
    for sx, sy in [(0.1, 0.2), (0.25, 0.12), (0.85, 0.18), (0.9, 0.6),
                   (0.15, 0.75), (0.6, 0.85)]:
        d.ellipse([x + w * sx - 1, y + h * sy - 1, x + w * sx + 1,
                   y + h * sy + 1], fill=(255, 255, 255))
    # orbit ring
    d.arc([x + w * 0.08, y - h * 0.35, x + w * 0.92, y + h * 1.05],
          200, 340, fill=(120, 160, 200), width=2)
    cx, cy = x + w * 0.5, y + h * 0.45
    d.rectangle([cx - 26, cy - 6, cx - 8, cy + 6], fill=(90, 120, 180))
    d.rectangle([cx - 8, cy - 10, cx + 8, cy + 10], fill=(200, 200, 210))
    d.rectangle([cx + 8, cy - 6, cx + 26, cy + 6], fill=(232, 184, 74))
    d.line([cx, cy - 10, cx, cy - 20], fill=(255, 255, 255), width=2)
    d.ellipse([cx - 3, cy - 23, cx + 3, cy - 17], fill=(255, 80, 60))


def ill_border(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(220, 230, 240))
    d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(90, 110, 80))
    # fence posts + wire
    for fx in (0.12, 0.38, 0.64, 0.88):
        d.rectangle([x + w * fx - 2, y + h * 0.22, x + w * fx + 2,
                     y + h * 0.68], fill=(70, 70, 70))
    for wy in (0.28, 0.42, 0.56):
        d.line([x, y + h * wy, x + w, y + h * wy], fill=(120, 120, 120),
               width=2)
    # warning triangle
    tx, ty = x + w * 0.5, y + h * 0.30
    d.polygon([(tx, ty - 12), (tx + 13, ty + 10), (tx - 13, ty + 10)],
              fill=(255, 200, 60), outline=(178, 44, 32), width=2)
    d.text((tx - 2, ty - 6), "!", font=font(SANS_B, 12), fill=(178, 44, 32))


def ill_bars(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(245, 240, 230))
    d.line([x + 8, y + h - 10, x + w - 8, y + h - 10], fill=(60, 60, 60),
           width=2)
    vals = [(0.14, 0.24, (150, 150, 150)), (0.34, 0.30, (150, 150, 150)),
            (0.54, 0.38, (178, 44, 32)), (0.74, 0.44, (178, 44, 32))]
    for fx, fh, col in vals:
        bx = x + w * fx
        d.rectangle([bx - 9, y + h * (0.92 - fh), bx + 9, y + h * 0.92 - 10],
                    fill=col)
    d.text((x + 8, y + 4), "700k", font=font(SANS_B, 13), fill=(178, 44, 32))


def ill_jets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(190, 215, 235))
    for cx, cy, s in [(0.2, 0.75, 16), (0.5, 0.85, 20), (0.82, 0.7, 14)]:
        d.ellipse([x + w * cx - s, y + h * cy - s // 2, x + w * cx + s,
                   y + h * cy + s // 2], fill=(255, 255, 255))
    # two jets
    for jx, jy, sc in [(0.30, 0.35, 1.0), (0.68, 0.55, 0.8)]:
        jx0, jy0 = x + w * jx, y + h * jy
        d.polygon([(jx0 + 22 * sc, jy0), (jx0 - 12 * sc, jy0 - 8 * sc),
                   (jx0 - 6 * sc, jy0), (jx0 - 12 * sc, jy0 + 8 * sc)],
                  fill=(60, 60, 70))
        d.polygon([(jx0 - 4 * sc, jy0 - 12 * sc), (jx0 - 2 * sc, jy0),
                   (jx0 - 10 * sc, jy0)], fill=(60, 60, 70))
        d.line([jx0 - 12 * sc, jy0, jx0 - 30 * sc, jy0],
               fill=(255, 255, 255), width=2)


def ill_seal(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 245, 235))
    d.rectangle([x + w * 0.12, y + h * 0.10, x + w * 0.88, y + h * 0.90],
                fill=(255, 255, 255), outline=(180, 170, 150))
    for i in range(3):
        yy = y + h * (0.22 + i * 0.14)
        d.line([x + w * 0.18, yy, x + w * 0.62, yy], fill=(150, 150, 160),
               width=2)
    cx, cy, r = x + w * 0.68, y + h * 0.58, 14
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 44, 32))
    d.ellipse([cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3],
              outline=(255, 255, 255), width=1)
    d.text((cx - 4, cy - 7), "*", font=font(SANS_B, 13),
           fill=(255, 255, 255))


def ill_radar(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(10, 30, 20))
    cx, cy = x + w * 0.5, y + h * 0.55
    for r in (26, 18, 10):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(60, 160, 90),
                  width=1)
    d.line([cx, cy - 26, cx, cy + 26], fill=(60, 160, 90), width=1)
    d.line([cx - 26, cy, cx + 26, cy], fill=(60, 160, 90), width=1)
    d.line([cx, cy, cx + 20, cy - 16], fill=(120, 255, 150), width=2)
    for bx, by in [(0.30, 0.35), (0.68, 0.30), (0.62, 0.68)]:
        d.ellipse([x + w * bx - 3, y + h * by - 3, x + w * bx + 3,
                   y + h * by + 3], fill=(120, 255, 150))


def ill_pumpjack(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 220, 160))
    d.ellipse([x + w * 0.78 - 14, y + h * 0.12 - 14, x + w * 0.78 + 14,
               y + h * 0.12 + 14], fill=(255, 200, 60))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(160, 120, 70))
    # pumpjack: tower + beam
    bx = x + w * 0.42
    d.polygon([(bx - 12, y + h * 0.72), (bx + 12, y + h * 0.72),
               (bx + 4, y + h * 0.30), (bx - 4, y + h * 0.30)],
              fill=(60, 60, 70))
    d.rectangle([bx - 34, y + h * 0.26, bx + 30, y + h * 0.32],
                fill=(40, 40, 50))
    d.ellipse([bx + 22, y + h * 0.26, bx + 36, y + h * 0.40],
              fill=(40, 40, 50))
    d.line([bx + 29, y + h * 0.40, bx + 29, y + h * 0.72],
           fill=(40, 40, 50), width=2)
    d.line([bx - 34, y + h * 0.30, bx - 34, y + h * 0.72],
           fill=(40, 40, 50), width=2)


def ill_hospital(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(230, 240, 245))
    d.rectangle([x + w * 0.14, y + h * 0.28, x + w * 0.86, y + h * 0.82],
                fill=(255, 255, 255), outline=(150, 150, 150))
    d.rectangle([x + w * 0.44, y + h * 0.34, x + w * 0.56, y + h * 0.62],
                fill=(178, 44, 32))
    d.rectangle([x + w * 0.36, y + h * 0.42, x + w * 0.64, y + h * 0.54],
                fill=(178, 44, 32))
    d.polygon([(x + w * 0.14, y + h * 0.28), (x + w * 0.50, y + h * 0.10),
               (x + w * 0.86, y + h * 0.28)], fill=(200, 60, 50))
    d.rectangle([x, y + h * 0.82, x + w, y + h], fill=(120, 160, 110))


MEDIUM_ILL = {
    4: ill_trophy, 5: ill_satellite, 6: ill_border, 7: ill_bars,
    8: ill_talks, 9: ill_chips, 10: ill_jets, 11: ill_seal,
    12: ill_radar, 13: ill_pumpjack, 14: ill_hospital, 15: ill_eu,
    16: ill_capitol,
}


# --------------------------------------------------------------------------
# World map: simplified continent polygons (lon, lat), drawn on a light
# ocean panel; pins are numbered to match story numbers.
# --------------------------------------------------------------------------

CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-130, 71), (-120, 72), (-105, 68), (-95, 69),
     (-85, 70), (-80, 73), (-68, 62), (-60, 55), (-55, 52), (-60, 47),
     (-65, 44), (-70, 42), (-75, 35), (-80, 32), (-84, 30), (-90, 21),
     (-95, 18), (-97, 16), (-92, 14), (-86, 12), (-83, 9), (-79, 8),
     (-82, 10), (-87, 13), (-92, 15), (-97, 16), (-105, 20), (-110, 23),
     (-114, 28), (-117, 33), (-122, 38), (-124, 46), (-128, 52),
     (-135, 58), (-150, 60), (-162, 58), (-168, 66)],
    # South America
    [(-79, 8), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-70, -52),
     (-66, -55), (-65, -48), (-62, -40), (-58, -34), (-52, -32),
     (-48, -28), (-40, -20), (-35, -8), (-35, -5), (-42, -2), (-50, 0),
     (-52, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12), (-77, 8)],
    # Africa
    [(-6, 35), (-10, 31), (-15, 27), (-17, 21), (-17, 15), (-15, 11),
     (-12, 8), (-8, 5), (-4, 5), (2, 6), (6, 4), (9, 4), (9, 0), (12, -5),
     (13, -12), (12, -18), (14, -22), (16, -28), (19, -34), (25, -34),
     (28, -32), (32, -28), (35, -24), (36, -18), (40, -15), (40, -10),
     (42, -4), (46, -1), (51, 2), (51, 11), (44, 11), (43, 12), (40, 15),
     (38, 18), (36, 22), (34, 27), (32, 31), (30, 31), (22, 33), (11, 37),
     (10, 37), (0, 36), (-6, 35)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 44), (-2, 48), (0, 50), (2, 51), (5, 53),
     (8, 57), (10, 59), (5, 60), (5, 62), (10, 64), (14, 67), (18, 69),
     (25, 71), (32, 70), (40, 68), (50, 69), (60, 69), (70, 72), (80, 73),
     (90, 75), (100, 77), (110, 76), (120, 73), (130, 72), (140, 72),
     (150, 70), (160, 69), (170, 67), (178, 65), (170, 60), (162, 60),
     (158, 53), (150, 59), (142, 59), (140, 52), (135, 43), (130, 42),
     (127, 40), (122, 39), (120, 35), (122, 31), (120, 25), (116, 23),
     (110, 20), (108, 18), (105, 10), (104, 8), (100, 7), (98, 10),
     (95, 16), (92, 21), (89, 22), (86, 20), (82, 17), (80, 13), (77, 8),
     (74, 20), (70, 22), (66, 25), (62, 25), (58, 26), (56, 27), (52, 28),
     (50, 30), (48, 30), (44, 29), (40, 20), (38, 18), (35, 28), (34, 31),
     (36, 36), (30, 36), (27, 37), (23, 36), (22, 38), (19, 42), (16, 44),
     (12, 44), (8, 44), (3, 43), (-1, 38), (-6, 36), (-9, 37), (-10, 36)],
    # Australia
    [(114, -22), (114, -30), (115, -35), (118, -35), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
     (146, -19), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20), (114, -22)],
]


def draw_map(d, x, y, w, h, stories):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    for poly in CONTINENTS:
        pts = [(x + (lon + 180) / 360 * w, y + (90 - lat) / 180 * h)
               for lon, lat in poly]
        d.polygon(pts, fill=(226, 216, 178), outline=(180, 168, 130))
    # manual spread for pins that would otherwise stack
    OFF = {3: (1, 2), 4: (-12, 6), 5: (1, -12), 6: (6, -10),
           7: (11, -9), 8: (-14, 12), 9: (12, -10), 11: (-16, 12),
           12: (4, 5), 13: (19, 12), 15: (-10, 5), 16: (-15, -8)}
    for s in stories:
        if s["kind"] == "also":
            continue
        px = x + (s["lon"] + 180) / 360 * w
        py = y + (90 - s["lat"]) / 180 * h
        ox, oy = OFF.get(s["n"], (0, 0))
        px += ox
        py += oy
        r = 8
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(s["n"])
        tw = d.textlength(t, font=font(SANS_B, 9))
        d.text((px - tw / 2, py - 5), t, font=font(SANS_B, 9),
               fill=(255, 255, 255))


def main():
    with open(os.path.join(HERE, "stories.json")) as f:
        data = json.load(f)
    stories = data["stories"]
    leads = [s for s in stories if s.get("kind") == "lead"]
    mediums = [s for s in stories if s.get("kind") == "medium"]
    also = [s for s in stories if s.get("kind") not in ("lead", "medium")]
    for s in also:
        s["kind"] = "also"

    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    MX = 16  # side margin

    # --- top bar -----------------------------------------------------------
    d.rectangle([0, 0, W, 26], fill=NAVY)
    d.text((MX, 5), "THE WORLD IN ONE DAY", font=font(SANS_B, 13),
           fill=CREAM)
    right = "38 STORIES · 9 REGIONS · EVERY ONE DATED TUESDAY 24 NOVEMBER 2026"
    d.text((W - MX - d.textlength(right, font=font(SANS_B, 12)), 6),
           right, font=font(SANS_B, 12), fill=GOLD)

    # --- masthead ----------------------------------------------------------
    f_mast = font(SERIF_B, 56)
    d.text((MX, 30), "Tuesday 24 November 2026", font=f_mast, fill=INK)
    d.line([MX, 98, W - MX, 98], fill=INK, width=2)
    f_sub = font(SANS_B, 15)
    sub = ("Houthi missile hits Riyadh tower  ·  Nvidia gives back $240bn  ·  "
           "2 killed in Zaporizhzhia strike")
    d.text((MX, 104), sub, font=f_sub, fill=RED)

    # --- by the numbers ------------------------------------------------------
    ny = 126
    d.rectangle([MX, ny, W - MX, ny + 58], fill=PAPER, outline=LINE)
    nums = data["numbers"]
    cw = (W - 2 * MX) / len(nums)
    for i, (big, label) in enumerate(nums):
        cx = MX + i * cw
        if i:
            d.line([cx, ny + 8, cx, ny + 50], fill=LINE, width=1)
        f_big = font(SERIF_B, 30)
        bw = d.textlength(big, font=f_big)
        d.text((cx + (cw - bw) / 2, ny + 4), big, font=f_big, fill=RED)
        f_lab = font(SANS, 10)
        lw = d.textlength(label, font=f_lab)
        d.text((cx + (cw - lw) / 2, ny + 40), label, font=f_lab, fill=GREY)

    # --- region bar ----------------------------------------------------------
    regions = []
    for s in stories:
        if s["region"] not in regions:
            regions.append(s["region"])
    counts = {r: sum(1 for s in stories if s["region"] == r)
              for r in regions}
    RCOL = {"Middle East": (178, 44, 32), "North America": (23, 90, 160),
            "Europe": (0, 90, 120), "Africa": (30, 125, 50),
            "East Asia": (178, 120, 0), "South Asia": (150, 60, 120),
            "Latin America": (16, 120, 110), "Oceania": (106, 76, 160),
            "World": (80, 80, 80)}
    ry = 190
    seg_w = (W - 2 * MX) / len(regions)
    for i, r in enumerate(regions):
        x0 = MX + i * seg_w
        d.rectangle([x0, ry, x0 + seg_w - 2, ry + 20], fill=RCOL[r])
        t = f"{r.upper()} {counts[r]}"
        tw = d.textlength(t, font=font(SANS_B, 10))
        d.text((x0 + (seg_w - 2 - tw) / 2, ry + 5), t,
               font=font(SANS_B, 10), fill=(255, 255, 255))

    # --- UTC timeline ---------------------------------------------------------
    ty = 216
    d.rectangle([MX, ty, W - MX, ty + 22], fill=NAVY)
    tl = "  THE DAY IN UTC   " + "   ·   ".join(
        f"{t}  {txt}" for t, txt in data["timeline"])
    f_tl = font(SANS_B, 10)
    while d.textlength(tl, font=f_tl) > W - 2 * MX - 8 and f_tl.size > 9:
        f_tl = font(SANS_B, f_tl.size - 1)
    assert d.textlength(tl, font=f_tl) <= W - 2 * MX - 8, "timeline too long"
    d.text((MX + 4, ty + 5), tl, font=f_tl, fill=CREAM)

    # --- 3 lead cards ---------------------------------------------------------
    ly = 246
    lw = 324
    lgap = 10
    lh = 232
    for i, s in enumerate(leads):
        x = MX + i * (lw + lgap)
        d.rounded_rectangle([x, ly, x + lw, ly + lh], radius=6,
                            fill=CARD, outline=LINE, width=1)
        ill = [ill_tower, ill_markets, ill_kyiv][i]
        ill(d, x + 1, ly + 1, lw - 2, 112)
        badge(d, x + lw - 78, ly + 8, s["certainty"], font(SANS_B, 9))
        tx = x + 10
        tw = lw - 20
        yy = ly + 120
        d.text((tx, yy), f"{s['n']}  {s['place']} · {s['region'].upper()}",
               font=font(SANS_B, 10), fill=RED)
        yy += 16
        hl = wrap(d, s["headline"], font(SERIF_B, 18), tw)
        assert len(hl) <= 2, f"lead {s['n']} headline wraps to {len(hl)}"
        hl = hl[:2]
        for ln in hl:
            d.text((tx, yy), ln, font=font(SERIF_B, 18), fill=INK)
            yy += 21
        bl = wrap(d, s["body"], font(SANS, 11), tw)
        assert len(bl) <= 2, f"lead {s['n']} body wraps to {len(bl)} lines"
        bl = bl[:2]
        for ln in bl:
            d.text((tx, yy), ln, font=font(SANS, 11), fill=GREY)
            yy += 14
        assert yy <= ly + lh - 18, f"lead {s['n']} body overflows"
        d.text((tx, ly + lh - 16), s["source"], font=font(SANS, 9),
               fill=GREY)

    # --- 12 medium cards, 2 rows x 6 -----------------------------------------
    my = ly + lh + 8
    mcw = 136
    mrow_h = 134
    for i, s in enumerate(mediums):
        row, col = (0, i) if i < 7 else (1, i - 7)
        if row == 0:
            x = MX + round(col * (W - 2 * MX - mcw) / 6)
        else:
            x = MX + 71 + round(col * (W - 2 * MX - mcw) / 6)
        y = my + row * (mrow_h + 8)
        d.rounded_rectangle([x, y, x + mcw, y + mrow_h], radius=5,
                            fill=CARD, outline=LINE, width=1)
        MEDIUM_ILL[s["n"]](d, x + 1, y + 1, mcw - 2, 52)
        badge(d, x + mcw - 64, y + 6, s["certainty"], font(SANS_B, 8))
        tx = x + 7
        tw = mcw - 14
        yy = y + 56
        d.text((tx, yy), f"{s['n']} {s['place']}",
               font=font(SANS_B, 8), fill=RED)
        yy += 12
        hl = wrap(d, s["headline"], font(SERIF_B, 11), tw)
        assert len(hl) <= 2, f"medium {s['n']} headline wraps to {len(hl)}"
        hl = hl[:2]
        for ln in hl:
            d.text((tx, yy), ln, font=font(SERIF_B, 11), fill=INK)
            yy += 13
        bl = wrap(d, s["body"], font(SANS, 9), tw)
        assert len(bl) <= 2, f"medium {s['n']} body wraps to {len(bl)} lines"
        bl = bl[:2]
        for ln in bl:
            d.text((tx, yy), ln, font=font(SANS, 9), fill=GREY)
            yy += 11
        assert yy <= y + mrow_h - 14, f"medium {s['n']} body overflows"
        d.text((tx, y + mrow_h - 13), s["source"], font=font(SANS, 8),
               fill=GREY)

    # --- bottom: also-on list + map -------------------------------------------
    by = my + 2 * mrow_h + 16
    bh = 154
    list_w = 660
    d.rounded_rectangle([MX, by, MX + list_w, by + bh], radius=5,
                        fill=PAPER, outline=LINE, width=1)
    title = f"ALSO ON TUESDAY — {len(also)} MORE STORIES"
    d.text((MX + 10, by + 6), title, font=font(SANS_B, 11), fill=INK)
    # certainty legend, right of the title
    lx = MX + 10 + int(d.textlength(title, font=font(SANS_B, 11))) + 16
    for lab in ("CONFIRMED", "REPORTED", "CLAIM", "PENDING", "FORECAST"):
        col = BADGE[lab]
        d.ellipse([lx, by + 9, lx + 7, by + 16], fill=col)
        d.text((lx + 10, by + 6), lab, font=font(SANS, 8), fill=GREY)
        lx += 10 + int(d.textlength(lab, font=font(SANS, 8))) + 8
    f_item = font(SANS, 10)
    f_item_b = font(SANS_B, 10)
    col_w = (list_w - 20) // 2
    per_col = (len(also) + 1) // 2
    for ci in range(2):
        cx = MX + 10 + ci * col_w
        yy = by + 26
        for s in also[ci * per_col:(ci + 1) * per_col]:
            col = BADGE[s["certainty"]]
            d.ellipse([cx, yy + 3, cx + 7, yy + 10], fill=col)
            pre = f"{s['n']} {s['place']} — "
            pw = d.textlength(pre, font=f_item_b)
            d.text((cx + 11, yy), pre, font=f_item_b, fill=INK)
            rest = s["headline"]
            avail = col_w - 11 - pw - 4
            if d.textlength(rest, font=f_item) > avail:
                while rest and d.textlength(rest + "…", font=f_item) > avail:
                    rest = rest[:-1]
                rest += "…"
            d.text((cx + 11 + pw, yy), rest, font=f_item, fill=INK)
            yy += 11
    # map panel
    map_x = MX + list_w + 10
    map_w = W - MX - map_x
    d.rounded_rectangle([map_x, by, map_x + map_w, by + bh], radius=5,
                        fill=PAPER, outline=LINE, width=1)
    d.text((map_x + 10, by + 6), "WHERE IT HAPPENED — pins = story numbers",
           font=font(SANS_B, 11), fill=INK)
    draw_map(d, map_x + 8, by + 26, map_w - 16, bh - 34, stories)

    # --- date check ------------------------------------------------------------
    dy = by + bh + 8
    dh = 52
    d.rounded_rectangle([MX, dy, W - MX, dy + dh], radius=5,
                        fill=(255, 250, 230), outline=RED, width=2)
    d.rectangle([MX, dy, MX + 108, dy + dh], fill=RED)
    d.text((MX + 10, dy + 16), "DATE CHECK", font=font(SANS_B, 13),
           fill=(255, 255, 255))
    f_dc = font(SANS, 10)
    dc_lines = wrap(d, data["date_check"], f_dc, W - MX - 108 - 40)
    assert len(dc_lines) <= 3, f"date check wraps to {len(dc_lines)} lines"
    yy = dy + 5
    for ln in dc_lines[:3]:
        d.text((MX + 118, yy), ln, font=f_dc, fill=INK)
        yy += 12

    # --- footer ------------------------------------------------------------------
    fy = dy + dh + 6
    f_ft = font(SANS, 10)
    fl = data["sources_line"]
    while d.textlength(fl, font=f_ft) > W - 2 * MX and f_ft.size > 8:
        f_ft = font(SANS, f_ft.size - 1)
    d.text((MX, fy), fl, font=f_ft, fill=GREY)

    img.save(os.path.join(HERE, "entry.png"), optimize=True)
    data_bytes = open(os.path.join(HERE, "entry.png"), "rb").read()
    print(f"wrote entry.png {img.size} {len(data_bytes)} bytes "
          f"sha256={hashlib.sha256(data_bytes).hexdigest()[:16]} "
          f"stories={len(stories)} regions={len(regions)} "
          f"leads={len(leads)} mediums={len(mediums)} also={len(also)} "
          f"bottom_y={fy}")
    assert len(stories) == 38
    assert len(regions) == 9
    assert len(data_bytes) <= 1024 * 1024


if __name__ == "__main__":
    main()
