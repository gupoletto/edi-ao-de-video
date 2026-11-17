"""The 5 fastest things humans ever made, ranked (#5 -> #1). Tue 17/11/2026, topic: physics, format: ranking.
Search 17/11: "physics simulation" median 1.14M.

Records (rounded):
- #5 ThrustSSC, 1997: 1,228 km/h (763 mph), the land speed record, first car to break the sound barrier;
- #4 North American X-15, 1967: 7,274 km/h (4,520 mph, Mach 6.7), fastest crewed aircraft;
- #3 Apollo 10 return, 1969: 39,897 km/h (24,791 mph), the fastest humans have ever traveled;
- #2 New Horizons at launch, 2006: about 58,500 km/h (36,400 mph) relative to Earth, the fastest launch ever;
- #1 Parker Solar Probe, perihelion of Dec 2024: about 692,000 km/h (430,000 mph), the fastest object ever made.
Each object crosses the screen at a speed proportional to the log of its real speed; the readout counts up.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import AREA, BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, round_rect, text_center  # noqa: E402

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2 + 80
DOTS = ["5", "4", "3", "2", "1"]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def fundo(ctx, ceu, chao=None, t=0.0, kmh=1000.0):
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.set_source_rgb(*ceu)
    ctx.fill()
    if ceu[0] < 0.1:   # espaço: estrelas
        ctx.set_source_rgba(1, 1, 1, 0.7)
        for i in range(70):
            x = X0 + ((i * 397 - t * 40 * math.log10(kmh)) % (X1 - X0))
            ctx.arc(x, Y0 + (i * 211) % (Y1 - Y0), 1.5 + (i % 3) * 0.6, 0, 2 * math.pi)
            ctx.fill()
    v = 120 * math.log10(kmh)   # riscos de velocidade
    for i in range(26):
        y = Y0 + 60 + (i * 53) % (Y1 - Y0 - 120)
        x = X1 - ((i * 177 + t * v * 3) % (X1 - X0 + 200))
        ctx.set_source_rgba(1, 1, 1, 0.25)
        ctx.set_line_width(3)
        ctx.move_to(x, y)
        ctx.line_to(x + 40 + v * 0.3, y)
        ctx.stroke()
    if chao:
        ctx.rectangle(X0, CY + 120, X1 - X0, Y1 - CY - 120)
        ctx.set_source_rgb(*chao)
        ctx.fill()


def carro(ctx, x, y):
    ctx.set_source_rgb(0.15, 0.17, 0.22)
    ctx.move_to(x - 230, y + 30)
    ctx.line_to(x + 200, y + 30)
    ctx.line_to(x + 240, y + 10)
    ctx.line_to(x - 40, y - 20)
    ctx.line_to(x - 230, y - 10)
    ctx.close_path()
    ctx.fill()
    for dx in (-150, -60, 130):
        ctx.arc(x + dx, y + 34, 26, 0, 2 * math.pi)
        ctx.fill()
    ctx.set_source_rgb(1, 0.5, 0.1)
    ctx.move_to(x - 230, y - 5)
    ctx.line_to(x - 310, y + 5)
    ctx.line_to(x - 230, y + 18)
    ctx.fill()


def aviao(ctx, x, y):
    ctx.set_source_rgb(0.12, 0.13, 0.16)
    ctx.move_to(x + 220, y)
    ctx.line_to(x - 200, y - 22)
    ctx.line_to(x - 200, y + 22)
    ctx.close_path()
    ctx.fill()
    ctx.move_to(x - 40, y)
    ctx.line_to(x - 140, y + 90)
    ctx.line_to(x - 170, y + 90)
    ctx.line_to(x - 120, y)
    ctx.fill()
    ctx.set_source_rgb(1, 0.6, 0.2)
    ctx.arc(x - 210, y, 18, 0, 2 * math.pi)
    ctx.fill()


def capsula(ctx, x, y):
    ctx.set_source_rgb(1, 0.55, 0.15)   # plasma da reentrada
    ctx.move_to(x + 90, y - 90)
    ctx.curve_to(x + 200, y - 60, x + 200, y + 60, x + 90, y + 90)
    ctx.fill()
    ctx.set_source_rgb(0.8, 0.8, 0.82)
    ctx.move_to(x + 90, y - 90)
    ctx.line_to(x + 90, y + 90)
    ctx.line_to(x - 90, y + 30)
    ctx.line_to(x - 90, y - 30)
    ctx.close_path()
    ctx.fill()


def sonda(ctx, x, y):
    ctx.set_source_rgb(0.85, 0.75, 0.3)
    ctx.rectangle(x - 50, y - 40, 100, 80)
    ctx.fill()
    ctx.set_source_rgb(0.9, 0.9, 0.92)
    ctx.arc(x + 20, y - 60, 70, math.pi * 1.1, math.pi * 1.9)
    ctx.fill()


def parker(ctx, x, y):
    import cairo
    g = cairo.RadialGradient(X1 + 300, CY, 50, X1 + 300, CY, 700)
    g.add_color_stop_rgba(0, 1, 0.9, 0.5, 0.9)
    g.add_color_stop_rgba(1, 1, 0.5, 0.1, 0)
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgb(0.95, 0.95, 0.9)   # escudo térmico
    ctx.rectangle(x + 40, y - 90, 26, 180)
    ctx.fill()
    ctx.set_source_rgb(0.4, 0.42, 0.48)
    ctx.rectangle(x - 60, y - 40, 100, 80)
    ctx.fill()


def cena(desenho, kmh, ceu, chao=None, nota=""):
    def draw(ctx, t, s):
        ctx.save()
        ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
        ctx.clip()
        fundo(ctx, ceu, chao, t, kmh)
        ctx.save()
        ctx.translate(CX, CY)
        ctx.scale(1.6, 1.6)
        ctx.translate(-CX, -CY)
        desenho(ctx, CX + 12 * math.sin(t * 9), CY + 4 * math.sin(t * 13))
        ctx.restore()
        ctx.restore()
        if len(s.items) > 1:
            k = ease((t - s.mark(1)) / 1.2)
            round_rect(ctx, X0 + 120, Y0 + 30, X1 - X0 - 240, 130, 24)
            ctx.set_source_rgba(0.03, 0.04, 0.08, 0.8)
            ctx.fill()
            a = ramp(t, s.mark(1), 0.3)
            text_center(ctx, f"{kmh * k:,.0f} KM/H", CX, Y0 + 95, 60, YELLOW, "ExtraBold", alpha=a)
            text_center(ctx, f"{kmh * k / 1.609:,.0f} MPH", CX, Y0 + 138, 28, WHITE, "Bold", alpha=a)
            if nota:
                text_center(ctx, nota, CX, Y1 - 50, 32, WHITE, "Bold", alpha=ramp(t, s.mark(1) + 1.3, 0.3))
    return draw


SEGMENTS = [
    Seg(["The fastest things humans ever built. Number one crosses America in twenty seconds."],
        cena(parker, 692000, (0.02, 0.02, 0.05)), {"title": "FASTEST THINGS EVER MADE"}, tail=0.2),
    Seg(["Number five, ThrustSSC.", "Faster than sound, on wheels."],
        cena(carro, 1228, (0.75, 0.82, 0.92), (0.85, 0.75, 0.55), "FIRST CAR TO BREAK THE SOUND BARRIER"),
        head(5, "THRUSTSSC"), sfx=[(1, 0, "whoosh")]),
    Seg(["Number four, the X-15 rocket plane.", "Over seven thousand. Mach six point seven!"],
        cena(aviao, 7274, (0.25, 0.40, 0.70), None, "FASTEST PLANE WITH A PILOT"), head(4, "X-15"),
        sfx=[(1, 0, "whoosh")]),
    Seg(["Number three, Apollo ten coming home.", "The fastest humans ever went."],
        cena(capsula, 39897, (0.02, 0.02, 0.05), None, "FASTEST HUMANS EVER"), head(3, "APOLLO 10"),
        sfx=[(1, 0, "whoosh")]),
    Seg(["Number two, New Horizons.", "The fastest launch ever, off to Pluto."],
        cena(sonda, 58500, (0.02, 0.02, 0.05), None, "OFF TO PLUTO"), head(2, "NEW HORIZONS"), sfx=[(1, 0, "whoosh")]),
    Seg(["And number one, the Parker Solar Probe.", "Six hundred ninety thousand, diving past the Sun."],
        cena(parker, 692000, (0.02, 0.02, 0.05), None, "FASTEST OBJECT EVER MADE"), head(1, "PARKER SOLAR PROBE"),
        sfx=[(1, 0, "whoosh")], tail=0.7),
]
SEGMENTS.append(pq.seg_pergunta("Which one would you ride in?", "WHICH ONE WOULD YOU RIDE?",
                                fundo=lambda ctx, t, s: cena(parker, 692000, (0.02, 0.02, 0.05))(ctx, t, s)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
