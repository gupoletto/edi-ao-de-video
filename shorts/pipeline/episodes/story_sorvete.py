"""How is ice cream made? (2D, padrão caprichado). Wed 25/11/2026. Search 25/11: "how ice cream is made" median 3.27M.

Facts:
- whipped-in air is called "overrun"; cheaper ice creams reach 100% overrun, meaning the tub is about half air by
  volume; premium brands use less (around 20-50%);
- the mix is milk, cream, sugar and stabilizers; it is pasteurized (heated to roughly 80 C), homogenized (fat broken
  into tiny droplets) and aged cold for hours;
- a continuous freezer chills it to about -5 C while blades whip air in and scrape ice off the walls;
- mix-ins are added, then it is "hardened" fast at around -30 to -40 C so the ice crystals stay tiny: that is what
  makes it smooth instead of icy.
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
ROSA = (1.0, 0.62, 0.72)
CREME = (0.99, 0.95, 0.85)
CHOC = (0.45, 0.26, 0.15)
AZUL = (0.55, 0.85, 1.0)
AMAR = (1.0, 0.85, 0.3)
FUNDO = ((0.98, 0.84, 0.88), (0.80, 0.55, 0.65))
FUNDO_FRIO = ((0.20, 0.35, 0.55), (0.05, 0.10, 0.20))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def casquinha(ctx, x, y, s=1.0, bolas=(ROSA, CREME, CHOC), ar=0.0, t=0.0):
    """Casquinha com bolas; ar 0..1 mostra bolhas de ar dentro das bolas."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    anim.sombra_chao(ctx, 0, 300, 200)
    ctx.new_path()
    ctx.move_to(-90, 0)
    ctx.line_to(90, 0)
    ctx.line_to(0, 290)
    ctx.close_path()
    ctx.set_source_rgb(0.85, 0.62, 0.32)
    ctx.fill_preserve()
    ctx.save()
    ctx.clip()   # quadriculado só dentro do cone
    ctx.set_source_rgba(0.6, 0.4, 0.18, 0.8)
    ctx.set_line_width(4)
    for k in range(-4, 5):
        ctx.move_to(-90 + k * 20, 0)
        ctx.line_to(k * 20 + 40, 200)
        ctx.move_to(90 - k * 20, 0)
        ctx.line_to(-k * 20 - 40, 200)
    ctx.stroke()
    ctx.restore()
    for i, cor in enumerate(bolas):
        by = -60 - i * 110
        anim.esfera(ctx, 0, by, 100, cor)
        if ar > 0:
            for j in range(14):
                a = j * 2.4 + t
                r = 70 * ((j * 37 % 10) / 10)
                ctx.new_path()
                ctx.set_source_rgba(1, 1, 1, 0.85 * ar)
                ctx.arc(r * math.cos(a), by + r * math.sin(a) * 0.8, 7 + j % 4, 0, 2 * math.pi)
                ctx.fill()
    ctx.restore()


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    m1 = s.mark(1) if len(s.items) > 1 else 99
    entra = ease(t / 0.6)
    casquinha(ctx, 540, 880 + 400 * (1 - entra), 0.85, ar=ease((t - m1) / 0.6), t=t)
    anim.contador(ctx, t - 0.2, 540, 520, 50, dur=1.2, sufixo="% AIR", size=120, cor=WHITE)
    if t > m1:
        anim.anel_destaque(ctx, t - m1 - 0.2, 540, 730, 210, cor=WHITE)


def d_mistura(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    itens = [("MILK", (0.97, 0.97, 0.98), 260), ("CREAM", CREME, 540), ("SUGAR", (1, 1, 1), 820)]
    for i, (nome, cor, x) in enumerate(itens):
        ti = t - 0.3 - i * 0.6
        core.evento_som("pop", ti)
        if ti < 0:
            continue
        k = max(core.mola(ti, 0.45), 0.001)
        ctx.save()
        ctx.translate(x, 960)
        ctx.scale(k, k)
        anim.cilindro(ctx, 0, -120, 170, 230, cor)
        text_center(ctx, nome, 0, 190, 40, (0.45, 0.15, 0.25), "ExtraBold")
        ctx.restore()
    anim.contador(ctx, t - 2.4, 540, 560, 80, dur=1.0, sufixo=" °C", size=100, cor=(0.9, 0.3, 0.2))


def d_freezer(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO_FRIO, bokeh=AZUL)
    anim.sombra_chao(ctx, 540, 1180, 760)
    anim.cilindro(ctx, 540, 720, 360, 440, (0.75, 0.78, 0.84))
    ctx.save()   # janela no tambor: pás girando e bolhas entrando
    ctx.rectangle(400, 780, 280, 320)
    ctx.clip()
    ctx.set_source_rgb(*CREME)
    ctx.paint()
    for k in range(4):
        a = t * 5 + k * math.pi / 2
        ctx.set_source_rgba(0.55, 0.58, 0.64, 0.9)
        ctx.set_line_width(16)
        ctx.move_to(540, 940)
        ctx.line_to(540 + 160 * math.cos(a), 940 + 160 * math.sin(a) * 0.4)
        ctx.stroke()
    anim.bolhas(ctx, t, 400, 680, 780, 1100, n=40, r=10, alpha=0.9)
    ctx.restore()
    for lado in (-1, 1):
        anim.seta(ctx, t - 0.5, 540 + lado * 200, 940, ang=0 if lado < 0 else math.pi, cor=AZUL, tam=70,
                  som="swish" if lado < 0 else None)
    anim.contador(ctx, t - 0.3, 540, 560, -5, dur=1.0, fmt="{:.0f}", sufixo=" °C", size=100, cor=AZUL)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["WHIPPING", "IN", "AIR"], 540, 650, size=72, cor=WHITE)


