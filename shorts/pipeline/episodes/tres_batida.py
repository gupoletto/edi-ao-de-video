"""What happens when a car hits a tree at 30 mph? (cinematic 3D, crash-test style). How it works 3D.

Shots: a car drives down a country road (tracking shot) -> wide shot, the car drifts off the road -> slow motion:
the front crumples like an accordion -> x-ray: the airbag inflates, the seatbelt holds the crash-test dummy ->
real-speed replay -> Quark asks the question.

Physics / facts:
- 30 mph = 13.4 m/s; hitting something solid at that speed is like falling v^2 / 2g = 9.2 m, about a 3-story building;
- crumple of ~0.6 m (about 2 ft): constant deceleration a = v^2 / (2 * 0.6) = 150 m/s^2 (~15 g), stop time
  t = v / a = 0.09 s ("about a tenth of a second");
- airbags inflate in roughly 20-30 ms after the sensor triggers (~15 ms after impact), faster than a blink;
- the belted dummy keeps moving forward until belt and airbag stop it (~0.2 m of travel), then rebounds.
No people are shown: only a crash-test dummy, no injuries.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import BLUE, PINK, WHITE, YELLOW, Seg, pill, render, text_center  # noqa: E402

V0 = 13.4                     # m/s (30 mph)
CRUSH = 0.6                   # m
A = V0 ** 2 / (2 * CRUSH)     # m/s^2
T_STOP = V0 / A               # ~0.089 s
ARV = (0.0, -4.6)             # árvore (x, z), igual ao cenas3d/batida.js
TH = 0.06                     # rumo do carro (rad): sai da pista em direção à árvore
D = (math.cos(TH), -math.sin(TH))
XF = 2.25                     # meio comprimento do carro
F = (ARV[0] - D[0] * 0.47, ARV[1] - D[1] * 0.47)   # ponto do para-choque no contato


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mistura(a, b, k):
    return [x + (y - x) * k for x, y in zip(a, b)]


def amassado(tp):
    if tp <= 0:
        return 0.0
    if tp < T_STOP:
        return V0 * tp - A * tp * tp / 2
    return CRUSH - 0.05 * ease((tp - T_STOP) / 0.15)  # pequeno rebote


def boneco(tp):
    """Deslocamento do boneco para a frente (m), relativo ao carro."""
    if tp <= 0:
        return 0.0
    t1 = math.sqrt(2 * 0.12 / A)          # cinto começa a segurar após 0,12 m
    if tp < t1:
        return A * tp * tp / 2
    vrel = A * t1
    dec = 180.0
    t2 = t1 + vrel / dec
    if tp < t2:
        dt = tp - t1
        return 0.12 + vrel * dt - dec * dt * dt / 2
    pico = 0.12 + vrel ** 2 / (2 * dec)
    return pico - (pico - 0.05) * ease((tp - t2) / 0.15)


def airbag(tp):
    if tp < 0.015:
        return 0.0
    if tp < 0.045:
        return ease((tp - 0.015) / 0.03)
    return 1.0 - 0.35 * ease((tp - 0.09) / 0.3)


def seg_de(t, segs):
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    return k, t - segs[k].t0


def tempo_fisico(t, segs):
    """Tempo físico (s, 0 = contato) para o tempo do vídeo t: real até a batida, câmera lenta, replay real."""
    k, lt = seg_de(t, segs)
    chegada = segs[2].t0
    if k <= 1:
        return t - chegada
    janelas = {2: (0.0, 0.015), 3: (0.015, 0.05), 4: (0.05, 0.11)}
    if k in janelas:
        a, b = janelas[k]
        return a + (b - a) * min(1.0, lt / (segs[k].dur - 0.3))
    if k == 5:
        return -1.4 + lt  # replay em velocidade real
    return -1.4 + segs[5].dur + lt


def centro(tp):
    s = (XF - amassado(tp)) if tp > 0 else XF + V0 * (-tp)
    return [F[0] - D[0] * s, F[1] - D[1] * s]


def estado(t, segs):
    k, lt = seg_de(t, segs)
    tp = tempo_fisico(t, segs)
    c = centro(tp)
    cabine = [c[0] - D[0] * 0.2, 1.0, c[1] - D[1] * 0.2 + 0.42]
    if k == 0:  # câmera acompanhando o carro, por trás e de lado
        cam = [c[0] - 4.2, 1.5, c[1] + 5.6]
        alvo = [c[0] + 2.6, 0.7, c[1] - 0.3]
        fov = 40
    elif k == 1:  # câmera parada perto da árvore, o carro chegando
        ini_c, ini_a = [c[0] - 4.2, 1.5, c[1] + 5.6], [c[0] + 2.6, 0.7, c[1] - 0.3]
        q = ease(lt / 1.2)
        cam = mistura(ini_c, [ARV[0] - 13.0, 2.4, ARV[1] + 13.0], q)
        alvo = mistura(ini_a, [ARV[0] - 4.0, 1.4, ARV[1] + 0.5], q)
        fov = 40 - 4 * q
    elif k == 2:  # câmera lenta, de lado, perto da frente
        cam = [F[0] - 1.0, 2.4, F[1] + 6.4]
        alvo = [F[0] - 1.1, 0.75, F[1]]
        fov = 40
    elif k in (3, 4):  # raio-x: aproxima da cabine
        q = ease(lt / 1.4) if k == 3 else 1.0
        cam = mistura([F[0] - 1.0, 2.4, F[1] + 6.4], [cabine[0] + 0.6, 1.7, cabine[1] + 4.4], q)
        alvo = mistura([F[0] - 1.1, 0.75, F[1]], [cabine[0] + 0.2, 1.0, cabine[1]], q)
        fov = 38
    else:  # replay e final: plano aberto e alto
        orb = 0.0 if k == 5 else 0.15 * ease(lt / 4)
        cam = [ARV[0] + 6.0 - 3 * math.sin(orb), 4.2, ARV[1] + 10.5]
        alvo = [ARV[0] - 2.4, 0.9, ARV[1] + 0.3]
        fov = 36
    batida = segs[2].t0 if k <= 4 else segs[5].t0 + 1.4
    tv = t - batida
    balanco = 0.06 * math.exp(-max(0, tv) * 0.9) * math.sin(max(0, tv) * 7) if tv > 0 else 0.0
    dist = (XF + V0 * 9) - (XF - amassado(tp) if tp > 0 else XF + V0 * (-tp))
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "carro": c, "rumo": TH, "amassa": amassado(tp),
            "boneco": boneco(tp), "airbag": airbag(tp), "raiox": ease(lt / 0.8) if k == 3 else (1.0 if k == 4 else 0.0),
            "roda": dist / 0.34, "balanco": balanco, "folhas": tv * 0.7 if tv > 0 else -1, "arvore": list(ARV)}


FILME = tres.Filme("batida.js", estado)


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)
    k = SEGMENTS.index(s) if s in SEGMENTS else -1
    if 2 <= k <= 4:  # cronômetro do tempo real dentro da câmera lenta
        tp = tempo_fisico(s.t0 + t, SEGS_CONSTRUIDOS)
        pill(ctx, "SLOW MOTION", 540, 470, WHITE, 1.0, size=30)
        text_center(ctx, f"{max(0.0, tp):.3f} s", 540, 560, 64, YELLOW, "ExtraBold")
    elif k == 5:
        pill(ctx, "REAL SPEED", 540, 470, PINK, 1.0, size=30)


SEGS_CONSTRUIDOS = []


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["What happens when a car hits a tree at thirty miles per hour?"],
        {"title": "WHAT HAPPENS WHEN A CAR HITS A TREE?"}, tail=0.2),
    seg(["It's like driving off a three story building."], {"big": "30 MPH", "sub": "= FALLING 3 STORIES", "color": YELLOW},
        tail=0.6),
    seg(["In slow motion. The bumper hits, and the front folds like an accordion. That's on purpose."],
        {"big": "CRUMPLE ZONE", "big_size": 90, "color": BLUE}, sfx=[(0, 0, "whoosh")]),
    seg(["The crash sensor fires the airbag. It inflates in about thirty milliseconds."],
        {"big": "AIRBAG", "sub": "FASTER THAN A BLINK", "color": WHITE}),
    seg(["The seatbelt holds you back, while two feet of crumpled metal soaks up the energy."],
        {"big": "SEATBELT", "sub": "HOLDS YOU IN PLACE", "color": PINK}),
    seg(["In real life, the whole crash is over in about a tenth of a second."],
        {"big": "0.1 s", "sub": "THE WHOLE CRASH", "color": YELLOW}, tail=0.4),
]
SEGMENTS.append(pq.seg_pergunta("Old steel car that doesn't bend, or a modern car that crumples? Which one would you "
                                "rather be in?", "STEEL TANK OR CRUMPLE ZONE?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    SEGS_CONSTRUIDOS[:] = segs
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
