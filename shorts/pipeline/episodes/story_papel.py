"""How is paper made? (2D animated story). Sun 22/11/2026, storytelling (history + how it's made).
Search 22/11: "how paper is made" median 933k.

Facts:
- around 105 AD, Cai Lun, an official of the Han court in China, is credited with the papermaking recipe: plant
  fibers (bark, hemp, old rags, fishing nets) beaten into a pulp in water, scooped onto a screen and dried; the
  technique stayed in Asia for centuries and reached Europe around the 1100s;
- today most paper comes from wood: logs are chipped and cooked with chemicals (kraft process) to dissolve the lignin
  that glues the fibers together, leaving soft cellulose fibers: pulp;
- the pulp that hits the paper machine is about 99% water; it is sprayed onto a fast-moving mesh, the water drains
  and the fibers mat together into a sheet;
- presses squeeze out more water, then steam-heated cylinders dry it; machines can be longer than a football field
  and run at around 100 km/h;
- paper fibers can be recycled roughly 5 to 7 times before they get too short.
Tone: history -> cinema music.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

core.MUSICA = "historia"   # tom -> cinema
PAPEL = (0.97, 0.96, 0.92)
MADEIRA = (0.60, 0.42, 0.25)
AGUA = (0.40, 0.65, 0.90)
OURO = (0.95, 0.75, 0.30)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def fundo(ctx, a=(0.12, 0.13, 0.18), b=(0.05, 0.05, 0.08)):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *a)
    g.add_color_stop_rgb(1, *b)
    ctx.set_source(g)
    ctx.paint()


def caixa(ctx, l1, l2, cor, y=540):
    round_rect(ctx, 150, y - 56, 780, 136, 26)
    ctx.set_source_rgba(0.03, 0.04, 0.08, 0.85)
    ctx.fill()
    text_center(ctx, l1, W / 2, y, 52, cor, "ExtraBold")
    text_center(ctx, l2, W / 2, y + 56, 28, WHITE, "Bold")


def folha(ctx, x, y, w, h, ang=0.0, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.new_path()
    ctx.set_source_rgba(*PAPEL, alpha)
    ctx.rectangle(-w / 2, -h / 2, w, h)
    ctx.fill()
    ctx.set_source_rgba(0.6, 0.7, 0.85, 0.5 * alpha)
    ctx.set_line_width(2)
    for i in range(1, int(h / 40)):
        ctx.move_to(-w / 2 + 20, -h / 2 + i * 40)
        ctx.line_to(w / 2 - 20, -h / 2 + i * 40)
    ctx.stroke()
    ctx.restore()


def arvore(ctx, x, y, s=1.0, alpha=1.0):
    ctx.new_path()
    ctx.set_source_rgba(*MADEIRA, alpha)
    ctx.rectangle(x - 22 * s, y - 220 * s, 44 * s, 220 * s)
    ctx.fill()
    ctx.set_source_rgba(0.15, 0.45, 0.22, alpha)
    for dx, dy, r in ((-60, -260, 90), (60, -260, 90), (0, -340, 110)):
        ctx.arc(x + dx * s, y + dy * s, r * s, 0, 2 * math.pi)
        ctx.fill()


def d_gancho(ctx, t, s):
    fundo(ctx)
    m1 = s.mark(1) if len(s.items) > 1 else 99
    k = ease((t - m1 + 0.2) / 1.0)
    folha(ctx, W / 2, 900, 480, 620, 0.05 * math.sin(t), 1 - k)
    if k > 0:
        arvore(ctx, W / 2, 1180, 1.5, k)


def d_cailun(ctx, t, s):
    fundo(ctx, (0.30, 0.20, 0.12), (0.12, 0.07, 0.04))
    ctx.set_source_rgb(0.45, 0.30, 0.18)   # tina de madeira
    round_rect(ctx, 200, 960, 680, 220, 30)
    ctx.fill()
    ctx.set_source_rgba(*AGUA, 0.8)
    ctx.rectangle(230, 980, 620, 60)
    ctx.fill()
    for i in range(14):   # trapos, casca e rede boiando
        x = 260 + (i * 47) % 560
        y = 1000 + 8 * math.sin(t * 2 + i)
        ctx.set_source_rgb(*[(0.75, 0.70, 0.60), (0.55, 0.40, 0.25), (0.65, 0.65, 0.55)][i % 3])
        ctx.rectangle(x, y, 34, 12)
        ctx.fill()
    k = ease((t - 2.0) / 1.5)   # a peneira sobe com a folha
    ctx.set_source_rgb(0.55, 0.40, 0.22)
    ctx.rectangle(330, 900 - 160 * k, 420, 18)
    ctx.fill()
    if k > 0:
        ctx.set_source_rgba(*PAPEL, k)
        ctx.rectangle(340, 890 - 160 * k, 400, 10)
        ctx.fill()
    caixa(ctx, "CHINA · 105 AD", "CAI LUN'S RECIPE: RAGS, BARK, WATER", OURO)


def d_cavacos(ctx, t, s):
    fundo(ctx)
    k = ease(t / 2.5)
    ctx.set_source_rgb(*MADEIRA)   # tora entrando no picador
    ctx.rectangle(120 + 200 * k, 840, 360, 90)
    ctx.fill()
    ctx.set_source_rgb(0.40, 0.42, 0.46)
    ctx.rectangle(560, 780, 120, 220)
    ctx.fill()
    for i in range(30):   # cavacos voando
        x = 700 + ((t * 250 + i * 23) % 260)
        y = 860 + 40 * math.sin(i * 1.7 + t * 4) + (i % 5) * 20
        ctx.set_source_rgb(0.85, 0.70, 0.45)
        ctx.rectangle(x, y, 20, 12)
        ctx.fill()
    ctx.set_source_rgb(0.30, 0.30, 0.34)   # panela de cozimento
    round_rect(ctx, 300, 1040, 480, 140, 20)
    ctx.fill()
    for i in range(8):
        ctx.set_source_rgba(1, 1, 1, 0.4)
        ctx.arc(340 + i * 55, 1030 - ((t * 60 + i * 20) % 60), 8, 0, 2 * math.pi)
        ctx.fill()
    caixa(ctx, "CHIPPED & COOKED", "THE WOOD'S GLUE DISSOLVES", MADEIRA)


def d_polpa(ctx, t, s):
    fundo(ctx)
    ctx.set_source_rgba(*AGUA, 0.85)
    ctx.rectangle(140, 720, 800, 460)
    ctx.fill()
    for i in range(70):   # fibras soltas na água
        x = 170 + (i * 113) % 740
        y = 750 + (i * 67) % 400 + 10 * math.sin(t * 1.5 + i)
        a = i * 0.7 + t * 0.4
        ctx.set_source_rgba(*PAPEL, 0.95)
        ctx.set_line_width(4)
        ctx.move_to(x, y)
        ctx.line_to(x + 30 * math.cos(a), y + 30 * math.sin(a))
        ctx.stroke()
    caixa(ctx, "99% WATER", "1% WOOD FIBERS", AGUA)


def d_maquina(ctx, t, s):
    fundo(ctx)
    ctx.set_source_rgb(0.45, 0.47, 0.52)   # tela
    ctx.rectangle(80, 960, 920, 16)
    ctx.fill()
    for i in range(10):   # roletes
        ctx.set_source_rgb(0.30, 0.31, 0.35)
        ctx.arc(110 + i * 96, 1000, 22, 0, 2 * math.pi)
        ctx.fill()
    ctx.set_source_rgba(*AGUA, 0.9)   # caixa de entrada jorrando polpa
    ctx.rectangle(60, 860, 90, 90)
    ctx.fill()
    for x in range(150, 1000, 8):   # faixa: azul (molhada) -> branca (papel)
        f = (x - 150) / 850
        cor = tuple(a + (b - a) * min(1, f * 1.5) for a, b in zip(AGUA, PAPEL))
        ctx.set_source_rgb(*cor)
        ctx.rectangle(x, 950 - 6 * (1 - f), 8, 10 + 6 * (1 - f))
        ctx.fill()
    for i in range(18):   # gotas caindo pela tela
        x = 170 + (i * 41) % 400
        y = 990 + ((t * 300 + i * 30) % 160)
        ctx.set_source_rgba(*AGUA, 0.8)
        ctx.arc(x, y, 5, 0, 2 * math.pi)
        ctx.fill()
    for i in range(6):   # marcas correndo = velocidade
        x = 150 + ((t * 700 + i * 150) % 850)
        ctx.set_source_rgba(1, 1, 1, 0.7)
        ctx.rectangle(x, 940, 40, 3)
        ctx.fill()
    caixa(ctx, "100 KM/H", "WATER DRAINS · FIBERS LOCK TOGETHER", GREEN)


def d_seca(ctx, t, s):
    fundo(ctx)
    for i in range(6):   # cilindros a vapor
        x = 170 + i * 150
        ctx.set_source_rgb(0.55, 0.56, 0.60)
        ctx.arc(x, 960 + (i % 2) * 120, 62, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.35)
        a = t * 4 + i
        ctx.arc(x, 960 + (i % 2) * 120, 50, a, a + 1.0)
        ctx.set_line_width(6)
        ctx.stroke()
    ctx.set_source_rgb(*PAPEL)   # o papel serpenteando entre eles
    ctx.set_line_width(8)
    ctx.move_to(80, 898)
    for i in range(6):
        x = 170 + i * 150
        y = 898 if i % 2 == 0 else 1142
        ctx.line_to(x, y)
    ctx.line_to(1000, 898)
    ctx.stroke()
    for i in range(8):   # vapor
        x = 150 + i * 110
        y = 860 - ((t * 80 + i * 30) % 120)
        ctx.set_source_rgba(1, 1, 1, 0.25)
        ctx.arc(x, y, 18, 0, 2 * math.pi)
        ctx.fill()
    k = ease((t - 2.5) / 1.0)
    if k > 0:   # a bobina gigante (os cilindros somem atrás)
        ctx.set_source_rgba(0.09, 0.09, 0.13, 0.92 * k)
        ctx.rectangle(0, 820, W, 400)
        ctx.fill()
        ctx.set_source_rgba(*PAPEL, k)
        ctx.arc(540, 1020, 150 * k, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_source_rgba(0.8, 0.78, 0.72, k)
        for r in range(20, int(150 * k), 18):
            ctx.arc(540, 1020, r, 0, 2 * math.pi)
            ctx.set_line_width(2)
            ctx.stroke()
    caixa(ctx, "PRESSED & DRIED", "ON STEAM-HEATED CYLINDERS", OURO)


def d_recicla(ctx, t, s):
    fundo(ctx)
    n = min(7, int(t / 0.6) + 1)
    for i in range(n):   # a mesma folha voltando mais cinza e menor
        k = i / 6
        folha(ctx, 220 + (i % 4) * 210, 820 + (i // 4) * 260, 150 * (1 - 0.35 * k), 200 * (1 - 0.35 * k),
              0.1 * math.sin(i), 1 - 0.5 * k)
        text_center(ctx, f"{i + 1}x", 220 + (i % 4) * 210, 950 + (i // 4) * 260, 30, WHITE, "ExtraBold")
    caixa(ctx, "RECYCLED 5-7 TIMES", "THEN THE FIBERS GET TOO SHORT", GREEN)


SEGMENTS = [
    Seg(["This sheet of paper was a tree.", "And a minute before it became paper, it was ninety nine percent water."],
        d_gancho, {"title": "HOW IS PAPER MADE?"}, tail=0.2),
    Seg(["The recipe started in China, almost two thousand years ago: soak rags and bark, beat them into mush, scoop it onto a screen, let it dry."],
        d_cailun, {"big": "105 AD", "color": OURO}, tail=0.2),
    Seg(["Today, logs are chipped and cooked in chemicals that dissolve the natural glue holding wood together."],
        d_cavacos, {"big": "COOK", "color": MADEIRA}, tail=0.2),
    Seg(["What's left are soft fibers floating in water. Ninety nine percent water."], d_polpa,
        {"big": "PULP", "color": AGUA}, tail=0.2),
    Seg(["It's sprayed onto a mesh racing at a hundred kilometers an hour. The water drains, and the fibers lock into a sheet."],
        d_maquina, {"big": "THE MACHINE", "color": GREEN}, tail=0.2),
    Seg(["Rollers squeeze it, hot cylinders dry it, and it's wound into rolls taller than you."], d_seca,
        {"big": "DRY", "color": OURO}, tail=0.2),
    Seg(["And when you recycle it, the fibers come back, five to seven times, before they're too short to hold on."],
        d_recicla, {"big": "AGAIN", "color": GREEN}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Paper books or screens: which do you read more?", "PAPER OR SCREEN?",
                                fundo=lambda ctx, t, s: (fundo(ctx), folha(ctx, W / 2, 900, 300, 380, 0.1, 0.4))))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
