"""What if you fell into lava? (Quark, padrão caprichado). Tue 24/11/2026. Search 24/11: "what happens if you fall into
lava" median 60k.

Facts:
- lava erupts at roughly 700-1,200 C (basaltic lava in Hawaii ~1,100-1,200 C);
- lava is about 2.6-3.1 g/cm3, roughly three times denser than water; a human body is about 1 g/cm3, so a person
  would not sink in like in the movies: they would stay on the surface;
- lava is very viscous, far thicker than honey;
- the real danger is the heat (radiant heat felt meters away; clothes ignite);
- volcanologists working near lava wear aluminized (silver) suits that reflect most of the radiant heat.
Quark never really gets hurt: he lands on top, sweats, and gets out in a silver suit.
Tone: perigo com humor -> suspense? Use "estranho"? -> misterio would be odd; perigo -> suspense.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import anim  # noqa: E402
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import W, WHITE, Seg, render, text_center  # noqa: E402

core.MUSICA = "perigo"   # -> suspense
LAVA = (1.0, 0.42, 0.08)
QUENTE = (1.0, 0.82, 0.35)
ROCHA = (0.16, 0.12, 0.11)
PRATA = (0.82, 0.84, 0.88)
LAGO_Y = 1060


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def cenario(ctx, t, calor=0.6):
    anim.fundo_vivo(ctx, t, (0.22, 0.07, 0.05), (0.05, 0.02, 0.02), bokeh=LAVA)
    ctx.new_path()   # paredes de rocha da cratera
    ctx.set_source_rgb(*ROCHA)
    ctx.move_to(0, 700)
    ctx.line_to(220, 820)
    ctx.line_to(140, LAGO_Y)
    ctx.line_to(0, LAGO_Y)
    ctx.close_path()
    ctx.fill()
    ctx.move_to(W, 680)
    ctx.line_to(860, 800)
    ctx.line_to(940, LAGO_Y)
    ctx.line_to(W, LAGO_Y)
    ctx.close_path()
    ctx.fill()
    lago(ctx, t, calor)


def lago(ctx, t, calor):
    import cairo
    g = cairo.LinearGradient(0, LAGO_Y - 30, 0, 1300)
    g.add_color_stop_rgb(0, *QUENTE)
    g.add_color_stop_rgb(0.25, *LAVA)
    g.add_color_stop_rgb(1, 0.45, 0.08, 0.02)
    ctx.new_path()
    ctx.move_to(0, 1300)
    for x in range(0, W + 20, 20):
        ctx.line_to(x, LAGO_Y + 10 * math.sin(x * 0.012 + t * 1.2))
    ctx.line_to(W, 1300)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgba(0.12, 0.05, 0.04, 0.8)   # crosta escura rachada boiando
    for i in range(9):
        x = (i * 137 + t * 25) % (W + 200) - 100
        y = LAGO_Y + 40 + (i % 3) * 55
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1, 0.3)
        ctx.arc(0, 0, 50 + (i % 4) * 14, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
    anim.brilho(ctx, 540, LAGO_Y, 520, LAVA, 0.35 * calor + 0.2)
    anim.faiscas(ctx, t, 540, LAGO_Y + 10, n=30, vel=420, cor=QUENTE, vida=1.4)


def d_gancho(ctx, t, s):
    cenario(ctx, t)
    p = pq.Pose(expr="surpreso", boca=pq.boca_da_voz(s, t), braco_e=2.6, braco_d=2.6, suor=True,
                olhar=(0.2, 0.8))
    pq.quark(ctx, 250, 1000 + 6 * math.sin(t * 3), 450, p, t)   # na beira da rocha, cabeça abaixo do título
    anim.contador(ctx, t - 0.1, 700, 620, 1200, dur=1.3, sufixo=" °C", size=100, cor=QUENTE)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["MOVIES", "ARE", "WRONG"], 700, 750, size=72, cor=WHITE,
                       cor_destaque=LAVA, destaque=2, largura=560)


def d_densidade(ctx, t, s):
    anim.fundo_vivo(ctx, t, (0.16, 0.10, 0.10), (0.04, 0.03, 0.03), bokeh=LAVA)
    # balança: um balde de lava pesa como três de água
    inc = 0.22 * ease((t - 0.6) / 0.8)
    ctx.save()
    ctx.translate(540, 760)
    ctx.rotate(-inc)
    ctx.set_source_rgb(0.55, 0.57, 0.62)
    ctx.rectangle(-360, -10, 720, 20)
    ctx.fill()
    ctx.restore()
    anim.bloco_3d(ctx, 520, 760, 40, 420, 20, (0.45, 0.47, 0.52))
    xl, yl = 540 - 330 * math.cos(inc), 760 + 330 * math.sin(inc)
    xr, yr = 540 + 330 * math.cos(inc), 760 - 330 * math.sin(inc)
    anim.cilindro(ctx, xl, yl + 20, 150, 150, LAVA)
    text_center(ctx, "LAVA", xl, yl + 230, 40, LAVA, "ExtraBold")
    for k in range(3):
        core.evento_som("pop", t - 0.6 - k * 0.35)
        if t > 0.6 + k * 0.35:
            anim.cilindro(ctx, xr - 120 + k * 120, yr - 90, 100, 100, (0.35, 0.65, 1.0))
    text_center(ctx, "WATER", xr, yr + 120, 40, (0.45, 0.75, 1.0), "ExtraBold")
    anim.texto_pop(ctx, t - 1.6, ["3×", "HEAVIER"], 540, 560, size=110, cor=QUENTE)


def d_boia(ctx, t, s):
    cenario(ctx, t)
    cai = ease(t / 0.7)
    y = 520 + (LAGO_Y + 20 - 520) * cai
    afunda = 30 * (1 - math.exp(-max(0.0, t - 0.7) * 4)) * (1 + 0.3 * math.sin(t * 8) * math.exp(-max(0.0, t - 0.7) * 2))
    p = pq.Pose(expr="surpreso" if t < 1.2 else "pensando", boca=pq.boca_da_voz(s, t), braco_e=2.9, braco_d=2.9,
                pulo=1.0 - cai, squash=1.0 - 0.15 * max(0.0, 1 - abs(t - 0.75) * 5), suor=True)
    pq.quark(ctx, 540, y + afunda, 440, p, t)
    anim.estouro(ctx, t - 0.7, 540, LAGO_Y + 20, cor=QUENTE, r0=120, r1=300)
    anim.seta(ctx, t - 1.4, 540, LAGO_Y + 40, ang=-math.pi / 2, cor=WHITE, som=None)
    if len(s.items) > 1:
        anim.texto_pop(ctx, t - s.mark(1), ["NO", "SINKING"], 540, 600, size=96, cor=QUENTE)


def d_mel(ctx, t, s):
    cenario(ctx, t)
    # Quark tenta andar e o pé gruda na lava grossa
    puxa = 0.5 + 0.5 * math.sin(t * 3)
    p = pq.Pose(expr="bravo", boca=pq.boca_da_voz(s, t), andar=t * 0.6, braco_e=1.6, braco_d=1.0,
                inclina=0.15 * math.sin(t * 3), suor=True)
    pq.quark(ctx, 520 + 10 * puxa, LAGO_Y + 40, 440, p, t)
    ctx.set_source_rgba(*LAVA, 0.95)   # fios de lava grudando
    ctx.set_line_width(14)
    for dx in (-40, 40):
        ctx.move_to(520 + dx, LAGO_Y + 30)
        ctx.curve_to(520 + dx, LAGO_Y + 10 - 40 * puxa, 520 + dx * 1.2, LAGO_Y - 20 * puxa, 520 + dx, LAGO_Y + 40)
        ctx.stroke()
    anim.texto_pop(ctx, t - 0.4, ["THICKER", "THAN", "HONEY"], 540, 580, size=84, cor=QUENTE)


def d_calor(ctx, t, s):
    ctx.save()
    anim.tremor(ctx, t - 0.3, forca=14, dur=0.5)
    cenario(ctx, t, calor=1.0)
    anim.brilho(ctx, 540, 900, 700, QUENTE, 0.35 + 0.1 * math.sin(t * 6))
    p = pq.Pose(expr="medo", boca=pq.boca_da_voz(s, t), braco_e=2.9, braco_d=2.9, suor=True,
                squash=1 + 0.04 * math.sin(t * 20))
    pq.quark(ctx, 540, LAGO_Y + 30, 440, p, t)
    for k in range(8):   # ondas de calor subindo
        y = LAGO_Y - ((t * 220 + k * 90) % 520)
        ctx.set_source_rgba(1, 0.8, 0.5, 0.35)
        ctx.set_line_width(5)
        ctx.move_to(260 + k * 80, y)
        ctx.curve_to(280 + k * 80, y - 30, 240 + k * 80, y - 60, 260 + k * 80, y - 90)
        ctx.stroke()
    ctx.restore()
    anim.texto_pop(ctx, t - 0.6, ["THE", "REAL", "DANGER:", "HEAT"], 540, 560, size=78, cor=WHITE,
                   cor_destaque=LAVA, destaque=3, intervalo=0.18)


def d_roupa(ctx, t, s):
    cenario(ctx, t, calor=0.7)
    p = pq.Pose(expr="determinado" if t < 2.5 else "feliz", boca=pq.boca_da_voz(s, t), braco_d=2.3, capacete=True)
    k = ease((t - 0.3) / 0.6)
    x = 540 + 200 * ease((t - 2.6) / 1.4)   # anda boiando para o lado, sem sair da tela
    ctx.push_group()
    pq.quark(ctx, x, LAGO_Y + 30, 440, p, t)
    ctx.pop_group_to_source()
    ctx.paint()
    if k > 0:   # traje prateado por cima do corpo (brilho metálico)
        anim.brilho(ctx, x, LAGO_Y - 200, 260, PRATA, 0.55 * k)
        anim.anel_destaque(ctx, t - 0.6, x, LAGO_Y - 190, 240, cor=PRATA)
    for i in range(6):   # raios de calor batendo e voltando
        a = -math.pi / 2 + (i - 2.5) * 0.25
        f = (t * 1.5 + i * 0.2) % 1.0
        r = 420 * (1 - abs(2 * f - 1))
        cx, cy = x, LAGO_Y - 190
        ctx.set_source_rgba(*QUENTE, 0.7)
        ctx.set_line_width(5)
        ctx.move_to(cx + r * math.cos(a) * 0.6, cy - 300 + r * 0.2)
        ctx.line_to(cx + (r - 40) * math.cos(a) * 0.6, cy - 300 + (r - 40) * 0.2)
        ctx.stroke()
    anim.texto_pop(ctx, t - 1.0, ["SILVER", "SUIT"], 540, 560, size=96, cor=PRATA)


SEGMENTS = [
    Seg(["What if I fell into lava? Movies say I'd sink like a stone.", "The movies are wrong."], d_gancho,
        {"title": "WHAT IF YOU FELL INTO LAVA?"}, tail=0.2),
    Seg(["Lava is about three times heavier than water, and I'm mostly water."], d_densidade,
        {"big": "HEAVY STUFF", "color": QUENTE}, tail=0.2),
    Seg(["So I wouldn't sink in.", "I'd land on top, like a waterbed made of fire."], d_boia,
        {"big": "SPLAT", "color": LAVA}, tail=0.2),
    Seg(["And it's so thick, walking would be like wading through hot honey."], d_mel,
        {"big": "STUCK", "color": QUENTE}, tail=0.2),
    Seg(["The real danger is the heat. Over a thousand degrees, glowing at me from every side."], d_calor,
        {"big": "THE HEAT", "color": LAVA}, tail=0.2),
    Seg(["That's why volcano scientists wear shiny silver suits. They bounce most of the heat right back."], d_roupa,
        {"big": "THE FIX", "color": PRATA}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Would you walk near a volcano?", "WOULD YOU GO NEAR ONE?",
                                fundo=lambda ctx, t, s: cenario(ctx, t)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
