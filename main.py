#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Draws an open passport spread (1024x1024 PNG) for the invented
Republic of Caldera: a bilingual data page with portrait and a real
ICAO-style machine-readable zone, and a visas page whose stamps tell
one consistent travel history.  Python standard library only.
"""
import math
import os
import struct
import zlib

W = H = 1024


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, color):
        self.w = w
        self.h = h
        self.px = bytearray(color) * (w * h)

    def set(self, x, y, color, alpha=1.0):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            if alpha >= 1.0:
                self.px[i] = color[0]
                self.px[i + 1] = color[1]
                self.px[i + 2] = color[2]
            else:
                a = alpha
                self.px[i] = int(self.px[i] * (1 - a) + color[0] * a)
                self.px[i + 1] = int(self.px[i + 1] * (1 - a) + color[1] * a)
                self.px[i + 2] = int(self.px[i + 2] * (1 - a) + color[2] * a)

    def get(self, x, y):
        i = (y * self.w + x) * 3
        return self.px[i], self.px[i + 1], self.px[i + 2]


def save_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- drawing
def line(cv, x0, y0, x1, y1, color, width=1.0, alpha=1.0):
    """Thick line: stamp filled discs along the segment."""
    r = max(0.4, width / 2.0)
    dist = math.hypot(x1 - x0, y1 - y0)
    steps = max(1, int(dist / max(0.5, r * 0.6)))
    ri = int(math.ceil(r))
    for s in range(steps + 1):
        t = s / steps
        cx = x0 + (x1 - x0) * t
        cy = y0 + (y1 - y0) * t
        for dy in range(-ri, ri + 1):
            for dx in range(-ri, ri + 1):
                if dx * dx + dy * dy <= r * r + 0.3:
                    cv.set(int(cx + dx), int(cy + dy), color, alpha)


def polyline(cv, pts, color, width=1.0, alpha=1.0, close=False):
    seq = list(pts)
    if close and len(seq) > 2:
        seq = seq + [seq[0]]
    for i in range(len(seq) - 1):
        line(cv, seq[i][0], seq[i][1], seq[i + 1][0], seq[i + 1][1],
             color, width, alpha)


def fill_rect(cv, x, y, w, h, color, alpha=1.0):
    for yy in range(int(y), int(y + h)):
        for xx in range(int(x), int(x + w)):
            cv.set(xx, yy, color, alpha)


def rect_outline(cv, x, y, w, h, color, width=1.0, alpha=1.0):
    polyline(cv, [(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
             color, width, alpha, close=True)


def fill_circle(cv, cx, cy, r, color, alpha=1.0):
    ri = int(r)
    for dy in range(-ri, ri + 1):
        span = int(math.sqrt(max(0.0, r * r - dy * dy)))
        for dx in range(-span, span + 1):
            cv.set(int(cx + dx), int(cy + dy), color, alpha)


def circle_outline(cv, cx, cy, r, color, width=1.0, alpha=1.0):
    steps = max(24, int(2 * math.pi * r / 3))
    pts = [(cx + r * math.cos(2 * math.pi * i / steps),
            cy + r * math.sin(2 * math.pi * i / steps))
           for i in range(steps + 1)]
    polyline(cv, pts, color, width, alpha)


def fill_ellipse(cv, cx, cy, rx, ry, color, alpha=1.0):
    for dy in range(int(-ry), int(ry) + 1):
        t = dy / ry if ry else 0
        span = int(rx * math.sqrt(max(0.0, 1 - t * t)))
        for dx in range(-span, span + 1):
            cv.set(int(cx + dx), int(cy + dy), color, alpha)


def ellipse_outline(cv, cx, cy, rx, ry, color, width=1.0, alpha=1.0):
    steps = 64
    pts = [(cx + rx * math.cos(2 * math.pi * i / steps),
            cy + ry * math.sin(2 * math.pi * i / steps))
           for i in range(steps + 1)]
    polyline(cv, pts, color, width, alpha)


def fill_poly(cv, pts, color, alpha=1.0):
    ys = [p[1] for p in pts]
    y0, y1 = int(min(ys)), int(max(ys))
    n = len(pts)
    for yy in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            xa, ya = pts[i]
            xb, yb = pts[(i + 1) % n]
            if (ya <= yy < yb) or (yb <= yy < ya):
                xs.append(xa + (yy - ya) * (xb - xa) / (yb - ya))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            for xx in range(int(xs[i]), int(xs[i + 1]) + 1):
                cv.set(xx, yy, color, alpha)


def wave_band(cv, x0, x1, yc, amp, period, phase, color, alpha, width=1.0):
    pts = []
    x = x0
    while x <= x1:
        pts.append((x, yc + amp * math.sin((x - x0) / period * 2 * math.pi
                                            + phase)))
        x += 4
    polyline(cv, pts, color, width, alpha)


# deterministic hash noise tile (paper / desk grain)
def _tile():
    t = bytearray(256 * 256)
    seed = 1234567
    for i in range(256 * 256):
        seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
        t[i] = (seed >> 9) & 0xFF
    return t


TILE = _tile()


def grain(cv, x0, y0, x1, y1, amount):
    for yy in range(y0, y1):
        row = (yy & 255) * 256
        for xx in range(x0, x1):
            v = TILE[row + (xx & 255)] - 128
            if v:
                i = (yy * cv.w + xx) * 3
                d = int(v * amount)
                cv.px[i] = max(0, min(255, cv.px[i] + d))
                cv.px[i + 1] = max(0, min(255, cv.px[i + 1] + d))
                cv.px[i + 2] = max(0, min(255, cv.px[i + 2] + d))


# ---------------------------------------------------------------- font
# Stroke glyphs on an 8-wide, 10-tall grid (y down, 0 = cap top).
GLYPHS = {
    "A": [[(0, 10), (4, 0), (8, 10)], [(1.9, 6.4), (6.1, 6.4)]],
    "B": [[(0, 0), (0, 10)], [(0, 0), (4.8, 0), (6.6, 1.4), (6.6, 3.6),
                               (4.8, 5), (0, 5)],
          [(4.8, 5), (6.9, 6.2), (6.9, 8.6), (5.2, 10), (0, 10)]],
    "C": [[(7.6, 2.2), (5.2, 0.4), (2.6, 0.4), (0.6, 2.4), (0.6, 7.6),
           (2.6, 9.6), (5.2, 9.6), (7.6, 7.8)]],
    "D": [[(0, 0), (0, 10)], [(0, 0), (4.4, 0), (7, 2.6), (7, 7.4),
                              (4.4, 10), (0, 10)]],
    "E": [[(7, 0), (0, 0), (0, 10), (7, 10)], [(0, 5), (5.4, 5)]],
    "F": [[(7, 0), (0, 0), (0, 10)], [(0, 5), (5.4, 5)]],
    "G": [[(7.6, 2.2), (5.2, 0.4), (2.6, 0.4), (0.6, 2.4), (0.6, 7.6),
           (2.6, 9.6), (5.4, 9.6), (7.6, 7.6), (7.6, 5.6), (4.6, 5.6)]],
    "H": [[(0, 0), (0, 10)], [(8, 0), (8, 10)], [(0, 5), (8, 5)]],
    "I": [[(4, 0), (4, 10)], [(1.6, 0), (6.4, 0)], [(1.6, 10), (6.4, 10)]],
    "J": [[(7.4, 0), (7.4, 7.4), (6, 9.6), (3, 9.6), (1, 8.4)]],
    "K": [[(0, 0), (0, 10)], [(7.4, 0), (0.6, 5.4)], [(1.8, 4.4), (7.4, 10)]],
    "L": [[(0, 0), (0, 10), (7, 10)]],
    "M": [[(0, 10), (0, 0), (4, 6), (8, 0), (8, 10)]],
    "N": [[(0, 10), (0, 0), (8, 10), (8, 0)]],
    "O": [[(4, 0), (6.7, 0.8), (8, 3), (8, 7), (6.7, 9.2), (4, 10),
           (1.3, 9.2), (0, 7), (0, 3), (1.3, 0.8), (4, 0)]],
    "P": [[(0, 10), (0, 0), (5.4, 0), (7.2, 1.6), (7.2, 3.9), (5.4, 5.5),
           (0, 5.5)]],
    "Q": [[(4, 0), (6.7, 0.8), (8, 3), (8, 7), (6.7, 9.2), (4, 10),
           (1.3, 9.2), (0, 7), (0, 3), (1.3, 0.8), (4, 0)],
          [(5.2, 7.4), (8.2, 10.2)]],
    "R": [[(0, 10), (0, 0), (5.4, 0), (7.2, 1.6), (7.2, 3.9), (5.4, 5.5),
           (0, 5.5)], [(4.4, 5.5), (7.4, 10)]],
    "S": [[(7.2, 1.6), (5, 0.3), (2.4, 0.5), (0.8, 2), (1.1, 3.8), (3, 5),
           (5.4, 6), (6.9, 7.8), (6.1, 9.3), (3.4, 9.8), (1, 9.2),
           (0.3, 8.1)]],
    "T": [[(0, 0), (8, 0)], [(4, 0), (4, 10)]],
    "U": [[(0, 0), (0, 7.4), (1.5, 9.5), (4, 10), (6.5, 9.5), (8, 7.4),
           (8, 0)]],
    "V": [[(0, 0), (4, 10), (8, 0)]],
    "W": [[(0, 0), (1.8, 10), (4, 3.8), (6.2, 10), (8, 0)]],
    "X": [[(0, 0), (8, 10)], [(8, 0), (0, 10)]],
    "Y": [[(0, 0), (4, 4.6), (8, 0)], [(4, 4.6), (4, 10)]],
    "Z": [[(0, 0), (8, 0), (0, 10), (8, 10)]],
    "0": [[(4, 0), (6.4, 0.8), (7.4, 3), (7.4, 7), (6.4, 9.2), (4, 10),
           (1.6, 9.2), (0.6, 7), (0.6, 3), (1.6, 0.8), (4, 0)]],
    "1": [[(2.2, 2.4), (5, 0), (5, 10)], [(1.8, 10), (7, 10)]],
    "2": [[(0.8, 2.2), (2.2, 0.6), (5.2, 0.4), (6.8, 1.8), (6.2, 4.2),
           (0.8, 9.8), (7.2, 9.8)]],
    "3": [[(1, 1), (3, 0.3), (5.4, 0.5), (6.8, 2), (5.8, 4.2), (3.4, 5)],
          [(3.4, 5), (6, 5.4), (7, 7.4), (5.8, 9.5), (3, 9.8), (0.8, 8.8)]],
    "4": [[(5.4, 10), (5.4, 0), (0.6, 7.4)], [(0, 7.4), (8, 7.4)]],
    "5": [[(7, 0), (1.6, 0), (1.2, 4.2), (4.4, 3.8), (6.4, 5.2), (6.8, 7.8),
           (5.2, 9.6), (2.4, 9.8), (0.8, 8.8)]],
    "6": [[(6.4, 1.2), (4.4, 0.4), (2, 2), (0.8, 5), (1, 8), (2.8, 9.6),
           (5.2, 9.5), (6.8, 7.8), (6.4, 5.6), (4.8, 4.4), (2.6, 4.6),
           (1, 6.2)]],
    "7": [[(0.6, 0), (7.4, 0), (4, 10)]],
    "8": [[(4, 5), (2, 4.6), (1, 3), (1.8, 1), (4, 0.4), (6.2, 1), (7, 3),
           (6, 4.6), (4, 5)],
          [(4, 5), (6.2, 5.6), (7.2, 7.5), (6.2, 9.4), (4, 10), (1.8, 9.4),
           (0.8, 7.5), (1.8, 5.6), (4, 5)]],
    "9": [[(1.6, 8.8), (3.6, 9.6), (6, 8), (7.2, 5), (7, 2), (5.2, 0.5),
           (2.8, 0.6), (1.2, 2.2), (1.6, 4.4), (3.2, 5.6), (5.4, 5.4),
           (7, 4)]],
    " ": [],
    ".": [[(3.9, 9.4), (4.1, 9.9)]],
    ",": [[(4.6, 9.2), (3.8, 10.8)]],
    ":": [[(3.9, 2.2), (4.1, 2.7)], [(3.9, 7.6), (4.1, 8.1)]],
    "-": [[(1.6, 5), (6.4, 5)]],
    "/": [[(1.2, 10), (6.8, 0)]],
    "(": [[(6.2, 0.6), (3.6, 2.6), (3.6, 7.4), (6.2, 9.4)]],
    ")": [[(1.8, 0.6), (4.4, 2.6), (4.4, 7.4), (1.8, 9.4)]],
    "<": [[(7, 1), (1.2, 5), (7, 9)]],
    ">": [[(1, 1), (6.8, 5), (1, 9)]],
    "'": [[(4, 0), (4, 2.6)]],
    "+": [[(4, 2.4), (4, 7.6)], [(1.4, 5), (6.6, 5)]],
    "*": [[(4, 2), (4, 8)], [(1.8, 3.4), (6.2, 6.6)], [(6.2, 3.4), (1.8, 6.6)]],
}


def _rot(x, y, ang):
    c = math.cos(ang)
    s = math.sin(ang)
    return x * c - y * s, x * s + y * c


def text_width(s, h, sp=1.9):
    if not s:
        return 0.0
    adv = (8 + sp) * (h / 10.0)
    return adv * len(s) - sp * (h / 10.0)


def draw_text(cv, x, y, s, h, color, sp=1.9, align="l", ang=0.0,
              weight=None, alpha=1.0):
    """Draw caps stroke text. (x, y) is the cap-top anchor; ang rotates
    the whole string around that anchor (radians, clockwise)."""
    scale = h / 10.0
    adv = (8 + sp) * scale
    wtot = text_width(s, h, sp)
    if align == "c":
        x -= wtot / 2.0 * math.cos(ang)
        y -= wtot / 2.0 * math.sin(ang)
    elif align == "r":
        x -= wtot * math.cos(ang)
        y -= wtot * math.sin(ang)
    if weight is None:
        weight = max(0.8, h * 0.11)
    dx, dy = _rot(adv, 0, ang)
    for ch in s:
        glyph = GLYPHS.get(ch)
        if glyph:
            for stroke in glyph:
                pts = []
                for (gx, gy) in stroke:
                    px, py = _rot(gx * scale, gy * scale, ang)
                    pts.append((x + px, y + py))
                polyline(cv, pts, color, weight, alpha)
        x += dx
        y += dy
    return wtot


def draw_arc_text(cv, cx, cy, r, s, h, color, mid_ang, flip=False,
                  sp=1.9, weight=None, alpha=1.0):
    """Text along a circle. mid_ang = angle (deg, 0=east, clockwise) of
    the string's middle. flip=False: text on the top arc reading
    left-to-right; flip=True: bottom arc, letters upright."""
    scale = h / 10.0
    adv = (8 + sp) * scale
    step = adv / r  # radians per char
    total = step * (len(s) - 1)
    for i, ch in enumerate(s):
        if flip:
            a = math.radians(mid_ang) + total / 2.0 - i * step
            rot = a - math.pi / 2.0
        else:
            a = math.radians(mid_ang) - total / 2.0 + i * step
            rot = a + math.pi / 2.0
        px = cx + r * math.cos(a)
        py = cy + r * math.sin(a)
        glyph = GLYPHS.get(ch)
        if glyph:
            for stroke in glyph:
                pts = []
                for (gx, gy) in stroke:
                    lx, ly = (gx - 4) * scale, (gy - 5) * scale
                    rx, ry = _rot(lx, ly, rot)
                    pts.append((px + rx, py + ry))
                polyline(cv, pts, color,
                         weight if weight else max(0.8, h * 0.11), alpha)


# ---------------------------------------------------------------- emblem
def draw_star(cv, cx, cy, r, color, alpha=1.0, width=1.4):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    polyline(cv, pts, color, width, alpha, close=True)


def draw_emblem(cv, cx, cy, s, color, alpha=1.0, width=1.6):
    """Coat of arms of Caldera: shield, volcano, waves, star."""
    w2 = s * 0.5
    shield = [(cx - w2, cy - s * 0.55), (cx + w2, cy - s * 0.55),
              (cx + w2, cy + s * 0.12), (cx + w2 * 0.6, cy + s * 0.42),
              (cx, cy + s * 0.62), (cx - w2 * 0.6, cy + s * 0.42),
              (cx - w2, cy + s * 0.12)]
    polyline(cv, shield, color, width, alpha, close=True)
    # volcano with crater notch and plume
    vol = [(cx - s * 0.27, cy + s * 0.16), (cx - s * 0.07, cy - s * 0.26),
           (cx - s * 0.02, cy - s * 0.19), (cx + s * 0.03, cy - s * 0.26),
           (cx + s * 0.08, cy - s * 0.19), (cx + s * 0.27, cy + s * 0.16)]
    polyline(cv, vol, color, width * 0.9, alpha)
    wave_band(cv, cx - s * 0.3, cx + s * 0.3, cy + s * 0.3, s * 0.045,
              s * 0.3, 0.0, color, alpha, width * 0.9)
    wave_band(cv, cx - s * 0.3, cx + s * 0.3, cy + s * 0.43, s * 0.045,
              s * 0.3, 1.4, color, alpha, width * 0.9)
    draw_star(cv, cx, cy - s * 0.4, s * 0.09, color, alpha, width * 0.9)


# ---------------------------------------------------------------- portrait
def make_portrait(w, h):
    """A flat, faded passport-photo portrait on its own canvas."""
    cv = Canvas(w, h, (198, 208, 216))
    for yy in range(h):  # gentle vertical gradient
        t = yy / h
        c = (int(202 - 26 * t), int(212 - 26 * t), int(219 - 22 * t))
        for xx in range(0, w, 7):
            fill_rect(cv, xx, yy, 7, 1, c)
    skin = (199, 167, 141)
    skin_sh = (183, 150, 124)
    hair = (56, 44, 36)
    jacket = (43, 51, 71)
    cx = w * 0.5
    # shoulders / jacket
    fill_poly(cv, [(w * 0.06, h), (w * 0.15, h * 0.79), (w * 0.31, h * 0.685),
                   (w * 0.69, h * 0.685), (w * 0.85, h * 0.79), (w * 0.94, h)],
              jacket)
    # shirt V and tie
    fill_poly(cv, [(w * 0.385, h * 0.70), (w * 0.615, h * 0.70),
                   (cx, h * 0.94)], (226, 224, 218))
    fill_poly(cv, [(cx - w * 0.035, h * 0.735), (cx + w * 0.035, h * 0.735),
                   (cx, h * 0.90)], (96, 34, 40))
    # neck
    fill_rect(cv, cx - w * 0.085, h * 0.55, w * 0.17, h * 0.16, skin_sh)
    # ears and head
    fill_ellipse(cv, cx - w * 0.205, h * 0.375, w * 0.035, h * 0.05, skin)
    fill_ellipse(cv, cx + w * 0.205, h * 0.375, w * 0.035, h * 0.05, skin)
    fill_ellipse(cv, cx, h * 0.36, w * 0.205, h * 0.265, skin)
    # hair: cap plus sides
    fill_ellipse(cv, cx, h * 0.185, w * 0.21, h * 0.145, hair)
    fill_rect(cv, cx - w * 0.215, h * 0.16, w * 0.045, h * 0.17, hair)
    fill_rect(cv, cx + w * 0.17, h * 0.16, w * 0.045, h * 0.17, hair)
    fill_ellipse(cv, cx, h * 0.235, w * 0.185, h * 0.1, skin)
    feat = (74, 60, 48)
    # brows and eyes
    line(cv, cx - w * 0.135, h * 0.335, cx - w * 0.045, h * 0.33, feat, 1.6, 0.75)
    line(cv, cx + w * 0.045, h * 0.33, cx + w * 0.135, h * 0.335, feat, 1.6, 0.75)
    line(cv, cx - w * 0.125, h * 0.375, cx - w * 0.055, h * 0.375, feat, 1.5, 0.8)
    line(cv, cx + w * 0.055, h * 0.375, cx + w * 0.125, h * 0.375, feat, 1.5, 0.8)
    fill_circle(cv, cx - w * 0.09, h * 0.378, 1.8, feat, 0.8)
    fill_circle(cv, cx + w * 0.09, h * 0.378, 1.8, feat, 0.8)
    # nose and mouth
    line(cv, cx, h * 0.385, cx - w * 0.012, h * 0.465, feat, 1.3, 0.55)
    line(cv, cx - w * 0.012, h * 0.465, cx + w * 0.03, h * 0.468, feat, 1.3, 0.55)
    line(cv, cx - w * 0.055, h * 0.545, cx + w * 0.055, h * 0.545, (120, 74, 66),
         1.6, 0.8)
    # faint print lines over the photo
    for yy in range(4, h, 6):
        line(cv, 0, yy, w, yy, (90, 100, 110), 0.7, 0.05)
    return cv


def blit(dst, src, x, y, alpha=1.0):
    for yy in range(src.h):
        for xx in range(src.w):
            c = src.get(xx, yy)
            dst.set(x + xx, y + yy, c, alpha)


# ---------------------------------------------------------------- MRZ
def _cd(s):
    vals = {str(d): d for d in range(10)}
    for i in range(26):
        vals[chr(65 + i)] = 10 + i
    vals["<"] = 0
    total = 0
    for i, ch in enumerate(s):
        total += vals[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def build_mrz():
    line1 = "P<CDR" + "ROCHA<<TOMAS<AURELIO"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "C0477215<"
    doc += _cd(doc)
    dob = "880202"
    dob += _cd(dob)
    exp = "310314"
    exp += _cd(exp)
    personal = "<" * 14
    personal += _cd(personal)
    composite = _cd(doc + dob + exp + personal)
    line2 = doc + "CDR" + dob + "M" + exp + personal + composite
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    return line1, line2


# ---------------------------------------------------------------- stamps
INK = 0.84


def _rp(cx, cy, ang, lx, ly):
    rx, ry = _rot(lx, ly, ang)
    return cx + rx, cy + ry


def stamp_text(cv, cx, cy, ang, dy, s, h, color, sp=1.9, alpha=INK,
               weight=None):
    px, py = _rp(cx, cy, ang, 0, dy)
    ax = px + math.sin(ang) * h / 2.0
    ay = py - math.cos(ang) * h / 2.0
    draw_text(cv, ax, ay, s, h, color, sp=sp, align="c", ang=ang,
              weight=weight, alpha=alpha)


def stamp_line(cv, cx, cy, ang, x0, x1, dy, color, width=1.2, alpha=INK):
    ax, ay = _rp(cx, cy, ang, x0, dy)
    bx, by = _rp(cx, cy, ang, x1, dy)
    line(cv, ax, ay, bx, by, color, width, alpha)


def round_stamp(cv, cx, cy, r, color, top, bottom, lines, ang_deg,
                symbol=None):
    ang = math.radians(ang_deg)
    circle_outline(cv, cx, cy, r, color, 2.2, INK)
    circle_outline(cv, cx, cy, r - 5, color, 0.9, INK)
    draw_arc_text(cv, cx, cy, r - 15, top, r * 0.128, color, -90 + ang_deg,
                  sp=1.1, alpha=INK)
    if bottom:
        draw_arc_text(cv, cx, cy, r - 15, bottom, r * 0.115, color,
                      90 + ang_deg, flip=True, sp=1.1, alpha=INK)
    for (lx, ly) in [(-(r - 15), 0), (r - 15, 0)]:
        px, py = _rp(cx, cy, ang, lx, ly)
        fill_circle(cv, px, py, 2.0, color, INK)
    if symbol == "anchor":
        sc = r / 74.0
        pts = [(0, -r * 0.52)]
        px, py = _rp(cx, cy, ang, 0, -r * 0.40)
        circle_outline(cv, px, py, 3.4 * sc, color, 1.4, INK)
        a = _rp(cx, cy, ang, 0, -r * 0.36)
        b = _rp(cx, cy, ang, 0, -r * 0.13)
        line(cv, a[0], a[1], b[0], b[1], color, 1.6, INK)
        a = _rp(cx, cy, ang, -6 * sc, -r * 0.30)
        b = _rp(cx, cy, ang, 6 * sc, -r * 0.30)
        line(cv, a[0], a[1], b[0], b[1], color, 1.6, INK)
        for sgn in (-1, 1):
            a = _rp(cx, cy, ang, sgn * 8 * sc, -r * 0.22)
            b = _rp(cx, cy, ang, sgn * 8 * sc, -r * 0.13)
            c = _rp(cx, cy, ang, sgn * 2 * sc, -r * 0.16)
            line(cv, a[0], a[1], b[0], b[1], color, 1.6, INK)
            line(cv, b[0], b[1], c[0], c[1], color, 1.6, INK)
    for (txt, dy, hh, sp) in lines:
        stamp_text(cv, cx, cy, ang, dy, txt, hh, color, sp=sp)


def rect_stamp(cv, cx, cy, w, h, color, lines, ang_deg, double=True,
               fill=None):
    ang = math.radians(ang_deg)
    corners = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2),
               (-w / 2, h / 2)]
    world = [_rp(cx, cy, ang, lx, ly) for (lx, ly) in corners]
    if fill is not None:
        fill_poly(cv, world, fill, 1.0)
    polyline(cv, world, color, 2.0, INK, close=True)
    if double:
        k = (w - 9) / w
        inner = [_rp(cx, cy, ang, lx * k, ly * (h - 9) / h)
                 for (lx, ly) in corners]
        polyline(cv, inner, color, 0.9, INK, close=True)
    for (txt, dy, hh, sp) in lines:
        stamp_text(cv, cx, cy, ang, dy, txt, hh, color, sp=sp)


# ---------------------------------------------------------------- scene
BLUE = (36, 74, 142)
VIOLET = (104, 60, 138)
TEAL = (14, 106, 100)
RED = (148, 42, 42)
GREEN = (32, 106, 62)
MAGENTA = (166, 30, 94)
INKD = (30, 32, 40)
LABEL = (94, 102, 112)
NAVY = (22, 44, 92)


def field(cv, x, y, label, value, vsize=14.5, vcolor=INKD, lw=None):
    draw_text(cv, x, y, label, 8, LABEL, sp=1.6)
    draw_text(cv, x, y + 11, value, vsize, vcolor,
              weight=max(1.0, vsize * 0.13))


def page_base(cv, x0):
    for i in range(9):
        yy = 96 + i * 96
        wave_band(cv, x0 + 14, x0 + 458, yy, 7, 118, i * 0.9,
                  (188, 208, 200), 0.30, 0.9)
        wave_band(cv, x0 + 14, x0 + 458, yy + 13, 7, 131, i * 0.7 + 2.0,
                  (196, 204, 220), 0.26, 0.9)
    draw_emblem(cv, x0 + 236, 512, 300, (110, 132, 148), 0.04, 2.4)
    rect_outline(cv, x0 + 12, 76, 448, 872, (172, 162, 142), 1.0, 0.55)


def draw(cv):
    # desk
    fill_rect(cv, 0, 0, W, H, (59, 52, 47))
    grain(cv, 0, 0, W, H, 0.03)
    # booklet shadow and pages
    fill_rect(cv, 54, 78, 944, 896, (24, 20, 18), 0.5)
    fill_rect(cv, 48, 70, 944, 896, (30, 26, 23), 0.35)
    fill_rect(cv, 40, 64, 472, 896, (246, 241, 228))
    fill_rect(cv, 512, 64, 472, 896, (244, 239, 225))
    grain(cv, 40, 64, 984, 960, 0.018)
    page_base(cv, 40)
    page_base(cv, 512)
    # spine gutter and stitching
    for xx in range(484, 541):
        a = 0.30 * (1 - abs(xx - 512) / 28.0)
        if a > 0:
            fill_rect(cv, xx, 64, 1, 896, (96, 84, 70), a)
    yy = 82
    while yy < 946:
        line(cv, 512, yy, 512, yy + 9, (122, 106, 88), 2.0, 0.6)
        yy += 18

    # ---------------- data page (left)
    draw_emblem(cv, 276, 116, 62, NAVY, 0.92, 2.0)
    draw_text(cv, 276, 158, "REPUBLICA DA CALDEIRA", 19, NAVY, sp=2.2,
              align="c", weight=2.4)
    draw_text(cv, 276, 184, "REPUBLIC OF CALDERA", 10, LABEL, sp=3.6,
              align="c")
    draw_text(cv, 276, 208, "PASSAPORTE", 14.5, NAVY, sp=5.2, align="c",
              weight=1.9)
    line(cv, 66, 234, 486, 234, NAVY, 1.6, 0.9)
    draw_text(cv, 276, 242, "DOCUMENTO DE VIAGEM - TRAVEL DOCUMENT", 7.2,
              LABEL, sp=1.6, align="c")

    # ghost image behind the fields
    ghost = make_portrait(84, 106)
    blit(cv, ghost, 394, 452, 0.09)

    # photo
    photo = make_portrait(150, 190)
    blit(cv, photo, 66, 282)
    rect_outline(cv, 66, 282, 150, 190, (110, 112, 116), 1.4, 0.9)
    for (cc, rr) in [((214, 44, 40), 17), ((44, 120, 60), 13),
                     ((40, 70, 160), 9.5)]:
        circle_outline(cv, 196, 300, rr, cc, 1.1, 0.28)

    fx = 234
    field(cv, fx, 282, "TIPO", "P", 13.5)
    field(cv, 282, 282, "CODIGO", "CDR", 13.5)
    field(cv, 352, 282, "PASSAPORTE NO.", "C0477215", 13, (140, 26, 26))
    field(cv, fx, 332, "APELIDO / SURNAME", "ROCHA", 16.5)
    field(cv, fx, 384, "NOMES / GIVEN NAMES", "TOMAS AURELIO", 15)
    field(cv, fx, 436, "NACIONALIDADE / NATIONALITY", "CALDERAN", 14.5)
    field(cv, fx, 486, "NASCIMENTO / DATE OF BIRTH", "02 FEB 1988",
          12.5)
    field(cv, 404, 486, "SEXO / SEX", "M", 12.5)
    field(cv, fx, 538, "NATURALIDADE / PLACE OF BIRTH", "PORTO CALDEIRA",
          13.5)
    field(cv, fx, 588, "EMISSAO / DATE OF ISSUE", "14 MAR 2021", 11.2)
    field(cv, 362, 588, "VALIDADE / EXPIRY", "14 MAR 2031", 11.2)
    draw_text(cv, fx, 640, "AUTORIDADE / AUTHORITY", 8, LABEL, sp=1.6)
    draw_text(cv, fx, 651, "MINISTRY OF THE INTERIOR", 10.5, INKD,
              sp=1.5, weight=1.4)
    draw_text(cv, fx, 692, "ASSINATURA DO TITULAR / HOLDER'S SIGNATURE",
              7.2, LABEL, sp=1.4)
    sig = [(238 + i * 3.1, 714 + 8 * math.sin(i * 0.5) * math.sin(i / 51.0
           * math.pi) - i * 0.1) for i in range(52)]
    polyline(cv, sig, (24, 40, 110), 1.7, 0.9)
    line(cv, 238, 726, 272, 704, (24, 40, 110), 1.5, 0.85)
    line(cv, 300, 720, 340, 712, (24, 40, 110), 1.3, 0.7)

    draw_emblem(cv, 276, 786, 44, NAVY, 0.4, 1.4)
    draw_text(cv, 276, 822, "ESTE PASSAPORTE CONTEM 32 PAGINAS", 7.2,
              LABEL, sp=1.6, align="c")
    draw_text(cv, 276, 834, "THIS PASSPORT CONTAINS 32 PAGES", 7.2,
              LABEL, sp=1.6, align="c")

    # MRZ
    l1, l2 = build_mrz()
    draw_text(cv, 73, 878, l1, 11, (24, 24, 26), sp=0.55, weight=1.3)
    draw_text(cv, 73, 904, l2, 11, (24, 24, 26), sp=0.55, weight=1.3)

    # laminate sheen over the data page
    fill_poly(cv, [(150, 64), (300, 64), (120, 960), (40, 960),
                   (40, 700)], (255, 255, 255), 0.045)

    # ---------------- visas page (right)
    draw_text(cv, 748, 88, "VISTOS", 13, NAVY, sp=3.4, align="c",
              weight=1.8)
    draw_text(cv, 748, 108, "VISAS", 8.5, LABEL, sp=3.4, align="c")
    draw_text(cv, 946, 88, "7", 11, LABEL, align="r")
    line(cv, 538, 128, 958, 128, NAVY, 1.2, 0.7)

    # printed notice: the telling detail
    rect_outline(cv, 548, 142, 400, 98, (58, 62, 68), 1.6, 0.9)
    rect_outline(cv, 552, 146, 392, 90, (58, 62, 68), 0.8, 0.9)
    draw_text(cv, 748, 154, "NOTICE TO THE BEARER", 9.5, (40, 44, 52),
              sp=2.4, align="c", weight=1.3)
    notice = ["IN THE EVENT OF ERUPTION THIS DOCUMENT",
              "ENTITLES THE BEARER TO PASSAGE ON ANY",
              "VESSEL LEAVING CALDERA, AND TO LANDING",
              "IN SANTA IRIA OR ONDINE WITHOUT VISA."]
    for i, ln in enumerate(notice):
        draw_text(cv, 748, 176 + i * 15, ln, 8.6, (52, 56, 64), sp=1.5,
                  align="c")

    # geothermal levy fee stamp, paid on the day of issue
    rect_stamp(cv, 870, 272, 178, 84, MAGENTA,
               [("GEOTHERMAL LEVY", -26, 10.5, 1.6), ("PAID", -6, 14, 2.6),
                ("PORTO CALDEIRA", 14, 7.6, 1.4),
                ("14 MAR 2021", 26, 7.6, 1.4)], -4)

    # Ondine visa sticker
    rect_stamp(cv, 652, 332, 254, 148, TEAL,
               [("REPUBLIC OF ONDINE", -56, 11.5, 1.8),
                ("VISITOR VISA", -30, 12, 2.2),
                ("MULTIPLE ENTRY - 30 DAYS", -6, 8.2, 1.4),
                ("ISSUED 20 OCT 2024", 10, 8.2, 1.4),
                ("PORT SEREIN - NO. V-88113", 26, 8.2, 1.4),
                ("ROCHA / TOMAS AURELIO", 48, 8.2, 1.4)], -3,
               fill=(238, 245, 241))
    rect_stamp(cv, 726, 442, 172, 76, TEAL,
               [("PORT SEREIN", -20, 9.5, 1.8), ("ENTERED", -2, 10.5, 2.2),
                ("28 OCT 2024", 16, 9.5, 1.6)], 2, double=False)

    # travel history in stamps
    round_stamp(cv, 884, 450, 72, BLUE, "REPUBLICA DA CALDEIRA",
                "PORTO CALDEIRA",
                [("SAIDA", -6, 11, 2.4), ("DEPARTURE", 8, 7.6, 1.8),
                 ("03 JUN 2023", 24, 12, 1.6)], 5, symbol="anchor")
    round_stamp(cv, 636, 572, 76, VIOLET, "SANTA IRIA", "PORTO DAS FLORES",
                [("ENTRADA", -16, 11, 2.2), ("ARRIVAL", -2, 7.6, 1.8),
                 ("03 JUN 2023", 14, 12, 1.6)], -7)
    round_stamp(cv, 866, 622, 69, VIOLET, "SANTA IRIA", "PORTO DAS FLORES",
                [("SAIDA", -15, 10.5, 2.2), ("DEPARTURE", -2, 7.2, 1.6),
                 ("17 JUN 2023", 13, 11.5, 1.5)], 3)
    round_stamp(cv, 640, 758, 69, BLUE, "REPUBLICA DA CALDEIRA",
                "PORTO CALDEIRA",
                [("ENTRADA", -15, 10.5, 2.0), ("ARRIVAL", -2, 7.2, 1.6),
                 ("17 JUN 2023", 13, 11.5, 1.5)], -4)
    rect_stamp(cv, 858, 788, 188, 88, RED,
               [("PORT SEREIN", -24, 10, 2.0), ("DEPARTURE", -4, 11, 2.2),
                ("02 NOV 2024", 14, 10, 1.6)], -2)
    round_stamp(cv, 866, 890, 58, GREEN, "THE MARROW ISLANDS",
                "KINGSTON ROADS",
                [("ARRIVAL", -13, 9.5, 1.8), ("11 APR 2025", 2, 10.5, 1.4)],
                6)
    rect_stamp(cv, 646, 884, 178, 76, GREEN,
               [("KINGSTON ROADS", -20, 9, 1.6), ("DEPARTURE", -2, 10, 2.0),
                ("19 APR 2025", 16, 9.5, 1.5)], -5, double=False)

    # vignette
    for yy in range(H):
        dy = (yy - 512) / 512.0
        for xx in range(W):
            dx = (xx - 512) / 512.0
            d = dx * dx + dy * dy
            if d > 0.55:
                f = 1.0 - min(0.30, (d - 0.55) * 0.38)
                i = (yy * W + xx) * 3
                cv.px[i] = int(cv.px[i] * f)
                cv.px[i + 1] = int(cv.px[i + 1] * f)
                cv.px[i + 2] = int(cv.px[i + 2] * f)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv = Canvas(W, H, (0, 0, 0))
    draw(cv)
    path = os.path.join(outdir, "entry.png")
    save_png(cv, path)
    print("wrote", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
