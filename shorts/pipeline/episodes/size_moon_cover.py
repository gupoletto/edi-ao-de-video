"""Can the Moon cover this country? 5 rounds. Sat 31/10/2026, topic: size comparison, format: interactive.

The Moon's diameter is 3,474 km (NASA). Each country's outline (Natural Earth 1:50m, far islands dropped) is drawn
in an azimuthal equidistant projection centred on it, so distances are true; the answer is whether the smallest
circle around the whole country is smaller than the Moon (radius 1,737 km). Computed values:
Mongolia 1,198 km (yes), Australia 2,022 (no), Mexico 1,663 (yes), Chile 2,080 (no), Argentina 1,713 (yes, barely).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import geo  # noqa: E402
import space as sp  # noqa: E402
from core import GREEN, RED, WHITE, YELLOW, Seg, pill, ramp, render, text_center  # noqa: E402
from quiz import countdown, question  # noqa: E402

N = 5
LUA = 1737.4
BOX = (geo.X0, geo.Y0, geo.X1, geo.Y0 + 760)


def preparar(nome, keep):
    rings = geo.country(nome, keep=keep)
    pts = [p for r in rings for p in r]
    lon0 = sum(p[0] for p in pts) / len(pts)
    lat0 = sum(p[1] for p in pts) / len(pts)
    proj = geo.azimutal(lon0, lat0)
    km = [[proj(*p) for p in r] for r in rings]
    (cx, cy), raio = geo.circulo_minimo([p for r in km for p in r])
    return km, (cx, cy), raio


def rodada(nome, keep=0.05):
    km, (mx, my), raio = preparar(nome, keep)
    cabe = raio <= LUA
    escala = 380 / max(raio, LUA)  # px por km: o maior dos dois cabe com folga
    ox, oy = (BOX[0] + BOX[2]) / 2 - mx * escala, (BOX[1] + BOX[3]) / 2 + my * escala

    def tela(x, y):
        return ox + x * escala, oy - y * escala

    def draw(ctx, t, s):
        sp.sky(ctx, t)
        r = s.mark(2)
        for anel in km:
            for i, p in enumerate(anel):
                (ctx.line_to if i else ctx.move_to)(*tela(*p))
            ctx.close_path()
        ctx.set_source_rgb(0.30, 0.78, 0.55)
        ctx.fill_preserve()
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(3)
        ctx.stroke()
        # a Lua desce de cima até o centro do país, na mesma escala
        k = ramp(t, r - 0.2, 0.9)
        cx, cy = tela(mx, my)
        lx, ly = cx, (BOX[1] - 400) + (cy - BOX[1] + 400) * k
        if t < r:  # antes da resposta, a Lua espera pequena no canto
            sp.planet(ctx, "moon", BOX[2] - 110, BOX[1] + 110, 70)
            text_center(ctx, "MOON", BOX[2] - 110, BOX[1] + 220, 30, WHITE)
        else:
            ctx.push_group()
            sp.planet(ctx, "moon", lx, ly, LUA * escala)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(0.78)
        text_center(ctx, nome.upper(), (BOX[0] + BOX[2]) / 2, BOX[3] + 70, 56, WHITE, "ExtraBold")
        countdown(ctx, t, s.mark(1), cx=BOX[0] + 110, cy=BOX[1] + 110)
        a = ramp(t, r + 1.0, 0.3)
        pill(ctx, "YES, IT FITS" if cabe else "NO, TOO BIG", 540, BOX[3] + 160, GREEN if cabe else RED, a, size=50)
    return draw


def d_intro(ctx, t, s):
    sp.sky(ctx, t)
    sp.planet(ctx, "moon", sp.CX, sp.CY - 40, 300 + 10 * math.sin(t * 2))
    text_center(ctx, "3,474 km", sp.CX, sp.CY + 340, 60, YELLOW, "ExtraBold", alpha=ramp(t, 0.8, 0.3))


def d_outro(ctx, t, s):
    d_intro(ctx, t + 2, s)


SEGMENTS = [
    Seg(["The Moon is three thousand four hundred seventy four kilometers wide. Can it cover these countries?"],
        d_intro, {"title": "CAN THE MOON COVER IT?"}, tail=0.2),
    question(1, N, "MONGOLIA", "Round one. Mongolia.", "Easily! Mongolia fits with room to spare.", rodada("Mongolia")),
    question(2, N, "AUSTRALIA", "Round two. Australia.", "No! Australia is wider than the Moon.", rodada("Australia"),
             result_sfx="ding"),
    question(3, N, "MEXICO", "Round three. Mexico.", "Yes, but just barely!", rodada("Mexico")),
    question(4, N, "CHILE", "Round four. Chile. It's thin, but…", "Too long! Chile sticks out on both ends.",
             rodada("Chile", keep=0.02)),
    question(5, N, "ARGENTINA", "Last one. Argentina.", "Yes, by only a few dozen kilometers!", rodada("Argentina")),
    Seg(["How many did you get right? Comment your score!"], d_outro, {"title": "HOW MANY DID YOU GET?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
