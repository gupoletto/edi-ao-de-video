"""What if Earth was actually flat? Tue 17/11/2026, topic: physics simulations (gravity), format: what if with the
mascot Quark (conflict arc). Search 17/11: "what if gravity" median 25.7k (top 1.56M "What if the Earth was actually
flat?").

Physics (a thin disk with Earth's mass, as in the classic thought experiment, e.g. Anders Sandberg 2014):
- gravity points toward the center of mass, so on a disk it points down only at the center; walking toward the rim,
  it tilts more and more toward the middle: the flat ground feels like a steeper and steeper hill;
- loose water and air flow downhill toward the center: one giant ocean dome in the middle, dry and airless near the
  rim;
- a disk this size is not stable: gravity would pull it back into a ball (anything larger than a few hundred km
  across collapses into a sphere), which is why planets are round.
Quark never really gets hurt: he slides back to the center comically.
Arc: hook (Quark at the center) -> rising (walks to the rim) -> conflict (the ground "tilts", he slides) -> proof
(gravity arrows) -> twist (the ocean piles up in the middle) -> payoff (it collapses into a ball) -> question.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

QH = 420


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ceu(ctx):
    ctx.set_source_rgb(0.03, 0.03, 0.08)
    ctx.paint()
    ctx.set_source_rgba(1, 1, 1, 0.7)
    for i in range(90):
        ctx.arc((i * 397) % W, (i * 211) % H, 1.3 + (i % 3) * 0.6, 0, 2 * math.pi)
        ctx.fill()


def disco(ctx, cx, cy, r, inc=0.22, oceano=0.0, bola=0.0):
    """Disco visto de lado em perspectiva (elipse); bola 0..1 transforma em esfera."""
    import cairo
    ry = r * (inc + (1 - inc) * bola)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(1, ry / r)
    g = cairo.RadialGradient(0, 0, r * 0.1, 0, 0, r)
    g.add_color_stop_rgb(0, 0.30, 0.62, 0.32)
    g.add_color_stop_rgb(1, 0.55, 0.45, 0.30)
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill()
    if oceano > 0:
        ctx.arc(0, 0, r * 0.55 * oceano, 0, 2 * math.pi)
        ctx.set_source_rgb(0.15, 0.40, 0.85)
        ctx.fill()
    ctx.restore()
    if bola < 0.5:   # espessura da borda
        ctx.set_source_rgb(0.40, 0.30, 0.22)
        ctx.rectangle(cx - r, cy, 2 * r, 30 * (1 - 2 * bola))
        ctx.fill()


def caixa(ctx, l1, l2, cor, y=560):
    round_rect(ctx, 200, y - 56, 680, 136, 26)
    ctx.set_source_rgba(0.04, 0.05, 0.09, 0.8)
    ctx.fill()
    text_center(ctx, l1, W / 2, y, 50, cor, "ExtraBold")
    text_center(ctx, l2, W / 2, y + 56, 28, WHITE, "Bold")


def chao_inclinado(ctx, ang, t):
    """Visão de perto: o chão plano, mas a "vertical" (gravidade) inclinada de ang: desenhamos o mundo girado."""
    import cairo
    ctx.save()
    ctx.translate(W / 2, 1240)
    ctx.rotate(-ang)
    g = cairo.LinearGradient(0, -1300, 0, 0)
    g.add_color_stop_rgb(0, 0.10, 0.12, 0.25)
    g.add_color_stop_rgb(1, 0.45, 0.62, 0.90)
    ctx.rectangle(-1400, -1500, 2800, 1500)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgb(0.55, 0.45, 0.30)
    ctx.rectangle(-1400, 0, 2800, 900)
    ctx.fill()
    ctx.restore()


def d_gancho(ctx, t, s):
    ceu(ctx)
    disco(ctx, W / 2, 1080, 470)
    p = pq.Pose(expr="feliz", boca=pq.boca_da_voz(s, t), braco_d=1.8)
    pq.quark(ctx, W / 2, 1060, 260, p, t)
    text_center(ctx, "CENTER", W / 2, 1200, 30, WHITE, "Bold")


def d_anda(ctx, t, s):
    k = ease(t / (s.dur - 0.3))
    chao_inclinado(ctx, 0.75 * k, t)
    p = pq.Pose(expr="determinado" if k < 0.6 else "surpreso", boca=pq.boca_da_voz(s, t), andar=t * 1.6,
                inclina=0.75 * k * 0.6, suor=k > 0.6)
    pq.quark(ctx, W / 2, 1240, QH, p, t)
    caixa(ctx, f"{45 * k:.0f}° SLOPE", "THE GROUND IS FLAT. GRAVITY ISN'T.", YELLOW)


def d_escorrega(ctx, t, s):
    chao_inclinado(ctx, 0.75, t)
    p = pq.Pose(expr="medo", boca=pq.boca_da_voz(s, t), braco_e=2.9, braco_d=2.9, inclina=0.9, suor=True,
                squash=0.9)
    pq.quark(ctx, W / 2 - 260 * ease(t / 2.0), 1240, QH, p, t)


def d_setas(ctx, t, s):
    ceu(ctx)
    disco(ctx, W / 2, 900, 470)
    for k in range(9):   # setas de gravidade apontando para o centro de massa
        x = W / 2 - 400 + k * 100
        dx, dy = (W / 2 - x), 140
        n = math.hypot(dx, dy)
        x0, y0 = x, 800
        x1, y1 = x0 + dx / n * 110, y0 + dy / n * 110
        ctx.set_source_rgb(1.0, 0.85, 0.25)
        ctx.set_line_width(8)
        ctx.move_to(x0, y0)
        ctx.line_to(x1, y1)
        ctx.stroke()
        ctx.arc(x1, y1, 10, 0, 2 * math.pi)
        ctx.fill()
    caixa(ctx, "GRAVITY POINTS", "TO THE CENTER OF THE DISK", YELLOW)


def d_oceano(ctx, t, s):
    ceu(ctx)
    disco(ctx, W / 2, 900, 470, oceano=ease(t / 2.0))
    caixa(ctx, "ONE GIANT OCEAN", "WATER AND AIR POOL IN THE MIDDLE", (0.4, 0.7, 1.0))


def d_bola(ctx, t, s):
    ceu(ctx)
    k = ease((t - 0.3) / 2.2)
    disco(ctx, W / 2, 900, 470 - 140 * k, bola=k)
    p = pq.Pose(expr="rindo" if k > 0.8 else "surpreso", boca=pq.boca_da_voz(s, t), braco_e=2.4, braco_d=2.4)
    pq.quark(ctx, W / 2 + 300, 1250, 300, p, t)


SEGMENTS = [
    Seg(["What if Earth was actually flat? I'm standing right at the center, and everything feels normal."], d_gancho,
        {"title": "WHAT IF EARTH WAS FLAT?"}, tail=0.1),
    Seg(["But as I walk toward the edge, the flat ground starts feeling like a hill."], d_anda,
        {"big": "UPHILL?", "color": YELLOW}, tail=0.1),
    Seg(["Whoa, it's too steep! I'm sliding back!"], d_escorrega, {"big": "TOO STEEP", "color": PINK}, tail=0.3),
    Seg(["Gravity pulls toward the middle of all that mass, so near the edge it pulls sideways."], d_setas,
        {"big": "SIDEWAYS GRAVITY", "big_size": 84, "color": YELLOW}, tail=0.2),
    Seg(["The oceans and the air would slide to the center, into one giant dome."], d_oceano,
        {"big": "OCEAN DOME", "color": (0.4, 0.7, 1.0)}, tail=0.2),
    Seg(["And then gravity would crush the whole disk back into a ball. That's why planets are round!"], d_bola,
        {"big": "BACK TO A BALL", "big_size": 88, "color": GREEN}, tail=0.4, sfx=[(0, 0.3, "ding")]),
]
SEGMENTS.append(pq.seg_pergunta("Would you live at the center or the edge?", "CENTER OR EDGE?",
                                fundo=lambda ctx, t, s: (ceu(ctx), disco(ctx, W / 2, 1000, 470, oceano=1.0))))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
