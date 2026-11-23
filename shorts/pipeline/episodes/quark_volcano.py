"""What if you fell into a volcano? Thu 12/11/2026, topic: Earth & physics, format: what if with the mascot Quark
(conflict arc). Search 12/11: "what if you fell into a volcano", median 16k ("Why lava won't let you sink" 30k).

Facts:
- molten basaltic lava has a density of about 2.6-3.0 g/cm3, while a human body is about 1.0 g/cm3 (like water), so
  you would not sink into it: you would float on it, like a ball on water;
- lava is about 700-1,200 C; its radiant heat burns skin from meters away, long before touching it;
- volcanic gases (sulfur dioxide, carbon dioxide) near a vent are a danger of their own;
- the cooled crust on a lava lake cracks into plates that glow at the seams.
Quark never really gets hurt: the danger turns into a joke and he escapes.
Arc: hook (Quark slips at the rim) -> rising (the fall) -> conflict (he doesn't sink!) -> proof (density bars) ->
twist (the heat is the real problem) -> payoff (hot-coal escape) -> question.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, round_rect, text_center  # noqa: E402

LAGO = 1240     # superfície do lago de lava
QH = 460


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ceu(ctx):
    import cairo
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.18, 0.08, 0.10)
    g.add_color_stop_rgb(0.6, 0.55, 0.20, 0.10)
    g.add_color_stop_rgb(1, 0.9, 0.45, 0.1)
    ctx.set_source(g)
    ctx.paint()


def lava(ctx, t, y=LAGO):
    import cairo
    g = cairo.LinearGradient(0, y, 0, H)
    g.add_color_stop_rgb(0, 1.0, 0.55, 0.1)
    g.add_color_stop_rgb(1, 0.85, 0.15, 0.02)
    ctx.rectangle(0, y, W, H - y)
    ctx.set_source(g)
    ctx.fill()
    ctx.set_source_rgba(0.25, 0.08, 0.04, 0.85)  # placas de crosta escura com as fendas brilhando
    for i in range(9):
        x = (i * 157 + t * 20) % (W + 200) - 100
        yy = y + 30 + (i * 53) % 140
        ctx.save()
        ctx.translate(x, yy)
        ctx.scale(1, 0.35)
        ctx.arc(0, 0, 70 + (i % 3) * 20, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()
    for i in range(6):  # bolhas
        ph = (t * 0.7 + i * 0.17) % 1
        ctx.set_source_rgba(1, 0.85, 0.3, 1 - ph)
        ctx.arc((i * 211) % W, y + 6 - ph * 30, 10 + ph * 14, 0, 2 * math.pi)
        ctx.fill()


def paredes(ctx, borda=True):
    ctx.set_source_rgb(0.16, 0.12, 0.12)
    ctx.move_to(0, 380)
    ctx.line_to(200, 520)
    ctx.line_to(120, 900)
    ctx.line_to(60, LAGO)
    ctx.line_to(0, LAGO)
    ctx.close_path()
    ctx.fill()
    ctx.move_to(W, 360)
    ctx.line_to(860, 560)
    ctx.line_to(960, 950)
    ctx.line_to(1010, LAGO)
    ctx.line_to(W, LAGO)
    ctx.close_path()
    ctx.fill()


def d_gancho(ctx, t, s):
    """Na borda da cratera, o Quark escorrega e cai."""
    ceu(ctx)
    lava(ctx, t, 1500)
    ctx.set_source_rgb(0.2, 0.15, 0.14)  # borda
    ctx.move_to(0, 1240)
    ctx.line_to(620, 1240)
    ctx.line_to(700, 1400)
    ctx.line_to(0, 1400)
    ctx.close_path()
    ctx.fill()
    if t < 1.6:
        p = pq.Pose(expr="feliz", boca=pq.boca_da_voz(s, t), andar=t * 1.4, braco_d=1.2)
        pq.quark(ctx, 260 + 160 * t, 1240, QH, p, t)
    else:
        k = t - 1.6
        p = pq.Pose(expr="surpreso", boca=pq.boca_da_voz(s, t), braco_e=2.8, braco_d=2.8, pulo=0.6,
                    inclina=0.6 * min(1.0, k * 2))
        pq.quark(ctx, 516 + 200 * k, 1240 + 900 * k * k, QH, p, t)


def d_queda(ctx, t, s):
    ceu(ctx)
    paredes(ctx)
    lava(ctx, t)
    y = 520 + 720 * ease(t / (s.dur - 0.4))
    p = pq.Pose(expr="medo", boca=pq.boca_da_voz(s, t), braco_e=2.9, braco_d=2.9, pulo=0.7, suor=True,
                inclina=0.2 * math.sin(t * 4))
    pq.quark(ctx, 540, min(y, LAGO), QH, p, t)


def d_flutua(ctx, t, s):
    """Ele bate na lava e não afunda: quica e fica boiando, como uma bola na água."""
    ceu(ctx)
    paredes(ctx)
    lava(ctx, t)
    quique = abs(math.sin(t * 5)) * 80 * math.exp(-t * 1.6)
    p = pq.Pose(expr="surpreso" if t < 1.2 else "pensando", boca=pq.boca_da_voz(s, t), squash=1 - 0.15 * math.exp(-t * 4),
                braco_e=1.8, braco_d=1.8)
    pq.quark(ctx, 540, LAGO + 30 - quique, QH, p, t)
    lava(ctx, t, LAGO + 30)  # a lava cobre só os pés


def d_densidade(ctx, t, s):
    ceu(ctx)
    lava(ctx, t, 1350)
    round_rect(ctx, 110, 470, 860, 520, 30)
    ctx.set_source_rgba(0.05, 0.04, 0.06, 0.85)
    ctx.fill()
    text_center(ctx, "DENSITY (g/cm³)", 540, 540, 36, WHITE, "ExtraBold")
    for i, (rot, val, cor) in enumerate((("WATER", 1.0, (0.3, 0.6, 1.0)), ("YOU", 1.0, (1.0, 0.85, 0.25)),
                                         ("LAVA", 2.8, (1.0, 0.45, 0.1)))):
        k = ease((t - 0.3 - i * 0.4) / 0.7)
        x = 250 + i * 290
        h = 140 * val * k
        round_rect(ctx, x - 60, 940 - h, 120, h, 12)
        ctx.set_source_rgb(*cor)
        ctx.fill()
        text_center(ctx, f"{val:.1f}", x, 925 - h, 34, WHITE, "ExtraBold", alpha=k)
        text_center(ctx, rot, x, 975, 28, WHITE, "Bold")
    p = pq.Pose(expr="feliz", boca=pq.boca_da_voz(s, t), braco_d=2.0)
    pq.quark(ctx, 870, 1380, 300, p, t)


def d_calor(ctx, t, s):
    ceu(ctx)
    paredes(ctx)
    lava(ctx, t)
    p = pq.Pose(expr="medo", boca=pq.boca_da_voz(s, t), suor=True, braco_e=2.6, braco_d=2.6,
                squash=1 - 0.03 * abs(math.sin(t * 25)))
    pq.quark(ctx, 540, LAGO + 30, QH, p, t)
    lava(ctx, t, LAGO + 30)
    for i in range(10):  # fumaça dos tênis
        ph = (t * 0.8 + i * 0.1) % 1
        ctx.set_source_rgba(0.75, 0.75, 0.75, 0.6 * (1 - ph))
        ctx.arc(470 + (i % 5) * 35 + 20 * math.sin(i + t), LAGO + 10 - ph * 260, 16 + ph * 26, 0, 2 * math.pi)
        ctx.fill()
    round_rect(ctx, 270, 470, 540, 130, 26)
    ctx.set_source_rgba(0.05, 0.04, 0.06, 0.8)
    ctx.fill()
    text_center(ctx, "1,100 °C", 540, 532, 56, YELLOW, "ExtraBold")
    text_center(ctx, "2,000 °F", 540, 580, 30, WHITE, "Bold")


def d_fuga(ctx, t, s):
    """Pulando como em brasa, ele chega na parede e sobe."""
    ceu(ctx)
    paredes(ctx)
    lava(ctx, t)
    x = 540 + 380 * ease(t / 2.2)
    hop = abs(math.sin(t * 9)) * 90
    y = LAGO + 10 - hop if t < 2.2 else LAGO - 300 * ease((t - 2.2) / 0.8)
    p = pq.Pose(expr="rindo", boca=pq.boca_da_voz(s, t), andar=t * 4, corrida=True, braco_e=2.6, braco_d=2.6)
    pq.quark(ctx, min(x, 900), y, QH, p, t)


SEGMENTS = [
    Seg(["Whoa, whoa! What if I fell into a volcano?"], d_gancho, {"title": "FALL INTO A VOLCANO?"}, tail=0.1),
    Seg(["I'm heading straight for a lake of melted rock!"], d_queda, {"big": "LAVA LAKE", "color": (1.0, 0.55, 0.15)},
        tail=0.1, sfx=[(0, 0, "whoosh")]),
    Seg(["Wait... I'm not sinking? I'm just bouncing on it!"], d_flutua,
        {"big": "I DON'T SINK?", "color": PINK}, tail=0.3),
    Seg(["Lava is almost three times denser than you. You'd float on it, like a ball on water."], d_densidade,
        {"big": "TOO DENSE", "sub": "YOU FLOAT ON LAVA", "color": YELLOW}, tail=0.2),
    Seg(["But it's over a thousand degrees. The heat would burn you long before you touched it."], d_calor,
        {"big": "THE REAL DANGER", "big_size": 88, "sub": "HEAT, NOT SINKING", "color": PINK}, tail=0.2),
    Seg(["Good thing I'm a cartoon. Hot, hot, hot, hot! I'm out of here!"], d_fuga,
        {"big": "HOT HOT HOT", "color": GREEN}, tail=0.4),
]
SEGMENTS.append(pq.seg_pergunta("Would you get this close to lava?", "WOULD YOU GET THIS CLOSE?",
                                fundo=lambda ctx, t, s: (ceu(ctx), paredes(ctx), lava(ctx, t))))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
