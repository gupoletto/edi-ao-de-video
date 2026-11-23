"""What if the Moon were twice as close? Wed 28/10/2026, topic: space, format: what if (simulation).

Physics: angular size ∝ 1/d -> 2x wider (4x area). Tidal force ∝ M/d³ -> 8x. Orbit integrated numerically
(velocity-Verlet, GM_earth = 3.986e14): period ∝ d^1.5 -> 27.3 d / 2^1.5 ≈ 9.7 days.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import space as sp  # noqa: E402
from core import BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, text_center  # noqa: E402

CX, CY = sp.CX, sp.CY
R_NOW, R_HALF = 3.844e8, 1.922e8
ORBITS, SPD = sp.orbit_sim([R_NOW, R_HALF], days=28)
SCALE = 410 / R_NOW


def stat(ctx, s, a, y=1330, color=YELLOW, size=54):
    text_center(ctx, s, CX, y, size, color, "ExtraBold", alpha=a)


def d_hook(ctx, t, s):
    sp.sky(ctx, t)
    # night sky over a horizon, the Moon grows to twice its width
    g = ramp(t, 0.6, 1.6)
    r = 70 * (1 + g)
    sp.planet(ctx, "moon", CX, sp.Y0 + 380, r, light=(0.2, -0.2))
    ctx.set_source_rgb(0.04, 0.06, 0.10)
    ctx.move_to(sp.X0, sp.Y1 - 230)
    for i in range(9):
        ctx.line_to(sp.X0 + (i + 1) * 120, sp.Y1 - 230 - 50 * math.sin(i * 1.9) ** 2)
    ctx.line_to(sp.X1, sp.Y1)
    ctx.line_to(sp.X0, sp.Y1)
    ctx.close_path()
    ctx.fill()


def d_sky(ctx, t, s):
    sp.sky(ctx, t)
    for x, r, label, c in ((330, 75, "TODAY", WHITE), (740, 150, "TWICE AS CLOSE", YELLOW)):
        a = 1 if r < 100 else ramp(t, s.mark(0) + 0.6, 0.5)
        ctx.push_group()
        sp.planet(ctx, "moon", x, CY - 60, r, light=(0.2, -0.2))
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(a)
        text_center(ctx, label, x, CY + 180, 36, c, alpha=a)
    stat(ctx, "2x WIDER · 4x THE AREA", ramp(t, s.mark(1), 0.4))


def d_orbit(ctx, t, s):
    sp.sky(ctx, t)
    start = s.mark(1)
    days = max(0.0, min(27.3, (t - start) * 2.6))
    i = int(days * SPD)
    ctx.set_line_width(3)
    for r, c in ((R_NOW, (1, 1, 1, 0.3)), (R_HALF, (1, 0.85, 0.25, 0.45))):
        ctx.set_source_rgba(*c)
        ctx.arc(CX, CY - 40, r * SCALE, 0, 2 * math.pi)
        ctx.stroke()
    sp.planet(ctx, "earth", CX, CY - 40, 55, spin=days * 0.6)
    for k, (name, rad, c) in enumerate((("today", 24, WHITE), ("close", 30, YELLOW))):
        x, y = ORBITS[k, i]
        sp.planet(ctx, "moon", CX + x * SCALE, CY - 40 - y * SCALE, rad)
    laps = ORBITS[1, :i + 1]
    ang = math.atan2(laps[-1, 1], laps[-1, 0]) % (2 * math.pi) if i else 0
    text_center(ctx, f"DAY {days:4.1f}", CX, sp.Y0 + 70, 52, WHITE, "ExtraBold")
    done = days / (27.3 / 2 ** 1.5)
    stat(ctx, f"CLOSE MOON: {done:.1f} ORBITS", ramp(t, start, 0.3), color=YELLOW, size=46)


def d_tides(ctx, t, s):
    sp.sky(ctx, t)
    k = ramp(t, s.mark(0) + 0.8, 1.2)
    stretch = 1 + 0.06 + 0.42 * k  # bulge (exaggerated for the eye)
    ctx.save()
    ctx.translate(CX, CY - 60)
    ctx.scale(stretch, 1 / math.sqrt(stretch))
    ctx.arc(0, 0, 230, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgba(0.25, 0.55, 1.0, 0.45)
    ctx.fill()
    sp.planet(ctx, "earth", CX, CY - 60, 200, spin=t * 0.3)
    sp.planet(ctx, "moon", sp.X1 - 70, CY - 60, 40 + 12 * k)
    text_center(ctx, "1x", CX, sp.Y0 + 80, 64, WHITE, "ExtraBold", alpha=1 - k)
    text_center(ctx, "8x TIDAL PULL", CX, sp.Y0 + 80, 64, PINK, "ExtraBold", alpha=k)
    stat(ctx, "BULGE NOT TO SCALE", 0.6 * k, size=30, color=WHITE, y=sp.Y1 - 40)


def d_outro(ctx, t, s):
    d_hook(ctx, t + 2.5, s)


SEGMENTS = [
    Seg(["What if the Moon were twice as close?"], d_hook, {"title": "WHAT IF THE MOON WERE 2x CLOSER?"}, tail=0.4),
    Seg(["First, it would look twice as wide in the sky.", "That's four times the glowing area every night."],
        d_sky, {"big": "BIGGER", "big_size": 96, "sub": "IN THE NIGHT SKY", "color": BLUE}, sfx=[(1, 0, "ding")]),
    Seg(["Second, it would race around us. Here's a real gravity simulation.", 0.3,
         "The closer Moon finishes an orbit in under ten days, instead of twenty-seven."],
        d_orbit, {"big": "FASTER", "big_size": 96, "sub": "REAL GRAVITY SIMULATION", "color": BLUE},
        sfx=[(2, 0.5, "ding")], tail=1.4),
    Seg(["And third, its tidal pull would be eight times stronger, because tides drop with distance cubed.",
         "Coastlines would see enormous tides, twice a day."],
        d_tides, {"big": "TIDES", "big_size": 96, "sub": "8 TIMES STRONGER", "color": PINK}, sfx=[(0, 1.6, "ding")]),
    Seg(["Would you still go to the beach? Tell me below."], d_outro,
        {"title": "WOULD YOU STILL GO TO THE BEACH?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
