"""What happens if lightning hits a plane? (cinematic 3D, Faraday cage). Sun 08/11/2026, 3D queue #7
(lightning and airliners, 855k-view reference), chosen over #5 because "what happens if" 3D titles perform best.
Search 07/11: "what happens if lightning hits a plane", median 7.5k (top 153k).

Shots: an airliner cruising through a thunderstorm -> a bolt hits the nose -> the current races along the metal skin
to the tail -> x-ray: passengers inside, untouched (Faraday cage) -> the bolt leaves from the tail -> static wicks
crackle -> the plane flies on -> Quark asks the question.

Facts:
- on average each commercial airliner is struck by lightning about once a year (roughly once every 1,000 flight
  hours);
- the strike usually attaches at an extremity such as the nose or a wingtip and exits at another, often the tail;
- the conductive aluminium skin (or the metal mesh embedded in composite skins) carries the current around the
  outside, so the cabin works like a Faraday cage and passengers are protected;
- airliners are designed and certified to withstand strikes; damage is usually small pit or scorch marks that are
  inspected after landing; static wicks on the trailing edges bleed off static charge.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import GREEN, PINK, WHITE, YELLOW, Seg, render  # noqa: E402

V = 230.0      # m/s, cruzeiro
ALT = 600.0


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mistura(a, b, k):
    return [x + (y - x) * k for x, y in zip(a, b)]


def seg_de(t, segs):
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    return k, t - segs[k].t0


T_RAIO = 1.3      # s depois do início do segmento 1: o raio bate no nariz


def estado(t, segs):
    k, lt = seg_de(t, segs)
    x = V * 0.12 * t        # o avião anda devagar na cena (as nuvens passam); a velocidade real fica no texto
    y = ALT + 2 * math.sin(t * 0.7)
    pitch = 0.02 * math.sin(t * 0.9)
    tr = segs[1].t0 + T_RAIO
    d = t - tr
    raio1 = 0.0
    if 0 <= d < 2.2:
        raio1 = max(0.0, 1 - d / 2.2) * (0.6 + 0.4 * (math.sin(d * 40) > -0.3))
    corrente = ease((t - segs[2].t0 - 0.3) / 2.6) if k >= 2 else 0.0
    brilho = 1.0 if 2 <= k <= 4 else (0.0 if k < 2 else max(0.0, 1 - (t - segs[5].t0) / 0.8))
    if k == 1:
        corrente, brilho = min(0.25, max(0.0, d) / 2), 1.0 if d > 0 else 0.0
    raiox = ease(lt / 0.6) if k == 3 else (1 - ease(lt / 0.6) if k == 4 else 0.0)
    ts = segs[4].t0 + 0.4
    d2 = t - ts
    raio2 = max(0.0, 1 - d2 / 2.0) * (0.6 + 0.4 * (math.sin(d2 * 37) > -0.3)) if 0 <= d2 < 2.0 else 0.0
    descarga = 1.0 if k == 4 and lt > 0.4 else (max(0.0, 1 - lt / 1.5) if k == 5 else 0.0)
    flash = max(raio1, raio2)
    if k == 0:  # relâmpagos ao longe
        flash = 0.35 * max(0.0, 1 - abs(lt - 1.2) / 0.15) + 0.25 * max(0.0, 1 - abs(lt - 2.6) / 0.12)
    # câmeras (relativas ao avião)
    lado_alto = ([x + 30, y + 4, 70], [x + 12, y + 6, 0], 44)
    if k == 0:
        q = ease(lt / 4.0)
        cam = [x + 120 - 40 * q, y + 30 - 10 * q, 110 - 30 * q]
        alvo = [x - 5, y + 12, 0]
        fov = 40
    elif k == 1:
        cam, alvo, fov = lado_alto
        cam = mistura([x + 80, y + 20, 80], cam, ease(lt / 1.0))
    elif k == 2:
        q = ease(lt / 1.2)
        cam = mistura(lado_alto[0], [x - 5, y + 14, 32], q)
        alvo = mistura(lado_alto[1], [x - 2, y + 4, 0], q)
        fov = 40 + 4 * q
    elif k == 3:
        q = ease(lt / 1.2)
        cam = mistura([x - 5, y + 14, 32], [x + 4, y + 8, 17], q)
        alvo = [x + 1, y + 3.5, 0]
        fov = 44
    elif k == 4:
        q = ease(lt / 1.2)
        cam = mistura([x + 4, y + 8, 17], [x + 40, y + 2, 55], q)
        alvo = mistura([x + 1, y + 3.5, 0], [x - 25, y - 10, 0], q)
        fov = 44
    else:
        q = ease(lt / 2.0) if k == 5 else 1.0
        cam = mistura([x + 40, y + 2, 55], [x + 90, y + 12, 70], q)
        alvo = [x - 2, y + 4, 0]
        fov = 40
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "pos": [x, y, 0.0], "pitch": pitch, "trem": 0.0,
            "hidr": 0.0, "falha": 0.0, "roda": 0.0, "trava": 0.0, "fumaca": -1.0, "toqueX": 0.0,
            "raio1": raio1, "raio2": raio2, "corrente": corrente, "brilhoCorr": brilho, "raiox": raiox,
            "descarga": descarga, "flash": flash}


FILME = tres.Filme("raio.js", estado)


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["What happens if lightning hits a plane in the middle of a storm? Is everyone in danger?"],
        {"title": "WHAT IF LIGHTNING HITS A PLANE?"}, tail=0.2),
    seg(["It happens to every airliner about once a year. Look, here it comes!"],
        {"big": "ONCE A YEAR", "sub": "EVERY AIRLINER, ON AVERAGE", "color": YELLOW}, tail=1.0, sfx=[(0, 1.3, "whoosh")]),
    seg(["Up to two hundred thousand amps race across the metal skin, from the nose all the way to the tail."],
        {"big": "THE SKIN", "sub": "THE CURRENT STAYS OUTSIDE", "color": (0.62, 0.82, 1.0)}, tail=0.3),
    seg(["Inside, nobody feels a thing. The metal shell works like a Faraday cage."],
        {"big": "FARADAY CAGE", "big_size": 92, "sub": "PASSENGERS ARE SHIELDED", "color": GREEN}, tail=0.3),
    seg(["Then the bolt jumps off the tail and keeps going."],
        {"big": "EXIT", "sub": "OUT THROUGH THE TAIL", "color": PINK}, tail=0.5, sfx=[(0, 0.4, "whoosh")]),
    seg(["The plane just flies on. After landing, mechanics check for tiny scorch marks, and that's it."],
        {"big": "IT FLIES ON", "sub": "BUILT AND TESTED FOR IT", "color": WHITE}, tail=1.2),
]
SEGMENTS.append(pq.seg_pergunta("Window seat in a storm, yes or no?", "WINDOW SEAT IN A STORM?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
