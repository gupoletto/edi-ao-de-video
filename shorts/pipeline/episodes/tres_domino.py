"""What happens if each domino is 1.5x bigger? (cinematic 3D, domino amplification). Sat 14/11/2026, topic:
satisfying (physics). Search 14/11: "domino satisfying", median 2.28M (top 24M "1 to 100 domino chain reaction").

Facts:
- physicist Lorne Whitehead (American Journal of Physics, 1983) showed a domino can topple one about 1.5 times
  larger; a chain of 13 growing dominoes amplifies the energy of the first tap about two billion times;
- starting from 5 mm, domino number n is 5 mm x 1.5^(n-1): #13 is ~0.65 m, #15 ~1.5 m (taller than a person),
  #29 ~430 m, about the height of the Empire State Building (381 m roof, 443 m to the tip);
- a falling domino takes longer the taller it is (~ square root of the height), so the chain slows down as it grows:
  the first ones fall in hundredths of a second, the last one takes several seconds.
Each domino's fall is a simple time function (start when the previous one has tilted ~30 degrees), timed with the
sqrt(h) law and sped up to fit the video.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import GREEN, PINK, WHITE, YELLOW, Seg, render, text_center  # noqa: E402

N, H0, F = 29, 0.005, 1.5
H = [H0 * F ** i for i in range(N)]
E = [h * 0.18 for h in H]
X = []
_x = 0.0
for i in range(N):
    X.append(_x)
    _x += E[i] + H[i] * 0.5


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ease_in(x):
    x = min(1.0, max(0.0, x))
    return x * x


def seg_de(t, segs):
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    return k, t - segs[k].t0


_CACHE = {}


def tempos(segs):
    """Início da queda de cada peça, no tempo do vídeo. Tempo de queda ~ 1,2 sqrt(h/g), acelerado para caber."""
    chave = round(segs[1].t0, 3), round(segs[5].t0, 3)
    if chave in _CACHE:
        return _CACHE[chave]
    T = [1.2 * math.sqrt(h / 9.81) for h in H]
    ini = [0.0]
    for i in range(1, N):
        ini.append(ini[-1] + 0.45 * T[i - 1])
    # sincroniza com a narração: peça 1 no segmento 1, a 13ª no 3, a 25ª no 4 e a 29ª no 5 (tempo deformado por
    # trechos, mantendo a ordem e o "cada vez mais devagar" dentro de cada trecho)
    import numpy as np
    ancoras_i = [0, 12, 24, 28]
    alvo = [segs[1].t0 + 1.6, segs[3].t0 + 0.6, segs[4].t0 + 1.0, segs[5].t0 + 0.6]
    bruto = [ini[i] for i in ancoras_i]
    novo_ini = [float(np.interp(a, bruto, alvo)) for a in ini]
    inc = [(alvo[j + 1] - alvo[j]) / (bruto[j + 1] - bruto[j]) for j in range(3)]
    novo_dur = []
    for i in range(N):
        j = 0 if i < 12 else (1 if i < 24 else 2)
        novo_dur.append(T[i] * (inc[j] if i < 28 else 2.6 / T[i]))
    _CACHE[chave] = (novo_ini, novo_dur)
    return _CACHE[chave]


def estado(t, segs):
    ini, dur = tempos(segs)
    ang = []
    for i in range(N):
        u = (t - ini[i]) / dur[i]
        fim = math.radians(90 if i == N - 1 else 72)
        ang.append(fim * ease_in(u) if u < 1 else fim)
    # peça "ativa" (contínua): interpola em escala log entre as peças que estão caindo agora
    a = 0.0
    for i in range(N):
        if t >= ini[i]:
            a = i + min(1.0, (t - ini[i]) / max(1e-6, (ini[i + 1] - ini[i]) if i + 1 < N else dur[i]))
    a = max(0.0, min(N - 1.0, a + 0.4))
    h = H0 * F ** a
    i0 = int(min(N - 2, a))
    xa = X[i0] + (X[i0 + 1] - X[i0]) * (a - i0)
    k, lt = seg_de(t, segs)
    if k == 0:
        h = H0 * 2.2
        xa = X[2]
    dist = 2.6 * h + 0.03
    cam = [xa + 0.9 * dist, 0.9 * h + 0.004, 1.5 * dist]
    alvo = [xa + 0.3 * h, 0.45 * h, 0.0]
    fov = 46
    emp = 0.0
    if k >= 5:  # final: recua para mostrar a 29ª ao lado do Empire State
        q = ease(lt / 3.0) if k == 5 else 1.0
        xf = X[N - 1]
        cam = [c + (d - c) * q for c, d in zip(cam, [xf + 250, 230, 1550])]
        alvo = [c + (d - c) * q for c, d in zip(alvo, [xf + 20, 210, -90])]
        emp = ease(lt / 1.2) if k == 5 else 1.0
    perto = max(0.0005, min(cam[2], dist) * 0.01)
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "ang": ang, "empire": emp, "perto": perto,
            "_ativa": a}


FILME = tres.Filme("domino.js", estado)
SEGS = []


def fmt(h):
    if h < 0.01:
        return f"{h * 1000:.0f} mm"
    if h < 1:
        return f"{h * 100:.0f} cm"
    return f"{h:,.1f} m" if h < 10 else f"{h:,.0f} m"


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)
    k = SEGMENTS.index(s) if s in SEGMENTS else -1
    if not SEGS or k < 1 or k > 5:
        return
    e = estado(s.t0 + t, SEGS)
    n = int(round(min(N - 1, max(0, e["_ativa"] - 0.4))))
    text_center(ctx, f"DOMINO #{n + 1}", 540, 560, 40, WHITE, "ExtraBold")
    text_center(ctx, fmt(H[n]), 540, 630, 64, YELLOW, "ExtraBold")


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["Every domino here is one and a half times bigger than the one before."],
        {"title": "WHAT IF EACH DOMINO IS 1.5x BIGGER?"}, tail=0.2),
    seg(["The first one is just five millimeters tall. One tiny tap starts it all."],
        {"big": "5 MILLIMETERS", "big_size": 88, "color": WHITE}, tail=0.2),
    seg(["A domino can knock over one about fifty percent bigger, so the chain keeps growing."],
        {"big": "1.5x EACH TIME", "big_size": 88, "sub": "LORNE WHITEHEAD, 1983", "color": YELLOW}, tail=0.2),
    seg(["Thirteen of them already multiply the energy of that tap two billion times."],
        {"big": "2 BILLION x", "sub": "THE ENERGY OF THE FIRST TAP", "color": PINK}, tail=0.2),
    seg(["And the bigger they get, the slower they fall. The giant ones take whole seconds."],
        {"big": "SLOWER", "sub": "BIG THINGS FALL SLOWLY", "color": (0.36, 0.78, 0.98)}, tail=0.2),
    seg(["Domino number twenty nine? As tall as the Empire State Building."],
        {"big": "#29", "sub": "430 METERS TALL", "color": GREEN}, tail=2.4, sfx=[(0, 1.0, "whoosh")]),
]
SEGMENTS.append(pq.seg_pergunta("Would you push the first domino?", "WOULD YOU PUSH IT?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    SEGS[:] = segs
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
