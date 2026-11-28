"""How are chocolate chip cookies made? (2D, padrão caprichado). Sat 28/11/2026. Search 28/11: median 716k.

Facts:
- Ruth Wakefield created the chocolate chip cookie around 1938 at the Toll House Inn in Whitman, Massachusetts,
  using a chopped semi-sweet chocolate bar; the story that it was an accident is considered a myth;
- the recipe became hugely popular; she reportedly let a chocolate company print it on its packaging in exchange for
  a lifetime supply of chocolate (said as "reportedly");
- method: butter creamed with sugar (traps tiny air bubbles), eggs, flour, baking soda, salt; then the chips;
- baked around 180 C for about 10 minutes: the dough melts and spreads, edges brown (caramelization and Maillard),
  the middle stays soft;
- in factories, machines drop identical balls of dough onto belts that run through long tunnel ovens.
Brand names are not drawn.
Tone: fun -> alegre.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import anim  # noqa: E402
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import W, WHITE, Seg, render, text_center  # noqa: E402

core.MUSICA = "divertido"
COOKIE = (0.88, 0.66, 0.38)
MASSA = (0.95, 0.85, 0.62)
CHOC = (0.30, 0.17, 0.09)
MANTEIGA = (1.0, 0.92, 0.55)
AMAR = (1.0, 0.85, 0.35)
FUNDO = ((0.55, 0.36, 0.22), (0.18, 0.10, 0.05))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def cookie(ctx, x, y, r, assado=1.0, gotas=10, achata=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, 0.78 * achata + 0.22)
    anim.sombra_chao(ctx, 0, r * 0.9, r * 2.3)
    cor = tuple(a + (b - a) * assado for a, b in zip(MASSA, COOKIE))
    anim.esfera(ctx, 0, 0, r, cor)
    if assado > 0.4:   # borda mais escura
        ctx.new_path()
        ctx.arc(0, 0, r * 0.95, 0, 2 * math.pi)
        ctx.set_source_rgba(0.6, 0.35, 0.12, 0.35 * assado)
        ctx.set_line_width(r * 0.12)
        ctx.stroke()
    for i in range(gotas):
        a = i * 2.4
        rr = r * 0.65 * ((i * 37 % 10) / 10)
        anim.esfera(ctx, rr * math.cos(a), rr * math.sin(a), r * 0.11, CHOC)
    ctx.restore()


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=AMAR)
    entra = ease(t / 0.5)
    cookie(ctx, 540, 960 + 300 * (1 - entra), 230)
    anim.contador(ctx, t - 0.1, 540, 540, 1938, ini=1900, dur=1.0, fmt="{:.0f}", size=110, cor=WHITE, som=None)
    if len(s.items) > 1:
        m = s.mark(1)
        anim.texto_pop(ctx, t - m, ["FREE", "CHOCOLATE", "FOR", "LIFE"], 540, 690, size=66, cor=AMAR, intervalo=0.15)


def d_ruth(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.35, 0.45, 0.55), (0.10, 0.14, 0.18), bokeh=(1, 1, 1))
    anim.sombra_chao(ctx, 540, 1180, 600)   # pousada (casinha)
    anim.bloco_3d(ctx, 290, 860, 500, 300, 60, (0.95, 0.92, 0.85))
    ctx.new_path()
    ctx.move_to(260, 860)
    ctx.line_to(540, 680)
    ctx.line_to(820, 860)
    ctx.close_path()
    ctx.set_source_rgb(0.55, 0.20, 0.15)
    ctx.fill()
    for i in range(3):
        ctx.set_source_rgba(1, 0.9, 0.6, 0.9)
        ctx.rectangle(330 + i * 150, 920, 80, 80)
        ctx.fill()
    anim.texto_pop(ctx, t - 0.4, ["NOT", "AN", "ACCIDENT"], 540, 540, size=84, cor=WHITE, cor_destaque=AMAR, destaque=2)
    if len(s.items) > 1:   # barra de chocolate sendo picada
        m = s.mark(1)
        corte = min(6, int(max(0.0, t - m) / 0.25))
        for i in range(6):
            dx = (i - 2.5) * 70 + (i - 2.5) * 12 * corte / 6
            anim.bloco_3d(ctx, 540 + dx - 30, 1165, 60, 36, 14, CHOC)
            core.evento_som("tick", t - m - 0.25 * (i + 1))


def d_creme(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=AMAR)
    anim.sombra_chao(ctx, 540, 1180, 600)
    anim.cilindro(ctx, 540, 820, 520, 330, (0.78, 0.80, 0.84))   # tigela
    ctx.save()
    ctx.new_path()
    ctx.rectangle(290, 840, 500, 300)
    ctx.clip()
    k = ease(t / 3.0)
    cor = tuple(a + (b - a) * k for a, b in zip(MANTEIGA, MASSA))
    ctx.set_source_rgb(*cor)
    ctx.paint()
    for i in range(int(40 * k)):   # bolhinhas de ar presas
        ctx.new_path()
        ctx.set_source_rgba(1, 1, 1, 0.7)
        ctx.arc(310 + (i * 53) % 460, 860 + (i * 37) % 260, 6, 0, 2 * math.pi)
        ctx.fill()
    ctx.restore()
    for i in range(2):   # batedor girando
        a = t * 8 + i * math.pi
        ctx.set_source_rgba(0.85, 0.87, 0.9, 1)
        ctx.set_line_width(10)
        ctx.move_to(540, 640)
        ctx.line_to(540 + 70 * math.cos(a), 900)
        ctx.stroke()
    anim.texto_pop(ctx, t - 0.4, ["BUTTER", "+", "SUGAR", "=", "AIR"], 540, 540, size=72, cor=WHITE, intervalo=0.15)


def d_gotas(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=AMAR)
    for i in range(40):   # gotas de chocolate chovendo na massa
        f = (t * 0.9 + i * 0.025) % 1.0
        anim.esfera(ctx, 300 + (i * 47) % 480, 600 + f * 420, 16, CHOC)
    anim.sombra_chao(ctx, 540, 1170, 560)
    ctx.save()
    ctx.translate(540, 1080)
    ctx.scale(1, 0.55)
    anim.esfera(ctx, 0, 0, 230, MASSA)
    ctx.restore()
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["SCOOP", "SCOOP", "SCOOP"], 540, 540, size=76, cor=WHITE, intervalo=0.3)


def d_forno(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.35, 0.15, 0.05), (0.10, 0.04, 0.01), bokeh=(1, 0.6, 0.2))
    anim.brilho(ctx, 540, 920, 480, (1, 0.55, 0.15), 0.45)
    k = ease(t / 3.5)
    for i, x in enumerate((300, 540, 780)):   # bolas virando cookies achatados
        cookie(ctx, x, 940, 70 + 50 * k, assado=k, gotas=6, achata=1.0 - 0.7 * k)
    anim.contador(ctx, t - 0.2, 540, 560, 180, dur=1.0, sufixo=" °C", size=100, cor=(1, 0.6, 0.25))
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["CRISPY", "EDGE,", "SOFT", "MIDDLE"], 540, 690, size=60, cor=AMAR,
                       intervalo=0.15)


def d_fabrica(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.30, 0.32, 0.36), (0.08, 0.09, 0.10), bokeh=AMAR)
    ctx.set_source_rgb(0.25, 0.27, 0.30)
    ctx.rectangle(0, 1100, W, 26)
    ctx.fill()
    anim.bloco_3d(ctx, 620, 880, 460, 200, 50, (0.55, 0.57, 0.62))   # túnel do forno
    anim.brilho(ctx, 850, 980, 260, (1, 0.55, 0.15), 0.5)
    for i in range(10):
        x = -100 + ((t * 200 + i * 120) % 1300)
        assado = min(1.0, max(0.0, (x - 620) / 460))
        cookie(ctx, x, 1070, 42, assado=assado, gotas=5, achata=1.0 - 0.6 * assado)
    anim.contador(ctx, t - 0.3, 540, 560, 1000000, dur=1.5, sufixo=" A DAY", size=70, cor=WHITE)


SEGMENTS = [
    Seg(["The chocolate chip cookie was invented in nineteen thirty eight.",
         "And its inventor reportedly traded the recipe for free chocolate for life."], d_gancho,
        {"title": "HOW ARE COOKIES MADE?"}, tail=0.2),
    Seg(["Her name was Ruth Wakefield, and it wasn't an accident.", "She chopped up a chocolate bar on purpose."],
        d_ruth, {"big": "THE INVENTOR", "big_size": 96, "color": AMAR}, tail=0.2),
    Seg(["The dough starts with butter and sugar, beaten until fluffy. That traps tiny air bubbles."], d_creme,
        {"big": "STEP 1", "color": MANTEIGA}, tail=0.2),
    Seg(["Then eggs, flour, a pinch of baking soda, and the chips.", "Scooped into balls."], d_gotas,
        {"big": "STEP 2", "color": MASSA}, tail=0.2),
    Seg(["In the oven, the balls melt and spread.", "The edges brown and crisp, while the middle stays soft."],
        d_forno, {"big": "BAKE", "color": (1, 0.6, 0.25)}, tail=0.2),
    Seg(["Factories do it nonstop: machines drop the dough onto belts that roll through ovens longer than a bus."],
        d_fabrica, {"big": "AT SCALE", "color": WHITE}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Crunchy or chewy cookies?", "CRUNCHY OR CHEWY?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO, bokeh=AMAR)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
