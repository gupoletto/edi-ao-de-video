"""Fun Stuff Shorts renderer: script -> voice -> timeline -> frames -> mp4.

An episode is a list of Seg. Each Seg holds narration lines (str) and pauses (float seconds),
a draw(ctx, t, seg) function for the illustration and an optional header. seg.mark(i) is the
segment-local start time of item i, so animations can sync to the narration.

    render(segments, "out.mp4")
"""
import hashlib
import json
import math
import os
import re
import subprocess
import tempfile
import urllib.request

import cairo
import numpy as np
import soundfile as sf

W, H, FPS = 1080, 1920, 30
SR = 24000
VOICE, SPEED = "am_puck", 1.05   # escolhida pelo usuário em 20/11/2026 (antes af_heart; am_michael 1.08)
HANDLE = "@funstuff-67"

BLUE = (0.36, 0.78, 0.98)
PINK = (1.0, 0.36, 0.54)
GREEN = (0.30, 0.90, 0.50)
RED = (1.0, 0.30, 0.30)
YELLOW = (1.0, 0.85, 0.25)
WHITE = (1, 1, 1)
GRAY = (0.45, 0.47, 0.52)

# Illustration area (between header and captions).
# Área das cenas. Fica fora das zonas que a interface do Shorts cobre (topo ~10 %, base 25 %, direita ~10 %):
# cabeçalho 190–410 px, cena 440–1270 px, legenda centrada em 1372 px (anuncios/zonas.py --zona shorts).
AREA = (90, 440, 990, 1270)
LEGENDA_Y = 1372

CACHE = os.path.expanduser("~/.cache")
FONT_URL = "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-{}.ttf"
KOKORO_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/{}"


def setup():
    """Fetch the font (OFL) and the Kokoro model once per machine."""
    fonts = os.path.expanduser("~/.local/share/fonts")
    os.makedirs(fonts, exist_ok=True)
    added = False
    for w in ("Bold", "ExtraBold", "SemiBold"):
        p = os.path.join(fonts, f"Poppins-{w}.ttf")
        if not os.path.exists(p):
            urllib.request.urlretrieve(FONT_URL.format(w), p)
            added = True
    if added:
        subprocess.run(["fc-cache", "-f"], check=True)
    kdir = os.path.join(CACHE, "kokoro")
    os.makedirs(kdir, exist_ok=True)
    for f in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
        p = os.path.join(kdir, f)
        if not os.path.exists(p):
            urllib.request.urlretrieve(KOKORO_URL.format(f), p)


# ---------- voice ----------

_kokoro = None


def say(text):
    """Speech for one line, trimmed, float32 at SR. Cached on disk."""
    global _kokoro
    key = hashlib.sha1(f"{VOICE}|{SPEED}|{text}".encode()).hexdigest()[:16]
    path = os.path.join(CACHE, "funstuff-tts", key + ".wav")
    if os.path.exists(path):
        return sf.read(path, dtype="float32")[0]
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(os.path.join(CACHE, "kokoro", "kokoro-v1.0.onnx"),
                         os.path.join(CACHE, "kokoro", "voices-v1.0.bin"))
    audio, sr = _kokoro.create(text, voice=VOICE, speed=SPEED, lang="en-us")
    assert sr == SR
    loud = np.nonzero(np.abs(audio) > 0.01)[0]
    audio = audio[max(0, loud[0] - 600):loud[-1] + 1200].astype(np.float32)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sf.write(path, audio, SR)
    return audio


def word_times(text, dur):
    """Approximate (start, word) pairs: time spread by letters, extra weight at punctuation."""
    words = text.split()
    weights = [len(re.sub(r"[^A-Za-z0-9]", "", w)) + 1.5 + (2.5 if re.search(r"[,.?!:;]$", w) else 0)
               for w in words]
    total, acc, out = sum(weights), 0.0, []
    for w, k in zip(words, weights):
        out.append((dur * acc / total, w))
        acc += k
    return out


# ---------- timeline ----------

class Seg:
    def __init__(self, items, draw, header=None, tail=0.6, sfx=()):
        self.items, self.draw, self.header, self.tail = items, draw, header, tail
        self.sfx = sfx  # (item index, offset seconds, name)

    def build(self):
        t, self.starts, self.lines, chunks = 0.0, [], [], []
        for it in self.items:
            self.starts.append(t)
            if isinstance(it, str):
                a = say(it)
                d = len(a) / SR
                self.lines.append((t, t + d, word_times(it, d)))
                chunks.append((t, a))
                t += d + 0.15
            else:
                t += it
        self.dur = t + self.tail
        self.audio = chunks
        return self

    def mark(self, i):
        return self.starts[i]


