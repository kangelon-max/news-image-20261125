#!/usr/bin/env python3
"""THE WORLD IN ONE DAY - Wednesday 25 November 2026.

Draws the one-image summary of the day's world news as a premium editorial
poster with PIL: a masthead, a hero scene for the Huang reversal market rout,
four major-story panels with drawn motifs, a briefs section and the markets
ticker. Renders at 2048x2048 and downscales to the judged entry.png at
1024x1024. Fully deterministic: fixed constants and fixed seeds only, and the
PNG is saved with no time metadata.
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- palette
PAPER = (245, 239, 226)
CREAM = (251, 247, 236)
NAVY = (13, 27, 46)
NAVY_2 = (21, 40, 66)
INK = (30, 32, 36)
SOFT = (74, 72, 64)
RED = (192, 57, 43)
RED_L = (219, 82, 62)
GOLD = (201, 162, 39)
GOLD_L = (236, 201, 94)
SEA = (36, 72, 94)
LAND = (74, 84, 58)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

W = 2048
MX = 48                      # side margin
CW = W - 2 * MX              # content width = 1952
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")


def F(path, size):
    return ImageFont.truetype(path, size)


def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return b[2] - b[0]


def fit(d, s, path, start, maxw, floor=10):
    """Largest font (<= start) whose rendered width fits maxw."""
    size = start
    while size > floor:
        f = F(path, size)
        if tw(d, s, f) <= maxw:
            return f, size
        size -= 2
    return F(path, floor), floor


def wrap(d, s, f, maxw):
    """Greedy word wrap; returns the list of lines."""
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if tw(d, trial, f) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_wrap(d, s, path, start, maxw, max_lines, floor=10):
    """Largest font (<= start) whose wrap of s fits max_lines lines."""
    size = start
    while size > floor:
        f = F(path, size)
        lines = wrap(d, s, f, maxw)
        if len(lines) <= max_lines:
            return f, size, lines
        size -= 2
    f = F(path, floor)
    return f, floor, wrap(d, s, f, maxw)


def text(d, x, y, s, f, color):
    d.text((x, y), s, font=f, fill=color)


def rtext(d, xr, y, s, f, color):
    d.text((xr - tw(d, s, f), y), s, font=f, fill=color)


# ---------------------------------------------------------------- masthead
def globe(d, cx, cy, r, color, width=4):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=width)
    for frac in (0.45, 0.8):
        w2 = r * frac
        d.ellipse([cx - w2, cy - r, cx + w2, cy + r], outline=color, width=3)
    d.line([cx - r, cy, cx + r, cy], fill=color, width=3)
    for off in (-0.48, 0.48):
        oy = cy + off * r
        half = math.sqrt(max(r * r - (off * r) ** 2, 1))
        d.line([cx - half, oy, cx + half, oy], fill=color, width=3)


def masthead(d):
    top, bot = 40, 224
    d.rectangle([MX, top, W - MX, bot], fill=NAVY)
    d.rectangle([MX + 6, top + 6, W - MX - 6, bot - 6], outline=GOLD, width=3)
    d.rectangle([MX + 15, top + 15, W - MX - 15, bot - 15], outline=GOLD, width=2)
    cy = (top + bot) // 2 - 14
    globe(d, MX + 108, cy, 58, GOLD)
    globe(d, W - MX - 108, cy, 58, GOLD)
    title = "THE WORLD IN ONE DAY"
    f, _ = fit(d, title, SERIF_B, 118, CW - 2 * 190)
    text(d, (W - tw(d, title, f)) // 2, top + 26, title, f, PAPER)
    dl = "WEDNESDAY · 25 NOVEMBER 2026"
    fd = F(SANS_B, 37)
    text(d, MX + 190, bot - 58, dl, fd, GOLD_L)
    rtext(d, W - MX - 190, bot - 58, "One image, the whole planet",
          F(SANS, 37), (232, 228, 212))


# ---------------------------------------------------------------- hero scene
def skyline(d, rng, baseline, color, hmin, hmax, windows=None,
            win_p=0.13, win_col=(238, 203, 110)):
    x = MX - 10
    while x < W - MX + 10:
        bw = rng.randint(58, 128)
        bh = rng.randint(hmin, hmax)
        d.rectangle([x, baseline - bh, x + bw, baseline], fill=color)
        if rng.random() < 0.35:
            d.rectangle([x + bw * 0.3, baseline - bh - 14, x + bw * 0.7,
                         baseline - bh], fill=color)
        if windows is not None:
            wy = baseline - bh + 14
            while wy < baseline - 16:
                wx = x + 10
                while wx < x + bw - 12:
                    if rng.random() < win_p:
                        d.rectangle([wx, wy, wx + 8, wy + 11],
                                    fill=win_col)
                    wx += 20
                wy += 24
        x += bw + rng.randint(4, 18)


def candlesticks(d):
    x0, y0, x1, y1 = 1566, 254, 1956, 354
    grid = (56, 78, 106)
    for i in range(4):
        gy = y0 + i * (y1 - y0) // 3
        d.line([x0, gy, x1, gy], fill=grid, width=2)
    for i in range(5):
        gx = x0 + i * (x1 - x0) // 4
        d.line([gx, y0, gx, y1], fill=grid, width=2)
    candles = [  # (open, close) in box-relative units, green up / red down
        (0.42, 0.30), (0.30, 0.36), (0.36, 0.22), (0.22, 0.30),
        (0.30, 0.44), (0.44, 0.40), (0.40, 0.58), (0.58, 0.74),
    ]
    cw_ = (x1 - x0) // len(candles)
    for i, (o, c) in enumerate(candles):
        cx = x0 + i * cw_ + cw_ // 2
        yo, yc = y0 + o * (y1 - y0), y0 + c * (y1 - y0)
        col = (58, 172, 100) if c < o else (206, 64, 46)
        hi = min(yo, yc) - 12
        lo = max(yo, yc) + 12
        d.line([cx, hi, cx, lo], fill=col, width=4)
        d.rectangle([cx - 13, min(yo, yc), cx + 13, max(yo, yc)], fill=col)


def arrow_shard(d, cx, cy, length, ang_deg, wdt):
    """One clean gold arrow tumbling along the plunge path."""
    a = math.radians(ang_deg)
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx
    hl = length * 0.42                       # head length
    hw = wdt * 1.5                           # head half-width
    tx, ty = cx - dx * length / 2, cy - dy * length / 2    # tail centre
    bx, by = cx + dx * (length / 2 - hl), cy + dy * (length / 2 - hl)
    tipx, tipy = cx + dx * length / 2, cy + dy * length / 2
    d.polygon([(tx + px * wdt / 2, ty + py * wdt / 2),
               (bx + px * hw, by + py * hw),
               (tipx, tipy),
               (bx - px * hw, by - py * hw),
               (tx - px * wdt / 2, ty - py * wdt / 2)],
              fill=(226, 182, 66), outline=(146, 110, 30), width=3)


def fracture(d, peak):
    """The rally line visibly cracks at the peak: a jagged split bridging
    the gap between the broken line ends, radiating crack branches and a
    bright fracture flash."""
    px_, py_ = peak
    pale = (243, 224, 164)
    bright = (255, 248, 220)
    # radiating crack branches (jagged polylines out of the break)
    branches = [
        [(px_, py_), (px_ - 24, py_ - 12), (px_ - 30, py_ - 28),
         (px_ - 52, py_ - 34)],
        [(px_, py_), (px_ + 6, py_ - 22), (px_ + 2, py_ - 34),
         (px_ + 14, py_ - 40)],
        [(px_, py_), (px_ + 32, py_ - 8), (px_ + 58, py_ - 18),
         (px_ + 84, py_ - 12)],
        [(px_, py_), (px_ - 28, py_ + 16), (px_ - 48, py_ + 36)],
        [(px_, py_), (px_ + 24, py_ + 24), (px_ + 28, py_ + 48),
         (px_ + 48, py_ + 62)],
    ]
    for br in branches:
        d.line(br, fill=pale, width=4, joint="curve")
    # the jagged split itself, bridging the gap between the line ends
    d.line([(px_ - 16, py_ + 7), (px_ - 6, py_ - 4), (px_ + 2, py_ + 6),
            (px_ + 10, py_ - 5), (px_ + 18, py_ - 6)],
           fill=bright, width=5, joint="curve")
    # fracture flash: starburst + hot core
    for ang in range(0, 360, 45):
        a = math.radians(ang + 12)
        r1 = 26 if ang % 90 == 0 else 17
        d.line([px_, py_, px_ + r1 * math.cos(a), py_ + r1 * math.sin(a)],
               fill=bright, width=4)
    d.ellipse([px_ - 17, py_ - 17, px_ + 17, py_ + 17],
              fill=(250, 222, 132))
    d.ellipse([px_ - 9, py_ - 9, px_ + 9, py_ + 9], fill=bright)


def candle_shard(d, cx, cy, hgt, col):
    """One small candlestick tumbling under the break point."""
    d.line([cx, cy - hgt // 2 - 8, cx, cy + hgt // 2 + 8], fill=col,
           width=3)
    d.rectangle([cx - 6, cy - hgt // 2, cx + 6, cy + hgt // 2], fill=col)


def hero_scene(d, img):
    top, bot = 236, 480
    # night-sky gradient
    c_top, c_bot = (9, 18, 34), (25, 45, 74)
    for i in range(bot - top):
        t = i / (bot - top)
        col = tuple(int(c_top[k] + (c_bot[k] - c_top[k]) * t)
                    for k in range(3))
        d.line([MX, top + i, W - MX, top + i], fill=col)
    # the chart line's path (the glow below is laid along it)
    rise = [(96, 444), (330, 428), (560, 384), (800, 330), (980, 294),
            (1138, 287)]
    fall = [(1168, 274), (1300, 318), (1470, 372), (1650, 430),
            (1830, 462), (1976, 478)]
    # soft glows: a halo running the length of the gold rally line and
    # of the red plunge, plus pools of light at the peak and the crash
    glow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(rise, fill=(240, 190, 80, 46), width=54, joint="curve")
    gd.line(fall, fill=(205, 62, 40, 42), width=48, joint="curve")
    gd.ellipse([1002, 196, 1302, 386], fill=(240, 190, 80, 46))
    gd.ellipse([1620, 360, 2006, 540], fill=(205, 62, 40, 58))
    glow = glow.filter(ImageFilter.GaussianBlur(26))
    img.paste(glow, (0, 0), glow)
    d = ImageDraw.Draw(img)  # fresh draw core after compositing
    # stars
    rng = random.Random(20261125)
    for _ in range(240):
        sx = rng.randint(MX + 8, W - MX - 8)
        sy = rng.randint(top + 8, top + 150)
        r = rng.choice((1, 2, 2, 3))
        shade = rng.choice(((210, 218, 232), (238, 226, 190),
                            (170, 184, 205)))
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=shade)
    # skyline, two layers: a dim distant row with sparse lit windows,
    # then the near-black row with brighter windows in front of it
    skyline(d, random.Random(41), bot, (17, 30, 50), 40, 88,
            windows=True, win_p=0.07, win_col=(190, 164, 92))
    skyline(d, random.Random(97), bot, (7, 12, 22), 62, 126,
            windows=True, win_p=0.17)
    candlesticks(d)
    # the chart line: gold rocket, red plunge — the two ends stop short
    # of the peak, leaving a visible gap for the fracture
    for pts, halo, mid, core in (
            (rise, (94, 72, 20), (172, 134, 42), (243, 203, 84)),
            (fall, (96, 24, 18), (156, 42, 30), (235, 88, 62))):
        for width, col in ((30, halo), (17, mid), (8, core)):
            d.line(pts, fill=col, width=width, joint="curve")
        for px, py in pts:
            d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=core)
    # the break: fracture flash and crack at the peak, then clean gold
    # arrow-shards tumbling down along the red plunge path
    fracture(d, (1152, 280))
    arrow_shard(d, 1345, 380, 74, 42, 16)
    arrow_shard(d, 1545, 442, 64, 8, 15)
    arrow_shard(d, 1730, 458, 52, 55, 13)
    # red candle shards and falling ticks shaken loose by the break,
    # tumbling away beneath the plunge path
    for cx, cy, hgt, col in ((1246, 322, 26, RED), (1318, 350, 18, RED_L),
                             (1408, 384, 28, RED), (1496, 408, 18, RED_L),
                             (1592, 428, 22, RED), (1792, 466, 16, RED_L)):
        candle_shard(d, cx, cy, hgt, col)
    for tx, ty, ln in ((1280, 306, 16), (1450, 366, 13), (1552, 402, 15),
                       (1680, 440, 12), (1852, 452, 14)):
        d.line([tx, ty, tx + ln, ty + ln + 5], fill=(222, 84, 52),
               width=4)
    # embers and falling fragments under the plunge
    rng = random.Random(7)
    for _ in range(46):
        ex = rng.randint(1240, 1985)
        ey = rng.randint(360, 478)
        r = rng.randint(2, 6)
        col = rng.choice(((238, 140, 60), (222, 84, 52), (243, 190, 92),
                          (178, 60, 44)))
        d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=col)
    for fx, fy, s in ((1400, 392, 10), (1560, 428, 8), (1620, 452, 9)):
        d.polygon([(fx, fy - s), (fx + s, fy + s), (fx - s, fy + s)],
                  fill=(150, 48, 38))


# ---------------------------------------------------------------- hero strip
def hero_strip(d):
    top, bot = 480, 724
    d.rectangle([MX, top, W - MX, bot], fill=NAVY)
    x = MX + 40
    wmax = CW - 80
    y = top + 10
    d.rectangle([x, y + 4, x + 15, y + 30], fill=RED_L)
    text(d, x + 26, y, "TOP STORY · WALL STREET", F(SANS_B, 33), RED_L)
    y += 40
    head = "THE HUANG REVERSAL"
    f, hs = fit(d, head, SERIF_B, 94, wmax)
    text(d, x, y, head, f, PAPER)
    y += hs + 8
    d.rectangle([x, y, x + 300, y + 4], fill=GOLD)
    y += 10
    sub1 = ("Nvidia plunges ~7% as the comeback rally collapses — "
            "lawmakers demand answers on Trump's role")
    f1, _ = fit(d, sub1, SANS, 35, wmax)
    text(d, x, y, sub1, f1, (238, 233, 218))
    y += 38
    sub2 = ("Huang to testify before the Senate on Dec 3 · Nikkei −2.8% · "
            "South Korean stocks −6%")
    f2, _ = fit(d, sub2, SANS_B, 34, wmax)
    text(d, x, y, sub2, f2, GOLD_L)
    assert y + 38 <= bot, "hero strip overflow"


# ---------------------------------------------------------------- motifs
def waves(d, x, y, w, col, step=30, amp=6):
    """A row of scalloped wave crests."""
    n = max(int(w // step), 1)
    for i in range(n):
        wx = x + i * step
        d.arc([wx, y - amp, wx + step, y + amp], 180, 360, fill=col,
              width=3)


def motif_hormuz(d, x, y, w, h):
    sea_y = y + h - 30
    d.rectangle([x, sea_y, x + w, y + h], fill=SEA)
    d.polygon([(x, y + h), (x, sea_y - 24), (x + 62, sea_y + 4),
               (x + 92, y + h)], fill=LAND)
    d.polygon([(x + w, y + h), (x + w, sea_y - 28), (x + w - 58, sea_y + 2),
               (x + w - 88, y + h)], fill=LAND)
    cx = x + w // 2
    hull = [(cx - 84, sea_y + 2), (cx + 86, sea_y + 2), (cx + 66, sea_y + 20),
            (cx - 62, sea_y + 20)]
    d.polygon(hull, fill=(22, 34, 52))
    d.rectangle([cx - 62, sea_y - 12, cx + 62, sea_y + 2], fill=(38, 52, 72))
    for i in range(3):
        dx = cx - 48 + i * 36
        d.pieslice([dx, sea_y - 24, dx + 28, sea_y + 2], 180, 360,
                   fill=(96, 108, 122))
    d.rectangle([cx + 40, sea_y - 30, cx + 62, sea_y - 12],
                fill=(224, 220, 206))
    d.rectangle([cx + 46, sea_y - 40, cx + 56, sea_y - 30], fill=RED)
    # flame tongues rising off the midship
    for dx, fh, col in ((-16, 44, RED), (-2, 58, (232, 126, 34)),
                        (12, 38, (244, 180, 60))):
        bx = cx + dx
        d.polygon([(bx - 11, sea_y - 10), (bx + 3, sea_y - 10 - fh),
                   (bx + 12, sea_y - 10)], fill=col)
    d.ellipse([cx - 26, sea_y - 20, cx + 26, sea_y - 6], fill=RED)
    # a layered smoke plume boiling up and trailing off to the right:
    # dark puffs behind, paler cores in front
    for sx, sy, r in ((cx + 20, sea_y - 54, 8), (cx + 38, sea_y - 63, 11),
                      (cx + 60, sea_y - 70, 14), (cx + 86, sea_y - 75, 17),
                      (cx + 114, sea_y - 78, 19)):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(122, 120, 114))
    for sx, sy, r in ((cx + 36, sea_y - 60, 7), (cx + 58, sea_y - 67, 9),
                      (cx + 84, sea_y - 72, 11), (cx + 112, sea_y - 75, 12)):
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(168, 166, 158))
    # wake at the stern and wave crests across the strait
    d.line([cx - 84, sea_y + 12, cx - 116, sea_y + 16], fill=(168, 196, 208),
           width=3)
    d.line([cx - 80, sea_y + 18, cx - 104, sea_y + 22], fill=(168, 196, 208),
           width=3)
    waves(d, x + 8, sea_y + 15, w - 16, (110, 150, 175))
    waves(d, x + 22, sea_y + 24, w - 44, (84, 124, 152))


def motif_cartagena(d, x, y, w, h):
    bx, by, bw, bh = x + 18, y + 8, w - 36, h - 26
    d.rectangle([bx, by, bx + bw, by + bh], fill=(219, 209, 182))
    d.rectangle([bx, by, bx + bw, by + 22], fill=RED)
    d.line([bx, by + 22, bx + bw, by + 22], fill=GOLD, width=3)
    for i in range(9):  # awning stripes
        ax = bx + 8 + i * (bw - 16) // 9
        col = RED if i % 2 == 0 else (240, 238, 228)
        d.polygon([(ax, by + 22), (ax + (bw - 16) // 9, by + 22),
                   (ax + (bw - 16) // 9 - 4, by + 38), (ax + 4, by + 38)],
                  fill=col)
    # double glass entrance doors with a centre mullion and handles
    dx0, dx1 = bx + bw // 2 - 19, bx + bw // 2 + 19
    d.rectangle([dx0, by + bh - 46, dx1, by + bh], fill=(70, 92, 114))
    d.rectangle([dx0, by + bh - 46, dx1, by + bh], outline=(52, 46, 40),
                width=3)
    d.line([bx + bw // 2, by + bh - 46, bx + bw // 2, by + bh],
           fill=(52, 46, 40), width=3)
    d.line([bx + bw // 2 - 6, by + bh - 24, bx + bw // 2 - 6, by + bh - 12],
           fill=(224, 220, 206), width=3)
    d.line([bx + bw // 2 + 6, by + bh - 24, bx + bw // 2 + 6, by + bh - 12],
           fill=(224, 220, 206), width=3)
    d.line([dx0 + 4, by + bh - 42, dx0 + 14, by + bh - 20],
           fill=(150, 172, 192), width=3)
    # display windows with shelf lines and goods silhouettes inside
    for i in range(3):
        for wx in (bx + 18 + i * 52, bx + bw - 52 - i * 52):
            d.rectangle([wx, by + 48, wx + 34, by + 76], fill=(100, 124, 148))
            d.rectangle([wx, by + 48, wx + 34, by + 76],
                        outline=(52, 46, 40), width=2)
            d.line([wx, by + 66, wx + 34, by + 66], fill=(52, 46, 40),
                   width=2)
            d.rectangle([wx + 5, by + 56, wx + 11, by + 66],
                        fill=(196, 120, 44))
            d.rectangle([wx + 15, by + 58, wx + 20, by + 66],
                        fill=(70, 110, 150))
            d.rectangle([wx + 23, by + 69, wx + 29, by + 75],
                        fill=(150, 44, 36))
            d.line([wx + 4, by + 52, wx + 16, by + 62],
                   fill=(170, 192, 208), width=2)
    # a shopping cart parked by the door: basket, handle and two wheels
    kx, ky = bx + bw - 66, by + bh - 26
    d.line([kx - 6, ky - 8, kx + 2, ky - 8], fill=(52, 46, 40), width=3)
    d.polygon([(kx, ky - 6), (kx + 36, ky - 6), (kx + 30, ky + 10),
               (kx + 5, ky + 10)], outline=(52, 46, 40), width=3)
    d.line([kx + 4, ky + 2, kx + 33, ky + 2], fill=(52, 46, 40), width=2)
    d.line([kx + 5, ky + 10, kx + 3, ky + 15], fill=(52, 46, 40), width=3)
    d.line([kx + 30, ky + 10, kx + 28, ky + 15], fill=(52, 46, 40), width=3)
    for wx in (kx + 6, kx + 27):
        d.ellipse([wx - 3, ky + 14, wx + 3, ky + 20], fill=(52, 46, 40))
    # police cordon: two posts and a sagging striped tape
    gy = y + h - 12
    for px in (x + 8, x + w - 14):
        d.rectangle([px, gy - 34, px + 6, gy], fill=(40, 40, 44))
    seg = 26
    sx = x + 11
    while sx < x + w - 20:
        sag = 7 if (sx // seg) % 2 == 0 else 2
        col = RED if (sx // seg) % 2 == 0 else (240, 238, 228)
        d.line([sx, gy - 30 + sag, sx + seg, gy - 30 + (2 if sag == 7 else 7)],
               fill=col, width=6)
        sx += seg


def motif_hodeidah(d, x, y, w, h):
    d.rectangle([x, y + h - 30, x + w, y + h], fill=SEA)
    d.polygon([(x + w - 96, y + h), (x + w, y + 30), (x + w, y + h)],
              fill=(206, 186, 140))
    d.ellipse([x + 16, y + 6, x + 52, y + 42], fill=(208, 84, 52))
    for cxx in (x + 74, x + 140):  # two port cranes
        d.line([cxx, y + h - 30, cxx, y + 22], fill=NAVY, width=6)
        d.line([cxx, y + 22, cxx + 56, y + 40], fill=NAVY, width=6)
        d.line([cxx, y + 22, cxx - 26, y + h - 30], fill=NAVY, width=4)
        d.rectangle([cxx - 5, y + 22, cxx + 9, y + 32],
                    fill=(90, 96, 104))  # operator cab
        d.line([cxx + 44, y + 36, cxx + 44, y + 62], fill=NAVY, width=3)
        d.rectangle([cxx + 36, y + 62, cxx + 52, y + 74], fill=(90, 96, 104))
    hx = x + 6  # ship at the quay, drawn large and clear of the coast
    wl = y + h - 30
    d.polygon([(hx, wl), (hx + 148, wl), (hx + 130, y + h - 8),
               (hx + 16, y + h - 8)], fill=(22, 34, 52))
    d.rectangle([hx + 8, wl - 8, hx + 140, wl], fill=(150, 44, 36))
    for px in range(4):  # portholes along the hull
        d.ellipse([hx + 30 + px * 22, wl + 6, hx + 38 + px * 22, wl + 14],
                  fill=(200, 212, 222))
    for i, col in enumerate(((196, 120, 44), (70, 110, 150),
                             (196, 120, 44))):  # container stacks
        cxx = hx + 16 + i * 34
        d.rectangle([cxx, wl - 26, cxx + 30, wl - 8], fill=col)
    d.rectangle([hx + 50, wl - 40, hx + 80, wl - 26],
                fill=(70, 110, 150))  # one box stacked on deck
    d.rectangle([hx + 116, wl - 40, hx + 140, wl - 8],
                fill=(224, 220, 206))  # bridge tower
    d.rectangle([hx + 122, wl - 34, hx + 134, wl - 28], fill=(40, 60, 84))
    d.line([hx + 60, wl - 26, hx + 60, wl - 44], fill=(22, 34, 52),
           width=4)  # mast
    waves(d, x + 10, wl + 13, w - 20, (110, 150, 175))
    waves(d, x + 26, wl + 22, w - 52, (84, 124, 152))


def star(d, cx, cy, r, col):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=col)


def motif_putin(d, x, y, w, h):
    base = y + h - 8
    # refinery: two distillation columns, pipes and a flare flame
    for cxx, chh in ((x + 26, 74), (x + 66, 58)):
        d.rectangle([cxx, base - chh, cxx + 24, base], fill=(124, 128, 134))
        for k in range(3):
            ly = base - chh + 12 + k * (chh // 3)
            d.line([cxx - 4, ly, cxx + 28, ly], fill=(96, 100, 106),
                   width=4)
    d.line([x + 38, base - 74, x + 38, base - 92], fill=(96, 100, 106),
           width=5)
    d.polygon([(x + 38, base - 108), (x + 46, base - 90), (x + 30,
               base - 90)], fill=(238, 132, 48))
    d.line([x + 50, base - 30, x + 120, base - 30], fill=(96, 100, 106),
           width=5)
    d.line([x + 50, base - 48, x + 104, base - 48], fill=(96, 100, 106),
           width=4)
    # a spherical storage tank between the columns and the wall
    d.ellipse([x + 92, base - 42, x + 126, base - 8], fill=(150, 152, 156))
    d.ellipse([x + 100, base - 38, x + 112, base - 28], fill=(172, 174, 178))
    d.line([x + 100, base - 10, x + 100, base], fill=(96, 100, 106),
           width=4)
    d.line([x + 118, base - 10, x + 118, base], fill=(96, 100, 106),
           width=4)
    # Kremlin wall and tower with spire
    wx = x + 128
    d.rectangle([wx, base - 52, x + w - 8, base], fill=(128, 52, 44))
    for i in range(6):
        mx_ = wx + 6 + i * 18
        d.rectangle([mx_, base - 62, mx_ + 10, base - 52],
                    fill=(128, 52, 44))
    d.line([wx + 4, base - 40, x + w - 12, base - 40], fill=(110, 44, 38),
           width=3)
    tx = x + w - 66
    d.rectangle([tx, base - 92, tx + 42, base], fill=(140, 58, 48))
    d.line([tx, base - 64, tx + 42, base - 64], fill=(224, 220, 206),
           width=3)
    d.ellipse([tx + 12, base - 56, tx + 30, base - 38],
              fill=(224, 220, 206))  # clock face
    d.line([tx + 21, base - 47, tx + 21, base - 53], fill=(52, 46, 40),
           width=2)
    d.line([tx + 21, base - 47, tx + 26, base - 44], fill=(52, 46, 40),
           width=2)
    d.polygon([(tx - 5, base - 92), (tx + 47, base - 92), (tx + 21,
               base - 128)], fill=(34, 84, 60))
    star(d, tx + 21, base - 133, 7, GOLD_L)


MOTIFS = (motif_hormuz, motif_cartagena, motif_hodeidah, motif_putin)


# ---------------------------------------------------------------- panels
PANELS = (
    ("STRAIT OF HORMUZ", "HORMUZ ESCALATES AGAIN",
     "IRGC says two more tankers were set ablaze on an 'unapproved route' "
     "through the strait — claims not independently verified."),
    ("COLOMBIA · CARTAGENA", "CARTAGENA SIEGE ENDS",
     "Security forces storm the supermarket and free every hostage "
     "unharmed; one assailant killed. De la Espriella: common crime, "
     "no armed-group link."),
    ("YEMEN · RED SEA", "THE WAR WIDENS TO THE RED SEA",
     "The Saudi-led coalition strikes Hodeidah port as Houthis threaten "
     "Jeddah; a Houthi attack on a Riyadh tower wounds 11."),
    ("KREMLIN · MOSCOW", "PUTIN VOWS 'INEVITABLE' RETALIATION",
     "Putin promises retaliation for refinery strikes. Kyiv claims the "
     "Sparta II hit, defends Benghazi under Article 51; Libya seeks an "
     "emergency UN meeting."),
)


def panel(d, x, y, w, h, kicker, headline, body, motif):
    d.rectangle([x + 6, y + 6, x + w + 6, y + h + 6],
                fill=(209, 199, 171))  # soft offset shadow on the paper
    d.rectangle([x, y, x + w, y + h], fill=CREAM)
    d.rectangle([x, y, x + w, y + h], outline=NAVY, width=3)
    px = x + 26
    motif_w = 264
    motif(d, x + w - motif_w - 18, y + 16, motif_w, 118)
    ky = y + 16
    d.rectangle([px, ky + 3, px + 15, ky + 29], fill=RED)
    text(d, px + 26, ky, kicker, F(SANS_B, 30), RED)
    hy = ky + 40
    hw = w - 52 - motif_w - 12
    hf, hs, hlines = fit_wrap(d, headline, SANS_B, 54, hw, 1, floor=40)
    if len(hlines) > 1:
        hf, hs, hlines = fit_wrap(d, headline, SANS_B, 46, hw, 2, floor=36)
    for ln in hlines:
        text(d, px, hy, ln, hf, NAVY)
        hy += int(hs * 1.14)
    ry = max(hy + 2, y + 140)
    d.rectangle([px, ry, x + w - 26, ry + 4], fill=GOLD)
    by = ry + 14
    bf = bs = None
    blines = []
    for size in range(36, 25, -1):
        cand = wrap(d, body, F(SANS, size), w - 52)
        if (len(cand) <= 3
                and by + len(cand) * int(size * 1.18) <= y + h - 8):
            bf, bs, blines = F(SANS, size), size, cand
            break
    if bf is None:
        bs = 26
        bf = F(SANS, bs)
        blines = wrap(d, body, bf, w - 52)
    for ln in blines:
        text(d, px, by, ln, bf, INK)
        by += int(bs * 1.18)
    assert by <= y + h - 8, "panel overflow: " + headline


def panels(d):
    pw = (CW - 28) // 2
    ph = 284
    spots = ((MX, 738), (MX + pw + 28, 738), (MX, 1036),
             (MX + pw + 28, 1036))
    for (x, y), (kick, head, body), motif in zip(spots, PANELS, MOTIFS):
        panel(d, x, y, pw, ph, kick, head, body, motif)


# ---------------------------------------------------------------- briefs
BRIEFS_L = (
    ("SPACE", "Zeeshan Ali becomes the first foreign national aboard "
              "China's Tiangong station, arriving on Shenzhou-24"),
    ("GAZA", "Israeli strike kills a second Hamas security chief in "
              "24 hours: Col. Mohammad Abuelouf, with his wife and two "
              "children, in Gaza City's Beach camp"),
    ("SENEGAL", "Court of Arbitration for Sport returns the CAN-2025 "
                "title to Senegal; Morocco is stripped, ten months "
                "after the final"),
    ("CHINA", "Beijing opens an investigation into Shanghai party "
              "chief Chen Jining, a Politburo member, for suspected "
              "severe violations"),
    ("HUAWEI", "US jury in New York finds Huawei guilty of bank fraud "
               "and theft of trade secrets after an 11-week trial"),
    ("SUDAN", "Ethiopia offers to host an inclusive Sudanese dialogue "
              "as condemnation grows over RSF drone attacks on "
              "Khartoum; 28 women and girls reported abducted in Blue "
              "Nile state"),
    ("WASHINGTON", "Democrats secure a House majority of at least 259 "
                   "seats, the largest since 1990"),
    ("NORTH KOREA", "Pyongyang expels Switzerland's envoy, orders its "
                    "new diplomatic office closed and gives its head "
                    "48 hours to leave"),
)
BRIEFS_R = (
    ("INDONESIA", "Rescuers search for miners trapped since Nov 23 in "
                  "a flooded 100-metre mine"),
    ("BRITAIN", "Defence Ministry and MI5 warn firms backing Ukraine's "
                "military they may face Russian sabotage attempts, "
                "including arson by proxies"),
    ("BANGLADESH", "Textile workers win a 36% minimum-wage increase "
                   "after weeks of protests since October"),
    ("US SECURITY", "Hackers breach an unclassified CIA and "
                    "intelligence system; officials say classified "
                    "systems were not disrupted"),
    ("SOLOMONS", "Solomon Islands and Australia sign a security "
                 "treaty; Australia the first security partner, "
                 "foreign bases barred"),
    ("TARIFFS", "The Trump administration is set to unveil new tariffs "
                "on 16 trading partners after an excess-capacity probe"),
    ("SPAIN", "Spain heads to a snap election"),
    ("AUSTRALIA", "Annual inflation jumps to 4.9% from 4.3%, nearly "
                  "double the central bank's target midpoint; the "
                  "treasurer calls it a very serious moment"),
)


def wrap_brief(d, lead, rest, fb, fr, maxw):
    """Wrap one brief: bold lead + regular rest, fitted together.

    Returns a list of (prefix, text) lines; prefix is the bold lead plus
    the dash on the first line and None on continuation lines.
    """
    prefix = lead + " "
    pw = tw(d, prefix, fb) + tw(d, "— ", fr)
    lines, cur, cap = [], "", maxw - pw
    for word in rest.split():
        trial = (cur + " " + word).strip()
        if tw(d, trial, fr) <= cap or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur, cap = word, maxw
    if cur:
        lines.append(cur)
    return [(prefix, lines[0])] + [(None, ln) for ln in lines[1:]]


def briefs(d):
    top = 1332
    d.rectangle([MX, top + 6, MX + 15, top + 32], fill=RED)
    text(d, MX + 26, top, "AROUND THE WORLD IN BRIEF", F(SANS_B, 34), RED)
    d.rectangle([MX, top + 42, W - MX, top + 45], fill=GOLD)
    rows_top = top + 54
    rows_h = 1952 - rows_top
    colw = (CW - 28) // 2
    tx_off = 30
    chosen = None
    for size in range(33, 24, -1):
        fb, fr = F(SANS_B, size), F(SANS, size)
        lh = int(size * 1.1)
        cols = []
        ok = True
        for items in (BRIEFS_L, BRIEFS_R):
            wrapped = [wrap_brief(d, lead, rest, fb, fr,
                                  colw - tx_off - 6)
                       for lead, rest in items]
            if any(len(w_) > 3 for w_ in wrapped):
                ok = False
                break
            height = sum(len(w_) * lh + 4 for w_ in wrapped) - 4
            cols.append((wrapped, height))
        if ok and max(h for _, h in cols) <= rows_h:
            chosen = (fb, fr, lh, cols)
            break
    assert chosen is not None, "briefs do not fit"
    fb, fr, lh, cols = chosen
    for ci, (wrapped, _) in enumerate(cols):
        cx = MX + ci * (colw + 28)
        tx = cx + tx_off
        y = rows_top
        for lines in wrapped:
            d.rectangle([cx + 2, y + 9, cx + 14, y + 21], fill=GOLD)
            for prefix, ln in lines:
                if prefix is not None:
                    text(d, tx, y, prefix, fb, INK)
                    text(d, tx + tw(d, prefix, fb), y, "— " + ln, fr, INK)
                else:
                    text(d, tx, y, ln, fr, INK)
                y += lh
            y += 4


# ---------------------------------------------------------------- ticker
TICKER = ("S&P 500 7,201 ▼0.50% · NASDAQ 23,734 ▼1.48% · NIKKEI 57,012 "
          "▼2.78% · FTSE 100 10,467 ▼0.13% · BRENT $87.4 · GOLD $3,516 · "
          "EUR/USD 1.09")


def ticker(d):
    top, bot = 1960, 2024
    d.rectangle([MX, top, W - MX, bot], fill=NAVY)
    d.rectangle([MX, top, W - MX, top + 3], fill=GOLD)
    parts = TICKER.split("▼")
    f, _ = fit(d, TICKER, SANS_B, 34, CW - 48)
    total = tw(d, TICKER, f)
    x = (W - total) // 2
    y = top + (bot - top - f.size) // 2 - 2
    for i, part in enumerate(parts):
        if i > 0:
            text(d, x, y, "▼", f, RED_L)
            x += tw(d, "▼", f)
        if part:
            text(d, x, y, part, f, (240, 236, 222))
            x += tw(d, part, f)


# ---------------------------------------------------------------- render
def main():
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img)
    masthead(d)
    hero_scene(d, img)
    d = ImageDraw.Draw(img)
    hero_strip(d)
    panels(d)
    briefs(d)
    ticker(d)
    entry = img.resize((1024, 1024), Image.LANCZOS)
    entry.save(OUT)
    print("wrote", OUT, entry.size)


if __name__ == "__main__":
    main()
