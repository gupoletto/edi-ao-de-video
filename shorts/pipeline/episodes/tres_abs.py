"""What happens if you slam the brakes on a wet road? (cinematic 3D, ABS vs locked wheels). Wed 11/11/2026, 3D queue
(ABS on a wet road). Search 11/11: "abs brakes how it works", median 42.8k; "what if your car had no ABS?" 25k.

Shots: a red car without ABS brakes hard on a wet road; the wheels lock, the driver turns the wheel but a sliding
tire can't steer, and it slides straight into the cones -> the same situation for a blue car with ABS: the brakes
are released and reapplied many times a second, the wheels keep turning and the car steers around -> wide shot of
both outcomes -> Quark asks the question.

Facts:
- a locked (sliding) tire loses its lateral grip, so steering input does almost nothing; a rolling tire can brake
  and steer at the same time;
- ABS senses a wheel about to lock and briefly releases brake pressure, cycling roughly 15 times per second (the
  buzz felt in the pedal);
- ABS's main job is keeping steering control; on wet asphalt it usually also shortens the stop a little;
- ABS is required on new cars in the EU (since 2004 by industry agreement, mandatory with 2007-2009 type approval
  rules) and effectively in the US through the electronic stability control mandate (2012).
Kinematics below: constant deceleration (locked 3.0 m/s^2 shown, ABS 4.5 m/s^2), speeds around 26-27 m/s (~60 mph).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import GREEN, PINK, WHITE, YELLOW, Seg, pill, render, round_rect, text_center  # noqa: E402

ZV, ZA = -6.0, 6.0
R_RODA = 0.34
CONES_V = [(0.0, ZV + dz) for dz in (-1.6, -0.8, 0.0, 0.8, 1.6)]
CONES_A = [(0.0, ZA + dz) for dz in (-1.6, -0.8, 0.0, 0.8, 1.6)]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def mistura(a, b, k):
    return [x + (y - x) * k for x, y in zip(a, b)]


def seg_de(t, segs):
    k = next(i for i, s in enumerate(segs) if t < s.t0 + s.dur or i == len(segs) - 1)
    return k, t - segs[k].t0


def corrida(t, t_freio, t_alvo, x_alvo, v_alvo, a):
    """Velocidade constante até t_freio, depois desacelera a até parar; passa por x_alvo em t_alvo com v_alvo.
    Devolve (x, v, distância percorrida desde o início)."""
    v_b = v_alvo + a * (t_alvo - t_freio)
    x_b = x_alvo - (v_alvo * (t_alvo - t_freio) + 0.5 * a * (t_alvo - t_freio) ** 2)
    if t < t_freio:
        return x_b - v_b * (t_freio - t), v_b
    tau = min(t - t_freio, v_b / a)
    return x_b + v_b * tau - 0.5 * a * tau * tau, v_b - a * tau


def tempos(segs):
    return {"vf": segs[0].t0 + 1.2, "vh": segs[2].t0 + 0.6, "af": segs[3].t0 + 0.8, "ah": segs[4].t0 + 1.4}


def estado(t, segs):
    k, lt = seg_de(t, segs)
    T = tempos(segs)
    # vermelho (sem ABS): trava em vf, chega nos cones em vh a 8 m/s
    xv, vv = corrida(t, T["vf"], T["vh"], -XF_CONE, 8.0, 3.0)
    girov = (xv if t < T["vf"] else corrida(T["vf"], T["vf"], T["vh"], -XF_CONE, 8.0, 3.0)[0]) / R_RODA
    estv = 0.38 * ease((t - T["vf"] - 0.6) / 0.5) if t > T["vf"] else 0.0
    # azul (com ABS): começa no segmento 3
    if t < segs[3].t0 - 0.5:
        xa, va = -500.0, 0.0
    else:
        xa, va = corrida(t, T["af"], T["ah"], -XF_CONE, 9.0, 4.5)
    za = ZA + 3.6 * ease((xa + 24) / 20.0)
    dzdx = 3.6 * 6 * max(0.0, min(1.0, (xa + 24) / 20)) * (1 - max(0.0, min(1.0, (xa + 24) / 20))) / 20.0
    rumoa = -math.atan(dzdx)
    pulso = 0.12 * math.sin(t * 2 * math.pi * 15) if T["af"] < t and va > 0.5 else 0.0
    giroa = xa / R_RODA + pulso
    esta = 0.3 * math.sin(math.pi * max(0.0, min(1.0, (xa + 26) / 22))) if xa > -26 else 0.0
    # cones derrubados pelo vermelho
    cones = []
    for i, (cx, cz) in enumerate(CONES_V):
        tau = t - T["vh"] - 0.03 * abs(i - 2)
        if tau > 0 and abs(cz - ZV) < 1.7:
            d = 5.0 * (1 - math.exp(-tau * 1.6)) * (1.0 + 0.2 * i)
            cones.append([cx + d, cz + (i - 2) * 0.5 * (1 - math.exp(-tau * 2)), min(math.pi / 2, tau * 5) * (1 if i % 2 else -1),
                          tau * 3 * (i - 2)])
        else:
            cones.append([cx, cz, 0.0, 0.0])
    for cx, cz in CONES_A:
        cones.append([cx, cz, 0.0, 0.0])
    marcas = max(0.0, xv - corrida(T["vf"], T["vf"], T["vh"], -XF_CONE, 8.0, 3.0)[0]) if t > T["vf"] else 0.0
    freiov = 1.0 if t > T["vf"] and vv > 0.1 else 0.0
    freioa = (0.55 + 0.45 * (math.sin(t * 2 * math.pi * 15) > 0)) if t > T["af"] and va > 0.1 else 0.0
    if k < 3:
        spray_de, spray = [xv, ZV], min(1.0, vv / 15)
    else:
        spray_de, spray = [xa, za], min(1.0, va / 15)
    # câmeras
    if k == 0:
        q = ease(lt / 2.5)
        cam = mistura([xv - 13, 3.2, ZV + 7], [xv - 9, 2.4, ZV + 5], q)
        alvo, fov = [xv + 2.5, 0.7, ZV], 50
    elif k == 1:
        q = ease(lt / 1.0)
        cam = mistura([xv - 9, 2.4, ZV + 5], [xv + 3.6, 1.1, ZV + 6.0], q)
        alvo = mistura([xv + 2.5, 0.7, ZV], [xv + 0.8, 0.5, ZV], q)
        fov = 50
    elif k == 2:
        cam, alvo, fov = [9, 2.4, ZV + 8], [xv - 1, 0.7, ZV], 46
    elif k == 3:
        q = ease((lt - 1.4) / 1.2)
        cam = mistura([xa - 13, 3.2, ZA - 7], [xa + 3.6, 1.1, za - 6.0], q)
        alvo = mistura([xa + 2.5, 0.7, ZA], [xa + 0.8, 0.5, za], q)
        fov = 50
    elif k == 4:
        cam, alvo, fov = [10, 3.0, ZA - 9], [xa, 0.7, za], 46
    else:
        q = ease(lt / 1.5) if k == 5 else 1.0
        cam = mistura([10, 3.0, ZA - 9], [-18, 20, 26], q)
        alvo = mistura([xa, 0.7, za], [4, 0, 0], q)
        fov = 46
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t,
            "verm": [xv, ZV, 0.0, girov, estv], "azul": [xa, za, rumoa, giroa, esta],
            "freioV": freiov, "freioA": freioa, "marcas": marcas, "marcaX": xv - 1.45, "marcaZ": ZV,
            "cones": cones, "spray": spray, "sprayDe": spray_de}


XF_CONE = 2.25 + 0.3   # o para-choque (meio comprimento) encosta no cone em x = 0
FILME = tres.Filme("abs.js", estado)
SEGS = []


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)
    k = SEGMENTS.index(s) if s in SEGMENTS else -1
    if not SEGS:
        return
    T = tempos(SEGS)
    tt = s.t0 + t
    if k in (0, 1, 2):
        pill(ctx, "NO ABS", 540, 560, PINK, 1.0, size=34)
        if tt > T["vf"] + 0.3:
            text_center(ctx, "WHEELS LOCKED", 540, 640, 44, PINK, "ExtraBold")
    elif k in (3, 4):
        pill(ctx, "WITH ABS", 540, 560, GREEN, 1.0, size=34)
        if tt > T["af"]:
            pisca = math.sin(tt * 2 * math.pi * 3) > 0
            round_rect(ctx, 430, 610, 220, 70, 14)
            ctx.set_source_rgba(1.0, 0.7, 0.1, 1.0 if pisca else 0.35)
            ctx.fill()
            text_center(ctx, "ABS", 540, 662, 46, (0.1, 0.08, 0.02), "ExtraBold")
            text_center(ctx, "~15 PULSES PER SECOND", 540, 725, 28, WHITE, "Bold")


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["Slam the brakes on a wet road at sixty miles per hour. Watch the wheels."],
        {"title": "WHAT IF YOU BRAKE ON A WET ROAD?"}, tail=0.2),
    seg(["Without ABS, they lock. The driver turns the wheel, but a sliding tire can't steer. Nothing happens."],
        {"big": "LOCKED", "sub": "NO GRIP TO STEER", "color": PINK}, tail=0.2),
    seg(["So it slides straight into the cones."],
        {"big": "STRAIGHT ON", "sub": "THE WHEEL DID NOTHING", "color": PINK}, tail=0.5, sfx=[(0, 0.5, "whoosh")]),
    seg(["Same road, with ABS. A computer lets go of the brakes about fifteen times a second."],
        {"big": "ABS", "sub": "RELEASE · GRIP · REPEAT", "color": YELLOW}, tail=0.2),
    seg(["The wheels keep rolling, so the car still steers around the cones and stops safely."],
        {"big": "IT STEERS", "sub": "BRAKING AND TURNING", "color": GREEN}, tail=0.4),
    seg(["That buzz in the pedal is the ABS working. New cars in the US and Europe must have it."],
        {"big": "THE BUZZ", "sub": "THAT'S THE ABS WORKING", "color": WHITE}, tail=1.2),
]
SEGMENTS.append(pq.seg_pergunta("Have you ever felt that pedal buzz?", "EVER FELT THE PEDAL BUZZ?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    SEGS[:] = segs
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
