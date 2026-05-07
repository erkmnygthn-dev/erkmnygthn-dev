#!/usr/bin/env python3
"""Generate assets/erk-showroom-banner.png for ERK INDUSTRY GitHub profile."""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 400
OUT = "assets/erk-showroom-banner.png"

FONT_BOLD   = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf"
FONT_REG    = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"
FONT_MED    = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf"

# ── COLOURS ──────────────────────────────────────────────────────────────────
CYAN   = (0, 212, 255)
BLUE   = (0, 100, 220)
WHITE  = (232, 244, 255)
DIM    = (0, 160, 220)


# ── 1. BACKGROUND (numpy gradient) ───────────────────────────────────────────
x_n = np.linspace(0, 1, W, dtype=np.float32)
y_n = np.linspace(0, 1, H, dtype=np.float32)
xx, yy = np.meshgrid(x_n, y_n)

t = xx * 0.55 + yy * 0.45  # diagonal 0‥1

bg = np.zeros((H, W, 3), dtype=np.float32)
bg[:, :, 0] = 2  + t * 3    # R  2‥5
bg[:, :, 1] = 4  + t * 6    # G  4‥10
bg[:, :, 2] = 15 + t * 8    # B 15‥23

# centre radial blue-purple ambient
dist_c = np.hypot(xx * W - W / 2, yy * H - H / 2)
g_c = (1 - (dist_c / (min(W, H) * 0.62)).clip(0, 1)) ** 2
bg[:, :, 1] += g_c * 7
bg[:, :, 2] += g_c * 30

# left soft cyan tint
dist_l = np.hypot(xx * W - W * 0.14, yy * H - H / 2)
g_l = (1 - (dist_l / (W * 0.30)).clip(0, 1)) ** 1.8
bg[:, :, 1] += g_l * 5
bg[:, :, 2] += g_l * 18

# right soft blue tint
dist_r = np.hypot(xx * W - W * 0.86, yy * H - H / 2)
g_r = (1 - (dist_r / (W * 0.30)).clip(0, 1)) ** 1.8
bg[:, :, 2] += g_r * 14

bg = bg.clip(0, 255).astype(np.uint8)
canvas = Image.fromarray(bg, 'RGB').convert('RGBA')


# ── HELPER FUNCTIONS ─────────────────────────────────────────────────────────
def composite(canvas, layer):
    return Image.alpha_composite(canvas, layer)

def new_layer():
    return Image.new('RGBA', (W, H), (0, 0, 0, 0))

def ov_line(canvas, x1, y1, x2, y2, rgb, alpha, width=1):
    lay = new_layer(); d = ImageDraw.Draw(lay)
    d.line([(x1, y1), (x2, y2)], fill=(*rgb, alpha), width=width)
    return composite(canvas, lay)

def ov_ellipse(canvas, cx, cy, r, rgb, alpha, width=1):
    lay = new_layer(); d = ImageDraw.Draw(lay)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(*rgb, alpha), width=width)
    return composite(canvas, lay)

def ov_dot(canvas, cx, cy, r, rgb, alpha):
    lay = new_layer(); d = ImageDraw.Draw(lay)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(*rgb, alpha))
    return composite(canvas, lay)


# ── 2. GRID ───────────────────────────────────────────────────────────────────
grid_layer = new_layer()
gd = ImageDraw.Draw(grid_layer)
gc = (0, 130, 210, 17)
for x in range(80, W, 80):
    gd.line([(x, 0), (x, H)], fill=gc, width=1)
for y in [72, 144, 180, 216, 288]:
    gd.line([(0, y), (W, y)], fill=gc, width=1)
canvas = composite(canvas, grid_layer)


# ── 3. DIAGONAL DEPTH LINES ───────────────────────────────────────────────────
for (x1, y1, x2, y2, a) in [
    (-60, 0,   290, H,  36), (180,  0,   530, H,  26),
    (990,  0,  1340, H,  36), (1100, H,  1450, 0,  26),
]:
    canvas = ov_line(canvas, x1, y1, x2, y2, (0, 40, 140), a)


