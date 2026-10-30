"""Ranking the tallest buildings ever built, to scale (#5 -> #1). Sat 31/10/2026, topic: size comparison,
format: ranking.

Heights to the architectural top (CTBUH): Ping An Finance Center (Shenzhen) 599 m, 115 floors; Abraj Al-Bait Clock
Tower (Mecca) 601 m, clock faces 43 m wide; Shanghai Tower 632 m, twists about 120 degrees; Merdeka 118 (Kuala Lumpur)
679 m, completed 2023, 118 floors; Burj Khalifa (Dubai) 828 m, 163 floors. Eiffel Tower 330 m for scale.
Silhouettes are stylised, drawn by code at true relative height.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import AREA, BLUE, GRAY, PINK, WHITE, YELLOW, Seg, ramp, render, text_center  # noqa: E402

X0, Y0, X1, Y1 = AREA
CHAO = Y1 - 150
PX_M = 760 / 828  # px por metro: o Burj Khalifa ocupa a altura útil
DOTS = ["5", "4", "3", "2", "1"]
AZUL_NOITE = (0.06, 0.09, 0.17)


def head(rank, name):
    return {"big": f"#{rank}", "sub": name, "dots": (DOTS, 5 - rank), "color": PINK if rank == 1 else BLUE}


def cenario(ctx):
    ctx.rectangle(X0, Y0, X1 - X0, Y1 - Y0)
    ctx.set_source_rgb(*AZUL_NOITE)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.06)  # marcas de 100 m
    for m in range(100, 900, 100):
        y = CHAO - m * PX_M
        ctx.rectangle(X0, y, X1 - X0, 2)
        ctx.fill()
        text_center(ctx, f"{m} m", X0 + 50, y - 6, 20, GRAY, "SemiBold")
    ctx.set_source_rgb(0.18, 0.2, 0.26)
    ctx.rectangle(X0, CHAO, X1 - X0, Y1 - CHAO)
    ctx.fill()


def eiffel(ctx, x, k=1.0):
    h = 330 * PX_M * k
    w = h * 0.38
    ctx.move_to(x - w / 2, CHAO)
    ctx.curve_to(x - w * 0.2, CHAO - h * 0.35, x - w * 0.05, CHAO - h * 0.7, x, CHAO - h)
    ctx.curve_to(x + w * 0.05, CHAO - h * 0.7, x + w * 0.2, CHAO - h * 0.35, x + w / 2, CHAO)
    ctx.line_to(x + w * 0.22, CHAO)
    ctx.curve_to(x + w * 0.1, CHAO - h * 0.15, x - w * 0.1, CHAO - h * 0.15, x - w * 0.22, CHAO)
    ctx.close_path()
    ctx.set_source_rgb(0.55, 0.45, 0.35)
    ctx.fill()
    text_center(ctx, "EIFFEL 330 m", x, CHAO + 50, 26, GRAY, "SemiBold")


def predio(ctx, x, altura, forma, cor, k):
    """Silhueta estilizada que cresce do chão (k = 0..1)."""
    h = altura * PX_M * k
    if h <= 1:
        return
    topo = CHAO - h
    ctx.new_path()
    if forma == "burj":  # degraus afinando + agulha
        for i, (fw, fh) in enumerate(((1.0, 0.25), (0.78, 0.45), (0.58, 0.62), (0.4, 0.76), (0.24, 0.86))):
            w = 120 * fw
            y_base = CHAO - h * (0 if i == 0 else (0.25, 0.45, 0.62, 0.76, 0.86)[i - 1])
            ctx.rectangle(x - w / 2, CHAO - h * fh, w, y_base - (CHAO - h * fh))
        ctx.move_to(x - 7, CHAO - h * 0.86)
        ctx.line_to(x, topo)
        ctx.line_to(x + 7, CHAO - h * 0.86)
    elif forma == "merdeka":  # facetas e agulha longa
        ctx.move_to(x - 55, CHAO)
        ctx.line_to(x - 40, CHAO - h * 0.72)
        ctx.line_to(x - 10, CHAO - h * 0.8)
        ctx.line_to(x - 3, topo)
        ctx.line_to(x + 3, topo)
        ctx.line_to(x + 10, CHAO - h * 0.8)
        ctx.line_to(x + 40, CHAO - h * 0.72)
        ctx.line_to(x + 55, CHAO)
    elif forma == "xangai":  # afunila em curva (a torção)
        ctx.move_to(x - 60, CHAO)
        ctx.curve_to(x - 58, CHAO - h * 0.5, x - 30, CHAO - h * 0.85, x - 18, topo)
        ctx.line_to(x + 26, topo + 8)
        ctx.curve_to(x + 40, CHAO - h * 0.8, x + 62, CHAO - h * 0.45, x + 60, CHAO)
    elif forma == "relogio":  # bloco, torre do relógio e agulha
        ctx.rectangle(x - 70, CHAO - h * 0.45, 140, h * 0.45)
        ctx.rectangle(x - 34, CHAO - h * 0.86, 68, h * 0.41)
        ctx.move_to(x - 14, CHAO - h * 0.86)
        ctx.line_to(x, topo)
        ctx.line_to(x + 14, CHAO - h * 0.86)
    else:  # pingan: obelisco
        ctx.move_to(x - 55, CHAO)
        ctx.line_to(x - 45, CHAO - h * 0.9)
        ctx.line_to(x, topo)
        ctx.line_to(x + 45, CHAO - h * 0.9)
        ctx.line_to(x + 55, CHAO)
    ctx.close_path()
    ctx.set_source_rgb(*cor)
    ctx.fill()
    if forma == "relogio" and k > 0.9:
        cy = CHAO - h * 0.78
        ctx.arc(x, cy, 22, 0, 6.3)
        ctx.set_source_rgb(1, 0.95, 0.75)
        ctx.fill()


def contador(ctx, t, s, alvo, cor):
    k = ramp(t, s.mark(1), 1.4)
    text_center(ctx, f"{int(alvo * k)} m", X1 - 190, Y0 + 110, 76, cor, "ExtraBold", alpha=ramp(t, s.mark(1), 0.3))


def cena(forma, altura, cor, nota):
    def draw(ctx, t, s):
        cenario(ctx)
        eiffel(ctx, X0 + 190)
        predio(ctx, X0 + 600, altura, forma, cor, ramp(t, s.mark(1), 1.4))
        contador(ctx, t, s, altura, cor)
        text_center(ctx, nota, (X0 + X1) / 2, Y1 - 60, 36, WHITE, "Bold", alpha=ramp(t, s.mark(1) + 1.6, 0.3))
    return draw


def d_intro(ctx, t, s):
    cenario(ctx)
    for i, (f, alt, cor) in enumerate((("pingan", 599, (0.55, 0.6, 0.7)), ("relogio", 601, (0.7, 0.62, 0.5)),
                                      ("xangai", 632, (0.45, 0.65, 0.8)), ("merdeka", 679, (0.6, 0.7, 0.75)),
                                      ("burj", 828, YELLOW))):
        predio(ctx, X0 + 120 + i * 180, alt, f, cor, ramp(t, 0.2 + i * 0.25, 0.8))


SEGMENTS = [
    Seg(["The five tallest buildings ever built, shown to scale next to the Eiffel Tower."], d_intro,
        {"title": "THE TALLEST BUILDINGS, TO SCALE"}, tail=0.3),
    Seg(["Number five, Ping An Finance Center in Shenzhen.", "Five hundred ninety nine meters, with one hundred fifteen floors."],
        cena("pingan", 599, (0.55, 0.6, 0.7), "115 FLOORS"), head(5, "PING AN FINANCE CENTER"), sfx=[(1, 1.4, "ding")]),
    Seg(["Number four, the Abraj Al Bait Clock Tower.", "Six hundred one meters, with clock faces forty three meters wide."],
        cena("relogio", 601, (0.7, 0.62, 0.5), "CLOCK FACES 43 m WIDE"), head(4, "ABRAJ AL-BAIT CLOCK TOWER"),
        sfx=[(1, 1.4, "ding")]),
    Seg(["Number three, Shanghai Tower.", "Six hundred thirty two meters, and the whole building twists as it rises."],
        cena("xangai", 632, (0.45, 0.65, 0.8), "IT TWISTS ~120°"), head(3, "SHANGHAI TOWER"), sfx=[(1, 1.4, "ding")]),
    Seg(["Number two, Merdeka one one eight in Kuala Lumpur.", "Six hundred seventy nine meters, finished in twenty twenty three."],
        cena("merdeka", 679, (0.6, 0.7, 0.75), "FINISHED IN 2023"), head(2, "MERDEKA 118"), sfx=[(1, 1.4, "ding")]),
    Seg(["And number one, the Burj Khalifa.", "Eight hundred twenty eight meters. That's two and a half Eiffel Towers!"],
        cena("burj", 828, YELLOW, "2.5x THE EIFFEL TOWER"), head(1, "BURJ KHALIFA"), sfx=[(1, 1.4, "ding")], tail=0.8),
    Seg(["Which one would you climb? Tell me in the comments."], d_intro, {"title": "WHICH ONE WOULD YOU CLIMB?"},
        tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
