"""What happens if a helicopter's engine fails? (cinematic 3D, autorotation). Fri 06/11/2026, 3D queue: helicopter.

Shots: a helicopter cruising over open country -> x-ray of the engine: it dies, the freewheel (sprag) clutch
disconnects it from the rotor -> wide side view: the pilot lowers collective, air now flows UP through the rotor and
keeps it spinning -> the controlled glide down -> the flare near the ground (nose up, the rotor's inertia brakes the
descent) -> soft touchdown on a field -> Quark asks the question.

Facts:
- every helicopter has a freewheeling unit (sprag/overrunning clutch) between engine and main gearbox, so a stopped
  engine does not drag the rotor;
- in autorotation the pilot lowers the collective (flatter blade pitch); the upward relative airflow through the
  disc drives the rotor like a windmill and keeps rotor RPM in the normal range;
- typical autorotative descent rates are roughly 1,500-2,000 ft/min (about 8-10 m/s); we use 9 m/s (~1,770 ft/min),
  forward speed around 60 knots (~30 m/s);
- near the ground the pilot flares (cyclic back: nose up), trading forward speed for lift, then raises the collective
  to use the stored rotor energy for a soft touchdown; autorotation is part of every helicopter pilot's training.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import FPS, PINK, WHITE, YELLOW, Seg, pill, render, text_center  # noqa: E402

V_CRUZEIRO, V_AUTO, DESC = 35.0, 28.0, 9.0      # m/s
X_POUSO = 520.0                                  # centro do campo de pouso (helicoptero.js)
W_ROTOR = 13.8                                   # rad/s (2,2 voltas/s: lê bem no vídeo)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mistura(a, b, k):
    return [x + (y - x) * k for x, y in zip(a, b)]


def seg_de(t, segs):
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    return k, t - segs[k].t0


_VOO = {}


def voo(segs):
    """Trajetória integrada no tempo do vídeo: x, y, velocidades, pitch, tempos da pane e do toque."""
    chave = tuple(round(s.t0, 3) for s in segs)
    if chave in _VOO:
        return _VOO[chave]
    total = segs[-1].t0 + segs[-1].dur
    dt = 1 / FPS
    ts = np.arange(0, total + 1, dt)
    t_pane = segs[1].t0 + 0.8
    t_auto = segs[2].t0
    t_flare = segs[4].t0
    d_flare = segs[4].dur
    t_toque = segs[5].t0 + 0.5
    vx, vy, pitch = [], [], []
    for t in ts:
        if t < t_auto:
            u, w, p = V_CRUZEIRO, 0.0, -0.06
        elif t < t_flare:
            k = ease((t - t_auto) / 2.0)
            u, w, p = V_CRUZEIRO + (V_AUTO - V_CRUZEIRO) * k, -DESC * k, -0.06 - 0.06 * k
        elif t < t_toque:
            k = ease((t - t_flare) / (t_toque - t_flare))
            u = V_AUTO + (2.0 - V_AUTO) * k
            w = -DESC + (DESC - 0.6) * k
            p = -0.12 + 0.30 * math.sin(math.pi * min(1.0, (t - t_flare) / (d_flare * 0.9))) + 0.17 * k
        else:
            k = ease((t - t_toque) / 1.0)
            u, w, p = 2.0 * (1 - k), 0.0, 0.05 * (1 - k)
        vx.append(u); vy.append(w); pitch.append(p)
    vx, vy = np.array(vx), np.array(vy)
    x = np.cumsum(vx) * dt
    y = np.cumsum(vy) * dt
    i_toque = int(t_toque / dt)
    x = x - x[i_toque] + X_POUSO
    y = y - y[i_toque]          # altura 0 no toque
    y[i_toque:] = 0.0
    _VOO[chave] = (ts, x, y, np.array(pitch), vy, t_pane, t_auto, t_flare, t_toque)
    return _VOO[chave]


def XRAY_C(x, y):
    return [x - 1.0, y + 5.0, 11.5]


def XRAY_A(x, y):
    return [x - 0.6, y + 3.0, 0]


def projeta(cam, alvo, fov, p):
    """Ponto 3D -> pixel na tela 1080x1920 (câmera pinhole do three.js, fov vertical)."""
    c, a, p = np.array(cam), np.array(alvo), np.array(p)
    fwd = (a - c) / np.linalg.norm(a - c)
    right = np.cross(fwd, [0, 1, 0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    d = p - c
    z = d @ fwd
    f = 960 / math.tan(math.radians(fov) / 2)
    return 540 + f * (d @ right) / z, 960 - f * (d @ up) / z


def amostra(arr, ts, t):
    return float(np.interp(t, ts, arr))


def estado(t, segs):
    k, lt = seg_de(t, segs)
    ts, X, Y, PIT, VY, t_pane, t_auto, t_flare, t_toque = voo(segs)
    x, y, pit = amostra(X, ts, t), amostra(Y, ts, t), amostra(PIT, ts, t)
    p = [x, y, 0.0]
    # câmera
    chase_c, chase_a = [x - 15, y + 4.5, 27], [x + 2, y + 1.8, 0]
    if k == 0:
        q = ease(lt / segs[0].dur)
        cam, alvo, fov = mistura([x - 45, y + 14, 80], chase_c, q), mistura([x + 5, y + 1, 0], chase_a, q), 40
    elif k == 1:
        q = ease(lt / 0.9)
        cam = mistura(chase_c, XRAY_C(x, y), q)
        alvo = mistura(chase_a, XRAY_A(x, y), q)
        fov = 40 - 6 * q
    elif k == 2:
        q = ease(lt / 0.9)
        cam = mistura(XRAY_C(x, y), [x - 3, y + 3.2, 21], q)
        alvo = mistura(XRAY_A(x, y), [x - 0.3, y + 2.6, 0], q)
        fov = 34 + 8 * q
    elif k == 3:
        q = ease(lt / 1.2)
        cam = mistura([x - 3, y + 3.2, 21], [x - 20, y + 9, 22], q)
        alvo = mistura([x - 0.3, y + 2.6, 0], [x + 2, y + 0.5, 0], q)
        fov = 42
    elif k == 4:  # o flare visto de lado, acompanhando, com o chão no quadro
        q = ease(lt / 1.0)
        lado_c = [x + 4, max(2.5, y * 0.55 + 2.5), 26]
        cam = mistura([x - 20, y + 9, 22], lado_c, q)
        alvo = mistura([x + 2, y + 0.5, 0], [x, y + 1.0, 0], q)
        fov = 42
    else:  # pouso e final: câmera parada no campo, perto
        q = ease(lt / 1.0) if k == 5 else 1.0
        x4 = amostra(X, ts, segs[5].t0)
        y4 = amostra(Y, ts, segs[5].t0)
        cam = mistura([x4 + 4, max(2.5, y4 * 0.55 + 2.5), 26], [X_POUSO + 9, 2.0, 19], q)
        alvo = mistura([x4, y4 + 1.0, 0], [x, y + 1.6, 0], q)
        fov = 40
    # rotor, motor, roda-livre, fluxo
    rotor = W_ROTOR * t - (0.0 if t < t_toque else W_ROTOR * (t - t_toque - (1 - math.exp(-(t - t_toque) / 2.5)) * 2.5))
    motor = 1 - ease((t - t_pane) / 0.5)
    eixo = 40 * min(t, t_pane) + (0 if t < t_pane else 40 * 0.6 * (1 - math.exp(-(t - t_pane) / 0.6)))
    roda = ease((t - t_pane - 0.3) / 0.3)
    passo = 0.12 if t < t_auto else (0.02 if t < t_toque - 0.8 else 0.22)
    if t < t_pane:
        fluxo = -1.0
    elif t < t_auto:
        fluxo = -1.0 * (1 - ease((t - t_pane) / 1.0))
    elif t < t_toque:
        fluxo = ease((t - t_auto) / 1.5)
    else:
        fluxo = 1 - ease((t - t_toque) / 0.6)
    raiox = ease(lt / 0.6) if k == 1 else (1 - ease(lt / 0.6) if k == 2 else 0.0)
    xp = amostra(X, ts, t_pane)
    yp = amostra(Y, ts, t_pane)
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "pos": p, "pitch": pit, "rotor": rotor,
            "cauda": rotor * 5.0, "motor": motor, "eixoMotor": eixo, "roda": roda, "passo": passo, "fluxo": fluxo,
            "raiox": raiox, "fumaca": (t - t_pane) if t > t_pane else -1.0, "fumacaX": [xp - 1.4, yp + 3.0, 0.0],
            "poeira": (t - t_toque) if t > t_toque else -1.0,
            "luzAlerta": (0.5 + 0.5 * math.sin(t * 14)) if t_pane < t < t_toque else 0.0}


FILME = tres.Filme("helicoptero.js", estado)
SEGS_CONSTRUIDOS = []


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)
    k = SEGMENTS.index(s) if s in SEGMENTS else -1
    if k == 1 and SEGS_CONSTRUIDOS and t > 0.9:  # rótulos das peças, projetados da posição 3D real
        e = estado(s.t0 + t, SEGS_CONSTRUIDOS)
        x, y = e["pos"][0], e["pos"][1]
        a = min(1.0, (t - 0.9) / 0.3)
        for (px, py), rot, cor in ((( x - 1.35, y + 3.0), "ENGINE", (1.0, 0.55, 0.2) if e["motor"] > 0.5 else (0.6, 0.6, 0.65)),
                                  ((x - 0.05, y + 3.0), "FREEWHEEL", (0.3, 0.9, 0.5) if e["roda"] < 0.5 else PINK)):
            sx, sy = projeta(e["cam"], e["alvo"], e["fov"], [px, py, 0.0])
            ctx.set_source_rgba(1, 1, 1, a)
            ctx.set_line_width(4)
            ctx.move_to(sx, sy)
            ctx.line_to(sx, sy + 170 if rot == "ENGINE" else sy - 170)
            ctx.stroke()
            pill(ctx, rot, sx, sy + 200 if rot == "ENGINE" else sy - 200, cor, a, size=34)
    if 2 <= k <= 4 and SEGS_CONSTRUIDOS:
        ts, X, Y, PIT, VY, *_ = voo(SEGS_CONSTRUIDOS)
        tt = s.t0 + t
        alt_ft = max(0.0, amostra(Y, ts, tt)) * 3.281
        desc_fpm = -amostra(VY, ts, tt) * 196.85
        text_center(ctx, f"{alt_ft:,.0f} ft", 540, 520, 60, YELLOW, "ExtraBold")
        text_center(ctx, f"DESCENT {desc_fpm:,.0f} ft/min", 540, 570, 32, WHITE, "Bold")
        pill(ctx, "ROTOR RPM 100%", 540, 630, (0.30, 0.90, 0.50), 1.0, size=28)


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["What happens if a helicopter's engine fails in the air? Does it just drop like a rock?"],
        {"title": "WHAT IF THE HELICOPTER ENGINE FAILS?"}, tail=0.2),
    seg(["The engine dies. But a freewheel clutch lets the rotor keep spinning on its own."],
        {"big": "ENGINE OUT", "sub": "THE FREEWHEEL CLUTCH LETS GO", "color": PINK}, tail=0.3,
        sfx=[(0, 1.0, "whoosh")]),
    seg(["The pilot flattens the blades. Now air rushes up through the rotor and keeps it turning, like a windmill."],
        {"big": "AUTOROTATION", "big_size": 96, "sub": "AIR FLOWS UP, ROTOR KEEPS SPINNING", "color": YELLOW}, tail=0.2),
    seg(["It glides down at about two thousand feet per minute, and the pilot can still steer to a safe spot."],
        {"big": "THE GLIDE", "sub": "~2,000 FT PER MINUTE", "color": WHITE}, tail=0.2),
    seg(["Near the ground, the pilot pulls the nose up. The spinning rotor brakes the fall."],
        {"big": "THE FLARE", "sub": "NOSE UP, SPEED DOWN", "color": (0.36, 0.78, 0.98)}, tail=0.3,
        sfx=[(0, 0, "whoosh")]),
    seg(["Then the rotor's last energy sets it down softly. Every helicopter pilot trains for this."],
        {"big": "SAFE LANDING", "sub": "PRACTICED BY EVERY PILOT", "color": (0.30, 0.90, 0.50)}, tail=0.4),
]
SEGMENTS.append(pq.seg_pergunta("Helicopter or plane, which feels safer?", "HELICOPTER OR PLANE?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    SEGS_CONSTRUIDOS[:] = segs
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