# ── 4. DEPTH RINGS ────────────────────────────────────────────────────────────
for r, a in [(178, 56), (138, 46), (98, 36), (58, 28), (20, 20)]:
    canvas = ov_ellipse(canvas, 1090, 180, r, (0, 60, 190), a)
for r, a in [(148, 51), (108, 41), (68, 31), (30, 22)]:
    canvas = ov_ellipse(canvas, 190, 180, r, (0, 50, 165), a)


# ── 5. EDGE GLOW LINES (numpy horizontal gradient bands) ─────────────────────
def hgrad_band(y_top, band_h, peak_g, peak_b, peak_a):
    arr = np.zeros((band_h, W, 4), dtype=np.uint8)
    for i in range(W):
        xn = i / W
        if xn < 0.5:
            t2 = xn * 2
            g2 = int(peak_g * (0.6 + 0.4 * t2))
            a2 = int(5 + t2 * (peak_a - 5))
        else:
            t2 = (xn - 0.5) * 2
            g2 = int(peak_g * (1 - 0.35 * t2))
            a2 = int(peak_a - t2 * (peak_a - 5))
        arr[:, i] = [0, g2, peak_b, a2]
    img = Image.fromarray(arr, 'RGBA')
    canvas.paste(img, (0, y_top), img)

hgrad_band(0,   2, 212, 255, 232)   # top edge
hgrad_band(H-2, 2, 140, 220, 190)   # bottom edge


# ── 6. HORIZONTAL ACCENT LINES around title ───────────────────────────────────
def accent_line(y_pos, x0, x1_end, alpha_peak):
    line_w = x1_end - x0
    arr = np.zeros((1, line_w, 4), dtype=np.uint8)
    for i in range(line_w):
        xn = i / line_w
        if xn < 0.5:
            t2 = xn * 2
            a2 = int(4 + t2 * (alpha_peak - 4))
            g2 = int(160 + t2 * 50)
        else:
            t2 = (xn - 0.5) * 2
            a2 = int(alpha_peak - t2 * (alpha_peak - 4))
            g2 = int(210 - t2 * 60)
        arr[0, i] = [0, g2, 220, a2]
    img = Image.fromarray(arr, 'RGBA')
    canvas.paste(img, (x0, y_pos), img)

accent_line(135, 130, 1150, 128)
accent_line(245, 260, 1020, 107)


# ── 7. VERTICAL SIDE ACCENTS ──────────────────────────────────────────────────
canvas = ov_line(canvas, 62,   108, 62,   252, CYAN, 36)
canvas = ov_line(canvas, 1218, 108, 1218, 252, BLUE, 36)


# ── 8. CORNER BRACKETS ────────────────────────────────────────────────────────
# Top-left
canvas = ov_line(canvas, 36, 36, 36, 90, CYAN, 200, 2)
canvas = ov_line(canvas, 36, 36, 90, 36, CYAN, 200, 2)
canvas = ov_dot(canvas,  36, 36,  3, CYAN, 230)
# Top-right
canvas = ov_line(canvas, 1244, 36, 1244, 90,  CYAN, 200, 2)
canvas = ov_line(canvas, 1244, 36, 1192, 36,  CYAN, 200, 2)
canvas = ov_dot(canvas,  1244, 36,  3,   CYAN, 230)
# Bottom-left
canvas = ov_line(canvas, 36, 326, 36, 274, BLUE, 154, 2)
canvas = ov_line(canvas, 36, 326, 90, 326, BLUE, 154, 2)
canvas = ov_dot(canvas,  36, 326,  3, BLUE, 205)
# Bottom-right
canvas = ov_line(canvas, 1244, 326, 1244, 274, BLUE, 154, 2)
canvas = ov_line(canvas, 1244, 326, 1192, 326, BLUE, 154, 2)
canvas = ov_dot(canvas,  1244, 326,  3,   BLUE, 205)


