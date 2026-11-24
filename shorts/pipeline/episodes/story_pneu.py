"""How are tires made? (2D, padrão caprichado). Tue 24/11/2026. Search 24/11: "how tires are made" median 296k.

Facts:
- early car tires were white or off-white: natural rubber with zinc oxide; around the 1910s makers began adding carbon
  black, which made tires far stronger and longer-lasting, and they turned black; carbon black is roughly a quarter
  to a third of a modern tire;
- rubber comes from latex tapped from rubber trees plus synthetic rubber made from oil;
- raw rubber gets sticky in heat and brittle in cold; in 1839 Charles Goodyear accidentally dropped a rubber-sulfur
  mix on a hot stove and it came out tough and elastic: vulcanization (sulfur bridges between rubber chains);
- a tire is built in layers on a drum: inner liner, fabric body plies, steel belts, then the tread (the "green tire");
- it is cured in a hot mold (around 150-180 C) under pressure for roughly 10-15 minutes for a car tire; the mold
  stamps the tread pattern and the sidewall lettering.
Tone: curious/fun -> alegre? No: construção/indústria -> epico.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import anim  # noqa: E402
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import W, WHITE, Seg, render, text_center  # noqa: E402

core.MUSICA = "epico"
BORRACHA = (0.13, 0.13, 0.15)
BRANCO = (0.93, 0.91, 0.85)
LATEX = (0.97, 0.96, 0.90)
AMAR = (1.0, 0.82, 0.25)
LARANJA = (1.0, 0.55, 0.15)
ACO = (0.66, 0.70, 0.76)
FUNDO = ((0.16, 0.17, 0.22), (0.04, 0.04, 0.07))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def pneu(ctx, x, y, r, cor, giro=0.0, banda=True):
    """Pneu visto de lado: borracha com sulcos, aro metálico e reflexo."""
    ctx.new_path()
    anim.sombra_chao(ctx, x, y + r + 8, r * 2.2)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source_rgb(*cor)
    ctx.fill()
    if banda:   # blocos da banda de rodagem girando
        ctx.set_source_rgba(0, 0, 0, 0.35)
        for k in range(28):
            a = giro + k * 2 * math.pi / 28
            ctx.save()
            ctx.translate(x + (r - 10) * math.cos(a), y + (r - 10) * math.sin(a))
            ctx.rotate(a)
            ctx.rectangle(-9, -6, 18, 12)
            ctx.restore()
            ctx.fill()
    anim.esfera(ctx, x, y, r * 0.58, ACO)   # aro
    ctx.set_source_rgba(0.25, 0.27, 0.3, 1)
    for k in range(5):   # raios
        a = giro + k * 2 * math.pi / 5
        ctx.set_line_width(14)
        ctx.move_to(x, y)
        ctx.line_to(x + r * 0.5 * math.cos(a), y + r * 0.5 * math.sin(a))
        ctx.stroke()
    anim.esfera(ctx, x, y, r * 0.12, ACO)


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 0.9, 0.7))
    m1 = s.mark(1) if len(s.items) > 1 else 99
    k = ease((t - m1 + 0.2) / 0.5)
    cor = tuple(a + (b - a) * k for a, b in zip(BORRACHA, BRANCO))   # preto -> branco na 2ª frase
    pneu(ctx, 540 - 380 + 380 * ease(t / 0.8), 900, 260, cor, giro=t * 4)   # entra rolando desde o quadro 0
    anim.texto_pop(ctx, t - 0.4, ["TIRES", "WERE", "WHITE"], 540, 520, size=96, cor=WHITE, cor_destaque=BRANCO,
                   destaque=2)
    if t > m1:
        anim.estouro(ctx, t - m1, 540, 900, cor=AMAR, r0=280, r1=420)


def d_latex(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.14, 0.26, 0.16), (0.03, 0.07, 0.04), bokeh=(0.7, 1, 0.7))
    anim.sombra_chao(ctx, 380, 1180, 300)   # tronco da seringueira com corte em espiral
    ctx.set_source_rgb(0.42, 0.30, 0.20)
    ctx.rectangle(310, 560, 140, 620)
    ctx.fill()
    ctx.set_source_rgba(0.25, 0.16, 0.10, 1)
    ctx.set_line_width(8)
    ctx.move_to(310, 820)
    ctx.line_to(450, 900)
    ctx.stroke()
    for j in range(6):   # gotas de látex caindo no copo
        y = 905 + ((t * 160 + j * 40) % 150)
        ctx.new_path()
        ctx.set_source_rgb(*LATEX)
        ctx.arc(452, y, 7, 0, 2 * math.pi)
        ctx.fill()
    anim.cilindro(ctx, 452, 1060, 90, 90, (0.55, 0.45, 0.35))
    anim.seta(ctx, t - 0.6, 452, 900, ang=math.pi, cor=AMAR)
    if len(s.items) > 1:
        m = s.mark(1)
        tc = t - m
        core.evento_som("pop", tc)
        if tc >= 0:   # barril de petróleo = borracha sintética
            k = max(core.mola(tc, 0.45), 0.001)
            ctx.save()
            ctx.translate(780, 1000)
            ctx.scale(k, k)
            anim.sombra_chao(ctx, 0, 150, 220)
            anim.cilindro(ctx, 0, -110, 170, 250, (0.15, 0.32, 0.65))
            text_center(ctx, "OIL", 0, 20, 44, WHITE, "ExtraBold")
            ctx.restore()


def d_carbono(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.86, 0.84, 0.80), (0.55, 0.53, 0.50), bokeh=(1, 1, 1))   # fundo claro: o pó preto aparece
    k = ease((t - 0.8) / 2.0)
    for i in range(160):   # pó preto caindo e escurecendo a massa
        f = ((t * 0.7 + i * 0.013) % 1.0)
        x = 340 + (i * 37) % 400
        y = 600 + f * 420
        ctx.new_path()
        ctx.set_source_rgba(0.05, 0.05, 0.06, 0.9 * (1 - f))
        ctx.arc(x, y, 4, 0, 2 * math.pi)
        ctx.fill()
    cor = tuple(a + (b - a) * k for a, b in zip(BRANCO, BORRACHA))
    anim.sombra_chao(ctx, 540, 1180, 520)
    ctx.new_path()
    ctx.save()
    ctx.translate(540, 1100)
    ctx.scale(1.0, 0.45)
    ctx.arc(0, 0, 300, math.pi, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgb(*cor)
    ctx.fill()
    anim.contador(ctx, t - 0.8, 540, 1240 - 60, 30, dur=1.6, sufixo="% CARBON BLACK", size=64, cor=AMAR)


def d_goodyear(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.22, 0.14, 0.10), (0.06, 0.04, 0.03), bokeh=LARANJA)
    anim.sombra_chao(ctx, 540, 1190, 600)   # fogão de ferro
    anim.bloco_3d(ctx, 300, 960, 480, 220, 60, (0.22, 0.22, 0.24))
    anim.brilho(ctx, 540, 960, 280, LARANJA, 0.6)
    queda = ease((t - 0.6) / 0.5)
    y = 650 + 300 * queda
    ctx.new_path()   # massa de borracha com enxofre caindo
    ctx.set_source_rgb(*(AMAR if queda < 1 else BORRACHA))
    ctx.save()
    ctx.translate(540, y)
    ctx.scale(1.4, 0.7 if queda >= 1 else 1.0)
    ctx.arc(0, 0, 60, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    anim.estouro(ctx, t - 1.1, 540, 950, cor=AMAR)
    if t > 1.1:
        anim.fumaca(ctx, t, 540, 930, cor=(0.8, 0.8, 0.8), alpha=0.25)
    anim.contador(ctx, t - 0.2, 540, 560, 1839, ini=1800, dur=1.0, fmt="{:.0f}", size=110, cor=WHITE, som=None)
    if len(s.items) > 1:
        m = s.mark(1)
        anim.texto_pop(ctx, t - m, ["TOUGH", "AND", "BOUNCY"], 540, 720, size=80, cor=AMAR)


def d_camadas(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO)
    camadas = [("INNER LINER", (0.30, 0.30, 0.33)), ("FABRIC PLIES", (0.80, 0.72, 0.55)),
               ("STEEL BELTS", ACO), ("TREAD", BORRACHA)]
    for i, (nome, cor) in enumerate(camadas):   # camadas empilhando com mola sobre o tambor
        ti = t - 0.4 - i * 0.9
        core.evento_som("pop", ti)
        if ti < 0:
            continue
        k = max(core.mola(ti, 0.4), 0.001)
        y = 1110 - i * 95
        ctx.save()
        ctx.translate(540, y)
        ctx.scale(k, 1)
        anim.bloco_3d(ctx, -330, -40, 660, 80, 40, cor)
        if nome == "STEEL BELTS":
            ctx.set_source_rgba(1, 1, 1, 0.5)
            ctx.set_line_width(3)
            for j in range(18):
                ctx.move_to(-320 + j * 37, -36)
                ctx.line_to(-300 + j * 37, 36)
            ctx.stroke()
        ctx.restore()
        text_center(ctx, nome, 540, y + 14, 34, WHITE if nome != "FABRIC PLIES" else (0.15, 0.15, 0.15), "ExtraBold",
                    alpha=min(1.0, ti * 3))


def d_forno(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.20, 0.10, 0.06), (0.05, 0.03, 0.02), bokeh=LARANJA)
    fecha = ease((t - 0.3) / 0.6) * (1 - ease((t - 3.6) / 0.5))
    anim.tremor(ctx, t - 0.9, forca=10, dur=0.3)
    for lado in (-1, 1):   # metades do molde
        x = 540 + lado * (40 + 300 * (1 - fecha))
        anim.bloco_3d(ctx, x - 150 if lado < 0 else x, 640, 150, 520, 40, (0.40, 0.42, 0.46))
    if fecha > 0.9:
        anim.brilho(ctx, 540, 900, 300, LARANJA, 0.7)
        anim.fumaca(ctx, t, 540, 640, cor=(1, 0.8, 0.6), alpha=0.18)
    if t > 4.0:
        pneu(ctx, 540, 900, 230, BORRACHA, giro=t)
        anim.anel_destaque(ctx, t - 4.3, 540, 900, 260, cor=AMAR)
    anim.contador(ctx, t - 0.9, 540, 560, 170, dur=1.2, sufixo=" °C", size=96, cor=LARANJA)


def d_fim(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 0.9, 0.7))
    pneu(ctx, 540, 960, 240, BORRACHA, giro=t * 6)
    anim.faiscas(ctx, t, 300, 1210, n=24, vel=360, cor=(0.8, 0.8, 0.8), ang=(-math.pi, -math.pi * 0.7))
    anim.texto_pop(ctx, t - 0.3, ["10", "MINUTES", "IN", "THE", "OVEN"], 540, 600, size=84, cor=WHITE, cor_destaque=AMAR,
                   destaque=1, intervalo=0.18)


SEGMENTS = [
    Seg(["The first car tires weren't black.", "They were white."], d_gancho,
        {"title": "HOW ARE TIRES MADE?"}, tail=0.2),
    Seg(["A tire starts as milky sap from rubber trees,", "mixed with synthetic rubber made from oil."], d_latex,
        {"big": "RUBBER", "color": LATEX}, tail=0.2),
    Seg(["Then they add carbon black, a sooty powder. It makes tires way tougher. That's why they turned black."],
        d_carbono, {"big": "WHY BLACK?", "color": AMAR}, tail=0.2),
    Seg(["But raw rubber melts in summer and cracks in winter. In eighteen thirty nine, Charles Goodyear dropped some on a hot stove.",
         "It came out tough and bouncy."], d_goodyear, {"big": "THE ACCIDENT", "big_size": 96, "color": LARANJA},
        tail=0.2),
    Seg(["Today a machine wraps it in layers: a liner, fabric, steel belts, and the tread."], d_camadas,
        {"big": "LAYERS", "color": ACO}, tail=0.2),
    Seg(["Then it's baked in a hot mold that presses the pattern in. Goodyear's accident, at full scale."], d_forno,
        {"big": "BAKE", "color": LARANJA}, tail=0.2),
    Seg(["About ten minutes later, it rolls out, ready for the road."], d_fim,
        {"big": "DONE", "color": WHITE}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Would you buy white tires today?", "WHITE TIRES: YES OR NO?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