def mola(t, dur=0.5):
    """Entrada com mola (0 -> passa de 1 -> assenta em 1), estilo "pop" dos motion graphics; t em s desde a entrada."""
    if t <= 0:
        return 0.0
    x = t / dur
    return 1 - math.exp(-6 * x) * math.cos(9 * x)


def pop_caixa(ctx, t, cx, cy, desenha, dur=0.5):
    """Desenha algo (função sem argumentos) com entrada de mola, escalando em volta de (cx, cy)."""
    k = mola(t, dur)
    if k <= 0.001:
        return
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(k, k)
    ctx.translate(-cx, -cy)
    desenha()
    ctx.restore()


def ramp(t, start, length=0.6):
    """0 -> 1 smoothly between start and start+length."""
    x = min(1.0, max(0.0, (t - start) / length))
    return x * x * (3 - 2 * x)


# ---------- drawing helpers ----------

def font(ctx, size, weight="Bold"):
    if weight == "ExtraBold":
        ctx.select_font_face("Poppins ExtraBold", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    elif weight == "SemiBold":
        ctx.select_font_face("Poppins SemiBold", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    else:
        ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)


def text_center(ctx, s, cx, y, size, color=WHITE, weight="Bold", alpha=1.0):
    font(ctx, size, weight)
    e = ctx.text_extents(s)
    ctx.set_source_rgba(*color, alpha)
    ctx.move_to(cx - e.x_bearing - e.width / 2, y)
    ctx.show_text(s)


def wrap(ctx, words, max_w):
    lines, cur = [], []
    for w in words:
        trial = " ".join(cur + [w])
        if cur and ctx.text_extents(trial).x_advance > max_w:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def round_rect(ctx, x, y, w, h, r):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def pill(ctx, s, cx, cy, color, alpha=1.0, size=44):
    """Verdict label, e.g. SAME LENGTH."""
    if alpha <= 0:
        return
    font(ctx, size, "ExtraBold")
    e = ctx.text_extents(s)
    w, h = e.x_advance + 60, size + 34
    round_rect(ctx, cx - w / 2, cy - h / 2, w, h, h / 2)
    ctx.set_source_rgba(*color, alpha)
    ctx.fill()
    ctx.set_source_rgba(0.04, 0.05, 0.09, alpha)
    ctx.move_to(cx - e.x_bearing - e.width / 2, cy + size * 0.36)
    ctx.show_text(s)


def _sombra(ctx, desenha):
    """Desenha o texto com uma sombra escura atrás, para ler em fundo claro (céu, cenas 3D)."""
    ctx.save()
    ctx.translate(3, 4)
    desenha(sombra=True)
    ctx.restore()
    desenha(sombra=False)


def draw_header(ctx, h):
    if not h:
        return
    tc = globals()["text_center"]

    def text_center(c, s, x, y, size, color=WHITE, weight="Bold", alpha=1.0):  # noqa: F811
        _sombra(c, lambda sombra: tc(c, s, x, y, size, (0.02, 0.03, 0.06) if sombra else color, weight,
                                     alpha * (0.55 if sombra else 1.0)))
    if "big" in h:
        text_center(ctx, h["big"], W / 2, 278, h.get("big_size", 112), h.get("color", BLUE), "ExtraBold")
    if "sub" in h:
        text_center(ctx, h["sub"], W / 2, 344, 48)
    if "title" in h:  # multi-line headline (intro / outro)
        font(ctx, 68, "ExtraBold")
        lines = wrap(ctx, h["title"].split(), 920)
        for i, ln in enumerate(lines):
            text_center(ctx, " ".join(ln), W / 2, 262 + i * 80, 68, WHITE, "ExtraBold")
    if "dots" in h:
        labels, active = h["dots"]
        n = len(labels)
        for i, lab in enumerate(labels):
            x = W / 2 + (i - (n - 1) / 2) * 62
            ctx.arc(x, 398, 19, 0, 2 * math.pi)
            if i == active:
                ctx.set_source_rgb(*(h.get("color", BLUE)))
            else:
                ctx.set_source_rgba(1, 1, 1, 0.16)
            ctx.fill()
            text_center(ctx, lab, x, 406, 20, WHITE, "Bold")


def draw_captions(ctx, seg, t):
    for (a, b, words) in seg.lines:
        if a <= t <= b + 0.35:
            break
    else:
        return
    font(ctx, 52)
    rows = wrap(ctx, [w for _, w in words], 840)
    lh = 68
    if len(rows) > 2:  # 3 linhas passariam da área segura: letra menor
        font(ctx, 44)
        rows = wrap(ctx, [w for _, w in words], 860)
        lh = 58
    top = min(LEGENDA_Y - len(rows) * lh / 2, 1428 - len(rows) * lh - 18)
    widest = max(ctx.text_extents(" ".join(r)).x_advance for r in rows)
    round_rect(ctx, W / 2 - widest / 2 - 30, top - 18, widest + 60, len(rows) * lh + 36, 22)
    ctx.set_source_rgba(0, 0, 0, 0.55)
    ctx.fill()
    k = 0
    for i, r in enumerate(rows):
        line = " ".join(r)
        x = W / 2 - ctx.text_extents(line).x_advance / 2
        y = top + i * lh + lh * 0.76
        for w in r:
            start = words[k][0] + a
            k += 1
            if t < start:
                ctx.set_source_rgba(1, 1, 1, 0.35)
            elif k < len(words) and t < words[k][0] + a:
                ctx.set_source_rgb(*YELLOW)
            else:
                ctx.set_source_rgb(1, 1, 1)
            ctx.move_to(x, y)
            ctx.show_text(w)
            x += ctx.text_extents(w + " ").x_advance


# ---------- audio ----------

def tone(freq, dur, amp, attack=0.01, decay=None, kind="sine"):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if kind == "sine":
        w = np.sin(2 * np.pi * freq * t)
    else:  # soft triangle
        w = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * freq * t))
    env = np.minimum(1, t / attack) * (np.exp(-t / decay) if decay else 1)
    return (amp * w * env).astype(np.float32)


