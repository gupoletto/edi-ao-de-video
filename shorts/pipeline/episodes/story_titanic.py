"""Why the "unsinkable" Titanic sank (2D animated story). Fri 20/11/2026, new format: storytelling (history).
Search 20/11: "why did the titanic sink" median 55k (top 1.4M); "history explained" 940k.

Facts:
- RMS Titanic left Southampton on 10 April 1912 on her maiden voyage, with about 2,224 people aboard;
- her hull was split into 16 compartments by watertight bulkheads; she could stay afloat with up to 4 of the forward
  compartments flooded;
- at 11:40 pm on 14 April she struck an iceberg; lookouts spotted it less than a minute before; the impact opened
  the hull along about 90 m and flooded the first 6 compartments;
- the bulkheads did not reach the top deck, so as the bow sank, water spilled over each one into the next, like an
  ice cube tray tipping;
- she carried 20 lifeboats with room for about 1,178 people (more than the law then required);
- she sank at 2:20 am, 2 h 40 min after the collision; about 1,500 people died.
Story arc: hook (the unsinkable ship) -> setup (16 compartments, 4 can flood) -> conflict (iceberg, 6 flood) ->
mechanism (ice cube tray) -> the human cost (lifeboats) -> ending -> question.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core  # noqa: E402
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, ramp, render, round_rect, text_center  # noqa: E402

core.MUSICA = "historia"   # tom -> cinema
MAR = 1150
CASCO = (0.10, 0.10, 0.12)
N_COMP = 16


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ceu(ctx, t, lua=True):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, MAR)
    g.add_color_stop_rgb(0, 0.02, 0.03, 0.08)
    g.add_color_stop_rgb(1, 0.06, 0.10, 0.20)
    ctx.set_source(g)
    ctx.paint()
    for i in range(110):   # estrelas cintilando
        a = 0.4 + 0.4 * math.sin(t * 2 + i * 1.7)
        ctx.set_source_rgba(1, 1, 1, a)
        ctx.arc((i * 397) % W, (i * 211) % (MAR - 60), 1.2 + (i % 3) * 0.6, 0, 2 * math.pi)
        ctx.fill()


def mar(ctx, t, y=MAR):
    import cairo
    g = cairo.LinearGradient(0, y, 0, H)
    g.add_color_stop_rgb(0, 0.04, 0.10, 0.20)
    g.add_color_stop_rgb(1, 0.01, 0.02, 0.05)
    ctx.move_to(0, H)
    for x in range(0, W + 20, 20):
        ctx.line_to(x, y + 6 * math.sin(x * 0.02 + t * 1.5))
    ctx.line_to(W, H)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill()


def navio(ctx, x, y, s=1.0, inc=0.0, afunda=0.0, luzes=1.0, t=0.0):
    """Titanic de perfil: casco preto, faixa branca, 4 chaminés amarelas; inc = inclinação (rad, proa para baixo)."""
    ctx.save()
    ctx.translate(x, y + afunda)
    ctx.rotate(inc)
    ctx.scale(s, s)
    L = 820
    ctx.move_to(-L / 2, -40)
    ctx.line_to(L / 2 + 20, -40)
    ctx.line_to(L / 2 - 10, 50)
    ctx.line_to(-L / 2 + 30, 50)
    ctx.close_path()
    ctx.set_source_rgb(*CASCO)
    ctx.fill()
    ctx.rectangle(-L / 2 + 40, -80, L - 90, 40)
    ctx.set_source_rgb(0.92, 0.90, 0.85)
    ctx.fill()
    for i in range(4):
        cx = -230 + i * 150
        ctx.rectangle(cx - 22, -190, 44, 110)
        ctx.set_source_rgb(0.85, 0.62, 0.20)
        ctx.fill()
        ctx.rectangle(cx - 22, -190, 44, 22)
        ctx.set_source_rgb(0.08, 0.08, 0.08)
        ctx.fill()
    ctx.set_source_rgba(1.0, 0.88, 0.55, 0.9 * luzes)   # janelas acesas
    for i in range(34):
        ctx.rectangle(-L / 2 + 60 + i * 22, -66, 7, 7)
        ctx.rectangle(-L / 2 + 60 + i * 22, -20, 6, 6)
    ctx.fill()
    ctx.restore()


def compartimentos(ctx, cheios, t, x0=90, y0=760, w=900, h=230, nivel=None):
    """Corte do casco com 16 compartimentos; cheios = quantos (a partir da proa, à direita) estão alagados."""
    cw = w / N_COMP
    ctx.set_source_rgb(0.12, 0.12, 0.15)
    ctx.rectangle(x0, y0, w, h)
    ctx.fill()
    for i in range(N_COMP):
        idx = N_COMP - 1 - i            # i = 0 é a proa (direita)
        x = x0 + idx * cw
        f = max(0.0, min(1.0, cheios - i))
        if f > 0:
            hh = h * 0.85 * f
            ctx.set_source_rgb(0.20, 0.55, 0.90)
            ctx.rectangle(x + 2, y0 + h - hh, cw - 4, hh)
            ctx.fill()
    ctx.set_source_rgb(0.85, 0.85, 0.88)
    ctx.set_line_width(4)
    for i in range(1, N_COMP):
        x = x0 + i * cw
        ctx.move_to(x, y0 + h)
        ctx.line_to(x, y0 + h * 0.25)   # anteparas que NÃO chegam ao convés
        ctx.stroke()
    ctx.rectangle(x0, y0, w, h)
    ctx.stroke()


def caixa(ctx, l1, l2, cor, y=560):
    round_rect(ctx, 150, y - 56, 780, 136, 26)
    ctx.set_source_rgba(0.03, 0.04, 0.08, 0.82)
    ctx.fill()
    text_center(ctx, l1, W / 2, y, 52, cor, "ExtraBold")
    text_center(ctx, l2, W / 2, y + 56, 28, WHITE, "Bold")


def d_gancho(ctx, t, s):
    ceu(ctx, t)
    mar(ctx, t)
    navio(ctx, 1500 - 220 * t, MAR - 30, 1.0, 0.0, 0, 1.0, t)   # entra pela direita
    if t > s.mark(1) if len(s.items) > 1 else False:
        caixa(ctx, "\"UNSINKABLE\"", "APRIL 10, 1912 · 2,224 PEOPLE ON BOARD", YELLOW)


def d_comp(ctx, t, s):
    ceu(ctx, t)
    compartimentos(ctx, 4 * ease((t - 1.5) / 2.0), t)
    caixa(ctx, "16 COMPARTMENTS", "IT COULD FLOAT WITH 4 FLOODED", GREEN)


def d_iceberg(ctx, t, s):
    ceu(ctx, t)
    mar(ctx, t)
    xi = W / 2 + 260
    ctx.set_source_rgb(0.85, 0.92, 0.98)   # iceberg
    ctx.move_to(xi - 130, MAR + 4)
    ctx.line_to(xi - 60, MAR - 170)
    ctx.line_to(xi + 10, MAR - 120)
    ctx.line_to(xi + 70, MAR - 210)
    ctx.line_to(xi + 140, MAR + 4)
    ctx.close_path()
    ctx.fill()
    xn = W / 2 - 520 + 260 * ease(t / 2.5)
    navio(ctx, xn, MAR - 30, 0.9, 0.0, 0, 1.0, t)
    bate = t > 2.4
    if bate:
        ctx.set_source_rgba(1, 1, 1, max(0.0, 1 - (t - 2.4) / 0.4))
        ctx.paint()
        caixa(ctx, "11:40 PM", "LESS THAN A MINUTE TO REACT", PINK)


def d_alaga(ctx, t, s):
    ceu(ctx, t)
    compartimentos(ctx, 6 * ease(t / 2.5), t)
    if t > 2.0:
        caixa(ctx, "6 FLOODED", "TWO MORE THAN IT COULD TAKE", PINK)


def d_bandeja(ctx, t, s):
    """Proa afunda e a água passa por cima de cada antepara, como uma forma de gelo inclinada."""
    ceu(ctx, t)
    inc = 0.14 * ease(t / 3.0)
    ctx.save()
    ctx.translate(W / 2, 880)
    ctx.rotate(inc)
    ctx.translate(-W / 2, -880)
    compartimentos(ctx, 6 + 6 * ease((t - 0.8) / 3.5), t)
    ctx.restore()
    caixa(ctx, "LIKE AN ICE CUBE TRAY", "WATER SPILLED OVER EACH WALL", (0.4, 0.7, 1.0))


def d_botes(ctx, t, s):
    ceu(ctx, t)
    mar(ctx, t)
    navio(ctx, W / 2 + 120, MAR - 60, 0.75, 0.25 * ease(t / 4.0), 40 * ease(t / 4.0), 1 - 0.7 * ease(t / 4.0), t)
    for i in range(20):   # 20 botes, na linha do mar
        x = 70 + (i % 10) * 50 + 8 * math.sin(t + i)
        y = MAR - 30 + (i // 10) * 22
        ctx.set_source_rgb(0.9, 0.9, 0.85)
        ctx.rectangle(x, y, 38, 12)
        ctx.fill()
    caixa(ctx, "20 LIFEBOATS", "ROOM FOR ABOUT 1,178 PEOPLE", YELLOW)


def d_fim(ctx, t, s):
    ceu(ctx, t)
    mar(ctx, t)
    k = ease(t / 3.0)
    navio(ctx, W / 2, MAR - 30, 0.9, 0.25 + 0.6 * k, 40 + 500 * k, 0.0, t)
    mar(ctx, t)
    if t > 1.5:
        caixa(ctx, "2:20 AM", "ABOUT 1,500 PEOPLE LOST", WHITE)


SEGMENTS = [
    Seg(["In 1912, the biggest ship in the world set sail.", "People called it unsinkable."], d_gancho,
        {"title": "WHY DID THE TITANIC SINK?"}, tail=0.2),
    Seg(["Its hull was split into sixteen sealed compartments. Four could flood, and it would still float."],
        d_comp, {"big": "THE SAFETY PLAN", "color": GREEN}, tail=0.2),
    Seg(["Then, near midnight, the lookouts saw an iceberg. Less than a minute away."], d_iceberg,
        {"big": "ICEBERG", "color": PINK}, tail=0.3, sfx=[(0, 2.4, "whoosh")]),
    Seg(["The ice sliced along the side. Not four compartments flooded. Six."], d_alaga,
        {"big": "SIX", "color": PINK}, tail=0.3),
    Seg(["And the walls between them didn't reach the top. As the front sank, water spilled into the next one, and the next."],
        d_bandeja, {"big": "THE FATAL FLAW", "big_size": 90, "color": (0.4, 0.7, 1.0)}, tail=0.2),
    Seg(["There were only twenty lifeboats, enough for about half the people on board."], d_botes,
        {"big": "NOT ENOUGH", "color": YELLOW}, tail=0.2),
    Seg(["Two hours and forty minutes after the crash, the unsinkable ship was gone."], d_fim,
        {"big": "GONE", "color": WHITE}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("What would have saved the Titanic?", "WHAT COULD HAVE SAVED IT?",
                                fundo=lambda ctx, t, s: (ceu(ctx, t), mar(ctx, t))))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
