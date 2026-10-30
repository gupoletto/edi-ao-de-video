#!/usr/bin/env python3
"""Sons sintetizados (sem direitos autorais): efeitos das transições e trilhas de fundo.

    python3 edicao/ferramentas/sons.py --ouvir            # gera edicao/estilo/sons/*.wav para ouvir

Efeitos: EFEITOS[nome]() -> np.float32 a 48 kHz. Trilhas: trilha(estilo, duracao) -> np.float32 estéreo (n, 2).
Estilos de trilha:
  lofi    80 bpm, batida arrastada, acordes de piano elétrico com 7ª, chiado de vinil (vlog do dia a dia)
  pop     118 bpm, bumbo em todo tempo, baixo pulsando e arpejo brilhante (montagens rápidas, rotina, treino)
  chill   92 bpm, pad suave e batida leve (falas longas, reflexão, fim do dia)
  epico   100 bpm, tambores graves que crescem e acordes abertos (chegada, conquista, show)
Todas em loops de 8 compassos, com entrada e saída suaves; o montar.py abaixa a trilha sozinho quando há voz.
"""
import argparse
import os

import numpy as np

SR = 48000
_rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a=0.005, r=None):
    """Envoltória ataque linear + queda exponencial (r = constante de tempo em s)."""
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(a, 1e-4))
    if r:
        e *= np.exp(-t / r)
    return e


def _passa_baixa(x, corte):
    """Filtro de 1 polo; corte em Hz (fixo ou array por amostra)."""
    if np.ndim(corte) == 0:
        from scipy.signal import lfilter
        k = 1 - np.exp(-2 * np.pi * corte / SR)
        return lfilter([k], [1, k - 1], x)
    k = 1 - np.exp(-2 * np.pi * np.broadcast_to(corte, x.shape) / SR)
    y, acc = np.empty_like(x), 0.0
    for i in range(len(x)):
        acc += k[i] * (x[i] - acc)
        y[i] = acc
    return y


def _norm(x, pico=0.3):
    m = np.abs(x).max()
    return (x / m * pico).astype(np.float32) if m > 0 else x.astype(np.float32)


# ---------- efeitos ----------

def whoosh(d=0.45):
    n = int(d * SR)
    t = np.linspace(0, 1, n)
    y = _passa_baixa(_rng.standard_normal(n), 300 + 5000 * np.sin(np.pi * t) ** 2)
    return _norm(y * np.sin(np.pi * t) ** 1.5, 0.22)


def pop():
    t = _t(0.09)
    f = 900 * np.exp(-t * 18) + 380
    return _norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45), 0.35)


def clique():
    t = _t(0.03)
    return _norm(np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 300) + 0.3 * _rng.standard_normal(len(t)) * np.exp(-t * 500), 0.4)


def campainha():  # de bicicleta: dois toques metálicos
    t = _t(0.9)
    toque = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in ((2093, 4), (2637, 5), (4186, 9)))
    y = np.zeros(int(1.1 * SR))
    for i0 in (0, int(0.16 * SR)):
        y[i0:i0 + len(t)] += toque[:len(y) - i0]
    return _norm(y, 0.25)


def tique_taque(d=0.9, ritmo=8):
    y = np.zeros(int(d * SR))
    for k in range(int(d * ritmo)):
        c = clique() * (0.8 if k % 2 else 1.0)
        i = int(k / ritmo * SR)
        y[i:i + len(c)] += c[:len(y) - i]
    return _norm(y, 0.25)


def ding():
    t = _t(1.2)
    return _norm(np.sin(2 * np.pi * 1318.5 * t) * np.exp(-t * 3) + 0.4 * np.sin(2 * np.pi * 1975.5 * t) * np.exp(-t * 4), 0.28)


def flash_foto():
    t = _t(0.35)
    estalo = _rng.standard_normal(len(t)) * np.exp(-t * 60)
    zumbido = np.sin(2 * np.pi * (3000 + 4000 * t) * t) * np.exp(-t * 8) * 0.3
    return _norm(estalo + zumbido, 0.35)


