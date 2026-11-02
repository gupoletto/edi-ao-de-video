"""What happens if an elevator cable snaps? (cinematic 3D). Tue 03/11/2026, 3D queue: "elevator cable snaps".

Shots: a glass elevator rides up the outside of an office tower -> the camera flies to the car roof and its cables ->
slow motion: all the cables snap and the car starts to fall -> up top, the overspeed governor spins too fast, its
flyweights swing out and its jaw grabs the governor rope -> at the car, that rope pulls the safety wedges up into the
guide rails (sparks) and the car stops -> real-speed replay from outside -> Quark asks the question.

Facts / physics:
- traction elevators hang from several steel hoist ropes (typically 4 to 8); codes require a large safety factor
  (around 10 or more for the set), so a single rope can hold the empty or loaded car on its own;
- the overspeed governor is a separate sheave driven by its own rope that is tied to the car; above a set speed
  (about 115-125 % of rated speed) centrifugal flyweights trip it and a jaw grips the governor rope;
- the rope, now stopped, lifts the safety-gear linkage on the moving car: wedges ride up between the car frame and
  the guide rails and brake by friction ("progressive safety gear");
- codes keep the average braking deceleration between 0.2 g and 1 g (EN 81-20); we use 0.6 g;
- here: car at rest when the ropes snap, rated 1.75 m/s, governor trips at 2.2 m/s (t = 2.2 / 9.81 = 0.22 s, 0.25 m
  of fall), wedges bite 0.03 s later (2.5 m/s, 0.32 m), stop after 2.5^2 / (2 * 0.6 * 9.81) = 0.53 m more:
  total drop 0.84 m (< 1 m), total time 0.68 s (< 1 s);
- Elisha Otis demonstrated his safety brake in 1854 (New York Crystal Palace), cutting the only rope of a platform
  he was standing on.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import BLUE, PINK, WHITE, YELLOW, Seg, pill, render, text_center  # noqa: E402

G = 9.81
V_RATED = 1.75
V_TRIP = 2.2
T_TRIP = V_TRIP / G
T_ENG = T_TRIP + 0.03
V_ENG = G * T_ENG
DEC = 0.6 * G
T_STOP = T_ENG + V_ENG / DEC
Y_STOP = 24.0              # piso da cabine quando para (m)
CH = 2.5                   # altura da cabine (igual ao elevador.js)
ZC = 1.45
TOPO = 46
GX, GZ, GR = -1.75, 2.05, 0.36
ENGATE = Y_STOP + CH + 0.4
QUEBRA = ENGATE + 2.0      # onde os cabos rompem


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mistura(a, b, k):
    return [x + (y - x) * k for x, y in zip(a, b)]


def queda(tp):
    """Quanto a cabine já desceu (m) e a velocidade (m/s, para baixo) no tempo físico tp (0 = rompimento)."""
    if tp <= 0:
        return 0.0, 0.0
    if tp < T_ENG:
        return G * tp * tp / 2, G * tp
    d0 = G * T_ENG ** 2 / 2
    if tp < T_STOP:
        dt = tp - T_ENG
        return d0 + V_ENG * dt - DEC * dt * dt / 2, V_ENG - DEC * dt
    return d0 + V_ENG ** 2 / (2 * DEC), 0.0


def altura(tp):
    """y do piso da cabine: subindo a 1,75 m/s, freia até parar no andar e, depois do rompimento, cai e para."""
    if tp > 0:
        return Y_STOP - queda(tp)[0]
    d = -tp
    a = V_RATED / 1.0
    if d <= 1.0:
        return Y_STOP - a * d * d / 2
    return Y_STOP - V_RATED * (d - 0.5)


def seg_de(t, segs):
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    return k, t - segs[k].t0


JANELAS = {2: (0.0, 0.12), 3: (0.12, T_ENG + 0.02), 4: (T_ENG + 0.02, T_STOP + 0.05)}
REPLAY0 = -1.6


def tempo_fisico(t, segs):
    """Tempo físico (s, 0 = rompimento): real até o rompimento, câmera lenta nos segs 2-4, replay real no 5."""
    k, lt = seg_de(t, segs)
    if k <= 1:
        return t - segs[2].t0
    if k in JANELAS:
        a, b = JANELAS[k]
        return a + (b - a) * min(1.0, lt / (segs[k].dur - 0.4))
    if k == 5:
        return REPLAY0 + lt
    return REPLAY0 + segs[5].dur + lt


def cam_cabos(yc):
    """Teto da cabine e o ponto de rompimento (2 m acima) no mesmo quadro."""
    return [4.6, yc + CH + 1.4, ZC + 9.6], [0.0, yc + CH + 1.0, ZC]


def cam_abertura(yc, q):
    """Plano aberto (praça, prédio, céu) que se aproxima da cabine subindo."""
    cam = mistura([26.0, 5.0, 50.0], [15.0, yc - 1.0, ZC + 27.0], q)
    alvo = mistura([0.0, 16.0, 0.0], [0.0, yc + 2.0, ZC], q)
    return cam, alvo


def cam_gov():
    return [-0.1, TOPO - 0.7, GZ + 4.4], [GX + 0.2, TOPO - 1.55, GZ]


def cam_freio(yc):
    return [-3.3, yc + 0.45, ZC + 3.6], [-0.95, yc - 0.05, ZC]


def cam_largo(yc, orb=0.0):
    alvo = [0.0, yc + 1.2, ZC]
    return [7.5 - 4 * orb, yc + 3.0, ZC + 14.0 + 1.5 * orb], alvo


def estado(t, segs):
    k, lt = seg_de(t, segs)
    tp = tempo_fisico(t, segs)
    yc = altura(tp)
    desc, vel = queda(tp)
    if k == 0:  # de fora: o prédio e a cabine de vidro subindo; câmera baixa, subindo junto
        cam, alvo = cam_abertura(yc, ease(lt / segs[0].dur))
        fov = 42
    elif k == 1:  # voa até o teto da cabine e os cabos
        q = ease(lt / (segs[1].dur * 0.75))
        c0, a0 = cam_abertura(yc, 1.0)
        c1, a1 = cam_cabos(yc)
        cam, alvo, fov = mistura(c0, c1, q), mistura(a0, a1, q), 42 - 4 * q
    elif k == 2:  # câmera lenta: os cabos arrebentam (câmera parada no ponto onde a cabine parou)
        cam, alvo = cam_cabos(Y_STOP)
        fov = 38
    elif k == 3:  # sobe até o regulador, no alto do poço
        q = ease(lt / 1.0)
        c0, a0 = cam_cabos(Y_STOP)
        c1, a1 = cam_gov()
        cam, alvo, fov = mistura(c0, c1, q), mistura(a0, a1, q), 38
    elif k == 4:  # desce até o freio de segurança, acompanhando a cabine
        q = ease(lt / 1.0)
        c0, a0 = cam_gov()
        c1, a1 = cam_freio(yc)
        cam, alvo, fov = mistura(c0, c1, q), mistura(a0, a1, q), 38 - 4 * q
    else:  # replay em velocidade real, de fora, e o final
        orb = 0.0 if k == 5 else ease(lt / 4.0)
        cam, alvo = cam_largo(Y_STOP, orb)
        fov = 40
    # regulador: a corda do lado da cabine anda com ela até a garra fechar
    corda = min(desc, queda(T_TRIP + 0.005)[0]) if tp > 0 else -(Y_STOP - yc)
    gov = corda / GR
    if tp <= 0:  # subindo: a polia gira com a cabine e os pesos abrem um pouco (velocidade normal)
        pesos = 0.6 * (V_RATED * min(1.0, -tp) / V_TRIP) ** 2
    else:
        pesos = min(1.0, (vel / V_TRIP) ** 2) if tp < T_TRIP else 1.0
    garra = ease((tp - T_TRIP) / 0.02)
    cunha = ease((tp - T_TRIP) / 0.03)
    atrito = 1.0 if T_ENG < tp < T_STOP else 0.0
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "ts": tp, "carro": yc, "carroIni": Y_STOP,
            "cabos": (tp * 2.2 if k in (2, 3, 4) else tp * 1.2) if tp > 0 else 0.0, "quebra": QUEBRA,
            "faisca": min(1.0, tp / 0.12) if 0 < tp < 0.12 else 0.0, "gov": gov, "pesos": pesos,
            "garra": garra, "cunha": cunha, "atrito": atrito, "raiox": 1.0 if k in (2, 3, 4) else 0.0}


FILME = tres.Filme("elevador.js", estado)
SEGS_CONSTRUIDOS = []


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)
    k = SEGMENTS.index(s) if s in SEGMENTS else -1
    if 2 <= k <= 4:  # cronômetro do tempo real e a velocidade dentro da câmera lenta
        tp = tempo_fisico(s.t0 + t, SEGS_CONSTRUIDOS)
        pill(ctx, "SLOW MOTION", 540, 470, WHITE, 1.0, size=30)
        text_center(ctx, f"{max(0.0, tp):.2f} s", 540, 560, 64, YELLOW, "ExtraBold")
        text_center(ctx, f"{queda(tp)[1]:.1f} m/s", 540, 616, 40, WHITE, "Bold")
    elif k == 5:
        pill(ctx, "REAL SPEED", 540, 470, PINK, 1.0, size=30)


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["What happens if an elevator cable snaps?"], {"title": "WHAT IF THE ELEVATOR CABLE SNAPS?"}, tail=0.4),
    seg(["First, it's never just one cable. There are four to eight, and each one can hold the car alone."],
        {"big": "4-8 CABLES", "sub": "EACH CAN HOLD THE CAR", "color": BLUE}, tail=0.3),
    seg(["But say they all snap at once. The car drops."], {"big": "SNAP!", "sub": "FREE FALL", "color": PINK},
        sfx=[(0, 0.2, "whoosh")], tail=0.6),
    seg(["Up top, the speed governor spins too fast. Its weights fly out, and it grabs its rope."],
        {"big": "GOVERNOR", "sub": "SPINS TOO FAST = TRIP", "color": YELLOW}, sfx=[(0, 0, "whoosh")]),
    seg(["That rope yanks steel wedges into the rails. Sparks fly, and the car stops in less than a meter."],
        {"big": "SAFETY BRAKES", "big_size": 90, "sub": "STOPS IN < 1 METER", "color": WHITE},
        sfx=[(0, 0, "whoosh")]),
    seg(["In real time, it's over in under a second. Elisha Otis showed off this brake in 1854."],
        {"big": "SINCE 1854", "sub": "THE OTIS SAFETY BRAKE", "color": BLUE}, tail=0.4),
]
SEGMENTS.append(pq.seg_pergunta("Stairs or elevator after this?", "STAIRS OR ELEVATOR?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    SEGS_CONSTRUIDOS[:] = segs
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
