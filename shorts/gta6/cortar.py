#!/usr/bin/env python3
"""Corte vertical de GTA 6 (Short em inglês) a partir de um vídeo de criador que AUTORIZOU (ver shorts/gta6/permissoes.md).

    python3 shorts/gta6/cortar.py video.mp4 --de 754.2 --ate 781.0 --criador "@nome" \\
        --gancho "HE FOUND THE SECRET BUNKER" [--cam 1500,780,400,280] [--contexto "He's been hunting this for hours."] \\
        --saida shorts/lote-AAAA-MM-DD/gta6_bunker.mp4

- recusa o corte se o criador não estiver em permissoes.md;
- vertical 1080x1920: com --cam (retângulo da câmera do streamer no vídeo original, x,y,w,h), gameplay em cima e
  câmera embaixo; sem --cam, zoom no centro do gameplay. Fundo: o próprio quadro desfocado;
- gancho fixo no topo (caixa branca, texto preto), legendas em inglês palavra por palavra (Whisper), crédito
  "Gameplay: @criador (used with permission)";
- --contexto: uma frase narrada (voz do canal) no começo, com o áudio original abaixado enquanto ela toca;
- áudio em -14 LUFS, H.264 + AAC.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

import cairo

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "edicao", "ferramentas"))
sys.path.insert(0, os.path.join(RAIZ, "shorts", "pipeline"))
W, H = 1080, 1920
FONTES = os.path.expanduser("~/.cache/funstuff-fonts")


def autorizado(criador):
    txt = open(os.path.join(AQUI, "permissoes.md"), encoding="utf-8").read().lower()
    linhas = [ln for ln in txt.splitlines() if ln.startswith("|") and criador.lower() in ln]
    return bool(linhas)


def sh(*cmd):
    subprocess.run(cmd, check=True, stdin=subprocess.DEVNULL)


def quebra(ctx, texto, larg):
    linhas, atual = [], ""
    for p in texto.split():
        t = (atual + " " + p).strip()
        if ctx.text_extents(t).x_advance > larg and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = t
    return linhas + [atual]


def sobreposicao(gancho, criador, saida):
    """PNG transparente com o gancho no topo e o crédito embaixo."""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    ctx.select_font_face("Poppins ExtraBold", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(58)
    linhas = quebra(ctx, gancho.upper(), 860)
    alt = 30 + 70 * len(linhas)
    y0 = 300
    ctx.rectangle(90, y0, 900, alt)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    ctx.set_source_rgb(0, 0, 0)
    for i, ln in enumerate(linhas):
        e = ctx.text_extents(ln)
        ctx.move_to(W / 2 - e.x_advance / 2, y0 + 72 + i * 70)
        ctx.show_text(ln)
    ctx.select_font_face("Poppins SemiBold", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(30)
    cred = f"Gameplay: {criador} (used with permission)"
    e = ctx.text_extents(cred)
    ctx.move_to(W / 2 - e.x_advance / 2, 1250)
    ctx.set_source_rgba(1, 1, 1, 0.9)
    ctx.show_text(cred)
    surf.write_to_png(saida)


def legendas(palavras, saida, y=1450):
    """ASS: grupos de 3 palavras, Poppins ExtraBold, a palavra falada em amarelo."""
    cab = (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\n\n[V4+ Styles]\n"
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
           "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
           "MarginR, MarginV, Encoding\n"
           f"Style: L,Poppins ExtraBold,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,"
           f"80,80,{H - y},1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, "
           "Text\n")

    def ts(t):
        return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
    ev = []
    for i in range(0, len(palavras), 3):
        g = palavras[i:i + 3]
        for j, w in enumerate(g):
            fim = g[j + 1]["start"] if j + 1 < len(g) else w["end"] + 0.1
            txt = " ".join(("{\\c&H00D9FF&}" + re.sub(r"[{}\\]", "", x["w"]).upper() + "{\\c&HFFFFFF&}") if k == j
                           else re.sub(r"[{}\\]", "", x["w"]).upper() for k, x in enumerate(g))
            ev.append(f"Dialogue: 0,{ts(w['start'])},{ts(fim)},L,,0,0,0,,{txt}")
    with open(saida, "w", encoding="utf-8") as f:
        f.write(cab + "\n".join(ev) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fonte")
    ap.add_argument("--de", type=float, required=True)
    ap.add_argument("--ate", type=float, required=True)
    ap.add_argument("--criador", required=True)
    ap.add_argument("--gancho", required=True)
    ap.add_argument("--cam", default="")
    ap.add_argument("--contexto", default="")
    ap.add_argument("--saida", required=True)
    a = ap.parse_args()
    if not autorizado(a.criador):
        sys.exit(f"RECUSADO: {a.criador} não está em shorts/gta6/permissoes.md (corte só com autorização).")
    dur = a.ate - a.de
    if not 10 <= dur <= 59:
        sys.exit("O corte precisa ter entre 10 e 59 s.")
    tmp = tempfile.mkdtemp(prefix="gta6_")
    trecho = os.path.join(tmp, "trecho.mkv")
    sh("ffmpeg", "-v", "error", "-y", "-ss", str(a.de), "-t", str(dur), "-i", a.fonte, "-c:v", "libx264", "-crf", "16",
       "-preset", "veryfast", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", trecho)
    # legendas (Whisper em inglês)
    from transcrever import transcrever
    transcrever(trecho, "en")
    tr = json.load(open(os.path.join(RAIZ, "edicao", "trabalho", "trecho", "transcricao.json"), encoding="utf-8"))
    palavras = [w for s in tr["segments"] for w in s["words"]]
    desloc = 0.0
    voz = None
    if a.contexto:  # frase narrada no começo
        import numpy as np
        import soundfile as sf
        import core
        core.setup()
        audio = core.say(a.contexto)
        voz = os.path.join(tmp, "voz.wav")
        sf.write(voz, np.asarray(audio, dtype=np.float32), core.SR)
        desloc = len(audio) / core.SR + 0.2
    ass = os.path.join(tmp, "leg.ass")
    legendas(palavras, ass)
    png = os.path.join(tmp, "sobre.png")
    sobreposicao(a.gancho, a.criador, png)
    # montagem vertical
    fundo = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=28:2,"
             f"eq=brightness=-0.12[bg]")
    if a.cam:
        cx, cy, cw, ch = [int(v) for v in a.cam.split(",")]
        topo = f"[0:v]crop=ih*4/3:ih,scale={W}:810[gp]"
        cam = f"[0:v]crop={cw}:{ch}:{cx}:{cy},scale={W}:-2[cm]"
        lay = f"{fundo};{topo};{cam};[bg][gp]overlay=0:440[a1];[a1][cm]overlay=0:1250:shortest=1[v0]"
    else:
        lay = f"{fundo};[0:v]crop=ih*0.62:ih,scale={W}:-2[gp];[bg][gp]overlay=0:(H-h)/2-60[v0]"
    filtro = f"{lay};[v0][1:v]overlay=0:0[v1];[v1]ass={ass}:fontsdir={FONTES}[v]"
    entradas = ["-i", trecho, "-loop", "1", "-i", png]
    if voz:
        entradas += ["-i", voz]
        filtro += (f";[0:a]volume='if(lt(t,{desloc}),0.25,1)':eval=frame[orig];[2:a]adelay=100|100[vz];"
                   f"[orig][vz]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    else:
        filtro += ";[0:a]loudnorm=I=-14:TP=-1.5[a]"
    os.makedirs(os.path.dirname(os.path.abspath(a.saida)), exist_ok=True)
    sh("ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", filtro, "-map", "[v]", "-map", "[a]",
       "-t", str(dur), "-r", "30", "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", a.saida)
    print(f"pronto: {a.saida} ({dur:.1f} s, crédito {a.criador})")


if __name__ == "__main__":
    main()
