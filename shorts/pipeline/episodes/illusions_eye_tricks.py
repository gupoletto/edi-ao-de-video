"""5 illusions your own eyes create, ranked (#5 -> #1). Mon 16/11/2026, topic: optical illusions, format: ranking.
Search: "optical illusion" median ~2M (week ranking of 15/11); "this illusion will make you" 37k.

Items (all drawn by code; each is a real, well-documented effect):
- #5 Hermann grid (Ludimar Hermann, 1870): gray smudges appear at the white intersections of a black grid;
- #4 scintillating grid (Lingelbach, 1994): white discs at the intersections, and black dots flash inside them;
- #3 Troxler fading (Ignaz Troxler, 1804): stare at the center and soft blobs in the periphery fade away;
- #2 lilac chaser (Jeremy Hinton, 2005): stare at the cross; the pink dots disappear and a green dot runs around;
- #1 negative afterimage: stare at a cyan heart, then at a white screen, and a red heart appears (tired cone cells).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import AREA, BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, text_center  # noqa: E402

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2 + 20
DOTS = ["5", "4", "3", "2", "1"]


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def fundo(ctx, cor):
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.set_source_rgb(*cor)
    ctx.fill()


def cruz(ctx, cor=(0, 0, 0)):
    ctx.set_source_rgb(*cor)
    ctx.set_line_width(5)
    ctx.move_to(CX - 18, CY)
    ctx.line_to(CX + 18, CY)
    ctx.move_to(CX, CY - 18)
    ctx.line_to(CX, CY + 18)
    ctx.stroke()


def grade(ctx, discos=False):
    fundo(ctx, (0.5, 0.5, 0.5) if discos else (1, 1, 1))   # ruas: cinza (cintilante) ou brancas (Hermann)
    lado, rua = 110, 26
    passo = lado + rua
    ctx.set_source_rgb(0, 0, 0)
    for i in range(-1, 8):
        for j in range(-1, 8):
            ctx.rectangle(X0 + 10 + i * passo, Y0 + 10 + j * passo, lado, lado)
    ctx.fill()
    if discos:
        ctx.set_source_rgb(1, 1, 1)
        for i in range(0, 8):
            for j in range(0, 8):
                ctx.arc(X0 + 10 + i * passo - rua / 2, Y0 + 10 + j * passo - rua / 2, rua * 0.62, 0, 2 * math.pi)
                ctx.fill()


def troxler(ctx, t):
    import cairo
    fundo(ctx, (0.62, 0.62, 0.66))
    cores = [(1.0, 0.5, 0.6), (0.5, 0.8, 1.0), (0.7, 1.0, 0.5), (1.0, 0.9, 0.4), (0.8, 0.6, 1.0), (0.5, 1.0, 0.9)]
    for k, c in enumerate(cores):
        a = k * math.pi / 3
        x, y = CX + 300 * math.cos(a), CY + 300 * math.sin(a)
        g = cairo.RadialGradient(x, y, 0, x, y, 150)
        g.add_color_stop_rgba(0, *c, 0.9)
        g.add_color_stop_rgba(1, *c, 0.0)
        ctx.arc(x, y, 150, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
    cruz(ctx)


def lilas(ctx, t):
    import cairo
    fundo(ctx, (0.74, 0.74, 0.74))
    falta = int(t / 0.1) % 12
    for k in range(12):
        if k == falta:
            continue
        a = k * math.pi / 6
        x, y = CX + 300 * math.cos(a), CY + 300 * math.sin(a)
        g = cairo.RadialGradient(x, y, 0, x, y, 70)
        g.add_color_stop_rgba(0, 0.85, 0.45, 0.85, 1.0)
        g.add_color_stop_rgba(1, 0.85, 0.45, 0.85, 0.0)
        ctx.arc(x, y, 70, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
    cruz(ctx)


def coracao(ctx, cor):
    ctx.save()
    ctx.translate(CX, CY - 30)
    ctx.scale(11, 11)
    ctx.move_to(0, 8)
    ctx.curve_to(-26, -10, -14, -30, 0, -16)
    ctx.curve_to(14, -30, 26, -10, 0, 8)
    ctx.close_path()
    ctx.restore()
    ctx.set_source_rgb(*cor)
    ctx.fill()


def depois(ctx, t, s):
    """Encara o coração ciano (com contagem); depois a tela fica branca."""
    troca = s.mark(2) if len(s.items) > 2 else 99
    if t < troca:
        fundo(ctx, (0.08, 0.08, 0.1))
        coracao(ctx, (0.0, 0.9, 0.9))
        ctx.set_source_rgb(0, 0, 0)
        ctx.arc(CX, CY - 60, 8, 0, 2 * math.pi)
        ctx.fill()
        if len(s.items) > 2:
            text_center(ctx, f"{max(0.0, troca - t):.0f}", CX, Y1 - 40, 60, YELLOW, "ExtraBold")
    else:
        fundo(ctx, (1, 1, 1))
        ctx.set_source_rgb(0, 0, 0)
        ctx.arc(CX, CY - 60, 8, 0, 2 * math.pi)
        ctx.fill()


def cena(desenho):
    def draw(ctx, t, s):
        ctx.save()
        ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
        ctx.clip()
        desenho(ctx, t, s)
        ctx.restore()
    return draw


SEGMENTS = [
    Seg(["These illusions aren't on the screen. Your own eyes make them up."],
        cena(lambda c, t, s: grade(c, True)), {"title": "5 ILLUSIONS YOUR EYES MAKE UP"}, tail=0.2),
    Seg(["Number five, the Hermann grid.", "See gray dots at the crossings? They aren't there."],
        cena(lambda c, t, s: grade(c)), head(5, "HERMANN GRID"), sfx=[(1, 0, "ding")]),
    Seg(["Number four, the scintillating grid.", "Black dots flash, but every dot is white."],
        cena(lambda c, t, s: grade(c, True)), head(4, "SCINTILLATING GRID"), sfx=[(1, 0, "ding")]),
    Seg(["Number three. Stare at the cross.", "The colors slowly fade away."],
        cena(lambda c, t, s: troxler(c, t)), head(3, "TROXLER FADING"), sfx=[(1, 0, "ding")], tail=1.2),
    Seg(["Number two. Keep staring at the cross.", "A green dot appears, but there is no green."],
        cena(lambda c, t, s: lilas(c, t)), head(2, "LILAC CHASER"), sfx=[(1, 0, "ding")], tail=1.2),
    Seg(["And number one. Stare at the black dot. Don't blink.", "Keep staring. Three, two, one.", "Now look at the white. A red heart!"],
        cena(depois), head(1, "AFTERIMAGE"), sfx=[(1, 0, "whoosh")], tail=1.5),
]
SEGMENTS.append(pq.seg_pergunta("Which one got you? Number?", "WHICH ONE GOT YOU?",
                                fundo=lambda ctx, t, s: cena(lambda c, tt, ss: grade(c, True))(ctx, t, s)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
