"""How are LEGO bricks made? (2D animated story). Sun 22/11/2026, storytelling (how it's made).
Search 22/11: "how lego is made" median 2.34M. Brand named only descriptively; no logo is drawn.

Facts (LEGO Group factory, Billund, Denmark):
- bricks are made from ABS plastic that arrives as small granules;
- the granules are heated to about 230 C until they melt;
- the melted plastic is injected into steel molds under very high pressure; it cools and the brick pops out in
  seconds;
- the molds are accurate to a few thousandths of a millimeter, so every brick clicks with every other;
- the stud-and-tube design was patented in 1958, and a 1958 brick still fits a brick made today;
- only about 18 bricks out of every million fail the quality check (LEGO's own figure);
- robots carry the bricks away; the factories make tens of billions of elements a year.
Tone: fun -> alegre music.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

core.MUSICA = "divertido"   # tom -> alegre
VERM = (0.88, 0.16, 0.14)
AZUL = (0.10, 0.40, 0.85)
AMAR = (1.0, 0.80, 0.10)
VERDE = (0.15, 0.65, 0.30)
CORES = [VERM, AZUL, AMAR, VERDE]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def fundo(ctx):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.14, 0.18, 0.30)
    g.add_color_stop_rgb(1, 0.05, 0.06, 0.12)
    ctx.set_source(g)
    ctx.paint()


def caixa(ctx, l1, l2, cor, y=540):
    round_rect(ctx, 150, y - 56, 780, 136, 26)
    ctx.set_source_rgba(0.03, 0.04, 0.08, 0.85)
    ctx.fill()
    text_center(ctx, l1, W / 2, y, 52, cor, "ExtraBold")
    text_center(ctx, l2, W / 2, y + 56, 28, WHITE, "Bold")


def tijolo(ctx, x, y, cor, w=4, s=1.0, alpha=1.0):
    """Tijolo de encaixe genérico visto de lado: w pinos; (x, y) = canto inferior esquerdo."""
    u = 48 * s
    ctx.new_path()
    escuro = tuple(c * 0.75 for c in cor)
    ctx.set_source_rgba(*cor, alpha)
    ctx.rectangle(x, y - 1.15 * u, w * u, 1.15 * u)
    ctx.fill()
    ctx.set_source_rgba(*escuro, alpha)
    ctx.rectangle(x, y - 0.18 * u, w * u, 0.18 * u)
    ctx.fill()
    for i in range(w):   # pinos
        ctx.set_source_rgba(*cor, alpha)
        ctx.rectangle(x + (i + 0.2) * u, y - 1.4 * u, 0.6 * u, 0.27 * u)
        ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.25 * alpha)
        ctx.rectangle(x + (i + 0.25) * u, y - 1.38 * u, 0.12 * u, 0.2 * u)
        ctx.fill()


def d_gancho(ctx, t, s):
    fundo(ctx)
    m1 = s.mark(1) if len(s.items) > 1 else 99
    k = ease((t - m1 + 0.3) / 0.8)
    x0, y0 = 252, 1060
    if k > 0:   # o de hoje entra por baixo e o velho encaixa em cima
        tijolo(ctx, x0, y0 + 30 + 300 * (1 - k), VERM, 4, 3.0, alpha=k)
    tijolo(ctx, x0, y0 + 30 - 166 * k, (0.80, 0.70, 0.50), 4, 3.0)
    text_center(ctx, "1958", W / 2, y0 + 30 - 166 * k - 230, 54, (0.95, 0.85, 0.6), "ExtraBold")
    if k > 0.9:
        text_center(ctx, "TODAY", W / 2, y0 - 20, 40, WHITE, "ExtraBold")


def d_graos(ctx, t, s):
    fundo(ctx)
    for i in range(240):   # grãos caindo num funil
        x = 300 + (i * 53) % 480
        y = 640 + ((t * 220 + i * 37) % 520)
        x = 540 + (x - 540) * max(0.15, 1 - (y - 640) / 600)
        ctx.set_source_rgb(*CORES[i % 4])
        ctx.arc(x, y, 7, 0, 2 * math.pi)
        ctx.fill()
    caixa(ctx, "PLASTIC GRANULES", "THIS IS WHERE EVERY BRICK STARTS", AMAR)


def d_derrete(ctx, t, s):
    fundo(ctx)
    k = ease(t / 3.0)
    ctx.set_source_rgb(0.5, 0.52, 0.56)   # cilindro aquecido com rosca
    round_rect(ctx, 120, 860, 840, 160, 30)
    ctx.fill()
    for i in range(10):
        ctx.set_source_rgba(1.0, 0.45, 0.1, 0.3 + 0.5 * k)   # aquecedores
        ctx.rectangle(150 + i * 82, 840, 60, 20)
        ctx.rectangle(150 + i * 82, 1020, 60, 20)
        ctx.fill()
    for i in range(16):   # rosca girando
        x = 150 + ((i * 52 + t * 120) % 780)
        ctx.set_source_rgb(0.35, 0.36, 0.40)
        ctx.move_to(x, 880)
        ctx.line_to(x + 30, 1000)
        ctx.set_line_width(10)
        ctx.stroke()
    ctx.set_source_rgba(*VERM, 0.85)
    ctx.rectangle(150 + 780 * (1 - k), 900, 780 * k, 80)
    ctx.fill()
    temp = int(230 * k)
    caixa(ctx, f"{temp} °C", "MELTED LIKE THICK HONEY", (1.0, 0.55, 0.2))


def d_molde(ctx, t, s):
    fundo(ctx)
    fecha = ease(t / 0.8) * (1 - ease((t - 2.6) / 0.6))
    enche = ease((t - 0.9) / 1.2)
    sai = ease((t - 3.2) / 0.8)
    # metades do molde de aço
    for lado in (-1, 1):
        x = 540 + lado * (60 + 200 * (1 - fecha))
        ctx.set_source_rgb(0.62, 0.64, 0.68)
        ctx.rectangle(x - 160 if lado < 0 else x, 760, 160, 420)
        ctx.fill()
    if enche > 0 and fecha > 0.5:
        ctx.set_source_rgb(*VERM)
        ctx.rectangle(440, 1060 - 200 * enche, 200, 200 * enche)
        ctx.fill()
    if sai > 0:
        tijolo(ctx, 348, 1080 - 60 * sai, VERM, 4, 2.0)
    p = int(enche * 100)
    caixa(ctx, "INJECTED INTO STEEL", f"UNDER HUGE PRESSURE · {p}%", (0.8, 0.85, 0.92))


def d_precisao(ctx, t, s):
    fundo(ctx)
    k = ease(t / 2.5)
    for i in range(3):   # pilha encaixando
        tijolo(ctx, 340, 1150 - i * 110 * k, CORES[i], 4, 2.0)
    ctx.set_source_rgba(1, 1, 1, 0.8)   # lupa com régua
    ctx.set_line_width(6)
    ctx.arc(820, 820, 90, 0, 2 * math.pi)
    ctx.stroke()
    ctx.move_to(885, 885)
    ctx.line_to(950, 950)
    ctx.stroke()
    text_center(ctx, "0.005", 820, 830, 34, AMAR, "ExtraBold")
    text_center(ctx, "MM", 820, 860, 22, WHITE, "Bold")
    caixa(ctx, "THOUSANDTHS OF A MM", "THAT'S WHY EVERY BRICK CLICKS", GREEN)


def d_controle(ctx, t, s):
    fundo(ctx)
    for i in range(8):   # esteira cheia de tijolos
        x = -200 + ((t * 180 + i * 190) % 1520)
        cor = CORES[i % 4]
        ruim = i == 5
        tijolo(ctx, x, 1100, cor, 2, 1.5, alpha=0.5 if ruim else 1.0)
        if ruim:
            ctx.set_source_rgb(1, 0.2, 0.2)
            ctx.set_line_width(6)
            ctx.move_to(x + 10, 1100 - 90)
            ctx.line_to(x + 134, 1100 - 10)
            ctx.move_to(x + 134, 1100 - 90)
            ctx.line_to(x + 10, 1100 - 10)
            ctx.stroke()
    ctx.set_source_rgb(0.25, 0.25, 0.3)
    ctx.rectangle(0, 1100, W, 30)
    ctx.fill()
    caixa(ctx, "18 IN A MILLION", "THAT'S HOW FEW FAIL THE CHECK", PINK)


SEGMENTS = [
    Seg(["A plastic brick from 1958", "still clicks perfectly into one made today."], d_gancho,
        {"title": "HOW ARE LEGO BRICKS MADE?"}, tail=0.2),
    Seg(["Every brick starts as tiny plastic granules, poured in by the ton."], d_graos,
        {"big": "GRANULES", "color": AMAR}, tail=0.2),
    Seg(["A giant screw pushes them through a tube heated to two hundred thirty degrees, until they melt."],
        d_derrete, {"big": "MELT", "color": (1.0, 0.55, 0.2)}, tail=0.2),
    Seg(["The hot plastic is blasted into a steel mold. It cools, the mold opens, and a brick pops out in seconds."],
        d_molde, {"big": "MOLD", "color": (0.8, 0.85, 0.92)}, tail=0.2),
    Seg(["The molds are accurate to a few thousandths of a millimeter. That's why every brick clicks with every other one."],
        d_precisao, {"big": "PRECISION", "color": GREEN}, tail=0.2),
    Seg(["And they're so precise that only about eighteen bricks in a million get rejected."], d_controle,
        {"big": "QUALITY", "color": PINK}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("What's the coolest thing you ever built?", "WHAT DID YOU BUILD?",
                                fundo=lambda ctx, t, s: fundo(ctx)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
