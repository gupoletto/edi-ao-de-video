"""5 most satisfying patterns in nature, ranked (#5 -> #1). Sat 14/11/2026, topic: satisfying, format: ranking.
Search 14/11: satisfying searches ("domino satisfying" 2.28M, "marble run satisfying" 658k); nature patterns drawn by
code, growing on screen.

Facts:
- #5 snowflakes have six-fold symmetry because water molecules lock into a hexagonal ice lattice;
- #4 honeycomb: hexagons divide a surface into equal cells with the least total wall length (Thomas Hales proved the
  "honeycomb conjecture" in 1999), so bees use the least wax;
- #3 basalt columns (Giant's Causeway, Northern Ireland): thick lava cools and contracts, cracking into mostly
  six-sided columns (about 40,000 of them there);
- #2 Romanesco broccoli: a fractal, each bud is a smaller copy of the whole, arranged in spirals;
- #1 sunflower: each new seed grows at the golden angle (~137.5 degrees) from the last, which packs them with no gaps
  and makes spiral counts that are Fibonacci numbers (commonly 34 and 55).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import AREA, BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, text_center  # noqa: E402

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2 + 30
DOTS = ["5", "4", "3", "2", "1"]
OURO = math.radians(137.508)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def painel(ctx, cor=(0.06, 0.08, 0.12)):
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.set_source_rgb(*cor)
    ctx.fill()


def floco(ctx, t, s):
    k = ease(t / 2.0)
    ctx.save()
    ctx.translate(CX, CY)
    ctx.rotate(t * 0.15)
    ctx.set_source_rgb(0.85, 0.94, 1.0)
    ctx.set_line_cap(1)
    for b in range(6):
        ctx.save()
        ctx.rotate(b * math.pi / 3)
        L = 300 * k
        ctx.set_line_width(14)
        ctx.move_to(0, 0)
        ctx.line_to(0, -L)
        ctx.stroke()
        for j, f in enumerate((0.35, 0.55, 0.75)):
            ramo = 110 * (1 - f * 0.6) * ease((k - f * 0.6) / 0.4)
            for lado in (-1, 1):
                ctx.set_line_width(9 - j * 2)
                ctx.move_to(0, -L * f)
                ctx.line_to(lado * ramo * 0.7, -L * f - ramo * 0.7)
                ctx.stroke()
        ctx.restore()
    ctx.restore()


def favo(ctx, t, s):
    painel(ctx, (0.18, 0.12, 0.04))
    r = 58
    n = 0
    for j in range(-6, 7):
        for i in range(-5, 6):
            x = CX + i * r * 1.5
            y = CY + j * r * math.sqrt(3) + (i % 2) * r * math.sqrt(3) / 2
            d = math.hypot(x - CX, y - CY)
            k = ease((t * 260 - d) / 120)
            if k <= 0 or not (X0 < x < X1 and Y0 < y < Y1):
                continue
            ctx.new_path()
            for a in range(6):
                ang = a * math.pi / 3
                ctx.line_to(x + r * 0.92 * k * math.cos(ang), y + r * 0.92 * k * math.sin(ang))
            ctx.close_path()
            ctx.set_source_rgb(0.98, 0.72 - 0.1 * (n % 3) * 0.3, 0.12)
            ctx.fill_preserve()
            ctx.set_source_rgb(0.55, 0.33, 0.05)
            ctx.set_line_width(5)
            ctx.stroke()
            n += 1


def basalto(ctx, t, s):
    """Vista de cima das colunas: polígonos irregulares (quase hexágonos), cada um numa altura de cinza."""
    painel(ctx, (0.10, 0.10, 0.11))
    r = 70
    for j in range(-6, 7):
        for i in range(-5, 6):
            x0 = CX + i * r * 1.5
            y0 = CY + j * r * math.sqrt(3) + (i % 2) * r * math.sqrt(3) / 2
            sem = (i * 7 + j * 13) % 11
            d = math.hypot(x0 - CX, y0 - CY)
            k = ease((t * 300 - d) / 150)
            if k <= 0:
                continue
            ctx.new_path()
            for a in range(6):
                ang = a * math.pi / 3 + 0.1 * math.sin(sem + a)
                rr = r * (0.88 + 0.08 * math.sin(sem * 3 + a * 2))
                ctx.line_to(x0 + rr * math.cos(ang), y0 + rr * math.sin(ang))
            ctx.close_path()
            g = 0.25 + 0.04 * (sem % 5)
            ctx.set_source_rgba(g, g, g + 0.02, k)
            ctx.fill()


def romanesco(ctx, t, s):
    painel(ctx, (0.05, 0.09, 0.05))
    k = ease(t / 2.5)

    def broto(x, y, r, n):
        if r < 5 or n > 3:
            ctx.arc(x, y, max(r, 2), 0, 2 * math.pi)
            ctx.set_source_rgb(0.55 + 0.1 * n, 0.85, 0.35)
            ctx.fill()
            return
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source_rgb(0.40 + 0.08 * n, 0.70, 0.25)
        ctx.fill()
        m = int(14 * k) + 4
        for i in range(m):
            a = i * OURO
            d = r * 0.75 * math.sqrt((i + 0.5) / m)
            broto(x + d * math.cos(a), y + d * math.sin(a), r * 0.22, n + 1)
    broto(CX, CY, 300, 0)


def girassol(ctx, t, s):
    painel(ctx, (0.08, 0.10, 0.06))
    n = int(900 * ease(t / 3.5))
    c = 11.0
    ctx.arc(CX, CY, 360, 0, 2 * math.pi)
    ctx.set_source_rgb(0.98, 0.78, 0.1)
    ctx.fill()
    for i in range(n):
        a = i * OURO
        d = c * math.sqrt(i)
        if d > 330:
            break
        ctx.arc(CX + d * math.cos(a), CY + d * math.sin(a), 6.0, 0, 2 * math.pi)
        ctx.set_source_rgb(0.30 + 0.25 * (i % 34 == 0), 0.18, 0.06)
        ctx.fill()
    if len(s.items) > 1 and t > s.mark(1):
        text_center(ctx, "137.5° · THE GOLDEN ANGLE", CX, Y1 - 40, 46, YELLOW, "ExtraBold", alpha=ramp(t, s.mark(1), 0.3))


def cena(fig, fundo=(0.06, 0.08, 0.12)):
    def draw(ctx, t, s):
        ctx.save()
        ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
        ctx.clip()
        painel(ctx, fundo)
        fig(ctx, t, s)
        ctx.restore()
    return draw


SEGMENTS = [
    Seg(["Nature's most satisfying patterns. Number one hides a secret angle."], cena(girassol),
        {"title": "5 SATISFYING PATTERNS IN NATURE"}, tail=0.2),
    Seg(["Number five, the snowflake.", "Six arms, every time, because ice locks into hexagons."],
        cena(floco, (0.04, 0.10, 0.20)), head(5, "SNOWFLAKE"), sfx=[(1, 0, "ding")]),
    Seg(["Number four, the honeycomb.", "Hexagons hold the most honey with the least wax."],
        cena(favo), head(4, "HONEYCOMB"), sfx=[(1, 0, "ding")]),
    Seg(["Number three, basalt columns.", "Cooling lava cracked into forty thousand columns, mostly six sided."],
        cena(basalto), head(3, "GIANT'S CAUSEWAY"), sfx=[(1, 0, "ding")]),
    Seg(["Number two, Romanesco broccoli.", "Every bud is a tiny copy of the whole thing."],
        cena(romanesco), head(2, "ROMANESCO"), sfx=[(1, 0, "ding")]),
    Seg(["And number one, the sunflower.", "Every new seed turns one hundred thirty seven degrees. No gaps."],
        cena(girassol), head(1, "SUNFLOWER"), sfx=[(1, 0, "whoosh")], tail=0.8),
]
SEGMENTS.append(pq.seg_pergunta("Which pattern is the most satisfying?", "WHICH ONE IS #1 FOR YOU?",
                                fundo=lambda ctx, t, s: cena(girassol)(ctx, 9.0, s)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
