"""What if you dropped a penny from the Empire State Building? Wed 04/11/2026, topic: physics simulations,
format: what if with the mascot Quark (conflict arc).

Facts / physics (numbers computed below, not typed in):
- the 86th-floor observation deck is about 320 m (1,050 ft) above the street;
- without air: v = sqrt(2 g h) = 79 m/s = 177 mph, fall time sqrt(2h/g) = 8.1 s;
- a US penny: 2.5 g, 19.05 mm across. Tumbling flat it has a drag coefficient around 1.1-1.2, so its terminal
  velocity is v = sqrt(2 m g / (rho Cd A)) = ~11 m/s = ~25 mph (University of Virginia physicist Louis Bloomfield
  measured pennies tumbling at roughly 25 mph in a wind tunnel and concluded a falling penny would sting, not kill);
- with air the fall takes about half a minute instead of 8 seconds.
The air penny is integrated numerically: dv/dt = g (1 - v^2 / vt^2).
Arc: hook (Quark flicks the penny) -> rising (the legend) -> conflict (177 mph) -> proof (race with and without
air) -> twist (terminal velocity, 25 mph) -> payoff (bonk, Quark laughs) -> question.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import AREA, BLUE, GREEN, H, PINK, W, WHITE, YELLOW, Seg, pill, ramp, render, text_center  # noqa: E402

G, ALTURA = 9.81, 320.0
M, D, RHO, CD = 0.0025, 0.01905, 1.225, 1.15
VT = math.sqrt(2 * M * G / (RHO * CD * math.pi * (D / 2) ** 2))
V_VACUO = math.sqrt(2 * G * ALTURA)
T_VACUO = math.sqrt(2 * ALTURA / G)
MPH = 2.23694

# moeda com ar: integração numérica
_dt = 1 / 600
_ts, _hs, _vs = [0.0], [0.0], [0.0]
while _hs[-1] < ALTURA:
    v = _vs[-1] + G * (1 - (_vs[-1] / VT) ** 2) * _dt
    _vs.append(v)
    _hs.append(_hs[-1] + v * _dt)
    _ts.append(_ts[-1] + _dt)
T_AR = _ts[-1]
TS, HS, VS = np.array(_ts), np.array(_hs), np.array(_vs)


def com_ar(tp):
    tp = min(max(tp, 0.0), T_AR)
    return float(np.interp(tp, TS, HS)), float(np.interp(tp, TS, VS))


def sem_ar(tp):
    tp = min(max(tp, 0.0), T_VACUO)
    return G * tp * tp / 2, G * tp


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


# ---------------- cenário ----------------

def ceu(ctx, claro=1.0):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.22 * claro, 0.48 * claro, 0.86 * claro)
    g.add_color_stop_rgb(1, 0.72, 0.85, 0.97)
    ctx.set_source(g)
    ctx.paint()


def predio(ctx, x, base, w, h, cor=(0.55, 0.58, 0.64), janelas=True):
    ctx.set_source_rgb(*cor)
    ctx.rectangle(x, base - h, w, h)
    ctx.fill()
    if janelas:
        ctx.set_source_rgba(1, 0.95, 0.75, 0.35)
        for yy in np.arange(base - h + 14, base - 10, 26):
            for xx in np.arange(x + 8, x + w - 12, 18):
                ctx.rectangle(xx, yy, 9, 13)
        ctx.fill()


def skyline(ctx, base, t=0.0, escala=1.0):
    rng = np.random.default_rng(4)
    x = -40
    while x < W + 40:
        w = rng.uniform(60, 130) * escala
        h = rng.uniform(120, 420) * escala
        predio(ctx, x, base, w, h, cor=(0.42 + rng.uniform(0, 0.1), 0.46, 0.55))
        x += w + rng.uniform(4, 20)


def empire(ctx, cx, base, s=1.0):
    """Silhueta em degraus do Empire State com a antena."""
    cor = (0.78, 0.76, 0.70)
    blocos = [(260, 520), (210, 640), (150, 700), (110, 760), (70, 800)]
    for w, h in blocos:
        ctx.set_source_rgb(*cor)
        ctx.rectangle(cx - w * s / 2, base - h * s, w * s, h * s)
        ctx.fill()
    ctx.set_source_rgba(0.35, 0.37, 0.42, 0.55)
    for yy in np.arange(base - 690 * s, base, 14 * s):
        ctx.rectangle(cx - 100 * s, yy, 200 * s, 4 * s)
    ctx.fill()
    ctx.set_source_rgb(*cor)
    ctx.move_to(cx - 14 * s, base - 800 * s)
    ctx.line_to(cx, base - 960 * s)
    ctx.line_to(cx + 14 * s, base - 800 * s)
    ctx.fill()


def fachada(ctx, x0, x1, rolar, y0=0, y1=H):
    """Parede do prédio com janelas, rolando para cima (a câmera desce junto com a moeda)."""
    ctx.save()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.clip()
    ctx.set_source_rgb(0.74, 0.72, 0.66)
    ctx.paint()
    passo = 120
    off = rolar % passo
    for yy in np.arange(y0 - passo, y1 + passo, passo):
        y = yy - off
        for xx in np.arange(x0 + 30, x1 - 60, 110):
            ctx.set_source_rgb(0.30, 0.40, 0.52)
            ctx.rectangle(xx, y + 20, 60, 80)
            ctx.fill()
            ctx.set_source_rgba(1, 1, 1, 0.25)
            ctx.rectangle(xx + 6, y + 26, 14, 68)
            ctx.fill()
        ctx.set_source_rgb(0.62, 0.60, 0.55)
        ctx.rectangle(x0, y + 108, x1 - x0, 10)
        ctx.fill()
    ctx.restore()


def moeda(ctx, x, y, r, giro):
    """Moeda de cobre vista girando: a elipse achata com cos(giro)."""
    import cairo
    k = math.cos(giro)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, max(0.08, abs(k)))
    g = cairo.RadialGradient(-r * 0.3, -r * 0.3, r * 0.1, 0, 0, r)
    claro = 0.15 if k > 0 else 0.0
    g.add_color_stop_rgb(0, 0.98, 0.70 + claro, 0.45)
    g.add_color_stop_rgb(1, 0.66, 0.36, 0.18)
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgb(0.45, 0.24, 0.12)
    ctx.set_line_width(max(2.0, r * 0.08))
    ctx.stroke()
    ctx.restore()
    ctx.save()  # borda quando está de lado
    if abs(k) < 0.35:
        ctx.set_source_rgb(0.55, 0.30, 0.15)
        ctx.rectangle(x - r, y - r * 0.09, 2 * r, r * 0.18)
        ctx.fill()
    ctx.restore()


def calcada(ctx, y):
    ctx.set_source_rgb(0.55, 0.56, 0.58)
    ctx.rectangle(0, y, W, H - y)
    ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.18)
    for x in range(0, W, 140):
        ctx.rectangle(x, y, 4, H - y)
    ctx.fill()
    ctx.set_source_rgb(0.40, 0.41, 0.44)
    ctx.rectangle(0, y, W, 14)
    ctx.fill()


def velocimetro(ctx, x, y, mph, cor, rot):
    text_center(ctx, f"{mph:.0f} mph", x, y, 74, cor, "ExtraBold")
    text_center(ctx, rot, x, y + 46, 30, WHITE, "Bold")


# ---------------- cenas ----------------

def d_gancho(ctx, t, s):
    """Do mirante: a cidade lá embaixo; o Quark joga a moeda por cima da grade."""
    ceu(ctx)
    skyline(ctx, 1500, escala=0.9)
    ctx.set_source_rgb(0.68, 0.66, 0.6)  # parapeito do mirante
    ctx.rectangle(0, 1180, W, 120)
    ctx.fill()
    ctx.set_source_rgb(0.25, 0.27, 0.3)  # grade
    ctx.set_line_width(6)
    for x in range(20, W, 70):
        ctx.move_to(x, 1180)
        ctx.line_to(x, 900)
    ctx.move_to(0, 905)
    ctx.line_to(W, 905)
    ctx.stroke()
    joga = 0.9
    lt = t - joga
    if lt < 0:
        mx, my = 700, 990 - 10 * math.sin(t * 6)
    else:  # lançada: sobe um pouco por cima da grade e cai para fora do quadro
        mx = 700 + 140 * lt
        my = 990 - 520 * lt + 0.5 * 1500 * lt * lt
    moeda(ctx, mx, my, 26, t * 14)
    p = pq.Pose(expr="determinado" if t < joga else "feliz", boca=pq.boca_da_voz(s, t),
                braco_d=1.4 + (1.2 * ease((t - 0.6) / 0.3)), braco_e=0.3, olhar=(0.6, -0.2 if t < joga else 0.6))
    pq.quark(ctx, 430, 1180, 520, p, t)


def d_lenda(ctx, t, s):
    """A câmera desce junto com a moeda (sem ar): as janelas passam cada vez mais rápido."""
    tp = 0.6 + t * 0.9
    h, v = sem_ar(tp)
    ceu(ctx)
    ctx.save()
    ctx.rectangle(0, 0, W * 0.62, H)
    ctx.clip()
    fachada(ctx, 0, W * 0.62, h * 38)
    ctx.restore()
    ctx.set_source_rgba(1, 1, 1, 0.5)  # traços de velocidade
    ctx.set_line_width(4)
    for i in range(14):
        x = 640 + (i * 53) % 360
        y = (i * 191 + h * 60) % H
        ctx.move_to(x, y)
        ctx.line_to(x, y - 30 - v * 3)
    ctx.stroke()
    moeda(ctx, 810, 860, 60, t * 18)
    velocimetro(ctx, 810, 1080, v * MPH, YELLOW, f"FALLEN {h * 3.281:.0f} FT")


def d_conflito(ctx, t, s):
    """177 mph: velocímetro de agulha; o Quark lá embaixo, olhando para cima com medo."""
    ceu(ctx)
    empire(ctx, 300, 1300, 1.05)
    skyline(ctx, 1300, escala=0.6)
    calcada(ctx, 1300)
    cx, cy, r = 700, 760, 230
    ctx.set_source_rgba(0.05, 0.06, 0.1, 0.85)
    ctx.arc(cx, cy, r + 20, 0, 2 * math.pi)
    ctx.fill()
    a0, a1 = math.radians(150), math.radians(390)
    ctx.set_line_width(26)
    ctx.set_source_rgba(1, 1, 1, 0.15)
    ctx.arc(cx, cy, r - 30, a0, a1)
    ctx.stroke()
    alvo = V_VACUO * MPH
    mph = alvo * ease(t / 1.6)
    frac = mph / 200
    ctx.set_source_rgb(*PINK)
    ctx.arc(cx, cy, r - 30, a0, a0 + (a1 - a0) * frac)
    ctx.stroke()
    ang = a0 + (a1 - a0) * frac
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(10)
    ctx.move_to(cx, cy)
    ctx.line_to(cx + (r - 60) * math.cos(ang), cy + (r - 60) * math.sin(ang))
    ctx.stroke()
    text_center(ctx, f"{mph:.0f}", cx, cy + 110, 96, WHITE, "ExtraBold")
    text_center(ctx, "MPH, NO AIR", cx, cy + 160, 32, WHITE, "Bold")
    p = pq.Pose(expr="medo", boca=pq.boca_da_voz(s, t), olhar=(-0.3, -0.9), braco_e=2.4, braco_d=2.4,
                suor=True, squash=1 + 0.04 * math.sin(t * 20))
    pq.quark(ctx, 780, 1262, 300, p, t)


RACE_Y0, RACE_Y1 = 670, 1160
PHYS_RATE = (3.6, 3.2)  # segundos físicos por segundo de vídeo, nas cenas 3 e 4


def raia(ctx, x, h, v, giro, rot, cor, chegou):
    ctx.set_source_rgba(1, 1, 1, 0.12)
    ctx.rectangle(x - 120, RACE_Y0 - 40, 240, RACE_Y1 - RACE_Y0 + 80)
    ctx.fill()
    y = RACE_Y0 + (RACE_Y1 - RACE_Y0) * (h / ALTURA)
    moeda(ctx, x, y, 34, giro)
    text_center(ctx, rot, x, 545, 36, cor, "ExtraBold")
    text_center(ctx, f"{v * MPH:.0f} mph", x, 615, 60, cor, "ExtraBold")
    if chegou:
        pill(ctx, "LANDED", x, RACE_Y1 + 70, cor, 1.0, size=28)


def corrida(ctx, tp, extra=None):
    ceu(ctx, 0.8)
    ctx.set_source_rgba(0.05, 0.06, 0.1, 0.55)
    ctx.paint()
    calcada(ctx, RACE_Y1 + 35)
    h1, v1 = sem_ar(tp)
    h2, v2 = com_ar(tp)
    raia(ctx, 330, h1, v1 if tp < T_VACUO else 0.0, 0.0 if tp < T_VACUO else 1.4, "NO AIR", PINK, tp >= T_VACUO)
    if tp >= T_VACUO:
        text_center(ctx, f"HIT AT {V_VACUO * MPH:.0f} MPH", 330, 660, 28, WHITE, "Bold")
    raia(ctx, 750, h2, v2 if tp < T_AR else 0.0, tp * 11, "REAL AIR", GREEN, tp >= T_AR)
    text_center(ctx, f"{tp:.1f} s", 540, 900, 44, YELLOW, "ExtraBold")
    if extra:
        extra(ctx)


def d_prova(ctx, t, s):
    corrida(ctx, t * PHYS_RATE[0])


def d_virada(ctx, t, s):
    t0 = SEGS[3].dur * PHYS_RATE[0] if SEGS else 0.0
    rate = max(1.0, (T_AR + 0.3 - t0) / max(0.5, (SEGS[4].dur if SEGS else 4.0) - 1.0))  # o pouso com ar fecha a cena
    tp = t0 + t * rate

    def selo(c):
        a = ramp(t, 0.6, 0.4)
        pill(c, f"TERMINAL VELOCITY ≈ {VT * MPH:.0f} MPH", 540, 472, GREEN, a, size=36)
    corrida(ctx, tp, selo)


def d_bonk(ctx, t, s):
    """A moeda bate na cabeça do Quark: dói um pouco, e ele ri."""
    ceu(ctx)
    skyline(ctx, 1260, escala=0.7)
    calcada(ctx, 1260)
    bate = 0.45
    if t < bate:
        moeda(ctx, 540, 500 + (900 - 500) * (t / bate), 28, t * 30)
    else:
        lt = t - bate
        moeda(ctx, 540 + 160 * lt, 900 - 300 * lt + 0.5 * 2200 * lt * lt, 28, lt * 20)
        if lt < 0.5:
            text_center(ctx, "BONK!", 760, 760, 90, YELLOW, "ExtraBold", alpha=1 - lt * 2)
    expr = "neutro" if t < bate else ("tonto" if t < bate + 0.9 else "rindo")
    sq = 1.0 - 0.12 * math.exp(-max(0, t - bate) * 6) if t > bate else 1.0
    p = pq.Pose(expr=expr, boca=pq.boca_da_voz(s, t), braco_e=0.4 + 2.0 * (t > bate + 0.9),
                braco_d=0.3 + 1.2 * (bate < t < bate + 0.9), squash=sq, olhar=(0.0, -0.8 if t < bate else 0.0))
    pq.quark(ctx, 540, 1262, 460, p, t)


SEGS = []
SEGMENTS = [
    Seg(["What if I dropped a penny from the Empire State Building?"], d_gancho,
        {"title": "DROP A PENNY FROM THE EMPIRE STATE?"}, tail=0.1),
    Seg(["People say it could fall so fast it would kill someone."], d_lenda,
        {"big": "1,050 FT", "sub": "86TH FLOOR DECK", "color": BLUE}, tail=0.1, sfx=[(0, 0, "whoosh")]),
    Seg([f"With no air, it would hit at {V_VACUO * MPH:.0f} miles per hour."], d_conflito,
        {"big": f"{V_VACUO * MPH:.0f} MPH?", "color": PINK}, tail=0.3),
    Seg(["But a penny is light and flat. It flips, and the air pushes back."], d_prova,
        {"big": "AIR VS NO AIR", "big_size": 92, "sub": "SAME PENNY, SAME DROP", "color": YELLOW}, tail=0.2),
    Seg([f"It never goes faster than about {round(VT * MPH / 5) * 5:.0f} miles per hour.",
         "That's its terminal velocity."], d_virada,
        {"big": f"{round(VT * MPH / 5) * 5:.0f} MPH MAX", "color": GREEN}, tail=0.3, sfx=[(0, 0.5, "ding")]),
    Seg(["Ow! So it stings, but that's it."], d_bonk, {"title": "IT STINGS. THAT'S IT."}, tail=0.5,
        sfx=[(0, 0.45, "tick")]),
]
SEGMENTS.append(pq.seg_pergunta("Would you stand under it? Be honest.", "WOULD YOU STAND UNDER IT?",
                                fundo=lambda ctx, t, s: (ceu(ctx), skyline(ctx, 1260, escala=0.7), calcada(ctx, 1260))))


def preparo(segs, total):
    SEGS[:] = segs


if __name__ == "__main__":
    print(f"vt = {VT:.1f} m/s ({VT * MPH:.0f} mph), vacuum {V_VACUO * MPH:.0f} mph in {T_VACUO:.1f} s, "
          f"with air {T_AR:.1f} s")
    render(SEGMENTS, sys.argv[1], preparo=preparo)
