"""How are marbles made? (2D animated story). Mon 23/11/2026, storytelling (how it's made).
Search 23/11: "how marbles are made" median 48.6k; "how coca cola is made" 2.12M; "how pencils are made" 268k.
Lesson from 22/11: LEGO (familiar object, fun tone) got 872 views in < 1 day while the slow-opening stories were
watched only 15-21%: hook with motion from frame 0 and a shocking fact; boxes pop in with a spring.

Facts:
- marbles are glass, often from recycled glass, melted in a furnace at over 1,000 C;
- colored glass is injected into the stream to make the swirl inside;
- a shear snips the glowing stream into small blobs ("gobs");
- each gob drops onto two spinning steel rollers with spiral grooves; the rollers turn it as it travels, so it rolls
  itself into a near-perfect sphere while it cools;
- they are cooled slowly and sorted by size; the marble-making machine was invented around 1905 by Martin Christensen
  in Akron, Ohio.
Tone: fun -> alegre.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, pop_caixa, render, round_rect, text_center  # noqa: E402

core.MUSICA = "divertido"   # tom -> alegre
LARANJA = (1.0, 0.55, 0.15)
CORES = [(0.15, 0.45, 0.95), (0.95, 0.25, 0.25), (0.20, 0.75, 0.35), (1.0, 0.80, 0.15), (0.65, 0.30, 0.90)]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def fundo(ctx):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.10, 0.14, 0.26)
    g.add_color_stop_rgb(1, 0.03, 0.04, 0.10)
    ctx.set_source(g)
    ctx.paint()


def caixa(ctx, t, l1, l2, cor, y=540):
    def d():
        round_rect(ctx, 150, y - 56, 780, 136, 26)
        ctx.set_source_rgba(0.03, 0.04, 0.08, 0.88)
        ctx.fill()
        text_center(ctx, l1, W / 2, y, 52, cor, "ExtraBold")
        text_center(ctx, l2, W / 2, y + 56, 28, WHITE, "Bold")
    pop_caixa(ctx, t, W / 2, y + 10, d)


def gude(ctx, x, y, r, cor, rot=0.0, brilho=1.0, alpha=1.0):
    """Bolinha de vidro com redemoinho colorido e reflexo."""
    import cairo
    ctx.new_path()
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.35, r * 0.1, x, y, r)
    g.add_color_stop_rgba(0, 0.95, 0.98, 1.0, 0.95 * alpha)
    g.add_color_stop_rgba(1, 0.55, 0.70, 0.80, 0.55 * alpha)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.save()   # redemoinho (a "fita" de cor dentro)
    ctx.arc(x, y, r * 0.92, 0, 2 * math.pi)
    ctx.clip()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.set_source_rgba(*cor, 0.9 * alpha)
    ctx.set_line_width(r * 0.28)
    ctx.move_to(-r, -r * 0.2)
    ctx.curve_to(-r * 0.3, -r * 0.9, r * 0.3, r * 0.9, r, r * 0.2)
    ctx.stroke()
    ctx.restore()
    ctx.set_source_rgba(1, 1, 1, 0.7 * brilho * alpha)   # reflexo
    ctx.arc(x - r * 0.38, y - r * 0.4, r * 0.18, 0, 2 * math.pi)
    ctx.fill()


def d_gancho(ctx, t, s):
    fundo(ctx)
    for i in range(18):   # chuva de bolinhas quicando desde o 1º quadro
        x = 120 + (i * 151) % 840
        fase = (t * 1.6 + i * 0.37) % 1.0
        y = 1180 - 560 * abs(math.sin(math.pi * fase)) * (0.6 + 0.4 * ((i * 7) % 5) / 4)
        gude(ctx, x, y, 44 + (i % 3) * 8, CORES[i % 5], rot=t * 3 + i)
    if len(s.items) > 1 and t > s.mark(1):
        caixa(ctx, t - s.mark(1), "NOBODY TOUCHES THEM", "A MACHINE ROLLS THEM ROUND", YELLOW)


def d_forno(ctx, t, s):
    fundo(ctx)
    k = ease(t / 2.5)
    ctx.set_source_rgb(0.30, 0.22, 0.20)
    round_rect(ctx, 190, 740, 700, 420, 40)
    ctx.fill()
    ctx.set_source_rgb(*[a + (b - a) * k for a, b in zip((0.25, 0.12, 0.06), LARANJA)])
    round_rect(ctx, 240, 800, 600, 300, 26)
    ctx.fill()
    for i in range(16):   # cacos de vidro reciclado derretendo
        x = 280 + (i * 61) % 520
        y = 830 + (i * 37) % 220 + 40 * k
        ctx.set_source_rgba(0.6, 0.85, 0.75, 1 - k)
        ctx.move_to(x, y)
        ctx.line_to(x + 30, y + 10)
        ctx.line_to(x + 10, y + 34)
        ctx.close_path()
        ctx.fill()
    caixa(ctx, t, f"{int(1000 + 300 * k):,} °C", "RECYCLED GLASS, MELTED", LARANJA)


def fio(ctx, t, x, y0, y1, cor):
    """Fio de vidro incandescente descendo com a fita de cor torcida."""
    ctx.set_source_rgb(*LARANJA)
    ctx.rectangle(x - 22, y0, 44, y1 - y0)
    ctx.fill()
    for j in range(int((y1 - y0) / 30)):   # a cor girando dentro
        y = y0 + j * 30 + (t * 120) % 30
        ctx.set_source_rgba(*cor, 0.9)
        ctx.move_to(x - 18, y)
        ctx.line_to(x + 18, y + 14)
        ctx.set_line_width(7)
        ctx.stroke()


def d_cor(ctx, t, s):
    fundo(ctx)
    fio(ctx, t, W / 2, 640, 1180, CORES[0])
    k = ease((t - 0.8) / 1.0)
    for lado, cor in ((-1, CORES[1]), (1, CORES[2])):   # bicos injetando cor
        ctx.set_source_rgb(0.55, 0.57, 0.62)
        ctx.rectangle(W / 2 + lado * 200 - 40, 800, 80, 60)
        ctx.fill()
        ctx.set_source_rgba(*cor, k)
        ctx.set_line_width(14)
        ctx.move_to(W / 2 + lado * 160, 830)
        ctx.line_to(W / 2 + lado * 26, 860 + 40 * k)
        ctx.stroke()
    caixa(ctx, t, "THE SWIRL", "COLOR SQUIRTED INTO THE STREAM", PINK)


def d_tesoura(ctx, t, s):
    fundo(ctx)
    ciclo = (t * 2.2) % 1.0
    fio(ctx, t, W / 2, 640, 900, CORES[3])
    fecha = max(0.0, 1 - abs(ciclo - 0.5) * 6)
    for lado in (-1, 1):   # lâminas
        ctx.save()
        ctx.translate(W / 2 + lado * (40 + 120 * (1 - fecha)), 910)
        ctx.set_source_rgb(0.80, 0.82, 0.88)
        ctx.move_to(0, -12)
        ctx.line_to(-lado * 130, 0)
        ctx.line_to(0, 12)
        ctx.close_path()
        ctx.fill()
        ctx.restore()
    for i in range(4):   # gotas caindo
        y = 960 + ((t * 2.2 + i * 0.25) % 1.0) * 260
        ctx.set_source_rgb(*LARANJA)
        ctx.arc(W / 2, y, 30, 0, 2 * math.pi)
        ctx.fill()
    caixa(ctx, t, "SNIP!", "GLOWING BLOBS, ONE BY ONE", YELLOW)


def d_rolos(ctx, t, s):
    fundo(ctx)
    for r in range(2):   # dois rolos com sulcos em espiral
        y = 930 + r * 90
        ctx.set_source_rgb(0.55, 0.57, 0.62)
        round_rect(ctx, 100, y - 40, 880, 80, 40)
        ctx.fill()
        for j in range(14):
            x = 110 + ((j * 64 + t * (90 if r == 0 else -90)) % 860)
            ctx.set_source_rgba(0.30, 0.31, 0.35, 0.9)
            ctx.set_line_width(6)
            ctx.move_to(x, y - 36)
            ctx.line_to(x + 26, y + 36)
            ctx.stroke()
    for i in range(7):   # bolinhas avançando e esfriando do laranja ao vidro
        x = 120 + ((t * 150 + i * 135) % 860)
        f = (x - 120) / 860
        if f < 0.4:
            ctx.set_source_rgb(*LARANJA)
            ctx.arc(x, 975, 38, 0, 2 * math.pi)
            ctx.fill()
        else:
            gude(ctx, x, 975, 38, CORES[i % 5], rot=x * 0.08, alpha=min(1.0, (f - 0.4) * 4))
    caixa(ctx, t, "ROLLED ROUND", "SPINNING STEEL ROLLERS", GREEN)


def d_pilha(ctx, t, s):
    fundo(ctx)
    n = min(60, int(t * 24))
    for i in range(n):   # pote enchendo
        col, lin = i % 10, i // 10
        x = 270 + col * 56 + (28 if lin % 2 else 0)
        y = 1150 - lin * 50
        gude(ctx, x, y, 26, CORES[i % 5], rot=i)
    ctx.set_source_rgba(1, 1, 1, 0.25)   # pote de vidro
    ctx.set_line_width(8)
    ctx.move_to(220, 820)
    ctx.line_to(220, 1190)
    ctx.line_to(860, 1190)
    ctx.line_to(860, 820)
    ctx.stroke()
    caixa(ctx, t, "SINCE 1905", "THE SAME TRICK, MILLIONS A DAY", (0.6, 0.85, 1.0))


SEGMENTS = [
    Seg(["No human hand makes these perfect spheres.", "A machine rolls them round, while they're still glowing."],
        d_gancho, {"title": "HOW ARE MARBLES MADE?"}, tail=0.2),
    Seg(["It starts with old glass, melted at over a thousand degrees."], d_forno,
        {"big": "MELT", "color": LARANJA}, tail=0.2),
    Seg(["Squirts of colored glass go into the stream. That's the swirl inside every marble."], d_cor,
        {"big": "SWIRL", "color": PINK}, tail=0.2),
    Seg(["Then a blade snips the glowing stream into little blobs. Snip, snip, snip."], d_tesoura,
        {"big": "SNIP", "color": YELLOW}, tail=0.2),
    Seg(["Each blob drops onto two spinning rollers with spiral grooves. They roll it forward until it's perfectly round, and cool."],
        d_rolos, {"big": "ROLL", "color": GREEN}, tail=0.2),
    Seg(["The same trick was invented in nineteen oh five, and it still makes millions of marbles a day."], d_pilha,
        {"big": "DONE", "color": (0.6, 0.85, 1.0)}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Did you ever play marbles? Be honest.", "DID YOU PLAY MARBLES?",
                                fundo=lambda ctx, t, s: fundo(ctx)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