def glitch(d=0.5):
    n = int(d * SR)
    y = np.zeros(n)
    i = 0
    while i < n:  # rajadas digitais curtas: onda quadrada em frequências aleatórias e ruído picotado
        L = int(_rng.uniform(0.02, 0.07) * SR)
        f = _rng.choice([180, 360, 720, 1440, 2880])
        seg = np.sign(np.sin(2 * np.pi * f * np.arange(L) / SR)) * (0.6 if _rng.random() > 0.3 else 0)
        seg += _rng.standard_normal(L) * 0.25 * (_rng.random() > 0.5)
        y[i:i + L] = seg[:n - i]
        i += L + int(_rng.uniform(0, 0.02) * SR)
    return _norm(y, 0.2)


def splash():  # tinta: baque grave + espirro de ruído
    t = _t(0.6)
    baque = np.sin(2 * np.pi * (120 * np.exp(-t * 6) + 50) * t) * np.exp(-t * 9)
    esp = _passa_baixa(_rng.standard_normal(len(t)), 2500) * np.exp(-t * 7) * 0.6
    return _norm(baque + esp, 0.33)


def rasgo(d=0.55):  # papel rasgando: estalos densos e filtrados
    n = int(d * SR)
    y = _rng.standard_normal(n) * (_rng.random(n) > 0.85)
    y = _passa_baixa(y, 3500) * np.sin(np.linspace(0, np.pi, n)) ** 0.5
    return _norm(y, 0.3)


def boing():  # íris de desenho animado
    t = _t(0.5)
    f = 300 + 180 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4)
    return _norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5), 0.3)


def persiana(d=0.4, n_lamelas=8):
    y = np.zeros(int(d * SR))
    for k in range(n_lamelas):
        c = clique()
        i = int(k / n_lamelas * d * SR)
        y[i:i + len(c)] += c[:len(y) - i] * 0.7
    return _norm(y + whoosh(d)[:len(y)] * 0.6, 0.28)


def projetor(d=1.0):  # rolo de filme: matraca a 24 Hz
    t = _t(d)
    mat = (np.sin(2 * np.pi * 24 * t) > 0.6) * _rng.standard_normal(len(t)) * 0.5
    return _norm(_passa_baixa(mat, 2000) + 0.15 * np.sin(2 * np.pi * 60 * t), 0.22)


def bipe_filme():
    t = _t(0.12)
    return _norm(np.sin(2 * np.pi * 1000 * t) * _env(len(t), 0.003, 0.08), 0.25)


def notificacao():  # celular: vibração + "ping" de duas notas
    t = _t(0.25)
    vib = np.sin(2 * np.pi * 160 * t) * (np.sin(2 * np.pi * 18 * t) > 0) * 0.5
    t2 = _t(0.5)
    ping = np.sin(2 * np.pi * 1760 * t2) * np.exp(-t2 * 9)
    ping[int(0.09 * SR):] += np.sin(2 * np.pi * 2637 * t2[:len(t2) - int(0.09 * SR)]) * np.exp(-t2[:len(t2) - int(0.09 * SR)] * 7)
    return _norm(np.concatenate([vib, ping]), 0.28)


def obturador():  # polaroid: clique + motor saindo a foto
    t = _t(0.6)
    motor = np.sin(2 * np.pi * 220 * t) * (1 + 0.5 * np.sin(2 * np.pi * 37 * t)) * 0.15 * (t > 0.08)
    return _norm(np.r_[clique(), np.zeros(1200), clique() * 0.6, motor], 0.3)


def blips():  # blocos: arpejo de bipes subindo
    y = np.zeros(int(0.55 * SR))
    for k, f in enumerate((523, 659, 784, 1047, 1319)):
        t = _t(0.08)
        b = np.sign(np.sin(2 * np.pi * f * t)) * np.exp(-t * 30) * 0.5
        i = int(k * 0.09 * SR)
        y[i:i + len(b)] += b[:len(y) - i]
    return _norm(y, 0.2)


