"""How is pasta made? (2D, padrão caprichado). Fri 27/11/2026. Search 26/11: "how pasta is made" median 660k.

Facts:
- dried pasta is made from durum wheat semolina and water (Italian law requires durum wheat for dried pasta sold as
  pasta in Italy); fresh egg pasta is a different product;
- the dough is pushed (extruded) under high pressure through metal plates called dies; the die's holes decide the
  shape; a rotating knife cuts short shapes;
- bronze dies leave a rough, porous surface that holds sauce better; non-stick (Teflon) dies make smooth, shiny pasta
  faster;
- industrial pasta is dried at high temperature in hours; traditional makers dry it slowly at low temperature, often
  for a day or two; dried pasta is about 12% water.
Tone: curious/alegre -> pop? Use "lista"? -> pop for variety.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import anim  # noqa: E402
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import W, WHITE, Seg, render, text_center  # noqa: E402

core.MUSICA = "animado"   # -> pop
MASSA = (0.98, 0.85, 0.48)
BRONZE = (0.80, 0.55, 0.30)
TEFLON = (0.30, 0.32, 0.36)
MOLHO = (0.85, 0.18, 0.12)
VERDE = (0.25, 0.60, 0.30)
FUNDO = ((0.70, 0.18, 0.14), (0.25, 0.05, 0.04))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def tubo(ctx, x, y, s, cor, rugoso=False, molho=0.0, ang=0.0):
    """Penne visto de lado: tubo com pontas em diagonal; rugoso = textura áspera; molho 0..1 agarrado."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    ctx.new_path()
    ctx.move_to(-120, -40)
    ctx.line_to(90, -40)
    ctx.line_to(130, 40)
    ctx.line_to(-80, 40)
    ctx.close_path()
    ctx.set_source_rgb(*cor)
    ctx.fill_preserve()
    ctx.save()
    ctx.clip()
    ctx.set_source_rgba(0, 0, 0, 0.12)
    for k in range(-6, 8):   # estrias
        ctx.rectangle(k * 22, -40, 6, 80)
    ctx.fill()
    if rugoso:
        for i in range(60):
            ctx.set_source_rgba(1, 1, 1, 0.35)
            ctx.arc(-110 + (i * 37) % 230, -36 + (i * 13) % 72, 2.2, 0, 2 * math.pi)
            ctx.fill()
    else:
        ctx.set_source_rgba(1, 1, 1, 0.45)   # brilho liso
        ctx.rectangle(-110, -30, 220, 10)
        ctx.fill()
    if molho > 0:
        ctx.set_source_rgba(*MOLHO, 0.9 * molho)
        for i in range(10 if rugoso else 3):
            ctx.arc(-90 + i * 22, -10 + 20 * math.sin(i * 1.7), 14, 0, 2 * math.pi)
            ctx.fill()
    ctx.restore()
    ctx.restore()


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 0.8, 0.6))
    m1 = s.mark(1) if len(s.items) > 1 else 99
    entra = ease(t / 0.5)
    tubo(ctx, 300, 900 - 260 * (1 - entra), 1.4, MASSA, rugoso=False, molho=ease((t - 1.0) / 0.8))
    tubo(ctx, 780, 900 + 260 * (1 - entra), 1.4, MASSA, rugoso=True, molho=ease((t - 1.0) / 0.8))
    text_center(ctx, "SMOOTH", 300, 1040, 44, WHITE, "ExtraBold", alpha=entra)
    text_center(ctx, "ROUGH", 780, 1040, 44, WHITE, "ExtraBold", alpha=entra)
    for i in range(8):   # gotas de molho caindo nas duas
        f = (t * 0.9 + i * 0.125) % 1.0
        anim.esfera(ctx, 240 + (i % 4) * 40 + (480 if i >= 4 else 0), 600 + f * 240, 12, MOLHO)
    if t > m1:
        anim.anel_destaque(ctx, t - m1, 780, 900, 220, cor=(1, 0.9, 0.4))
        anim.texto_pop(ctx, t - m1, ["ROUGH", "WINS"], 540, 560, size=96, cor=(1, 0.9, 0.4))


def d_ingred(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 0.8, 0.6))
    for i, (nome, cor, x) in enumerate((("SEMOLINA", MASSA, 320), ("WATER", (0.55, 0.80, 1.0), 760))):
        ti = t - 0.3 - i * 0.7
        core.evento_som("pop", ti)
        if ti < 0:
            continue
        k = max(core.mola(ti, 0.45), 0.001)
        ctx.save()
        ctx.translate(x, 860)
        ctx.scale(k, k)
        anim.sombra_chao(ctx, 0, 140, 260)
        anim.cilindro(ctx, 0, -110, 220, 240, cor)
        text_center(ctx, nome, 0, 190, 40, WHITE, "ExtraBold")
        ctx.restore()
    anim.texto_pop(ctx, t - 1.8, ["NO", "EGGS"], 540, 560, size=96, cor=WHITE)


