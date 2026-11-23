"""What if Earth stopped spinning? Sun 15/11/2026, topic: Earth & nature, format: what if with the mascot Quark
(conflict arc). Search 15/11: "what if earth stopped spinning", median 22.5k.

Facts:
- at the equator Earth's surface moves at about 1,670 km/h (1,040 mph): circumference 40,075 km / ~24 h;
- if the planet stopped suddenly, the atmosphere and everything not bolted down would keep moving east at that speed:
  supersonic winds, worse than any tornado;
- without the spin, the equatorial bulge would no longer hold the oceans there: over time water would migrate toward
  the poles, leaving two polar oceans and a giant continent around the equator (NASA/Esri modelling);
- with no rotation, one day would last a whole year (the Sun would rise and set once per orbit): about six months of
  daylight, then six months of night;
- Earth's rotation slows very gradually (days get ~1.7 ms longer per century); it will not stop.
Quark never really gets hurt: he gets blown away comically and lands safely.
Arc: hook (the spin stops) -> rising (1,670 km/h) -> conflict (everything flies east) -> proof (oceans move to the
poles) -> twist (a day lasts a year) -> payoff (it won't happen) -> question.
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


def paisagem(ctx, t, vento=0.0, escuro=0.0):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, CHAO)
    k = 1 - 0.85 * escuro
    g.add_color_stop_rgb(0, 0.28 * k, 0.55 * k, 0.92 * k)
    g.add_color_stop_rgb(1, 0.75 * k, 0.88 * k, 0.98 * k)
    ctx.set_source(g)
    ctx.paint()
    ctx.set_source_rgb(0.40 * k + 0.05, 0.66 * k + 0.05, 0.32 * k + 0.05)
    ctx.rectangle(0, CHAO, W, H - CHAO)
    ctx.fill()
    for i in range(int(40 * vento)):   # riscos de vento para o leste (direita)
        y = 420 + (i * 47) % 800
        x = ((i * 233 + t * 2600) % (W + 400)) - 200
        ctx.set_source_rgba(1, 1, 1, 0.45)
        ctx.set_line_width(4)
        ctx.move_to(x, y)
        ctx.line_to(x - 180, y)
        ctx.stroke()


def caixa(ctx, l1, l2, cor, y=560):
    round_rect(ctx, 200, y - 56, 680, 136, 26)
    ctx.set_source_rgba(0.04, 0.05, 0.09, 0.78)
    ctx.fill()
    text_center(ctx, l1, W / 2, y, 52, cor, "ExtraBold")
    text_center(ctx, l2, W / 2, y + 56, 30, WHITE, "Bold")


def globo(ctx, x, y, r, giro, mapa_novo=0.0):
    import cairo
    ctx.save()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.clip()
    ctx.set_source_rgb(0.12, 0.35, 0.75)
    ctx.paint()
    ctx.set_source_rgb(0.30, 0.62, 0.32)
    for k in range(5):   # continentes passando (giro)
        cx = x - r + ((k * 0.45 * r + giro * r) % (2.6 * r)) - 0.3 * r
        ctx.save()
        ctx.translate(cx, y + (k % 3 - 1) * r * 0.35)
        ctx.scale(1.0, 0.7)
        ctx.arc(0, 0, r * 0.22, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
    if mapa_novo > 0:   # oceanos nos polos, terra no equador
        ctx.set_source_rgba(0.55, 0.50, 0.32, mapa_novo)
        ctx.rectangle(x - r, y - r * 0.5, 2 * r, r)
        ctx.fill()
        ctx.set_source_rgba(0.12, 0.35, 0.75, mapa_novo)
        ctx.rectangle(x - r, y - r, 2 * r, r * 0.5)
        ctx.rectangle(x - r, y + r * 0.5, 2 * r, r * 0.5)
        ctx.fill()
    ctx.restore()
    g = cairo.RadialGradient(x - r * 0.4, y - r * 0.4, r * 0.1, x, y, r)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.25)
    g.add_color_stop_rgba(1, 0, 0, 0.1, 0.35)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()


def d_gancho(ctx, t, s):
    paisagem(ctx, t, vento=ease((t - 3.2) / 0.8))
    giro = t * 0.8 if t < 2.4 else 2.4 * 0.8
    globo(ctx, 800, 640, 130, giro)
    if t > 2.4:
        text_center(ctx, "STOP", 800, 820, 44, PINK, "ExtraBold")
    p = pq.Pose(expr="surpreso" if t > 2.4 else "feliz", boca=pq.boca_da_voz(s, t), braco_d=1.4,
                inclina=0.15 * ease((t - 3.4) / 0.6))
    pq.quark(ctx, 380, CHAO, QH, p, t)


def d_rapido(ctx, t, s):
    paisagem(ctx, t, vento=0.6)
    globo(ctx, 540, 820, 230, 2.0)
    ctx.set_source_rgb(1, 0.85, 0.2)
    ctx.set_line_width(6)
    ctx.move_to(310, 820)
    ctx.line_to(770, 820)
    ctx.stroke()
    caixa(ctx, "1,670 KM/H", "1,040 MPH AT THE EQUATOR", YELLOW, y=1140)


def d_voa(ctx, t, s):
    paisagem(ctx, t, vento=1.0)
    for i in range(6):   # coisas voando para o leste
        x = ((i * 190 + t * 900) % (W + 300)) - 150
        y = 600 + (i * 97) % 500 + 30 * math.sin(t * 5 + i)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(t * 6 + i)
        ctx.set_source_rgb(*((0.55, 0.38, 0.22) if i % 2 else (0.85, 0.3, 0.25)))
        ctx.rectangle(-30, -18, 60, 36)
        ctx.fill()
        ctx.restore()
    p = pq.Pose(expr="medo", boca=pq.boca_da_voz(s, t), braco_e=2.9, braco_d=2.9, pulo=0.7,
                inclina=0.9 + 0.2 * math.sin(t * 7), suor=True)
    pq.quark(ctx, 300 + 350 * ease(t / 2.5), 1000 - 80 * math.sin(t * 3), QH, p, t)
    caixa(ctx, "SUPERSONIC WIND", "EVERYTHING KEEPS MOVING EAST", PINK)


def d_mapa(ctx, t, s):
    paisagem(ctx, t)
    globo(ctx, 540, 840, 300, 2.0, mapa_novo=ease((t - 0.6) / 1.5))
    if t > 1.8:
        text_center(ctx, "OCEAN", 540, 640, 36, WHITE, "ExtraBold")
        text_center(ctx, "ONE GIANT CONTINENT", 540, 856, 36, WHITE, "ExtraBold")
        text_center(ctx, "OCEAN", 540, 1060, 36, WHITE, "ExtraBold")


def d_ano(ctx, t, s):
    fase = (t / 2.2) % 1
    escuro = 0.0 if fase < 0.5 else 1.0
    paisagem(ctx, t, escuro=ease((fase - 0.45) / 0.1) if fase < 0.6 else escuro)
    caixa(ctx, "1 DAY = 1 YEAR", "6 MONTHS SUN · 6 MONTHS NIGHT", YELLOW)
    p = pq.Pose(expr="pensando" if escuro < 0.5 else "medo", boca=pq.boca_da_voz(s, t), braco_d=1.6)
    pq.quark(ctx, 540, CHAO, QH, p, t)


def d_ufa(ctx, t, s):
    paisagem(ctx, t)
    globo(ctx, 800, 640, 130, t * 0.8)
    p = pq.Pose(expr="rindo", boca=pq.boca_da_voz(s, t), braco_e=2.6, braco_d=2.6)
    pq.quark(ctx, 380, CHAO, QH, p, t)


SEGMENTS = [
    Seg(["What if Earth suddenly stopped spinning? The ground stops, but the air doesn't!"], d_gancho,
        {"title": "WHAT IF EARTH STOPPED SPINNING?"}, tail=0.2),
    Seg(["At the equator, the ground moves at sixteen hundred kilometers per hour."], d_rapido,
        {"big": "1,670 KM/H", "color": YELLOW}, tail=0.1),
    Seg(["Stop it, and everything not bolted down keeps flying east. Including me!"], d_voa,
        {"big": "WHOOSH", "color": PINK}, tail=0.2, sfx=[(0, 0, "whoosh")]),
    Seg(["Over time the oceans slide to the poles, and one giant continent rises around the equator."], d_mapa,
        {"big": "A NEW MAP", "color": WHITE}, tail=0.2),
    Seg(["And one day would last a whole year. Six months of sun, then six months of night."], d_ano,
        {"big": "LONGEST DAY", "big_size": 92, "color": YELLOW}, tail=0.2),
    Seg(["Relax, Earth is only slowing down by milliseconds per century."], d_ufa,
        {"big": "PHEW", "color": GREEN}, tail=0.4, sfx=[(0, 0.2, "ding")]),
]
SEGMENTS.append(pq.seg_pergunta("Endless day or endless night, which one?", "DAY OR NIGHT?",
                                fundo=lambda ctx, t, s: paisagem(ctx, t, escuro=0.5)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
