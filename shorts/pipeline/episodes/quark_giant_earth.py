"""What if Earth was the size of Jupiter? Fri 13/11/2026, topic: size and scale, format: what if with the mascot
Quark (conflict arc). Search 13/11: "what if earth was the size of", median 56k ("Earth the size of Jupiter?!" 745k).

Physics (same rock, same density): surface gravity g = (4/3) pi G rho R grows in proportion to the radius, and so
does escape velocity. Jupiter's radius is ~11.2 Earth radii, so:
- gravity ~11 g (110 m/s^2): you would weigh ~11 times more;
- trained fighter pilots in g-suits handle about 9 g for a few seconds before blacking out; 11 g all the time is far
  beyond what a body can take;
- escape velocity 11.2 km/s x 11.2 = ~125 km/s, far more than any rocket can reach from the ground.
Quark never really gets hurt: he is squashed flat as a joke and pops back.
Arc: hook (Earth grows) -> rising (11x wider) -> conflict (11x heavier, can't stand) -> proof (fighter pilots) ->
twist (no rocket could leave) -> payoff (back to normal Earth) -> question.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

CHAO = 1240
QH = 460
K = 11.2


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def espaco(ctx):
    ctx.set_source_rgb(0.02, 0.02, 0.06)
    ctx.paint()
    ctx.set_source_rgba(1, 1, 1, 0.8)
    for i in range(110):
        ctx.arc((i * 397) % W, (i * 211) % H, 1.3 + (i % 3) * 0.6, 0, 2 * math.pi)
        ctx.fill()


def terra(ctx, x, y, r):
    import cairo
    g = cairo.RadialGradient(x - r * 0.3, y - r * 0.3, r * 0.1, x, y, r)
    g.add_color_stop_rgb(0, 0.35, 0.65, 1.0)
    g.add_color_stop_rgb(1, 0.08, 0.25, 0.6)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.save()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.clip()
    ctx.set_source_rgb(0.25, 0.62, 0.3)
    for dx, dy, rr in ((-0.3, -0.2, 0.35), (0.35, 0.1, 0.3), (-0.05, 0.45, 0.22)):
        ctx.save()
        ctx.translate(x + dx * r, y + dy * r)
        ctx.scale(1.3, 0.8)
        ctx.arc(0, 0, rr * r, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
    ctx.restore()


def chao_terra(ctx, t, gigante=False):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, CHAO)
    g.add_color_stop_rgb(0, 0.28, 0.55, 0.92)
    g.add_color_stop_rgb(1, 0.75, 0.88, 0.98)
    ctx.set_source(g)
    ctx.paint()
    ctx.set_source_rgb(0.40, 0.66, 0.32)
    ctx.rectangle(0, CHAO, W, H - CHAO)
    ctx.fill()
    if gigante:  # horizonte quase reto: planeta enorme
        ctx.set_source_rgba(1, 1, 1, 0.5)
        ctx.set_line_width(3)
        ctx.move_to(0, CHAO + 2)
        ctx.line_to(W, CHAO + 2)
        ctx.stroke()


def caixa(ctx, l1, l2, cor, y=560):
    round_rect(ctx, 220, y - 56, 640, 136, 26)
    ctx.set_source_rgba(0.04, 0.05, 0.09, 0.78)
    ctx.fill()
    text_center(ctx, l1, W / 2, y, 52, cor, "ExtraBold")
    text_center(ctx, l2, W / 2, y + 56, 30, WHITE, "Bold")


def d_gancho(ctx, t, s):
    espaco(ctx)
    k = ease((t - 0.4) / 2.0)
    r = 40 + (40 * K - 40) * k
    terra(ctx, W / 2, 1200 + r * 0.55, r)
    ctx.set_source_rgba(1, 0.75, 0.45, 0.9)  # contorno de Júpiter para comparação
    ctx.set_line_width(4)
    ctx.set_dash([14, 10])
    ctx.arc(W / 2, 1200 + 40 * K * 0.55, 40 * K, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_dash([])
    p = pq.Pose(expr="surpreso" if t > 1.0 else "feliz", boca=pq.boca_da_voz(s, t), braco_e=2.4, braco_d=2.4)
    pq.quark(ctx, 540, 1000 - 200 * k, 440, p, t)


def d_largo(ctx, t, s):
    espaco(ctx)
    k = ease(t / 1.5)
    terra(ctx, 220, 760, 22)
    text_center(ctx, "EARTH", 220, 820, 30, WHITE, "Bold")
    r = 22 + 22 * (K - 1) * k
    terra(ctx, 640, 760, r)
    text_center(ctx, "GIANT EARTH", 640, 760 + r + 40, 30, WHITE, "Bold", alpha=k)
    caixa(ctx, f"{1 + (K - 1) * k:.1f}x WIDER", "SAME ROCK, SAME DENSITY", YELLOW, y=1110)


def d_pesado(ctx, t, s):
    chao_terra(ctx, t, True)
    k = ease((t - 0.3) / 0.7)
    p = pq.Pose(expr="tonto", boca=pq.boca_da_voz(s, t), squash=1 - 0.55 * k, braco_e=0.1, braco_d=0.1, suor=True)
    pq.quark(ctx, 540, CHAO, QH, p, t)
    caixa(ctx, f"{1 + (K - 1) * k:.0f}x HEAVIER", "THAT'S 11 g, ALL DAY LONG", PINK)


def d_piloto(ctx, t, s):
    chao_terra(ctx, t, True)
    for i, (rot, g, cor) in enumerate((("YOU ON EARTH", 1, GREEN), ("ROLLER COASTER", 4, YELLOW),
                                       ("FIGHTER PILOT", 9, (1.0, 0.6, 0.2)), ("GIANT EARTH", K, PINK))):
        k = ease((t - 0.3 - 0.35 * i) / 0.6)
        y = 560 + i * 130
        round_rect(ctx, 130, y - 40, 820, 100, 20)
        ctx.set_source_rgba(0.04, 0.05, 0.09, 0.78)
        ctx.fill()
        round_rect(ctx, 150, y + 18, 560 * g / K * k, 26, 13)
        ctx.set_source_rgb(*cor)
        ctx.fill()
        text_center(ctx, rot, 340, y + 4, 30, WHITE, "Bold")
        text_center(ctx, f"{g:.0f} g", 840, y + 14, 44, cor, "ExtraBold", alpha=k)


def d_foguete(ctx, t, s):
    chao_terra(ctx, t, True)
    sobe = 300 * math.sin(math.pi * min(1.0, t / 2.2))
    x, y = 760, CHAO - 40 - sobe
    ctx.set_source_rgb(0.9, 0.92, 0.95)
    ctx.rectangle(x - 30, y - 200, 60, 200)
    ctx.fill()
    ctx.move_to(x - 30, y - 200)
    ctx.line_to(x, y - 260)
    ctx.line_to(x + 30, y - 200)
    ctx.fill()
    ctx.set_source_rgba(1, 0.6, 0.2, 0.9)
    ctx.move_to(x - 22, y)
    ctx.line_to(x, y + 70 + 20 * math.sin(t * 30))
    ctx.line_to(x + 22, y)
    ctx.fill()
    caixa(ctx, "125 km/s", "TO ESCAPE (EARTH: 11 km/s)", PINK)
    p = pq.Pose(expr="medo", boca=pq.boca_da_voz(s, t), squash=0.5, braco_e=0.1, braco_d=0.1, olhar=(0.8, -0.6))
    pq.quark(ctx, 300, CHAO, QH, p, t)


def d_volta(ctx, t, s):
    chao_terra(ctx, t)
    k = ease((t - 0.2) / 0.5)
    pulo = max(0.0, math.sin(min(math.pi, (t - 0.2) * 3))) * 120
    p = pq.Pose(expr="rindo", boca=pq.boca_da_voz(s, t), squash=0.5 + 0.5 * k, braco_e=2.6, braco_d=2.6,
                pulo=0.5 if pulo > 10 else 0)
    pq.quark(ctx, 540, CHAO - pulo, QH, p, t)


SEGMENTS = [
    Seg(["What if Earth suddenly grew as big as Jupiter?"], d_gancho, {"title": "EARTH THE SIZE OF JUPITER?"},
        tail=0.1),
    Seg(["Same rock, eleven times wider. More rock under your feet means more gravity."], d_largo,
        {"big": "11x WIDER", "color": YELLOW}, tail=0.1),
    Seg(["I'd weigh eleven times more. I can't even stand up!"], d_pesado,
        {"big": "11x HEAVIER", "color": PINK}, tail=0.3),
    Seg(["Fighter pilots black out around nine g, for a few seconds. This is eleven g, forever."], d_piloto,
        {"big": "WORSE THAN A JET", "big_size": 90, "color": (1.0, 0.6, 0.2)}, tail=0.3),
    Seg(["And no rocket could ever leave. You'd need a hundred twenty five kilometers per second."], d_foguete,
        {"big": "TRAPPED", "color": PINK}, tail=0.3, sfx=[(0, 0.3, "whoosh")]),
    Seg(["Okay, back to normal. Our Earth is just the right size."], d_volta,
        {"big": "JUST RIGHT", "color": GREEN}, tail=0.4, sfx=[(0, 0.2, "ding")]),
]
SEGMENTS.append(pq.seg_pergunta("Would you survive one day on giant Earth?", "WOULD YOU SURVIVE A DAY?",
                                fundo=lambda ctx, t, s: chao_terra(ctx, t, True)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
