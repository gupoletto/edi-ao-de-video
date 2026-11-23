"""How is steel made? (2D, "caprichado" standard). Mon 23/11/2026, demo of the new quality standard (anim.py +
automatic attention triggers in core.render). Search 22/11: "how steel is made" median 375k.

Facts (World Steel Association; basic oxygen route, ~70% of world steel):
- molten steel is around 1,600 C; lava erupts at roughly 700-1,200 C;
- raw materials: iron ore (iron oxide, "rusty rock"), coke made from coal, and limestone;
- the blast furnace is a tower tens of meters tall; hot air is blown in at the bottom; carbon monoxide from the coke
  strips the oxygen from the ore and molten iron collects at the bottom;
- that "pig iron" has about 4% carbon and is brittle;
- in the basic oxygen furnace, a lance blows pure oxygen at supersonic speed onto the metal; the carbon burns off
  (down to well under 1%), throwing sparks; scrap steel is added too;
- continuous casting pours it into a mold that solidifies it into an endless slab, then rolling mills squash it into
  sheets, beams and coils;
- the world produced about 1.9 billion tonnes of steel in 2023; steel is the most recycled material by tonnage.
Attention beats (one every 2-3 s): counter on frame 0, objects popping in, ring and arrow on the detail being
named, shake on the oxygen blast, kinetic big number at the end.
Tone: epic -> epico music.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import anim  # noqa: E402
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import W, WHITE, YELLOW, Seg, render, text_center  # noqa: E402

core.MUSICA = "epico"
FUNDIDO = (1.0, 0.55, 0.12)
QUENTE = (1.0, 0.85, 0.40)
ACO = (0.62, 0.66, 0.72)
ESCURO = ((0.10, 0.07, 0.07), (0.02, 0.02, 0.03))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def rio(ctx, t, x0, y0, x1, y1, larg=46):
    """Jorro de metal fundido de (x0, y0) até (x1, y1), ondulando, com núcleo claro."""
    for w, cor, a in ((larg * 2.6, FUNDIDO, 0.18), (larg, FUNDIDO, 1.0), (larg * 0.45, QUENTE, 1.0)):
        ctx.new_path()
        ctx.set_line_width(w)
        ctx.set_source_rgba(*cor, a)
        ctx.move_to(x0, y0)
        mx = (x0 + x1) / 2 + 18 * math.sin(t * 5)
        ctx.curve_to(mx, y0, x1 - 10 * math.sin(t * 4), (y0 + y1) / 2, x1, y1)
        ctx.stroke()


def panela(ctx, x, y, ang):
    """Panela de aço tombando (canto de onde sai o jorro em x, y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    anim.bloco_3d(ctx, -260, -40, 260, 200, 60, (0.30, 0.30, 0.34))
    ctx.restore()


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *ESCURO, bokeh=FUNDIDO)
    panela(ctx, 330, 860, 0.35)
    rio(ctx, t, 300, 940, 560, 1160)
    anim.brilho(ctx, 600, 1160, 360, FUNDIDO, 0.55)
    ctx.set_source_rgb(*FUNDIDO)   # poça
    ctx.save()
    ctx.translate(600, 1170)
    ctx.scale(1, 0.18)
    ctx.arc(0, 0, 320, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    anim.faiscas(ctx, t, 600, 1150, n=60, vel=640)
    anim.contador(ctx, t - 0.1, 540, 560, 1600, dur=1.4, sufixo=" °C", size=130, cor=QUENTE)
    anim.texto_pop(ctx, t - 0.6, ["HOTTER", "THAN", "LAVA"], 540, 720, size=86, cor=WHITE,
                   cor_destaque=FUNDIDO, destaque=2)
    if len(s.items) > 1:   # o carro em que esse aço vai virar
        m = s.mark(1)
        tc = t - m
        core.evento_som("pop", tc)
        if tc >= 0:
            k = max(core.mola(tc, 0.45), 0.001)
            ctx.save()
            ctx.translate(850, 1060)
            ctx.scale(k, k)
            anim.sombra_chao(ctx, 0, 70, 300)
            anim.bloco_3d(ctx, -140, -20, 280, 70, 30, ACO)
            anim.bloco_3d(ctx, -80, -75, 150, 55, 30, ACO)
            ctx.set_source_rgba(0.6, 0.85, 1.0, 0.8)
            ctx.rectangle(-65, -65, 120, 38)
            ctx.fill()
            for wx in (-85, 85):
                anim.esfera(ctx, wx, 55, 30, (0.12, 0.12, 0.14))
            ctx.restore()
            anim.anel_destaque(ctx, tc - 0.3, 850, 1050, 190, cor=QUENTE, som=None)


def d_ingredientes(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.14, 0.12, 0.12), (0.04, 0.04, 0.05), bokeh=(1, 0.8, 0.6))
    itens = [("IRON ORE", (0.62, 0.25, 0.15), 230), ("COAL", (0.12, 0.12, 0.13), 540),
             ("LIMESTONE", (0.85, 0.83, 0.78), 850)]
    for i, (nome, cor, x) in enumerate(itens):
        ti = t - (0.5 + i * 0.75)
        core.evento_som("pop", ti)
        if ti < 0:
            continue
        k = max(core.mola(ti, 0.45), 0.001)
        ctx.save()
        ctx.translate(x, 1010)
        ctx.scale(k, k)
        anim.sombra_chao(ctx, 0, 95, 260)
        for j in range(7):   # monte de pedras
            px = (j % 4) * 52 - 78 + (26 if j >= 4 else 0)
            py = 60 - (j // 4) * 50
            anim.esfera(ctx, px, py, 36 + (j % 3) * 4, cor)
        ctx.restore()
        text_center(ctx, nome, x, 1150, 36, WHITE, "ExtraBold", alpha=min(1.0, ti * 3))
    anim.seta(ctx, t - 0.7, 230, 900, ang=math.pi / 2, cor=FUNDIDO)
    if t > 0.8:
        text_center(ctx, "= RUSTY ROCK", 230, 760, 34, FUNDIDO, "ExtraBold", alpha=min(1.0, (t - 0.8) * 3))


def d_alto_forno(ctx, t, s):
    anim.fundo_vivo(ctx, t, *ESCURO, bokeh=FUNDIDO)
    x, topo, alt = 540, 500, 560
    anim.sombra_chao(ctx, x, topo + alt + 20, 520)
    anim.cilindro(ctx, x, topo, 340, alt, (0.35, 0.35, 0.38))
    ctx.save()   # janela de corte mostrando o fogo dentro
    ctx.rectangle(x - 110, topo + 80, 220, alt - 160)
    ctx.clip()
    ctx.set_source_rgb(0.15, 0.05, 0.02)
    ctx.paint()
    anim.brilho(ctx, x, topo + alt - 120, 260, FUNDIDO, 0.9)
    for i in range(14):   # carga descendo
        yy = topo + 80 + ((t * 70 + i * 40) % (alt - 220))
        anim.esfera(ctx, x - 80 + (i * 37) % 160, yy, 16, [(0.62, 0.25, 0.15), (0.12, 0.12, 0.13)][i % 2])
    ctx.restore()
    for lado in (-1, 1):   # ar quente soprando embaixo
        anim.seta(ctx, t - 0.4, x + lado * 175, topo + alt - 90, ang=0 if lado < 0 else math.pi, cor=(0.5, 0.8, 1.0),
                  tam=70, som="swish" if lado < 0 else None)
    if len(s.items) > 1:
        m = s.mark(1)
        if t > m:
            k = ease((t - m) / 0.8)
            rio(ctx, t, x + 150, topo + alt - 40, x + 150 + 200 * k, topo + alt + 40, larg=30)
            anim.faiscas(ctx, t, x + 150 + 200 * k, topo + alt + 40, n=30, vel=400)
            anim.anel_destaque(ctx, t - m - 0.4, x + 330, topo + alt + 20, 90, cor=QUENTE)
            if t > m + 0.6:
                text_center(ctx, "MOLTEN IRON", x + 300, topo + alt - 110, 40, QUENTE, "ExtraBold")


def d_fragil(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.10, 0.10, 0.13), (0.03, 0.03, 0.05), bokeh=(0.7, 0.8, 1.0))
    quebra = 1.6
    ctx.save()
    anim.tremor(ctx, t - quebra)
    curva = 0.25 * ease(t / quebra)
    for lado in (-1, 1):   # barra dobrando e partindo no meio
        sep = 40 * ease((t - quebra) / 0.4)
        ctx.save()
        ctx.translate(540 + lado * (6 + sep), 980)
        ctx.rotate(lado * curva)
        x0 = 0 if lado > 0 else -380
        anim.bloco_3d(ctx, x0, -50, 380, 100, 50, (0.45, 0.45, 0.48))
        ctx.restore()
    ctx.restore()
    anim.estouro(ctx, t - quebra, 540, 960, cor=QUENTE)
    if t > quebra:
        anim.contador(ctx, t - quebra - 0.2, 540, 700, 4, dur=0.6, fmt="{:.0f}", sufixo="% CARBON", size=96,
                      cor=(1.0, 0.4, 0.35), som=None)


