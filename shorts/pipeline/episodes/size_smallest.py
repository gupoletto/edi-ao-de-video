"""How small can things get? 5 tiny things to scale (#5 -> #1). Fri 13/11/2026, topic: size and scale, format:
ranking. Search 13/11: "size comparison universe", median 442k (top 19.5M: "Are humans closer to the biggest or
smallest thing?"; "How small is the Planck length?" 6.9M).

Sizes (typical): human hair ~70 micrometers wide; red blood cell ~7.5 um; influenza virus ~100 nm; hydrogen atom
~0.1 nm; Planck length 1.6e-35 m.
Comparison for #1: blow an atom up to the size of the observable universe (~8.8e26 m, a factor of ~8.8e36) and a
Planck length becomes about 140 m, the height of a skyscraper.
The animation zooms in between items on a log scale; each item is drawn at true size relative to the previous one.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import AREA, BLUE, PINK, WHITE, YELLOW, Seg, ramp, render, text_center  # noqa: E402

X0, Y0, X1, Y1 = AREA
CX, CY = (X0 + X1) / 2, (Y0 + Y1) / 2 + 50
RAIO_TELA = 270
DOTS = ["5", "4", "3", "2", "1"]
COISAS = {  # tamanho (m), rótulo
    "grao": (1e-3, "1 mm"),
    "cabelo": (7e-5, "0.07 mm"),
    "hemacia": (7.5e-6, "0.0075 mm"),
    "virus": (1e-7, "100 nanometers"),
    "atomo": (1e-10, "0.1 nanometers"),
    "planck": (1.6e-35, "0.000…016 m (34 zeros)"),
}
ORDEM = ["grao", "cabelo", "hemacia", "virus", "atomo", "planck"]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def fundo(ctx):
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.set_source_rgb(0.05, 0.06, 0.10)
    ctx.fill()


def desenha(ctx, nome, x, y, r, t):
    """Cada coisa ocupa um círculo de raio r (px)."""
    import cairo
    if r < 1.0:
        ctx.set_source_rgb(1, 1, 1)
        ctx.arc(x, y, 1.5, 0, 2 * math.pi)
        ctx.fill()
        return
    if nome == "grao":  # grão de areia
        ctx.set_source_rgb(0.85, 0.72, 0.48)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.fill()
    elif nome == "cabelo":  # fio de cabelo: faixa marrom com escamas
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(-0.5)
        ctx.rectangle(-r * 6, -r, r * 12, 2 * r)
        ctx.set_source_rgb(0.42, 0.27, 0.16)
        ctx.fill()
        ctx.set_source_rgba(0, 0, 0, 0.25)
        ctx.set_line_width(max(1.0, r * 0.05))
        for k in range(-6, 7):
            ctx.move_to(k * r * 0.9, -r)
            ctx.curve_to(k * r * 0.9 + r * 0.4, -r * 0.3, k * r * 0.9 + r * 0.4, r * 0.3, k * r * 0.9, r)
        ctx.stroke()
        ctx.restore()
    elif nome == "hemacia":  # disco bicôncavo
        g = cairo.RadialGradient(x, y, r * 0.2, x, y, r)
        g.add_color_stop_rgb(0, 0.65, 0.08, 0.10)
        g.add_color_stop_rgb(0.55, 0.85, 0.15, 0.15)
        g.add_color_stop_rgb(1, 0.6, 0.05, 0.08)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
    elif nome == "virus":  # esfera com espículas
        ctx.set_source_rgb(0.45, 0.75, 0.45)
        for k in range(18):
            a = k * math.pi * 2 / 18 + t * 0.3
            ctx.move_to(x + math.cos(a) * r * 0.8, y + math.sin(a) * r * 0.8)
            ctx.line_to(x + math.cos(a) * r, y + math.sin(a) * r)
            ctx.set_line_width(max(1.0, r * 0.06))
            ctx.stroke()
            ctx.arc(x + math.cos(a) * r, y + math.sin(a) * r, r * 0.07, 0, 2 * math.pi)
            ctx.fill()
        ctx.arc(x, y, r * 0.8, 0, 2 * math.pi)
        ctx.set_source_rgb(0.30, 0.62, 0.38)
        ctx.fill()
    elif nome == "atomo":  # nuvem de elétron e núcleo
        g = cairo.RadialGradient(x, y, 0, x, y, r)
        g.add_color_stop_rgba(0, 0.4, 0.7, 1.0, 0.9)
        g.add_color_stop_rgba(1, 0.4, 0.7, 1.0, 0.0)
        ctx.arc(x, y, r, 0, 2 * math.pi)
        ctx.set_source(g)
        ctx.fill()
        ctx.set_source_rgb(1, 0.6, 0.3)
        ctx.arc(x, y, max(1.5, r * 0.03), 0, 2 * math.pi)
        ctx.fill()
        a = t * 3
        ctx.set_source_rgb(1, 1, 1)
        ctx.arc(x + r * 0.6 * math.cos(a), y + r * 0.6 * math.sin(a), max(2.0, r * 0.04), 0, 2 * math.pi)
        ctx.fill()
    else:  # espuma quântica: grade que tremula
        ctx.set_line_width(2)
        for i in range(-6, 7):
            for j in range(-6, 7):
                px, py = x + i * r / 6, y + j * r / 6
                if (px - x) ** 2 + (py - y) ** 2 > r * r:
                    continue
                f = 0.5 + 0.5 * math.sin(t * 7 + i * 1.7 + j * 2.3)
                ctx.set_source_rgba(0.8, 0.5, 1.0, 0.3 + 0.7 * f)
                ctx.arc(px, py, 3 + 6 * f, 0, 2 * math.pi)
                ctx.fill()


def cena(nome, nota):
    i = ORDEM.index(nome)
    ant = ORDEM[i - 1]
    s_novo, s_ant = COISAS[nome][0], COISAS[ant][0]

    def draw(ctx, t, s):
        ctx.save()
        ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
        ctx.clip()
        fundo(ctx)
        z = ease((t - 0.2) / 1.4)
        lz = math.log10(s_ant) + (math.log10(s_novo) - math.log10(s_ant)) * z   # zoom em escala log
        escala = RAIO_TELA / (10 ** lz)      # px por metro (raio)
        ra, rn = s_ant * escala, s_novo * escala
        if ra < 20000:
            desenha(ctx, ant, CX, CY + ra - RAIO_TELA * 0.2 if ra > RAIO_TELA else CY, ra, t)
        desenha(ctx, nome, CX, CY, rn, t)
        text_center(ctx, COISAS[nome][1], CX, Y0 + 70, 48, YELLOW, "ExtraBold", alpha=ramp(t, 1.4, 0.3))
        text_center(ctx, nota, CX, Y1 - 40, 30, WHITE, "Bold", alpha=ramp(t, 1.8, 0.3))
        ctx.restore()
    return draw


def d_intro(ctx, t, s):
    ctx.save()
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.clip()
    fundo(ctx)
    lz = -3 - 7 * ease(t / 3.2)
    escala = RAIO_TELA / (10 ** lz)
    for nome in ORDEM[:5]:
        r = COISAS[nome][0] * escala
        if 0.5 < r < 4000:
            desenha(ctx, nome, CX, CY, r, t)
    ctx.restore()


SEGMENTS = [
    Seg(["How small can things get? Let's zoom in until physics breaks."], d_intro,
        {"title": "HOW SMALL CAN THINGS GET?"}, tail=0.2),
    Seg(["Number five, a human hair.", "About seventy thousandths of a millimeter wide."],
        cena("cabelo", "YOU CAN STILL SEE IT"), head(5, "A HUMAN HAIR"), sfx=[(1, 0, "ding")]),
    Seg(["Number four, a red blood cell.", "Ten of them fit across one hair."],
        cena("hemacia", "~10 ACROSS A HAIR"), head(4, "RED BLOOD CELL"), sfx=[(1, 0, "ding")]),
    Seg(["Number three, a virus.", "Seventy five of them across one blood cell."],
        cena("virus", "INVISIBLE TO LIGHT MICROSCOPES"), head(3, "A VIRUS"), sfx=[(1, 0, "ding")]),
    Seg(["Number two, an atom.", "A thousand times smaller than a virus, and it's mostly empty space."],
        cena("atomo", "MOSTLY EMPTY SPACE"), head(2, "AN ATOM"), sfx=[(1, 0, "ding")]),
    Seg(["And number one, the Planck length.",
         "Blow an atom up to the size of the universe, and this would be as tall as a skyscraper."],
        cena("planck", "THE SMALLEST LENGTH IN PHYSICS"), head(1, "PLANCK LENGTH"), sfx=[(1, 0, "whoosh")], tail=0.7),
]
SEGMENTS.append(pq.seg_pergunta("Did number one break your brain?", "DID #1 BREAK YOUR BRAIN?",
                                fundo=lambda ctx, t, s: d_intro(ctx, 9.0, s)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
