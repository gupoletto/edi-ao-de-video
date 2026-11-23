"""Stare at this spiral, then look at Quark (motion aftereffect). Mon 16/11/2026, topic: optical illusions, format:
what if with the mascot Quark ("what if you stared at a spiral?"). Search 16/11: "this illusion will make you",
median 37k (top 778k: "Do the objects around you look like they're getting closer?").

Facts:
- the motion aftereffect (the "waterfall illusion", described by Robert Addams in 1834): after staring at continuous
  motion for several seconds, a still image seems to move the opposite way;
- an inward-moving (contracting) spiral leaves an aftereffect of expansion: still things seem to swell or come closer;
- explanation: motion-sensitive neurons tuned to the adapted direction get fatigued, so the balance with neurons for
  the opposite direction tips the other way for a few seconds.
The spiral turns and contracts for ~11 s before Quark appears perfectly still.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
from core import GREEN, H, PINK, W, WHITE, YELLOW, Seg, render, text_center  # noqa: E402

CX, CY = W / 2, 860


def espiral(ctx, t):
    ctx.set_source_rgb(0.98, 0.97, 0.94)
    ctx.paint()
    ctx.set_source_rgb(0.06, 0.06, 0.08)
    n = 8
    fase = t * 2.2          # gira
    enc = (t * 0.9) % 1.0   # contrai (as faixas andam para o centro)
    for k in range(n):   # braços de largura angular constante (metade de cada setor), girando e "entrando"
        a0 = fase + k * 2 * math.pi / n
        ctx.new_path()
        for j in range(160):
            r = 12 + (j / 159) * 900
            a = a0 + math.log(r / 12) * 1.1 + enc * 2 * math.pi / n
            ctx.line_to(CX + r * math.cos(a), CY + r * math.sin(a))
        for j in range(159, -1, -1):
            r = 12 + (j / 159) * 900
            a = a0 + math.pi / n + math.log(r / 12) * 1.1 + enc * 2 * math.pi / n
            ctx.line_to(CX + r * math.cos(a), CY + r * math.sin(a))
        ctx.close_path()
        ctx.fill()
    ctx.set_source_rgba(0.04, 0.04, 0.07, 0.92)   # faixa escura atrás do cabeçalho
    ctx.rectangle(0, 0, W, 330)
    ctx.fill()
    ctx.set_source_rgb(0.9, 0.15, 0.2)
    ctx.arc(CX, CY, 16, 0, 2 * math.pi)
    ctx.fill()


def fundo_neutro(ctx):
    ctx.set_source_rgb(0.95, 0.94, 0.90)
    ctx.paint()
    ctx.set_source_rgba(0, 0, 0, 0.06)
    for x in range(0, W, 60):
        ctx.rectangle(x, 0, 2, H)
    for y in range(0, H, 60):
        ctx.rectangle(0, y, W, 2)
    ctx.fill()


def d_espiral(ctx, t, s, t0=0.0):
    espiral(ctx, t + t0)


def d_conta(ctx, t, s):
    espiral(ctx, t + 6.3)
    resta = max(0.0, s.dur - t)
    text_center(ctx, f"{resta:.0f}", CX, 285, 64, (1.0, 0.85, 0.25), "ExtraBold")


def d_olha(ctx, t, s):
    fundo_neutro(ctx)
    p = pq.Pose(expr="surpreso", boca=pq.boca_da_voz(s, t), piscar=0.0, braco_e=0.25, braco_d=0.25)
    pq.quark(ctx, CX, 1260, 640, p, 0.0)   # tempo congelado: ele não se mexe nem respira


def d_explica(ctx, t, s):
    fundo_neutro(ctx)
    for k in range(3):   # neurônios "cansados"
        x = 300 + k * 240
        ctx.set_source_rgb(0.85, 0.55, 0.95)
        ctx.arc(x, 640, 50, 0, 2 * math.pi)
        ctx.fill()
        text_center(ctx, "z", x + 50, 590 - 10 * math.sin(t * 3 + k), 40, (0.4, 0.3, 0.6), "ExtraBold")
    text_center(ctx, "MOTION NEURONS: TIRED", CX, 760, 36, (0.4, 0.3, 0.6), "ExtraBold")
    p = pq.Pose(expr="pensando", boca=pq.boca_da_voz(s, t), braco_d=1.6)
    pq.quark(ctx, CX, 1260, 470, p, t)


def d_mao(ctx, t, s):
    fundo_neutro(ctx)
    p = pq.Pose(expr="rindo", boca=pq.boca_da_voz(s, t), braco_e=2.6, braco_d=2.6)
    pq.quark(ctx, CX, 1260, 500, p, t)


SEGMENTS = [
    Seg(["Stare at the red dot in the middle, and don't look away. Something weird is about to happen to me."],
        d_espiral, {"title": "STARE AT THE RED DOT"}, tail=0.2),
    Seg(["Keep staring. Almost there."], d_conta, {"title": "KEEP STARING"}, tail=2.6),
    Seg(["Now look at me! Am I growing? I'm not moving at all."], d_olha, {"big": "LOOK AT ME", "color": PINK},
        tail=0.8, sfx=[(0, 0, "whoosh")]),
    Seg(["The motion cells in your brain got tired of the spiral, so still things seem to move the other way."],
        d_explica, {"big": "TIRED NEURONS", "sub": "MOTION AFTEREFFECT", "color": YELLOW}, tail=0.2),
    Seg(["Watch it again, then look at your hand. It'll swell up too."], d_mao,
        {"big": "TRY YOUR HAND", "color": GREEN}, tail=0.3),
]
SEGMENTS.append(pq.seg_pergunta("Did my face move for you?", "DID MY FACE MOVE?",
                                fundo=lambda ctx, t, s: fundo_neutro(ctx)))

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1])