def d_extrusao(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.22, 0.24, 0.28), (0.05, 0.06, 0.08), bokeh=(1, 0.9, 0.7))
    anim.sombra_chao(ctx, 540, 1190, 600)
    anim.cilindro(ctx, 540, 600, 300, 280, (0.62, 0.65, 0.70))   # extrusora
    for k in range(8):   # rosca empurrando
        y = 620 + ((t * 120 + k * 35) % 260)
        ctx.set_source_rgba(0.35, 0.36, 0.40, 0.8)
        ctx.set_line_width(8)
        ctx.move_to(420, y)
        ctx.line_to(660, y + 18)
        ctx.stroke()
    anim.bloco_3d(ctx, 380, 880, 320, 40, 30, BRONZE)   # matriz
    for i in range(6):   # fios de massa saindo e sendo cortados
        x = 410 + i * 52
        comp = 60 + ((t * 160) % 120)
        ctx.set_source_rgb(*MASSA)
        ctx.rectangle(x, 920, 28, comp)
        ctx.fill()
    faca = (t * 1.3) % 1.0   # faca giratória
    ctx.save()
    ctx.translate(540, 1050)
    ctx.rotate(faca * 2 * math.pi)
    ctx.set_source_rgb(0.85, 0.87, 0.90)
    ctx.rectangle(-180, -6, 360, 12)
    ctx.fill()
    ctx.restore()
    anim.texto_pop(ctx, t - 0.4, ["PUSHED", "THROUGH", "A", "DIE"], 540, 500, size=62, cor=WHITE, intervalo=0.16, largura=1000)


def d_matrizes(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 0.8, 0.6))
    formas = ["○", "◎", "✱", "≈"]
    for i in range(4):   # quatro matrizes diferentes, uma forma cada
        ti = t - 0.3 - i * 0.5
        core.evento_som("pop", ti)
        if ti < 0:
            continue
        k = max(core.mola(ti, 0.4), 0.001)
        x = 230 + (i % 2) * 620
        y = 760 + (i // 2) * 300
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(k, k)
        anim.esfera(ctx, 0, 0, 110, BRONZE)
        ctx.restore()
        tubo(ctx, x + (310 if i % 2 == 0 else -310), y, 0.8, MASSA, ang=0.4 * (i - 1.5))
    anim.texto_pop(ctx, t - 0.4, ["THE", "HOLE", "=", "THE", "SHAPE"], 540, 560, size=74, cor=WHITE, intervalo=0.15)


def d_bronze(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 0.8, 0.6))
    anim.esfera(ctx, 300, 820, 120, BRONZE)
    text_center(ctx, "BRONZE", 300, 990, 44, WHITE, "ExtraBold")
    anim.esfera(ctx, 780, 820, 120, TEFLON)
    text_center(ctx, "NON-STICK", 780, 990, 44, WHITE, "ExtraBold")
    tubo(ctx, 300, 1100, 0.9, MASSA, rugoso=True, molho=ease((t - 1.5) / 0.8))
    tubo(ctx, 780, 1100, 0.9, MASSA, rugoso=False, molho=ease((t - 1.5) / 0.8))
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["SAUCE", "STICKS"], 300, 560, size=72, cor=(1, 0.9, 0.4), largura=520)
    anim.anel_destaque(ctx, t - 2.2, 300, 1100, 105, cor=(1, 0.9, 0.4))


def d_secagem(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.75, 0.58, 0.30), (0.35, 0.22, 0.08), bokeh=(1, 1, 0.8))
    for r in range(3):   # varas com massa pendurada secando
        y = 700 + r * 170
        ctx.set_source_rgb(0.45, 0.30, 0.18)
        ctx.rectangle(140, y, 800, 14)
        ctx.fill()
        for i in range(24):
            x = 160 + i * 32
            ctx.set_source_rgb(*MASSA)
            ctx.rectangle(x, y + 14, 8, 120 + 6 * math.sin(t * 2 + i + r))
            ctx.fill()
    anim.contador(ctx, t - 0.3, 540, 560, 48, dur=1.3, sufixo=" HOURS", size=96, cor=WHITE)


SEGMENTS = [
    Seg(["Smooth pasta or rough pasta? Pour on the sauce,", "and the rough one wins every time."], d_gancho,
        {"title": "HOW IS PASTA MADE?"}, tail=0.2),
    Seg(["Dry pasta is just two things: durum wheat semolina and water. No eggs."], d_ingred,
        {"big": "THE DOUGH", "color": MASSA}, tail=0.2),
    Seg(["A giant screw pushes the dough through a metal plate called a die, and a spinning knife cuts it."],
        d_extrusao, {"big": "THE PRESS", "color": WHITE}, tail=0.2),
    Seg(["Every shape has its own die. The holes decide if it's spaghetti, penne, or a spiral."], d_matrizes,
        {"big": "THE SHAPES", "color": MASSA}, tail=0.2),
    Seg(["Old school dies are bronze. They scratch the pasta and leave it rough,", "so the sauce clings."],
        d_bronze, {"big": "THE SECRET", "color": (1, 0.85, 0.55)}, tail=0.2),
    Seg(["Then it dries, fast in big factories, or slowly for up to two days in traditional ones."], d_secagem,
        {"big": "DRY", "color": WHITE}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("What's your favorite pasta shape?", "FAVORITE SHAPE?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
