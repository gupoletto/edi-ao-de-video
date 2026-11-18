"""What happens if a 1 km asteroid hits Earth? (cinematic 3D). Wed 18/11/2026, topic: space. Search 18/11: "what
happens if an asteroid hits earth", median 10.7k (top 1M; "What if the biggest asteroid hit Earth?" 465k).

Facts (1 km stony asteroid at ~20 km/s, from impact studies such as Collins, Melosh & Marcus 2005 and NASA CNEOS):
- it crosses the atmosphere in a few seconds, glowing;
- impact energy is on the order of 100,000 megatons of TNT, far more than all nuclear weapons combined;
- it digs a crater roughly 10-20 km across;
- the blast and heat devastate a region hundreds of kilometers wide; dust and soot in the atmosphere could cool the
  climate for months to years;
- impacts this size happen roughly once every half a million years; NASA tracks over 90% of near-Earth asteroids 1 km
  or larger and none is on a collision course. In 2022 NASA's DART mission showed a spacecraft can nudge an asteroid.
The visuals are not to scale (a 1 km rock would be invisible at planet scale).
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import GREEN, PINK, WHITE, YELLOW, Seg, render, text_center  # noqa: E402

R = 10.0
N = np.array([0.0, 0.42, 0.91])
N = N / np.linalg.norm(N)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mistura(a, b, k):
    return [x + (y - x) * k for x, y in zip(a, b)]


def seg_de(t, segs):
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    return k, t - segs[k].t0


def estado(t, segs):
    k, lt = seg_de(t, segs)
    t_imp = segs[2].t0 + 0.4
    alvo_p = N * R
    vinda = np.array([0.55, 0.45, 0.70])
    vinda = vinda / np.linalg.norm(vinda)
    d = max(0.0, t_imp - t)
    ast = alvo_p + vinda * (1.2 + 9 * d)
    brilho = ease(1 - d / 2.0)
    dt = t - t_imp
    flash = max(0.0, 1 - dt / 0.8) if dt > 0 else 0.0
    onda = 1.4 * (1 - math.exp(-max(0.0, dt) / 2.5)) if dt > 0 else 0.0
    cratera = ease(dt / 1.5) if dt > 0 else 0.0
    poeira = ease(dt / 6.0) if dt > 0 else 0.0
    longe = [0.0, 8.0, 68.0]
    perto = list(alvo_p * 1.0 + np.array([12.0, 9.0, 16.0]))
    if k == 0:
        q = ease(lt / 4.0)
        cam, alvo, fov = mistura([0.0, 12.0, 95.0], longe, q), [0, 2, 0], 40
    elif k == 1:
        q = ease(lt / 3.0)
        cam, alvo, fov = mistura(longe, perto, q), mistura([0, 2, 0], list(alvo_p), q), 42
    elif k in (2, 3):
        cam, alvo, fov = perto, list(alvo_p), 42
        if k == 3:
            q = ease(lt / 3.0)
            cam = mistura(perto, [8.0, 14.0, 48.0], q)
            alvo = mistura(list(alvo_p), [0, 3, 0], q)
    else:
        q = ease(lt / 3.0) if k == 4 else 1.0
        cam, alvo, fov = mistura([8.0, 14.0, 48.0], [0.0, 10.0, 66.0], q), [0, 2, 0], 40
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "ast": list(ast), "astR": 0.6, "brilho": brilho,
            "flash": flash, "onda": onda, "cratera": cratera, "poeira": poeira}


FILME = tres.Filme("asteroide.js", estado)


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["A rock one kilometer wide is heading straight for Earth at twenty kilometers per second. Here's what happens."],
        {"title": "WHAT IF AN ASTEROID HITS EARTH?"}, tail=0.2),
    seg(["It tears through the atmosphere in about three seconds, glowing like a second Sun."],
        {"big": "3 SECONDS", "sub": "THROUGH THE ATMOSPHERE", "color": YELLOW}, tail=0.1),
    seg(["Impact. A hundred thousand megatons, more than every nuclear bomb ever built, combined."],
        {"big": "IMPACT", "sub": "~100,000 MEGATONS", "color": PINK}, tail=0.3, sfx=[(0, 0.4, "whoosh")]),
    seg(["A crater over ten kilometers wide, and a blast wave flattening everything for hundreds of kilometers."],
        {"big": "THE BLAST", "sub": "HUNDREDS OF KM", "color": PINK}, tail=0.2),
    seg(["Dust fills the sky and could cool the whole planet for years. But relax: NASA tracks almost every rock this size, and none is coming."],
        {"big": "NONE IS COMING", "sub": "NASA TRACKS 90%+ OF THEM", "color": GREEN}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Should we build a planetary shield?", "SHOULD WE BUILD A SHIELD?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
