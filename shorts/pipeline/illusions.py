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


# ---------- size / alignment (Tue 03/11/2026) ----------

def _sector(ctx, cx, cy, r1, r2, a0, a1):
    ctx.new_path()
    ctx.arc(cx, cy, r2, a0, a1)
    ctx.arc_negative(cx, cy, r1, a1, a0)
    ctx.close_path()


def jastrow(ctx, t=0.0, overlay=0.0, sway=1.0):
    """Jastrow: two identical ring sectors stacked; the lower one looks bigger. overlay 0->1 slides the top
    one down onto the bottom one (they match exactly)."""
    panel(ctx)
    r1, r2 = 330, 500
    a0, a1 = math.radians(-120), math.radians(-60)
    dx = 22 * math.sin(t * 2.4) * sway * (1 - overlay)
    cy_b = 1300
    cy_a = 1060 + (cy_b - 1060) * overlay
    _sector(ctx, CX - dx, cy_b, r1, r2, a0, a1)
    ctx.set_source_rgb(0.36, 0.78, 0.98)
    ctx.fill()
    _sector(ctx, CX + dx, cy_a, r1, r2, a0, a1)
    ctx.set_source_rgba(1.0, 0.36, 0.54, 1 - 0.45 * overlay)
    ctx.fill()


def ponzo(ctx, t=0.0, fade=0.0, slide=0.0):
    """Ponzo: two equal yellow bars on converging rails; the far (top) bar looks longer. slide moves the top
    bar down beside the bottom one."""
    panel(ctx, (0.10, 0.10, 0.12))
    vx, vy = CX, Y0 + 30
    a = 1 - fade
    ctx.set_line_cap(1)
    ctx.set_source_rgba(0.55, 0.42, 0.30, a)  # sleepers, spaced like a real track in perspective
    for k in range(1, 15):
        y = vy + (Y1 - vy) * (k / 14) ** 1.7  # closer together toward the horizon
        f = (y - vy) / (Y1 - vy)
        half = 380 * f
        ctx.set_line_width(4 + 16 * f)
        ctx.move_to(vx - half * 1.15, y)
        ctx.line_to(vx + half * 1.15, y)
        ctx.stroke()
    ctx.set_source_rgba(0.85, 0.87, 0.92, a)
    ctx.set_line_width(12)
    for s in (-1, 1):
        ctx.move_to(vx, vy)
        ctx.line_to(vx + s * 380, Y1)
        ctx.stroke()
    L = 230
    y_top, y_bot = 640, 1110
    y_t = y_top + (y_bot - 70 - y_top) * slide
    ctx.set_line_width(26)
    ctx.set_line_cap(0)
    for y, rgb in ((y_t, (1.0, 0.85, 0.25)), (y_bot, (1.0, 0.85, 0.25))):
        ctx.set_source_rgb(*rgb)
        ctx.move_to(CX - L / 2, y)
        ctx.line_to(CX + L / 2, y)
        ctx.stroke()


