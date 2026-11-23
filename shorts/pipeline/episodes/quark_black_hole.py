"""What if you fell into a black hole? Wed 18/11/2026, topic: space, format: what if with the mascot Quark (conflict
arc). Search 18/11: "what if you fell into a black hole", median 2.2k (top 185k); space is #6 in the week ranking.

Facts:
- near a stellar-mass black hole (a few to tens of Suns) the difference in gravity between your head and your feet
  (tidal force) is enormous: you get stretched thin before you even reach the event horizon ("spaghettification");
- near a supermassive one (millions of Suns), the tides at the horizon are gentle: you could cross it without feeling
  anything special;
- a faraway friend watching you would see you slow down, redden and fade at the horizon (gravitational time dilation
  and redshift); from your own point of view you cross it in finite time;
- once inside the event horizon, every path leads inward; not even light can escape.
Quark never really gets hurt: he gets stretched like a noodle and snaps back as a joke.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

CX, CY = W / 2, 900


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def espaco(ctx):
    ctx.set_source_rgb(0.01, 0.01, 0.03)
    ctx.paint()
    ctx.set_source_rgba(1, 1, 1, 0.7)
    for i in range(110):
        ctx.arc((i * 397) % W, (i * 211) % H, 1.2 + (i % 3) * 0.6, 0, 2 * math.pi)
        ctx.fill()


def buraco(ctx, r, t):
    import cairo
    for k in range(18):   # disco de acreção
        a = t * 0.8 + k * 0.35
        ctx.save()
        ctx.translate(CX, CY)
        ctx.scale(1, 0.28)
        ctx.set_source_rgba(1.0, 0.55 + 0.3 * (k % 3) / 2, 0.15, 0.35)
        ctx.set_line_width(14)
        ctx.arc(0, 0, r * (1.5 + k * 0.08), a, a + 2.4)
        ctx.stroke()
        ctx.restore()
    g = cairo.RadialGradient(CX, CY, r * 0.9, CX, CY, r * 1.25)
    g.add_color_stop_rgba(0, 1, 0.75, 0.4, 0.9)
    g.add_color_stop_rgba(1, 1, 0.5, 0.2, 0.0)
    ctx.arc(CX, CY, r * 1.25, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgb(0, 0, 0)
    ctx.arc(CX, CY, r, 0, 2 * math.pi)
    ctx.fill()


def caixa(ctx, l1, l2, cor, y=560):
    round_rect(ctx, 200, y - 56, 680, 136, 26)
    ctx.set_source_rgba(0.04, 0.05, 0.09, 0.8)
    ctx.fill()
    text_center(ctx, l1, W / 2, y, 50, cor, "ExtraBold")
    text_center(ctx, l2, W / 2, y + 56, 28, WHITE, "Bold")


def d_gancho(ctx, t, s):
    espaco(ctx)
    buraco(ctx, 160, t)
    y = 1250 - 220 * ease(t / 5.0)
    p = pq.Pose(expr="determinado", boca=pq.boca_da_voz(s, t), braco_d=2.4, capacete=True, pulo=0.5)
    pq.quark(ctx, CX + 240, y, 320, p, t)


def d_estica(ctx, t, s):
    espaco(ctx)
    buraco(ctx, 180, t)
    k = ease(t / 2.5)
    p = pq.Pose(expr="medo" if k > 0.3 else "surpreso", boca=pq.boca_da_voz(s, t), squash=1 + 1.6 * k,
                braco_e=2.9, braco_d=2.9, capacete=True, suor=True)
    pq.quark(ctx, CX + 200, 1250, 260, p, t)
    caixa(ctx, "SPAGHETTIFIED", "YOUR FEET PULLED HARDER THAN YOUR HEAD", PINK)


def d_grande(ctx, t, s):
    espaco(ctx)
    buraco(ctx, 420, t * 0.3)
    p = pq.Pose(expr="feliz", boca=pq.boca_da_voz(s, t), braco_e=1.2, braco_d=1.2, capacete=True)
    pq.quark(ctx, CX + 300, 1250 + 20 * math.sin(t), 260, p, t)
    caixa(ctx, "SUPERMASSIVE", "GENTLE TIDES AT THE EDGE", GREEN)


def d_amigo(ctx, t, s):
    espaco(ctx)
    buraco(ctx, 300, t * 0.3)
    k = ease(t / 3.5)
    p = pq.Pose(expr="feliz", braco_d=2.2, capacete=True, piscar=0.0)
    ctx.push_group()
    pq.quark(ctx, CX + 300, CY - 150, 200 * (1 - 0.3 * k), p, 0.0)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(1 - 0.85 * k)
    ctx.set_source_rgba(0.8, 0.1, 0.05, 0.5 * k)   # avermelhando
    ctx.arc(CX + 300, CY - 250, 120, 0, 2 * math.pi)
    ctx.fill()
    caixa(ctx, "FROZEN IN TIME", "WHAT YOUR FRIEND WOULD SEE", YELLOW)


def d_dentro(ctx, t, s):
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    for k in range(12):   # todos os caminhos apontam para o centro
        a = k * math.pi / 6 + t * 0.2
        ctx.set_source_rgba(1, 0.6, 0.2, 0.5)
        ctx.set_line_width(5)
        ctx.move_to(CX + 420 * math.cos(a), CY + 420 * math.sin(a))
        ctx.line_to(CX + 120 * math.cos(a), CY + 120 * math.sin(a))
        ctx.stroke()
    p = pq.Pose(expr="pensando", boca=pq.boca_da_voz(s, t), capacete=True, braco_d=1.6)
    pq.quark(ctx, CX, CY + 230, 300, p, t)


SEGMENTS = [
    Seg(["What if I fell into a black hole? I'm about to find out, the hard way."], d_gancho,
        {"title": "FALL INTO A BLACK HOLE?"}, tail=0.1),
    Seg(["A small one would stretch me like spaghetti, because gravity pulls my feet way harder than my head!"],
        d_estica, {"big": "STRETCHED", "color": PINK}, tail=0.2),
    Seg(["But a giant one, millions of Suns heavy, is gentle at the edge. I'd cross without feeling a thing."],
        d_grande, {"big": "THE BIG ONE", "color": GREEN}, tail=0.2),
    Seg(["To a friend far away, I'd slow down, turn red, and freeze at the edge forever."], d_amigo,
        {"big": "FROZEN?", "color": YELLOW}, tail=0.3),
    Seg(["And inside, every direction points to the center. Not even light gets out."], d_dentro,
        {"big": "NO WAY OUT", "color": PINK}, tail=0.4),
]
SEGMENTS.append(pq.seg_pergunta("Big black hole or small one, pick!", "BIG OR SMALL?",
                                fundo=lambda ctx, t, s: (espaco(ctx), buraco(ctx, 160, t))))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
