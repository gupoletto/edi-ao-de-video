"""What if you ran across a pool of liquid? (oobleck, shear thickening). Sun 08/11/2026, topic: satisfying,
format: what if with the mascot Quark (conflict arc). Search 07/11: "non newtonian fluid", median 534k views
(top: "Can a human run on liquid?", 13.8M).

Facts:
- oobleck is cornstarch mixed with water (roughly 1.5 to 2 parts starch to 1 part water); it is a shear-thickening
  (non-Newtonian) fluid;
- a sudden impact makes the starch grains jam together and the mix briefly behaves like a solid under the foot
  (Waitukaitis & Jaeger, Nature 2012, "impact-activated solidification"); people really do run across pools of it;
- standing still, the grains slide apart again and you sink;
- pulling a stuck leg out fast makes it grip harder; moving slowly lets it flow, so slow is the way out;
- a fast punch on the surface meets a hard, solid-feeling surface.
Arc: hook (Quark runs onto the pool) -> rising (it holds him) -> conflict (he stops and sinks) -> proof (the grains
jam when he yanks) -> twist (slow = liquid) -> payoff (punch, it's a wall) -> question.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, YELLOW, Seg, render  # noqa: E402

SUP = 1150            # superfície da piscina (px)
FUNDO = 1560
X_ESQ, X_DIR = 40, 860
OOB = (0.96, 0.93, 0.84)
OOB_ESC = (0.84, 0.80, 0.70)
QH = 470              # altura do Quark


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ---------------- cenário ----------------

def quintal(ctx):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, SUP)
    g.add_color_stop_rgb(0, 0.30, 0.58, 0.92)
    g.add_color_stop_rgb(1, 0.78, 0.89, 0.98)
    ctx.set_source(g)
    ctx.paint()
    ctx.set_source_rgb(0.80, 0.62, 0.42)  # cerca de madeira
    for x in range(-20, W + 40, 62):
        ctx.move_to(x, SUP - 60)
        ctx.line_to(x, SUP - 330)
        ctx.line_to(x + 26, SUP - 360)
        ctx.line_to(x + 52, SUP - 330)
        ctx.line_to(x + 52, SUP - 60)
        ctx.close_path()
    ctx.fill()
    ctx.set_source_rgb(0.66, 0.48, 0.32)
    for y in (SUP - 290, SUP - 150):
        ctx.rectangle(0, y, W, 18)
    ctx.fill()
    ctx.set_source_rgb(0.40, 0.68, 0.32)  # grama
    ctx.rectangle(0, SUP - 70, W, H - SUP + 70)
    ctx.fill()


def piscina(ctx, t, onda=1.0):
    """Corte da piscina: azulejos e a mistura branca; a superfície ondula de leve (é líquido)."""
    ctx.set_source_rgb(0.25, 0.55, 0.78)
    ctx.rectangle(X_ESQ - 26, SUP - 10, X_DIR - X_ESQ + 52, FUNDO - SUP + 36)
    ctx.fill()
    ctx.set_source_rgb(*OOB)
    ctx.move_to(X_ESQ, FUNDO)
    for x in range(X_ESQ, X_DIR + 1, 20):
        ctx.line_to(x, SUP + onda * 4 * math.sin(x * 0.02 + t * 2.2))
    ctx.line_to(X_DIR, FUNDO)
    ctx.close_path()
    ctx.fill()
    rng = np.random.default_rng(3)  # grãos de amido visíveis no corte
    ctx.set_source_rgba(*OOB_ESC, 0.6)
    for _ in range(170):
        x, y = rng.uniform(X_ESQ + 10, X_DIR - 10), rng.uniform(SUP + 30, FUNDO - 10)
        ctx.arc(x + 3 * math.sin(t * 1.3 + x), y, rng.uniform(3, 6), 0, 2 * math.pi)
        ctx.fill()
    ctx.set_source_rgb(0.85, 0.86, 0.88)  # borda de pedra
    for x0, x1 in ((0, X_ESQ), (X_DIR, W)):
        ctx.rectangle(x0, SUP - 14, x1 - x0, 28)
    ctx.fill()


def placa_solida(ctx, x, idade, forte=1.0):
    """Onde o pé bate, os grãos travam: um cone mais escuro e rachaduras na superfície (some em ~0,5 s)."""
    if idade < 0 or idade > 0.55:
        return
    a = (1 - idade / 0.55) * forte
    ctx.set_source_rgba(0.62, 0.56, 0.42, 0.55 * a)
    ctx.move_to(x - 70, SUP)
    ctx.line_to(x + 70, SUP)
    ctx.line_to(x + 22, SUP + 190)
    ctx.line_to(x - 22, SUP + 190)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.9 * a)
    ctx.set_line_width(4)
    for k in range(6):
        ang = k * math.pi / 5
        ctx.move_to(x, SUP + 2)
        ctx.line_to(x + math.cos(ang) * 85, SUP + 2 + math.sin(ang) * 12)
    ctx.stroke()


def cobre(ctx, x, prof, t):
    """Mistura por cima das pernas afundadas, com a borda subindo em volta do Quark."""
    if prof <= 0:
        return
    ctx.set_source_rgb(*OOB)
    ctx.move_to(x - 170, SUP + 2)
    ctx.curve_to(x - 110, SUP + 2, x - 100, SUP - 14, x - 70, SUP - 16)
    ctx.line_to(x + 70, SUP - 16)
    ctx.curve_to(x + 100, SUP - 14, x + 110, SUP + 2, x + 170, SUP + 2)
    ctx.line_to(x + 170, SUP + prof + 40)
    ctx.line_to(x - 170, SUP + prof + 40)
    ctx.close_path()
    ctx.fill()


def corrida(t0, x0, vel, cad, t):
    """Posição e passos de uma corrida: pisadas a cada meio ciclo."""
    x = x0 + vel * (t - t0)
    pisadas = [x0 + vel * (k / (2 * cad)) for k in range(int(max(0, t - t0) * 2 * cad) + 1)]
    idades = [(t - t0) - k / (2 * cad) for k in range(len(pisadas))]
    return x, list(zip(pisadas, idades))


# ---------------- grãos (o "porquê") ----------------

def graos(ctx, cx, cy, r, trava, t):
    """Zoom nos grãos de amido na água. trava 0 = soltos, deslizando; 1 = travados em blocos, com as linhas de força."""
    ctx.save()
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.clip()
    ctx.set_source_rgb(0.55, 0.78, 0.95)
    ctx.paint()
    rng = np.random.default_rng(11)
    n = 7
    pos = []
    for i in range(n):
        for j in range(n):
            px = cx - r + (i + 0.5) * 2 * r / n + (j % 2) * r / n
            py = cy - r + (j + 0.5) * 2 * r / n
            dx = rng.uniform(-1, 1) * 22 * math.sin(t * 1.5 + i + j * 1.7)
            dy = rng.uniform(-1, 1) * 22 * math.cos(t * 1.2 + i * 1.3 + j)
            px += dx * (1 - trava) + (cx - px) * 0.12 * trava
            py += dy * (1 - trava) + (cy - py) * 0.12 * trava
            pos.append((px, py))
    if trava > 0.05:
        ctx.set_source_rgba(1.0, 0.85, 0.25, trava)
        ctx.set_line_width(6)
        for a in range(len(pos)):
            for b in range(a + 1, len(pos)):
                d = math.dist(pos[a], pos[b])
                if d < 2 * r / n * 1.02:
                    ctx.move_to(*pos[a])
                    ctx.line_to(*pos[b])
        ctx.stroke()
    for px, py in pos:
        ctx.set_source_rgb(*OOB)
        ctx.arc(px, py, r / n * 0.62, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgb(*OOB_ESC)
        ctx.set_line_width(3)
        ctx.arc(px, py, r / n * 0.62, 0, 2 * math.pi)
        ctx.stroke()
    ctx.restore()
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(8)
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.stroke()
    from core import text_center
    text_center(ctx, "STARCH GRAINS" if trava < 0.5 else "JAMMED!", cx, cy + r + 44, 30, (1, 1, 1), "ExtraBold")


# ---------------- cenas ----------------

def d_gancho(ctx, t, s):
    """Na borda, o Quark toma distância e entra correndo na piscina."""
    quintal(ctx)
    piscina(ctx, t)
    x, pis = corrida(0.6, -60, 300, 2.4, t) if t > 0.6 else (-60 + 30 * t, [])
    for px, idade in pis:
        if px > X_ESQ + 20:
            placa_solida(ctx, px, idade)
    p = pq.Pose(expr="determinado", boca=pq.boca_da_voz(s, t), andar=t * 2.4, corrida=True,
                braco_e=0.9 + 0.6 * math.sin(t * 15), braco_d=0.9 - 0.6 * math.sin(t * 15))
    pq.quark(ctx, max(x, 150), SUP, QH, p, t)


def d_corre(ctx, t, s):
    """Correndo por cima: a cada pisada a mistura vira chão por um instante."""
    quintal(ctx)
    piscina(ctx, t, onda=0.4)
    t0 = -1.6
    x, pis = corrida(t0, 150 - 300 * 0.6, 300, 2.4, t)
    xq = 240 + ((x - 240) % 460)  # volta e meia: dá a volta na piscina (fica no quadro)
    for px, idade in pis[-3:]:
        placa_solida(ctx, 240 + ((px - 240) % 460), idade)
    p = pq.Pose(expr="rindo", boca=pq.boca_da_voz(s, t), andar=t * 2.4, corrida=True,
                braco_e=2.2, braco_d=2.2)
    pq.quark(ctx, xq, SUP, QH, p, t)


X_PARA = 560


def prof_afunda(t):
    return 230 * ease((t - 0.6) / 2.0)


def d_afunda(ctx, t, s):
    quintal(ctx)
    piscina(ctx, t)
    if t < 0.5:
        x = X_PARA - 120 + 240 * t
        p = pq.Pose(expr="feliz", boca=pq.boca_da_voz(s, t), andar=t * 2.4, corrida=True)
        pq.quark(ctx, x, SUP, QH, p, t)
        return
    prof = prof_afunda(t)
    medo = t > 1.0
    p = pq.Pose(expr="medo" if medo else "feliz", boca=pq.boca_da_voz(s, t), suor=medo,
                braco_e=2.6 if medo else 1.2, braco_d=2.6 if medo else 1.2, olhar=(0, 0.8) if medo else (0, 0))
    pq.quark(ctx, X_PARA, SUP + prof, QH, p, t)
    cobre(ctx, X_PARA, prof, t)


def d_prova(ctx, t, s):
    """Ele puxa a perna com força: os grãos travam (linhas de força) e a mistura segura mais."""
    quintal(ctx)
    piscina(ctx, t, onda=0.3)
    prof = 230
    puxa = max(0.0, math.sin(t * 6.5))
    p = pq.Pose(expr="bravo", boca=pq.boca_da_voz(s, t), braco_e=0.2 + 2.2 * puxa, braco_d=0.2 + 2.2 * puxa,
                squash=1 + 0.08 * puxa, suor=True)
    pq.quark(ctx, X_PARA, SUP + prof - 12 * puxa, QH, p, t)
    cobre(ctx, X_PARA, prof, t)
    placa_solida(ctx, X_PARA, 0.15 * (1 - puxa), forte=puxa)
    graos(ctx, 830, 700, 160, 0.35 + 0.65 * puxa, t)


def d_devagar(ctx, t, s):
    """Devagar: os grãos deslizam e ele sai, como quem sai de areia movediça."""
    quintal(ctx)
    piscina(ctx, t)
    k = ease((t - 0.4) / 3.0)
    x = X_PARA + (900 - X_PARA) * ease((t - 2.2) / 1.6)
    prof = 230 * (1 - k)
    y = SUP + prof if x < X_DIR else SUP - 14
    p = pq.Pose(expr="pensando" if t < 2.2 else "feliz", boca=pq.boca_da_voz(s, t),
                andar=t * 0.5 if t > 2.2 else None, braco_e=0.6, braco_d=0.6)
    pq.quark(ctx, x, y, QH, p, t)
    cobre(ctx, X_PARA if prof > 0 else x, prof, t)
    graos(ctx, 250, 700, 150, 0.0, t)


def d_soco(ctx, t, s):
    """Da borda, ele soca a superfície: bate como numa parede."""
    quintal(ctx)
    piscina(ctx, t, onda=0.4)
    soco = 0.6
    a = ease((t - (soco - 0.25)) / 0.25)
    p = pq.Pose(expr="rindo" if t > soco + 0.3 else "determinado", boca=pq.boca_da_voz(s, t),
                inclina=0.35 * a, braco_d=1.2 + 1.6 * a, braco_e=0.4)
    pq.quark(ctx, 860, SUP - 14, QH, p, t)
    placa_solida(ctx, 660, t - soco, forte=1.2)
    if t > soco:
        ctx.set_source_rgba(1, 1, 1, max(0.0, 1 - (t - soco) / 0.4))
        for k in range(10):
            ang = math.pi + k * math.pi / 9
            ctx.move_to(660 + math.cos(ang) * 40, SUP + math.sin(ang) * 40)
            ctx.line_to(660 + math.cos(ang) * 110, SUP + math.sin(ang) * 110)
        ctx.set_line_width(7)
        ctx.stroke()


SEGMENTS = [
    Seg(["What if I tried to run across a pool of liquid?"], d_gancho,
        {"title": "CAN YOU RUN ON LIQUID?"}, tail=0.1),
    Seg(["It's cornstarch and water. When I run, every step hits it so fast it turns solid!"], d_corre,
        {"big": "OOBLECK", "sub": "CORNSTARCH + WATER", "color": YELLOW}, tail=0.1, sfx=[(0, 0, "whoosh")]),
    Seg(["But the moment I stop, I start sinking!"], d_afunda,
        {"big": "STOP = SINK", "color": PINK}, tail=0.4),
    Seg(["If I yank my leg out, it grips even harder. The grains jam together like a solid."], d_prova,
        {"big": "IT GRIPS HARDER", "big_size": 88, "sub": "FAST = SOLID", "color": YELLOW}, tail=0.2),
    Seg(["The trick is to go slow. Slow, it flows like a liquid, and I'm out."], d_devagar,
        {"big": "GO SLOW", "sub": "SLOW = LIQUID", "color": GREEN}, tail=0.2, sfx=[(0, 0.5, "ding")]),
    Seg(["And if I punch it? Ow! It's like hitting a wall."], d_soco,
        {"title": "PUNCH IT = WALL"}, tail=0.4),
]
SEGMENTS.append(pq.seg_pergunta("Would you try running across it?", "WOULD YOU RUN ON IT?",
                                fundo=lambda ctx, t, s: (quintal(ctx), piscina(ctx, t))))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
