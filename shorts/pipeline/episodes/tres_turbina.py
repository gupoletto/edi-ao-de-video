"""How a jet engine actually works (cinematic 3D). Thu 05/11/2026, topic: how it works 3D.

Shots: airliner cruising above the clouds -> camera flies to the engine -> the nacelle is cut away -> suck, squeeze,
bang, blow with the airflow drawn as particles -> pull back to the plane -> Quark asks the question.

Facts (high-bypass turbofan, e.g. GE90 on the Boeing 777):
- big twin-jets weigh up to ~350 t at takeoff (777-300ER MTOW 351.5 t) -> "a three hundred ton plane";
- the fan moves over a ton of air per second (GE90: ~1,350 kg/s at takeoff);
- most of the air bypasses the core, and the bypass air makes most of the thrust (~80-90 % on high-bypass engines);
- overall pressure ratio ~40:1 (GE90-115B: ~42);
- combustion gas ~1,500 °C+, hotter than the nickel-alloy turbine blades can survive on their own (they are cooled by
  air flowing through tiny holes);
- the turbines drive the fan and the compressor through shafts; combustion is continuous, not explosions.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import BLUE, PINK, WHITE, YELLOW, Seg, render  # noqa: E402

E = (3.4, -2.55, 6.6)          # centro do motor no mundo (igual ao cenas3d/turbina.js)
FASES = [("1", "SUCK", BLUE), ("2", "SQUEEZE", WHITE), ("3", "BANG", (1.0, 0.55, 0.2)), ("4", "BLOW", PINK)]
DOTS = [f[0] for f in FASES]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mistura(a, b, k):
    return [x + (y - x) * k for x, y in zip(a, b)]


def orbita(ang, dist, alt, alvo):
    """Câmera ao redor do motor: ang 0 = de lado (z+), positivo = vai para a frente (x+)."""
    return [alvo[0] + math.sin(ang) * dist, alvo[1] + alt, alvo[2] + math.cos(ang) * dist]


def seg_de(t, segs):
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    return k, t - segs[k].t0


def estado(t, segs):
    k, lt = seg_de(t, segs)
    bob = 0.25 * math.sin(t * 0.7)
    eng = [E[0], E[1] + bob, E[2]]
    # ---- câmera ----
    largo_cam, largo_alvo = [58 - 6 * ease(t / 4), -11, 26 - 4 * ease(t / 4)], [0, -1, 1]  # abertura: avião vindo
    perto_alvo = [eng[0] + 0.5, eng[1] + 0.2, eng[2]]
    if k == 0:
        cam, alvo, fov = largo_cam, largo_alvo, 34
    elif k == 1:  # voa até o motor
        q = ease(lt / segs[1].dur * 1.15)
        cam = mistura(largo_cam, orbita(1.0, 14.5, -2.6, perto_alvo), q)
        alvo = mistura(largo_alvo, perto_alvo, q)
        fov = 34 + (30 - 34) * q
    elif k <= 6:  # explicação: órbita lenta, do quarto-frontal para o lado
        tt = t - segs[2].t0
        total = segs[6].t0 + segs[6].dur - segs[2].t0
        ang = 1.0 - 0.4 * ease(tt / total)
        cam, alvo, fov = orbita(ang, 14.5 - 1.5 * ease(tt / total), -2.6, perto_alvo), perto_alvo, 30
    else:  # recua até o avião inteiro, por trás e de lado
        q = ease(lt / 3.0)
        fim = [-30, 7, 36]  # por trás, de cima: o sol fica fora do quadro
        ini = orbita(0.6, 13.0, -2.6, perto_alvo)
        cam = mistura(ini, fim, q)
        alvo = mistura(perto_alvo, [3, -2, 0], q)
        fov = 30 + 4 * q
    # ---- motor ----
    giro = t * 2 * math.pi
    fogo = 0.0
    if k >= 5:
        fogo = ease((t - segs[5].t0 - 1.0) / 0.6)
    corte = 0.0 if k < 1 else ease((lt - (segs[1].dur - 1.4)) / 1.2) if k == 1 else 1.0
    if k >= 7:
        corte = 1 - ease(lt / 1.5)
    ate, bypass, nucleo, destaque = 9.0, 0.0, 0.0, ""
    if k == 2:      # suck: o ar entra até o fan
        ate, bypass, nucleo, destaque = 3.6 - 2.6 * ease(lt / 2.5), 1.0, 1.0, "fan"
    elif k == 3:    # bypass: o ar de fora passa em volta do núcleo
        ate, bypass, nucleo, destaque = 1.0 - 5.2 * ease(lt / 3.0), 1.0, 0.35, ""
    elif k == 4:    # squeeze
        ate, bypass, nucleo, destaque = -4.2 if lt > 3 else min(1.0, 1.3 - 1.4 * ease(lt / 2.5)), 0.45, 1.0, "comp"
        ate = max(-4.2, 1.3 - 1.5 * ease(lt / 2.5))
    elif k == 5:    # bang
        ate, bypass, nucleo, destaque = 0.0 - 0.6 * ease((lt - 1.0) / 1.0), 0.45, 1.0, "comb"
    elif k >= 6:    # blow (e depois tudo junto)
        ate = -0.6 - 3.6 * ease(lt / 2.5) if k == 6 else -4.2
        bypass, nucleo, destaque = (0.6 if k == 6 else 1.0), 1.0, ("turb" if k == 6 else "")
    if k <= 1:
        bypass = nucleo = 0.0
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "nuvem": t * 38.0, "rolagem": 0.0,
            "fan": giro * 1.1, "lp": giro * 1.1, "hp": giro * 2.3, "corte": corte, "fogo": fogo, "ate": ate,
            "bypass": bypass, "nucleo": nucleo, "destaque": destaque, "pulso": 0.5 + 0.5 * math.sin(t * 6)}


FILME = tres.Filme("turbina.js", estado)


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
    seg(["How does a jet engine push a three hundred ton plane through the sky?"],
        {"title": "HOW A JET ENGINE ACTUALLY WORKS"}, tail=0.1, sfx=[(0, 0, "whoosh")]),
    seg(["Let's cut one open.", 0.8], None, tail=0.1, sfx=[(0, 0.2, "whoosh")]),
    seg(["Step one, suck. The giant fan pulls in over a ton of air every second."], fase(0)),
    seg(["Most of it flows around the core. That bypass air makes most of the thrust."],
        {"big": "BYPASS", "sub": "MOST OF THE THRUST", "color": BLUE}),
    seg(["Step two, squeeze. The compressor crushes the rest to forty times its pressure."], fase(1)),
    seg(["Step three, bang. Fuel burns at around fifteen hundred degrees, hotter than the blades could survive."],
        fase(2), sfx=[(0, 1.0, "whoosh")]),
    seg(["Step four, blow. The hot gas spins the turbines, which turn the fan, and blasts out the back."], fase(3)),
    seg(["Suck, squeeze, bang, blow. All at once, nonstop, for the whole flight."],
        {"title": "SUCK · SQUEEZE · BANG · BLOW"}, tail=0.3),
]
SEGMENTS.append(pq.seg_pergunta("What should I cut open next? A rocket, or a helicopter?", "WHAT SHOULD I CUT OPEN NEXT?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True

if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=FILME.renderizar)
