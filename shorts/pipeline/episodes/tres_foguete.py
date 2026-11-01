"""Why rockets fly sideways to reach orbit (cinematic 3D). Mon 02/11/2026, topic: space, format: cinematic 3D.

Shots: launch with smoke and flame, the rocket pitches over -> space: Earth with Newton's-cannon paths: straight up
falls straight back; sideways but slow falls farther away; sideways at orbital speed never lands -> orbit.

Facts: space (Karman line) is ~100 km up; low orbit needs ~7.8 km/s sideways = ~17,500 mph (ISS ~7.66 km/s at
~400 km); an orbit is free fall with enough horizontal speed that the ground curves away as fast as you fall.
Orbit altitude is drawn exaggerated (labelled "not to scale").
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import BLUE, PINK, WHITE, YELLOW, Seg, render, text_center  # noqa: E402

A_SUBIDA = 7.0  # m/s^2 (visual) na subida


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
    base = {"t": t, "tr": [0, 0, 0, 0], "marca": -1, "pos": -1, "giro": 0.02 * t, "incl": 0.0, "sobe": 0.0,
            "chama": 0.0, "ignicao": -1.0}
    if k <= 1:  # solo
        tv = t - 0.3
        sobe = 0.5 * A_SUBIDA * max(0.0, tv) ** 2
        incl = 0.5 * ease((t - segs[1].t0 - 1.0) / 3.0) if k == 1 else 0.0
        if k == 0:
            cam, alvo, fov = [52, 6 + sobe * 0.4, 78], [0, 17 + sobe, 0], 40
        else:
            q = ease(lt / 2.0)
            cam = mistura([52, 6 + sobe * 0.4, 78], [70, sobe * 0.85, 110], q)
            alvo = [math.sin(incl) * max(0, sobe - 60) * 0.5, sobe + 17, 0]
            fov = 40
        return dict(base, fase=0, cam=cam, alvo=alvo, fov=fov, sobe=sobe, incl=incl, chama=1.0,
                    ignicao=t + 0.8)
    # espaço
    perto_c, perto_a = [0, 74, 120], [0, 64, 0]
    meio_c, meio_a = [0, 30, 250], [0, 40, 0]
    longe_c, longe_a = [0, 0, 520], [0, 0, 0]
    tr = [0.0, 0.0, 0.0, 0.0]
    marca, pos = -1, -1
    if k == 2:
        cam, alvo = mistura(meio_c, perto_c, ease(lt / 1.0)), mistura(meio_a, perto_a, ease(lt / 1.0))
        tr[0] = ease((lt - 0.6) / (segs[2].dur - 1.0))
        marca = 0
    elif k == 3:
        q = ease(lt / 1.5)
        cam, alvo = mistura(perto_c, meio_c, q), mistura(perto_a, meio_a, q)
        tr[0] = 1.0
        meio = segs[3].dur / 2
        tr[1] = ease((lt - 0.4) / (meio - 0.4))
        tr[2] = ease((lt - meio) / (segs[3].dur - meio - 0.2))
        marca = 1 if lt < meio else 2
    elif k == 4:
        q = ease(lt / 1.5)
        cam, alvo = mistura(meio_c, longe_c, q), mistura(meio_a, longe_a, q)
        tr[0] = tr[1] = tr[2] = 1.0
        tr[3] = ease((lt - 0.5) / (segs[4].dur - 0.7))
        marca = 3
    else:  # órbita: o foguetinho segue dando voltas; a câmera gira devagar
        tg = t - segs[5].t0
        ang = 0.25 * math.sin(tg * 0.25)
        cam = [math.sin(ang) * 520, 20, math.cos(ang) * 520]
        alvo = [0, 0, 0]
        tr = [1.0, 1.0, 1.0, 1.0]
        marca, pos = 3, (tg / 6.0) % 1.0
    return dict(base, fase=1, cam=cam, alvo=alvo, fov=34, tr=tr, marca=marca, pos=pos)


FILME = tres.Filme("foguete.js", estado)


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)
    if s in SEGMENTS[2:6]:
        text_center(ctx, "NOT TO SCALE", 540, 1255, 22, WHITE, "SemiBold", alpha=0.6)


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["Why do rockets turn sideways right after launch?"], {"title": "WHY ROCKETS FLY SIDEWAYS"}, tail=0.1,
        sfx=[(0, 0, "whoosh")]),
    seg(["Space is only about sixty miles up. Going up is the easy part."],
        {"big": "60 MILES", "sub": "TO SPACE", "color": YELLOW}, tail=0.3),
    seg(["But fly straight up, and you fall straight back down."], {"big": "STRAIGHT UP", "big_size": 90, "color": PINK},
        tail=0.4),
    seg(["Go sideways, and you land farther away. Go faster, even farther."],
        {"big": "SIDEWAYS", "big_size": 90, "color": YELLOW}, tail=0.3),
    seg(["At about seventeen thousand miles per hour, you never land."],
        {"big": "17,500 MPH", "big_size": 96, "sub": "ORBITAL SPEED", "color": BLUE}, tail=0.5),
    seg(["That's an orbit. You're always falling, but so fast sideways that you keep missing the Earth."],
        {"title": "ORBIT = FALLING SIDEWAYS"}, tail=0.3),
]
SEGMENTS.append(pq.seg_pergunta("Would you ride a rocket to orbit?", "WOULD YOU GO?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=FILME.renderizar)
