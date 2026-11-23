"""The 5 hottest things in the universe we know, ranked (#5 -> #1). Thu 12/11/2026, topic: how it works / physics,
format: ranking (twist: #1 was made by humans).

Temperatures (rounded, commonly cited):
- #5 surface of Venus ~465 C (~870 F), hotter than Mercury despite being farther from the Sun (greenhouse effect);
- #4 surface of the Sun (photosphere) ~5,500 C (~10,000 F);
- #3 a lightning bolt's channel ~30,000 C (~54,000 F), about five times the Sun's surface;
- #2 the Sun's core ~15 million C;
- #1 quark-gluon plasma made by smashing lead nuclei at CERN's Large Hadron Collider: ~5.5 trillion C (ALICE, 2012),
  the hottest temperature ever made, for a tiny fraction of a second.
The thermometer is on a log scale (each mark is 10x the previous).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import AREA, BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, round_rect, text_center  # noqa: E402

X0, Y0, X1, Y1 = AREA
DOTS = ["5", "4", "3", "2", "1"]
TX, TY0, TY1 = X0 + 120, Y1 - 110, Y0 + 170     # termômetro: base e topo
LMIN, LMAX = 2.0, 13.0                           # log10 de 100 C a 10 trilhões C


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def y_de(temp):
    return TY0 - (TY0 - TY1) * (math.log10(temp) - LMIN) / (LMAX - LMIN)


def fundo(ctx):
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.set_source_rgb(0.06, 0.05, 0.09)
    ctx.fill()


def termometro(ctx, temp, a=1.0):
    round_rect(ctx, TX - 22, TY1 - 20, 44, TY0 - TY1 + 40, 22)
    ctx.set_source_rgba(1, 1, 1, 0.15)
    ctx.fill()
    ctx.arc(TX, TY0 + 30, 40, 0, 2 * math.pi)
    ctx.set_source_rgb(0.95, 0.25, 0.2)
    ctx.fill()
    y = y_de(max(100.0, temp))
    ctx.rectangle(TX - 12, y, 24, TY0 + 10 - y)
    ctx.fill()
    for e in range(2, 14):
        yy = y_de(10 ** e)
        ctx.set_source_rgba(1, 1, 1, 0.5)
        ctx.rectangle(TX + 26, yy - 1, 18 if e % 3 == 0 else 10, 2)
        ctx.fill()
        if e % 3 == 0:
            rot = {3: "1,000", 6: "1 million", 9: "1 billion", 12: "1 trillion"}[e]
            text_center(ctx, rot, TX + 110, yy + 8, 20, WHITE, "SemiBold", alpha=0.7)


def fmt(t):
    if t >= 1e12:
        return f"{t / 1e12:.1f} TRILLION °C"
    if t >= 1e6:
        return f"{t / 1e6:.0f} MILLION °C"
    return f"{t:,.0f} °C"


# ---------------- ícones ----------------

def venus(ctx, cx, cy, t):
    import cairo
    g = cairo.RadialGradient(cx - 50, cy - 50, 20, cx, cy, 170)
    g.add_color_stop_rgb(0, 1.0, 0.85, 0.55)
    g.add_color_stop_rgb(1, 0.75, 0.45, 0.15)
    ctx.arc(cx, cy, 170, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.18)
    for k in range(5):
        ctx.rectangle(cx - 170, cy - 120 + k * 55 + 8 * math.sin(t + k), 340, 18)
    ctx.save()
    ctx.arc(cx, cy, 170, 0, 2 * math.pi)
    ctx.clip()
    ctx.fill()
    ctx.restore()


def sol(ctx, cx, cy, t, nucleo=False):
    import cairo
    g = cairo.RadialGradient(cx, cy, 20, cx, cy, 190)
    g.add_color_stop_rgb(0, 1.0, 0.98, 0.8)
    g.add_color_stop_rgb(0.7, 1.0, 0.75, 0.2)
    g.add_color_stop_rgb(1, 0.95, 0.4, 0.1)
    ctx.arc(cx, cy, 190, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    if nucleo:  # corte em fatia mostrando o núcleo
        ctx.move_to(cx, cy)
        ctx.arc(cx, cy, 190, -math.pi / 2, 0)
        ctx.close_path()
        ctx.set_source_rgb(0.98, 0.55, 0.15)
        ctx.fill()
        ctx.move_to(cx, cy)
        ctx.arc(cx, cy, 70, -math.pi / 2, 0)
        ctx.close_path()
        ctx.set_source_rgb(1, 1, 0.92)
        ctx.fill()
        text_center(ctx, "CORE", cx + 40, cy - 20, 26, (0.4, 0.2, 0.05), "ExtraBold")


def raio(ctx, cx, cy, t):
    pts = [(cx + 30, cy - 220), (cx - 40, cy - 60), (cx + 20, cy - 50), (cx - 60, cy + 120), (cx + 10, cy + 110),
           (cx - 30, cy + 230)]
    pisca = 0.6 + 0.4 * (math.sin(t * 23) > -0.2)
    for w, a in ((40, 0.15), (18, 0.4), (8, 1.0)):
        ctx.set_source_rgba(0.85, 0.9, 1.0, a * pisca)
        ctx.set_line_width(w)
        ctx.set_line_join(1)
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.stroke()


def colisor(ctx, cx, cy, t):
    ctx.set_source_rgba(0.4, 0.7, 1.0, 0.8)
    ctx.set_line_width(14)
    ctx.arc(cx, cy, 170, 0, 2 * math.pi)
    ctx.stroke()
    for s in (1, -1):  # dois feixes girando em sentidos opostos
        a = s * t * 3
        x, y = cx + 170 * math.cos(a), cy + 170 * math.sin(a)
        ctx.arc(x, y, 14, 0, 2 * math.pi)
        ctx.set_source_rgb(1, 0.9, 0.4)
        ctx.fill()
    flash = max(0.0, math.sin(t * 3)) ** 8
    ctx.arc(cx + 170, cy, 30 + 60 * flash, 0, 2 * math.pi)
    ctx.set_source_rgba(1, 0.6, 0.9, 0.8 * flash)
    ctx.fill()
    text_center(ctx, "LHC · CERN", cx, cy + 10, 34, WHITE, "ExtraBold")


def cena(icone, temp, nota):
    def draw(ctx, t, s):
        fundo(ctx)
        k = ease((t - s.mark(1)) / 1.2) if len(s.items) > 1 else 1.0
        termometro(ctx, 10 ** (LMIN + (math.log10(temp) - LMIN) * k))
        icone(ctx, X0 + 560, Y0 + 430, t)
        text_center(ctx, fmt(temp * k if k < 1 else temp), X0 + 560, Y1 - 150, 52, YELLOW, "ExtraBold",
                    alpha=ramp(t, s.mark(1) if len(s.items) > 1 else 0, 0.3))
        text_center(ctx, nota, X0 + 560, Y1 - 95, 28, WHITE, "Bold", alpha=ramp(t, (s.mark(1) if len(s.items) > 1 else 0) + 1.2, 0.3))
    return draw


def d_intro(ctx, t, s):
    fundo(ctx)
    termometro(ctx, 10 ** (LMIN + (LMAX - 0.3 - LMIN) * ease(t / 2.5)))
    sol(ctx, X0 + 560, Y0 + 430, t)


SEGMENTS = [
    Seg(["The hottest things we know. Number one was made by humans."], d_intro,
        {"title": "5 HOTTEST THINGS IN THE UNIVERSE"}, tail=0.2),
    Seg(["Number five, the surface of Venus.", "Four hundred sixty five degrees, hot enough to melt lead."],
        cena(venus, 465, "HOTTER THAN MERCURY"), head(5, "VENUS"), sfx=[(1, 0, "ding")]),
    Seg(["Number four, the surface of the Sun.", "About five thousand five hundred degrees."],
        cena(sol, 5500, "~10,000 °F"), head(4, "THE SUN'S SURFACE"), sfx=[(1, 0, "ding")]),
    Seg(["Number three, a lightning bolt.", "Thirty thousand degrees. Five times hotter than the Sun's surface!"],
        cena(raio, 30000, "5x THE SUN'S SURFACE"), head(3, "LIGHTNING"), sfx=[(1, 0, "whoosh")]),
    Seg(["Number two, the core of the Sun.", "Fifteen million degrees."],
        cena(lambda c, x, y, t: sol(c, x, y, t, nucleo=True), 15e6, "WHERE FUSION HAPPENS"), head(2, "THE SUN'S CORE"),
        sfx=[(1, 0, "ding")]),
    Seg(["And number one, made by humans.", "Smashing atoms at CERN hit five and a half trillion degrees."],
        cena(colisor, 5.5e12, "FOR A TINY FRACTION OF A SECOND"), head(1, "PARTICLE COLLIDER"), sfx=[(1, 0, "whoosh")],
        tail=0.7),
]
SEGMENTS.append(pq.seg_pergunta("Which one surprised you the most?", "WHICH ONE SURPRISED YOU?",
                                fundo=lambda ctx, t, s: d_intro(ctx, 9.0, s)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
