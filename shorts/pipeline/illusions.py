"""Optical illusions drawn from scratch with cairo. Each takes `reveal` in [0, 1]:
0 = the illusion at full strength, 1 = the trick removed so the truth is visible."""
import math

from core import AREA, round_rect

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2


def panel(ctx, rgb=(0.09, 0.11, 0.17)):
    round_rect(ctx, X0, Y0, X1 - X0, Y1 - Y0, 36)
    ctx.set_source_rgb(*rgb)
    ctx.fill_preserve()
    ctx.clip()


def muller_lyer(ctx, fins=1.0, guides=0.0):
    """Two equal lines: fins pointing out (looks longer) vs arrowheads (looks shorter)."""
    panel(ctx)
    a, b, fl, ang = 290, 790, 100, math.radians(38)
    ctx.set_line_cap(1)  # round
    ctx.set_line_width(14)
    for y, out in ((720, 1), (1080, -1)):
        ctx.set_source_rgb(1, 1, 1)
        ctx.move_to(a, y)
        ctx.line_to(b, y)
        ctx.stroke()
        ctx.set_source_rgba(1, 1, 1, fins)
        for x, side in ((a, -1), (b, 1)):
            for s in (-1, 1):
                ctx.move_to(x, y)
                ctx.line_to(x + side * out * fl * math.cos(ang), y + s * fl * math.sin(ang))
                ctx.stroke()
    if guides > 0:
        ctx.set_source_rgba(1, 0.3, 0.3, guides)
        ctx.set_line_width(6)
        ctx.set_dash([18, 14])
        for x in (a, b):
            ctx.move_to(x, 600)
            ctx.line_to(x, 600 + 600 * guides)
            ctx.stroke()
        ctx.set_dash([])


def ebbinghaus(ctx, reveal=0.0, slide=0.0):
    """Same orange circle among big neighbours (looks small) and small neighbours (looks big)."""
    panel(ctx)
    r = 50
    left, right = (335, CY), (805, CY)
    a = 1 - reveal
    ctx.set_source_rgba(0.55, 0.58, 0.66, a)
    for k in range(6):
        t = k * math.pi / 3
        ctx.arc(left[0] + 178 * math.cos(t), CY + 178 * math.sin(t), 88, 0, 2 * math.pi)
        ctx.fill()
    for k in range(8):
        t = k * math.pi / 4
        ctx.arc(right[0] + 86 * math.cos(t), CY + 86 * math.sin(t), 22, 0, 2 * math.pi)
        ctx.fill()
    lx = left[0] + (CX - 62 - left[0]) * slide
    rx = right[0] + (CX + 62 - right[0]) * slide
    ctx.set_source_rgb(1.0, 0.55, 0.1)
    for x in (lx, rx):
        ctx.arc(x, CY, r, 0, 2 * math.pi)
        ctx.fill()


def hering(ctx, reveal=0.0, spin=0.0):
    """Two straight red lines over a fan of rays look bowed outward."""
    panel(ctx)
    ctx.set_source_rgba(0.55, 0.7, 1.0, 0.85 * (1 - reveal))
    ctx.set_line_width(3)
    for k in range(48):
        t = k * math.pi / 24 + spin
        ctx.move_to(CX, CY)
        ctx.line_to(CX + 900 * math.cos(t), CY + 900 * math.sin(t))
        ctx.stroke()
    ctx.set_source_rgb(1, 0.25, 0.3)
    ctx.set_line_width(10)
    for x in (CX - 170, CX + 170):
        ctx.move_to(x, Y0 + 50)
        ctx.line_to(x, Y1 - 50)
        ctx.stroke()


def cafe_wall(ctx, shift=1.0):
    """Rows of offset black/white tiles with grey mortar: parallel lines look tilted."""
    panel(ctx, (1, 1, 1))
    tw, th, mortar = 80, 70, 5
    rows = int((Y1 - Y0) / th) + 1
    pattern = (0, 0.25, 0.5, 0.25)
    for r in range(rows):
        y = Y0 + 20 + r * th
        off = pattern[r % 4] * tw * shift
        x = X0 - 2 * tw + off
        k = 0
        while x < X1 + tw:
            if k % 2 == 0:
                ctx.set_source_rgb(0.02, 0.02, 0.02)
                ctx.rectangle(x, y, tw, th)
                ctx.fill()
            x += tw
            k += 1
        ctx.set_source_rgb(0.5, 0.5, 0.5)
        ctx.rectangle(X0, y + th - mortar / 2, X1 - X0, mortar)
        ctx.fill()


