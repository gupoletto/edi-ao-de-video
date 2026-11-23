"""How is Coca-Cola made? (2D animated story). Mon 23/11/2026, storytelling (history + how it's made).
Search 23/11: "how coca cola is made" median 2.12M. Brand named only descriptively; no logo or trade dress drawn
(generic red can and bottle), disclaimer in the description.

Facts:
- invented in 1886 by pharmacist John Pemberton in Atlanta; first sold at a pharmacy soda fountain for 5 cents a
  glass, about 9 glasses a day in the first year;
- the exact formula is a trade secret; the company keeps it in a vault at the World of Coca-Cola in Atlanta (since
  2011);
- the company makes a concentrate and sends it to bottling plants around the world;
- at the plant, the concentrate is mixed with treated water and sweetener into a syrup and then the drink;
- the drink is chilled and carbon dioxide is dissolved into it under pressure (cold liquid holds more gas): that is
  the fizz;
- fast filling lines fill around 2,000 cans per minute and seal them immediately so the gas stays in.
Tone: lively -> pop music.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, pop_caixa, render, round_rect, text_center  # noqa: E402

core.MUSICA = "animado"   # tom -> pop
VERM = (0.85, 0.08, 0.12)
COLA = (0.30, 0.12, 0.05)
PRATA = (0.80, 0.82, 0.86)
AZUL = (0.45, 0.75, 1.0)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def fundo(ctx, a=(0.55, 0.05, 0.08), b=(0.20, 0.02, 0.04)):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *a)
    g.add_color_stop_rgb(1, *b)
    ctx.set_source(g)
    ctx.paint()


def caixa(ctx, t, l1, l2, cor, y=540):
    def d():
        round_rect(ctx, 150, y - 56, 780, 136, 26)
        ctx.set_source_rgba(0.06, 0.02, 0.02, 0.9)
        ctx.fill()
        text_center(ctx, l1, W / 2, y, 52, cor, "ExtraBold")
        text_center(ctx, l2, W / 2, y + 56, 28, WHITE, "Bold")
    pop_caixa(ctx, t, W / 2, y + 10, d)


def lata(ctx, x, y, s=1.0, ang=0.0, aberta=False):
    """Lata vermelha genérica (sem marca), centro (x, y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    ctx.new_path()
    ctx.set_source_rgb(*VERM)
    round_rect(ctx, -80, -150, 160, 300, 24)
    ctx.fill()
    ctx.set_source_rgb(*PRATA)
    ctx.rectangle(-72, -165, 144, 22)
    ctx.rectangle(-72, 143, 144, 18)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.85)   # onda branca genérica
    ctx.set_line_width(10)
    ctx.move_to(-80, 20)
    ctx.curve_to(-30, -30, 30, 60, 80, 0)
    ctx.stroke()
    ctx.set_source_rgba(1, 1, 1, 0.25)   # reflexo
    ctx.rectangle(-55, -140, 18, 280)
    ctx.fill()
    ctx.restore()


def bolhas(ctx, t, x0, x1, y0, y1, n=40, r=8):
    for i in range(n):
        x = x0 + (i * 73) % max(1, int(x1 - x0))
        y = y1 - ((t * (120 + (i % 5) * 30) + i * 41) % (y1 - y0))
        ctx.set_source_rgba(1, 1, 1, 0.7)
        ctx.arc(x + 4 * math.sin(t * 3 + i), y, r * (0.5 + (i % 3) * 0.3), 0, 2 * math.pi)
        ctx.fill()


def d_gancho(ctx, t, s):
    fundo(ctx)
    k = ease(t / 0.6)
    lata(ctx, W / 2, 890 + 260 * (1 - k), 1.35, 0.25 * math.sin(t * 2.5))   # sobe girando desde o 1º quadro
    bolhas(ctx, t, 300, 780, 640, 1200, n=50, r=10)
    if len(s.items) > 1 and t > s.mark(1):
        caixa(ctx, t - s.mark(1), "TOP SECRET", "THE RECIPE SITS IN A VAULT", YELLOW)


