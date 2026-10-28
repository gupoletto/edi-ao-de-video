#!/usr/bin/env python3
"""Etapas 5 e 6: monta a linha do tempo e renderiza.

    python3 edicao/ferramentas/montar.py edicao/bruto/meu-video.mp4 --previa   # rápido, 540p, para revisar
    python3 edicao/ferramentas/montar.py edicao/bruto/meu-video.mp4            # final -> edicao/final/

Como nos vídeos de referência, tudo é ffmpeg: `select` mantém só os trechos do plano, o áudio segue
contínuo por baixo, os elementos entram com `overlay=enable='between(t,..)'`, o zoom alterna a cada corte
e as legendas são queimadas a partir da transcrição. Final: H.264 + AAC, fps do original, −14 LUFS.
"""
import argparse
import json
import os
import re
import subprocess

from comum import FINAL, FONTES, gravar, ler, pasta_trabalho, preparar, sonda
from elementos import TELA_CHEIA, resolucao
from planejar import saida


def entre(intervalos, var="t"):
    return "+".join(f"between({var},{a:.3f},{b:.3f})" for a, b in intervalos) or "0"


# ---------- legendas (ASS) ----------

def ass_tempo(t):
    h, r = divmod(max(0.0, t), 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def legendas(plano, tr, W, H, caminho):
    din = plano["estilo"] == "dinamico"
    vertical = H > W
    if din:  # 1 a 3 palavras, sans pesada branca com contorno preto; palavra-chave em itálico amarelo
        tam, max_pal = (88 if vertical else 64), 3
        estilo = (f"Style: L,Poppins ExtraBold,{tam},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,"
                  f"1,{tam // 11},2,2,60,60,{int(H * (0.30 if vertical else 0.08))},1")
    else:  # frase curta numa caixa escura discreta
        tam, max_pal = (64 if vertical else 46), 6
        estilo = (f"Style: L,Inter,{tam},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,"
                  f"3,14,0,2,80,80,{int(H * (0.22 if vertical else 0.06))},1")
    cheios = [(e["de"], e["ate"]) for e in plano["elementos"] if e["tipo"] in TELA_CHEIA]
    fix = {k.lower(): v for k, v in plano.get("correcoes", {}).items()}  # ex.: {"cloud": "Claude"}
    eventos = []
    for s in tr["segments"]:
        ws = [w for w in s["words"] if any(a <= w["start"] and w["end"] <= b + 0.05 for a, b in plano["manter"])]
        for i in range(0, len(ws), max_pal):
            grupo = ws[i:i + max_pal]
            a, b = grupo[0]["start"], grupo[-1]["end"]
            if not din and any(x <= a < y for x, y in cheios):
                continue  # no editorial, o card de tela cheia já tem o texto
            txt = []
            for w in grupo:
                p = re.sub(r"[{}\\]", "", w["w"])
                nu = re.sub(r"\W", "", p).lower()
                if nu in fix:
                    p = p.replace(re.sub(r"\W", "", p), fix[nu])
                limpo = re.sub(r"\W", "", p)
                if din and len(limpo) >= 7:
                    p = r"{\i1\c&H3CD7FF&}" + p + r"{\i0\c&HFFFFFF&}"
                txt.append(p)
            texto = " ".join(txt)
            if din:
                texto = r"{\fscx80\fscy80\t(0,90,\fscx100\fscy100)}" + texto  # "pulo" curto na entrada
            eventos.append((saida(plano, a), saida(plano, b) + 0.05, texto))
    for k in range(len(eventos) - 1):  # nunca duas legendas ao mesmo tempo
        a, b, t = eventos[k]
        eventos[k] = (a, min(b, eventos[k + 1][0]), t)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 0\n\n"
                "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
                "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
                f"Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n{estilo}\n\n"
                "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        for a, b, t in eventos:
            if b > a:
                f.write(f"Dialogue: 0,{ass_tempo(a)},{ass_tempo(b)},L,,0,0,0,,{t}\n")
    return len(eventos)


# ---------- montagem ----------

def montar(fonte, previa=False):
    preparar()
    pasta = pasta_trabalho(fonte)
    plano = ler(os.path.join(pasta, "plano.json"))
    tr = ler(os.path.join(pasta, "transcricao.json"))
    info = sonda(plano["fonte"])
    W, H = resolucao(plano)
    fx, fy = plano.get("foco", [0.5, 0.42])
    manter = plano["manter"]
    sel = entre(manter)
    dur = sum(b - a for a, b in manter)

    # geometria da base: corta para a proporção do formato, centrado no foco, e escala
    alvo = W / H
    if abs(info["w"] / info["h"] - alvo) < 0.01:
        base = f"scale={W}:{H}"
    elif info["w"] / info["h"] > alvo:
        base = f"crop=ih*{alvo:.5f}:ih:(iw-ih*{alvo:.5f})*{fx}:0,scale={W}:{H}"
    else:
        base = f"crop=iw:iw/{alvo:.5f}:0:(ih-iw/{alvo:.5f})*{fy},scale={W}:{H}"

    g = [f"[0:v]select='{sel}',setpts=N/FRAME_RATE/TB,{base},setsar=1,split=2[b0][b1]"]
    zooms = [(saida(plano, z["de"]), saida(plano, z["ate"])) for z in plano["zooms"]]
    z = plano["zooms"][0]["escala"] if plano["zooms"] else 1.1
    g.append(f"[b1]crop=iw/{z}:ih/{z}:(iw-iw/{z})*{fx}:(ih-ih/{z})*{fy},scale={W}:{H}[bz]")
    g.append(f"[b0][bz]overlay=enable='{entre(zooms)}'[v0]")
    entradas, atual = [], "v0"
    for i, e in enumerate(plano["elementos"], 1):
        mov = os.path.join(pasta, "elementos", f"E{i:02d}_{e['tipo']}.mov")
        if not os.path.exists(mov):
            raise SystemExit(f"falta {mov}: rode elementos.py antes")
        a = saida(plano, e["de"])
        entradas += ["-itsoffset", f"{a:.3f}", "-i", mov]
        g.append(f"[{atual}][{i}:v]overlay=eof_action=pass:enable='between(t,{a:.3f},{a + e['ate'] - e['de']:.3f})'[v{i}]")
        atual = f"v{i}"
    if plano.get("legendas"):
        ass = os.path.join(pasta, "legendas.ass")
        n = legendas(plano, tr, W, H, ass)
        g.append(f"[{atual}]ass='{ass}':fontsdir='{FONTES}'[vl]")
        atual = "vl"
        print(f"  {n} legendas")
    if previa:
        g.append(f"[{atual}]scale=-2:540[vp]")
        atual = "vp"
    g.append(f"[{atual}]format=yuv420p[vout]")

    # áudio: os mesmos trechos, contínuo; volume em −14 LUFS (duas passadas, só no áudio)
    a_sel = f"[0:a]aselect='{sel}',asetpts=N/SR/TB"
    med = subprocess.run(["ffmpeg", "-hide_banner", "-i", plano["fonte"], "-vn", "-filter_complex",
                          a_sel + ",loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                         capture_output=True, text=True, check=True).stderr
    m = json.loads(med[med.rindex("{"):])
    g.append(a_sel + f",loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
             f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']},"
             "aresample=48000[aout]")

    script = os.path.join(pasta, "filtro.txt")
    with open(script, "w", encoding="utf-8") as f:
        f.write(";\n".join(g))
    nome = os.path.splitext(os.path.basename(plano["fonte"]))[0]
    if previa:
        out = os.path.join(pasta, "previa.mp4")
        vcod = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "28"]
    else:
        os.makedirs(FINAL, exist_ok=True)
        out = os.path.join(FINAL, f"{nome}_editado.mp4")
        vcod = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high"]
    cmd = (["ffmpeg", "-v", "error", "-stats", "-y", "-i", plano["fonte"]] + entradas +
           ["-filter_complex_script", script, "-map", "[vout]", "-map", "[aout]", "-r", f"{info['fps']:.3f}"] +
           vcod + ["-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    print(f"montando {dur:.0f}s ({len(manter)} trechos, {len(plano['elementos'])} elementos)...", flush=True)
    subprocess.run(cmd, check=True)
    gravar(os.path.join(pasta, "ultima_montagem.json"), {"saida": out, "comando": cmd})
    print(f"pronto: {out}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("fonte")
    ap.add_argument("--previa", action="store_true")
    a = ap.parse_args()
    montar(a.fonte, a.previa)
