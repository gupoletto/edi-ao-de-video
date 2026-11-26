"""How is soap made? (2D, padrão caprichado). Thu 26/11/2026. Search 26/11: "how soap is made" median 1.14M.

Facts:
- soap is made by saponification: fats or oils react with a strong alkali (lye, sodium hydroxide) and turn into soap
  plus glycerin; lye on its own burns skin, but none is left once the reaction is complete;
- one of the oldest records of soap making is from ancient Babylon, around 2800 BC (fats boiled with wood ash);
- a soap molecule has a water-loving head and an oil-loving tail; the tails grab grease, the molecules surround it
  in tiny balls (micelles), and water rinses it away;
- in factories the soap is dried into small pellets/"noodles", mixed with fragrance and color, milled, squeezed into
  a long bar (extruded), then cut and stamped.
Tone: curious -> lofi.
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
SABAO = (0.62, 0.86, 0.80)
ROSA = (1.0, 0.70, 0.80)
GORDURA = (1.0, 0.92, 0.60)
SODA = (0.85, 0.92, 1.0)
PERIGO = (1.0, 0.35, 0.30)
AMAR = (1.0, 0.85, 0.3)
FUNDO = ((0.20, 0.36, 0.42), (0.05, 0.10, 0.13))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def barra(ctx, x, y, cor, s=1.0, texto=None):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    anim.sombra_chao(ctx, 0, 90, 360)
    anim.bloco_3d(ctx, -170, -60, 340, 140, 60, cor)
    if texto:
        text_center(ctx, texto, 0, 25, 40, (1, 1, 1), "ExtraBold", alpha=0.7)
    ctx.restore()


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(0.7, 1, 0.95))
    anim.bolhas(ctx, t, 200, 880, 600, 1200, n=30, r=14, alpha=0.6)
    entra = ease(t / 0.6)
    barra(ctx, 540, 900 + 300 * (1 - entra), SABAO, 1.3)
    m1 = s.mark(1) if len(s.items) > 1 else 99
    anim.texto_pop(ctx, t - 0.4, ["MADE", "WITH", "FAT"], 540, 540, size=96, cor=WHITE, cor_destaque=GORDURA, destaque=2)
    if t > m1:
        anim.texto_pop(ctx, t - m1, ["AND", "LYE"], 540, 680, size=96, cor=PERIGO, intervalo=0.25)
        anim.estouro(ctx, t - m1 - 0.25, 540, 680, cor=PERIGO, r0=150, r1=280)


def d_receita(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(0.7, 1, 0.95))
    for i, (nome, cor, x) in enumerate((("OIL / FAT", GORDURA, 300), ("LYE", SODA, 780))):
        ti = t - 0.3 - i * 0.8
        core.evento_som("pop", ti)
        if ti < 0:
            continue
        k = max(core.mola(ti, 0.45), 0.001)
        ctx.save()
        ctx.translate(x, 900)
        ctx.scale(k, k)
        anim.cilindro(ctx, 0, -130, 200, 260, cor)
        text_center(ctx, nome, 0, 200, 42, WHITE, "ExtraBold")
        ctx.restore()
    if t > 1.3:   # selo de perigo na soda
        anim.esfera(ctx, 870, 800, 34, PERIGO)
        text_center(ctx, "!", 870, 815, 40, WHITE, "ExtraBold")
    anim.texto_pop(ctx, t - 2.0, ["BURNS", "SKIN"], 540, 560, size=88, cor=PERIGO)


def d_reacao(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.30, 0.22, 0.15), (0.08, 0.05, 0.03), bokeh=AMAR)
    k = ease((t - 0.5) / 2.5)
    anim.sombra_chao(ctx, 540, 1180, 640)
    anim.cilindro(ctx, 540, 720, 520, 420, (0.55, 0.57, 0.62))
    ctx.save()
    ctx.new_path()
    ctx.rectangle(300, 760, 480, 360)
    ctx.clip()
    cor = tuple(a + (b - a) * k for a, b in zip(GORDURA, SABAO))
    ctx.set_source_rgb(*cor)
    ctx.paint()
    for i in range(6):   # pá misturando
        a = t * 3 + i
        ctx.set_source_rgba(1, 1, 1, 0.35)
        ctx.set_line_width(6)
        ctx.arc(540, 940, 60 + i * 25, a, a + 1.2)
        ctx.stroke()
    ctx.restore()
    anim.fumaca(ctx, t, 540, 720, cor=(1, 1, 1), alpha=0.18)
    anim.texto_pop(ctx, t - 0.4, ["SOAP", "+", "GLYCERIN"], 540, 560, size=84, cor=WHITE, cor_destaque=SABAO, destaque=0)
    if len(s.items) > 1:
        anim.anel_destaque(ctx, t - s.mark(1), 540, 940, 220, cor=AMAR)


def d_babilonia(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.55, 0.40, 0.22), (0.20, 0.12, 0.06), bokeh=AMAR)
    anim.sombra_chao(ctx, 540, 1180, 600)
    for i in range(3):   # zigurate em degraus
        w = 560 - i * 150
        anim.bloco_3d(ctx, 540 - w / 2, 1040 - i * 120, w, 120, 40, (0.80, 0.62, 0.38))
    anim.contador(ctx, t - 0.3, 540, 560, 2800, ini=0, dur=1.4, fmt="{:.0f}", sufixo=" BC", size=110, cor=WHITE,
                  som=None)
    anim.texto_pop(ctx, t - 1.8, ["BABYLON"], 540, 690, size=84, cor=AMAR)


def molecula(ctx, x, y, ang, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    ctx.set_source_rgb(0.95, 0.85, 0.45)   # cauda que gosta de gordura
    ctx.set_line_width(6)
    ctx.move_to(0, 0)
    for k in range(1, 6):
        ctx.line_to(k * 14, (-1) ** k * 8)
    ctx.stroke()
    anim.esfera(ctx, 0, 0, 14, (0.35, 0.70, 1.0))   # cabeça que gosta de água
    ctx.restore()


def d_limpa(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.18, 0.42, 0.62), (0.04, 0.12, 0.22), bokeh=(0.8, 0.95, 1))
    k = ease((t - 0.8) / 1.5)
    cx, cy = 540, 900
    ctx.new_path()   # gota de gordura no centro
    ctx.arc(cx, cy, 90, 0, 2 * math.pi)
    ctx.set_source_rgb(0.85, 0.65, 0.25)
    ctx.fill()
    for i in range(16):   # moléculas cercando a gordura (micela)
        a = i * 2 * math.pi / 16 + t * 0.3
        r = 360 - 200 * k
        molecula(ctx, cx + r * math.cos(a), cy + r * math.sin(a), a + math.pi, 1.0)
    if len(s.items) > 1:
        m = s.mark(1)
        sai = ease((t - m) / 1.0)
        anim.seta(ctx, t - m, cx + 250, cy + 40 - 0, ang=0, cor=WHITE, som="swish")
        anim.texto_pop(ctx, t - m, ["RINSED", "AWAY"], 540, 560, size=90, cor=WHITE)
    else:
        anim.texto_pop(ctx, t - 0.5, ["GRABS", "GREASE"], 540, 560, size=90, cor=WHITE)


def d_fabrica(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(0.7, 1, 0.95))
    ctx.set_source_rgb(0.25, 0.27, 0.30)   # esteira
    ctx.rectangle(0, 1110, W, 26)
    ctx.fill()
    for i in range(6):   # barras saindo da extrusora e sendo carimbadas
        x = -200 + ((t * 220 + i * 260) % 1500)
        carimbada = x > 560
        barra(ctx, x, 1030, ROSA if i % 2 else SABAO, 0.55, texto="FUN" if carimbada else None)
    desce = abs(math.sin(t * 2.6))   # carimbo
    anim.bloco_3d(ctx, 490, 760 + 110 * desce, 160, 90, 30, (0.45, 0.47, 0.52))
    if desce > 0.97:
        core.evento_som("thud", 0.0)
    anim.texto_pop(ctx, t - 0.4, ["CUT", "&", "STAMPED"], 540, 560, size=88, cor=WHITE)


SEGMENTS = [
    Seg(["Your soap was made from fat,", "and a chemical that can burn your skin."], d_gancho,
        {"title": "HOW IS SOAP MADE?"}, tail=0.2),
    Seg(["The recipe is just two things: oil or fat, and lye, a strong alkali."], d_receita,
        {"big": "THE RECIPE", "color": SABAO}, tail=0.2),
    Seg(["Mix them, and a reaction turns the fat into soap and glycerin.", "When it's done, no lye is left."],
        d_reacao, {"big": "THE REACTION", "big_size": 92, "color": AMAR}, tail=0.2),
    Seg(["People were doing this in Babylon almost five thousand years ago, with animal fat and wood ash."],
        d_babilonia, {"big": "ANCIENT", "color": AMAR}, tail=0.2),
    Seg(["Each soap molecule has a head that loves water and a tail that loves grease. The tails grab the dirt,",
         "and water carries it away."], d_limpa, {"big": "HOW IT CLEANS", "big_size": 92, "color": (0.6, 0.85, 1.0)},
        tail=0.2),
    Seg(["In factories, the soap is dried, scented, squeezed into a long bar, then cut and stamped."], d_fabrica,
        {"big": "THE FACTORY", "color": SABAO}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Bar soap or liquid soap?", "BAR OR LIQUID?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
