"""The 5 coldest places in the universe, ranked (#5 -> #1). Wed 18/11/2026, topic: space, format: ranking (twist: #1
is in a lab on Earth). Search 18/11: "coldest place in the universe", median 17.9k.

Facts (rounded):
- #5 Vostok Station, Antarctica: -89.2 C (-128.6 F), 21 July 1983, the coldest air temperature measured on Earth;
- #4 surface of Pluto: about -230 C (-382 F);
- #3 empty space: the cosmic microwave background, 2.7 K (-270.4 C);
- #2 Boomerang Nebula: about 1 K (-272 C), the coldest natural place known, colder than the background;
- #1 a lab on Earth: in 2021 a Bose-Einstein condensate dropped down a tower in Bremen, Germany, reached about 38
  trillionths of a degree above absolute zero (38 picokelvin), the coldest temperature ever measured.
Absolute zero = 0 K = -273.15 C.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import AREA, BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, round_rect, text_center  # noqa: E402

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2 + 60
DOTS = ["5", "4", "3", "2", "1"]
GELO = (0.55, 0.85, 1.0)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def fundo(ctx, cor):
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.set_source_rgb(*cor)
    ctx.fill()


def neve(ctx, t, n=60):
    ctx.set_source_rgba(1, 1, 1, 0.8)
    for i in range(n):
        x = X0 + ((i * 173 + t * 30 * (1 + i % 3)) % (X1 - X0))
        y = Y0 + ((i * 97 + t * 90) % (Y1 - Y0))
        ctx.arc(x, y, 2 + i % 3, 0, 2 * math.pi)
        ctx.fill()


def estrelas(ctx):
    ctx.set_source_rgba(1, 1, 1, 0.75)
    for i in range(80):
        ctx.arc(X0 + (i * 397) % (X1 - X0), Y0 + (i * 211) % (Y1 - Y0), 1.3 + (i % 3) * 0.6, 0, 2 * math.pi)
        ctx.fill()


def antartida(ctx, t):
    fundo(ctx, (0.55, 0.65, 0.80))
    ctx.set_source_rgb(0.93, 0.96, 1.0)
    ctx.move_to(X0, CY + 120)
    ctx.curve_to(X0 + 300, CY + 60, X1 - 300, CY + 160, X1, CY + 90)
    ctx.line_to(X1, Y1)
    ctx.line_to(X0, Y1)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgb(0.75, 0.25, 0.2)   # base
    ctx.rectangle(CX - 90, CY + 20, 180, 90)
    ctx.fill()
    neve(ctx, t)


def plutao(ctx, t):
    import cairo
    fundo(ctx, (0.02, 0.02, 0.05))
    estrelas(ctx)
    g = cairo.RadialGradient(CX - 80, CY - 80, 30, CX, CY, 260)
    g.add_color_stop_rgb(0, 0.92, 0.85, 0.78)
    g.add_color_stop_rgb(1, 0.55, 0.42, 0.35)
    ctx.arc(CX, CY, 260, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgba(1, 0.97, 0.93, 0.9)   # o "coração"
    ctx.save()
    ctx.translate(CX + 60, CY + 60)
    ctx.scale(4, 4)
    ctx.move_to(0, 18)
    ctx.curve_to(-26, 0, -14, -20, 0, -6)
    ctx.curve_to(14, -20, 26, 0, 0, 18)
    ctx.restore()
    ctx.fill()


def espaco(ctx, t):
    fundo(ctx, (0.02, 0.02, 0.05))
    for i in range(120):   # manchas do fundo de micro-ondas
        x = X0 + (i * 397) % (X1 - X0)
        y = Y0 + (i * 211) % (Y1 - Y0)
        ctx.set_source_rgba(0.9 if i % 2 else 0.3, 0.5, 0.2 if i % 2 else 0.9, 0.12)
        ctx.arc(x, y, 60 + (i % 5) * 20, 0, 2 * math.pi)
        ctx.fill()
    estrelas(ctx)


def bumerangue(ctx, t):
    import cairo
    fundo(ctx, (0.02, 0.02, 0.05))
    estrelas(ctx)
    for lado in (-1, 1):
        g = cairo.RadialGradient(CX, CY, 10, CX + lado * 200, CY, 320)
        g.add_color_stop_rgba(0, 0.6, 0.75, 1.0, 0.9)
        g.add_color_stop_rgba(1, 0.2, 0.3, 0.8, 0.0)
        ctx.save()
        ctx.translate(CX + lado * 170, CY)
        ctx.scale(1.6, 0.8)
        ctx.arc(0, 0, 160, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source(g)
        ctx.fill()
    ctx.set_source_rgb(1, 1, 0.9)
    ctx.arc(CX, CY, 16, 0, 2 * math.pi)
    ctx.fill()


def laboratorio(ctx, t):
    fundo(ctx, (0.08, 0.10, 0.14))
    ctx.set_source_rgb(0.7, 0.74, 0.8)   # torre de queda
    ctx.rectangle(CX - 60, Y0 + 120, 120, Y1 - Y0 - 200)
    ctx.fill()
    y = Y0 + 160 + ((t * 120) % (Y1 - Y0 - 320))
    for r, a in ((60, 0.15), (38, 0.35), (20, 0.9)):   # nuvem de átomos caindo
        ctx.set_source_rgba(*GELO, a)
        ctx.arc(CX, y, r, 0, 2 * math.pi)
        ctx.fill()


def cena(desenho, celsius, kelvin_txt, nota):
    def draw(ctx, t, s):
        ctx.save()
        ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
        ctx.clip()
        desenho(ctx, t)
        ctx.restore()
        if len(s.items) > 1:
            a = ramp(t, s.mark(1), 0.3)
            round_rect(ctx, X0 + 130, Y0 + 30, X1 - X0 - 260, 130, 24)
            ctx.set_source_rgba(0.03, 0.04, 0.08, 0.8)
            ctx.fill()
            text_center(ctx, celsius, CX, Y0 + 95, 56, GELO, "ExtraBold", alpha=a)
            text_center(ctx, kelvin_txt, CX, Y0 + 138, 26, WHITE, "Bold", alpha=a)
            text_center(ctx, nota, CX, Y1 - 50, 32, WHITE, "Bold", alpha=ramp(t, s.mark(1) + 1.3, 0.3))
    return draw


SEGMENTS = [
    Seg(["The coldest places in the universe. Number one isn't in space, it's on Earth."], cena(laboratorio, "", "", ""),
        {"title": "5 COLDEST PLACES IN THE UNIVERSE"}, tail=0.2),
    Seg(["Number five, Antarctica.", "Minus eighty nine, the coldest air ever measured."],
        cena(antartida, "−89 °C", "−128 °F · VOSTOK, 1983", "COLDEST AIR ON EARTH"), head(5, "ANTARCTICA"),
        sfx=[(1, 0, "ding")]),
    Seg(["Number four, Pluto.", "Around minus two hundred thirty."],
        cena(plutao, "−230 °C", "−382 °F", "FROZEN NITROGEN PLAINS"), head(4, "PLUTO"), sfx=[(1, 0, "ding")]),
    Seg(["Number three, empty space.", "Just under three degrees above absolute zero."],
        cena(espaco, "−270 °C", "2.7 KELVIN", "THE COSMIC BACKGROUND"), head(3, "EMPTY SPACE"), sfx=[(1, 0, "ding")]),
    Seg(["Number two, the Boomerang Nebula.", "Colder than empty space itself."],
        cena(bumerangue, "−272 °C", "1 KELVIN", "COLDEST NATURAL PLACE"), head(2, "BOOMERANG NEBULA"),
        sfx=[(1, 0, "ding")]),
    Seg(["And number one, a lab in Germany.", "Atoms dropped down a tower hit thirty eight trillionths of a degree."],
        cena(laboratorio, "−273.15 °C", "0.000000000038 K", "COLDEST EVER MEASURED"), head(1, "A LAB ON EARTH"),
        sfx=[(1, 0, "whoosh")], tail=0.7),
]
SEGMENTS.append(pq.seg_pergunta("Which one surprised you the most?", "WHICH ONE SURPRISED YOU?",
                                fundo=lambda ctx, t, s: cena(bumerangue, "", "", "")(ctx, t, s)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
