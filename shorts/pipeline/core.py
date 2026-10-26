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
VOICE, SPEED = "am_michael", 1.08
HANDLE = "@funstuff-67"

BLUE = (0.36, 0.78, 0.98)
PINK = (1.0, 0.36, 0.54)
GREEN = (0.30, 0.90, 0.50)
RED = (1.0, 0.30, 0.30)
YELLOW = (1.0, 0.85, 0.25)
WHITE = (1, 1, 1)
GRAY = (0.45, 0.47, 0.52)

# Illustration area (between header and captions).
AREA = (60, 420, 1020, 1400)

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


def draw_header(ctx, h):
    if not h:
        return
    if "big" in h:
        text_center(ctx, h["big"], W / 2, 220, h.get("big_size", 130), h.get("color", BLUE), "ExtraBold")
    if "sub" in h:
        text_center(ctx, h["sub"], W / 2, 300, 52)
    if "title" in h:  # multi-line headline (intro / outro)
        font(ctx, 72, "ExtraBold")
        lines = wrap(ctx, h["title"].split(), 960)
        for i, ln in enumerate(lines):
            text_center(ctx, " ".join(ln), W / 2, 200 + i * 86, 72, WHITE, "ExtraBold")
    if "dots" in h:
        labels, active = h["dots"]
        n = len(labels)
        for i, lab in enumerate(labels):
            x = W / 2 + (i - (n - 1) / 2) * 62
            ctx.arc(x, 365, 21, 0, 2 * math.pi)
            if i == active:
                ctx.set_source_rgb(*(h.get("color", BLUE)))
            else:
                ctx.set_source_rgba(1, 1, 1, 0.16)
            ctx.fill()
            text_center(ctx, lab, x, 374, 22, WHITE, "Bold")


def draw_captions(ctx, seg, t):
    for (a, b, words) in seg.lines:
        if a <= t <= b + 0.35:
            break
    else:
        return
    font(ctx, 52)
    rows = wrap(ctx, [w for _, w in words], 900)
    lh, top = 68, 1560 - (len(rows) * 68) / 2
    widest = max(ctx.text_extents(" ".join(r)).x_advance for r in rows)
    round_rect(ctx, W / 2 - widest / 2 - 30, top - 18, widest + 60, len(rows) * lh + 36, 22)
    ctx.set_source_rgba(0, 0, 0, 0.55)
    ctx.fill()
    k = 0
    for i, r in enumerate(rows):
        line = " ".join(r)
        x = W / 2 - ctx.text_extents(line).x_advance / 2
        y = top + i * lh + 52
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


def music(dur):
    """Original synth bed: slow I–V–vi–IV pad with a gentle arpeggio."""
    n = int(dur * SR)
    out = np.zeros(n, np.float32)
    chords = [(261.6, 329.6, 392.0), (196.0, 246.9, 293.7), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6)]
    bar = 2.0
    for k in range(int(dur / bar) + 1):
        c = chords[k % 4]
        s = int(k * bar * SR)
        for f in c:
            p = tone(f / 2, bar + 0.3, 0.05, attack=0.4, kind="tri")
            p *= np.linspace(1, 0.3, len(p)).astype(np.float32)
            e = min(n, s + len(p))
            if s < n:
                out[s:e] += p[:e - s]
        for j in range(4):
            f = c[j % 3] * 2
            ss = s + int(j * bar / 4 * SR)
            p = tone(f, 0.45, 0.035, decay=0.18)
            e = min(n, ss + len(p))
            if ss < n:
                out[ss:e] += p[:e - ss]
    fade = int(0.5 * SR)
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


def render(segments, out, music_on=True):
    setup()
    segs = [s.build() for s in segments]
    total = sum(s.dur for s in segs)
    assert 20 <= total <= 60, f"duration {total:.1f}s outside 20-60 s"
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
        mix += music(n / SR)[:n]
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
        ctx.paint_with_alpha(ramp(lt, 0, 0.25) if k else 1.0)
        draw_captions(ctx, s, lt)
        text_center(ctx, HANDLE, W / 2, 1840, 28, GRAY, "SemiBold")
        surf.flush()
        enc.stdin.write(bytes(surf.get_data()))
    enc.stdin.close()
    enc.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", aac, "-map", "0:v", "-map", "1:a",
                    "-c", "copy", "-shortest", "-movflags", "+faststart", out], check=True)
    print(f"wrote {out} ({os.path.getsize(out) / 1e6:.1f} MB)")
