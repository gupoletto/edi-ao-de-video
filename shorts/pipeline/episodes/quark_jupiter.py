"""What if you jumped into Jupiter? Mon 02/11/2026, topic: space, format: what if with the mascot Quark (conflict arc).

Facts: falling from far away you reach Jupiter at about its escape velocity, 59.5 km/s (~60 km/s); Earth-Moon
384,400 km / 60 km/s = 6,400 s, under two hours. Jupiter has no solid surface. NASA's Galileo probe entered on
7 Dec 1995 and transmitted for 58 minutes, reaching ~150 km below the 1-bar level at ~23 bar and ~153 °C (top of
the clouds ~ -110 °C). Deeper, hydrogen is squeezed into liquid metallic hydrogen.
Arc: hook (falling) -> rising (speed) -> conflict (no ground) -> proof (Galileo) -> twist (liquid metal) -> payoff (the
rope pulls Quark out) -> loop question.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import space  # noqa: E402
from core import BLUE, H, PINK, W, WHITE, YELLOW, Seg, pill, ramp, render, text_center  # noqa: E402

RNG = np.random.default_rng(7)
ESTRELAS = [(RNG.uniform(0, W), RNG.uniform(0, H), RNG.uniform(1, 3)) for _ in range(160)]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def espaco(ctx, t, rastro=0.0):
    ctx.set_source_rgb(0.02, 0.025, 0.06)
    ctx.paint()
    for x, y, r in ESTRELAS:
        yy = (y - t * rastro * 900) % H  # estrelas sobem quando o Quark cai
        ctx.set_source_rgba(1, 1, 1, 0.75)
        if rastro > 0.05:
            ctx.set_line_width(r)
            ctx.move_to(x, yy)
            ctx.line_to(x, yy + rastro * 60)
            ctx.stroke()
        else:
            ctx.arc(x, yy, r, 0, 2 * math.pi)
            ctx.fill()


def caindo(t, s, expr="medo", **kw):
    fala = pq.boca_da_voz(s, t)
    return pq.Pose(expr=expr, boca=fala, braco_e=2.7 + 0.3 * math.sin(t * 9), braco_d=2.6 + 0.3 * math.sin(t * 9 + 1),
                   andar=t * 2.2, capacete=True, inclina=0.25 * math.sin(t * 1.6), **kw)


def d_gancho(ctx, t, s):
    """Quark despenca na direção de Júpiter, que cresce lá embaixo."""
    espaco(ctx, t, rastro=0.6)
    r = 380 + 120 * ease(t / 4)
    space.planet(ctx, "jupiter", W / 2, H - 120 + r * 0.25, r * 1.6, spin=t * 0.05)
    y = 820 + 40 * math.sin(t * 2)
    ctx.save()
    ctx.translate(W / 2, y)
    ctx.rotate(math.pi + 0.3 * math.sin(t * 1.3))  # de cabeça para baixo
    pq.quark(ctx, 0, 260, 520, caindo(t, s), t)
    ctx.restore()


def d_velocidade(ctx, t, s):
    espaco(ctx, t, rastro=1.4)
    space.planet(ctx, "jupiter", W / 2, H + 500, 1100, spin=t * 0.05)
    k = ease(t / 3.5)
    calor = ease((t - 1.5) / 2)
    x, y = W / 2, 900
    if calor > 0:  # plasma da entrada: aura laranja à frente
        g_r = 260 + 30 * math.sin(t * 20)
        for i in range(6):
            ctx.arc(x, y + 140 + i * 18, g_r - i * 30, 0, math.pi)
            ctx.set_source_rgba(1.0, 0.45 + i * 0.06, 0.1, 0.12 * calor)
            ctx.fill()
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.pi)
    pq.quark(ctx, 0, 240, 480, caindo(t, s, expr="surpreso", suor=calor > 0.5), t)
    ctx.restore()
    text_center(ctx, f"{60 * k:.0f} km/s", W / 2, 300, 130, YELLOW, "ExtraBold")
    text_center(ctx, "ENTRY SPEED", W / 2, 370, 44, WHITE, "Bold")
    pill(ctx, "EARTH → MOON IN < 2 HOURS", W / 2, 1340, BLUE, ramp(t, 2.6, 0.4), size=40)


CAMADAS = [(0.93, 0.85, 0.72), (0.80, 0.62, 0.42), (0.88, 0.74, 0.56), (0.70, 0.48, 0.30), (0.62, 0.36, 0.22)]


def nuvens(ctx, t, prof):
    """Camadas de nuvem subindo; ficam mais escuras e avermelhadas com a profundidade (0..1)."""
    for i in range(12):
        y = (i * 190 - t * 420) % (H + 380) - 190
        c = CAMADAS[i % len(CAMADAS)]
        f = 1 - 0.55 * prof
        cor = (min(1, c[0] * f + 0.35 * prof), c[1] * f, c[2] * f * (1 - 0.4 * prof))
        ctx.move_to(0, y)
        for k in range(13):
            ctx.line_to(k * W / 12, y + 26 * math.sin(k * 1.3 + i + t * 0.8))
        ctx.line_to(W, y + 230)
        ctx.line_to(0, y + 230)
        ctx.close_path()
        ctx.set_source_rgba(*cor, 0.92)
        ctx.fill()


def medidores(ctx, t, prof, alpha=1.0):
    km = 150 * prof
    bar = 1 + 22 * prof ** 1.6
    temp = -110 + 263 * prof
    for i, (rot, val, cor) in enumerate((("DEPTH", f"{km:.0f} km", WHITE), ("PRESSURE", f"{bar:.0f} bar", BLUE),
                                         ("TEMP", f"{temp:+.0f} °C", PINK))):
        x = 200 + i * 340
        text_center(ctx, rot, x, 1300, 30, WHITE, "Bold", alpha=alpha * 0.8)
        text_center(ctx, val, x, 1370, 58, cor, "ExtraBold", alpha=alpha)


def d_sem_chao(ctx, t, s):
    prof = ease(t / 6.5) * 0.55
    nuvens(ctx, t, prof)
    x, y = W / 2 + 40 * math.sin(t * 1.4), 780
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.pi * (1 - ease(t / 1.5)))  # endireita e olha para baixo, assustado
    p = caindo(t, s, expr="medo", suor=True)
    p.olhar = (0.0, 0.9)
    pq.quark(ctx, 0, 260, 480, p, t)
    ctx.restore()
    medidores(ctx, t, prof, ramp(t, 0.5, 0.4))


def sonda(ctx, x, y, s, ang=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.move_to(-s, 0)
    ctx.curve_to(-s * 0.9, -s * 0.9, s * 0.9, -s * 0.9, s, 0)
    ctx.close_path()
    ctx.set_source_rgb(0.75, 0.75, 0.8)
    ctx.fill()
    ctx.rectangle(-s, 0, 2 * s, s * 0.35)
    ctx.set_source_rgb(0.45, 0.32, 0.22)
    ctx.fill()
    for k in (-0.6, 0.6):  # cordas do paraquedas
        ctx.move_to(k * s, -s * 0.5)
        ctx.line_to(0, -s * 2.6)
    ctx.set_source_rgba(1, 1, 1, 0.7)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.arc(0, -s * 2.6, s * 1.1, math.pi, 2 * math.pi)
    ctx.set_source_rgb(0.95, 0.95, 0.95)
    ctx.fill()
    ctx.restore()


def d_galileo(ctx, t, s):
    prof = 0.55 + ease(t / 5) * 0.45
    nuvens(ctx, t + 6.5, prof)
    perdeu = t > 4.0
    sx = W / 2 + 220
    if not perdeu:
        sonda(ctx, sx, 930 + 50 * math.sin(t), 70, 0.1 * math.sin(t * 2))
    else:  # sinal perdido
        a = ramp(t, 4.0, 0.3)
        ctx.set_source_rgba(1, 0.3, 0.3, a)
        ctx.set_line_width(14)
        for d in (1, -1):
            ctx.move_to(sx - 70, 900 - 70 * d)
            ctx.line_to(sx + 70, 900 + 70 * d)
        ctx.stroke()
        text_center(ctx, "SIGNAL LOST", sx, 1060, 44, PINK, "ExtraBold", alpha=a)
    minutos = 58 * ease(t / 4.0)
    text_center(ctx, f"{int(minutos):02d}:{int((minutos % 1) * 60):02d}", W / 2, 520, 120, YELLOW, "ExtraBold")
    text_center(ctx, "MINUTES OF SIGNAL", W / 2, 590, 38, WHITE, "Bold")
    p = pq.Pose(expr="surpreso" if not perdeu else "medo", boca=pq.boca_da_voz(s, t), olhar=(0.9, -0.1),
                capacete=True, braco_d=1.6, suor=perdeu)
    pq.quark(ctx, W / 2 - 230, 1200, 440, p, t)
    medidores(ctx, t, prof)


def d_metal(ctx, t, s):
    """Júpiter com um quarto recortado mostrando as camadas; o Quark minúsculo desce pelo corte."""
    espaco(ctx, t)
    cx, cy, r = W / 2 - 60, 1000, 440
    space.planet(ctx, "jupiter", cx, cy, r, spin=t * 0.05)
    abre = ease(t / 1.0)
    camadas = [(1.0, (0.86, 0.72, 0.52)), (0.93, (0.50, 0.60, 0.80)), (0.70, (0.70, 0.76, 0.86)),
               (0.22, (0.60, 0.34, 0.22))]
    for f, cor in camadas:  # o recorte abre como um leque (de -90° até 0°)
        ctx.move_to(cx, cy)
        ctx.arc(cx, cy, r * f, -math.pi / 2, -math.pi / 2 + math.pi / 2 * abre)
        ctx.close_path()
        ctx.set_source_rgb(*cor)
        ctx.fill()
    brilho = 0.5 + 0.5 * math.sin(t * 6)  # o metal líquido cintila
    ctx.move_to(cx, cy)
    ctx.arc(cx, cy, r * 0.70, -math.pi / 2, -math.pi / 2 + math.pi / 2 * abre)
    ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.25 * brilho * ramp(t, 1.6, 0.4))
    ctx.fill()
    for k, (nome, raio) in enumerate((("LIQUID HYDROGEN", 0.82), ("METALLIC HYDROGEN", 0.46), ("CORE", 0.0))):
        a = ramp(t, 0.9 + k * 0.6, 0.4)
        ang = -math.pi / 4
        x = cx + raio * r * math.cos(ang) + (30 if raio else 0)
        y = cy + raio * r * math.sin(ang)
        ctx.set_source_rgba(1, 1, 1, a)
        ctx.set_line_width(4)
        ctx.move_to(x, y)
        ctx.line_to(W - 330, 560 + k * 120)
        ctx.stroke()
        pill(ctx, nome, W - 200, 560 + k * 120, WHITE, a, size=28)
    k = ease((t - 0.8) / 3.5)
    pq.quark(ctx, cx + 60, cy - r * 0.97 + k * r * 0.5, 80,
             pq.Pose(expr="tonto" if k > 0.7 else "medo", capacete=True, braco_e=2.8, braco_d=2.8), t)


def d_corda(ctx, t, s):
    """Payoff: a corda puxa o Quark de volta para o espaço."""
    k = ease((t - 0.6) / 1.6)
    espaco(ctx, t, rastro=-0.8 * (1 - ease((t - 2.4) / 1)) if t > 0.6 else 0)
    space.planet(ctx, "jupiter", W / 2, H + 500 + 700 * k, 1100, spin=t * 0.05)
    y = 1300 - 380 * k
    ctx.set_source_rgb(0.95, 0.92, 0.8)
    ctx.set_line_width(8)
    ctx.move_to(W / 2 + 30, 0)
    ctx.line_to(W / 2 + 30, y - 480)
    ctx.stroke()
    expr = "medo" if t < 0.6 else ("surpreso" if k < 1 else "rindo")
    p = pq.Pose(expr=expr, boca=pq.boca_da_voz(s, t), capacete=True, braco_d=3.0, braco_e=0.6 + 1.8 * (k >= 1),
                cotovelo_d=0.3, squash=1.0 + 0.12 * math.sin(min(t, 2.2) * 8) * (1 - k))
    pq.quark(ctx, W / 2, y, 480, p, t)


def d_pergunta(ctx, t, s):
    espaco(ctx, t)
    space.planet(ctx, "jupiter", 280, 700, 190, spin=t * 0.05)
    space.saturn_rings(ctx, 800, 700, 140, False)
    space.planet(ctx, "saturn", 800, 700, 140)
    space.saturn_rings(ctx, 800, 700, 140, True)
    p = pq.Pose(expr="feliz", boca=pq.boca_da_voz(s, t), braco_e=0.3 + 2.2 * ease(t / 0.6), braco_d=0.3,
                olhar=(0.5 * math.sin(t * 2), -0.3))
    pq.quark(ctx, W / 2, 1420, 420, p, t)


SEGMENTS = [
    Seg(["What if I jumped into Jupiter?"], d_gancho, {"title": "WHAT IF YOU JUMPED INTO JUPITER?"}, tail=0.3),
    Seg(["I'd hit the clouds at sixty kilometers per second.", "That's Earth to the Moon in under two hours."],
        d_velocidade, None, tail=0.2, sfx=[(0, 0, "whoosh")]),
    Seg(["Problem. Jupiter has no ground.", "Just clouds, getting hotter and heavier the deeper you fall."],
        d_sem_chao, {"big": "NO GROUND", "color": PINK}, tail=0.2),
    Seg(["NASA's Galileo probe tried this in nineteen ninety five.", "It lasted fifty eight minutes."],
        d_galileo, {"big": "GALILEO", "sub": "NASA PROBE, 1995", "color": YELLOW}, tail=0.5,
        sfx=[(1, 1.3, "tick")]),
    Seg(["And deeper down, the pressure squeezes hydrogen into a liquid metal."],
        d_metal, {"big": "LIQUID METAL", "sub": "THE HYDROGEN OCEAN", "color": BLUE}, tail=0.6),
    Seg(["Good thing I brought a rope."], d_corda, {"title": "GOOD THING I BROUGHT A ROPE"}, tail=1.2,
        sfx=[(0, 0.6, "whoosh")]),
    Seg(["Jupiter or Saturn, which one would you jump into?"], d_pergunta, {"title": "JUPITER OR SATURN?"}, tail=0.8),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
