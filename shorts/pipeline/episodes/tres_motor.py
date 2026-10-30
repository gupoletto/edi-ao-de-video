"""How a car engine actually works (3D). Format "how it works 3D" (shorts/pipeline/tres.py).

Four-stroke cycle = two crankshaft turns (720°): intake (piston down, intake valve open), compression (both closed,
piston up), power (spark near top dead centre, piston pushed down), exhaust (exhaust valve open, piston up).
Each cylinder fires once every two turns: at 3,000 rpm that is 3000 / 60 / 2 = 25 power strokes per second.
Piston position from real crank-slider kinematics (cenas3d/motor.js); crank radius / rod length = 1 / 3.2.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import tres  # noqa: E402
from core import BLUE, PINK, WHITE, YELLOW, Seg, ramp, render  # noqa: E402

PI = math.pi
FASES = [("1", "INTAKE", BLUE), ("2", "COMPRESSION", WHITE), ("3", "POWER", YELLOW), ("4", "EXHAUST", PINK)]
DOTS = [f[0] for f in FASES]
AR, AR_DENSO, FOGO, FUMACA = (0.37, 0.66, 1.0), (0.30, 0.55, 1.0), (1.0, 0.32, 0.04), (0.55, 0.56, 0.62)
FAISCA = 1.6  # s dentro do trecho "power" em que a vela dispara


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def theta(t, segs):
    """Ângulo do virabrequim no tempo global t, contínuo entre os trechos."""
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    s = segs[k]
    lt = t - s.t0
    if k == 0:  # abertura: 3 ciclos completos (6 voltas), desacelerando até o começo da admissão
        return 12 * PI * (1 - (1 - min(1.0, lt / s.dur)) ** 2)
    if k == 3:  # explosão: o pistão espera no topo e desce rápido quando a vela dispara (no "fires" da narração)
        return 12 * PI + 2 * PI + PI * ease((lt - FAISCA) / 1.3)
    if 1 <= k <= 4:  # um tempo por trecho, devagar, para ver cada peça
        return 12 * PI + (k - 1) * PI + PI * ease((lt - 0.3) / max(0.5, s.dur - 0.6))
    # depois: acelera e segue girando
    base = 16 * PI
    if k == 5:
        return base + 2 * PI * 3.0 * lt * min(1.0, lt / 1.5)
    s5 = segs[5]
    return base + 2 * PI * 3.0 * s5.dur + 2 * PI * 3.0 * (t - s.t0)


def estado(t, segs):
    th = theta(t, segs)
    fi = th % (4 * PI)
    adm = math.sin(fi) if fi < PI else 0.0
    esc = math.sin(fi - 3 * PI) if fi >= 3 * PI else 0.0
    if fi < PI:
        cor, op, fa = AR, 0.25 + 0.15 * fi / PI, 0.0
    elif fi < 2 * PI:
        cor, op, fa = AR_DENSO, 0.4 + 0.3 * (fi - PI) / PI, 0.0
    elif fi < 3 * PI:
        q = (fi - 2 * PI) / PI
        cor = tuple(a + (b - a) * min(1, q * 1.4) for a, b in zip(FOGO, FUMACA))
        op, fa = 0.85 - 0.3 * q, max(0.0, 1 - q * 3.5)
    else:
        cor, op, fa = FUMACA, 0.5 - 0.35 * (fi - 3 * PI) / PI, 0.0
    brilho = max(0.0, 0.6 - (fi - 2 * PI) / PI) if 2 * PI <= fi < 3 * PI else 0.0
    k = next(i for i, sg in enumerate(segs) if t < sg.t0 + sg.dur or i == len(segs) - 1)
    if k == 3:  # no trecho lento da explosão o efeito segue o tempo, não o ângulo
        lt = t - segs[3].t0
        if lt < FAISCA:
            cor, op, fa, brilho = AR_DENSO, 0.7, 0.0, 0.0
        else:
            q = min(1.0, (lt - FAISCA) / 2.5)
            cor = tuple(a + (b - a) * q for a, b in zip(FOGO, FUMACA))
            op, fa, brilho = 0.9 - 0.3 * q, math.exp(-(lt - FAISCA) / 0.35), max(0.0, 0.9 - q)
    return {"brilho": brilho, "theta": th, "lift_adm": adm, "lift_esc": esc, "gas_cor": list(cor), "gas_op": op, "faisca": fa,
            "cam_ang": 0.45 + 0.3 * math.sin(t * 0.18), "cam_r": 31.0 - 2.0 * ease((t - 3) / 8), "cam_y": 6.5,
            "cam_alvo": 3.3}


FILME = tres.Filme("motor.js", estado)


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)


def fase(i):
    n, nome, cor = FASES[i]
    return {"big": n, "sub": nome, "dots": (DOTS, i), "color": cor}


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["This is what's happening inside your car's engine, right now, thousands of times a minute."],
        {"title": "HOW A CAR ENGINE ACTUALLY WORKS"}, tail=0.2),
    seg(["Step one, intake. The piston drops, the blue valve opens, and air and fuel rush in."], fase(0)),
    seg(["Step two, compression. Both valves close, and the piston squeezes the mix into a tiny space."], fase(1)),
    seg(["Step three, power. The spark plug fires, and the blast shoves the piston down."], fase(2),
        sfx=[(0, FAISCA, "ding")]),
    seg(["Step four, exhaust. The red valve opens, and the piston pushes the burnt gas out."], fase(3)),
    seg(["Then it repeats. At three thousand RPM, every cylinder fires twenty five times a second."],
        {"big": "25x", "sub": "EVERY SECOND", "color": YELLOW}),
    seg(["Did you know this was happening under your hood? Tell me in the comments!"],
        {"title": "DID YOU KNOW THIS?"}, tail=0.6),
]

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=FILME.renderizar)
