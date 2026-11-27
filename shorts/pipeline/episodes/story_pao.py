"""How is bread made? (2D, padrão caprichado). Fri 27/11/2026. Search 26/11: "how bread is made" median 552k.

Facts:
- in January 1943 the US government banned the sale of sliced bread as a wartime measure (to save steel for slicing
  machines and wax paper); the ban was lifted in March 1943 after public outcry;
- the bread-slicing machine was invented by Otto Rohwedder; sliced bread was first sold in 1928 (Chillicothe,
  Missouri);
- dough is flour, water, yeast and salt; kneading builds gluten, a stretchy protein network;
- yeast eats sugars and releases carbon dioxide; the gluten traps the gas, so the dough rises;
- baked around 220-250 C: the gas expands ("oven spring"), the crust browns (Maillard reaction) and the inside sets
  at about 95 C.
Tone: história curiosa -> cinema? curious -> lofi used often; use alegre for variety.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import anim  # noqa: E402
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import W, WHITE, Seg, render, text_center  # noqa: E402

core.MUSICA = "historia"   # -> cinema
CASCA = (0.78, 0.48, 0.20)
MIOLO = (0.98, 0.90, 0.70)
MASSA = (0.96, 0.90, 0.78)
VERM = (0.95, 0.30, 0.28)
AMAR = (1.0, 0.82, 0.35)
FUNDO = ((0.42, 0.28, 0.16), (0.12, 0.07, 0.04))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def pao_forma(ctx, x, y, s=1.0, fatias=0, crescer=1.0, cor_casca=CASCA):
    """Pão de forma visto de lado; fatias = quantas fatias separadas na frente."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    anim.sombra_chao(ctx, 0, 110, 520)
    h = 150 * crescer
    ctx.new_path()
    ctx.move_to(-230, 100)
    ctx.line_to(-230, 100 - h)
    ctx.curve_to(-250, 100 - h - 190 * crescer, 250, 100 - h - 190 * crescer, 230, 100 - h)   # cúpula alta
    ctx.line_to(230, 100)
    ctx.close_path()
    ctx.set_source_rgb(*cor_casca)
    ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.25)
    ctx.set_line_width(4)
    for i in range(1, 9):   # marcas das fatias
        xx = -230 + i * 51
        ctx.move_to(xx, 100)
        ctx.line_to(xx, 100 - h - 60 * crescer)
    ctx.stroke()
    for i in range(fatias):   # fatias caindo para a frente
        ctx.save()
        ctx.translate(250 + i * 70, 100)
        ctx.rotate(0.15 + i * 0.05)
        ctx.new_path()
        ctx.rectangle(0, -200, 50, 200)
        ctx.set_source_rgb(*MIOLO)
        ctx.fill()
        ctx.set_source_rgb(*cor_casca)
        ctx.set_line_width(10)
        ctx.rectangle(0, -200, 50, 200)
        ctx.stroke()
        ctx.restore()
    ctx.restore()


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=AMAR)
    entra = ease(t / 0.6)
    m1 = s.mark(1) if len(s.items) > 1 else 99
    pao_forma(ctx, 470 - 300 * (1 - entra), 960, 1.0, fatias=3)
    anim.contador(ctx, t - 0.1, 540, 560, 1943, ini=1900, dur=1.0, fmt="{:.0f}", size=110, cor=AMAR, som=None)
    if t > m1:   # carimbo BANNED
        tc = t - m1
        core.evento_som("thud", tc)
        k = max(1.0 + 0.6 * (1 - ease(tc / 0.25)), 0.001)
        ctx.save()
        ctx.translate(540, 880)
        ctx.rotate(-0.18)
        ctx.scale(k, k)
        ctx.set_source_rgba(*VERM, 0.9)
        ctx.set_line_width(12)
        ctx.rectangle(-260, -70, 520, 140)
        ctx.stroke()
        text_center(ctx, "BANNED", 0, 30, 110, VERM, "ExtraBold")
        ctx.restore()


def d_guerra(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.35, 0.38, 0.30), (0.10, 0.11, 0.08), bokeh=(1, 1, 0.8))
    anim.sombra_chao(ctx, 540, 1170, 600)   # máquina de fatiar com lâminas de aço
    anim.bloco_3d(ctx, 260, 780, 560, 360, 60, (0.55, 0.58, 0.62))
    for i in range(9):
        ctx.set_source_rgba(0.9, 0.92, 0.95, 0.9)
        ctx.rectangle(300 + i * 58, 800 + 6 * math.sin(t * 20 + i), 6, 320)
        ctx.fill()
    anim.anel_destaque(ctx, t - 1.0, 540, 960, 230, cor=AMAR)
    anim.texto_pop(ctx, t - 0.4, ["SAVE", "THE", "STEEL"], 540, 560, size=92, cor=WHITE, cor_destaque=AMAR, destaque=2)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["2", "MONTHS", "LATER:", "BACK"], 540, 690, size=60, cor=(0.6, 1.0, 0.6))


