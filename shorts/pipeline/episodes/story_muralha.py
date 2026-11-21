"""How was the Great Wall of China built? (2D animated story). Sat 21/11/2026, storytelling (how it was built).
Search 21/11: "how the great wall of china was built" median 32.9k (top 689k).

Facts:
- it is not one wall: many dynasties built walls over about 2,000 years, from before the Qin (221 BC) to the Ming
  (1368-1644); the famous brick-and-stone sections near Beijing are Ming;
- a 2012 Chinese government survey counted all sections together at about 21,196 km;
- early walls were mostly rammed earth: soil packed in thin layers between wooden boards and pounded hard;
- Ming builders used bricks and stone with lime mortar mixed with sticky rice soup (amylopectin), confirmed by a 2010
  study; it made the mortar stronger and more water resistant;
- hundreds of thousands of soldiers, peasants and convicts did the work;
- watchtowers passed warnings with smoke by day and fire by night, much faster than a rider;
- it is not visible to the naked eye from space (astronauts, including China's Yang Liwei, confirmed this).
Tone: epic construction -> epico music.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

core.MUSICA = "construcao"   # tom -> épico
PEDRA = (0.72, 0.66, 0.56)
TERRA = (0.66, 0.50, 0.33)
FOGO = (1.0, 0.55, 0.15)
VERM = (0.85, 0.25, 0.20)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ceu(ctx, noite=0.0):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    a, b = (0.55, 0.75, 0.95), (0.98, 0.85, 0.65)
    n1, n2 = (0.03, 0.04, 0.12), (0.10, 0.10, 0.22)
    g.add_color_stop_rgb(0, *[x + (y - x) * noite for x, y in zip(a, n1)])
    g.add_color_stop_rgb(0.7, *[x + (y - x) * noite for x, y in zip(b, n2)])
    ctx.set_source(g)
    ctx.paint()


def morro_y(x, t=0.0, fase=0.0):
    return 1000 - 140 * math.sin(x * 0.006 + fase) - 60 * math.sin(x * 0.017 + 1.3 + fase)


def montanhas(ctx, fase=0.0, noite=0.0):
    for camada, (cor, dy, f) in enumerate((((0.45, 0.55, 0.50), -160, 2.0), ((0.30, 0.45, 0.32), 0, 0.0))):
        c = [x * (1 - 0.6 * noite) for x in cor]
        ctx.set_source_rgb(*c)
        ctx.move_to(0, H)
        for x in range(0, W + 20, 20):
            ctx.line_to(x, morro_y(x, fase=fase + f) + dy)
        ctx.line_to(W, H)
        ctx.close_path()
        ctx.fill()


def muralha(ctx, frac, fase=0.0, torres=True, fogo=None, noite=0.0):
    """Muralha serpenteando sobre o morro da frente até a fração frac da largura."""
    xmax = W * frac
    ctx.set_source_rgb(*[x * (1 - 0.5 * noite) for x in PEDRA])
    ctx.set_line_width(26)
    ctx.move_to(0, morro_y(0, fase=fase) - 12)
    x = 0
    while x < xmax:
        x += 10
        ctx.line_to(x, morro_y(x, fase=fase) - 12)
    ctx.stroke()
    ctx.set_line_width(4)   # ameias
    x = 0
    while x < xmax:
        y = morro_y(x, fase=fase) - 26
        ctx.rectangle(x, y - 10, 8, 10)
        x += 18
    ctx.fill()
    if torres:
        for i, tx in enumerate(range(120, int(xmax), 260)):
            ty = morro_y(tx, fase=fase) - 12
            ctx.set_source_rgb(*[x * (1 - 0.5 * noite) for x in (0.62, 0.56, 0.47)])
            ctx.rectangle(tx - 30, ty - 80, 60, 80)
            ctx.fill()
            if fogo is not None and i <= fogo:
                for j in range(5):
                    h = 30 + 15 * math.sin(fogo * 9 + j * 2 + i)
                    ctx.set_source_rgba(*FOGO, 0.9)
                    ctx.move_to(tx - 20 + j * 10, ty - 80)
                    ctx.line_to(tx - 15 + j * 10, ty - 80 - h)
                    ctx.line_to(tx - 10 + j * 10, ty - 80)
                    ctx.close_path()
                    ctx.fill()


def caixa(ctx, l1, l2, cor, y=540):
    round_rect(ctx, 150, y - 56, 780, 136, 26)
    ctx.set_source_rgba(0.03, 0.04, 0.08, 0.82)
    ctx.fill()
    text_center(ctx, l1, W / 2, y, 52, cor, "ExtraBold")
    text_center(ctx, l2, W / 2, y + 56, 28, WHITE, "Bold")


def d_gancho(ctx, t, s):
    ceu(ctx)
    fase = t * 0.12
    montanhas(ctx, fase)
    muralha(ctx, 1.0, fase)
    if len(s.items) > 1 and t > s.mark(1):
        caixa(ctx, "2,000 YEARS", "AND IT'S NOT EVEN ONE WALL", YELLOW)


def d_muitas(ctx, t, s):
    ctx.set_source_rgb(0.93, 0.88, 0.76)   # mapa estilizado
    ctx.paint()
    linhas = [("QIN · 221 BC", VERM, 0.0, 740), ("HAN · 206 BC", (0.25, 0.45, 0.80), 1.2, 900),
              ("MING · 1368-1644", (0.20, 0.55, 0.30), 2.4, 1060)]
    for nome, cor, t0, y0 in linhas:
        k = ease((t - t0) / 1.2)
        if k <= 0:
            continue
        ctx.set_source_rgb(*cor)
        ctx.set_line_width(10)
        ctx.move_to(130, y0)
        x = 130
        while x < 130 + 820 * k:
            x += 12
            ctx.line_to(x, y0 - 30 * math.sin(x * 0.012 + t0) - 12 * math.sin(x * 0.04))
        ctx.stroke()
        text_center(ctx, nome, W / 2, y0 + 78, 30, cor, "ExtraBold", alpha=k)
    caixa(ctx, "21,196 KM", "ALL THE WALLS ADDED UP", VERM)


def d_taipa(ctx, t, s):
    ceu(ctx)
    ctx.set_source_rgb(0.45, 0.32, 0.20)   # chão
    ctx.rectangle(0, 1180, W, H - 1180)
    ctx.fill()
    camadas = min(9, int(t / 0.55))
    for i in range(camadas):   # camadas socadas
        ctx.set_source_rgb(*[c * (0.9 + 0.1 * (i % 2)) for c in TERRA])
        ctx.rectangle(330, 1170 - (i + 1) * 40, 420, 38)
        ctx.fill()
    ctx.set_source_rgb(0.55, 0.38, 0.20)   # tábuas
    topo = 1170 - (camadas + 2) * 40
    ctx.rectangle(300, topo, 30, 1180 - topo)
    ctx.rectangle(750, topo, 30, 1180 - topo)
    ctx.fill()
    ys = 1170 - (camadas + 1) * 40   # pilão batendo
    b = abs(math.sin(t * 7))
    for px in (430, 650):
        ctx.set_source_rgb(0.4, 0.28, 0.15)
        ctx.rectangle(px - 8, ys - 220 + 60 * b, 16, 200)
        ctx.fill()
        ctx.rectangle(px - 30, ys - 30 + 60 * b - 10, 60, 30)
        ctx.fill()
    caixa(ctx, "RAMMED EARTH", "DIRT POUNDED LAYER BY LAYER", TERRA)


def d_arroz(ctx, t, s):
    ceu(ctx)
    ctx.new_path()   # sem isso o arco ligava a um ponto solto e desenhava uma cunha
    ctx.set_source_rgb(0.95, 0.95, 0.93)   # tigela de arroz
    ctx.arc(300, 940, 150, 0, math.pi)
    ctx.fill()
    for i in range(40):
        ctx.set_source_rgb(1, 1, 0.97)
        ctx.save()
        ctx.translate(200 + (i * 37) % 200, 930 - (i * 13) % 40)
        ctx.rotate(i)
        ctx.scale(1, 0.5)
        ctx.arc(0, 0, 10, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
    k = ease((t - 1.0) / 3.0)
    for r in range(4):   # tijolos sendo assentados
        for c in range(4):
            idx = r * 4 + c
            if idx / 16 > k:
                continue
            x = 500 + c * 100 + (50 if r % 2 else 0)
            y = 1120 - r * 56
            ctx.set_source_rgb(0.62, 0.58, 0.55)
            ctx.rectangle(x, y, 94, 50)
            ctx.fill()
            ctx.set_source_rgb(0.96, 0.95, 0.88)   # argamassa
            ctx.rectangle(x, y + 50, 94, 6)
            ctx.fill()
    caixa(ctx, "STICKY RICE MORTAR", "STRONGER THAN LIME ALONE", (0.96, 0.95, 0.88))


def d_gente(ctx, t, s):
    ceu(ctx)
    montanhas(ctx, 0.3)
    muralha(ctx, 0.55 + 0.1 * ease(t / 4), 0.3)
    for i in range(36):   # fila de trabalhadores subindo o morro
        x = (i * 31 + t * 40) % (W + 60) - 30
        y = morro_y(x, fase=0.3) + 30 + (i % 3) * 14
        ctx.set_source_rgb(0.15, 0.12, 0.10)
        ctx.arc(x, y - 30, 8, 0, 2 * math.pi)
        ctx.fill()
        ctx.rectangle(x - 6, y - 22, 12, 24)
        ctx.fill()
        ctx.set_source_rgb(0.62, 0.58, 0.55)   # tijolo nas costas
        ctx.rectangle(x - 12, y - 30, 10, 14)
        ctx.fill()
    caixa(ctx, "HUNDREDS OF THOUSANDS", "SOLDIERS, FARMERS, PRISONERS", PINK)


def d_sinais(ctx, t, s):
    noite = 1.0
    ceu(ctx, noite)
    montanhas(ctx, 0.0, noite)
    muralha(ctx, 1.0, 0.0, fogo=int(t / 0.6), noite=noite)
    caixa(ctx, "FIRE BY NIGHT", "SMOKE BY DAY · FASTER THAN A HORSE", FOGO)


def d_espaco(ctx, t, s):
    import cairo
    ctx.set_source_rgb(0.01, 0.01, 0.04)
    ctx.paint()
    ctx.set_source_rgba(1, 1, 1, 0.7)
    for i in range(90):
        ctx.arc((i * 397) % W, (i * 211) % H, 1.3, 0, 2 * math.pi)
        ctx.fill()
    g = cairo.RadialGradient(440, 860, 40, 540, 960, 340)
    g.add_color_stop_rgb(0, 0.35, 0.6, 0.95)
    g.add_color_stop_rgb(1, 0.05, 0.15, 0.40)
    ctx.arc(540, 960, 290, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgba(0.3, 0.55, 0.3, 0.8)
    ctx.arc(600, 890, 105, 0, 2 * math.pi)
    ctx.fill()
    caixa(ctx, "NOT VISIBLE FROM SPACE", "TOO NARROW · SAME COLOR AS THE LAND", GREEN)


SEGMENTS = [
    Seg(["The Great Wall of China took about two thousand years to build.", "And it's not even one wall."], d_gancho,
        {"title": "HOW WAS THE GREAT WALL BUILT?"}, tail=0.2),
    Seg(["Dynasty after dynasty built their own walls. Add them all up: over twenty one thousand kilometers."],
        d_muitas, {"big": "MANY WALLS", "color": VERM}, tail=0.2),
    Seg(["The early walls were just dirt, packed between wooden boards and pounded rock hard, layer by layer."],
        d_taipa, {"big": "RAMMED EARTH", "color": TERRA}, tail=0.2),
    Seg(["Later builders used bricks, and glued them with a mortar made with sticky rice. It still holds today."],
        d_arroz, {"big": "THE SECRET GLUE", "big_size": 90, "color": (0.96, 0.95, 0.88)}, tail=0.2),
    Seg(["Hundreds of thousands of soldiers, farmers and prisoners carried it all up the mountains, by hand."],
        d_gente, {"big": "BY HAND", "color": PINK}, tail=0.2),
    Seg(["And the towers talked: smoke by day, fire by night, faster than any horse."], d_sinais,
        {"big": "THE ALARM", "color": FOGO}, tail=0.2),
    Seg(["One myth, though: you can't see it from space. It's too narrow, and the same color as the land."],
        d_espaco, {"big": "THE MYTH", "color": GREEN}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Would you walk the whole thing?", "WOULD YOU WALK IT ALL?",
                                fundo=lambda ctx, t, s: (ceu(ctx), montanhas(ctx), muralha(ctx, 1.0))))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
