"""How is coffee made? (2D, padrão caprichado). Thu 26/11/2026. Search 26/11: "how coffee is made" median 696k.

Facts:
- coffee "beans" are the seeds of a red fruit, the coffee cherry; most cherries hold two seeds;
- Brazil is the world's largest coffee producer;
- after picking, the fruit is removed (washed process, or dried in the sun first: natural process), leaving pale
  green beans that smell grassy, not like coffee;
- roasting at roughly 200-230 C for about 10-15 minutes; around 196 C the beans "crack" (first crack) with a popping
  sound like popcorn; browning reactions (Maillard) create the coffee aroma;
- roasted beans are ground and brewed with hot water.
Legend (said as legend): a goat herder named Kaldi noticed his goats got energetic after eating the cherries.
Tone: curious/warm -> lofi.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import anim  # noqa: E402
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import W, WHITE, Seg, render, text_center  # noqa: E402

core.MUSICA = "curioso"
CEREJA = (0.85, 0.12, 0.15)
VERDE_GRAO = (0.66, 0.74, 0.50)
CAFE = (0.32, 0.18, 0.10)
CREME = (0.86, 0.68, 0.45)
FOLHA = (0.20, 0.55, 0.25)
FUNDO = ((0.30, 0.20, 0.13), (0.08, 0.05, 0.03))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def grao(ctx, x, y, r, cor, ang=0.0):
    """Grão (semente) oval com a fenda no meio."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(1, 0.72)
    anim.esfera(ctx, 0, 0, r, cor)
    ctx.restore()
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.set_source_rgba(0, 0, 0, 0.45)
    ctx.set_line_width(max(2, r * 0.12))
    ctx.move_to(-r * 0.7, 0)
    ctx.curve_to(-r * 0.2, -r * 0.2, r * 0.2, r * 0.2, r * 0.7, 0)
    ctx.stroke()
    ctx.restore()


def cereja(ctx, x, y, r, aberta=0.0):
    anim.esfera(ctx, x, y, r, CEREJA)
    if aberta > 0:   # duas sementes saindo
        grao(ctx, x - r * 0.9 * aberta - 10, y + 10, r * 0.6, VERDE_GRAO, -0.3)
        grao(ctx, x + r * 0.9 * aberta + 10, y + 10, r * 0.6, VERDE_GRAO, 0.3)


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 0.8, 0.6))
    m1 = s.mark(1) if len(s.items) > 1 else 99
    # galho com cerejas desde o quadro 0
    ctx.set_source_rgb(0.35, 0.22, 0.12)
    ctx.set_line_width(14)
    ctx.move_to(120, 700)
    ctx.curve_to(400, 760, 700, 720, 980, 800)
    ctx.stroke()
    for i, x in enumerate((300, 420, 560, 700, 840)):
        y = 770 + 10 * math.sin(t * 2 + i) + (i % 2) * 30
        ctx.new_path()
        ctx.set_source_rgb(*FOLHA)
        ctx.save()
        ctx.translate(x - 40, y - 70)
        ctx.rotate(-0.5)
        ctx.scale(1, 0.45)
        ctx.arc(0, 0, 60, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
        cereja(ctx, x, y, 44, aberta=ease((t - m1 - 0.1 * i) / 0.6) if i == 2 else 0.0)
    anim.texto_pop(ctx, t - 0.3, ["NOT", "A", "BEAN"], 540, 540, size=100, cor=WHITE, cor_destaque=CEREJA, destaque=2)
    if t > m1:
        anim.anel_destaque(ctx, t - m1 - 0.4, 560, 790, 120, cor=(1, 0.85, 0.3))


def d_colheita(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.30, 0.55, 0.35), (0.07, 0.18, 0.10), bokeh=(0.9, 1, 0.8))
    for i in range(30):   # cerejas caindo num cesto
        f = (t * 0.9 + i * 0.033) % 1.0
        x = 320 + (i * 47) % 440
        anim.esfera(ctx, x, 690 + f * 300, 22, CEREJA)
    anim.sombra_chao(ctx, 540, 1180, 560)
    anim.cilindro(ctx, 540, 980, 460, 190, (0.70, 0.52, 0.30))
    anim.texto_pop(ctx, t - 0.5, ["#1", "BRAZIL"], 540, 560, size=96, cor=(1, 0.85, 0.3))


