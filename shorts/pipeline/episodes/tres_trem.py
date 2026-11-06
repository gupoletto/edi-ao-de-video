"""What happens if a plane's landing gear won't come down? (cinematic 3D, gravity extension). Sat 07/11/2026,
3D queue #4 (landing gear), rewritten as "what happens if" (the 3D titles that work, see tendencias/2026-11-05.md).

Shots: an airliner on final approach over the runway -> the pilot selects gear down, the hydraulic actuators should
push the gear out but nothing moves -> red "gear unsafe" lights -> the manual release opens the uplocks and the gear
free-falls into place -> three green lights -> touchdown with tire smoke -> Quark asks the question.

Facts:
- airliner landing gear is normally extended and retracted by hydraulic actuators; while retracted it hangs on
  mechanical uplocks;
- airliners have an alternate (manual / gravity) extension: on the Boeing 737 the manual gear extension handles release
  the uplocks, on the Airbus A320 a crank handle does the same; the gear then free-falls by gravity (helped by the
  airflow) until the downlocks engage;
- the cockpit shows one light per gear leg: red = in transit or unsafe, green = down and locked ("three green");
- a normal approach is flown on a ~3 degree glide path at roughly 130-150 knots (we use 70 m/s, ~136 kt).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import GREEN, PINK, RED, WHITE, YELLOW, Seg, pill, render, round_rect, text_center  # noqa: E402

V = 70.0                       # m/s na aproximação
TAN_GLIDE = math.tan(math.radians(3))
X_TOQUE = 0.0                  # ponto de toque na pista (aviao.js)
Y_RODA = 0.62                  # raio da roda principal: origem do avião acima do chão com o trem embaixo


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mistura(a, b, k):
    return [x + (y - x) * k for x, y in zip(a, b)]


def seg_de(t, segs):
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    return k, t - segs[k].t0


def t_toque(segs):
    return segs[5].t0 + 0.8


def voo(t, segs):
    """Posição (x, y), pitch, velocidade de avanço: rampa de 3 graus, arredondamento ("flare") nos últimos 3 s, toque e
    rolagem freando."""
    tt = t_toque(segs)
    dt = tt - t
    if dt > 3.0:
        return X_TOQUE - V * dt, Y_RODA + V * dt * TAN_GLIDE, 0.05, V
    if dt > 0:
        h3, s3, s0 = V * 3 * TAN_GLIDE, V * TAN_GLIDE, 0.7  # Hermite: altura e razão de descida nas duas pontas
        u = dt / 3.0
        y = (h3 * (3 * u * u - 2 * u ** 3) + s3 * 3 * (u ** 3 - u ** 2) + s0 * 3 * (u - 2 * u * u + u ** 3))
        return X_TOQUE - V * dt, Y_RODA + max(0.0, y), 0.05 + 0.05 * ease(1 - u), V
    tau = -dt
    a = 3.0
    v = max(0.0, V - a * tau)
    x = X_TOQUE + V * tau - 0.5 * a * tau * tau
    return x, Y_RODA, 0.10 * (1 - ease(tau / 1.8)), v


def trem(t, segs):
    """0 = recolhido, 1 = embaixo e travado. Queda livre depois que as travas abrem, com um quique no fim."""
    k, lt = seg_de(t, segs)
    if k <= 2:
        return 0.02 * math.sin(lt * 30) * ease((lt - 1.2) / 0.3) * (1 - ease((lt - 3.0) / 0.4)) if k == 1 else 0.0
    t_solta = segs[3].t0 + T_SOLTA
    tau = t - t_solta
    if tau <= 0:
        return 0.0
    queda = 0.85
    if tau < queda:
        return (tau / queda) ** 2
    d = tau - queda
    return 1 - 0.07 * math.exp(-6 * d) * abs(math.sin(14 * d))


T_SOLTA = 2.6   # s depois do início do segmento 3 em que as travas abrem ("...the locks open")


def estado(t, segs):
    k, lt = seg_de(t, segs)
    x, y, pitch, v = voo(t, segs)
    tt = t_toque(segs)
    g = trem(t, segs)
    hidr = 0.0
    falha = 0.0
    if k == 1:
        hidr = ease((lt - 1.0) / 0.4) * (0.75 + 0.25 * math.sin(lt * 12))
        falha = ease((lt - segs[1].dur + 1.2) / 0.8)
        hidr *= 1 - 0.7 * falha
    elif k == 2:
        falha, hidr = 1.0, 0.25 * (0.5 + 0.5 * math.sin(lt * 9))
    elif k >= 3:
        falha = 1.0
    trava = ease((t - segs[3].t0 - T_SOLTA + 0.3) / 0.3) if k >= 3 else 0.0
    # rodas: giram depois do toque (v / raio)
    roda = 0.0
    if t > tt:
        tau = t - tt
        roda = (V * tau - 1.5 * tau * tau) / Y_RODA
    # câmeras
    frente_baixo = ([x + 21, y - 2.6, 15], [x - 3, y + 1.8, 0.5], 40)
    if k == 0:
        q = ease(lt / 4.0)
        cam = [x + 60 - 20 * q, y + 9 - 3 * q, 52 - 10 * q]
        alvo = [x - 3, y + 3, 0]
        fov = 40
    elif k in (1, 2, 3):
        if k == 1:
            q = ease(lt / 1.2)
            c0 = [x + 40, y + 6, 42]
            cam = mistura(c0, frente_baixo[0], q)
            alvo = mistura([x - 3, y + 3, 0], frente_baixo[1], q)
            fov = 40
        else:
            cam, alvo, fov = frente_baixo
            if k == 3:  # abre um pouco para ver as duas pernas caírem
                q = ease(lt / 2.0)
                cam = mistura(cam, [x + 22, y - 3.0, 16], q)
    elif k == 4:
        q = ease(lt / 1.4)
        cam = mistura([x + 22, y - 3.0, 16], [x + 40, y + 0.8, 17], q)
        alvo = mistura(frente_baixo[1], [x - 1, y + 2.3, 0], q)
        fov = 40 - 2 * q
    else:
        fixo = [X_TOQUE + 360, 3.0, 60]
        if k == 5:
            q = ease(lt / 1.0)
            x4, y4, _, _ = voo(segs[5].t0, segs)
            cam = mistura([x4 + 40, y4 + 0.8, 17], fixo, q)
        else:
            cam = fixo
        alvo = [x, y + 3.0, 0]
        fov = 36 - 14 * ease((t - tt) / 4.0)
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "pos": [x, y, 0.0], "pitch": pitch, "trem": g,
            "hidr": hidr, "falha": falha, "roda": roda, "trava": trava,
            "fumaca": (t - tt) if t > tt else -1.0, "toqueX": X_TOQUE}


FILME = tres.Filme("aviao.js", estado)
SEGS_CONSTRUIDOS = []


def luzes(ctx, t, s, k):
    """Painel do trem: uma luz por perna (vermelha = em trânsito / insegura, verde = embaixo e travada)."""
    segs = SEGS_CONSTRUIDOS
    tt = s.t0 + t
    g = trem(tt, segs)
    cx, cy = 540, 560
    round_rect(ctx, cx - 210, cy - 70, 420, 150, 28)
    ctx.set_source_rgba(0.05, 0.06, 0.09, 0.88)
    ctx.fill()
    text_center(ctx, "LANDING GEAR", cx, cy - 32, 26, WHITE, "Bold")
    for i, (rot, atraso) in enumerate((("L", 0.0), ("NOSE", 0.12), ("R", 0.05))):
        x = cx - 130 + i * 130
        if k == 1 and t < 1.0:
            cor, a = (0.25, 0.25, 0.28), 1.0
        elif g >= 0.995 and tt > segs[3].t0 + T_SOLTA + 0.85 + atraso:
            cor, a = GREEN, 1.0
        else:
            cor, a = RED, (0.55 + 0.45 * (math.sin(tt * 10) > 0)) if k == 2 else 1.0
        ctx.arc(x, cy + 22, 26, 0, 2 * math.pi)
        ctx.set_source_rgba(*cor, a)
        ctx.fill()
        text_center(ctx, rot, x, cy + 76, 20, WHITE, "SemiBold", alpha=0.8)


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)
    k = SEGMENTS.index(s) if s in SEGMENTS else -1
    if 1 <= k <= 5 and SEGS_CONSTRUIDOS:
        luzes(ctx, t, s, k)
        if k == 2:
            pill(ctx, "GEAR UNSAFE", 540, 700, RED, min(1.0, t / 0.3), size=34)
        if k == 4 and t > 1.0:
            pill(ctx, "DOWN AND LOCKED", 540, 700, GREEN, min(1.0, (t - 1.0) / 0.3), size=34)


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["What happens if a plane's landing gear won't come down? Does it have to crash land?"],
        {"title": "WHAT IF THE LANDING GEAR FAILS?"}, tail=0.3),
    seg(["The pilot moves the gear lever, and hydraulic pistons should push the wheels down. Nothing moves."],
        {"big": "GEAR DOWN?", "sub": "HYDRAULICS SHOULD DO THE WORK", "color": YELLOW}, tail=0.2,
        sfx=[(0, 1.0, "whoosh")]),
    seg(["The hydraulics failed, and the wheels are still locked up."],
        {"big": "STUCK UP", "sub": "HYDRAULIC FAILURE", "color": PINK}, tail=0.3),
    seg(["So the pilot pulls a manual release. The locks open, and gravity drops the wheels."],
        {"big": "GRAVITY DROP", "big_size": 96, "sub": "NO HYDRAULICS NEEDED", "color": YELLOW}, tail=0.4),
    seg(["They swing down until the locks click in. Down and locked. Three green lights!"],
        {"big": "THREE GREEN", "sub": "ALL GEAR DOWN AND LOCKED", "color": GREEN}, tail=0.3),
    seg(["And the plane lands like nothing happened. Every airliner has this backup, and pilots train for it."],
        {"big": "SAFE LANDING", "sub": "EVERY AIRLINER HAS A BACKUP", "color": (0.36, 0.78, 0.98)}, tail=0.5),
]
SEGMENTS.append(pq.seg_pergunta("Would this make you nervous on a flight?", "WOULD YOU BE NERVOUS?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    SEGS_CONSTRUIDOS[:] = segs
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
