"""What happens when a submarine dives? (cinematic 3D, ballast tanks in x-ray). Fri 13/11/2026, 3D queue (submarine).
Search 13/11: "how submarines dive", median 28.8k (top 374k; "Why submarines dive and surface using ballast tanks" 237k).

Shots: a submarine at the surface -> x-ray: vents on top open and seawater floods the ballast tanks, air bubbles out
-> heavier than the water it displaces, it sinks -> the crew trims it to neutral buoyancy and it hovers ->
compressed air blows the water out of the tanks -> it rises and breaks the surface -> Quark asks the question.

Facts:
- a submarine dives by flooding its main ballast tanks (vents on top let the air out, flood holes at the bottom let
  seawater in), making it heavier than the water it displaces (Archimedes);
- smaller trim/compensating tanks fine-tune the weight so it can hover at neutral buoyancy; the hydroplanes help
  steer up and down;
- to surface, high-pressure air is blown into the ballast tanks, pushing the water out;
- a US Virginia-class attack submarine displaces about 7,800 tonnes submerged and is about 115 m long (our model is
  shorter, for framing).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import GREEN, PINK, WHITE, YELLOW, Seg, render  # noqa: E402

Y_SUP, Y_FUNDO = -1.6, -38.0
V = 2.5    # m/s para a frente


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
    t_abre = segs[1].t0 + 0.5
    t_desce, t_neutro = segs[2].t0, segs[3].t0 + 0.5
    t_sopro, t_sobe = segs[4].t0 + 0.4, segs[5].t0
    x = V * t
    lastro = ease((t - t_abre) / (t_desce + 1.5 - t_abre)) * (1 - ease((t - t_sopro) / 2.5))
    if t < t_desce:
        y = Y_SUP - 1.2 * lastro
    elif t < t_neutro:
        y = Y_SUP - 1.2 + (Y_FUNDO - Y_SUP + 1.2) * ease((t - t_desce) / (t_neutro - t_desce))
    elif t < t_sobe:
        y = Y_FUNDO + 0.4 * math.sin((t - t_neutro) * 1.5)
    else:
        y = Y_FUNDO + (Y_SUP - Y_FUNDO) * ease((t - t_sobe) / (segs[5].dur * 0.85))
    pitch = 0.0
    if t_desce < t < t_neutro:
        pitch = -0.12 * math.sin(math.pi * (t - t_desce) / (t_neutro - t_desce))
    if t > t_sobe:
        pitch = 0.15 * math.sin(math.pi * min(1.0, (t - t_sobe) / (segs[5].dur * 0.85)))
    raiox = ease((t - segs[1].t0) / 0.6) * (1 - ease((t - segs[5].t0 - 1.0) / 0.6))
    vent = 1.0 if t_abre < t < t_desce + 1.5 else 0.0
    sopro = 1.0 if t_sopro < t < t_sopro + 3.0 else 0.0
    # câmeras
    if k == 0:
        q = ease(lt / 3.0)
        cam = mistura([x + 70, 18, 70], [x + 45, 9, 48], q)
        alvo, fov = [x, 0, 0], 40
    elif k in (1, 2):
        q = ease((t - segs[1].t0) / 1.5)
        cam = mistura([x + 45, 9, 48], [x + 34, y + 9, 36], q)
        alvo = [x, y, 0]
        fov = 46
    elif k == 3:
        cam, alvo, fov = [x + 34, y + 9, 36], [x, y, 0], 46
    elif k == 4:
        cam, alvo, fov = [x + 32, y - 6, 36], [x, y + 1, 0], 46
    else:
        q = ease(lt / 2.5) if k == 5 else 1.0
        cam = mistura([x + 32, y - 6, 36], [x + 55, 6, 55], q)
        alvo = [x, y + 2, 0]
        fov = 42
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "pos": [x, y, 0.0], "pitch": pitch, "raiox": raiox,
            "lastro": lastro, "bolhasVent": vent, "bolhasSopro": sopro, "helice": t * 6}


FILME = tres.Filme("submarino.js", estado)


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["This submarine weighs thousands of tonnes, and it's about to sink, on purpose."], {"title": "HOW DOES A SUBMARINE DIVE?"}, tail=0.3),
    seg(["Vents on top open, the air rushes out, and seawater floods huge ballast tanks."],
        {"big": "FLOOD THE TANKS", "big_size": 88, "sub": "AIR OUT, WATER IN", "color": YELLOW}, tail=0.2),
    seg(["Now it's heavier than the water it pushes aside, so down it goes."],
        {"big": "HEAVIER = SINK", "sub": "ARCHIMEDES", "color": PINK}, tail=0.2),
    seg(["To hover, the crew fine-tunes small trim tanks until it's perfectly balanced."],
        {"big": "NEUTRAL", "sub": "NOT SINKING, NOT RISING", "color": WHITE}, tail=0.3),
    seg(["To come back up, compressed air blasts the water out of the tanks."],
        {"big": "BLOW THE TANKS", "big_size": 90, "sub": "HIGH-PRESSURE AIR", "color": (0.36, 0.78, 0.98)}, tail=0.3,
        sfx=[(0, 0.4, "whoosh")]),
    seg(["Lighter than the water again, the submarine rises all the way back to the surface. A fish does the same trick with its swim bladder."],
        {"big": "SURFACE", "sub": "LIKE A FISH'S SWIM BLADDER", "color": GREEN}, tail=0.8),
]
SEGMENTS.append(pq.seg_pergunta("Would you ride in a submarine?", "WOULD YOU RIDE IN ONE?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