def d_verde(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.75, 0.62, 0.40), (0.40, 0.28, 0.14), bokeh=(1, 1, 0.8))
    for i in range(18):   # grãos verdes secando ao sol, sendo revirados
        x = 260 + (i % 6) * 110
        y = 900 + (i // 6) * 90
        grao(ctx, x, y, 36, VERDE_GRAO, ang=0.4 * math.sin(t * 2 + i))
    anim.brilho(ctx, 900, 560, 200, (1, 0.9, 0.5), 0.7)   # sol
    anim.esfera(ctx, 900, 560, 70, (1, 0.85, 0.35))
    anim.texto_pop(ctx, t - 0.4, ["GREEN", "&", "GRASSY"], 460, 560, size=80, cor=WHITE, cor_destaque=VERDE_GRAO,
                   destaque=0, largura=560)


def d_torra(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 0.6, 0.3))
    k = ease(t / 4.0)
    anim.sombra_chao(ctx, 540, 1190, 640)
    anim.cilindro(ctx, 540, 740, 520, 420, (0.30, 0.30, 0.33))
    ctx.save()
    ctx.new_path()
    ctx.arc(540, 950, 170, 0, 2 * math.pi)
    ctx.clip()
    ctx.set_source_rgb(0.12, 0.06, 0.03)
    ctx.paint()
    for i in range(22):   # grãos girando e escurecendo
        a = t * 3 + i * 0.29
        r = 30 + (i * 37) % 120
        cor = tuple(a_ + (b - a_) * k for a_, b in zip(VERDE_GRAO, CAFE))
        grao(ctx, 540 + r * math.cos(a), 950 + r * math.sin(a), 22, cor, ang=a)
    ctx.restore()
    anim.brilho(ctx, 540, 950, 260, (1, 0.5, 0.2), 0.3)
    anim.contador(ctx, t - 0.2, 540, 560, 220, dur=1.4, sufixo=" °C", size=100, cor=(1, 0.55, 0.2))
    if len(s.items) > 1:
        m = s.mark(1)
        anim.texto_pop(ctx, t - m, ["CRACK!"], 540, 690, size=90, cor=WHITE)
        anim.estouro(ctx, t - m, 540, 950, cor=(1, 0.8, 0.4), r0=180, r1=320)
        anim.tremor(ctx, t - m, forca=10, dur=0.3, som=None)


def d_xicara(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 0.8, 0.6))
    anim.sombra_chao(ctx, 540, 1140, 520)
    ctx.new_path()   # pires
    ctx.save()
    ctx.translate(540, 1110)
    ctx.scale(1, 0.25)
    ctx.arc(0, 0, 260, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgb(0.92, 0.92, 0.90)
    ctx.fill()
    anim.cilindro(ctx, 540, 860, 340, 240, (0.97, 0.97, 0.95))
    ctx.new_path()   # café na xícara
    ctx.save()
    ctx.translate(540, 860)
    ctx.scale(170, 27)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgb(*CAFE)
    ctx.fill()
    ctx.set_source_rgb(0.97, 0.97, 0.95)   # alça
    ctx.set_line_width(26)
    ctx.arc(720, 960, 60, -1.2, 1.2)
    ctx.stroke()
    anim.fumaca(ctx, t, 540, 830, cor=(1, 1, 1), alpha=0.22)
    anim.texto_pop(ctx, t - 0.3, ["FROM", "FRUIT", "TO", "CUP"], 540, 560, size=86, cor=WHITE, cor_destaque=CEREJA,
                   destaque=1, intervalo=0.18)


SEGMENTS = [
    Seg(["Coffee beans aren't beans.", "They're the seeds of a red fruit."], d_gancho,
        {"title": "HOW IS COFFEE MADE?"}, tail=0.2),
    Seg(["The coffee cherry grows on bushes, mostly near the equator. Brazil grows more than anyone."], d_colheita,
        {"big": "THE HARVEST", "color": (1, 0.85, 0.3)}, tail=0.2),
    Seg(["The fruit is stripped off, and the seeds are dried. At this point they're green, and smell like grass."],
        d_verde, {"big": "GREEN BEANS", "big_size": 96, "color": VERDE_GRAO}, tail=0.2),
    Seg(["The magic is roasting: around two hundred twenty degrees for about twelve minutes.",
         "The beans crack, like popcorn, and that's when the coffee smell is born."], d_torra,
        {"big": "THE ROAST", "color": (1, 0.55, 0.2)}, tail=0.2),
    Seg(["Then they're ground, and hot water pulls out the flavor. Fruit seed to cup."], d_xicara,
        {"big": "BREW", "color": CREME}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("How many coffees a day? Be honest.", "HOW MANY A DAY?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
