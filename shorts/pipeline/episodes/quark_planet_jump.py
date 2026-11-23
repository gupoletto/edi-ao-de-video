"""What if you jumped on every planet? Mon 09/11/2026, topic: space (paired with the illusions ranking), format:
what if with the mascot Quark (conflict arc). Search 08/11: "space facts", median 968k.

Physics (computed below): the same take-off speed everywhere, set by a 0.5 m jump on Earth: v0 = sqrt(2 g h) =
3.13 m/s. Height h = v0^2 / (2 g), time in the air t = 2 v0 / g. Surface gravities (m/s^2): Earth 9.81,
Moon 1.62, Mars 3.71, Jupiter 24.79 (at the cloud tops: Jupiter has no solid surface), Pluto 0.62.
-> Moon 3.0 m and 3.9 s; Mars 1.3 m; Jupiter 0.20 m and 0.25 s; Pluto 7.9 m and 10 s.
Arc: hook (Quark jumps on Earth) -> rising (Moon, huge jump) -> Mars -> conflict (Jupiter: crushed, and no ground)
-> payoff (Pluto: 8 m, 10 s) -> question.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, text_center  # noqa: E402

G_TERRA = 9.81
V0 = math.sqrt(2 * G_TERRA * 0.5)
CHAO = 1240
PX_M = 42          # px por metro (Plutão: 7,9 m = 332 px)
QH = 450

PLANETAS = {  # g, céu (topo, baixo), chão, nome
    "earth": (9.81, ((0.30, 0.58, 0.92), (0.75, 0.88, 0.98)), (0.40, 0.66, 0.32)),
    "moon": (1.62, ((0.02, 0.02, 0.05), (0.08, 0.08, 0.12)), (0.68, 0.68, 0.70)),
    "mars": (3.71, ((0.62, 0.40, 0.30), (0.88, 0.66, 0.50)), (0.70, 0.36, 0.22)),
    "jupiter": (24.79, ((0.55, 0.42, 0.30), (0.86, 0.72, 0.55)), (0.80, 0.64, 0.46)),
    "pluto": (0.62, ((0.01, 0.01, 0.03), (0.05, 0.05, 0.09)), (0.86, 0.80, 0.74)),
}


def altura(g):
    return V0 * V0 / (2 * g)


def no_ar(g):
    return 2 * V0 / g


def cenario(ctx, nome, t):
    import cairo
    g, (topo, baixo), chao = PLANETAS[nome]
    gr = cairo.LinearGradient(0, 0, 0, CHAO)
    gr.add_color_stop_rgb(0, *topo)
    gr.add_color_stop_rgb(1, *baixo)
    ctx.set_source(gr)
    ctx.paint()
    if nome in ("moon", "pluto"):
        ctx.set_source_rgba(1, 1, 1, 0.8)
        for i in range(70):
            x, y = (i * 397) % W, (i * 211) % (CHAO - 80)
            ctx.arc(x, y, 1.5 + (i % 3), 0, 2 * math.pi)
            ctx.fill()
    if nome == "moon":  # a Terra no céu
        ctx.set_source_rgb(0.25, 0.5, 0.9)
        ctx.arc(860, 600, 70, 0, 2 * math.pi)
        ctx.fill()
    if nome == "jupiter":  # faixas de nuvens
        for k in range(7):
            ctx.set_source_rgba(0.6 + 0.05 * k % 0.2, 0.45, 0.32, 0.35)
            ctx.rectangle(0, 470 + k * 110 + 12 * math.sin(t + k), W, 50)
            ctx.fill()
    ctx.set_source_rgb(*chao)
    ctx.rectangle(0, CHAO, W, H - CHAO)
    ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.15)
    for i in range(12):
        ctx.arc((i * 173) % W, CHAO + 40 + (i * 37) % 140, 18 + (i % 4) * 8, 0, 2 * math.pi)
        ctx.fill()
    # régua em metros
    ctx.set_source_rgba(1, 1, 1, 0.6)
    ctx.set_line_width(3)
    ctx.move_to(990, CHAO)
    ctx.line_to(990, CHAO - 8.5 * PX_M)
    ctx.stroke()
    for m in range(0, 9):
        y = CHAO - m * PX_M
        ctx.move_to(975, y)
        ctx.line_to(1005, y)
        ctx.stroke()
        if m % 2 == 0:
            text_center(ctx, f"{m} m", 950, y + 8, 22, WHITE, "SemiBold", alpha=0.8)


def leitura(ctx, l1, l2, cor, y=560):
    from core import round_rect
    round_rect(ctx, 110, y - 52, 390, 130, 24)
    ctx.set_source_rgba(0.04, 0.05, 0.09, 0.75)
    ctx.fill()
    text_center(ctx, l1, 305, y, 44, cor, "ExtraBold")
    text_center(ctx, l2, 305, y + 54, 30, WHITE, "Bold")


def pulo(nome, x=690, inicio=0.5, expr_ar="rindo", escala_tempo=1.0, rotulo=None):
    g = PLANETAS[nome][0]

    def draw(ctx, t, s):
        cenario(ctx, nome, t)
        tau = (t - inicio) * escala_tempo
        T = no_ar(g)
        if 0 <= tau <= T:
            y = V0 * tau - g * tau * tau / 2
            pose = pq.Pose(expr=expr_ar, boca=pq.boca_da_voz(s, t), pulo=0.6, braco_e=2.4, braco_d=2.4)
        else:
            y = 0.0
            ag = max(0.0, min(1.0, (inicio - t) / 0.3)) if tau < 0 else 0.0
            pose = pq.Pose(expr="determinado" if tau < 0 else "feliz", boca=pq.boca_da_voz(s, t),
                           squash=1 - 0.15 * (1 - ag) if tau < 0 and t > inicio - 0.3 else 1.0)
        pq.quark(ctx, x, CHAO - y * PX_M, QH, pose, t)
        hmax = altura(g)
        if tau > T * 0.5 or tau < 0 and t > 2:
            pass
        l1, l2 = rotulo or (f"{hmax:.1f} m HIGH", f"{T:.1f} s IN THE AIR")
        leitura(ctx, l1, l2, YELLOW)
        if escala_tempo != 1.0:
            text_center(ctx, f"{escala_tempo:.0f}x SPEED", 300, 700, 28, WHITE, "Bold", alpha=0.8)
    return draw


def d_jupiter(ctx, t, s):
    """Júpiter: 2,5 vezes mais pesado, o pulo mal sai do chão... e não tem chão de verdade: ele afunda nas nuvens."""
    nome = "jupiter"
    cenario(ctx, nome, t)
    g = PLANETAS[nome][0]
    T = no_ar(g)
    tau = t - 0.5
    y = (V0 * tau - g * tau * tau / 2) if 0 <= tau <= T else 0.0
    afunda = max(0.0, t - 2.4) * 140
    pose = pq.Pose(expr="medo" if t > 2.2 else "tonto", boca=pq.boca_da_voz(s, t), squash=0.82, suor=True,
                   braco_e=2.6 if t > 2.2 else 0.2, braco_d=2.6 if t > 2.2 else 0.2)
    pq.quark(ctx, 690, CHAO - y * PX_M + afunda, QH, pose, t)
    if afunda > 0:  # nuvens cobrindo o Quark
        ctx.set_source_rgba(0.80, 0.64, 0.46, 1)
        ctx.rectangle(0, CHAO, W, H - CHAO)
        ctx.fill()
    leitura(ctx, f"{altura(g) * 100:.0f} cm HIGH", f"{g / G_TERRA:.1f}x HEAVIER", PINK)
    if t > 2.2:
        leitura(ctx, "NO SOLID", "GROUND!", WHITE, y=780)


SEGMENTS = [
    Seg(["What if I jumped on every planet? Earth: half a meter."], pulo("earth", inicio=1.6, expr_ar="feliz",
        rotulo=("0.5 m HIGH", "0.6 s IN THE AIR")), {"title": "JUMP ON EVERY PLANET"}, tail=0.3),
    Seg(["On the Moon, the same jump sends me three meters up, and I float for almost four seconds!"], pulo("moon", inicio=0.4),
        {"big": "THE MOON", "sub": "1/6 OF EARTH'S GRAVITY", "color": WHITE}, tail=0.3, sfx=[(0, 0.4, "whoosh")]),
    Seg(["Mars, about one point three meters. Not bad."], pulo("mars", inicio=0.3),
        {"big": "MARS", "sub": "38% OF EARTH'S GRAVITY", "color": (1.0, 0.55, 0.35)}, tail=0.2),
    Seg(["Jupiter. I weigh two and a half times more, I barely leave the ground... and wait, there's no ground!"],
        d_jupiter, {"big": "JUPITER", "sub": "2.5x EARTH'S GRAVITY", "color": PINK}, tail=0.3),
    Seg(["But on Pluto? Eight meters high, and ten seconds in the air! Not bad for a dwarf planet."], pulo("pluto", inicio=0.3, escala_tempo=2.0),
        {"big": "PLUTO", "sub": "1/16 OF EARTH'S GRAVITY", "color": GREEN}, tail=0.5, sfx=[(0, 0.3, "ding")]),
]
SEGMENTS.append(pq.seg_pergunta("Which planet would you jump on first?", "WHICH PLANET FIRST?",
                                fundo=lambda ctx, t, s: cenario(ctx, "pluto", t)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