SFX = {
    "ding": lambda: tone(1318.5, 1.2, 0.30, decay=0.35) + tone(1975.5, 1.2, 0.12, decay=0.25),
    "tick": lambda: tone(880, 0.12, 0.25, decay=0.03),
    "whoosh": lambda: (np.random.default_rng(1).standard_normal(int(0.4 * SR)) *
                       np.hanning(int(0.4 * SR)) * 0.06).astype(np.float32),
}


def _kick(amp=0.35):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 30)
    return (amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)).astype(np.float32)


def _snare(amp=0.12, seed=0):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    ruido = np.random.default_rng(seed).standard_normal(n)
    return (amp * (0.7 * ruido + 0.3 * np.sin(2 * np.pi * 190 * t)) * np.exp(-t * 18)).astype(np.float32)


def _hat(amp=0.035, seed=0):
    n = int(0.06 * SR)
    r = np.random.default_rng(seed).standard_normal(n)
    r = np.diff(r, prepend=0)          # agudo
    return (amp * r * np.exp(-np.arange(n) / SR * 70)).astype(np.float32)


def _soma(out, s, p):
    if s >= len(out):
        return
    e = min(len(out), s + len(p))
    out[s:e] += p[:e - s]


MUSICA = os.environ.get("FUNSTUFF_MUSICA", "")   # estilo da trilha; cada episódio escolhe pelo tom (ver TONS)

# Tom do vídeo -> estilo da trilha (pedido do usuário em 20/11: música variada de acordo com o tom do vídeo).
TONS = {
    "curioso": "lofi", "calmo": "lofi", "explicativo": "lofi",
    "historia": "cinema", "dramatico": "cinema", "triste": "cinema",
    "animado": "pop", "ranking": "pop", "lista": "pop",
    "tenso": "suspense", "perigo": "suspense", "desastre": "suspense",
    "misterio": "misterio", "estranho": "misterio", "espaco": "misterio",
    "epico": "epico", "construcao": "epico", "conquista": "epico",
    "divertido": "alegre", "quark": "alegre", "engracado": "alegre",
}
ESTILOS = ["lofi", "cinema", "pop", "suspense", "misterio", "epico", "alegre"]


