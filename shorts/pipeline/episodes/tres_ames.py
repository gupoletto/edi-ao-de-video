"""Why does this room make people shrink? (cinematic 3D, the Ames room). Mon 16/11/2026, topic: optical illusions.
Search 16/11: "optical illusion" median ~2M (week ranking); "ames room illusion" itself is small (1.2k), so the title
leads with the effect ("makes people shrink").

Shots: from the peephole, two people of the same height look giant and tiny -> they swap corners and seem to grow
and shrink as they walk -> the camera rises: the room is a trapezoid, the left corner almost twice as far -> back to
the peephole: the brain assumes a rectangular room -> Quark asks the question.

Facts:
- the Ames room was devised by American ophthalmologist Adelbert Ames Jr. in 1946 (based on an idea by Hermann von
  Helmholtz);
- it is built so that, seen with one eye from a fixed peephole, its distorted trapezoidal shape projects exactly like
  a normal rectangular room; the far corner is much farther away than the near one;
- the brain assumes the room is rectangular (both people at the same distance), so it concludes they differ in size.
Construction: every vertex of an apparent rectangular room is pushed along the ray from the eye by a factor that
grows to the left (1.0 at the right wall, 1.9 at the left wall), which keeps the image from the eye unchanged.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import GREEN, PINK, WHITE, YELLOW, Seg, render  # noqa: E402

OLHO = [0.0, 1.6, 8.0]
ESQ, DIR = [-1.9, -5.3], [1.9, -5.3]


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
    # caminhada: no segmento 1 eles trocam de canto (pelo fundo do quarto, em posições aparentes)
    q = ease((t - segs[1].t0 - 0.3) / (segs[1].dur - 0.5)) if k >= 1 else 0.0
    pA = mistura(ESQ, DIR, q)
    pB = mistura(DIR, ESQ, q)
    pB[1] += 0.6 * math.sin(math.pi * q)   # desviam um do outro
    anda = 0 < q < 1
    passo = t * 9 if anda else 0.0
    alvo_olho = [0.0, 1.2, -6.0]
    vista_cima = ([6.0, 22.0, 6.0], [-2.0, 0.0, -8.0], 55)
    if k <= 1:
        cam, alvo, fov = OLHO, alvo_olho, 52
    elif k == 2:
        qq = ease(lt / 2.5)
        cam = mistura(OLHO, vista_cima[0], qq)
        alvo = mistura(alvo_olho, vista_cima[1], qq)
        fov = 52
    elif k == 3:
        cam, alvo, fov = vista_cima
    elif k == 4:
        qq = ease(lt / 2.0)
        cam = mistura(vista_cima[0], OLHO, qq)
        alvo = mistura(vista_cima[1], alvo_olho, qq)
        fov = 52
    else:
        cam, alvo, fov = OLHO, alvo_olho, 52
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "pA": pA, "pB": pB, "passoA": passo, "passoB": passo + 1,
            "olho": 1.0 if 2 <= k <= 3 else 0.0, "virar": 0.0}


FILME = tres.Filme("ames.js", estado)


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["These two people are exactly the same height. But one looks like a giant, and the other like a toy."],
        {"title": "WHY DOES THIS ROOM SHRINK PEOPLE?"}, tail=0.2),
    seg(["Now they swap corners. Watch them grow and shrink as they walk!"],
        {"big": "THEY SWAP", "color": YELLOW}, tail=0.3),
    seg(["Here's the trick. From above, the room isn't a box at all."],
        {"big": "THE TRICK", "color": PINK}, tail=0.2, sfx=[(0, 0, "whoosh")]),
    seg(["The left corner is almost twice as far away, and the walls and floor are slanted to hide it."],
        {"big": "TWICE AS FAR", "sub": "A SLANTED ROOM", "color": PINK}, tail=0.3),
    seg(["From the peephole, your brain assumes the room is a normal box, so it decides the people changed size."],
        {"big": "YOUR BRAIN ASSUMES", "big_size": 84, "color": WHITE}, tail=0.3),
    seg(["It's called the Ames room, built in 1946."],
        {"big": "THE AMES ROOM", "big_size": 92, "sub": "ADELBERT AMES JR., 1946", "color": GREEN}, tail=0.8),
]
SEGMENTS.append(pq.seg_pergunta("Did your brain fall for it?", "DID YOUR BRAIN FALL FOR IT?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
