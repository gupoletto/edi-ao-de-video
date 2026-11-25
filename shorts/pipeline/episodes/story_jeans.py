"""How are jeans made? (2D, padrão caprichado). Wed 25/11/2026. Search 25/11: "how jeans are made" median 390k.

Facts:
- the tiny front pocket was added in the 1870s for pocket watches (often called the watch pocket);
- copper rivets on pocket corners were patented in 1873 by tailor Jacob Davis and fabric seller Levi Strauss, to stop
  work pants from ripping;
- denim is cotton twill: blue (indigo) threads run lengthwise and white threads run across, which is why the inside
  of jeans is lighter;
- indigo dye only coats the outside of each thread and leaves a white core ("ring dyeing"), so jeans fade as the
  surface wears away;
- the faded look is often made by stone-washing: tumbling jeans with pumice stones in big washing machines.
Brand names are not drawn; Levi Strauss is mentioned as a historical person.
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

core.MUSICA = "curioso"   # -> lofi
INDIGO = (0.16, 0.25, 0.55)
INDIGO_CL = (0.40, 0.55, 0.82)
COBRE = (0.85, 0.52, 0.25)
ALGODAO = (0.97, 0.97, 0.95)
AMAR = (1.0, 0.82, 0.30)
FUNDO = ((0.86, 0.88, 0.92), (0.55, 0.60, 0.70))


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def calca_frente(ctx, x, y, s=1.0, cor=INDIGO, desbotado=0.0):
    """Parte de cima de um jeans (cintura e bolsos), centro (x, y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.new_path()
    ctx.move_to(-300, -200)
    ctx.line_to(300, -200)
    ctx.line_to(330, 300)
    ctx.line_to(-330, 300)
    ctx.close_path()
    ctx.set_source_rgb(*cor)
    ctx.fill()
    if desbotado > 0:   # desbotado no meio
        anim.brilho(ctx, 0, 120, 260, (0.75, 0.82, 0.95), 0.6 * desbotado)
    ctx.set_source_rgb(*[c * 0.8 for c in cor])   # cós
    ctx.rectangle(-300, -200, 600, 60)
    ctx.fill()
    ctx.set_source_rgba(*AMAR, 0.9)   # costuras
    ctx.set_dash([10, 8])
    ctx.set_line_width(3)
    ctx.move_to(-290, -150)
    ctx.line_to(290, -150)
    for lado in (-1, 1):   # bolsos curvos
        ctx.move_to(lado * 300, -130)
        ctx.curve_to(lado * 220, -120, lado * 150, -60, lado * 140, 40)
    ctx.move_to(0, -140)
    ctx.line_to(0, 160)
    ctx.stroke()
    ctx.set_dash([])
    ctx.set_source_rgba(*AMAR, 0.9)   # bolsinho do relógio
    ctx.set_line_width(3)
    ctx.rectangle(150, -120, 90, 80)
    ctx.stroke()
    ctx.restore()


def d_gancho(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    entra = ease(t / 0.6)
    calca_frente(ctx, 540, 870 + 300 * (1 - entra), 1.0)
    anim.anel_destaque(ctx, t - 0.5, 540 + 195, 870 - 80, 90, cor=AMAR)
    anim.seta(ctx, t - 0.7, 540 + 195, 870 - 140, ang=math.pi / 2, cor=AMAR, som=None)
    if len(s.items) > 1:
        m = s.mark(1)
        tc = t - m
        core.evento_som("pop", tc)
        if tc >= 0:   # relógio de bolso
            k = max(core.mola(tc, 0.45), 0.001)
            ctx.save()
            ctx.translate(540, 540)
            ctx.scale(k, k)
            anim.esfera(ctx, 0, 0, 90, (0.85, 0.70, 0.30))
            ctx.new_path()
            ctx.arc(0, 0, 70, 0, 2 * math.pi)
            ctx.set_source_rgb(0.98, 0.97, 0.92)
            ctx.fill()
            ctx.set_source_rgb(0.1, 0.1, 0.1)
            ctx.set_line_width(5)
            a = t * 2
            ctx.move_to(0, 0)
            ctx.line_to(45 * math.sin(a), -45 * math.cos(a))
            ctx.move_to(0, 0)
            ctx.line_to(30 * math.sin(a / 12), -30 * math.cos(a / 12))
            ctx.stroke()
            ctx.restore()


def d_rebite(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    calca_frente(ctx, 540, 870, 1.0)
    for i, (x, y) in enumerate(((540 - 300, 870 - 130), (540 - 140, 870 + 40), (540 + 300, 870 - 130), (540 + 140, 870 + 40))):
        ti = t - 0.8 - i * 0.35
        core.evento_som("thud", ti)
        if ti < 0:
            continue
        k = max(core.mola(ti, 0.35), 0.001)
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(k, k)
        anim.esfera(ctx, 0, 0, 18, COBRE)
        ctx.restore()
        anim.estouro(ctx, ti, x, y, cor=COBRE, r0=24, r1=70, som=None)
    anim.contador(ctx, t - 0.2, 540, 600, 1873, ini=1840, dur=1.0, fmt="{:.0f}", size=110, cor=COBRE, som=None)


def d_trama(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    k = ease(t / 3.0)
    x0, y0, n, passo = 240, 640, 12, 50
    for i in range(n):   # fios azuis no comprimento
        ctx.set_source_rgb(*INDIGO)
        ctx.rectangle(x0 + i * passo, y0, 30, 560)
        ctx.fill()
    for j in range(int(11 * k)):   # fios brancos atravessando (sarja: sobe e desce em diagonal)
        y = y0 + 20 + j * passo
        for i in range(n):
            por_cima = (i + j) % 3 == 0
            if por_cima:
                ctx.set_source_rgb(*ALGODAO)
                ctx.rectangle(x0 + i * passo - 10, y, passo, 26)
                ctx.fill()
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["INSIDE", "=", "LIGHTER"], 540, 560, size=80, cor=INDIGO)


def d_fio(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    k = ease((t - 0.4) / 1.0)
    # corte do fio: anel azul por fora, miolo branco
    anim.sombra_chao(ctx, 540, 1150, 520)
    ctx.new_path()
    ctx.arc(540, 880, 240, 0, 2 * math.pi)
    ctx.set_source_rgb(*INDIGO)
    ctx.fill()
    ctx.arc(540, 880, 240 - 120 * k, 0, 2 * math.pi)
    ctx.set_source_rgb(*ALGODAO)
    ctx.fill()
    anim.anel_destaque(ctx, t - 1.4, 540, 880, 130, cor=AMAR)
    anim.texto_pop(ctx, t - 0.6, ["WHITE", "CORE"], 540, 560, size=96, cor=INDIGO)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["FADES", "AS", "IT", "WEARS"], 540, 1180, size=58, cor=WHITE)


def d_pedras(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.30, 0.38, 0.50), (0.08, 0.10, 0.15), bokeh=(0.8, 0.9, 1))
    anim.tremor(ctx, t - 0.3, forca=6, dur=0.3, som="swish")
    anim.sombra_chao(ctx, 540, 1180, 640)
    anim.cilindro(ctx, 540, 690, 560, 480, (0.78, 0.80, 0.84))
    ctx.save()   # janela da lavadora com jeans e pedras rodando
    ctx.new_path()
    ctx.arc(540, 930, 190, 0, 2 * math.pi)
    ctx.clip()
    ctx.set_source_rgb(0.25, 0.35, 0.55)
    ctx.paint()
    for i in range(14):
        a = t * 2.5 + i * 0.45
        r = 60 + (i * 31 % 120)
        x, y = 540 + r * math.cos(a), 930 + r * math.sin(a)
        if i % 3 == 0:
            anim.esfera(ctx, x, y, 22, (0.70, 0.68, 0.62))   # pedra-pomes
        else:
            ctx.set_source_rgb(*(INDIGO_CL if i % 2 else INDIGO))
            ctx.rectangle(x - 30, y - 12, 60, 24)
            ctx.fill()
    ctx.restore()
    anim.bolhas(ctx, t, 360, 720, 700, 1060, n=20, r=8, alpha=0.6)
    anim.texto_pop(ctx, t - 0.5, ["STONE", "WASHED"], 540, 540, size=96, cor=WHITE)


def d_fim(ctx, t, s):
    anim.fundo_vivo(ctx, t, *FUNDO, bokeh=(1, 1, 1))
    calca_frente(ctx, 540, 870, 1.0, cor=INDIGO, desbotado=ease(t / 1.5))
    anim.anel_destaque(ctx, t - 0.8, 540 + 195, 870 - 80, 90, cor=AMAR)
    anim.texto_pop(ctx, t - 0.3, ["STILL", "THERE"], 540, 600, size=96, cor=INDIGO)


SEGMENTS = [
    Seg(["See this tiny pocket on your jeans?", "It was made for a pocket watch."], d_gancho,
        {"title": "HOW ARE JEANS MADE?"}, tail=0.2),
    Seg(["In eighteen seventy three, a tailor and a fabric seller named Levi Strauss patented copper rivets, so work pants wouldn't rip."],
        d_rebite, {"big": "RIVETS", "color": COBRE}, tail=0.2),
    Seg(["Denim is woven with blue threads one way and white threads the other.", "That's why the inside is lighter."],
        d_trama, {"big": "THE WEAVE", "color": INDIGO}, tail=0.2),
    Seg(["And the blue dye only coats the outside of each thread. The core stays white,", "so jeans fade as they wear."],
        d_fio, {"big": "THE DYE", "color": INDIGO}, tail=0.2),
    Seg(["Want that faded look now? Factories tumble jeans with volcanic stones in giant washers."], d_pedras,
        {"big": "THE FADE", "color": WHITE}, tail=0.2),
    Seg(["And the watch pocket? Almost nobody carries a pocket watch anymore. It's still there."], d_fim,
        {"big": "150 YEARS", "color": INDIGO}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("What do you keep in that tiny pocket?", "WHAT'S IN YOUR TINY POCKET?",
                                fundo=lambda ctx, t, s: anim.fundo_vivo(ctx, t, *FUNDO)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