def multidao(d=1.2):  # aplauso/torcida ao longe
    n = int(d * SR)
    palmas = _rng.standard_normal(n) * (_rng.random(n) > 0.97)
    y = _passa_baixa(palmas, 3000) + 0.3 * _passa_baixa(_rng.standard_normal(n), 600)
    return _norm(y * np.sin(np.linspace(0, np.pi, n)), 0.2)


def impressora(d=1.2):  # impressora térmica: zumbido picotado
    t = _t(d)
    y = np.sign(np.sin(2 * np.pi * 95 * t)) * (np.sin(2 * np.pi * 7 * t) > -0.3) * 0.4
    y += _passa_baixa(_rng.standard_normal(len(t)), 1800) * 0.3
    return _norm(y * np.minimum(1, (d - t) / 0.1), 0.18)


def metal():  # anilha batendo
    t = _t(1.0)
    y = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in ((310, 5), (835, 7), (1490, 9), (2210, 12)))
    y += _rng.standard_normal(len(t)) * np.exp(-t * 60) * 0.8
    return _norm(y, 0.33)


def chiado(d=0.9):  # frigideira/vapor
    n = int(d * SR)
    r = _rng.standard_normal(n)
    y = r - _passa_baixa(r, 3000)
    return _norm(y * np.sin(np.linspace(0, np.pi, n)) ** 0.7 * (1 + 0.3 * _rng.random(n)), 0.16)


def rebobinar_fita(d=1.1):  # motor de VCR acelerando + guinchos
    t = _t(d)
    f = 200 + 1800 * t / d
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + _passa_baixa(_rng.standard_normal(len(t)), 900) * 0.4
    return _norm(y * np.minimum(1, t / 0.1) * np.minimum(1, (d - t) / 0.15), 0.2)


EFEITOS = {"impressora": impressora, "metal": metal, "chiado": chiado, "rebobinar": rebobinar_fita,
           "whoosh": whoosh, "pop": pop, "clique": clique, "campainha": campainha, "tique": tique_taque,
           "ding": ding, "flash": flash_foto, "glitch": glitch, "splash": splash, "rasgo": rasgo, "boing": boing,
           "persiana": persiana, "projetor": projetor, "bipe": bipe_filme, "notificacao": notificacao,
           "obturador": obturador, "blips": blips, "multidao": multidao}

# som de cada transição: [(efeito, segundos em relação ao corte)]
DA_TRANSICAO = {
    "roda": [("whoosh", -0.3), ("campainha", -0.45)],
    "rota": [("whoosh", -0.3), ("pop", 0.35), ("ding", 0.55)],
    "relogio": [("tique", -0.45), ("ding", 0.3)],
    "cortina": [("whoosh", -0.3), ("multidao", 0.0)],
    "flash": [("flash", -0.1)],
    "blocos": [("blips", -0.3)],
    "tinta": [("splash", -0.15)],
    "glitch": [("glitch", -0.25)],
    "papel": [("rasgo", -0.35)],
    "iris": [("boing", -0.2)],
    "persiana": [("persiana", -0.3)],
    "filme": [("projetor", -0.55), ("bipe", -0.05)],
    "celular": [("notificacao", -0.2)],
    "polaroid": [("obturador", -0.15)],
    "cronometro": [("bipe", -0.4), ("bipe", -0.25), ("ding", 0.35)],
    "cupom": [("impressora", -0.4)],
    "anilhas": [("whoosh", -0.35), ("metal", -0.02)],
    "vapor": [("chiado", -0.4)],
    "rebobinar": [("rebobinar", -0.7)],
}


# ---------- trilhas ----------

NOTAS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def _hz(nota, oit=4):
    return 440 * 2 ** ((NOTAS[nota] + 12 * (oit - 4) - 9) / 12)


def _acorde(raiz, tipo):
    iv = {"maj7": (0, 4, 7, 11), "m7": (0, 3, 7, 10), "7": (0, 4, 7, 10), "maj": (0, 4, 7, 12), "m": (0, 3, 7, 12),
          "sus": (0, 5, 7, 12), "add9": (0, 4, 7, 14)}[tipo]
    return [_hz(raiz, 3) * 2 ** (i / 12) for i in iv]