def d_farmacia(ctx, t, s):
    fundo(ctx, (0.55, 0.40, 0.25), (0.25, 0.15, 0.08))
    ctx.set_source_rgb(0.40, 0.26, 0.14)   # balcão
    ctx.rectangle(120, 1040, 840, 140)
    ctx.fill()
    for i in range(5):   # frascos na prateleira
        ctx.set_source_rgba(*[(0.3, 0.6, 0.4), (0.7, 0.4, 0.2), (0.3, 0.4, 0.7)][i % 3], 0.85)
        round_rect(ctx, 200 + i * 150, 760, 70, 110, 14)
        ctx.fill()
    ctx.set_source_rgba(0.9, 0.95, 1.0, 0.6)   # copo
    ctx.move_to(480, 880)
    ctx.line_to(600, 880)
    ctx.line_to(585, 1040)
    ctx.line_to(495, 1040)
    ctx.close_path()
    ctx.fill()
    k = ease((t - 0.5) / 2.0)
    ctx.set_source_rgb(*COLA)
    ctx.move_to(490 + 3 * (1 - k), 1040 - 150 * k)
    ctx.line_to(590 - 3 * (1 - k), 1040 - 150 * k)
    ctx.line_to(585, 1040)
    ctx.line_to(495, 1040)
    ctx.close_path()
    ctx.fill()
    bolhas(ctx, t, 500, 580, 1040 - 150 * k, 1040, n=int(14 * k), r=4)
    caixa(ctx, t, "1886 · 5 CENTS", "SOLD AT A PHARMACY IN ATLANTA", YELLOW)


