"""The 5 fastest winds ever measured, ranked (#5 -> #1). Sun 15/11/2026, topic: Earth & nature (+ space twist), format:
ranking. Search 15/11: "tornado simulation", median 299k.

Facts:
- #5 a Category 5 hurricane: sustained winds of 157 mph (252 km/h) or more (Saffir-Simpson scale);
- #4 Cyclone Olivia, Barrow Island, Australia, 1996: a 253 mph (408 km/h) gust, the fastest wind ever measured that
  was not inside a tornado (WMO record);
- #3 the Bridge Creek-Moore tornado, Oklahoma, 1999: about 302 mph (486 km/h), measured by a mobile Doppler radar;
- #2 Neptune: winds up to about 1,300 mph (2,100 km/h), the fastest in the solar system;
- #1 exoplanet HD 189733b: winds estimated around 5,400 mph (8,700 km/h); its blue color comes from silicate
  particles, so it may "rain" glass sideways.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import AREA, BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, round_rect, text_center  # noqa: E402

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2 + 70
DOTS = ["5", "4", "3", "2", "1"]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def vento(ctx, t, mph, cor=(1, 1, 1)):
    """Riscos de vento atravessando o quadro; a velocidade na tela cresce com o log da velocidade real."""
    v = 260 * math.log10(mph)
    for i in range(46):
        y = Y0 + 40 + (i * 37) % (Y1 - Y0 - 80)
        x = X0 + ((i * 211 + t * v) % (X1 - X0 + 300)) - 150
        L = 40 + v * 0.18
        ctx.set_source_rgba(*cor, 0.35)
        ctx.set_line_width(3)
        ctx.move_to(x, y)
        ctx.line_to(x - L, y)
        ctx.stroke()


def medidor(ctx, mph, kmh, cor, a):
    round_rect(ctx, X0 + 150, Y0 + 30, X1 - X0 - 300, 120, 24)
    ctx.set_source_rgba(0.03, 0.04, 0.08, 0.8)
    ctx.fill()
    text_center(ctx, f"{mph:,.0f} MPH", CX, Y0 + 92, 58, cor, "ExtraBold", alpha=a)
    text_center(ctx, f"{kmh:,.0f} KM/H", CX, Y0 + 132, 28, WHITE, "Bold", alpha=a)


def furacao(ctx, t):
    ctx.save()
    ctx.translate(CX, CY)
    ctx.rotate(-t * 1.2)
    for k in range(5):
        ctx.rotate(2 * math.pi / 5)
        ctx.set_source_rgba(0.92, 0.95, 1.0, 0.85)
        ctx.set_line_width(46)
        ctx.new_path()
        for j in range(60):
            a = j * 0.07
            r = 30 + j * 4.5
            ctx.line_to(r * math.cos(a), r * math.sin(a))
        ctx.stroke()
    ctx.set_source_rgb(0.12, 0.25, 0.45)
    ctx.arc(0, 0, 26, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def anemometro(ctx, t):
    ctx.set_source_rgb(0.75, 0.78, 0.82)
    ctx.rectangle(CX - 8, CY - 40, 16, 300)
    ctx.fill()
    for k in range(3):
        a = t * 18 + k * 2 * math.pi / 3
        x, y = CX + 120 * math.cos(a), CY - 40 + 40 * math.sin(a)
        ctx.set_line_width(8)
        ctx.move_to(CX, CY - 40)
        ctx.line_to(x, y)
        ctx.stroke()
        ctx.arc(x, y, 34, 0, 2 * math.pi)
        ctx.fill()


def tornado(ctx, t):
    for j in range(40):
        f = j / 39
        y = CY + 260 - f * 560
        w = 30 + 230 * f ** 1.6
        x = CX + 30 * math.sin(t * 2 + f * 4)
        ctx.set_source_rgba(0.55, 0.55, 0.6, 0.35)
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1, 0.25)
        ctx.arc(0, 0, w, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
    for k in range(18):   # destroços girando
        a = t * 4 + k
        f = (k * 0.13 + t * 0.2) % 1
        ctx.set_source_rgb(0.35, 0.25, 0.18)
        ctx.rectangle(CX + (40 + 200 * f) * math.cos(a), CY + 200 - f * 450, 10, 6)
        ctx.fill()


def planeta(ctx, t, c0, c1, faixas=True, vidro=False):
    import cairo
    g = cairo.RadialGradient(CX - 80, CY - 80, 30, CX, CY, 270)
    g.add_color_stop_rgb(0, *c0)
    g.add_color_stop_rgb(1, *c1)
    ctx.arc(CX, CY, 270, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    if faixas:
        ctx.save()
        ctx.arc(CX, CY, 270, 0, 2 * math.pi)
        ctx.clip()
        for k in range(6):
            ctx.set_source_rgba(1, 1, 1, 0.12)
            ctx.rectangle(CX - 300 + (t * 120 * (1 + k % 2)) % 80, CY - 200 + k * 70, 600, 16)
            ctx.fill()
        ctx.restore()
    if vidro:
        for k in range(30):
            x = X0 + ((k * 173 + t * 900) % (X1 - X0))
            y = Y0 + 200 + (k * 97) % 700
            ctx.set_source_rgba(0.85, 0.95, 1.0, 0.9)
            ctx.move_to(x, y)
            ctx.line_to(x - 40, y + 4)
            ctx.line_to(x - 36, y + 10)
            ctx.close_path()
            ctx.fill()


def cena(desenho, mph, cor_fundo, cor_med=YELLOW):
    kmh = mph * 1.609

    def draw(ctx, t, s):
        ctx.save()
        ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
        ctx.clip()
        ctx.set_source_rgb(*cor_fundo)
        ctx.paint()
        desenho(ctx, t)
        vento(ctx, t, mph)
        if len(s.items) > 1:   # abertura e pergunta final: sem número
            k = ease((t - s.mark(1)) / 1.0)
            medidor(ctx, mph * k, kmh * k, cor_med, ramp(t, s.mark(1), 0.3))
        ctx.restore()
    return draw


SEGMENTS = [
    Seg(["The fastest winds ever measured. Number one isn't even on Earth."],
        cena(tornado, 302, (0.30, 0.33, 0.40)), {"title": "THE 5 FASTEST WINDS EVER"}, tail=0.2),
    Seg(["Number five, a Category five hurricane.", "Over one fifty seven miles per hour."],
        cena(lambda c, t: furacao(c, t), 157, (0.10, 0.25, 0.45)), head(5, "CATEGORY 5 HURRICANE"), sfx=[(1, 0, "ding")]),
    Seg(["Number four, Cyclone Olivia.", "A two fifty three mile per hour gust."],
        cena(anemometro, 253, (0.20, 0.30, 0.42)), head(4, "CYCLONE OLIVIA"), sfx=[(1, 0, "ding")]),
    Seg(["Number three, an Oklahoma tornado.", "Radar clocked three hundred two."],
        cena(tornado, 302, (0.30, 0.33, 0.40)), head(3, "BRIDGE CREEK-MOORE TORNADO"), sfx=[(1, 0, "whoosh")]),
    Seg(["Number two, Neptune.", "Thirteen hundred miles per hour."],
        cena(lambda c, t: planeta(c, t, (0.45, 0.65, 1.0), (0.10, 0.20, 0.60)), 1300, (0.02, 0.02, 0.06)),
        head(2, "NEPTUNE"), sfx=[(1, 0, "ding")]),
    Seg(["And number one, a faraway blue planet.", "Fifty four hundred miles per hour, and it may rain glass."],
        cena(lambda c, t: planeta(c, t, (0.40, 0.70, 1.0), (0.05, 0.15, 0.55), vidro=True), 5400, (0.02, 0.02, 0.06),
             PINK), head(1, "HD 189733b"), sfx=[(1, 0, "whoosh")], tail=0.7),
]
SEGMENTS.append(pq.seg_pergunta("Which wind would you stand in?", "WHICH WOULD YOU SURVIVE?",
                                fundo=lambda ctx, t, s: cena(tornado, 302, (0.30, 0.33, 0.40))(ctx, t, s)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