# ── 9. TEXT ───────────────────────────────────────────────────────────────────
f_title = ImageFont.truetype(FONT_BOLD, 66)
f_sub   = ImageFont.truetype(FONT_MED,  15)
f_tag   = ImageFont.truetype(FONT_REG,  10)
f_sm    = ImageFont.truetype(FONT_REG,   9)

draw = ImageDraw.Draw(canvas)


def spaced_width(draw, text, font, spacing):
    """Measure total width of text with extra letter spacing."""
    total = 0
    for i, ch in enumerate(text):
        bb = draw.textbbox((0, 0), ch, font=font)
        total += bb[2] - bb[0]
        if i < len(text) - 1:
            total += spacing
    return total


def draw_spaced(draw, x, y, text, font, fill, spacing):
    """Draw text with manual letter spacing."""
    for i, ch in enumerate(text):
        draw.text((x, y), ch, font=font, fill=fill)
        bb = draw.textbbox((0, 0), ch, font=font)
        x += bb[2] - bb[0] + spacing
        if i < len(text) - 1:
            x += 0


def draw_centered(draw, y, text, font, fill):
    bb = draw.textbbox((0, 0), text, font=font)
    x = (W - (bb[2] - bb[0])) // 2
    draw.text((x, y), text, font=font, fill=fill)


def draw_centered_spaced(draw, y, text, font, fill, spacing):
    tw = spaced_width(draw, text, font, spacing)
    x = (W - tw) // 2
    draw_spaced(draw, x, y, text, font, fill, spacing)


# ── Title shadow (offset, dark) ───────────────────────────────────────────────
TITLE = "ERK INDUSTRY"
TITLE_SP = 10
tw = spaced_width(draw, TITLE, f_title, TITLE_SP)
tx = (W - tw) // 2

draw_spaced(draw, tx + 2, 152, TITLE, f_title, (0, 18, 60, 215), TITLE_SP)

# Title glow halo (slight cyan tint, very transparent, offset 4 directions)
for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    draw_spaced(ld, tx + dx, 150 + dy, TITLE, f_title, (0, 180, 255, 18), TITLE_SP)
    canvas = composite(canvas, lay)

# Rebuild draw handle after compositing
draw = ImageDraw.Draw(canvas)

# Title: crisp main layer
draw_spaced(draw, tx, 150, TITLE, f_title, (*WHITE, 255), TITLE_SP)

# ── Subtitle ──────────────────────────────────────────────────────────────────
SUBTITLE = "Built in Turkiye. Designed for the world."
draw_centered(draw, 255, SUBTITLE, f_sub, (*CYAN, 225))

# ── Bottom tag line ───────────────────────────────────────────────────────────
TAG = "AI  \u2014  INDUSTRIAL  \u2014  GAMING  \u2014  MOBILE  \u2014  SAAS"
draw_centered(draw, 312, TAG, f_tag, (0, 100, 220, 92))

# ── System labels ─────────────────────────────────────────────────────────────
draw.text((58, 52), "SYS // ERK-001", font=f_sm, fill=(*CYAN, 112))

est_txt = "EST. TURKIYE"
bb = draw.textbbox((0, 0), est_txt, font=f_sm)
draw.text((W - 58 - (bb[2]-bb[0]), 52), est_txt, font=f_sm, fill=(*CYAN, 112))

# ── Bottom corner labels ───────────────────────────────────────────────────────
draw.text((58, 348), "FOUNDER / BUILDER", font=f_sm, fill=(*DIM, 72))

right_lbl = "YIGITHAN ERKMEN"
bb = draw.textbbox((0, 0), right_lbl, font=f_sm)
draw.text((W - 58 - (bb[2]-bb[0]), 348), right_lbl, font=f_sm, fill=(*DIM, 72))


# ── 10. SAVE ──────────────────────────────────────────────────────────────────
canvas.convert('RGB').save(OUT, 'PNG', optimize=True)
print(f"Saved: {OUT}")
