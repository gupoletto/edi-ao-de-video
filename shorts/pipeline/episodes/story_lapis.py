"""How are pencils made? (2D animated story). Mon 23/11/2026, storytelling (history + how it's made).
Search 23/11: "how pencils are made" median 268k.

Facts:
- there is no lead in a pencil: the core is graphite mixed with clay; in the 1500s a huge graphite deposit found in
  Borrowdale, England, was thought to be a kind of lead ("plumbago"), and the name stuck;
- more clay makes a harder, lighter pencil (H); more graphite makes a softer, darker one (B);
- the graphite-clay paste is pressed into thin rods and baked in a kiln at around 1,000 C;
- a slat of wood (often cedar) gets grooves cut into it, the leads are laid in, a second grooved slat is glued on top
  (a "sandwich"), and the block is cut into individual pencils;
- then they are painted, stamped, and get an eraser in a metal band (the ferrule).
Tone: curious -> lofi.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, pop_caixa, render, round_rect, text_center  # noqa: E402

core.MUSICA = "curioso"   # tom -> lofi
GRAF = (0.28, 0.29, 0.32)
ARGILA = (0.80, 0.68, 0.52)
CEDRO = (0.88, 0.66, 0.45)
AMAR = (1.0, 0.80, 0.15)
ROSA = (0.95, 0.55, 0.60)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def fundo(ctx):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.16, 0.22, 0.30)
    g.add_color_stop_rgb(1, 0.06, 0.08, 0.12)
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


def lapis(ctx, x, y, L=700, ang=0.0, s=1.0):
    """Lápis amarelo deitado; (x, y) = ponta."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    ctx.new_path()
    ctx.set_source_rgb(*GRAF)   # grafite da ponta
    ctx.move_to(0, 0)
    ctx.line_to(36, -10)
    ctx.line_to(36, 10)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgb(*CEDRO)   # madeira apontada
    ctx.move_to(36, -10)
    ctx.line_to(110, -36)
    ctx.line_to(110, 36)
    ctx.line_to(36, 10)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgb(*AMAR)
    ctx.rectangle(110, -36, L - 200, 72)
    ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.12)
    ctx.rectangle(110, 12, L - 200, 24)
    ctx.fill()
    ctx.set_source_rgb(0.75, 0.76, 0.80)   # ponteira de metal
    ctx.rectangle(L - 90, -38, 40, 76)
    ctx.fill()
    ctx.set_source_rgb(*ROSA)   # borracha
    round_rect(ctx, L - 50, -36, 60, 72, 14)
    ctx.fill()
    ctx.restore()


def d_gancho(ctx, t, s):
    fundo(ctx)
    ctx.set_source_rgb(0.97, 0.97, 0.94)   # papel
    ctx.rectangle(120, 700, 840, 520)
    ctx.fill()
    ctx.set_source_rgb(*GRAF)   # rabisco desenhado ao vivo desde o 1º quadro
    ctx.set_line_width(7)
    ctx.move_to(180, 960)
    n = int(min(1.0, t / 2.5) * 120)
    px, py = 180, 960
    for i in range(n):
        px = 180 + i * 5.4
        py = 960 + 120 * math.sin(i * 0.18) * math.cos(i * 0.05)
        ctx.line_to(px, py)
    ctx.stroke()
    lapis(ctx, px, py, 600, -0.9, 0.8)
    if len(s.items) > 1 and t > s.mark(1):
        caixa(ctx, t - s.mark(1), "0% LEAD", "IT NEVER HAD ANY", PINK)


def d_nome(ctx, t, s):
    fundo(ctx)
    ctx.set_source_rgb(0.30, 0.45, 0.30)   # colina de Borrowdale
    ctx.move_to(0, 1180)
    ctx.curve_to(300, 800, 700, 820, W, 1050)
    ctx.line_to(W, 1250)
    ctx.line_to(0, 1250)
    ctx.close_path()
    ctx.fill()
    k = ease((t - 0.5) / 1.2)
    ctx.set_source_rgb(*GRAF)   # veio de grafite brilhando
    ctx.save()
    ctx.translate(540, 1040)
    ctx.scale(1, 0.4)
    ctx.arc(0, 0, 160 * k, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.4 * k)
    ctx.arc(500, 1020, 20, 0, 2 * math.pi)
    ctx.fill()
    caixa(ctx, t, "ENGLAND · 1500s", "THEY THOUGHT IT WAS LEAD", (0.75, 0.80, 0.90))


