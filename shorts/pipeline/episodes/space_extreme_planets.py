"""The 5 most extreme planets in our solar system (#5 -> #1). Wed 28/10/2026, topic: space, format: ranking.

Facts (NASA planetary fact sheets): Olympus Mons ~22 km (Everest 8.85 km); Neptune winds > 2,000 km/h
(~1,200 mph); Great Red Spot wider than Earth, observed since the 1800s; Mercury 430 °C day / -180 °C night
(800 °F / -290 °F); Venus ~465 °C (~870 °F), surface pressure ~92x Earth's.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import space as sp  # noqa: E402
from core import BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, text_center  # noqa: E402

DOTS = ["5", "4", "3", "2", "1"]
CX, CY = sp.CX, sp.CY


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def stat(ctx, s, a, y=1330, color=YELLOW, size=58):
    text_center(ctx, s, CX, y, size, color, "ExtraBold", alpha=a)


def d_intro(ctx, t, s):
    sp.sky(ctx, t)
    for i, (n, r) in enumerate([("mars", 70), ("neptune", 95), ("jupiter", 150), ("mercury", 55), ("venus", 90)]):
        ang = t * 0.25 + i * 2 * math.pi / 5
        sp.planet(ctx, n, CX + 290 * math.cos(ang), CY + 290 * math.sin(ang), r, spin=t * 0.1)


def d5(ctx, t, s):  # Mars: Olympus Mons vs Everest
    sp.sky(ctx, t)
    sp.planet(ctx, "mars", CX, sp.Y0 + 170, 120, spin=t * 0.05)
    base = sp.Y1 - 120
    k = 22  # px per km
    g = ramp(t, s.mark(1), 1.4)
    for x, km, rgb, label in ((250, 8.85, (0.75, 0.78, 0.85), "EVEREST 8.8 km"), (720, 21.9, (0.82, 0.38, 0.22), "OLYMPUS MONS 22 km")):
        h = km * k * (g if km > 10 else min(1, g * 2.5))
        ctx.move_to(x - h * 0.6, base)
        ctx.line_to(x, base - h)
        ctx.line_to(x + h * 0.6, base)
        ctx.close_path()
        ctx.set_source_rgb(*rgb)
        ctx.fill()
        text_center(ctx, label, x, base + 60, 34, WHITE, alpha=ramp(t, s.mark(1) + 0.6, 0.4))
    ctx.set_source_rgba(1, 1, 1, 0.3)
    ctx.rectangle(sp.X0, base, sp.X1 - sp.X0, 3)
    ctx.fill()


def d4(ctx, t, s):  # Neptune winds
    sp.sky(ctx, t)
    sp.planet(ctx, "neptune", CX, CY - 40, 260, spin=t * 0.6)
    ctx.set_line_width(5)
    for i in range(14):
        y = CY - 260 + i * 38
        off = ((t * 900 + i * 137) % 1300) - 400
        ctx.set_source_rgba(1, 1, 1, 0.55)
        ctx.move_to(sp.X0 + off, y)
        ctx.line_to(sp.X0 + off + 160, y)
        ctx.stroke()
    v = int(1200 * ramp(t, s.mark(1), 1.6))
    stat(ctx, f"{v:,} MPH", ramp(t, s.mark(1), 0.3))


def d3(ctx, t, s):  # Jupiter's Great Red Spot vs Earth (spot ~1.3 Earth diameters wide)
    sp.sky(ctx, t)
    zoom = ramp(t, s.mark(1), 1.5)
    r = 330 + 900 * zoom
    sp.planet(ctx, "jupiter", CX, CY - zoom * r * 0.32, r, spin=0.7)  # spin 0.7 puts the spot mid-disc
    spot_y = CY - zoom * r * 0.32 + r * 0.32
    a = ramp(t, s.mark(1) + 1.2, 0.5)
    if a > 0:
        re = r * 0.13 * 1.6 / 1.3
        ctx.push_group()
        sp.planet(ctx, "earth", CX, spot_y, re)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(a * 0.92)
        text_center(ctx, "EARTH", CX, spot_y + re + 50, 34, WHITE, alpha=a)
    stat(ctx, "WIDER THAN EARTH", a)


def d2(ctx, t, s):  # Mercury: day/night temperature swing
    sp.sky(ctx, t)
    swing = 0.5 + 0.5 * math.sin((t - s.mark(1)) * 1.6) if t > s.mark(1) else 1.0
    lx = -0.9 + 1.8 * swing
    sp.planet(ctx, "mercury", CX - 120, CY - 40, 250, light=(lx * -1, -0.3))
    hot = swing
    color = (1.0, 0.35 + 0.4 * (1 - hot), 0.2 + 0.7 * (1 - hot))
    sp.thermometer(ctx, 880, sp.Y0 + 90, sp.Y1 - 210, 0.08 + 0.9 * hot, color)
    deg = int(-290 + (800 + 290) * hot)
    stat(ctx, f"{deg:+,}°F", 1.0, color=color)


def d1(ctx, t, s):  # Venus: hottest planet, crushing pressure
    sp.sky(ctx, t)
    sp.planet(ctx, "venus", CX - 110, CY - 40, 270, spin=t * 0.2)
    ctx.save()
    ctx.arc(CX - 110, CY - 40, 270, 0, 2 * math.pi)
    ctx.clip()
    for i in range(8):
        ctx.set_source_rgba(1, 0.95, 0.8, 0.18)
        x = CX - 380 + ((t * 70 + i * 90) % 560)
        ctx.save()
        ctx.translate(x, CY - 260 + i * 60)
        ctx.scale(3, 1)
        ctx.arc(0, 0, 30, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
    ctx.restore()
    heat = ramp(t, s.mark(1), 1.5)
    sp.thermometer(ctx, 880, sp.Y0 + 90, sp.Y1 - 210, 0.1 + 0.9 * heat, (1.0, 0.35, 0.2))
    stat(ctx, f"{int(870 * heat)}°F", ramp(t, s.mark(1), 0.3), color=(1.0, 0.45, 0.3))
    stat(ctx, "92x EARTH'S PRESSURE", ramp(t, s.mark(2), 0.3), y=sp.Y0 + 70, color=WHITE, size=44)


def d_outro(ctx, t, s):
    d_intro(ctx, t + 3, s)


SEGMENTS = [
    Seg(["These are the five most extreme planets in our solar system."], d_intro,
        {"title": "THE 5 MOST EXTREME PLANETS"}, tail=0.3),
    Seg(["Number five, Mars.", "It has Olympus Mons, a volcano about fourteen miles high. That's two and a half Everests!"],
        d5, head(5, "MARS"), sfx=[(1, 0.6, "ding")]),
    Seg(["Number four, Neptune.", "Its winds blow faster than twelve hundred miles per hour, the fastest in the solar system."],
        d4, head(4, "NEPTUNE"), sfx=[(1, 1.6, "ding")]),
    Seg(["Number three, Jupiter.", "Its Great Red Spot is a storm wider than the entire Earth, raging for well over a century."],
        d3, head(3, "JUPITER"), sfx=[(1, 1.4, "ding")]),
    Seg(["Number two, Mercury.", "Days hit eight hundred degrees Fahrenheit. Nights drop to minus two ninety."],
        d2, head(2, "MERCURY"), sfx=[(1, 0.5, "ding")]),
    Seg(["And number one, Venus.", "It's the hottest planet, around eight hundred seventy degrees, hot enough to melt lead.",
         "And the air pressure is ninety-two times stronger than on Earth."],
        d1, head(1, "VENUS"), sfx=[(1, 1.5, "ding")], tail=0.8),
    Seg(["Which planet would you visit first? Tell me in the comments."], d_outro,
        {"title": "WHICH ONE WOULD YOU VISIT?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