def music(dur, estilo=None):
    """Trilha original sintetizada (desde 20/11/2026). O estilo segue o tom do vídeo (core.MUSICA = estilo ou tom):
    lofi     - acordes de sétima com Rhodes suave, bateria hip-hop lenta (~84 BPM): curioso, calmo, explicativo;
    cinema   - pulso de cordas em colcheias, tambor grave e pad crescendo (~100 BPM): história, drama;
    pop      - acordes brilhantes em síncope, palmas e baixo saltado (~112 BPM): listas e rankings;
    suspense - drone grave, batida de coração e tremolo agudo em menor (~70 BPM): perigo, desastre, tensão;
    misterio - caixinha de música em arpejos com eco sobre pad (~76 BPM): estranho, espaço, enigmas;
    epico    - tambores tipo taiko, acordes graves cheios e cordas subindo (~90 BPM): construções, conquistas;
    alegre   - pizzicato saltitante, baixo alternado e palmas (~120 BPM): Quark, temas leves e engraçados."""
    estilo = estilo or MUSICA or "lofi"
    estilo = TONS.get(estilo, estilo)
    if estilo not in ESTILOS:
        raise ValueError(f"estilo de música desconhecido: {estilo}")
    n = int(dur * SR)
    out = np.zeros(n, np.float32)
    nota = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    if estilo == "lofi":
        bpm, prog = 84, [(57, 60, 64, 67), (53, 57, 60, 64), (55, 59, 62, 65), (52, 55, 59, 62)]  # Am7 Fmaj7 G7 Em7
    elif estilo == "cinema":
        bpm, prog = 100, [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]                  # Am F C G
    elif estilo == "pop":
        bpm, prog = 112, [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)]                  # C G Am F
    elif estilo == "suspense":
        bpm, prog = 70, [(50, 53, 57), (46, 50, 53), (43, 46, 50), (45, 49, 52)]                   # Dm Bb Gm A
    elif estilo == "misterio":
        bpm, prog = 76, [(52, 55, 59), (48, 52, 55, 59), (45, 48, 52), (47, 51, 54, 57)]           # Em Cmaj7 Am B7
    elif estilo == "epico":
        bpm, prog = 90, [(50, 53, 57), (46, 50, 53), (53, 57, 60), (48, 52, 55)]                   # Dm Bb F C
    else:
        bpm, prog = 120, [(60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62)]                  # C Am F G
    bt = 60 / bpm
    compasso = 4 * bt
    for k in range(int(dur / compasso) + 1):
        c = prog[k % 4]
        s0 = int(k * compasso * SR)
        cresce = min(1.0, k / 4)
        if estilo == "lofi":
            for m in c:   # Rhodes: dois toques por compasso, um pouco "atrasados"
                for b in (0, 2.5):
                    p = tone(nota(m), 1.6, 0.028, attack=0.01, decay=0.8) + tone(nota(m) * 2, 1.6, 0.008, decay=0.3)
                    _soma(out, s0 + int((b * bt + 0.02) * SR), p)
            _soma(out, s0, tone(nota(c[0] - 24), compasso, 0.07, attack=0.02, decay=1.2))
            for b in range(4):
                _soma(out, s0 + int(b * bt * SR), _kick(0.22) if b in (0, 2) else _snare(0.07, k * 4 + b))
                for h in (0, 0.5):
                    _soma(out, s0 + int((b + h) * bt * SR), _hat(0.02, k * 8 + b))
        elif estilo == "cinema":
            for m in c:   # pad
                p = tone(nota(m), compasso + 0.3, 0.02 + 0.015 * cresce, attack=0.6, kind="tri")
                _soma(out, s0, p * np.linspace(1, 0.6, len(p)).astype(np.float32))
            for j in range(8):   # pulso de cordas em colcheias
                _soma(out, s0 + int(j * bt / 2 * SR), tone(nota(c[0] - 12), bt / 2, 0.05 * (0.5 + 0.5 * cresce),
                                                           attack=0.005, decay=0.12, kind="tri"))
            _soma(out, s0, _kick(0.28))
            _soma(out, s0 + int(2 * bt * SR), _kick(0.18))
        elif estilo == "suspense":
            _soma(out, s0, tone(nota(c[0] - 24), compasso + 0.2, 0.09, attack=0.8))   # drone
            _soma(out, s0, tone(nota(c[0] - 12), compasso + 0.2, 0.03 * cresce, attack=1.2, kind="tri"))
            for b in range(4):   # coração: tum-tum
                _soma(out, s0 + int(b * bt * SR), _kick(0.24))
                _soma(out, s0 + int((b + 0.3) * bt * SR), _kick(0.14))
            for j in range(16):  # tremolo agudo em segunda menor, crescendo
                m = c[2] + 12 + (j % 2)
                _soma(out, s0 + int(j * bt / 4 * SR), tone(nota(m), bt / 4, 0.010 + 0.012 * cresce, attack=0.01,
                                                           decay=0.08, kind="tri"))
        elif estilo == "misterio":
            for m in c:
                _soma(out, s0, tone(nota(m - 12), compasso + 0.4, 0.016, attack=0.9, kind="tri"))
            arp = list(c) + list(c[::-1][1:-1])
            for j in range(8):   # caixinha de música em colcheias, com eco
                m = arp[j % len(arp)] + 24
                p = tone(nota(m), 1.0, 0.035, attack=0.003, decay=0.35)
                at = s0 + int(j * bt / 2 * SR)
                _soma(out, at, p)
                _soma(out, at + int(0.75 * bt * SR), p * 0.35)
            _soma(out, s0, _kick(0.12))
        elif estilo == "epico":
            for m in c:   # acordes graves cheios
                p = tone(nota(m - 12), compasso + 0.3, 0.03 + 0.02 * cresce, attack=0.25, kind="tri")
                _soma(out, s0, p)
            _soma(out, s0, tone(nota(c[0] - 24), compasso, 0.08, attack=0.05, decay=1.5))
            for b in (0, 1.5, 2, 3, 3.5):   # taiko
                _soma(out, s0 + int(b * bt * SR), _kick(0.34 if b in (0, 2) else 0.22))
            if k >= 2:
                for b in (1, 3):
                    _soma(out, s0 + int(b * bt * SR), _snare(0.08, k * 4 + int(b)))
            if k >= 4:   # cordas subindo em semicolcheias
                for j in range(16):
                    m = c[j % len(c)] + 12 + 12 * (j // 8)
                    _soma(out, s0 + int(j * bt / 4 * SR), tone(nota(m), bt / 4, 0.016, attack=0.004, decay=0.07,
                                                               kind="tri"))
        elif estilo == "alegre":
            for b in range(4):
                raiz = c[0] - 12 if b % 2 == 0 else c[2] - 24   # baixo alternado
                _soma(out, s0 + int(b * bt * SR), tone(nota(raiz), bt * 0.8, 0.07, decay=0.15))
                for i, m in enumerate(c):   # pizzicato no contratempo, "dedilhado"
                    _soma(out, s0 + int(((b + 0.5) * bt + i * 0.012) * SR),
                          tone(nota(m + 12), 0.25, 0.024, attack=0.002, decay=0.07, kind="tri"))
                if b in (1, 3):
                    _soma(out, s0 + int(b * bt * SR), _snare(0.07, k * 4 + b))
                _soma(out, s0 + int((b + 0.5) * bt * SR), _hat(0.02, k * 7 + b))
            if k % 2 == 1:   # assobio de melodia simples
                for j, m in enumerate((c[2] + 24, c[1] + 24, c[0] + 24, c[1] + 24)):
                    _soma(out, s0 + int(j * bt * SR), tone(nota(m), bt * 0.9, 0.018, attack=0.04, decay=0.3))
        else:
            for j, b in enumerate((0, 0.75, 1.5, 2.5, 3.0)):   # acordes em síncope
                for m in c:
                    _soma(out, s0 + int(b * bt * SR), tone(nota(m + 12), 0.35, 0.022, attack=0.005, decay=0.15, kind="tri"))
            for b in range(4):
                _soma(out, s0 + int(b * bt * SR), _kick(0.25))
                _soma(out, s0 + int((b + 0.5) * bt * SR), tone(nota(c[0] - 12 + (12 if b % 2 else 0)), bt / 2, 0.06,
                                                                decay=0.12))
                if b in (1, 3):
                    _soma(out, s0 + int(b * bt * SR), _snare(0.09, k * 4 + b))
                _soma(out, s0 + int((b + 0.5) * bt * SR), _hat(0.025, k * 9 + b))
    pico = np.max(np.abs(out)) or 1
    out = out / pico * 0.22          # a mixagem final abaixa sob a voz
    rms = float(np.sqrt(np.mean(out ** 2))) or 1
    if rms > 0.031:                  # estilos mais densos (suspense, épico) ficam no mesmo volume médio dos outros
        out *= 0.031 / rms
    fade = int(0.8 * SR)
    out[:fade] *= np.linspace(0, 1, fade)
    out[-fade:] *= np.linspace(1, 0, fade)
    return out


def lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


def loudnorm(src, dst, target=-14.0):
    """Gain to -14 LUFS with a -3 dBFS peak limiter (AAC overshoots), AAC 48 kHz. The limiter eats a little
    loudness, so the gain is corrected once from a second measurement."""
    gain = target - lufs(src)
    for _ in range(3):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
                        f"volume={gain:.2f}dB,alimiter=limit=0.7:attack=2:release=50:level=false,aresample=48000",
                        "-c:a", "aac", "-b:a", "160k", dst], check=True)
        err = target - lufs(dst)
        if abs(err) < 0.3:
            break
        gain += err