def stepping_feet(ctx, t, stripes=1.0, speed=105):
    """Yellow and dark-blue bars glide at one constant speed but seem to take turns stepping."""
    panel(ctx, (0.5, 0.5, 0.5))
    period = 60
    for x in range(X0, X1, period):
        ctx.set_source_rgba(0, 0, 0, stripes)
        ctx.rectangle(x, Y0, period / 2, Y1 - Y0)
        ctx.fill()
        ctx.set_source_rgba(1, 1, 1, stripes)
        ctx.rectangle(x + period / 2, Y0, period / 2, Y1 - Y0)
        ctx.fill()
    bw, bh = 3 * period, 70
    span = (X1 - X0) + bw
    x = X0 - bw + (speed * t) % span
    for y, rgb in ((CY - 130, (1.0, 0.92, 0.0)), (CY + 60, (0.03, 0.08, 0.45))):
        ctx.set_source_rgb(*rgb)
        ctx.rectangle(x, y, bw, bh)
        ctx.fill()


# ---------- brightness / colour ----------

def gradient_squares(ctx, left, right, flatten=0.0, bridge=0.0, flat_level=0.18):
    """Two grey squares on a dark-to-light gradient (simultaneous contrast)."""
    import cairo
    round_rect(ctx, X0, Y0, X1 - X0, Y1 - Y0, 36)
    ctx.clip()
    g = cairo.LinearGradient(X0, 0, X1, 0)
    lo, hi = 0.04 + (flat_level - 0.04) * flatten, 0.96 + (flat_level - 0.96) * flatten
    g.add_color_stop_rgb(0, lo, lo, lo)
    g.add_color_stop_rgb(1, hi, hi, hi)
    ctx.set_source(g)
    ctx.paint()
    s = 190
    for x, v in ((300, left), (780, right)):
        ctx.set_source_rgb(v, v, v)
        ctx.rectangle(x - s / 2, CY - s / 2, s, s)
        ctx.fill()
    if bridge > 0 and left == right:
        ctx.set_source_rgb(left, left, left)
        ctx.rectangle(300, CY - 35, 480 * bridge, 70)
        ctx.fill()


def whites(ctx, flatten=0.0, grey=0.5):
    """White's illusion: identical grey bars sitting on black stripes vs on white stripes."""
    ctx.save()
    round_rect(ctx, X0, Y0, X1 - X0, Y1 - Y0, 36)
    ctx.clip()
    sh = 44
    n = int((Y1 - Y0) / sh) + 1
    flat = 0.12
    for i in range(n):
        v = 0.0 if i % 2 == 0 else 1.0
        v = v + (flat - v) * flatten
        ctx.set_source_rgb(v, v, v)
        ctx.rectangle(X0, Y0 + i * sh, X1 - X0, sh)
        ctx.fill()
    ctx.set_source_rgb(grey, grey, grey)
    for i in range(n):
        y = Y0 + i * sh
        if not (Y0 + 250 < y < Y1 - 280):
            continue
        if i % 2 == 0:  # black stripe -> left group
            ctx.rectangle(170, y, 190, sh)
        else:  # white stripe -> right group
            ctx.rectangle(720, y, 190, sh)
        ctx.fill()
    ctx.restore()


def munker(ctx, fade=0.0):
    """The same red under blue stripes (looks purple) and under yellow stripes (looks orange)."""
    panel(ctx, (0.08, 0.09, 0.13))
    red = (0.9, 0.12, 0.15)
    sh = 26
    for x0, other in ((110, (0.1, 0.25, 1.0)), (610, (1.0, 0.92, 0.0))):
        for i in range(24):
            y = CY - 312 + i * sh
            if i % 2 == 0:
                ctx.set_source_rgb(*red)
            else:
                ctx.set_source_rgba(*other, 1 - fade)
            ctx.rectangle(x0, y, 360, sh)
            ctx.fill()