def d_massa(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=AMAR)
    itens = [("FLOUR", (0.99, 0.98, 0.95), 230), ("WATER", (0.55, 0.80, 1.0), 430), ("YEAST", (0.85, 0.72, 0.45), 650),
             ("SALT", (0.95, 0.95, 0.95), 850)]
    for i, (nome, cor, x) in enumerate(itens):
        ti = t - 0.2 - i * 0.45
        core.evento_som("pop", ti)
        if ti < 0:
            continue
        k = max(core.mola(ti, 0.4), 0.001)
        ctx.save()
        ctx.translate(x, 780)
        ctx.scale(k, k)
        anim.esfera(ctx, 0, 0, 62, cor)
        text_center(ctx, nome, 0, 115, 32, WHITE, "ExtraBold")
        ctx.restore()
    sova = math.sin(t * 6)   # massa sendo sovada e esticando (glúten)
    ctx.save()
    ctx.translate(540, 1060)
    ctx.scale(1 + 0.25 * sova, 1 - 0.15 * sova)
    anim.esfera(ctx, 0, 0, 110, MASSA)
    ctx.restore()
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["STRETCHY", "GLUTEN"], 540, 560, size=84, cor=AMAR)


def d_fermenta(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=AMAR)
    k = ease(t / 4.0)
    anim.sombra_chao(ctx, 540, 1180, 600)
    anim.bloco_3d(ctx, 290, 1000, 500, 160, 50, (0.55, 0.57, 0.62))   # forma
    ctx.save()
    ctx.translate(540, 1000)
    ctx.scale(1, 0.45 + 0.85 * k)
    anim.esfera(ctx, 0, 0, 240, MASSA)
    ctx.restore()
    for i in range(16):   # bolhas de CO2 dentro da massa
        a = i * 2.3
        r = 160 * ((i * 37 % 10) / 10)
        ctx.new_path()
        ctx.set_source_rgba(0.85, 0.78, 0.62, 0.9)
        ctx.arc(540 + r * math.cos(a), 1000 - (60 + 80 * k) * abs(math.sin(a)) * 1.2, 6 + 10 * k, 0, 2 * math.pi)
        ctx.fill()
    anim.texto_pop(ctx, t - 0.5, ["YEAST", "MAKES", "GAS"], 540, 560, size=88, cor=WHITE)


def d_forno(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.30, 0.12, 0.06), (0.08, 0.03, 0.02), bokeh=(1, 0.5, 0.2))
    k = ease(t / 3.0)
    anim.brilho(ctx, 540, 960, 420, (1, 0.5, 0.15), 0.6)
    cor = tuple(a + (b - a) * k for a, b in zip(MASSA, CASCA))
    pao_forma(ctx, 540, 980, 1.0, crescer=0.8 + 0.25 * k, cor_casca=cor)
    anim.contador(ctx, t - 0.2, 540, 560, 230, dur=1.2, sufixo=" °C", size=100, cor=(1, 0.6, 0.25))
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["GOLDEN", "CRUST"], 540, 690, size=78, cor=AMAR)


def d_fatia(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=AMAR)
    n = min(4, int(t / 0.7))
    for i in range(n):
        core.evento_som("swish", t - 0.7 * (i + 1))
    pao_forma(ctx, 430, 960, 0.95, fatias=n)
    anim.texto_pop(ctx, t - 0.4, ["SINCE", "1928"], 540, 560, size=96, cor=WHITE, cor_destaque=AMAR, destaque=1)


SEGMENTS = [
    Seg(["In nineteen forty three, the United States banned sliced bread.", "For real."], d_gancho,
        {"title": "HOW IS BREAD MADE?"}, tail=0.2),
    Seg(["It was wartime, and the government wanted to save steel from slicing machines.",
         "People were so angry, the ban lasted two months."], d_guerra, {"big": "WHY?", "color": AMAR}, tail=0.2),
    Seg(["Bread itself is simple: flour, water, yeast and salt. Kneading it", "builds gluten, a stretchy net."],
        d_massa, {"big": "THE DOUGH", "color": MASSA}, tail=0.2),
    Seg(["Yeast eats the sugar and burps gas. The gluten traps it, and the dough puffs up."], d_fermenta,
        {"big": "THE RISE", "color": AMAR}, tail=0.2),
    Seg(["In a hot oven the gas expands one last time,", "and the outside browns into a crust."], d_forno,
        {"big": "BAKE", "color": (1, 0.6, 0.25)}, tail=0.2),
    Seg(["Then a machine with dozens of blades slices it. The best thing since, well, sliced bread."], d_fatia,
        {"big": "SLICED", "color": AMAR}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Crust: eat it or leave it?", "CRUST: YES OR NO?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
