"""What happens when you flush a toilet? (cinematic 3D, x-ray of the siphon). Thu 12/11/2026, topic: how it works,
3D queue (toilet flush / siphon). Search 12/11: "what happens when you flush", median 28.9k.

Shots: a toilet; the handle is pressed -> x-ray: the flapper lifts and the tank dumps its water into the bowl ->
the bowl level rises above the top of the curved trapway and water spills over it -> the siphon starts and pulls the
whole bowl down the drain -> air reaches the trap and the siphon breaks (the gurgle) -> the tank refills and a
little water stays in the trap as a seal -> Quark asks the question.

Facts:
- in a gravity-flush (siphonic) toilet the handle lifts a flapper, and the tank's water (about 6 L in modern
  1.6 gpf toilets) rushes into the bowl through the rim and the siphon jet in a few seconds;
- the trapway is an S-shaped channel: once the water fills it past its highest point, a siphon forms and pulls the
  bowl empty;
- when the bowl empties enough for air to enter the trap, the siphon breaks with the characteristic gurgle;
- the refill tube tops up the bowl so water stays in the trap: that water seal keeps sewer gases out.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import personagem as pq  # noqa: E402
import tres  # noqa: E402
from core import GREEN, PINK, WHITE, YELLOW, Seg, render  # noqa: E402

Y_SELO, Y_CURVA, Y_FUNDO = 0.24, 0.37, 0.18


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
    t_puxa = segs[0].t0 + 1.4
    t_cheio = segs[2].t0 + 0.8        # a bacia passa da curva do sifão
    t_sifao = segs[3].t0 + 0.2        # o sifão puxa
    t_ar = segs[4].t0 + 0.4           # entra ar: gorgolejo
    t_enche = segs[5].t0 + 0.2
    alav = ease((t - t_puxa) / 0.25) * (1 - ease((t - t_puxa - 0.8) / 0.4))
    flapper = ease((t - t_puxa - 0.1) / 0.3) * (1 - ease((t - t_ar) / 0.5))
    # caixa: esvazia do puxão até o gorgolejo; depois enche de novo
    if t < t_puxa:
        caixa = 1.0
    elif t < t_ar:
        caixa = 1 - ease((t - t_puxa) / (t_ar - t_puxa)) * 0.95
    else:
        caixa = 0.05 + 0.95 * ease((t - t_enche) / 5.0)
    # bacia: sobe até passar a curva, o sifão puxa até o fundo, depois volta ao nível do selo
    if t < t_puxa + 0.2:
        bacia = Y_SELO
    elif t < t_cheio:
        bacia = Y_SELO + (Y_CURVA + 0.02 - Y_SELO) * ease((t - t_puxa - 0.2) / (t_cheio - t_puxa - 0.2))
    elif t < t_sifao:
        bacia = Y_CURVA + 0.02
    elif t < t_ar:
        bacia = Y_CURVA + 0.02 - (Y_CURVA + 0.02 - Y_FUNDO - 0.01) * ease((t - t_sifao) / (t_ar - t_sifao))
    else:
        bacia = Y_FUNDO + 0.01 + (Y_SELO - Y_FUNDO - 0.01) * ease((t - t_enche - 0.5) / 3.0)
    sifao = 0.45 if t < t_cheio else (0.45 + 0.55 * ease((t - t_cheio) / 0.8) if t < t_ar else
                                      max(0.45, 1 - 0.55 * ease((t - t_ar) / 1.0)))
    fluxo_caixa = 1.0 if t_puxa + 0.2 < t < t_ar else 0.0
    fluxo_sifao = 1.0 if t_cheio < t < t_ar + 0.6 else 0.0
    bolhas = 1.0 if t_ar < t < t_ar + 2.0 else 0.0
    raiox = ease((t - segs[1].t0 - 0.2) / 0.6) if k < 5 else 1 - ease((lt - 3.5) / 0.8) if k == 5 else 0.0
    if k >= 6:
        raiox = 0.0
    frente = ([1.55, 1.25, 2.25], [-0.08, 0.40, 0.0], 38)
    lado = ([-0.06, 0.45, 2.45], [-0.08, 0.40, 0.0], 40)
    perto = ([-0.08, 0.36, 1.75], [-0.1, 0.30, 0.0], 40)
    if k == 0:
        q = ease(lt / 3.0)
        cam = mistura([2.0, 1.5, 2.8], frente[0], q)
        alvo, fov = frente[1], 38
    elif k == 1:
        q = ease(lt / 1.5)
        cam, alvo = mistura(frente[0], lado[0], q), mistura(frente[1], lado[1], q)
        fov = 40
    elif k == 2:
        cam, alvo, fov = lado
    elif k == 3:
        q = ease(lt / 1.5)
        cam, alvo = mistura(lado[0], perto[0], q), mistura(lado[1], perto[1], q)
        fov = 40
    elif k == 4:
        cam, alvo, fov = perto
    else:
        q = ease(lt / 2.0) if k == 5 else 1.0
        cam, alvo = mistura(perto[0], frente[0], q), mistura(perto[1], frente[1], q)
        fov = 40 - 2 * q
    return {"cam": cam, "alvo": alvo, "fov": fov, "t": t, "raiox": raiox, "caixa": caixa, "bacia": bacia,
            "alavanca": alav, "flapper": flapper, "fluxoCaixa": fluxo_caixa, "fluxoSifao": fluxo_sifao,
            "sifao": sifao, "bolhas": bolhas}


FILME = tres.Filme("banheiro.js", estado)


def tela(ctx, t, s):
    FILME.quadro(ctx, s.t0 + t)


def seg(itens, header, **kw):
    s = Seg(itens, tela, header, **kw)
    s.continuo = True
    return s


SEGMENTS = [
    seg(["Here's what really happens inside a toilet when you flush."], {"title": "WHAT HAPPENS WHEN YOU FLUSH?"}, tail=0.3,
        sfx=[(0, 1.4, "whoosh")]),
    seg(["The handle lifts a rubber flapper, and the tank dumps all its water into the bowl in seconds."],
        {"big": "THE DUMP", "sub": "ABOUT 6 LITERS", "color": YELLOW}, tail=0.2),
    seg(["The water rises past the top of this curved pipe hidden inside, called the trapway."],
        {"big": "THE HIDDEN PIPE", "big_size": 90, "sub": "AN S-SHAPED CURVE", "color": WHITE}, tail=0.3),
    seg(["Now it's a siphon. Gravity pulls the whole bowl down the drain, like sucking through a straw."],
        {"big": "SIPHON", "sub": "THE BOWL GETS PULLED", "color": (0.36, 0.78, 0.98)}, tail=0.2),
    seg(["When air finally gets in, the siphon breaks. That's the gurgle."],
        {"big": "THE GURGLE", "sub": "AIR BREAKS THE SIPHON", "color": PINK}, tail=0.4),
    seg(["Then the tank refills, and a little water stays in the pipe as a seal, so sewer smell can't come back up."],
        {"big": "THE WATER SEAL", "big_size": 90, "sub": "NO SEWER SMELL", "color": GREEN}, tail=1.2),
]
SEGMENTS.append(pq.seg_pergunta("Did you know your toilet is a siphon?", "DID YOU KNOW IT'S A SIPHON?",
                                fundo=lambda ctx, t, s: FILME.quadro(ctx, s.t0 + t)))
SEGMENTS[-1].continuo = True


def preparo(segs, total):
    FILME.renderizar(segs, total)


if __name__ == "__main__":
    render(SEGMENTS, sys.argv[1], preparo=preparo)
