"""Which is deeper? 4-round quiz about Earth's deepest places. Fri 06/11/2026, topic: Earth & nature, format: interactive.

Facts (to scale in the bars):
- Grand Canyon: up to ~1,857 m (6,093 ft) deep; Burj Khalifa: 828 m tall -> the canyon is ~2.2x deeper;
- Mariana Trench, Challenger Deep: ~10,935 m; Mount Everest: 8,849 m -> Everest would sit ~2 km under the surface;
- Kola Superdeep Borehole (Russia, drilled 1970-1989): 12,262 m, the deepest hole humans ever made, only ~23 cm wide
  -> deeper than the Mariana Trench (the "trick" round);
- Veryovkina Cave (Georgia/Abkhazia), deepest known cave: ~2,212 m -> deeper than the Grand Canyon.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import AREA, BLUE, GREEN, PINK, WHITE, YELLOW, Seg, ramp, render, round_rect, text_center  # noqa: E402
from quiz import answer, countdown, question  # noqa: E402

X0, Y0, X1, Y1 = AREA
BASE, HMAX, BW = 1150, 520, 230
XA, XB = 330, 750
ROCHA, AGUA, PEDRA, ACO = (0.62, 0.42, 0.28), (0.20, 0.50, 0.85), (0.60, 0.63, 0.68), (0.75, 0.80, 0.88)
N = 4

RODADAS = [  # (nome A, metros A, cor A, ícone A, nome B, metros B, cor B, ícone B)
    ("GRAND CANYON", 1857, ROCHA, "canyon", "BURJ KHALIFA", 828, ACO, "torre"),
    ("MARIANA TRENCH", 10935, AGUA, "onda", "MOUNT EVEREST", 8849, PEDRA, "monte"),
    ("DEEPEST HOLE EVER DUG", 12262, ROCHA, "broca", "MARIANA TRENCH", 10935, AGUA, "onda"),
    ("DEEPEST CAVE", 2212, ROCHA, "caverna", "GRAND CANYON", 1857, ROCHA, "canyon"),
]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def painel(ctx):
    round_rect(ctx, X0, Y0, X1 - X0, Y1 - Y0, 36)
    ctx.set_source_rgb(0.07, 0.08, 0.13)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.08)  # linhas de grade
    for k in range(1, 5):
        y = BASE - HMAX * k / 4
        ctx.rectangle(X0 + 40, y, X1 - X0 - 80, 2)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.5)
    ctx.rectangle(X0 + 40, BASE, X1 - X0 - 80, 4)
    ctx.fill()


def icone(ctx, tipo, x, y, s=46, cor=WHITE):
    ctx.save()
    ctx.translate(x, y)
    ctx.set_source_rgb(*cor)
    ctx.set_line_width(6)
    if tipo == "monte":
        ctx.move_to(-s, s * 0.6); ctx.line_to(-s * 0.2, -s * 0.7); ctx.line_to(s * 0.15, -s * 0.1)
        ctx.line_to(s * 0.4, -s * 0.4); ctx.line_to(s, s * 0.6); ctx.close_path(); ctx.fill()
    elif tipo == "torre":
        ctx.move_to(-s * 0.35, s * 0.6); ctx.line_to(-s * 0.12, -s * 0.9); ctx.line_to(0, -s * 1.2)
        ctx.line_to(s * 0.12, -s * 0.9); ctx.line_to(s * 0.35, s * 0.6); ctx.close_path(); ctx.fill()
    elif tipo == "onda":
        ctx.move_to(-s, 0)
        for k in range(9):
            xx = -s + k * s / 4
            ctx.curve_to(xx + s / 12, -s * 0.35, xx + s / 6, -s * 0.35, xx + s / 4, 0)
        ctx.stroke()
        ctx.move_to(-s, s * 0.4)
        for k in range(9):
            xx = -s + k * s / 4
            ctx.curve_to(xx + s / 12, s * 0.05, xx + s / 6, s * 0.05, xx + s / 4, s * 0.4)
        ctx.stroke()
    elif tipo == "broca":
        ctx.rectangle(-s * 0.15, -s, s * 0.3, s * 1.2); ctx.fill()
        ctx.move_to(-s * 0.15, s * 0.2); ctx.line_to(0, s * 0.7); ctx.line_to(s * 0.15, s * 0.2); ctx.close_path()
        ctx.fill()
        ctx.rectangle(-s * 0.6, -s, s * 1.2, s * 0.25); ctx.fill()
    elif tipo == "caverna":
        ctx.arc(0, s * 0.3, s * 0.8, math.pi, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(0.07, 0.08, 0.13)
        ctx.arc(0, s * 0.35, s * 0.4, math.pi, 2 * math.pi); ctx.fill()
    else:  # canyon
        ctx.move_to(-s, -s * 0.5); ctx.line_to(-s * 0.4, -s * 0.5); ctx.line_to(-s * 0.15, s * 0.6)
        ctx.line_to(s * 0.15, s * 0.6); ctx.line_to(s * 0.4, -s * 0.5); ctx.line_to(s, -s * 0.5)
        ctx.line_to(s, s * 0.7); ctx.line_to(-s, s * 0.7); ctx.close_path(); ctx.fill()
    ctx.restore()


def barra(ctx, x, h, cor, rot, valor_txt, ic, a_val):
    import cairo
    top = BASE - h
    g = cairo.LinearGradient(0, top, 0, BASE)
    g.add_color_stop_rgb(0, *[min(1, c * 1.25) for c in cor])
    g.add_color_stop_rgb(1, *[c * 0.6 for c in cor])
    round_rect(ctx, x - BW / 2, top, BW, h, 16)
    ctx.set_source(g)
    ctx.fill()
    icone(ctx, ic, x, top - 50, cor=WHITE)
    text_center(ctx, rot, x, Y0 + 52, 30 if len(rot) < 16 else 24, WHITE, "ExtraBold")
    text_center(ctx, valor_txt, x, top + 70, 46, WHITE, "ExtraBold", alpha=a_val)  # dentro da barra


def fmt(m):
    return f"{m:,.0f} m"


def rodada(k):
    na, ma, ca, ia, nb, mb, cb, ib = RODADAS[k]
    escala = HMAX / max(ma, mb)

    def draw(ctx, t, s):
        r = s.mark(2)
        cresce = ease((t - r) / 1.0)
        painel(ctx)
        teaser = HMAX * 0.55 + 12 * math.sin(t * 3)  # antes da resposta: as duas iguais, "respirando"
        ha = teaser + (ma * escala - teaser) * cresce
        hb = teaser + (mb * escala - teaser) * cresce
        barra(ctx, XA, ha, ca, na, fmt(ma * cresce), ia, ramp(t, r + 0.2, 0.3))
        barra(ctx, XB, hb, cb, nb, fmt(mb * cresce), ib, ramp(t, r + 0.2, 0.3))
        if t < r:
            for x in (XA, XB):
                text_center(ctx, "?", x, BASE - teaser / 2 + 40, 130, WHITE, "ExtraBold", alpha=0.85)
        countdown(ctx, t, s.mark(1), cx=540, cy=BASE - HMAX - 10)
        if cresce >= 1:
            text_center(ctx, "DEEPER", XA if ma > mb else XB, BASE + 70, 44, GREEN, "ExtraBold",
                        alpha=ramp(t, r + 1.0, 0.3))
    return draw


def resultado(ctx, k):
    """Rodada k já revelada (fundo da pergunta final)."""
    na, ma, ca, ia, nb, mb, cb, ib = RODADAS[k]
    escala = HMAX / max(ma, mb)
    painel(ctx)
    barra(ctx, XA, ma * escala, ca, na, fmt(ma), ia, 1.0)
    barra(ctx, XB, mb * escala, cb, nb, fmt(mb), ib, 1.0)


def d_intro(ctx, t, s):
    painel(ctx)
    for x, c, f in ((XA, AGUA, 0.9), (XB, ROCHA, 0.7)):
        h = HMAX * f * ease(t / 1.2) + 10 * math.sin(t * 4 + x)
        round_rect(ctx, x - BW / 2, BASE - h, BW, h, 16)
        ctx.set_source_rgb(*c)
        ctx.fill()
    icone(ctx, "onda", XA, BASE - HMAX * 0.9 * ease(t / 1.2) - 60)
    icone(ctx, "broca", XB, BASE - HMAX * 0.7 * ease(t / 1.2) - 60)


SEGMENTS = [
    Seg(["How deep does Earth go? Four rounds. Keep score!"], d_intro, {"title": "WHICH IS DEEPER?"}, tail=0.15),
    question(1, N, "CANYON VS TOWER", "One. Is the Grand Canyon deeper than the Burj Khalifa is tall?",
             "Yes! The canyon is more than twice as deep.", rodada(0)),
    question(2, N, "TRENCH VS EVEREST", "Two. The Mariana Trench, or Mount Everest upside down?",
             "The trench! Everest would sink two kilometers under water.", rodada(1)),
    question(3, N, "HUMANS VS THE OCEAN", "Three. Most people miss this. Our deepest hole, or the Mariana Trench?",
             "The hole! Twelve kilometers deep, and narrower than a dinner plate.", rodada(2)),
    question(4, N, "CAVE VS CANYON", "Last one. The deepest cave, or the Grand Canyon?",
             "The cave, by more than three hundred meters.", rodada(3)),
]
SEGMENTS.append(pq.seg_pergunta("Which one surprised you the most?", "WHICH ONE SURPRISED YOU?",
                                fundo=lambda ctx, t, s: resultado(ctx, 2)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