def d_mistura(ctx, t, s):
    fundo(ctx)
    for i, (nome, cor, x) in enumerate((("GRAPHITE", GRAF, 300), ("CLAY", ARGILA, 780))):
        ctx.set_source_rgb(*cor)
        ctx.move_to(x - 120, 920)
        ctx.curve_to(x - 60, 740, x + 60, 740, x + 120, 920)
        ctx.close_path()
        ctx.fill()
        text_center(ctx, nome, x, 975, 34, WHITE, "ExtraBold")
    k = 0.5 + 0.5 * math.sin(t * 1.4)   # régua H <-> B
    ctx.set_source_rgba(1, 1, 1, 0.3)
    round_rect(ctx, 200, 1015, 680, 40, 20)
    ctx.fill()
    ctx.set_source_rgb(*AMAR)
    ctx.arc(200 + 680 * k, 1035, 28, 0, 2 * math.pi)
    ctx.fill()
    text_center(ctx, "B · SOFT", 260, 1105, 26, WHITE, "Bold")
    text_center(ctx, "H · HARD", 820, 1105, 26, WHITE, "Bold")
    caixa(ctx, t, "GRAPHITE + CLAY", "MORE CLAY = HARDER PENCIL", ARGILA)


def d_forno(ctx, t, s):
    fundo(ctx)
    k = ease(t / 2.5)
    ctx.set_source_rgb(0.32, 0.22, 0.20)
    round_rect(ctx, 160, 720, 760, 440, 40)
    ctx.fill()
    ctx.set_source_rgb(*[a + (b - a) * k for a, b in zip((0.25, 0.12, 0.06), (1.0, 0.50, 0.15))])
    round_rect(ctx, 210, 780, 660, 320, 26)
    ctx.fill()
    for i in range(9):   # varetas assando
        ctx.set_source_rgb(*GRAF)
        ctx.rectangle(250 + i * 70, 820, 14, 240)
        ctx.fill()
    caixa(ctx, t, f"{int(1000 * k):,} °C", "BAKED INTO HARD THIN RODS", (1.0, 0.55, 0.2))


def d_sanduiche(ctx, t, s):
    fundo(ctx)
    tampa = ease((t - 2.0) / 1.0)
    ctx.set_source_rgb(*CEDRO)   # tábua de baixo com sulcos
    ctx.rectangle(170, 1000, 740, 70)
    ctx.fill()
    n = 9
    for i in range(n):
        x = 200 + i * 80
        ctx.set_source_rgb(0.70, 0.50, 0.32)
        ctx.rectangle(x, 1000, 30, 22)
        ctx.fill()
        cai = ease((t - 0.3 - i * 0.12) / 0.4)   # grafite cai no sulco
        ctx.set_source_rgb(*GRAF)
        ctx.rectangle(x + 6, 1004 - 260 * (1 - cai), 18, 18)
        ctx.fill()
    ctx.set_source_rgb(*[c * 0.95 for c in CEDRO])   # tábua de cima descendo
    ctx.rectangle(170, 930 - 200 * (1 - tampa), 740, 70)
    ctx.fill()
    caixa(ctx, t, "THE SANDWICH", "TWO GROOVED WOOD SLATS, GLUED", CEDRO)


def d_final(ctx, t, s):
    fundo(ctx)
    for i in range(6):   # lápis saindo da máquina e caindo em fila
        k = ease((t - i * 0.4) / 0.6)
        if k <= 0:
            continue
        lapis(ctx, 160, 760 + i * 80 + 30 * (1 - k), 760, 0.0, 1.0)
    caixa(ctx, t, "CUT, PAINTED, ERASER ON", "READY TO WRITE", AMAR)


SEGMENTS = [
    Seg(["Here's a weird fact about every pencil you've ever used.", "There's zero lead in it."], d_gancho,
        {"title": "HOW ARE PENCILS MADE?"}, tail=0.2),
    Seg(["In the fifteen hundreds, English miners found a black rock that marked paper. They thought it was lead. The name stuck."],
        d_nome, {"big": "THE MIX-UP", "color": (0.75, 0.80, 0.90)}, tail=0.2),
    Seg(["It was graphite. Today it's mixed with clay. More clay makes it harder and lighter, more graphite makes it darker."],
        d_mistura, {"big": "THE CORE", "color": ARGILA}, tail=0.2),
    Seg(["The paste is squeezed into thin rods and baked at a thousand degrees."], d_forno,
        {"big": "BAKE", "color": (1.0, 0.55, 0.2)}, tail=0.2),
    Seg(["The rods are laid into grooves in a wood slat, and a second slat is glued on top. A pencil sandwich."],
        d_sanduiche, {"big": "SANDWICH", "color": CEDRO}, tail=0.2),
    Seg(["Then it's cut apart, painted, stamped, and topped with an eraser."], d_final,
        {"big": "DONE", "color": AMAR}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Do you chew your pencils? Be honest.", "DO YOU CHEW THEM?",
                                fundo=lambda ctx, t, s: fundo(ctx)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
