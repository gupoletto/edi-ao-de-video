"""Space visuals drawn from scratch with cairo: starfield, stylised planets, real orbit integration."""
import math

import cairo
import numpy as np

from core import AREA, round_rect

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2
_rng = np.random.default_rng(7)
STARS = [(X0 + _rng.random() * (X1 - X0), Y0 + _rng.random() * (Y1 - Y0), _rng.random() * 2 + 0.6, _rng.random() * 6)
         for _ in range(170)]

# name: base colour, band colours (None = solid), extras
PLANETS = {
    "mercury": ((0.62, 0.60, 0.58), None),
    "venus": ((0.93, 0.80, 0.52), [(0.97, 0.88, 0.65), (0.86, 0.70, 0.42)]),
    "earth": ((0.16, 0.42, 0.85), None),
    "moon": ((0.72, 0.72, 0.74), None),
    "mars": ((0.80, 0.36, 0.20), None),
    "jupiter": ((0.85, 0.72, 0.55), [(0.93, 0.85, 0.72), (0.72, 0.52, 0.35), (0.88, 0.78, 0.62), (0.66, 0.45, 0.30)]),
    "saturn": ((0.90, 0.80, 0.58), [(0.95, 0.88, 0.70), (0.80, 0.68, 0.46)]),
    "uranus": ((0.55, 0.85, 0.88), None),
    "neptune": ((0.22, 0.40, 0.90), [(0.30, 0.50, 0.95), (0.18, 0.32, 0.80)]),
    "pluto": ((0.78, 0.66, 0.55), None),
    "ganymede": ((0.58, 0.54, 0.50), None),
}


def sky(ctx, t=0.0):
    round_rect(ctx, X0, Y0, X1 - X0, Y1 - Y0, 36)
    ctx.set_source_rgb(0.02, 0.025, 0.06)
    ctx.fill_preserve()
    ctx.clip()
    for x, y, r, ph in STARS:
        a = 0.45 + 0.45 * math.sin(t * 1.7 + ph)
        ctx.set_source_rgba(1, 1, 1, a)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.fill()


def planet(ctx, name, x, y, r, spin=0.0, light=(-0.55, -0.45)):
    """Shaded sphere with bands/features; spin shifts features for rotation."""
    base, bands = PLANETS[name]
    ctx.save()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.clip()
    ctx.set_source_rgb(*base)
    ctx.paint()
    if bands:
        n = 9
        for i in range(n):
            ctx.set_source_rgba(*bands[i % len(bands)], 0.85)
            yy = y - r + (i + 0.5 * math.sin(i * 1.3)) * 2 * r / n
            ctx.rectangle(x - r, yy, 2 * r, 2 * r / n * 0.55)
            ctx.fill()
    rng = np.random.default_rng(len(name))
    if name == "earth":
        for _ in range(7):
            u, v, s = rng.random() * 2 - 1, rng.random() * 1.6 - 0.8, 0.18 + rng.random() * 0.25
            px = x + ((u + spin) % 2 - 1) * r
            ctx.set_source_rgb(0.22, 0.62, 0.30)
            ctx.save()
            ctx.translate(px, y + v * r)
            ctx.scale(1.4, 1)
            ctx.arc(0, 0, s * r, 0, 2 * math.pi)
            ctx.restore()
            ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.55)
        for k in range(4):
            ctx.rectangle(x - r, y - r * 0.7 + k * r * 0.45, 2 * r, r * 0.06)
            ctx.fill()
    elif name in ("moon", "mercury", "ganymede", "pluto"):
        for _ in range(14):
            u, v, s = rng.random() * 2 - 1, rng.random() * 2 - 1, 0.05 + rng.random() * 0.14
            px = x + ((u + spin) % 2 - 1) * r
            ctx.set_source_rgba(0, 0, 0, 0.16)
            ctx.arc(px, y + v * r, s * r, 0, 2 * math.pi)
            ctx.fill()
        if name == "pluto":  # the bright "heart"
            ctx.set_source_rgba(0.96, 0.92, 0.86, 0.85)
            ctx.arc(x + 0.15 * r, y + 0.15 * r, 0.35 * r, 0, 2 * math.pi)
            ctx.fill()
    elif name == "mars":
        ctx.set_source_rgba(1, 1, 1, 0.8)
        ctx.arc(x, y - r * 1.02, r * 0.35, 0, 2 * math.pi)
        ctx.fill()
        for _ in range(6):
            u, v = rng.random() * 2 - 1, rng.random() * 1.4 - 0.7
            ctx.set_source_rgba(0.45, 0.18, 0.10, 0.45)
            ctx.arc(x + ((u + spin) % 2 - 1) * r, y + v * r, r * (0.1 + rng.random() * 0.2), 0, 2 * math.pi)
            ctx.fill()
    elif name == "jupiter":
        gx = x + (((0.3 + spin) % 2) - 1) * r
        ctx.save()
        ctx.translate(gx, y + r * 0.32)
        ctx.scale(1.6, 1)
        ctx.arc(0, 0, r * 0.13, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(0.78, 0.33, 0.22)
        ctx.fill()
    # day/night shading
    g = cairo.RadialGradient(x + light[0] * r, y + light[1] * r, r * 0.1, x, y, r * 1.05)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.18)
    g.add_color_stop_rgba(0.55, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.62)
    ctx.set_source(g)
    ctx.paint()
    ctx.restore()


def saturn_rings(ctx, x, y, r, front):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, 0.32)
    ctx.set_line_width(r * 0.28)
    ctx.set_source_rgba(0.85, 0.76, 0.55, 0.8)
    if front:
        ctx.arc(0, 0, r * 1.75, 0, math.pi)
    else:
        ctx.arc(0, 0, r * 1.75, math.pi, 2 * math.pi)
    ctx.restore()
    ctx.stroke()


def thermometer(ctx, x, y0, y1, frac, color):
    """Vertical gauge; frac 0..1 of the tube filled."""
    ctx.set_source_rgba(1, 1, 1, 0.18)
    round_rect(ctx, x - 22, y0, 44, y1 - y0, 22)
    ctx.fill()
    ctx.arc(x, y1 + 20, 40, 0, 2 * math.pi)
    ctx.set_source_rgb(*color)
    ctx.fill()
    h = (y1 - y0 - 16) * max(0.02, min(1, frac))
    round_rect(ctx, x - 13, y1 - h, 26, h + 10, 13)
    ctx.fill()


def orbit_sim(radii, days, steps_per_day=48):
    """Moons on circular starts around Earth, integrated with velocity-Verlet in SI units.
    Returns array [len(radii), steps, 2] of positions (m)."""
    gm = 3.986004e14
    dt = 86400 / steps_per_day
    n = int(days * steps_per_day) + 1
    out = np.zeros((len(radii), n, 2))
    for k, r in enumerate(radii):
        p = np.array([r, 0.0])
        v = np.array([0.0, math.sqrt(gm / r)])
        a = -gm * p / np.linalg.norm(p) ** 3
        for i in range(n):
            out[k, i] = p
            p = p + v * dt + 0.5 * a * dt * dt
            a2 = -gm * p / np.linalg.norm(p) ** 3
            v = v + 0.5 * (a + a2) * dt
            a = a2
    return out, steps_per_day