def d_cofre(ctx, t, s):
    fundo(ctx, (0.25, 0.27, 0.32), (0.08, 0.09, 0.12))
    ctx.set_source_rgb(0.50, 0.52, 0.58)   # porta do cofre
    ctx.arc(W / 2, 900, 260, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(0.35, 0.37, 0.42)
    ctx.arc(W / 2, 900, 200, 0, 2 * math.pi)
    ctx.fill()
    a = 2.5 * math.sin(t * 1.5)   # roda girando
    ctx.set_source_rgb(0.75, 0.77, 0.82)
    ctx.set_line_width(18)
    for j in range(4):
        b = a + j * math.pi / 2
        ctx.move_to(W / 2, 900)
        ctx.line_to(W / 2 + 150 * math.cos(b), 900 + 150 * math.sin(b))
        ctx.stroke()
    ctx.arc(W / 2, 900, 40, 0, 2 * math.pi)
    ctx.fill()
    caixa(ctx, t, "THE VAULT", "THE FORMULA IS A TRADE SECRET", PRATA)


def d_xarope(ctx, t, s):
    fundo(ctx)
    k = ease(t / 3.0)
    for i, (nome, cor, x) in enumerate((("CONCENTRATE", COLA, 260), ("WATER", AZUL, 540), ("SWEETENER", (1, 1, 1), 820))):
        ctx.set_source_rgb(0.70, 0.72, 0.76)   # tanques
        round_rect(ctx, x - 90, 700, 180, 220, 20)
        ctx.fill()
        ctx.set_source_rgb(*cor)
        round_rect(ctx, x - 75, 715 + 190 * k, 150, 190 * (1 - k), 14)
        ctx.fill()
        text_center(ctx, nome, x, 960, 26, WHITE, "ExtraBold")
        ctx.set_source_rgba(*cor, 0.9)   # cano até o misturador
        ctx.set_line_width(14)
        ctx.move_to(x, 990)
        ctx.line_to(540, 1080)
        ctx.stroke()
    ctx.set_source_rgb(0.70, 0.72, 0.76)
    round_rect(ctx, 380, 1060, 320, 130, 24)
    ctx.fill()
    ctx.set_source_rgb(*COLA)
    round_rect(ctx, 395, 1180 - 110 * k, 290, 110 * k, 18)
    ctx.fill()
    caixa(ctx, t, "MIX", "SHIPPED TO BOTTLERS WORLDWIDE", AZUL)


def d_gas(ctx, t, s):
    fundo(ctx, (0.10, 0.25, 0.45), (0.03, 0.08, 0.18))
    k = ease(t / 3.0)
    ctx.set_source_rgb(0.70, 0.72, 0.76)   # tanque pressurizado
    round_rect(ctx, 260, 700, 560, 480, 60)
    ctx.fill()
    ctx.set_source_rgb(*COLA)
    round_rect(ctx, 290, 740, 500, 410, 40)
    ctx.fill()
    for i in range(int(60 * k)):   # CO2 entrando e dissolvendo
        x = 310 + (i * 53) % 460
        y = 760 + (i * 89) % 370
        ctx.set_source_rgba(1, 1, 1, 0.75)
        ctx.arc(x + 3 * math.sin(t * 4 + i), y, 6, 0, 2 * math.pi)
        ctx.fill()
    text_center(ctx, "CO2", 540, 680 + 10 * math.sin(t * 3), 40, WHITE, "ExtraBold")
    ctx.set_source_rgba(*AZUL, 0.9)   # gelo no termômetro
    caixa(ctx, t, "COLD + PRESSURE", "FORCES GAS INTO THE DRINK", AZUL)


def d_linha(ctx, t, s):
    fundo(ctx)
    ctx.set_source_rgb(0.25, 0.25, 0.28)   # esteira
    ctx.rectangle(0, 1150, W, 30)
    ctx.fill()
    for i in range(9):   # latas correndo; enchem e são lacradas no meio
        x = -120 + ((t * 420 + i * 150) % 1350)
        lata(ctx, x, 1010, 0.6)
        if 470 < x < 610:
            ctx.set_source_rgba(1, 1, 1, 0.8)
            ctx.rectangle(x - 6, 820, 12, 80)
            ctx.fill()
    ctx.set_source_rgb(0.55, 0.57, 0.62)   # bico de enchimento
    ctx.rectangle(500, 760, 80, 60)
    ctx.fill()
    n = int(2000 * ease(t / 3.0))
    caixa(ctx, t, f"{n:,} CANS / MIN", "FILLED AND SEALED BEFORE THE FIZZ ESCAPES", YELLOW)


SEGMENTS = [
    Seg(["Billions of these are made every year.", "But the recipe is locked in a vault."], d_gancho,
        {"title": "HOW IS COCA-COLA MADE?"}, tail=0.2),
    Seg(["It started in eighteen eighty six, in a pharmacy in Atlanta, sold for five cents a glass."], d_farmacia,
        {"big": "1886", "color": YELLOW}, tail=0.2),
    Seg(["The exact formula is a trade secret, kept in a vault in Atlanta."], d_cofre,
        {"big": "THE SECRET", "color": PRATA}, tail=0.2),
    Seg(["The company ships a concentrate to bottling plants. There, it's mixed with filtered water and sweetener."],
        d_xarope, {"big": "THE MIX", "color": AZUL}, tail=0.2),
    Seg(["Then it's chilled, and carbon dioxide is forced in under pressure. Cold liquid holds more gas. That's the fizz."],
        d_gas, {"big": "THE FIZZ", "color": AZUL}, tail=0.2),
    Seg(["Machines fill up to two thousand cans a minute, and seal them instantly, before the bubbles escape."],
        d_linha, {"big": "FILL & SEAL", "color": YELLOW}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Can or glass bottle: which tastes better?", "CAN OR GLASS BOTTLE?",
                                fundo=lambda ctx, t, s: (fundo(ctx), bolhas(ctx, t, 200, 880, 600, 1250))))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
