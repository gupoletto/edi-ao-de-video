"""What happens when a tsunami hits the coast? (cinematic 3D, shoaling and drawback). Sun 15/11/2026, topic: Earth &
nature. Search 15/11: "tsunami simulation", median 261k.

Shots: a low, fast wave crossing the open ocean under a ship -> it reaches shallow water, slows down and grows ->
the sea pulls back and the beach drains (drawback) -> a wall of water runs up into the town -> wide shot with the
safety rule -> Quark asks the question.

Facts:
- in the deep ocean a tsunami travels at roughly 700-800 km/h (speed = sqrt(g x depth)) and is usually less than a
  meter tall, so ships at sea barely notice it;
- as the water gets shallower the wave slows (to tens of km/h) and its height grows (Green's law: height ~ depth^-1/4,
  plus the wave bunching up), reaching several to more than 10 m at the coast;
- often the trough arrives first and the sea recedes far from the beach (the drawback): a natural warning sign;
- official advice: if the sea suddenly pulls back or you feel a strong earthquake on the coast, go to high ground
  immediately.
Visual scale: horizontal distances and depths are compressed to fit the shot; the wave's speed follows sqrt(depth)
along the profile (integrated below) and its height follows Green's law, capped near the shore.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import GREEN, PINK, WHITE, YELLOW, Seg, render  # noqa: E402

NS, X0, DX = 260, -2600.0, 11.0
XS = X0 + DX * np.arange(NS)


def chao(x):
    if x < -1400:
        return -60.0
    if x < -120:
        return -60 + 58 * (x + 1400) / 1280
    if x < 60:
        return -2 + 5 * (x + 120) / 180
    return 3 + max(0.0, (x - 400) * 0.08)


CHAO = np.array([chao(x) for x in XS])


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mistura(a, b, k):
    return [x + (y - x) * k for x, y in zip(a, b)]


def seg_de(t, segs):
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    return k, t - segs[k].t0


_C = {}


def trajeto(segs):
    """Posição do centro da onda no tempo do vídeo: dx/dt = k sqrt(g h(x)), escalado para chegar à praia no seg 4."""
    chave = tuple(round(s.t0, 3) for s in segs)
    if chave in _C:
        return _C[chave]
    dt = 1 / 240
    xs, x = [], -2300.0
    while x < 40:
        xs.append(x)
        h = max(1.5, -chao(x))
        x += math.sqrt(9.81 * h) * dt
    bruto = np.arange(len(xs)) * dt
    t_ini, t_praia = 0.2, segs[4].t0 + 0.6
    tempos = t_ini + bruto * (t_praia - t_ini) / bruto[-1]
    _C[chave] = (tempos, np.array(xs))
    return _C[chave]


def centro(t, segs):
    ts, xs = trajeto(segs)
    if t <= ts[-1]:
        return float(np.interp(t, ts, xs)), False
    return 40 + 30 * (t - ts[-1]), True     # sobe pela terra devagar


def eta(t, segs):
    X, terra = centro(t, segs)
    h = max(1.5, -chao(min(X, 0)))
    A = min(12.0, 1.2 * (60 / h) ** 0.25 * (1 + 6 * max(0.0, (300 - (0 - X)) / 300) ** 2))   # Green + amontoamento
    w = 25 + 140 * math.sqrt(h / 60)       # o comprimento encurta com a velocidade
    xi = XS - X
    e = A * np.exp(-((xi + w) / w) ** 2) - 0.7 * A * np.exp(-((xi - 1.3 * w) / (1.3 * w)) ** 2)
    if terra:   # a água avança por cima da terra e vai perdendo altura
        frente = X + 40
        e = np.where(XS < frente, np.maximum(e, CHAO + 4.0 * np.exp(-(t % 100) * 0)), e)
    sup = np.maximum(e, CHAO - 0.5)
    sup = np.where((CHAO > 0) & (e < CHAO + 0.05), CHAO - 0.6, sup)  # terra seca: água escondida embaixo
    return sup, X, A


def estado(t, segs):
    k, lt = seg_de(t, segs)
    sup, X, A = eta(t, segs)
    xn = -1700.0
    i = int((xn - X0) / DX)
    navio = [xn, float(sup[i]) + 1.0, float((sup[i + 2] - sup[i - 2]) / (4 * DX))]
    if k == 0:
        q = ease(lt / 5.0)
        cam = mistura([X - 380, 160, 420], [X - 260, 90, 300], q)
        alvo, fov = [X + 300, 0, 0], 50
    elif k == 1:
        cam, alvo, fov = [xn + 70, 18, 100], [xn, 2, -60], 46
    elif k == 2:   # de lado, acompanhando o perfil da onda
        q = ease(lt / 1.2)
        cam = mistura([xn + 70, 18, 100], [X + 10, 3, 120], q)
        alvo, fov = mistura([xn, 2, -60], [X + 10, 0, 0], q), 40
    elif k in (3, 4):   # de lado, centrado na praia: o mar recua e a parede chega
        cam, alvo, fov = [-25, 4, 95], [-25, 1, 0], 40
    else:
        q = ease(lt / 2.0) if k == 5 else 1.0
        cam = mistura([-25, 4, 95], [260, 120, 300], q)
        alvo, fov = mistura([-25, 1, 0], [60, 0, -150], q), 50
    spray = min(1.0, max(0.0, (A - 4) / 6))
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "eta": [round(float(v), 2) for v in sup],
            "navio": navio, "spray": spray, "sprayX": X - 20}


FILME = tres.Filme("tsunami.js", estado)


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["A tsunami is racing across the ocean, as fast as a jet plane. Watch what happens when it reaches the beach."],
        {"title": "WHAT HAPPENS WHEN A TSUNAMI HITS?"}, tail=0.2),
    seg(["Out in deep water it's less than a meter tall. This ship barely feels it."],
        {"big": "DEEP WATER", "sub": "~800 KM/H, UNDER 1 M TALL", "color": WHITE}, tail=0.2),
    seg(["Near the coast the water gets shallow, so the wave slows down and all that energy piles up."],
        {"big": "SLOWER = TALLER", "big_size": 90, "color": YELLOW}, tail=0.2),
    seg(["First, the sea pulls back. The beach drains for hundreds of meters."],
        {"big": "THE DRAWBACK", "sub": "NATURE'S WARNING SIGN", "color": PINK}, tail=0.3),
    seg(["Then a wall of water ten meters tall rushes in, and it keeps on coming."],
        {"big": "THE WALL", "sub": "10+ METERS", "color": PINK}, tail=0.4, sfx=[(0, 0.6, "whoosh")]),
    seg(["If the sea ever suddenly pulls back, run to high ground. Don't wait to see the wave."],
        {"big": "RUN UPHILL", "sub": "DON'T WAIT FOR THE WAVE", "color": GREEN}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Did you know the sea pulls back first?", "DID YOU KNOW THIS?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
