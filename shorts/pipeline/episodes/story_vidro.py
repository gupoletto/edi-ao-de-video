"""How is glass made? (2D animated story). Sat 21/11/2026, storytelling (how it's made).
Search 21/11: "how glass is made" median 596k (top 9.3M); "how pencils are made" 255k.

Facts (common soda-lime glass, the kind in windows and bottles):
- about 70% silica sand, plus soda ash (sodium carbonate, lowers the melting point) and limestone (makes it durable);
- melted in a furnace at around 1,500 C;
- in sand (quartz) the atoms sit in a neat crystal grid; when the melt cools fast they freeze in a jumble, with no
  crystals to scatter light, which is why glass is clear;
- flat window glass is made with the float process (Alastair Pilkington, 1950s): the molten glass is poured onto a
  bath of molten tin, floats, and spreads into a perfectly flat sheet;
- then it is cooled slowly in a long oven (annealing) so it doesn't crack, and cut into sheets.
Tone: curious -> lofi music.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

core.MUSICA = "curioso"   # tom -> lofi
AREIA = (0.93, 0.80, 0.55)
LAVA = (1.0, 0.55, 0.15)
VIDRO = (0.70, 0.90, 0.95)
CY = 900


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mix(a, b, k):
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def fundo(ctx, cor=(0.10, 0.12, 0.18)):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *cor)
    g.add_color_stop_rgb(1, *(c * 0.4 for c in cor))
    ctx.set_source(g)
    ctx.paint()


def caixa(ctx, l1, l2, cor, y=540):
    round_rect(ctx, 150, y - 56, 780, 136, 26)
    ctx.set_source_rgba(0.03, 0.04, 0.08, 0.82)
    ctx.fill()
    text_center(ctx, l1, W / 2, y, 52, cor, "ExtraBold")
    text_center(ctx, l2, W / 2, y + 56, 28, WHITE, "Bold")


def graos(ctx, k, t, cx=W / 2, cy=CY, r=230, n=260):
    """Grãos de areia; k = 0 espalhados num monte, 1 desfeitos (para a transição)."""
    for i in range(n):
        a = i * 2.39996
        d = r * math.sqrt((i + 0.5) / n)
        x = cx + d * math.cos(a) * 1.4
        y = cy + 120 - abs(d * math.sin(a)) * 0.9
        y += k * (300 + (i % 7) * 30)
        ctx.set_source_rgba(*mix(AREIA, (0.8, 0.65, 0.4), (i % 5) / 5), 1 - k)
        ctx.arc(x + 3 * math.sin(t * 2 + i), y, 5 + i % 3, 0, 2 * math.pi)
        ctx.fill()


def janela(ctx, alpha, t, cx=W / 2, cy=CY):
    import cairo
    w, h = 520, 620
    ctx.push_group()
    g = cairo.LinearGradient(0, cy - h / 2, 0, cy + h / 2)
    g.add_color_stop_rgb(0, 0.45, 0.72, 0.98)
    g.add_color_stop_rgb(1, 0.85, 0.93, 1.0)
    ctx.rectangle(cx - w / 2, cy - h / 2, w, h)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.9)   # nuvem
    for dx, r in ((-60, 50), (0, 70), (70, 50)):
        ctx.arc(cx - 80 + dx + 20 * math.sin(t * 0.5), cy - 120, r, 0, 2 * math.pi)
        ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.35)   # reflexo
    ctx.move_to(cx - w / 2 + 40, cy + h / 2)
    ctx.line_to(cx - w / 2 + 160, cy + h / 2)
    ctx.line_to(cx + w / 2, cy - h / 2 + 60)
    ctx.line_to(cx + w / 2, cy - h / 2 - 40 + 60)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgb(0.95, 0.95, 0.95)   # moldura
    ctx.set_line_width(26)
    ctx.rectangle(cx - w / 2, cy - h / 2, w, h)
    ctx.stroke()
    ctx.set_line_width(14)
    ctx.move_to(cx, cy - h / 2)
    ctx.line_to(cx, cy + h / 2)
    ctx.move_to(cx - w / 2, cy)
    ctx.line_to(cx + w / 2, cy)
    ctx.stroke()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)


def d_gancho(ctx, t, s):
    fundo(ctx)
    m1 = s.mark(1) if len(s.items) > 1 else 99
    k = ease((t - m1 + 0.2) / 1.2)
    janela(ctx, 1 - k, t)
    if k > 0:
        ctx.push_group()
        graos(ctx, 0, t)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(k)


def d_receita(ctx, t, s):
    fundo(ctx)
    itens = [("SAND", "70%", AREIA, 300), ("SODA ASH", "MELTS IT EASIER", (0.95, 0.95, 0.95), 540),
             ("LIMESTONE", "MAKES IT TOUGH", (0.75, 0.75, 0.70), 780)]
    for i, (nome, sub, cor, x) in enumerate(itens):
        k = ease((t - i * 1.0) / 0.6)
        if k <= 0:
            continue
        y = 1040 - 40 * (1 - k)
        ctx.set_source_rgba(*cor, k)   # monte
        ctx.move_to(x - 110, y)
        ctx.curve_to(x - 60, y - 170, x + 60, y - 170, x + 110, y)
        ctx.close_path()
        ctx.fill()
        text_center(ctx, nome, x, y + 60, 36, cor, "ExtraBold", alpha=k)
        text_center(ctx, sub, x, y + 100, 22, WHITE, "Bold", alpha=k)
    caixa(ctx, "THE RECIPE", "THREE POWDERS, THAT'S IT", YELLOW)


def forno(ctx, t, calor):
    ctx.set_source_rgb(0.30, 0.22, 0.20)
    round_rect(ctx, 190, 720, 700, 460, 40)
    ctx.fill()
    ctx.set_source_rgb(*mix((0.2, 0.1, 0.05), LAVA, calor))
    round_rect(ctx, 240, 780, 600, 340, 26)
    ctx.fill()
    for i in range(14):   # chamas
        x = 270 + i * 42
        h = (40 + 30 * math.sin(t * 7 + i * 1.3)) * calor
        ctx.set_source_rgba(1, 0.8, 0.3, 0.8 * calor)
        ctx.move_to(x - 14, 1120)
        ctx.line_to(x, 1120 - h)
        ctx.line_to(x + 14, 1120)
        ctx.close_path()
        ctx.fill()


def d_forno(ctx, t, s):
    fundo(ctx, (0.14, 0.08, 0.06))
    k = ease(t / 3.5)
    forno(ctx, t, k)
    ctx.save()
    ctx.rectangle(240, 780, 600, 340)
    ctx.clip()
    graos(ctx, 0, t, cx=540, cy=900, r=180, n=160)   # a areia derrete por cima
    ctx.set_source_rgba(*LAVA, k)
    ctx.paint()
    ctx.restore()
    temp = int(1500 * k / 10) * 10
    caixa(ctx, f"{temp:,} °C", "HOTTER THAN LAVA", LAVA)


def d_atomos(ctx, t, s):
    fundo(ctx)
    k = ease((t - s.dur * 0.38) / 1.3)   # troca quando a voz chega em "cool the melt fast"
    for i in range(8):
        for j in range(8):
            gx = 280 + i * 75
            gy = 690 + j * 62
            rnd = math.sin(i * 12.9898 + j * 78.233) * 43758.5453
            dx = (rnd - math.floor(rnd) - 0.5) * 60
            dy = (math.sin(rnd) * 0.5) * 50
            x = gx + dx * k
            y = gy + dy * k
            ctx.set_source_rgb(*mix(AREIA, VIDRO, k))
            ctx.arc(x, y, 13, 0, 2 * math.pi)
            ctx.fill()
    if k > 0.8:   # luz atravessando
        for j in range(5):
            y = 720 + j * 100
            x = 180 + ((t * 500 + j * 130) % 760)
            ctx.set_source_rgba(1, 1, 0.6, 0.85)
            ctx.set_line_width(6)
            ctx.move_to(x - 80, y)
            ctx.line_to(x, y)
            ctx.stroke()
    caixa(ctx, "FROZEN CHAOS" if k > 0.5 else "NEAT CRYSTALS",
          "NOTHING LEFT TO BLOCK LIGHT" if k > 0.5 else "SAND: ATOMS IN A GRID", VIDRO if k > 0.5 else AREIA)


def d_estanho(ctx, t, s):
    fundo(ctx)
    ctx.set_source_rgb(0.62, 0.65, 0.70)   # banho de estanho
    ctx.rectangle(90, 960, 900, 120)
    ctx.fill()
    for i in range(10):
        ctx.set_source_rgba(1, 1, 1, 0.25)
        ctx.rectangle(110 + ((i * 97 + t * 60) % 860), 990 + (i % 3) * 25, 40, 4)
        ctx.fill()
    L = 120 + 820 * ease(t / 4.0)   # fita de vidro se espalhando
    ctx.set_source_rgba(*LAVA, 0.95)
    ctx.move_to(120, 900)
    ctx.curve_to(150, 930, 140, 950, 160, 958)
    ctx.line_to(120 + L, 958)
    ctx.line_to(120 + L, 945)
    ctx.line_to(170, 945)
    ctx.close_path()
    ctx.fill()
    ctx.rectangle(100, 820, 60, 90)   # bico do forno
    ctx.fill()
    caixa(ctx, "FLOATS ON MOLTEN TIN", "PERFECTLY FLAT, EVERY TIME", (0.8, 0.85, 0.92))


def d_recozer(ctx, t, s):
    fundo(ctx)
    k = ease(t / 4.0)
    for i in range(12):   # rolos
        ctx.set_source_rgb(0.35, 0.35, 0.40)
        ctx.arc(120 + i * 76, 1000, 18, 0, 2 * math.pi)
        ctx.fill()
    for i in range(4):   # chapas andando, esfriando do laranja ao transparente
        x = -260 + ((t * 160 + i * 300) % 1400)
        c = mix(LAVA, VIDRO, min(1.0, max(0.0, (x + 100) / 900)))
        ctx.set_source_rgba(*c, 0.9)
        ctx.rectangle(x, 960, 240, 18)
        ctx.fill()
    a = ease((t - 2.5) / 1.0)
    if a > 0:   # a chapa vira a janela
        ctx.set_source_rgba(0.08, 0.09, 0.13, a)
        ctx.rectangle(0, 600, W, 700)
        ctx.fill()
        janela(ctx, a, t, cx=W / 2, cy=900)
    if a < 0.5:   # a caixa sai quando a janela entra
        caixa(ctx, "COOLED SLOWLY", "OR IT WOULD CRACK", GREEN, y=540)


SEGMENTS = [
    Seg(["Look through any window. Fun fact:", "it used to be a beach."], d_gancho,
        {"title": "HOW IS GLASS MADE?"}, tail=0.2),
    Seg(["Glass starts as sand, mixed with soda ash and crushed limestone."], d_receita,
        {"big": "THE RECIPE", "color": YELLOW}, tail=0.2),
    Seg(["The mix goes into a furnace at fifteen hundred degrees, hot enough to melt rock."], d_forno,
        {"big": "MELT", "color": LAVA}, tail=0.2),
    Seg(["In sand, atoms sit in a neat grid. Cool the melt fast, and they freeze in a jumble. That's why glass is clear."],
        d_atomos, {"big": "THE SECRET", "color": VIDRO}, tail=0.2),
    Seg(["For windows, the hot glass is poured onto a pool of melted tin. It floats, and spreads perfectly flat."],
        d_estanho, {"big": "THE TIN BATH", "color": (0.8, 0.85, 0.92)}, tail=0.2),
    Seg(["Then it cools slowly in a long oven, gets cut, and becomes the window you're looking through."],
        d_recozer, {"big": "COOL DOWN", "color": GREEN}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("What everyday thing should I explain next?", "WHAT SHOULD I EXPLAIN NEXT?",
                                fundo=lambda ctx, t, s: (fundo(ctx), janela(ctx, 0.5, t))))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