def d_misturas(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    anim.sombra_chao(ctx, 540, 1170, 520)
    anim.bloco_3d(ctx, 290, 900, 500, 260, 50, CREME)   # pote
    for i in range(40):   # gotas de chocolate e granulado chovendo
        f = (t * 0.8 + i * 0.037) % 1.0
        x = 320 + (i * 53) % 440
        y = 560 + f * 360
        ctx.new_path()
        ctx.set_source_rgb(*(CHOC if i % 3 else ROSA))
        ctx.arc(x, y, 9, 0, 2 * math.pi)
        ctx.fill()
    anim.texto_pop(ctx, t - 0.3, ["CHUNKS", "GO", "IN"], 540, 560, size=88, cor=WHITE, cor_destaque=CHOC, destaque=0)


def d_tunel(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO_FRIO, bokeh=AZUL)
    anim.tremor(ctx, t - 0.3, forca=8, dur=0.3, som="swish")
    for i in range(5):   # potes atravessando o túnel de congelamento
        x = -200 + ((t * 230 + i * 280) % 1400)
        anim.bloco_3d(ctx, x, 980, 160, 110, 30, CREME)
    ctx.set_source_rgba(0.75, 0.9, 1.0, 0.25)   # paredes do túnel
    ctx.rectangle(0, 860, W, 300)
    ctx.fill()
    for i in range(40):   # flocos de gelo
        x = (i * 97 + t * 60) % W
        y = 760 + (i * 53 % 420)
        ctx.new_path()
        ctx.set_source_rgba(1, 1, 1, 0.8)
        ctx.arc(x, y, 3 + i % 3, 0, 2 * math.pi)
        ctx.fill()
    anim.contador(ctx, t - 0.3, 540, 560, -35, dur=1.2, fmt="{:.0f}", sufixo=" °C", size=110, cor=AZUL)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["TINY", "CRYSTALS"], 540, 700, size=80, cor=WHITE)


def d_fim(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    casquinha(ctx, 540, 880, 0.85, t=t)
    anim.confete(ctx, t, n=40)
    anim.texto_pop(ctx, t - 0.3, ["SMOOTH,", "NOT", "ICY"], 540, 520, size=88, cor=WHITE)


SEGMENTS = [
    Seg(["Your ice cream might be half air.", "And that's on purpose."], d_gancho,
        {"title": "HOW IS ICE CREAM MADE?"}, tail=0.2),
    Seg(["It starts as milk, cream and sugar, heated to about eighty degrees to kill any germs."], d_mistura,
        {"big": "THE MIX", "color": (0.55, 0.18, 0.30)}, tail=0.2),
    Seg(["Then it goes into a freezer with spinning blades.", "They chill it and whip air in at the same time."],
        d_freezer, {"big": "FREEZE", "color": AZUL}, tail=0.2),
    Seg(["Cheap tubs can be fifty percent air. Premium ones, much less. Then come the chunks."], d_misturas,
        {"big": "THE AIR", "color": (0.55, 0.18, 0.30)}, tail=0.2),
    Seg(["Last, a tunnel at minus thirty five freezes it fast,", "so the ice crystals stay tiny."], d_tunel,
        {"big": "HARDEN", "color": AZUL}, tail=0.2),
    Seg(["That's the secret: tiny crystals feel smooth. Big ones feel icy."], d_fim,
        {"big": "SMOOTH", "color": (0.55, 0.18, 0.30)}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("What's the best ice cream flavor?", "BEST FLAVOR?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
