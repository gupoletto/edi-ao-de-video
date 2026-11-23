"""How was the Burj Khalifa built? (2D animated story). Fri 20/11/2026, new format: storytelling (how it's built).
Search 20/11: "how were skyscrapers built" median 35k (top 867k); "how was the golden gate bridge built" 19k.

Facts (Burj Khalifa, Dubai, built 2004-2010, opened 4 January 2010):
- 828 m tall, the tallest building in the world;
- it stands on 192 concrete piles, 1.5 m wide, driven about 50 m into the ground, under a 3.7 m thick raft;
- the ground is sand and weak rock: the piles hold the tower by friction, not by reaching bedrock;
- concrete was pumped more than 600 m up, a world record at the time; in the desert heat it was poured at night with
  ice mixed in so it would not crack while setting;
- the Y-shaped plan (inspired by a desert flower) buttresses the core and confuses the wind;
- at the peak pace a new floor went up about every 3 days;
- the steel spire (over 200 m) was assembled inside the tower and jacked up into place.
Story arc: hook (taller than anything) -> problem (sand) -> foundation trick -> concrete at night with ice ->
floors every 3 days -> spire jacked from inside -> ending -> question.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

core.MUSICA = "construcao"   # tom -> épico
CHAO = 1180
AZUL = (0.4, 0.75, 1.0)
LARANJA = (1.0, 0.62, 0.25)
TOPO_MAX = 760
TX = 730          # x do eixo da torre   # altura da torre em px quando completa (sem a agulha)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ceu(ctx, noite=0.0):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, CHAO)
    a = (0.98, 0.72, 0.42)
    b = (0.40, 0.66, 0.92)
    n1 = (0.03, 0.04, 0.12)
    n2 = (0.08, 0.10, 0.25)
    mix = lambda c, d: [x + (y - x) * noite for x, y in zip(c, d)]  # noqa: E731
    g.add_color_stop_rgb(0, *mix(b, n1))
    g.add_color_stop_rgb(1, *mix(a, n2))
    ctx.set_source(g)
    ctx.paint()
    if noite > 0.3:
        ctx.set_source_rgba(1, 1, 1, noite * 0.7)
        for i in range(70):
            ctx.arc((i * 397) % W, (i * 211) % 700, 1.4, 0, 2 * math.pi)
            ctx.fill()


def deserto(ctx, t):
    ctx.set_source_rgb(0.86, 0.70, 0.46)
    ctx.move_to(0, CHAO)
    for x in range(0, W + 30, 30):
        ctx.line_to(x, CHAO + 8 * math.sin(x * 0.01))
    ctx.line_to(W, H)
    ctx.line_to(0, H)
    ctx.close_path()
    ctx.fill()
    for i in range(6):   # cidade ao fundo
        x = 60 + i * 180
        h = 80 + (i * 53) % 120
        ctx.set_source_rgba(0.35, 0.40, 0.50, 0.5)
        ctx.rectangle(x, CHAO - h, 70, h)
        ctx.fill()


def torre(ctx, frac, agulha=0.0, cx=TX, noite=0.0, guindaste=True, t=0.0):
    """Perfil escalonado da torre: frac 0..1 de altura construída; agulha 0..1 (sobe por dentro)."""
    hmax = TOPO_MAX * frac
    degraus = [(1.0, 300), (0.82, 240), (0.66, 190), (0.52, 150), (0.40, 110), (0.28, 80), (0.17, 56), (0.08, 40)]
    # cada degrau: (fração de altura onde começa a estreitar, largura)
    for i, (f0, w) in enumerate(degraus):
        y0 = CHAO - TOPO_MAX * (1 - f0)
        y1 = CHAO - TOPO_MAX * (1 - degraus[i + 1][0]) if i + 1 < len(degraus) else CHAO - TOPO_MAX
        topo = max(y1, CHAO - hmax)
        if topo >= y0:
            break
        ctx.rectangle(cx - w / 2, topo, w, y0 - topo)
        ctx.set_source_rgb(0.62, 0.68, 0.76)
        ctx.fill()
        ctx.rectangle(cx - w / 2, topo, w / 2, y0 - topo)   # lado na sombra
        ctx.set_source_rgba(0.2, 0.25, 0.35, 0.35)
        ctx.fill()
    if noite > 0.3 and frac > 0.05:   # janelas acesas
        ctx.set_source_rgba(1, 0.9, 0.6, noite * 0.8)
        y = CHAO - 12
        while y > CHAO - hmax + 10:
            ctx.rectangle(cx - 10, y, 20, 3)
            y -= 14
        ctx.fill()
    if agulha > 0 and frac >= 0.999:
        h = 200 * agulha
        ctx.set_source_rgb(0.85, 0.88, 0.92)
        ctx.move_to(cx - 8, CHAO - TOPO_MAX)
        ctx.line_to(cx + 8, CHAO - TOPO_MAX)
        ctx.line_to(cx + 2, CHAO - TOPO_MAX - h)
        ctx.line_to(cx - 2, CHAO - TOPO_MAX - h)
        ctx.close_path()
        ctx.fill()
    if guindaste and 0.02 < frac < 0.999:   # guindaste que sobe junto com a torre
        yt = CHAO - hmax
        ctx.set_source_rgb(*YELLOW)
        ctx.set_line_width(5)
        ctx.move_to(cx + 10, yt)
        ctx.line_to(cx + 10, yt - 70)
        ctx.move_to(cx - 60, yt - 70)
        ctx.line_to(cx + 170, yt - 70)
        ctx.stroke()
        gx = cx + 150 - 60 * (0.5 + 0.5 * math.sin(t * 1.3))
        ctx.set_line_width(2)
        ctx.move_to(gx, yt - 70)
        ctx.line_to(gx, yt - 25)
        ctx.stroke()
        ctx.rectangle(gx - 10, yt - 25, 20, 12)
        ctx.fill()


def caixa(ctx, l1, l2, cor, y=520, lado=False):
    """lado=True: caixa estreita à esquerda, para não tapar a torre (que fica em TX)."""
    x0, w, fs = (60, 500, 44) if lado else (150, 780, 52)
    round_rect(ctx, x0, y - 56, w, 136, 26)
    ctx.set_source_rgba(0.03, 0.04, 0.08, 0.82)
    ctx.fill()
    text_center(ctx, l1, x0 + w / 2, y, fs, cor, "ExtraBold")
    text_center(ctx, l2, x0 + w / 2, y + 56, 26 if lado else 28, WHITE, "Bold")


def d_gancho(ctx, t, s):
    ceu(ctx)
    deserto(ctx, t)
    torre(ctx, 1.0, 1.0, guindaste=False)
    if len(s.items) > 1 and t > s.mark(1):
        caixa(ctx, "828 METERS", "TALLEST BUILDING ON EARTH", YELLOW, y=560, lado=True)


def d_areia(ctx, t, s):
    ceu(ctx)
    deserto(ctx, t)
    for i in range(160):   # grãos de areia escorrendo
        x = (i * 173) % W
        y = CHAO + 40 + ((i * 97 + t * 60) % (H - CHAO - 60))
        ctx.set_source_rgba(0.6, 0.45, 0.25, 0.6)
        ctx.arc(x, y, 3, 0, 2 * math.pi)
        ctx.fill()
    caixa(ctx, "NO SOLID ROCK", "JUST SAND AND WEAK STONE", PINK)


def d_estacas(ctx, t, s):
    import cairo
    ctx.set_source_rgb(0.86, 0.70, 0.46)   # corte do solo
    ctx.paint()
    g = cairo.LinearGradient(0, 0, 0, 640)
    g.add_color_stop_rgb(0, 0.40, 0.66, 0.92)
    g.add_color_stop_rgb(1, 0.98, 0.72, 0.42)
    ctx.rectangle(0, 0, W, 640)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgb(0.55, 0.55, 0.58)   # radier
    ctx.rectangle(140, 640, 800, 40)
    ctx.fill()
    n = 14
    k = ease(t / 3.0)
    for i in range(n):
        x = 170 + i * (740 / (n - 1))
        h = 520 * min(1.0, max(0.0, k * n - i * 0.6) / 2)
        ctx.set_source_rgb(0.72, 0.72, 0.75)
        ctx.rectangle(x - 12, 680, 24, h)
        ctx.fill()
    caixa(ctx, "192 PILES", "1.5 M WIDE · 50 M DEEP", GREEN, y=520)


def d_atrito(ctx, t, s):
    d_estacas(ctx, 10.0, s)
    for i in range(14):   # setas de atrito subindo ao longo das estacas
        x = 170 + i * (740 / 13)
        for j in range(4):
            y = 1150 - j * 120 - ((t * 80) % 120)
            ctx.set_source_rgba(*YELLOW, 0.9)
            ctx.move_to(x + 16, y)
            ctx.line_to(x + 30, y + 18)
            ctx.line_to(x + 2, y + 18)
            ctx.close_path()
            ctx.fill()
    caixa(ctx, "FRICTION", "THE SAND GRIPS EVERY PILE", YELLOW, y=520)


def d_concreto(ctx, t, s):
    ceu(ctx, noite=1.0)
    deserto(ctx, t)
    frac = 0.35 + 0.25 * ease(t / 5.0)
    torre(ctx, frac, noite=1.0, t=t)
    ctx.set_source_rgb(0.9, 0.5, 0.2)   # tubo de bombeamento
    ctx.set_line_width(6)
    ctx.move_to(TX + 160, CHAO)
    ctx.line_to(TX + 160, CHAO - TOPO_MAX * frac)
    ctx.stroke()
    for j in range(8):   # concreto subindo pelo tubo
        y = CHAO - ((t * 260 + j * 90) % (TOPO_MAX * frac))
        ctx.set_source_rgb(0.75, 0.75, 0.78)
        ctx.arc(TX + 160, y, 7, 0, 2 * math.pi)
        ctx.fill()
    for i in range(5):   # cubos de gelo
        x = 220 + i * 40
        y = CHAO - 40 - 20 * abs(math.sin(t * 2 + i))
        ctx.set_source_rgba(0.8, 0.95, 1.0, 0.9)
        ctx.rectangle(x, y, 26, 26)
        ctx.fill()
    caixa(ctx, "POURED AT NIGHT", "WITH ICE IN THE MIX", AZUL, y=560, lado=True)


def d_andares(ctx, t, s):
    noite = 0.5 + 0.5 * math.sin(t * 2.2)   # dias e noites passando
    ceu(ctx, noite=max(0.0, noite))
    deserto(ctx, t)
    torre(ctx, 0.6 + 0.4 * ease(t / 4.5), noite=max(0.0, noite), t=t * 4)
    caixa(ctx, "1 FLOOR / 3 DAYS", "AT FULL SPEED", GREEN, y=560, lado=True)


def d_agulha(ctx, t, s):
    ceu(ctx)
    deserto(ctx, t)
    torre(ctx, 1.0, ease((t - 0.6) / 3.5), guindaste=False)
    caixa(ctx, "JACKED UP", "THE SPIRE ROSE FROM INSIDE", LARANJA, y=560, lado=True)


def d_fim(ctx, t, s):
    ceu(ctx, noite=ease(t / 3.0))
    deserto(ctx, t)
    torre(ctx, 1.0, 1.0, noite=ease(t / 3.0), guindaste=False)
    if t > 1.0:
        caixa(ctx, "6 YEARS", "2004 - 2010", YELLOW, y=560, lado=True)


SEGMENTS = [
    Seg(["This is the tallest building on Earth.", "Eight hundred twenty eight meters, standing on sand."], d_gancho,
        {"title": "HOW WAS THE BURJ KHALIFA BUILT?"}, tail=0.2),
    Seg(["Dubai has no solid rock near the surface. So how do you hold up half a million tons?"], d_areia,
        {"big": "THE PROBLEM", "color": PINK}, tail=0.2),
    Seg(["They drilled a hundred ninety two concrete piles, fifty meters into the ground."], d_estacas,
        {"big": "THE FOUNDATION", "color": GREEN}, tail=0.1),
    Seg(["They never touch bedrock. The sand squeezing every pile is what holds the tower up."], d_atrito,
        {"big": "THE TRICK", "color": YELLOW}, tail=0.2),
    Seg(["The desert heat would crack fresh concrete, so they poured it at night, with ice mixed in, and pumped it six hundred meters up."],
        d_concreto, {"big": "THE HEAT", "color": AZUL}, tail=0.2),
    Seg(["At full speed, a new floor went up every three days."], d_andares,
        {"big": "FAST", "color": GREEN}, tail=0.3),
    Seg(["And the giant spire on top? They built it inside the tower, then pushed it up two hundred meters."],
        d_agulha, {"big": "THE SPIRE", "color": LARANJA}, tail=0.2),
    Seg(["Six years after the first pile, the tallest thing humans ever built switched on its lights."], d_fim,
        {"big": "DONE", "color": YELLOW}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Would you live on the top floor?", "WOULD YOU LIVE UP THERE?",
                                fundo=lambda ctx, t, s: (ceu(ctx, 1.0), deserto(ctx, t),
                                                         torre(ctx, 1.0, 1.0, noite=1.0, guindaste=False))))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
