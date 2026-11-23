"""How many Earths fit inside the Sun? Sat 31/10/2026, topic: size comparison, format: why/how.

Mean radii (NASA fact sheets): Earth 6,371 km, Jupiter 69,911 km, Sun 695,700 km.
Diameter ratios: Jupiter/Earth = 11.0, Sun/Earth = 109.2. Volume ratios: Jupiter/Earth = 1,321;
Sun/Earth = 1.30 million; Sun/Jupiter = 991 (about a thousand).
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import space as sp  # noqa: E402
from core import BLUE, PINK, WHITE, YELLOW, Seg, pill, ramp, render, text_center  # noqa: E402

CX, CY = sp.CX, sp.CY
_rng = np.random.default_rng(11)


def contador(ctx, valor, y=sp.Y1 - 90, cor=YELLOW, a=1.0):
    text_center(ctx, valor, CX, y, 84, cor, "ExtraBold", alpha=a)


def enchendo(ctx, x, y, R, r, k, n_vis):
    """Pontinhos-Terra enchendo um disco de raio R, de baixo para cima, até a fração k."""
    pts = _pontos(R, r)
    m = int(len(pts) * k)
    for px, py in pts[:m][:n_vis]:
        ctx.arc(x + px, y + py, r * 0.9, 0, 2 * math.pi)
        ctx.new_sub_path()
    ctx.set_source_rgb(0.25, 0.55, 0.95)
    ctx.fill()


_cache = {}


def _pontos(R, r):
    if (R, r) not in _cache:
        pts = []
        passo = 2 * r
        y = R - r
        while y > -R:
            x = -R + r
            while x < R:
                if x * x + y * y <= (R - r) ** 2:
                    pts.append((x, y))
                x += passo
            y -= passo * 0.87
        _cache[(R, r)] = pts
    return _cache[(R, r)]


def d_intro(ctx, t, s):
    sp.sky(ctx, t)
    sp.planet(ctx, "sun", CX, CY + 520, 760)
    sp.planet(ctx, "earth", CX, CY - 260, 26, spin=t * 0.2)
    text_center(ctx, "?", CX, CY - 120, 120, WHITE, "ExtraBold", alpha=ramp(t, 0.8, 0.3))


def d_jupiter(ctx, t, s):
    sp.sky(ctx, t)
    R = 360
    sp.planet(ctx, "jupiter", CX, CY - 40, R, spin=t * 0.1)
    k = ramp(t, s.mark(1), 2.6)
    ctx.push_group()
    enchendo(ctx, CX, CY - 40, R, R / 11.0, k, 10 ** 9)  # Terras no tamanho real (um corte do volume)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(0.9)
    contador(ctx, f"{int(1321 * k):,}", a=ramp(t, s.mark(1), 0.3))
    pill(ctx, "BY VOLUME", CX, sp.Y0 + 70, WHITE, ramp(t, s.mark(1), 0.3), size=36)


def d_sol_largura(ctx, t, s):
    sp.sky(ctx, t)
    R = 470
    sp.planet(ctx, "sun", CX, CY - 40, R)
    k = ramp(t, s.mark(0) + 0.6, 2.2)
    n = int(109 * k)
    r = R / 109.2
    for i in range(n):  # 109 Terras atravessando o diâmetro
        ctx.arc(CX - R + r + i * 2 * r, CY - 40, r * 0.95, 0, 2 * math.pi)
        ctx.new_sub_path()
    ctx.set_source_rgb(0.25, 0.55, 0.95)
    ctx.fill()
    contador(ctx, f"{n} EARTHS ACROSS", a=ramp(t, s.mark(0) + 0.6, 0.3))


def d_sol_volume(ctx, t, s):
    sp.sky(ctx, t)
    R = 470
    sp.planet(ctx, "sun", CX, CY - 40, R)
    k = ramp(t, s.mark(0) + 0.3, 3.0) ** 2
    ctx.push_group()
    enchendo(ctx, CX, CY - 40, R, 4.5, k, 10 ** 9)  # cada ponto aqui vale muitas Terras: é só a ideia de encher
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(0.85)
    v = 1_300_000 * k
    contador(ctx, f"{v / 1e6:.1f} MILLION" if v >= 1e6 else f"{int(v):,}", a=ramp(t, s.mark(0) + 0.3, 0.3))
    pill(ctx, "BY VOLUME", CX, sp.Y0 + 70, WHITE, ramp(t, s.mark(0) + 0.5, 0.3), size=36)


def d_sol_jupiter(ctx, t, s):
    sp.sky(ctx, t)
    R = 470
    sp.planet(ctx, "sun", CX, CY - 40, R)
    sp.planet(ctx, "jupiter", CX + R + 10 - R / 9.95, CY - 40, R / 9.95, spin=t * 0.1)
    contador(ctx, "~1,000 JUPITERS", cor=PINK, a=ramp(t, s.mark(0) + 1.0, 0.3))


def d_outro(ctx, t, s):
    d_intro(ctx, t + 2, s)


SEGMENTS = [
    Seg(["How many Earths would fit inside the Sun? Let's start smaller."], d_intro,
        {"title": "HOW MANY EARTHS FIT IN THE SUN?"}, tail=0.2),
    Seg(["Jupiter is eleven Earths wide.", "So, by volume, about one thousand three hundred Earths fit inside it."],
        d_jupiter, {"big": "JUPITER", "big_size": 110, "sub": "11 EARTHS WIDE"}, sfx=[(1, 2.6, "ding")]),
    Seg(["Now the Sun. One hundred nine Earths, lined up, just to cross it."], d_sol_largura,
        {"big": "THE SUN", "big_size": 110, "sub": "109 EARTHS WIDE", "color": YELLOW}, sfx=[(0, 2.8, "ding")]),
    Seg(["Fill it up, and you get about one point three million Earths."], d_sol_volume,
        {"big": "1.3 MILLION", "big_size": 110, "sub": "EARTHS INSIDE THE SUN", "color": YELLOW},
        sfx=[(0, 3.3, "ding")], tail=0.8),
    Seg(["Even Jupiter is tiny. The Sun could swallow about a thousand of them."], d_sol_jupiter,
        {"big": "JUPITER?", "big_size": 110, "sub": "STILL TINY", "color": PINK}, sfx=[(0, 1.0, "ding")]),
    Seg(["What's the biggest thing you can imagine? Tell me in the comments!"], d_outro,
        {"title": "WHAT'S BIGGER THAN THE SUN?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