def d_oxigenio(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.12, 0.06, 0.04), (0.03, 0.02, 0.02), bokeh=FUNDIDO)
    sopro = 0.6
    ctx.save()
    anim.tremor(ctx, t - sopro, forca=22, dur=0.6)
    x, y = 540, 1000
    anim.sombra_chao(ctx, x, y + 190, 560)
    ctx.new_path()   # conversor em forma de pera
    ctx.move_to(x - 170, y - 120)
    ctx.curve_to(x - 260, y + 40, x - 220, y + 190, x, y + 190)
    ctx.curve_to(x + 220, y + 190, x + 260, y + 40, x + 170, y - 120)
    ctx.line_to(x + 90, y - 210)
    ctx.line_to(x - 90, y - 210)
    ctx.close_path()
    ctx.set_source_rgb(0.30, 0.30, 0.33)
    ctx.fill()
    ctx.set_source_rgb(0.15, 0.06, 0.03)
    ctx.save()
    ctx.translate(x, y - 205)
    ctx.scale(1, 0.25)
    ctx.arc(0, 0, 88, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    descida = ease(t / 0.6)   # lança descendo
    ctx.set_source_rgb(0.75, 0.78, 0.82)
    ctx.rectangle(x - 14, 640, 28, 150 + 200 * descida)
    ctx.fill()
    if t > sopro:
        anim.brilho(ctx, x, y - 210, 420, QUENTE, 0.8)
        anim.faiscas(ctx, t, x, y - 215, n=140, vel=900, g=1100, vida=1.0, ang=(-math.pi * 0.95, -math.pi * 0.05))
        anim.fumaca(ctx, t, x, y - 260, cor=(1.0, 0.7, 0.5), alpha=0.2)
    ctx.restore()
    if len(s.items) > 1:
        m = s.mark(1)
        anim.contador(ctx, t - m, 540, 600, 0.5, ini=4.0, dur=1.2, fmt="{:.1f}", sufixo="% C", size=96,
                      cor=QUENTE)


def d_laminacao(ctx, t, s):
    anim.fundo_vivo(ctx, t, *ESCURO, bokeh=FUNDIDO)
    y = 1000
    for i, x in enumerate((330, 600, 870)):   # pares de rolos girando
        for dy in (-1, 1):
            r = 70
            cy = y + dy * (r + 30 - i * 8)
            anim.esfera(ctx, x, cy, r, ACO)
            a = t * 6 * dy + i
            ctx.set_source_rgba(0, 0, 0, 0.35)
            ctx.set_line_width(6)
            ctx.move_to(x, cy)
            ctx.line_to(x + r * 0.8 * math.cos(a), cy + r * 0.8 * math.sin(a))
            ctx.stroke()
    off = (t * 260) % 260
    for j in range(-1, 6):   # placa ficando mais fina e mais fria a cada rolo
        x0 = -200 + j * 260 + off
        esp = 60 - 12 * max(0.0, min(3.0, (x0 - 200) / 270))
        f = max(0.0, min(1.0, (x0 - 100) / 900))
        cor = tuple(a + (b - a) * f for a, b in zip(QUENTE, (0.85, 0.30, 0.10)))
        ctx.set_source_rgb(*cor)
        ctx.rectangle(x0, y - esp / 2, 250, esp)
        ctx.fill()
    anim.brilho(ctx, 300, y, 300, FUNDIDO, 0.35)
    if len(s.items) > 1:
        m = s.mark(1)
        anim.seta(ctx, t - m, 870, y - 130, ang=math.pi / 2, cor=QUENTE)


def d_numero(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.10, 0.10, 0.16), (0.02, 0.02, 0.05), bokeh=(0.6, 0.8, 1.0))
    anim.contador(ctx, t - 0.2, 540, 760, 1.9, dur=1.3, fmt="{:.1f}", size=220, cor=WHITE)
    anim.texto_pop(ctx, t - 1.0, ["BILLION", "TONS", "A", "YEAR"], 540, 930, size=78, cor=QUENTE)
    if len(s.items) > 1:
        m = s.mark(1)
        anim.texto_pop(ctx, t - m, ["#1", "MOST", "RECYCLED"], 540, 1130, size=70, cor=(0.45, 0.9, 0.55),
                       intervalo=0.18)
        if t > m:
            anim.confete(ctx, t - m, n=40)