# ---------- render ----------

def background():
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.055, 0.075, 0.13)
    g.add_color_stop_rgb(1, 0.02, 0.025, 0.045)
    c.set_source(g)
    c.paint()
    return s


def render(segments, out, music_on=True, preparo=None):
    setup()
    segs = [s.build() for s in segments]
    total = sum(s.dur for s in segs)
    assert 20 <= total <= 60, f"duration {total:.1f}s outside 20-60 s"
    t0 = 0.0
    for s in segs:  # início de cada trecho no vídeo (cenas contínuas, como as 3D, usam o tempo global)
        s.t0, t0 = t0, t0 + s.dur
    if preparo:  # ex.: renderizar os quadros 3D agora que os tempos da narração são conhecidos
        preparo(segs, total)
    print(f"{out}: {total:.1f}s, {len(segs)} segments")

    # audio
    n = int((total + 0.2) * SR)
    voice = np.zeros(n, np.float32)
    fx = np.zeros(n, np.float32)
    t0 = 0.0
    for s in segs:
        for st, a in s.audio:
            i = int((t0 + st) * SR)
            voice[i:i + len(a)] += a[:n - i]
        for idx, off, name in s.sfx:
            a = SFX[name]()
            i = int((t0 + s.mark(idx) + off) * SR)
            fx[i:i + len(a)] += a[:max(0, n - i)]
        t0 += s.dur
    mix = voice + fx
    if music_on:
        m = music(n / SR)[:n]  # pode vir 1 amostra menor por arredondamento
        env = np.convolve(np.abs(voice[:len(m)]), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
        env = np.clip(env / (np.percentile(env, 95) + 1e-6), 0, 1)
        m = m * (1 - 0.55 * env).astype(np.float32)   # abaixa a trilha enquanto a voz fala
        mix[:len(m)] += m
    tmp = tempfile.mkdtemp()
    wav, aac, vid = (os.path.join(tmp, f) for f in ("mix.wav", "mix.m4a", "video.mp4"))
    sf.write(wav, mix, SR)
    loudnorm(wav, aac)

    # video
    bg = background()
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr0",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                            "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", vid],
                           stdin=subprocess.PIPE)
    frames = int(math.ceil(total * FPS))
    t0, k = 0.0, 0
    for f in range(frames):
        t = f / FPS
        while k < len(segs) - 1 and t >= t0 + segs[k].dur:
            t0 += segs[k].dur
            k += 1
        s, lt = segs[k], t - t0
        ctx.set_source_surface(bg)
        ctx.paint()
        ctx.push_group()
        ctx.save()
        s.draw(ctx, lt, s)
        ctx.restore()
        draw_header(ctx, s.header)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(ramp(lt, 0, 0.25) if k and not getattr(s, "continuo", False) else 1.0)
        draw_captions(ctx, s, lt)
        text_center(ctx, HANDLE, W / 2, 1840, 28, GRAY, "SemiBold")
        surf.flush()
        enc.stdin.write(bytes(surf.get_data()))
    enc.stdin.close()
    enc.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", aac, "-map", "0:v", "-map", "1:a",
                    "-c", "copy", "-shortest", "-movflags", "+faststart", out], check=True)
    print(f"wrote {out} ({os.path.getsize(out) / 1e6:.1f} MB)")
