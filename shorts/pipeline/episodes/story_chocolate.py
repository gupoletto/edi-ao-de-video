"""How is chocolate made? (2D animated story). Sun 22/11/2026, storytelling (how it's made).
Search 22/11: "how chocolate is made" median 2.56M; "how lego is made" 2.34M; "how paper is made" 933k.

Facts:
- cacao pods grow straight out of the trunk of the cacao tree, in the tropics (Ivory Coast and Ghana grow over half
  the world's cocoa); each pod holds roughly 30-50 beans in sweet white pulp;
- raw beans are bitter; they are fermented for about a week (under banana leaves or in boxes), which builds the
  chocolate flavor, then dried in the sun;
- roasted, cracked, and the shells blown away, leaving the nibs;
- ground nibs (about half cocoa butter) melt into a thick liquid, "chocolate liquor" (no alcohol);
- mixed with sugar (and milk for milk chocolate) and conched: stirred for hours or days to make it smooth (Rodolphe
  Lindt, 1879);
- tempered: heated and cooled to precise temperatures so the cocoa butter forms the right crystals, giving the snap
  and shine; then poured into molds.
Tone: curious -> lofi.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

core.MUSICA = "curioso"   # tom -> lofi
CACAU = (0.85, 0.45, 0.15)
CHOC = (0.36, 0.20, 0.10)
CHOC_CL = (0.55, 0.32, 0.17)
CREME = (0.98, 0.95, 0.88)
OURO = (0.80, 0.45, 0.05)   # cabeçalhos legíveis no fundo claro


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def fundo(ctx, a=(0.98, 0.90, 0.78), b=(0.90, 0.72, 0.55)):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *a)
    g.add_color_stop_rgb(1, *b)
    ctx.set_source(g)
    ctx.paint()


def caixa(ctx, l1, l2, cor, y=540):
    round_rect(ctx, 150, y - 56, 780, 136, 26)
    ctx.set_source_rgba(0.18, 0.09, 0.04, 0.88)
    ctx.fill()
    text_center(ctx, l1, W / 2, y, 52, cor, "ExtraBold")
    text_center(ctx, l2, W / 2, y + 56, 28, WHITE, "Bold")


def vagem(ctx, x, y, s=1.0, ang=0.0, aberta=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    ctx.new_path()
    ctx.set_source_rgb(*CACAU)
    ctx.save()
    ctx.scale(1, 2.1)
    ctx.arc(0, 0, 55, 0, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    ctx.set_source_rgba(0.6, 0.28, 0.08, 0.6)   # gomos
    ctx.set_line_width(4)
    for dx in (-28, 0, 28):
        ctx.move_to(dx, -105)
        ctx.curve_to(dx * 1.6, -40, dx * 1.6, 40, dx, 105)
        ctx.stroke()
    if aberta > 0:   # metade aberta mostrando as sementes na polpa branca
        ctx.set_source_rgba(*CREME, aberta)
        ctx.save()
        ctx.scale(1, 2.0)
        ctx.arc(0, 0, 42, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
        for i in range(10):
            ctx.set_source_rgba(0.55, 0.30, 0.35, aberta)
            ctx.save()
            ctx.translate(-14 + 28 * (i % 2), -72 + 16 * i)
            ctx.scale(1.3, 0.8)
            ctx.arc(0, 0, 11, 0, 2 * math.pi)
            ctx.restore()
            ctx.fill()
    ctx.restore()


def d_gancho(ctx, t, s):
    fundo(ctx, (0.55, 0.80, 0.60), (0.20, 0.45, 0.25))
    ctx.set_source_rgb(0.38, 0.25, 0.15)   # tronco
    ctx.rectangle(470, 680, 140, 600)
    ctx.fill()
    ctx.set_source_rgb(0.15, 0.40, 0.18)   # copa
    for dx, dy, r in ((-150, 660, 140), (150, 660, 140), (0, 600, 160)):
        ctx.arc(540 + dx, dy + 12 * math.sin(t * 0.8 + dx), r, 0, 2 * math.pi)
        ctx.fill()
    for i, (x, y, a) in enumerate(((440, 860, -0.4), (650, 960, 0.4), (430, 1100, -0.3))):
        k = ease((t - i * 0.4) / 0.6)
        if k > 0:
            vagem(ctx, x, y, 0.75 * k, a + 0.05 * math.sin(t * 2 + i))


def d_vagem(ctx, t, s):
    fundo(ctx)
    k = ease((t - 0.8) / 1.2)
    vagem(ctx, W / 2, 920, 1.6, 0.0, aberta=k)
    caixa(ctx, "30-50 BEANS", "IN SWEET WHITE PULP · AND BITTER", PINK)


def d_fermenta(ctx, t, s):
    fundo(ctx, (0.95, 0.85, 0.60), (0.80, 0.60, 0.35))
    dias = min(7, int(t / 0.6) + 1)
    cor = tuple(a + (b - a) * (dias - 1) / 6 for a, b in zip((0.70, 0.45, 0.45), CHOC_CL))
    for i in range(36):   # monte de sementes mudando de cor
        x = 300 + (i % 9) * 60 + (30 if (i // 9) % 2 else 0)
        y = 1050 - (i // 9) * 40
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1.3, 0.8)
        ctx.arc(0, 0, 24, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(*cor)
        ctx.fill()
    ctx.set_source_rgba(0.25, 0.55, 0.20, 0.9)   # folha de bananeira por cima
    ctx.save()
    ctx.translate(540, 840)
    ctx.scale(3.2, 0.7)
    ctx.arc(0, 0, 110, math.pi, 2 * math.pi)
    ctx.restore()
    ctx.fill()
    caixa(ctx, f"DAY {dias}", "FERMENTING = FLAVOR", YELLOW)


def d_torra(ctx, t, s):
    fundo(ctx)
    ctx.set_source_rgb(0.30, 0.30, 0.33)   # tambor de torra girando
    ctx.arc(540, 930, 230, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgb(0.18, 0.18, 0.2)
    ctx.arc(540, 930, 190, 0, 2 * math.pi)
    ctx.fill()
    for i in range(22):
        a = t * 2.5 + i * 0.29
        r = 60 + (i * 37) % 120
        ctx.save()
        ctx.translate(540 + r * math.cos(a), 930 + r * math.sin(a) * 0.9)
        ctx.rotate(a)
        ctx.scale(1.3, 0.8)
        ctx.arc(0, 0, 16, 0, 2 * math.pi)
        ctx.restore()
        ctx.set_source_rgb(*CHOC)
        ctx.fill()
    for i in range(6):   # cascas voando para fora
        x = 780 + ((t * 200 + i * 60) % 280)
        y = 760 - 30 * math.sin(i + t * 3)
        ctx.set_source_rgba(0.75, 0.6, 0.4, 0.8)
        ctx.rectangle(x, y, 18, 8)
        ctx.fill()
    caixa(ctx, "ROASTED & CRACKED", "SHELLS BLOWN AWAY · NIBS LEFT", CHOC_CL)


def d_moer(ctx, t, s):
    fundo(ctx)
    k = ease(t / 3.0)
    ctx.set_source_rgb(0.62, 0.62, 0.66)   # mós
    for dx in (-120, 120):
        ctx.arc(540 + dx, 820, 110, 0, 2 * math.pi)
        ctx.fill()
    ctx.set_source_rgb(0.45, 0.45, 0.5)
    for dx, sgn in ((-120, 1), (120, -1)):
        a = sgn * t * 3
        ctx.set_line_width(8)
        ctx.move_to(540 + dx, 820)
        ctx.line_to(540 + dx + 100 * math.cos(a), 820 + 100 * math.sin(a))
        ctx.stroke()
    ctx.set_source_rgb(*CHOC)   # rio de chocolate escorrendo
    ctx.move_to(500, 900)
    ctx.curve_to(480, 1000, 600, 1040, 560, 1100 + 60 * k)
    ctx.line_to(620, 1100 + 60 * k)
    ctx.curve_to(660, 1040, 560, 980, 580, 900)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgb(*CHOC)
    ctx.rectangle(200, 1140, 680, 40 + 20 * k)
    ctx.fill()
    caixa(ctx, "HALF OF IT IS FAT", "SO IT MELTS INTO A LIQUID", CHOC_CL)


def d_concha(ctx, t, s):
    fundo(ctx)
    ctx.set_source_rgb(0.55, 0.55, 0.6)   # tanque
    round_rect(ctx, 220, 760, 640, 420, 40)
    ctx.fill()
    ctx.set_source_rgb(*CHOC_CL)
    round_rect(ctx, 250, 800, 580, 350, 30)
    ctx.fill()
    for i in range(5):   # redemoinhos
        a = t * 3 + i * 1.3
        ctx.set_source_rgba(0.65, 0.42, 0.25, 0.8)
        ctx.set_line_width(10)
        ctx.arc(540 + 150 * math.cos(i * 1.25), 975 + 60 * math.sin(i * 1.25), 50, a, a + 3.5)
        ctx.stroke()
    for i in range(10):   # açúcar e leite caindo
        x = 340 + (i * 47) % 400
        y = 640 + ((t * 300 + i * 60) % 180)
        ctx.set_source_rgba(1, 1, 1, 0.9)
        ctx.rectangle(x, y, 12, 12)
        ctx.fill()
    caixa(ctx, "STIRRED FOR HOURS", "SUGAR, MILK · SILKY SMOOTH", CREME)


def d_tempera(ctx, t, s):
    fundo(ctx)
    k = ease((t - 1.5) / 2.0)
    temps = [45, 27, 31]
    idx = min(2, int(t / 1.0))
    for i in range(3):   # forminhas
        x = 270 + i * 270
        ctx.set_source_rgb(0.85, 0.85, 0.88)
        round_rect(ctx, x - 100, 900, 200, 260, 20)
        ctx.fill()
        ctx.set_source_rgb(*CHOC)
        round_rect(ctx, x - 85, 1160 - 230 * k, 170, 230 * k, 14)
        ctx.fill()
        if k > 0.95:   # brilho da barra
            ctx.set_source_rgba(1, 1, 1, 0.35)
            ctx.rectangle(x - 60, 950, 20, 180)
            ctx.fill()
    caixa(ctx, f"{temps[idx]} °C", "HEAT, COOL, HEAT: THE SNAP & SHINE", YELLOW)


SEGMENTS = [
    Seg(["Chocolate starts on a tree.", "Inside a weird fruit that grows straight out of the trunk."], d_gancho,
        {"title": "HOW IS CHOCOLATE MADE?"}, tail=0.2),
    Seg(["Crack one open, and you'll find beans in white pulp. And they taste awful. Super bitter."], d_vagem,
        {"big": "CACAO POD", "color": (0.85, 0.25, 0.35)}, tail=0.2),
    Seg(["So farmers pile them under banana leaves for a week. They ferment, and that's where the chocolate flavor is born."],
        d_fermenta, {"big": "FERMENT", "color": OURO}, tail=0.2),
    Seg(["Then they're dried, roasted, and cracked. The shells blow away."], d_torra,
        {"big": "ROAST", "color": CHOC_CL}, tail=0.2),
    Seg(["The bits left inside are half fat. Grind them, and they melt into a thick chocolate liquid."], d_moer,
        {"big": "GRIND", "color": CHOC_CL}, tail=0.2),
    Seg(["Add sugar and milk, and stir it for hours, until it's silky smooth."], d_concha,
        {"big": "STIR", "color": CHOC}, tail=0.2),
    Seg(["Last trick: heat it, cool it, heat it again, to the exact degree. That's what gives the shine and the snap."],
        d_tempera, {"big": "TEMPER", "color": OURO}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Dark, milk, or white: which team are you?", "DARK, MILK OR WHITE?",
                                fundo=lambda ctx, t, s: fundo(ctx)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