def _mesa(ctx, c, u, v, alpha=1.0, pernas=1.0, cor=(0.80, 0.55, 0.33), topo=True):
    """Shepard table top = parallelogram c ± u/2 ± v/2, with four legs behind it and a thin front edge."""
    pts = [(c[0] + sa * u[0] / 2 + sb * v[0] / 2, c[1] + sa * u[1] / 2 + sb * v[1] / 2)
           for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    if pernas > 0:
        ctx.set_source_rgba(0.45, 0.28, 0.16, pernas)
        for x, y in pts:
            ctx.rectangle(x - 9, y, 18, 150)
            ctx.fill()
        low = max(range(4), key=lambda i: pts[i][1])  # corner nearest the viewer: thickness along its two edges
        ctx.set_source_rgba(0.55, 0.34, 0.19, pernas * (1 if topo else 0))
        for j in ((low + 1) % 4, (low + 3) % 4):
            ctx.move_to(*pts[low])
            ctx.line_to(*pts[j])
            ctx.line_to(pts[j][0], pts[j][1] + 22)
            ctx.line_to(pts[low][0], pts[low][1] + 22)
            ctx.close_path()
            ctx.fill()
    if not topo:
        return
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()
    ctx.set_source_rgba(*cor, alpha)
    ctx.fill()


def _rot(v, a):
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


SHEP_U = _rot((300, 0), math.radians(-62))  # long side, receding into depth
SHEP_V = _rot((135, 0), math.radians(12))
SHEP_ROT = math.radians(78)  # the right table is the same top turned by this angle


def shepard(ctx, match=0.0):
    """Shepard tables: identical table tops, one turned; the left looks long and thin, the right short and wide.
    match 0->1 lifts the right top off its legs, turns it and lays it on the left one."""
    panel(ctx)
    cl, cr = (330, 830), (765, 900)
    _mesa(ctx, cl, SHEP_U, SHEP_V)
    a = SHEP_ROT * (1 - match)
    c = (cr[0] + (cl[0] - cr[0]) * match, cr[1] + (cl[1] - cr[1]) * match)
    sai = min(1.0, match * 3)  # the legs stay behind and fade while the top flies over
    if sai < 1:
        _mesa(ctx, cr, _rot(SHEP_U, SHEP_ROT), _rot(SHEP_V, SHEP_ROT), pernas=1 - sai, topo=False)
    k = min(1.0, match * 1.4)
    cor = (0.80 + (0.36 - 0.80) * k, 0.55 + (0.78 - 0.55) * k, 0.33 + (0.98 - 0.33) * k)
    _mesa(ctx, c, _rot(SHEP_U, a), _rot(SHEP_V, a), pernas=0, alpha=1 - 0.25 * k, cor=cor)


POGG_W = 170
POGG_SLOPE = math.tan(math.radians(33))
POGG_X0 = CX - POGG_W / 2


def poggendorff(ctx, truth=0.0, opcoes=(-115, -45, 0), certo=2):
    """Poggendorff: a diagonal disappears behind a bar; which of the lines on the right is its continuation?
    opcoes = vertical offsets (px) of A/B/C from the true continuation. truth 0->1 makes the bar see-through and
    draws the real line across it."""
    panel(ctx)
    x0, x1 = POGG_X0, POGG_X0 + POGG_W
    y_in = 760

    def y_at(x, off=0.0):
        return y_in + (x - x0) * POGG_SLOPE + off
    ctx.set_line_cap(1)
    ctx.set_line_width(12)
    ctx.set_source_rgb(1, 1, 1)
    ctx.move_to(X0 + 50, y_at(X0 + 50))
    ctx.line_to(x0, y_in)
    ctx.stroke()
    from core import font
    for i, off in enumerate(opcoes):
        ok = i == certo
        cor = (0.30, 0.90, 0.50) if (ok and truth > 0) else (1, 1, 1)
        al = 1.0 if (ok or truth == 0) else 1 - 0.65 * truth
        ctx.set_source_rgba(*cor, al)
        xe = x1 + 260
        ctx.move_to(x1, y_at(x1, off))
        ctx.line_to(xe, y_at(xe, off))
        ctx.stroke()
        font(ctx, 46, "ExtraBold")
        ctx.move_to(xe + 22, y_at(xe, off) + 16)
        ctx.show_text("ABC"[i])
    ctx.set_source_rgba(0.55, 0.58, 0.66, 1 - 0.7 * truth)
    ctx.rectangle(x0, Y0 + 40, POGG_W, Y1 - Y0 - 80)
    ctx.fill()
    if truth > 0:
        ctx.set_source_rgb(0.30, 0.90, 0.50)
        ctx.set_dash([20, 14])
        ctx.move_to(x0, y_in)
        ctx.line_to(x0 + (x1 - x0) * truth, y_at(x0 + (x1 - x0) * truth))
        ctx.stroke()
        ctx.set_dash([])
