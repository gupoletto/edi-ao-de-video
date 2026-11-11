"""What if the Sun disappeared? Wed 11/11/2026, topic: space, format: what if with the mascot Quark (conflict arc).
Search 11/11: "what if the sun disappeared", median 29.9k (top 1.1M).

Facts:
- sunlight takes about 8 minutes 20 seconds to reach Earth (1 AU / c = 499 s), so for that long we would still see
  the Sun shining;
- changes in gravity also travel at the speed of light, so Earth keeps orbiting for those same ~8 minutes, then
  flies off in a straight line along its orbit (tangent);
- the Moon and planets shine only by reflected sunlight, so they go dark too (the Moon ~1.3 s later);
- commonly cited estimates: within about a week the average surface temperature falls below 0 F (-18 C); in a year,
  about -100 F (-73 C);
- the oceans freeze from the top, and the ice insulates the water below, which can stay liquid for a very long time;
  life around hydrothermal vents does not depend on sunlight.
Arc: hook (the Sun vanishes, nothing happens) -> rising (8:20 countdown) -> conflict (darkness, the Moon goes dark)
-> proof (Earth leaves its orbit) -> twist (the cold) -> payoff (deep oceans and vent life) -> question.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

CHAO = 1240
QH = 460


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def paisagem(ctx, dia=1.0, frio=0.0, t=0.0, estrelas=0.0):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, CHAO)
    g.add_color_stop_rgb(0, 0.28 * dia + 0.01, 0.55 * dia + 0.02, 0.92 * dia + 0.06)
    g.add_color_stop_rgb(1, 0.75 * dia + 0.03, 0.88 * dia + 0.04, 0.98 * dia + 0.10)
    ctx.set_source(g)
    ctx.paint()
    if estrelas > 0:
        ctx.set_source_rgba(1, 1, 1, estrelas)
        for i in range(90):
            ctx.arc((i * 397) % W, (i * 211) % (CHAO - 100), 1.4 + (i % 3) * 0.7, 0, 2 * math.pi)
            ctx.fill()
    # morro: verde que vira branco de gelo com o frio
    verde = (0.40, 0.66, 0.32)
    gelo = (0.86, 0.92, 0.98)
    c = [(a + (b - a) * frio) * (0.35 + 0.65 * max(dia, 0.25)) for a, b in zip(verde, gelo)]
    ctx.set_source_rgb(*c)
    ctx.move_to(0, CHAO + 40)
    ctx.curve_to(300, CHAO - 60, 700, CHAO - 50, W, CHAO + 30)
    ctx.line_to(W, H)
    ctx.line_to(0, H)
    ctx.close_path()
    ctx.fill()


def sol(ctx, x, y, r, a=1.0, t=0.0):
    import cairo
    g = cairo.RadialGradient(x, y, r * 0.2, x, y, r * 1.8)
    g.add_color_stop_rgba(0, 1, 0.95, 0.6, a)
    g.add_color_stop_rgba(0.5, 1, 0.85, 0.3, 0.5 * a)
    g.add_color_stop_rgba(1, 1, 0.8, 0.3, 0)
    ctx.arc(x, y, r * 1.8, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgba(1, 0.92, 0.5, a)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def lua(ctx, x, y, r, a=1.0):
    ctx.set_source_rgba(0.92, 0.92, 0.88, a)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(0.7, 0.7, 0.68, a)
    for dx, dy, rr in ((-12, -8, 9), (14, 10, 7), (4, -18, 5)):
        ctx.arc(x + dx, y + dy, rr, 0, 2 * math.pi)
        ctx.fill()


def caixa(ctx, l1, l2, cor, y=560, cx=W / 2, w=580):
    round_rect(ctx, cx - w / 2, y - 56, w, 136, 26)
    ctx.set_source_rgba(0.04, 0.05, 0.09, 0.75)
    ctx.fill()
    text_center(ctx, l1, cx, y, 52, cor, "ExtraBold")
    text_center(ctx, l2, cx, y + 56, 26 if w < 500 else 30, WHITE, "Bold")


def d_gancho(ctx, t, s):
    """O Sol some... e nada muda: o céu continua claro (a luz que já estava a caminho)."""
    paisagem(ctx)
    sumiu = t > 1.2
    if not sumiu:
        sol(ctx, 800, 640, 70, 1.0, t)
    else:  # contorno pontilhado onde ele estava (a luz que chega ainda é a de 8 minutos atrás)
        sol(ctx, 800, 640, 70, 0.9, t)
        ctx.set_source_rgba(1, 1, 1, 0.9)
        ctx.set_line_width(5)
        ctx.set_dash([12, 10])
        ctx.arc(800, 640, 120, 0, 2 * math.pi)
        ctx.stroke()
        ctx.set_dash([])
        text_center(ctx, "ALREADY GONE", 800, 800, 32, WHITE, "ExtraBold")
    p = pq.Pose(expr="surpreso" if sumiu else "feliz", boca=pq.boca_da_voz(s, t), olhar=(0.7, -0.6),
                braco_d=2.2 if not sumiu else 1.0)
    pq.quark(ctx, 380, CHAO, QH, p, t)


def d_espera(ctx, t, s):
    """Contagem dos 8 min 20 s (acelerada): ainda tem Sol no céu."""
    paisagem(ctx)
    sol(ctx, 800, 640, 70, 0.9, t)
    resta = max(0.0, 500 * (1 - t / (s.dur - 0.3)))
    caixa(ctx, f"{int(resta // 60)}:{int(resta % 60):02d}", "UNTIL THE LAST LIGHT", YELLOW, y=900, cx=770, w=400)
    p = pq.Pose(expr="feliz", boca=pq.boca_da_voz(s, t), andar=t * 1.2, braco_e=1.0, braco_d=0.4)
    pq.quark(ctx, 260 + 20 * math.sin(t), CHAO, QH, p, t)


def d_escuro(ctx, t, s):
    k = ease(t / 0.6)
    paisagem(ctx, dia=1 - k, estrelas=k)
    if t < 0.4:
        sol(ctx, 800, 640, 70, 1 - t / 0.4, t)
    lua(ctx, 230, 560, 46, max(0.0, 1 - max(0.0, t - 1.6) / 0.3) * k)
    if t > 1.9:
        text_center(ctx, "THE MOON GOES DARK TOO", W / 2, 700, 34, WHITE, "ExtraBold")
    p = pq.Pose(expr="medo", boca=pq.boca_da_voz(s, t), braco_e=2.6, braco_d=2.6, suor=True, olhar=(0, -0.6))
    pq.quark(ctx, 600, CHAO, QH, p, t)


def d_orbita(ctx, t, s):
    """Diagrama: a Terra sai pela tangente da órbita."""
    paisagem(ctx, dia=0.0, estrelas=1.0)
    cx, cy, r = W / 2, 820, 300
    ctx.set_source_rgba(1, 1, 1, 0.35)
    ctx.set_line_width(4)
    ctx.set_dash([12, 10])
    ctx.arc(cx, cy, r, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_dash([])
    ang0 = -math.pi / 2 - 0.6
    if t < 1.0:
        ang = ang0 + 0.6 * t
        ex, ey = cx + r * math.cos(ang), cy + r * math.sin(ang)
        sol(ctx, cx, cy, 30, 1.0 - t, t)
    else:
        ang = ang0 + 0.6
        tx, ty = -math.sin(ang), math.cos(ang)
        d = (t - 1.0) * 160
        ex, ey = cx + r * math.cos(ang) + tx * d, cy + r * math.sin(ang) + ty * d
        ctx.set_source_rgba(1.0, 0.85, 0.3, 0.9)
        ctx.set_line_width(5)
        ctx.move_to(cx + r * math.cos(ang), cy + r * math.sin(ang))
        ctx.line_to(ex, ey)
        ctx.stroke()
    ctx.set_source_rgb(0.25, 0.55, 0.95)
    ctx.arc(ex, ey, 26, 0, 2 * math.pi)
    ctx.fill()
    text_center(ctx, "EARTH", ex, ey - 40, 28, WHITE, "Bold")
    if t > 1.2:
        text_center(ctx, "STRAIGHT LINE, NO ORBIT", W / 2, 1180, 36, YELLOW, "ExtraBold")


def d_frio(ctx, t, s):
    k = ease(t / 3.0)
    paisagem(ctx, dia=0.12, frio=k, estrelas=0.9)
    temp = 15 - 33 * k
    caixa(ctx, f"{temp:.0f} °C", f"{temp * 9 / 5 + 32:.0f} °F · ONE WEEK LATER", (0.6, 0.85, 1.0))
    p = pq.Pose(expr="tonto", boca=pq.boca_da_voz(s, t), braco_e=2.9, braco_d=2.9,
                squash=1 - 0.03 * abs(math.sin(t * 30)))  # tremendo de frio
    pq.quark(ctx, 540 + 4 * math.sin(t * 40), CHAO, QH, p, t)


def d_oceano(ctx, t, s):
    """Corte do oceano: gelo em cima, água líquida embaixo e uma fonte hidrotermal com vida."""
    ctx.set_source_rgb(0.02, 0.03, 0.08)
    ctx.paint()
    ctx.set_source_rgb(0.85, 0.92, 0.98)
    ctx.rectangle(0, 470, W, 120)
    ctx.fill()
    ctx.set_source_rgb(0.05, 0.22, 0.42)
    ctx.rectangle(0, 590, W, 800)
    ctx.fill()
    ctx.set_source_rgb(0.18, 0.15, 0.13)
    ctx.move_to(0, 1390)
    ctx.line_to(700, 1390)
    ctx.line_to(780, 1180)
    ctx.line_to(860, 1390)
    ctx.line_to(W, 1390)
    ctx.line_to(W, H)
    ctx.line_to(0, H)
    ctx.close_path()
    ctx.fill()
    for i in range(10):  # "fumaça" quente da fonte
        ph = (t * 0.6 + i * 0.1) % 1
        ctx.set_source_rgba(0.95, 0.55, 0.25, 0.6 * (1 - ph))
        ctx.arc(780 + 25 * math.sin(i + t * 2), 1170 - ph * 300, 14 + ph * 22, 0, 2 * math.pi)
        ctx.fill()
    text_center(ctx, "ICE", W / 2, 548, 40, (0.2, 0.3, 0.45), "ExtraBold")
    text_center(ctx, "LIQUID WATER", 760, 700, 34, WHITE, "ExtraBold")
    text_center(ctx, "HOT VENT", 780, 1440, 30, WHITE, "Bold")
    p = pq.Pose(expr="feliz", boca=pq.boca_da_voz(s, t), braco_e=0.6, braco_d=2.0, capacete=True)
    pq.quark(ctx, 330, 1150 + 20 * math.sin(t * 1.5), 440, p, t)


SEGMENTS = [
    Seg(["What if the Sun just vanished? Look, nothing happens!"], d_gancho, {"title": "WHAT IF THE SUN VANISHED?"},
        tail=0.1),
    Seg(["Its last light is still on the way. For eight minutes, I don't even know."], d_espera,
        {"big": "8 MIN 20 S", "sub": "LIGHT'S TRAVEL TIME", "color": YELLOW}, tail=0.1),
    Seg(["Then, lights out. The Moon goes dark too. It only reflects sunlight."], d_escuro,
        {"big": "LIGHTS OUT", "color": PINK}, tail=0.3, sfx=[(0, 0, "whoosh")]),
    Seg(["And with no Sun to pull it, Earth flies off in a straight line."], d_orbita,
        {"big": "NO MORE ORBIT", "sub": "GRAVITY ALSO TAKES 8 MINUTES", "color": WHITE}, tail=0.2),
    Seg(["In about a week, it's colder than zero Fahrenheit everywhere."], d_frio,
        {"big": "THE BIG FREEZE", "color": (0.6, 0.85, 1.0)}, tail=0.3),
    Seg(["But deep under the ice, the oceans stay liquid, and life at hot vents keeps going."], d_oceano,
        {"big": "LIFE GOES ON", "sub": "DEEP UNDER THE ICE", "color": GREEN}, tail=0.4, sfx=[(0, 0.4, "ding")]),
]
SEGMENTS.append(pq.seg_pergunta("Where would you hide if the Sun vanished?", "WHERE WOULD YOU HIDE?",
                                fundo=lambda ctx, t, s: paisagem(ctx, dia=0.1, frio=1.0, estrelas=1.0)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