ESTILOS_TRILHA = {
    "lofi": dict(bpm=80, swing=0.62, prog=[("F", "maj7"), ("E", "m7"), ("D", "m7"), ("C", "maj7")],
                 bumbo=(0, 2.5), caixa=(1, 3), chimbal=8, timbre="rhodes", vinil=True, arpejo=False, volume=0.9),
    "pop": dict(bpm=118, swing=0.5, prog=[("A", "m"), ("F", "maj"), ("C", "maj"), ("G", "maj")],
                bumbo=(0, 1, 2, 3), caixa=(1, 3), chimbal=8, timbre="pluck", vinil=False, arpejo=True, volume=0.8),
    "chill": dict(bpm=92, swing=0.55, prog=[("D", "maj7"), ("B", "m7"), ("G", "maj7"), ("A", "7")],
                  bumbo=(0, 2.75), caixa=(2,), chimbal=4, timbre="pad", vinil=False, arpejo=False, volume=0.85),
    "epico": dict(bpm=100, swing=0.5, prog=[("D", "m"), ("A#", "maj"), ("F", "maj"), ("C", "maj")],
                  bumbo=(0, 1.5, 2, 3.5), caixa=(), chimbal=0, timbre="cordas", vinil=False, arpejo=False,
                  tambores=True, volume=0.8),
}


def _bumbo():
    t = _t(0.35)
    return np.sin(2 * np.pi * np.cumsum(45 + 120 * np.exp(-t * 30)) / SR) * np.exp(-t * 9)


def _caixa():
    t = _t(0.22)
    return 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) + _passa_baixa(_rng.standard_normal(len(t)), 5000) * np.exp(-t * 18) * 0.7


def _chimbal():
    t = _t(0.06)
    r = _rng.standard_normal(len(t))
    return (r - _passa_baixa(r, 7000)) * np.exp(-t * 70) * 0.5


def _tambor():
    t = _t(0.8)
    return np.sin(2 * np.pi * np.cumsum(70 + 40 * np.exp(-t * 10)) / SR) * np.exp(-t * 4) + \
        _passa_baixa(_rng.standard_normal(len(t)), 400) * np.exp(-t * 6) * 0.5


def _nota(f, d, timbre):
    t = _t(d)
    if timbre == "rhodes":
        y = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3)
        y *= _env(len(t), 0.01, 1.2) * (1 + 0.15 * np.sin(2 * np.pi * 4.5 * t))
    elif timbre == "pluck":
        y = sum(np.sin(2 * np.pi * f * h * t) / h for h in (1, 2, 3, 4)) * _env(len(t), 0.003, 0.18)
    elif timbre == "pad":
        y = sum(np.sin(2 * np.pi * f * (1 + dt) * t) for dt in (-0.004, 0, 0.004)) / 3
        y *= np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)
    else:  # cordas: serra suavizada, ataque lento
        y = sum(np.sin(2 * np.pi * f * h * t) / h for h in range(1, 7)) * np.minimum(1, t / 0.25) * np.minimum(1, (d - t) / 0.3)
    return y


