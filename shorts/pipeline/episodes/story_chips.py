"""How are potato chips made? (2D, padrão caprichado). Sat 28/11/2026. Search 28/11: "how potato chips are made" 590k.

Facts:
- the "air" in a chip bag is nitrogen: it replaces oxygen so the chips don't go stale or rancid, and the cushion
  protects them from breaking;
- legend says chef George Crum invented chips in 1853 in Saratoga Springs to annoy a customer who complained his
  fries were too thick (historians consider it a legend; thin fried potato recipes existed earlier);
- potatoes are washed, peeled and sliced about 1.5 mm thin;
- slices are rinsed to wash off surface starch (so they don't stick), then fried at roughly 175-190 C for a few
  minutes until most of the water is gone;
- salted/seasoned; optical sorters spot dark chips and air jets blow them off the line;
- bags are filled and flushed with nitrogen, then sealed.
Tone: fun -> pop.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import anim  # noqa: E402
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import W, WHITE, Seg, render, text_center  # noqa: E402

core.MUSICA = "animado"
BATATA = (0.85, 0.68, 0.40)
CHIP = (0.98, 0.82, 0.40)
OLEO = (1.0, 0.70, 0.20)
SACO = (0.20, 0.45, 0.85)
N2 = (0.65, 0.85, 1.0)
AMAR = (1.0, 0.88, 0.35)
FUNDO = ((0.18, 0.35, 0.65), (0.05, 0.10, 0.22))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def batata(ctx, x, y, r):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1.3, 0.85)
    anim.esfera(ctx, 0, 0, r, BATATA)
    ctx.restore()
    for i in range(5):   # olhinhos da batata
        ctx.new_path()
        ctx.set_source_rgba(0.45, 0.30, 0.15, 0.7)
        ctx.arc(x + (i - 2) * r * 0.4, y + ((i * 37) % 3 - 1) * r * 0.25, 4, 0, 2 * math.pi)
        ctx.fill()


def chip(ctx, x, y, r, ang=0.0, cor=CHIP, onda=True):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(1, 0.6)
    ctx.new_path()
    for k in range(25):
        a = k / 24 * 2 * math.pi
        rr = r * (1 + 0.08 * math.sin(a * 5))
        ctx.line_to(rr * math.cos(a), rr * math.sin(a))
    ctx.close_path()
    ctx.set_source_rgb(*cor)
    ctx.fill()
    if onda:
        ctx.set_source_rgba(1, 1, 1, 0.35)
        ctx.set_line_width(3)
        ctx.arc(-r * 0.2, -r * 0.2, r * 0.5, 3.6, 5.2)
        ctx.stroke()
    ctx.restore()


def saco(ctx, x, y, s=1.0, cheio=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    anim.sombra_chao(ctx, 0, 300, 360)
    ctx.new_path()
    w = 200 + 20 * cheio
    ctx.move_to(-w, -260)
    ctx.curve_to(-w - 30 * cheio, 0, -w - 30 * cheio, 120, -w, 280)
    ctx.line_to(w, 280)
    ctx.curve_to(w + 30 * cheio, 120, w + 30 * cheio, 0, w, -260)
    ctx.close_path()
    ctx.set_source_rgb(*SACO)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.25)
    ctx.rectangle(-w + 30, -220, 40, 460)
    ctx.fill()
    for lado in (-1, 1):
        ctx.set_source_rgb(0.85, 0.87, 0.92)
        ctx.rectangle(-w, -280 if lado < 0 else 260, 2 * w, 22)
        ctx.fill()
    chip(ctx, 0, 0, 90, 0.3)
    ctx.restore()


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    m1 = s.mark(1) if len(s.items) > 1 else 99
    entra = ease(t / 0.5)
    saco(ctx, 540, 960 + 300 * (1 - entra), 0.9, cheio=1.0)
    anim.texto_pop(ctx, t - 0.4, ["NOT", "AIR"], 540, 520, size=100, cor=WHITE)
    if t > m1:
        tc = t - m1
        for i in range(14):   # moléculas de nitrogênio (pares) dentro do saco
            a = i * 0.45 + t
            x = 540 + 150 * math.cos(a) * ((i % 3) + 1) / 3
            y = 960 + 180 * math.sin(a * 1.3) * ((i % 4) + 1) / 4
            k = ease((tc - i * 0.05) / 0.3)
            if k > 0:
                anim.esfera(ctx, x - 9, y, 11 * k, N2)
                anim.esfera(ctx, x + 9, y, 11 * k, N2)
        anim.texto_pop(ctx, tc, ["NITROGEN"], 540, 650, size=90, cor=N2)


def d_lenda(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.42, 0.30, 0.20), (0.12, 0.08, 0.05), bokeh=AMAR)
    anim.contador(ctx, t - 0.2, 540, 540, 1853, ini=1800, dur=1.0, fmt="{:.0f}", size=110, cor=WHITE, som=None)
    anim.sombra_chao(ctx, 540, 1160, 520)
    ctx.new_path()   # prato
    ctx.save()
    ctx.translate(540, 1060)
    ctx.scale(1, 0.32)
    ctx.arc(0, 0, 260, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgb(0.95, 0.95, 0.93)
    ctx.fill()
    fina = ease((t - 1.6) / 0.8)
    for i in range(8):   # batatas grossas viram fatias finíssimas
        x = 360 + (i % 4) * 110
        y = 1030 + (i // 4) * 40
        if fina < 0.5:
            ctx.set_source_rgb(*BATATA)
            ctx.rectangle(x - 15, y - 40, 30, 80)
            ctx.fill()
        else:
            chip(ctx, x, y, 45, ang=i)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["TOO", "THICK?"], 540, 690, size=80, cor=AMAR)


def d_fatiar(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    batata(ctx, 380, 900, 120)
    giro = t * 10   # lâmina girando
    ctx.save()
    ctx.translate(620, 900)
    ctx.rotate(giro)
    ctx.set_source_rgb(0.80, 0.82, 0.86)
    for k in range(4):
        ctx.rotate(math.pi / 2)
        ctx.rectangle(0, -8, 120, 16)
        ctx.fill()
    ctx.restore()
    for i in range(10):   # fatias voando
        f = (t * 1.2 + i * 0.1) % 1.0
        chip(ctx, 680 + f * 300, 880 + f * 260 - 200 * f * (1 - f), 40, ang=i + t * 3, onda=False)
    anim.texto_pop(ctx, t - 0.4, ["1.5", "MM", "THIN"], 540, 540, size=96, cor=AMAR)


def d_fritar(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.35, 0.20, 0.08), (0.10, 0.05, 0.02), bokeh=OLEO)
    anim.sombra_chao(ctx, 540, 1180, 760)
    anim.bloco_3d(ctx, 170, 940, 740, 220, 50, (0.45, 0.47, 0.52))   # fritadeira
    ctx.set_source_rgb(*OLEO)
    ctx.rectangle(190, 960, 700, 70)
    ctx.fill()
    anim.bolhas(ctx, t, 200, 880, 900, 1030, n=40, r=7, alpha=0.8)
    for i in range(8):   # chips boiando, dourando
        x = 230 + ((t * 120 + i * 90) % 640)
        chip(ctx, x, 975, 40, ang=i, cor=tuple(a + (b - a) * min(1, (x - 230) / 640) for a, b in zip((1, 0.95, 0.8), CHIP)))
    anim.contador(ctx, t - 0.3, 540, 560, 180, dur=1.0, sufixo=" °C", size=100, cor=OLEO)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["WATER", "OUT,", "CRUNCH", "IN"], 540, 690, size=62, cor=WHITE,
                       intervalo=0.15)


def d_laser(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    ctx.set_source_rgb(0.25, 0.27, 0.30)
    ctx.rectangle(0, 1040, W, 26)
    ctx.fill()
    for i in range(9):
        x = -100 + ((t * 230 + i * 140) % 1300)
        queimado = i == 4
        soprado = queimado and x > 640
        y = 1010 - (220 * min(1.0, (x - 640) / 120) if soprado else 0)
        chip(ctx, x, y, 48, ang=i, cor=(0.45, 0.28, 0.12) if queimado else CHIP)
    ctx.set_source_rgba(1, 0.2, 0.2, 0.7)   # feixe do sensor
    ctx.set_line_width(4)
    ctx.move_to(620, 700)
    ctx.line_to(620, 1040)
    ctx.stroke()
    anim.esfera(ctx, 620, 690, 30, (0.6, 0.62, 0.66))
    anim.texto_pop(ctx, t - 0.4, ["BAD", "CHIP?", "BLOWN", "AWAY"], 540, 540, size=74, cor=WHITE, intervalo=0.16)


def d_ensaca(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    infla = ease((t - 0.8) / 1.2)
    saco(ctx, 540, 960, 0.8, cheio=infla)
    for i in range(10):   # jato de nitrogênio entrando
        f = (t * 1.5 + i * 0.1) % 1.0
        if t > 0.6:
            anim.esfera(ctx, 540 + 30 * math.sin(i), 650 + f * 200, 8, N2)
    anim.texto_pop(ctx, t - 0.4, ["NITROGEN", "PILLOW"], 540, 540, size=84, cor=N2)


SEGMENTS = [
    Seg(["That puffy bag of chips isn't full of air.", "It's full of nitrogen."], d_gancho,
        {"title": "HOW ARE POTATO CHIPS MADE?"}, tail=0.2),
    Seg(["Legend says chips were invented in eighteen fifty three, by a chef annoyed with a customer",
         "who said his fries were too thick."], d_lenda, {"big": "THE LEGEND", "color": AMAR}, tail=0.2),
    Seg(["Today, potatoes are washed, peeled, and sliced thinner than two millimeters."], d_fatiar,
        {"big": "SLICE", "color": AMAR}, tail=0.2),
    Seg(["The slices are rinsed, then fried at about one hundred eighty degrees,",
         "until almost all their water is gone."], d_fritar, {"big": "FRY", "color": OLEO}, tail=0.2),
    Seg(["A camera checks every chip. Burnt ones get blasted off the belt by a puff of air."], d_laser,
        {"big": "INSPECT", "color": (1, 0.4, 0.4)}, tail=0.2),
    Seg(["Then the bag is filled with nitrogen. It keeps them fresh, and works like a pillow."], d_ensaca,
        {"big": "THE BAG", "color": N2}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("What's the best chip flavor?", "BEST FLAVOR?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
