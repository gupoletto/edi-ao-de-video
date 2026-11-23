"""15 pendulums, each a little longer: wait for it (cinematic 3D, pendulum wave). Tue 17/11/2026, topic: physics
simulations. Search 17/11: "physics simulation" median 1.14M; "pendulum wave" 13.8k (top 39k "24 pendulums, each a
bit shorter").

Physics (computed below): small-angle pendulum, period T = 2 pi sqrt(L / g). Pendulum n (n = 0..14) makes exactly
20 + n swings in 30 s, so T_n = 30 / (20 + n) and L_n = g (T_n / 2 pi)^2 (from ~55 cm down to ~23 cm). Released
together, they drift out of phase into waves, then look random, then line up perfectly again at 30 s. At 15 s they
form two opposite rows (each has made a whole or a half number of swings).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import GREEN, PINK, WHITE, YELLOW, Seg, render, text_center  # noqa: E402

N, CICLO, G = 15, 30.0, 9.81
T = [CICLO / (20 + n) for n in range(N)]
L = [G * (t / (2 * math.pi)) ** 2 for t in T]
A0 = 0.32
T_SOLTA = 1.2   # instante do vídeo em que eles são soltos


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def solta(segs):
    return segs[5].t0 + 0.8 - CICLO   # o alinhamento cai junto com "Thirty seconds"


def estado(t, segs):
    tau = max(0.0, t - solta(segs))
    ang = [A0 * math.cos(2 * math.pi * tau / T[n]) for n in range(N)]
    a = 0.12 * math.sin(t * 0.18)          # vista em diagonal da fileira, balançando de leve
    cam = [1.0 + 1.5 * a, 3.9, 4.4]
    return {"cam": cam, "alvo": [0, 1.8, -0.3], "fov": 44, "t": t, "ang": ang, "L": L}


FILME = tres.Filme("pendulos.js", estado)
SEGS = []


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)
    if not SEGS:
        return
    tt = s.t0 + t - solta(SEGS)
    if 0 < tt < CICLO + 1.5:
        text_center(ctx, f"{min(CICLO, tt):04.1f} s", 540, 1235, 46, YELLOW, "ExtraBold")


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["Fifteen pendulums, each a little shorter than the last. Watch what they do in thirty seconds."],
        {"title": "15 PENDULUMS: WAIT FOR IT"}, tail=0.2),
    seg(["Shorter ones swing faster, so they drift apart into a snake."],
        {"big": "THE SNAKE", "color": YELLOW}, tail=2.2),
    seg(["Now it looks like total chaos."], {"big": "CHAOS?", "color": PINK}, tail=2.8),
    seg(["But every pendulum was tuned to swing a whole number of times in thirty seconds."],
        {"big": "TUNED", "sub": "20, 21, 22 … 34 SWINGS", "color": WHITE}, tail=2.0),
    seg(["Two rows, then waves again, and here it comes."], {"big": "ALMOST…", "color": YELLOW}, tail=2.2),
    seg(["Thirty seconds. Perfectly lined up again."], {"big": "LINED UP!", "color": GREEN}, tail=1.5,
        sfx=[(0, 0.6, "ding")]),
]
SEGMENTS.append(pq.seg_pergunta("Did you wait for the end?", "DID YOU WAIT FOR IT?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    SEGS[:] = segs
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
