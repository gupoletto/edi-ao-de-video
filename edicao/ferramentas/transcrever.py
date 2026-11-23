#!/usr/bin/env python3
"""Etapa 2: transcreve a fala com o tempo de cada frase e (aproximado) de cada palavra.

    python3 edicao/ferramentas/transcrever.py edicao/bruto/meu-video.mp4 [pt] [--turbo]

--turbo usa o Whisper large-v3-turbo (~1,6 GB, bem mais preciso em áudio de rua; mais lento).

Roda no próprio computador: detector de voz (Silero) + Whisper small (sherpa-onnx), em português.
Saída em edicao/trabalho/<nome>/: transcricao.json e transcricao.txt.
"""
import os
import re
import subprocess
import sys

import numpy as np

from comum import SHERPA, gravar, hms, pasta_trabalho, preparar, sonda

SR = 16000


def palavras(texto, a, b):
    """Tempo de cada palavra dentro da frase, proporcional ao número de letras (pontuação pesa uma pausa)."""
    ws = texto.split()
    if not ws:
        return []
    peso = [len(re.sub(r"\W", "", w)) + 1.5 + (2.5 if re.search(r"[,.?!:;]$", w) else 0) for w in ws]
    tot, acc, out = sum(peso), 0.0, []
    for w, k in zip(ws, peso):
        ini = a + (b - a) * acc / tot
        acc += k
        out.append({"w": w, "start": round(ini, 3), "end": round(a + (b - a) * acc / tot, 3)})
    return out


def transcrever(fonte, idioma="pt", turbo=False):
    import sherpa_onnx
    preparar(stt=True, turbo=turbo)
    nome = "turbo" if turbo else "small"
    w = os.path.join(SHERPA, f"sherpa-onnx-whisper-{nome}", f"{nome}-")
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=w + "encoder.int8.onnx", decoder=w + "decoder.int8.onnx", tokens=w + "tokens.txt",
        language=idioma, task="transcribe", num_threads=os.cpu_count() or 4)
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", fonte, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    cfg = sherpa_onnx.VadModelConfig()
    cfg.silero_vad.model = os.path.join(SHERPA, "silero_vad.onnx")
    cfg.silero_vad.min_silence_duration = 0.2
    cfg.silero_vad.min_speech_duration = 0.15
    cfg.silero_vad.max_speech_duration = 8  # frases curtas = tempos de palavra mais precisos
    cfg.sample_rate = SR
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=120)
    segs = []

    def esvaziar():
        while not vad.empty():
            s = vad.front
            st = rec.create_stream()
            st.accept_waveform(SR, s.samples)
            rec.decode_stream(st)
            a, b = s.start / SR, (s.start + len(s.samples)) / SR
            txt = st.result.text.strip()
            if txt:
                segs.append({"start": round(a, 3), "end": round(b, 3), "text": txt, "words": palavras(txt, a, b)})
                print(f"  [{hms(a)}] {txt}", flush=True)
            vad.pop()

    win = cfg.silero_vad.window_size
    for i in range(0, len(audio), win):
        vad.accept_waveform(audio[i:i + win])
        esvaziar()
    vad.flush()
    esvaziar()
    info = sonda(fonte)
    pasta = pasta_trabalho(fonte)
    gravar(os.path.join(pasta, "transcricao.json"), {"fonte": os.path.abspath(fonte), **info, "segments": segs})
    with open(os.path.join(pasta, "transcricao.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(f"[{hms(s['start'])}–{hms(s['end'])}] {s['text']}" for s in segs) + "\n")
    print(f"\n{len(segs)} frases -> {pasta}/transcricao.txt")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    transcrever(args[0], *(args[1:2]), turbo="--turbo" in sys.argv)
