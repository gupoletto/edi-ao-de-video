"""What if you rode a marble through a loop? Sat 14/11/2026, topic: satisfying (marble runs + physics), format: what
if with the mascot Quark (conflict arc). Search 14/11: "marble run satisfying", median 658k.

Physics (simulated below, not typed in): a solid ball rolling without slipping keeps 2/7 of its energy as spin, so
v^2 = (10/7) g (h0 - y). To stay on the track at the top of a loop of radius R it needs v^2 >= g R there, which
means starting at least 2.7 R above the bottom of the loop (a sliding block would need 2.5 R). Starting at 2 R,
the ball loses contact before the top and falls off the loop.
Quark rides inside a clear ball (like a hamster ball); he never gets hurt, the fall is a comic tumble.
Arc: hook (top of the ramp) -> rising (first run from the loop's height) -> conflict (falls off) -> proof (the
2.7 rule) -> payoff (second run from higher up, makes it) -> question.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

G = 9.81
R = 1.0                 # raio do caminho do centro da bola no looping (m)
PX = 300.0              # px por metro
RB = 150.0              # raio da bola na tela (px)
LCX = 0.0               # centro do looping (m); o fundo do looping fica em y = 0
RAMPA_ANG = math.radians(55)
X_PE_RAMPA = -2.2       # onde a rampa encontra o chão (m)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def caminho(s, h0):
    """Posição (x, y) no trilho a uma distância s do início da rampa, e o tipo de trecho."""
    L_rampa = h0 / math.sin(RAMPA_ANG)
    x_ini = X_PE_RAMPA - h0 / math.tan(RAMPA_ANG)
    if s < L_rampa:
        return x_ini + s * math.cos(RAMPA_ANG), h0 - s * math.sin(RAMPA_ANG), "rampa"
    s -= L_rampa
    plano = LCX - X_PE_RAMPA
    if s < plano:
        return X_PE_RAMPA + s, 0.0, "plano"
    s -= plano
    if s < 2 * math.pi * R:
        phi = s / R    # 0 no fundo, anti-horário (sobe pelo lado direito)
        return LCX + R * math.sin(phi), R - R * math.cos(phi), "loop"
    s -= 2 * math.pi * R
    return LCX + s, 0.0, "saida"


def simula(h0, dur=6.0, dt=1 / 600):
    """Rola pelo trilho conservando energia (com o 2/7 do giro); no looping, solta se v^2/R < -g cos(phi)."""
    ts, xs, ys, solto = [], [], [], []
    s, v, t = 0.0, 0.0, 0.0
    voo = None
    while t < dur:
        if voo is None:
            x, y, tipo = caminho(s, h0)
            v = math.sqrt(max(0.0, (10 / 7) * G * (h0 - y)))
            if tipo == "loop":
                phi = s_loop = (s - (h0 / math.sin(RAMPA_ANG) + (LCX - X_PE_RAMPA))) / R
                if v * v / R < -G * math.cos(phi) and math.pi * 0.5 < phi < math.pi * 1.5:
                    voo = [x, y, v * math.cos(phi), v * math.sin(phi)]   # tangente no sentido do movimento
            s += max(v, 0.3) * dt if h0 - y > 0.001 or tipo != "loop" else 0
        if voo is not None:
            voo[2] *= 1.0
            voo[3] -= G * dt
            voo[0] += voo[2] * dt
            voo[1] += voo[3] * dt
            if voo[1] < 0:   # quica no chão e rola
                voo[1] = 0.0
                voo[3] = -voo[3] * 0.35
                voo[2] *= 0.7
            x, y = voo[0], voo[1]
        ts.append(t)
        xs.append(x)
        ys.append(y)
        solto.append(voo is not None)
        t += dt
    return np.array(ts), np.array(xs), np.array(ys), np.array(solto)


SIM = {"falha": simula(2.0 * R), "ok": simula(2.75 * R)}


def em(sim, t):
    ts, xs, ys, so = sim
    i = min(len(ts) - 1, max(0, int(t * 600)))
    return xs[i], ys[i], bool(so[i])


def cena_trilho(ctx, h0, cam_x, cam_y, t):
    """Desenha o trilho em coordenadas de tela, com a câmera centrada em (cam_x, cam_y) metros."""
    def tela(x, y):
        return 540 + (x - cam_x) * PX, 900 - (y - cam_y) * PX
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.12, 0.10, 0.22)
    g.add_color_stop_rgb(1, 0.30, 0.18, 0.40)
    ctx.set_source(g)
    ctx.paint()
    ctx.set_source_rgb(0.22, 0.16, 0.28)   # chão (abaixo do trilho: o centro da bola está RB acima)
    _, yc = tela(0, 0)
    ctx.rectangle(0, yc + RB, W, H)
    ctx.fill()
    ctx.set_line_width(30)
    ctx.set_source_rgb(0.95, 0.75, 0.25)
    pts = []
    s = 0.0
    total = h0 / math.sin(RAMPA_ANG) + (LCX - X_PE_RAMPA) + 2 * math.pi * R + 6
    while s < total:
        x, y, tipo = caminho(s, h0)
        if tipo == "loop":
            phi = math.atan2(x - LCX, R - y)
            nx, ny = -math.sin(phi), -math.cos(phi) * -1   # normal para fora do círculo
            ox, oy = (x - LCX) / R, (y - R) / R
            px, py = tela(x + ox * RB / PX, y + oy * RB / PX)
        else:
            nx, ny = (math.sin(RAMPA_ANG), math.cos(RAMPA_ANG)) if tipo == "rampa" else (0.0, 1.0)
            px, py = tela(x - nx * RB / PX * 0, y - RB / PX if tipo != "rampa" else y - ny * RB / PX)
            if tipo == "rampa":
                px, py = tela(x + math.sin(RAMPA_ANG) * RB / PX, y - math.cos(RAMPA_ANG) * RB / PX)
        pts.append((px, py))
        s += 0.02
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke()
    return tela


def bola(ctx, x, y, t, expr, giro=0.0):
    ctx.set_source_rgba(0.75, 0.9, 1.0, 0.25)
    ctx.arc(x, y, RB, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.7)
    ctx.set_line_width(6)
    ctx.arc(x, y, RB, 0, 2 * math.pi)
    ctx.stroke()
    ctx.arc(x - RB * 0.4, y - RB * 0.45, RB * 0.18, 0, 2 * math.pi)
    ctx.set_source_rgba(1, 1, 1, 0.35)
    ctx.fill()
    p = pq.Pose(expr=expr, braco_e=2.4, braco_d=2.4, inclina=0.25 * math.sin(giro))
    pq.quark(ctx, x, y + RB * 0.85, RB * 1.9, p, t)


def corrida(nome, t_ini, expr_bom, expr_ruim):
    sim = SIM[nome]
    h0 = 2.0 * R if nome == "falha" else 2.75 * R

    def draw(ctx, t, s):
        tt = max(0.0, (t - t_ini) * 0.75)    # câmera lenta 0,75x
        x, y, solto = em(sim, tt)
        cx = min(LCX, max(x, X_PE_RAMPA - 1.2)) if x < LCX else LCX
        cy = 1.1
        tela = cena_trilho(ctx, h0, cx, cy, t)
        bx, by = tela(x, y)
        bola(ctx, bx, by, t, expr_ruim if solto else expr_bom, giro=tt * 4)
        round_rect(ctx, 300, 470, 480, 110, 22)
        ctx.set_source_rgba(0.04, 0.03, 0.08, 0.75)
        ctx.fill()
        text_center(ctx, f"START: {h0 / R:.1f} x R", 540, 520, 44, YELLOW if nome == "ok" else PINK, "ExtraBold")
        text_center(ctx, "R = LOOP RADIUS", 540, 560, 24, WHITE, "Bold")
    return draw


def d_gancho(ctx, t, s):
    tela = cena_trilho(ctx, 2.75 * R, X_PE_RAMPA - 0.8, 1.6, t)
    x0 = X_PE_RAMPA - 2.75 * R / math.tan(RAMPA_ANG)
    bx, by = tela(x0, 2.75 * R)
    bola(ctx, bx + 30 * math.sin(t * 3), by, t, "determinado")


def d_regra(ctx, t, s):
    import cairo
    ctx.set_source_rgb(0.10, 0.09, 0.18)
    ctx.paint()
    cx, cy, r = 600, 950, 220
    ctx.set_source_rgb(0.95, 0.75, 0.25)
    ctx.set_line_width(14)
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.stroke()
    base = cy + r
    for k, (h, cor, rot) in enumerate(((2.0, PINK, "2.0 R: FALLS OFF"), (2.7, GREEN, "2.7 R: MAKES IT"))):
        a = ease((t - 0.4 - k * 0.8) / 0.6)
        y = base - h * r * a
        ctx.set_source_rgb(*cor)
        ctx.rectangle(220 + k * 90, y, 50, base - y)
        ctx.fill()
        text_center(ctx, rot, 540, 520 + k * 60, 40, cor, "ExtraBold", alpha=a)
    text_center(ctx, "SPEED + SPIN", 540, 1350 - 120, 34, WHITE, "Bold")


SEGMENTS = [
    Seg(["What if I rode a giant marble through a loop?"], d_gancho, {"title": "CAN I MAKE THE LOOP?"}, tail=0.1),
    Seg(["Okay. I'll start exactly as high as the loop itself. That's enough, right?"], corrida("falha", 0.6, "feliz", "medo"),
        {"big": "TRY #1", "color": YELLOW}, tail=0.2),
    Seg(["Nope! I fall off before the top! Ow, ow, ow."], corrida("falha", -2.9, "feliz", "tonto"),
        {"big": "NOPE", "color": PINK}, tail=0.3),
    Seg(["Some energy goes into spinning. At the top you still need speed, so you start two point seven times higher."],
        d_regra, {"big": "THE 2.7 RULE", "big_size": 92, "color": GREEN}, tail=0.2),
    Seg(["Try number two, from a bit higher up. Here we go... over the top... I made it!"], corrida("ok", 0.4, "rindo", "rindo"),
        {"big": "TRY #2", "color": GREEN}, tail=0.5, sfx=[(0, 0.4, "whoosh")]),
]
SEGMENTS.append(pq.seg_pergunta("Would you ride a loop inside a marble?", "WOULD YOU RIDE IT?",
                                fundo=lambda ctx, t, s: d_gancho(ctx, t, s)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