SEGMENTS = [
    Seg(["This river is hotter than lava.", "And soon it'll be part of a car."], d_gancho,
        {"title": "HOW IS STEEL MADE?"}, tail=0.2),
    Seg(["It starts as three things: rusty rock, coal, and limestone."], d_ingredientes,
        {"big": "3 INGREDIENTS", "big_size": 96, "color": QUENTE}, tail=0.2),
    Seg(["They go into a blast furnace, as tall as a building, with hot air roaring in.",
         "The coal steals the oxygen from the rock, and liquid iron pours out the bottom."], d_alto_forno,
        {"big": "BLAST FURNACE", "big_size": 92, "color": FUNDIDO}, tail=0.2),
    Seg(["But this iron is brittle. Too much carbon. Bend it, and it snaps."], d_fragil,
        {"big": "THE PROBLEM", "color": (1.0, 0.4, 0.35)}, tail=0.2),
    Seg(["So they blast pure oxygen into it, faster than sound.", "The carbon burns away in a storm of sparks."],
        d_oxigenio, {"big": "OXYGEN BLAST", "big_size": 96, "color": QUENTE}, tail=0.2),
    Seg(["Then it's cast into an endless glowing slab,", "and giant rollers squash it into sheets and beams."],
        d_laminacao, {"big": "SQUASH", "color": FUNDIDO}, tail=0.2),
    Seg(["The world makes almost two billion tons a year.", "And it's the most recycled material on Earth."],
        d_numero, {"big": "STEEL", "color": WHITE}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Name one thing with no steel in it.", "NAME ONE THING WITHOUT STEEL",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *ESCURO, bokeh=FUNDIDO)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
