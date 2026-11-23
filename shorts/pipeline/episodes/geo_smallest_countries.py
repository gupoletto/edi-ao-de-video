"""The 5 smallest countries on Earth, to scale (#5 -> #1). Fri 30/10/2026, topic: countries & geography, format: ranking.

Areas (CIA World Factbook / national figures): San Marino 61 km² (23.6 sq mi), Tuvalu 26 km² (10 sq mi, nine islands),
Nauru 21 km² (8.1 sq mi; ring road ~19 km = 12 mi), Monaco 2.08 km² (0.8 sq mi), Vatican City 0.49 km² (0.19 sq mi).
Central Park: 3.41 km² (1.32 sq mi), about 4.0 x 0.8 km -> it could hold the Vatican's area about 7 times.
San Marino's traditional founding date: 301 AD. Outlines: Natural Earth 1:10m, which is too coarse for the
tiniest states (its Vatican is 0.01 km²), so each single-piece outline is rescaled to the official area.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import geo  # noqa: E402
from core import BLUE, GREEN, PINK, WHITE, YELLOW, Seg, pill, ramp, render, text_center  # noqa: E402

DOTS = ["5", "4", "3", "2", "1"]
MAP = (geo.X0, geo.Y0, geo.X1, geo.Y1 - 200)  # shape area; the stat goes under it
PARK = (0.8, 4.0)  # Central Park, km (width, height)
AREA_KM2 = {"San Marino": 61, "Nauru": 21, "Monaco": 2.08, "Vatican": 0.49}


def true_area(rings, km2):
    """Scale a single outline about its centre so its area (local km) matches km2."""
    r = rings[0]
    lon0 = sum(p[0] for p in r) / len(r)
    lat0 = sum(p[1] for p in r) / len(r)
    c = math.cos(math.radians(lat0))
    now = geo.ring_area([(p[0] * c * 111.32, p[1] * 110.57) for p in r])
    f = math.sqrt(km2 / now)
    return [[(lon0 + (p[0] - lon0) * f, lat0 + (p[1] - lat0) * f) for p in r]]


SHAPES = {n: geo.country(n, "10m") for n in ("San Marino", "Tuvalu", "Nauru", "Monaco", "Vatican")}
SHAPES.update({n: true_area(SHAPES[n], a) for n, a in AREA_KM2.items()})
COLORS = {"San Marino": BLUE, "Tuvalu": (0.35, 0.85, 0.85), "Nauru": YELLOW, "Monaco": (1.0, 0.62, 0.25),
          "Vatican": PINK}


def head(rank, name):
    return {"big": f"#{rank}", "sub": name.upper(), "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def view_for(name, park=False):
    rings = SHAPES[name]
    v = geo.fit(rings, box=MAP, pad=120)
    if not park:
        return v
    # widen the frame so a Central Park rectangle at the same scale fits on the right
    pts = [v.proj(*p) for r in rings for p in r]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    pw, ph = PARK[0] / 6371, PARK[1] / 6371
    gap = pw * 1.5
    y0 = min(min(ys), (min(ys) + max(ys)) / 2 - ph / 2)
    y1 = max(max(ys), (min(ys) + max(ys)) / 2 + ph / 2)
    v = geo.View(v.proj, min(xs), y0, max(xs) + gap + pw, y1, MAP, 90)
    v.park = (max(xs) + gap, (min(ys) + max(ys)) / 2 - ph / 2, pw, ph)
    return v


VIEWS = {n: view_for(n, n in ("Monaco", "Vatican")) for n in SHAPES}


def grid(ctx, v):
    """1 km grid in the background, so every country is read at the same kind of scale."""
    step = 1.0 / geo.km_per_px(v)
    if step < 14:  # too dense: 10 km grid
        step *= 10
    ctx.set_source_rgba(1, 1, 1, 0.06)
    ctx.set_line_width(2)
    x = geo.CX % step
    while x < geo.X1:
        if x > geo.X0:
            ctx.move_to(x, MAP[1])
            ctx.line_to(x, MAP[3])
        x += step
    y = MAP[1] + (geo.CY - MAP[1]) % step
    while y < MAP[3]:
        ctx.move_to(geo.X0, y)
        ctx.line_to(geo.X1, y)
        y += step
    ctx.stroke()


def country(ctx, t, s, name, sq_mi, bar_km, bar_label, start=0.0):
    v = VIEWS[name]
    ctx.rectangle(MAP[0], MAP[1], MAP[2] - MAP[0], MAP[3] - MAP[1])
    ctx.set_source_rgba(1, 1, 1, 0.03)
    ctx.fill()
    grid(ctx, v)
    a = ramp(t, start, 0.5)
    ctx.save()
    ctx.translate(geo.CX, geo.CY)
    ctx.scale(0.6 + 0.4 * a, 0.6 + 0.4 * a)
    ctx.translate(-geo.CX, -geo.CY)
    geo.shape(ctx, SHAPES[name], v, COLORS[name], a, stroke=WHITE, width=4)
    ctx.restore()
    geo.scale_bar(ctx, v, bar_km, bar_label, geo.X0 + 50, MAP[3] - 90)
    k = ramp(t, s.mark(1), 1.2)
    val = sq_mi * k
    txt = f"{val:.2f} sq mi" if sq_mi < 1 else f"{val:.0f} sq mi"
    text_center(ctx, txt, geo.CX, geo.Y1 - 70, 72, COLORS[name], "ExtraBold", alpha=ramp(t, s.mark(1), 0.3))
    return v


def park(ctx, v, a, label=True):
    x, y, w, h = v.park
    px, py = v.ox + v.k * x, v.oy - v.k * (y + h)
    ctx.rectangle(px, py, v.k * w, v.k * h)
    ctx.set_source_rgba(*GREEN, 0.55 * a)
    ctx.fill_preserve()
    ctx.set_source_rgba(*GREEN, a)
    ctx.set_line_width(4)
    ctx.stroke()
    if label:
        ctx.save()
        ctx.translate(px + v.k * w / 2, py + v.k * h / 2)
        ctx.rotate(-math.pi / 2)
        text_center(ctx, "CENTRAL PARK", 0, 0, 34, WHITE, "ExtraBold", alpha=a)
        ctx.restore()


def d_intro(ctx, t, s):
    names = list(SHAPES)
    for i, n in enumerate(names):
        x = geo.X0 + 110 + i * 185
        y = geo.CY - 80 + (60 if i % 2 else -60)
        box = (x - 85, y - 85, x + 85, y + 85)
        v = geo.fit(SHAPES[n] if n != "Tuvalu" else SHAPES[n][:1], box=box, pad=6)
        a = ramp(t, 0.15 * i, 0.4)
        geo.shape(ctx, SHAPES[n] if n != "Tuvalu" else SHAPES[n][:1], v, COLORS[n], a, stroke=WHITE, width=3)
    pill(ctx, "FROM #5 TO #1", geo.CX, geo.Y1 - 120, YELLOW, ramp(t, 1.0, 0.3), size=48)


def d5(ctx, t, s):
    country(ctx, t, s, "San Marino", 23.6, 5, "5 km = 3 mi")
    pill(ctx, "FOUNDED 301 AD", geo.CX, MAP[1] + 50, WHITE, ramp(t, s.mark(2), 0.3), size=40)


def d4(ctx, t, s):
    v = country(ctx, t, s, "Tuvalu", 10, 100, "100 km = 62 mi")
    a = ramp(t, s.mark(1) + 0.4, 0.3)
    for i, r in enumerate(SHAPES["Tuvalu"]):
        x, y = v(*r[0])
        rr = 28 + 6 * math.sin(t * 4 + i)
        ctx.new_path()
        ctx.arc(x, y, rr, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.8 * ramp(t, s.mark(1) + 0.4 + i * 0.12, 0.2))
        ctx.set_line_width(4)
        ctx.stroke()
    pill(ctx, "9 ISLANDS", geo.CX, MAP[1] + 50, WHITE, a, size=40)


def d3(ctx, t, s):
    v = country(ctx, t, s, "Nauru", 8.1, 2, "2 km = 1.2 mi")
    ring = SHAPES["Nauru"][0]
    cx = sum(p[0] for p in ring) / len(ring)
    cy = sum(p[1] for p in ring) / len(ring)
    road = [(cx + (p[0] - cx) * 0.86, cy + (p[1] - cy) * 0.86) for p in ring]
    a = ramp(t, s.mark(2), 0.3)
    if a > 0:
        ctx.set_dash([18, 12])
        geo.path(ctx, [road], v)
        ctx.set_source_rgba(0.1, 0.1, 0.12, a)
        ctx.set_line_width(8)
        ctx.stroke()
        ctx.set_dash([])
        # a car driving the loop
        f = ((t - s.mark(2)) / 3.0) % 1.0
        n = len(road)
        i = int(f * n)
        u = f * n - i
        p, q = road[i], road[(i + 1) % n]
        x, y = v(p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)
        ctx.new_path()
        ctx.arc(x, y, 16, 0, 2 * math.pi)
        ctx.set_source_rgba(*PINK, a)
        ctx.fill()
        pill(ctx, "1 ROAD · 12 MILES", geo.CX, MAP[1] + 50, WHITE, a, size=40)


def d2(ctx, t, s):
    v = country(ctx, t, s, "Monaco", 0.8, 1, "1 km = 0.6 mi")
    park(ctx, v, ramp(t, s.mark(2), 0.4))
    pill(ctx, "SMALLER THAN CENTRAL PARK", geo.CX, MAP[1] + 50, WHITE, ramp(t, s.mark(2) + 0.6, 0.3), size=36)


def d1(ctx, t, s):
    v = country(ctx, t, s, "Vatican", 0.19, 1, "1 km = 0.6 mi")
    park(ctx, v, ramp(t, s.mark(2), 0.4))
    pill(ctx, "FITS 7 TIMES", geo.CX, MAP[1] + 50, PINK, ramp(t, s.mark(2) + 0.8, 0.3), size=44)


SEGMENTS = [
    Seg(["These are the five smallest countries on Earth. Number one is tiny."], d_intro,
        {"title": "THE 5 SMALLEST COUNTRIES ON EARTH"}, tail=0.3),
    Seg(["Number five, San Marino.", "Only twenty four square miles.",
         "And it claims to be the oldest republic in the world, founded in the year three oh one."],
        d5, head(5, "San Marino"), sfx=[(1, 1.0, "ding")]),
    Seg(["Number four, Tuvalu.", "Just ten square miles of land, spread over nine tiny islands in the Pacific."],
        d4, head(4, "Tuvalu"), sfx=[(1, 1.0, "ding")]),
    Seg(["Number three, Nauru.", "Eight square miles.", "One road goes around the whole country, and it's only twelve miles long."],
        d3, head(3, "Nauru"), sfx=[(1, 1.0, "ding")]),
    Seg(["Number two, Monaco.", "Less than one square mile.", "It's smaller than Central Park in New York."],
        d2, head(2, "Monaco"), sfx=[(1, 1.0, "ding")]),
    Seg(["And number one, Vatican City.", "About a fifth of a square mile.",
         "Central Park could hold it seven times."],
        d1, head(1, "Vatican City"), sfx=[(1, 1.0, "ding")], tail=0.8),
    Seg(["Which one would you visit? Tell me in the comments."], d_intro,
        {"title": "WHICH ONE WOULD YOU VISIT?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