def trilha(estilo, duracao, inicio_suave=1.5, fim_suave=2.5):
    """Trilha estéreo do tamanho pedido (loop de 8 compassos), já com fade."""
    p = ESTILOS_TRILHA[estilo]
    tempo = 60 / p["bpm"]
    compasso = 4 * tempo
    n_comp = 8
    L = int(n_comp * compasso * SR)
    esq, dir_ = np.zeros(L), np.zeros(L)

    def por(som, t, ganho=1.0, pan=0.0):
        i = int(t * SR)
        if i >= L:
            return
        s = som[:L - i] * ganho
        esq[i:i + len(s)] += s * (1 - max(0, pan))
        dir_[i:i + len(s)] += s * (1 + min(0, pan))

    bumbo, caixa = _bumbo(), _caixa()
    for c in range(n_comp):
        t0 = c * compasso
        raiz, tipo = p["prog"][c % len(p["prog"])]
        notas = _acorde(raiz, tipo)
        if p["timbre"] in ("pad", "cordas"):
            for k, f in enumerate(notas):
                por(_nota(f * 2, compasso, p["timbre"]), t0, 0.16, (k - 1.5) * 0.3)
        elif p["arpejo"]:  # colcheias subindo e descendo
            seq = notas + notas[-2:0:-1]
            for k in range(8):
                por(_nota(seq[k % len(seq)] * 2, tempo * 0.6, "pluck"), t0 + k * tempo / 2, 0.18, 0.4 if k % 2 else -0.4)
            for k in (0, 2):
                for f in notas:
                    por(_nota(f, tempo * 1.8, "pad"), t0 + k * tempo, 0.06)
        else:  # rhodes: acorde no 1 e uma antecipação no 2-e
            for at, g in ((0, 0.2), (1.5, 0.12)):
                for k, f in enumerate(notas):
                    por(_nota(f * 2, tempo * 2.2, p["timbre"]), t0 + at * tempo + k * 0.012, g, (k - 1.5) * 0.25)
        baixo = _hz(raiz, 2)
        for b in ((0, 2) if not p["arpejo"] else (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5)):
            dur = tempo * (1.8 if not p["arpejo"] else 0.45)
            t = _t(dur)
            nota = np.sin(2 * np.pi * baixo * t) * _env(len(t), 0.01, dur * 0.6)
            por(nota + 0.3 * np.sin(4 * np.pi * baixo * t) * _env(len(t), 0.01, dur * 0.3), t0 + b * tempo, 0.35)
        for b in p["bumbo"]:
            por(bumbo, t0 + b * tempo, 0.55)
        for b in p["caixa"]:
            por(caixa, t0 + b * tempo, 0.32)
        if p["chimbal"]:
            passo = 4 / p["chimbal"]
            for k in range(p["chimbal"]):
                sw = (p["swing"] - 0.5) * 2 * passo * tempo if k % 2 else 0
                por(_chimbal(), t0 + k * passo * tempo + sw, 0.22 if k % 2 else 0.3, 0.3)
        if p.get("tambores") and c >= 4:  # crescendo na segunda metade
            for k in range(4 if c < 7 else 8):
                por(_tambor(), t0 + k * compasso / (4 if c < 7 else 8), 0.3 + 0.05 * c)
    loop = np.stack([esq, dir_], 1)
    if p["vinil"]:
        chiado = _passa_baixa(_rng.standard_normal(L), 3000) * 0.012
        chiado += (_rng.random(L) > 0.9995) * _rng.standard_normal(L) * 0.15
        loop += chiado[:, None]
    loop = _passa_baixa_st(loop, 9000 if estilo != "lofi" else 4500)
    n = int(duracao * SR)
    out = np.tile(loop, (n // L + 1, 1))[:n]
    t = np.arange(n) / SR
    out *= np.minimum(1, t / inicio_suave)[:, None] * np.minimum(1, (duracao - t) / fim_suave)[:, None]
    m = np.abs(out).max()
    return (out / m * 0.5 * p["volume"]).astype(np.float32) if m > 0 else out.astype(np.float32)


def _passa_baixa_st(x, corte):
    from scipy.signal import butter, sosfilt
    sos = butter(2, corte, fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)


if __name__ == "__main__":
    import soundfile as sf
    from comum import ESTILO
    ap = argparse.ArgumentParser()
    ap.add_argument("--ouvir", action="store_true")
    a = ap.parse_args()
    pasta = os.path.join(ESTILO, "sons")
    os.makedirs(pasta, exist_ok=True)
    for nome, f in EFEITOS.items():
        sf.write(os.path.join(pasta, f"efeito_{nome}.wav"), f(), SR)
    for est in ESTILOS_TRILHA:
        sf.write(os.path.join(pasta, f"trilha_{est}.wav"), trilha(est, 24), SR)
    print(f"sons em {pasta}")
