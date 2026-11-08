"""What happens to a skyscraper in an earthquake? (cinematic 3D, resonance vs base isolation). Mon 09/11/2026,
3D queue (earthquake building). Search 08/11: "earthquake simulation", median 98k; "what happens if 3d animation" 1.75M.

Shots: two 12-floor towers on a plaza; the ground starts shaking at once -> the fixed-base tower sways in resonance
and its columns glow red -> close-up of the rubber bearings under the second tower shearing while the slab above
barely moves -> the isolated tower stands almost still -> wide shot -> Quark asks the question.

Physics (integrated below, not typed in): ground motion g(t) = A(t) sin(2 pi f t), f = 1.0 Hz. Each tower's first
mode is a damped oscillator x'' = -w^2 (x - b) - 2 z w (x' - b'). The fixed-base tower has a natural frequency of
1.0 Hz (a rule of thumb for ~10-12 storey buildings is a period of about 0.1 s per storey) and damping 3%, so it
resonates. The isolated tower's base sits on bearings with a 0.35 Hz frequency and 20% damping; its superstructure
(same 1.0 Hz) is driven by the base, which moves far less at 1 Hz. Relative sway is drawn 3x larger to be visible
(said on screen).

Facts: base isolation (laminated rubber bearings) decouples a building from horizontal ground motion; it is used for
hospitals, towers and bridges in Japan, California, Chile and elsewhere.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import FPS, GREEN, PINK, WHITE, YELLOW, Seg, pill, render, text_center  # noqa: E402

N = 12
F_CHAO = 1.0
EXAGERO = 3.0
XN, XI = -11.0, 11.0


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mistura(a, b, k):
    return [x + (y - x) * k for x, y in zip(a, b)]


def seg_de(t, segs):
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    return k, t - segs[k].t0


_SIM = {}


def simula(segs):
    chave = tuple(round(s.t0, 3) for s in segs)
    if chave in _SIM:
        return _SIM[chave]
    total = segs[-1].t0 + segs[-1].dur + 1
    dt = 1 / (FPS * 8)
    ts = np.arange(0, total, dt)
    fim = segs[5].t0 + segs[5].dur * 0.5
    amp = 0.25 * np.clip((ts - 0.1) / 1.5, 0, 1) * np.clip((fim - ts) / 2.0 + 1, 0, 1)
    g = amp * np.sin(2 * np.pi * F_CHAO * ts)
    gv = np.gradient(g, dt)

    def osc(base, basev, f, z):
        w = 2 * np.pi * f
        x, v = 0.0, 0.0
        out = np.zeros_like(ts)
        for i in range(len(ts)):
            a = -w * w * (x - base[i]) - 2 * z * w * (v - basev[i])
            v += a * dt
            x += v * dt
            out[i] = x
        return out
    topoN = osc(g, gv, 1.0, 0.03)
    b = osc(g, gv, 0.35, 0.20)
    bv = np.gradient(b, dt)
    topoI = osc(b, bv, 1.0, 0.03)
    _SIM[chave] = (ts, g, topoN, b, topoI)
    return _SIM[chave]


def amostra(arr, ts, t):
    return float(np.interp(t, ts, arr))


def projeta(cam, alvo, fov, p):
    c, a, p = np.array(cam), np.array(alvo), np.array(p)
    fwd = (a - c) / np.linalg.norm(a - c)
    right = np.cross(fwd, [0, 1, 0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    d = p - c
    f = 960 / math.tan(math.radians(fov) / 2)
    return 540 + f * (d @ right) / (d @ fwd), 960 - f * (d @ up) / (d @ fwd)


def estado(t, segs):
    k, lt = seg_de(t, segs)
    ts, g, tn, b, ti = simula(segs)
    gg, bb = amostra(g, ts, t), amostra(b, ts, t)
    reln, reli = amostra(tn, ts, t) - gg, amostra(ti, ts, t) - bb
    forma = [math.sin(math.pi / 2 * (i + 1) / N) for i in range(N)]
    andN = [gg + EXAGERO * reln * f for f in forma]
    andI = [bb + EXAGERO * reli * f for f in forma]
    estresse = min(1.0, abs(reln) / 0.45)
    tremor = gg * 0.15   # a câmera treme um pouco junto
    largo = ([0 + tremor, 18, 100], [0, 25, 0], 45)
    if k <= 1:
        q = ease((t) / (segs[1].t0 + segs[1].dur))
        cam = mistura([0 + tremor, 12, 110], largo[0], q)
        alvo, fov = largo[1], 45
    elif k == 2:
        q = ease(lt / 1.2)
        cam = mistura(largo[0], [XN + 2 + tremor, 26, 52], q)
        alvo = mistura(largo[1], [XN, 23, 0], q)
        fov = 45
    elif k == 3:
        q = ease(lt / 1.2)
        cam = mistura([XN + 2, 26, 52], [XI + 9, 3.2, 17], q)
        alvo = mistura([XN, 23, 0], [XI + 2, 2.2, 0], q)
        fov = 45
    elif k == 4:
        q = ease(lt / 1.5)
        cam = mistura([XI + 9, 3.2, 17], [XI - 2 + tremor, 26, 54], q)
        alvo = mistura([XI + 2, 2.2, 0], [XI, 23, 0], q)
        fov = 45
    else:
        q = ease(lt / 1.5) if k == 5 else 1.0
        cam = mistura([XI - 2, 26, 54], largo[0], q)
        alvo = mistura([XI, 23, 0], largo[1], q)
        fov = 45
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "chao": gg, "andN": andN, "andI": andI, "base": bb,
            "estresse": estresse, "poeira": min(1.0, abs(gg) / 0.2) if k < 6 else 0.0}


FILME = tres.Filme("terremoto.js", estado)
SEGS = []


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)
    k = SEGMENTS.index(s) if s in SEGMENTS else -1
    if not SEGS:
        return
    e = estado(s.t0 + t, SEGS)
    if k in (0, 1, 5):
        for x, rot, cor in ((XN, "NORMAL", PINK), (XI, "ON BEARINGS", GREEN)):
            sx, sy = projeta(e["cam"], e["alvo"], e["fov"], [x, 30, 7])
            pill(ctx, rot, sx, sy - 30, cor, 1.0, size=30)
    if 1 <= k <= 5:
        text_center(ctx, f"SWAY SHOWN {EXAGERO:.0f}x LARGER", 540, 1255, 24, WHITE, "SemiBold", alpha=0.7)


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["An earthquake hits two towers. Watch what happens."],
        {"title": "WHAT IF AN EARTHQUAKE HITS?"}, tail=0.2),
    seg(["The ground swings back and forth, about once every second. Now watch the left tower."],
        {"big": "THE SHAKING", "sub": "ONE SWING PER SECOND", "color": YELLOW}, tail=0.3),
    seg(["This tower naturally sways at the same rhythm, so every push makes the swing bigger. Its columns take a beating."],
        {"big": "RESONANCE", "sub": "THE SWINGS ADD UP", "color": PINK}, tail=0.4),
    seg(["The other tower sits on rubber bearings. The ground slides under them, and the rubber bends instead of the building."],
        {"big": "BASE ISOLATION", "big_size": 88, "sub": "RUBBER + STEEL LAYERS", "color": GREEN}, tail=0.4),
    seg(["So the tower above barely moves, while the ground keeps shaking."],
        {"big": "ALMOST STILL", "sub": "THE BEARINGS SOAK IT UP", "color": GREEN}, tail=0.3),
    seg(["Hospitals and towers in Japan, California and Chile are built like this, so they keep working after a big quake."],
        {"big": "REAL TECH", "sub": "JAPAN · CALIFORNIA · CHILE", "color": WHITE}, tail=0.6),
]
SEGMENTS.append(pq.seg_pergunta("Which tower would you rather be in?", "WHICH TOWER WOULD YOU PICK?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    SEGS[:] = segs
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
