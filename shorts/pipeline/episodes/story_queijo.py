"""How is cheese made? (2D, padrão caprichado). Thu 26/11/2026. Search 26/11: "how cheese is made" median 1.36M.

Facts:
- the holes ("eyes") in Swiss-type cheese come from carbon dioxide released by Propionibacterium freudenreichii
  bacteria during warm ripening;
- starter bacteria turn milk sugar (lactose) into lactic acid; rennet (the enzyme chymosin, traditionally from calf
  stomachs, today mostly made by fermentation) makes the milk set into a gel;
- the gel is cut into curds; heating and stirring push out the liquid whey; curds are pressed into molds and salted
  (often in brine);
- it then ages for weeks to years; hard cheeses take about 10 liters of milk per kilogram.
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
QUEIJO = (1.0, 0.82, 0.35)
LEITE = (0.98, 0.98, 0.96)
SORO = (0.92, 0.93, 0.75)
VERDE = (0.45, 0.85, 0.45)
FUNDO = ((0.78, 0.52, 0.22), (0.42, 0.26, 0.10))   # âmbar escuro: título branco legível
FUNDO_ESC = ((0.30, 0.22, 0.14), (0.08, 0.06, 0.04))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def fatia(ctx, x, y, s=1.0, furos=1.0, t=0.0):
    """Fatia triangular de queijo suíço em 3D simples, com furos que crescem (furos 0..1)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    anim.sombra_chao(ctx, 0, 130, 520)
    ctx.new_path()   # topo
    ctx.move_to(-250, 0)
    ctx.line_to(250, -60)
    ctx.line_to(200, -150)
    ctx.close_path()
    ctx.set_source_rgb(*[min(1, c * 1.08) for c in QUEIJO])
    ctx.fill()
    ctx.move_to(-250, 0)   # frente
    ctx.line_to(250, -60)
    ctx.line_to(250, 80)
    ctx.line_to(-250, 140)
    ctx.close_path()
    ctx.set_source_rgb(*QUEIJO)
    ctx.fill()
    ctx.move_to(250, -60)   # lado
    ctx.line_to(200, -150)
    ctx.line_to(200, -10)
    ctx.line_to(250, 80)
    ctx.close_path()
    ctx.set_source_rgb(*[c * 0.85 for c in QUEIJO])
    ctx.fill()
    for i, (fx, fy, r) in enumerate(((-150, 60, 28), (-40, 40, 20), (70, 30, 32), (170, 10, 18), (-90, 105, 15),
                                     (30, 90, 22), (140, 60, 14))):
        rr = r * ease(furos * 1.4 - i * 0.06)
        if rr <= 0:
            continue
        ctx.new_path()
        ctx.save()
        ctx.translate(fx, fy)
        ctx.scale(1, 0.9)
        ctx.arc(0, 0, rr, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(*[c * 0.72 for c in QUEIJO])
        ctx.fill()
    ctx.restore()


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    entra = ease(t / 0.6)
    m1 = s.mark(1) if len(s.items) > 1 else 99
    fatia(ctx, 540, 900 + 300 * (1 - entra), 1.0, furos=ease(t / 1.5), t=t)
    anim.anel_destaque(ctx, t - 1.0, 540 + 70, 930, 70, cor=WHITE)
    if t > m1:   # bactéria com balãozinho "burp"
        tc = t - m1
        core.evento_som("pop", tc)
        k = max(core.mola(tc, 0.45), 0.001)
        ctx.save()
        ctx.translate(760, 640)
        ctx.scale(k, k)
        anim.esfera(ctx, 0, 0, 80, VERDE)
        ctx.set_source_rgb(0.1, 0.2, 0.1)
        for dx in (-24, 24):
            ctx.new_path()
            ctx.arc(dx, -10, 10, 0, 2 * math.pi)
            ctx.fill()
        ctx.restore()
        anim.texto_pop(ctx, tc - 0.2, ["BURP!"], 540, 560, size=100, cor=WHITE)


def d_bacterias(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    anim.sombra_chao(ctx, 540, 1180, 700)
    anim.cilindro(ctx, 540, 700, 600, 440, (0.78, 0.80, 0.84))
    ctx.save()
    ctx.new_path()
    ctx.rectangle(260, 720, 560, 400)
    ctx.clip()
    ctx.set_source_rgb(*LEITE)
    ctx.paint()
    for i in range(int(20 * ease(t / 2.0))):   # bactérias aparecendo
        x = 300 + (i * 97) % 480
        y = 760 + (i * 61) % 330 + 8 * math.sin(t * 3 + i)
        anim.esfera(ctx, x, y, 14, VERDE)
    ctx.restore()
    anim.texto_pop(ctx, t - 0.4, ["MILK", "+", "BACTERIA"], 540, 560, size=84, cor=WHITE, cor_destaque=VERDE, destaque=2)


def d_coalho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    k = ease((t - 0.8) / 1.5)
    anim.sombra_chao(ctx, 540, 1180, 700)
    anim.bloco_3d(ctx, 230, 760, 620, 380, 60, (0.78, 0.80, 0.84))
    ctx.set_source_rgb(*[a + (b - a) * k for a, b in zip(LEITE, (0.99, 0.95, 0.80))])
    ctx.rectangle(250, 790, 580, 340)
    ctx.fill()
    if k > 0.5:   # facas cortando o gel em cubos
        ctx.set_source_rgba(0.6, 0.55, 0.4, 0.9)
        ctx.set_line_width(4)
        n = int(8 * ease((t - 2.0) / 1.2))
        for i in range(1, n + 1):
            ctx.move_to(250 + i * 64, 790)
            ctx.line_to(250 + i * 64, 1130)
            ctx.move_to(250, 790 + i * 40)
            ctx.line_to(830, 790 + i * 40)
        ctx.stroke()
    for j in range(6):   # gotas de coalho
        y = 600 + ((t * 300 + j * 60) % 180)
        if t < 1.5:
            ctx.new_path()
            ctx.set_source_rgb(0.85, 0.70, 0.55)
            ctx.arc(540, y, 8, 0, 2 * math.pi)
            ctx.fill()
    anim.texto_pop(ctx, t - 0.3, ["RENNET"], 540, 560, size=96, cor=WHITE)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["MILK", "JELLY"], 540, 690, size=70, cor=(0.99, 0.93, 0.75))


def d_soro(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    anim.sombra_chao(ctx, 540, 1180, 700)
    anim.bloco_3d(ctx, 230, 760, 620, 380, 60, (0.78, 0.80, 0.84))
    nivel = 1 - 0.6 * ease((t - 0.6) / 2.5)
    ctx.set_source_rgba(*SORO, 0.9)
    ctx.rectangle(250, 1130 - 300 * nivel, 580, 300 * nivel)
    ctx.fill()
    for i in range(24):   # coalhada (cubos) ficando no fundo
        x = 280 + (i % 8) * 68
        y = 1080 - (i // 8) * 52 + 4 * math.sin(t * 4 + i)
        anim.bloco_3d(ctx, x, y, 48, 40, 12, (0.99, 0.95, 0.80))
    for j in range(10):   # soro escorrendo pelo ralo
        f = (t * 1.5 + j * 0.1) % 1.0
        ctx.new_path()
        ctx.set_source_rgba(*SORO, 1 - f)
        ctx.arc(860 + f * 60, 1120 + f * 80, 7, 0, 2 * math.pi)
        ctx.fill()
    anim.texto_pop(ctx, t - 0.3, ["CURDS", "&", "WHEY"], 540, 560, size=92, cor=WHITE)


def d_prensa(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO_ESC, bokeh=QUEIJO)
    desce = ease((t - 0.4) / 0.6)
    anim.tremor(ctx, t - 1.0, forca=10, dur=0.3)
    anim.sombra_chao(ctx, 540, 1170, 600)
    anim.cilindro(ctx, 540, 960, 460, 180, QUEIJO)   # roda de queijo
    anim.bloco_3d(ctx, 300, 560 + 300 * desce, 480, 90, 40, (0.45, 0.47, 0.52))   # prensa
    if len(s.items) > 1:
        m = s.mark(1)
        anim.contador(ctx, t - m, 540, 560, 12, dur=1.2, fmt="{:.0f}", sufixo=" MONTHS", size=96, cor=QUEIJO)


def d_furos(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO_ESC, bokeh=QUEIJO)
    fatia(ctx, 540, 880, 1.1, furos=ease(t / 2.0), t=t)
    for i in range(8):   # bolhas de CO2 subindo
        f = (t * 0.6 + i * 0.125) % 1.0
        ctx.new_path()
        ctx.set_source_rgba(1, 1, 1, 0.6 * (1 - f))
        ctx.arc(320 + i * 60, 820 - f * 220, 10, 0, 2 * math.pi)
        ctx.fill()
    anim.texto_pop(ctx, t - 0.3, ["GAS", "BUBBLES"], 540, 560, size=96, cor=QUEIJO)


SEGMENTS = [
    Seg(["The holes in Swiss cheese?", "They're bacteria burps."], d_gancho,
        {"title": "HOW IS CHEESE MADE?"}, tail=0.2),
    Seg(["Cheese starts as milk, with good bacteria that turn its sugar into acid."], d_bacterias,
        {"big": "STEP 1", "color": VERDE}, tail=0.2),
    Seg(["Then comes rennet, an enzyme that makes the milk set,", "like a soft jelly. It's cut into tiny cubes."],
        d_coalho, {"big": "STEP 2", "color": (0.99, 0.93, 0.75)}, tail=0.2),
    Seg(["Heated and stirred, the cubes squeeze out a yellow liquid called whey. The cubes are the cheese."], d_soro,
        {"big": "STEP 3", "color": (0.99, 0.93, 0.75)}, tail=0.2),
    Seg(["They're pressed into wheels, salted,", "and left to age for months."], d_prensa,
        {"big": "PRESS", "color": QUEIJO}, tail=0.2),
    Seg(["In Swiss cheese, special bacteria keep eating and burping gas. The bubbles get trapped, and become holes."],
        d_furos, {"big": "THE HOLES", "color": QUEIJO}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("What's the best cheese on Earth?", "BEST CHEESE?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
