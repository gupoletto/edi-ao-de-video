#!/usr/bin/env python3
"""Etapas 5 e 6: monta a linha do tempo e renderiza.

    python3 edicao/ferramentas/montar.py edicao/bruto/meu-video.mp4 --previa             # 540p, para revisar
    python3 edicao/ferramentas/montar.py edicao/bruto/meu-video.mp4 --previa --trecho 60 120   # só um pedaço
    python3 edicao/ferramentas/montar.py edicao/bruto/meu-video.mp4                      # final -> edicao/final/

Como nos vídeos de referência, tudo é ffmpeg: `select` mantém só os trechos do plano (com a abertura, se
houver, na frente), o áudio segue contínuo por baixo, os elementos entram com `overlay=enable='between(t,..)'`,
o zoom alterna a cada corte, a tela dividida e a gravação de tela usam o próprio vídeo num cartão ou numa
miniatura, e as legendas são queimadas a partir da transcrição. Final: H.264 + AAC, fps do original, −14 LUFS.
"""
import argparse
import json
import math
import os
import re
import subprocess

import numpy as np
import soundfile as sf

from comum import FINAL, FONTES, RAIZ, gravar, ler, pasta_trabalho, preparar, sonda
from elementos import CREME, SO_MONTAR, TAUPE, TELA_CHEIA, cartao_rect, hexrgb, no_editado, resolucao
from planejar import dur_abertura, saida

SR = 48000


def entre(intervalos, var="t"):
    return "+".join(f"between({var},{a:.3f},{b:.3f})" for a, b in intervalos) or "0"


def na_abertura(plano, t):
    """Tempo no bruto -> tempo no vídeo editado, se o instante faz parte da abertura (senão None)."""
    acc = 0.0
    for a, b in plano.get("abertura", []):
        if a <= t <= b:
            return acc + t - a
        acc += b - a
    return None


# ---------- legendas (ASS) ----------

def ass_tempo(t):
    h, r = divmod(max(0.0, t), 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def ass_cor(rgb):
    r, g, b = (int(c * 255) for c in rgb)
    return f"&H{b:02X}{g:02X}{r:02X}&"


def legendas(plano, tr, W, H, caminho):
    """palavra: 1–3 palavras, contorno preto, palavra-chave em itálico amarelo (estilo dinâmico).
    frase: 2–3 palavras em sans pesada branca, a palavra-chave em serifa itálica clara, entrando com desfoque.
    caixa: frase curta numa caixa escura discreta."""
    modo = plano.get("legenda_estilo") or ("palavra" if plano["estilo"] == "dinamico" else "caixa")
    texto_cor, chave_cor = ass_cor(hexrgb(CREME)), ass_cor(hexrgb(TAUPE))  # paleta do canal
    tc = "&H00" + texto_cor[2:-1]
    vertical = H > W
    if modo == "palavra":
        tam, max_pal = (88 if vertical else 64), 3
        estilo = (f"Style: L,Poppins ExtraBold,{tam},{tc},{tc},&H003A1001,&H643A1001,0,0,0,0,100,100,0,0,"
                  f"1,{tam // 11},2,2,60,60,{int(H * (0.30 if vertical else 0.08))},1")
    elif modo == "frase":
        tam, max_pal = (84 if vertical else 62), 3
        estilo = (f"Style: L,Poppins ExtraBold,{tam},{tc},{tc},&H503A1001,&H783A1001,0,0,0,0,100,100,-1,0,"
                  f"1,2,4,2,60,60,{int(H * (0.26 if vertical else 0.12))},1")
    else:
        tam, max_pal = (64 if vertical else 46), 6
        estilo = (f"Style: L,Inter,{tam},{tc},{tc},&H003A1001,&H303A1001,-1,0,0,0,100,100,0,0,"
                  f"3,14,0,2,80,80,{int(H * (0.22 if vertical else 0.06))},1")
    cheios = [(e["de"], e["ate"]) for e in plano["elementos"] if e["tipo"] in TELA_CHEIA | {"tela"}]
    fix = {k.lower(): v for k, v in plano.get("correcoes", {}).items()}  # ex.: {"cloud": "Claude"}
    janelas = [(a, b, "main") for a, b in plano["manter"]] + [(a, b, "abertura") for a, b in plano.get("abertura", [])]
    eventos = []
    for s in tr["segments"]:
        for a0, b0, onde in janelas:
            ws = [w for w in s["words"] if a0 <= w["start"] and w["end"] <= b0 + 0.05]
            for i in range(0, len(ws), max_pal):
                grupo = ws[i:i + max_pal]
                a, b = grupo[0]["start"], grupo[-1]["end"]
                if modo != "palavra" and onde == "main" and any(x <= a < y for x, y in cheios):
                    continue  # o card de tela cheia já tem o próprio texto
                palavras = []
                for w in grupo:
                    p = re.sub(r"[{}\\]", "", w["w"])
                    nu = re.sub(r"\W", "", p).lower()
                    if nu in fix:
                        p = p.replace(re.sub(r"\W", "", p), fix[nu])
                    palavras.append(p)
                chave = max(range(len(palavras)), key=lambda k: len(re.sub(r"\W", "", palavras[k])))
                if len(re.sub(r"\W", "", palavras[chave])) < (7 if modo == "palavra" else 5):
                    chave = -1
                if modo == "palavra" and chave >= 0:
                    palavras[chave] = rf"{{\i1\c{chave_cor}}}" + palavras[chave] + rf"{{\i0\c{texto_cor}}}"
                elif modo == "frase" and chave >= 0:
                    palavras[chave] = (rf"{{\fnSource Serif 4 Semibold\i1\c{chave_cor}}}" + palavras[chave] +
                                       rf"{{\fnPoppins ExtraBold\i0\c{texto_cor}}}")
                texto = " ".join(palavras)
                if modo == "palavra":
                    texto = r"{\fscx80\fscy80\t(0,90,\fscx100\fscy100)}" + texto  # "pulo" curto na entrada
                elif modo == "frase":
                    texto = r"{\fad(120,60)\blur8\t(0,160,\blur0)}" + texto  # entra desfocada, como no Léo Lamera
                if onde == "main":
                    ta, tb = saida(plano, a), saida(plano, b)
                else:
                    ta, tb = na_abertura(plano, a), na_abertura(plano, b)
                eventos.append((ta, tb + 0.05, texto))
    eventos.sort()
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


# ---------- efeitos sonoros (sintetizados, sem direitos autorais) ----------

def _whoosh(dur=0.45):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    ruido = np.random.default_rng(3).standard_normal(n)
    # passa-baixa móvel: a "varrida" sobe e desce
    corte = 0.02 + 0.25 * np.sin(np.pi * t)
    y, acc = np.zeros(n), 0.0
    for i in range(n):
        acc += corte[i] * (ruido[i] - acc)
        y[i] = acc
    return (y / np.abs(y).max() * 0.22 * np.sin(np.pi * t) ** 1.5).astype(np.float32)


def _pop(dur=0.09):
    t = np.arange(int(dur * SR)) / SR
    f = 900 * np.exp(-t * 18) + 380
    return (0.35 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)).astype(np.float32)


def efeitos(plano, total, caminho):
    """Whoosh na entrada de cada card de tela cheia, "pop" em cada item que entra."""
    pista = np.zeros(int((total + 1) * SR), np.float32)
    w, p, n = _whoosh(), _pop(), 0

    def por(som, t):
        i = int(max(0.0, t) * SR)
        pista[i:i + len(som)] += som[:max(0, len(pista) - i)]

    for e in plano["elementos"]:
        if e["tipo"] in SO_MONTAR and e["tipo"] != "tela":
            continue
        e = no_editado(plano, e)
        a, dur = e["de"], e["ate"] - e["de"]
        if e["tipo"] in TELA_CHEIA or e["tipo"] == "tela":
            por(w, a - 0.12)
            n += 1
        itens = e.get("itens", [])
        if e["tipo"] == "letreiro":
            passo = max(0.3, min(1.0, (dur * 0.5) / max(1, len(itens))))
            for k in range(len(itens)):
                por(p, a + 0.15 + k * passo)
                n += 1
        elif e["tipo"] == "lista":
            passo = max(0.35, min(1.2, (dur * 0.6) / max(1, len(itens))))
            for k in range(len(itens)):
                por(p, (e["tempos"][k] if e.get("tempos") else a + 0.4 + k * passo))
                n += 1
    sf.write(caminho, pista, SR)
    return n


# ---------- montagem ----------

def recorte_rosto(cw, ch, fx, fy, W, H, altura=0.96):
    """crop no quadro base (W x H) com a proporção cw:ch, em volta do foco."""
    hh = H * altura
    ww = hh * cw / ch
    if ww > W:
        ww, hh = W, W * ch / cw
    x = min(max(W * fx - ww / 2, 0), W - ww)
    y = min(max(H * fy - hh / 2, 0), H - hh)
    return f"crop={ww:.0f}:{hh:.0f}:{x:.0f}:{y:.0f},scale={cw:.0f}:{ch:.0f}"


def montar(fonte, previa=False, trecho=None, crf=20):
    preparar()
    pasta = pasta_trabalho(fonte)
    plano = ler(os.path.join(pasta, "plano.json"))
    tr = ler(os.path.join(pasta, "transcricao.json"))
    info = sonda(plano["fonte"])
    W, H = resolucao(plano)
    fx, fy = plano.get("foco", [0.5, 0.42])
    manter, abertura = plano["manter"], plano.get("abertura", [])
    total = dur_abertura(plano) + sum(b - a for a, b in manter)
    els = plano["elementos"]

    entradas, idx = ["-i", plano["fonte"]], 1
    sfx = None
    if plano.get("sons", True):
        sfx = os.path.join(pasta, "efeitos.wav")
        print(f"  {efeitos(plano, total, sfx)} efeitos sonoros")
        entradas += ["-i", sfx]
        sfx_idx, idx = idx, idx + 1

    # 1. linha do tempo: abertura (gancho) + trechos mantidos, vídeo e áudio juntos
    g, a_g = [], []
    if abertura:
        # cada trecho da abertura é uma entrada própria (na ordem do plano, não na do bruto; um split
        # guardaria o vídeo todo na memória), recortado com -ss/-t e emendado antes dos trechos mantidos

        for k, (a, b) in enumerate(abertura):
            entradas += ["-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", plano["fonte"]]
            g.append(f"[{idx}:v]setpts=PTS-STARTPTS[va{k}]")
            a_g.append(f"[{idx}:a]asetpts=PTS-STARTPTS[aa{k}]")
            idx += 1
        g.append(f"[0:v]select='{entre(manter)}',setpts=N/FRAME_RATE/TB[vm]")
        a_g.append(f"[0:a]aselect='{entre(manter)}',asetpts=N/SR/TB[am]")
        # concat precisa de vídeo e áudio juntos: aqui só vídeo e só áudio, cada um com seu concat
        g.append("".join(f"[va{k}]" for k in range(len(abertura))) + f"[vm]concat=n={len(abertura) + 1}:v=1:a=0[lin]")
        a_g.append("".join(f"[aa{k}]" for k in range(len(abertura))) + f"[am]concat=n={len(abertura) + 1}:v=0:a=1[alin]")
    else:
        g.append(f"[0:v]select='{entre(manter)}',setpts=N/FRAME_RATE/TB[lin]")
        a_g.append(f"[0:a]aselect='{entre(manter)}',asetpts=N/SR/TB[alin]")

    # 2. geometria: corta para a proporção do formato, centrado no foco, e escala; zoom alternado
    alvo = W / H
    if abs(info["w"] / info["h"] - alvo) < 0.01:
        base = f"scale={W}:{H}"
    elif info["w"] / info["h"] > alvo:
        base = f"crop=ih*{alvo:.5f}:ih:(iw-ih*{alvo:.5f})*{fx}:0,scale={W}:{H}"
    else:
        base = f"crop=iw:iw/{alvo:.5f}:0:(ih-iw/{alvo:.5f})*{fy},scale={W}:{H}"
    g.append(f"[lin]{base},setsar=1,split=2[b0][b1]")
    zooms = [(saida(plano, z["de"]), saida(plano, z["ate"])) for z in plano["zooms"]]
    z = plano["zooms"][0]["escala"] if plano["zooms"] else 1.1
    g.append(f"[b1]crop=iw/{z}:ih/{z}:(iw-iw/{z})*{fx}:(ih-ih/{z})*{fy},scale={W}:{H}[bz]")
    g.append(f"[b0][bz]overlay=enable='{entre(zooms)}',format=yuv420p[vbase]")

    # áudio: voz contínua + efeitos; −14 LUFS em duas passadas (a primeira só mede)
    if sfx:
        a_g.append(f"[{sfx_idx}:a]aresample={SR}[fx]")
        a_g.append(f"[alin]aresample={SR}[voz];[voz][fx]amix=inputs=2:duration=first:normalize=0[amix]")
        a_fim = "amix"
    else:
        a_fim = "alin"
    medir = ";".join(a_g) + f";[{a_fim}]loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json"
    med = subprocess.run(["ffmpeg", "-hide_banner"] + entradas + ["-vn", "-filter_complex", medir, "-f", "null", "-"],
                         capture_output=True, text=True, check=True).stderr
    m = json.loads(med[med.rindex("{"):])
    a_g.append(f"[{a_fim}]loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
               f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']},"
               "aresample=48000[aout]")
    script_a = os.path.join(pasta, "filtro_base.txt")
    with open(script_a, "w", encoding="utf-8") as f:
        f.write(";\n".join(g + a_g))
    # passada 1: linha do tempo pronta (vídeo quase sem perda + áudio PCM) num arquivo intermediário.
    # A passada 2 abre esse arquivo uma vez para cada camada que usa o próprio vídeo (cartão, miniatura,
    # pop-up): várias entradas em vez de um split, que trava quando as camadas consomem em ritmos diferentes.
    lin = os.path.join(pasta, "linha_do_tempo.mkv")
    print(f"passada 1: linha do tempo ({total:.0f}s)...", flush=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + entradas + ["-filter_complex_script", script_a,
                    "-map", "[vbase]", "-map", "[aout]", "-r", f"{info['fps']:.3f}", "-c:v", "libx264",
                    "-preset", "ultrafast" if previa else "veryfast", "-crf", "23" if previa else "12",
                    "-c:a", "pcm_s16le", lin], check=True)

    entradas, idx, g = ["-i", lin], 1, []
    atual, n = "0:v", 0

    def camada(filtro):
        nonlocal atual, n
        n += 1
        g.append(f"[{atual}]{filtro}[c{n}]" if not filtro.startswith("[") else f"{filtro}[c{n}]")
        atual = f"c{n}"

    def copia(a, b):
        """O vídeo da linha do tempo de novo, como entrada separada, só no trecho [a, b]."""
        nonlocal entradas, idx
        entradas += ["-i", lin]
        idx += 1
        g.append(f"[{idx - 1}:v]trim=start={a:.3f}:end={b:.3f}[q{idx - 1}]")  # mantém os tempos originais
        return f"q{idx - 1}"

    # 3. elementos, na ordem do plano (os de cima por último)
    for i, e in enumerate(els, 1):
        a, b = saida(plano, e["de"]), saida(plano, e["ate"])
        quando = f"enable='between(t,{a:.3f},{b:.3f})'"
        tipo = e["tipo"]
        if tipo == "dividido":  # o rosto entra no cartão; o clipe do elemento tem o buraco
            x, y, cw, ch = cartao_rect(W, H, e.get("lado", "esquerda"))
            g.append(f"[{copia(a, b)}]{recorte_rosto(cw, ch, fx, fy, W, H)}[r{i}]")
            camada(f"[{atual}][r{i}]overlay={x:.0f}:{y:.0f}:eof_action=pass:{quando}")
        if tipo == "tela":  # gravação de tela em tela cheia + rosto em miniatura arredondada
            arq = e["arquivo"] if os.path.isabs(e["arquivo"]) else os.path.join(RAIZ, e["arquivo"])
            entradas += ["-ss", f"{e.get('inicio', 0):.3f}", "-itsoffset", f"{a:.3f}", "-i", arq]
            g.append(f"[{idx}:v]scale={W}:{H}:force_original_aspect_ratio=decrease,"
                     f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x01103A,setsar=1[t{i}]")
            camada(f"[{atual}][t{i}]overlay=eof_action=pass:{quando}")
            idx += 1
            pw, ph = (W * 0.2, W * 0.2 * 1.15) if W > H else (W * 0.34, W * 0.34 * 1.15)
            pw, ph, r = round(pw / 2) * 2, round(ph / 2) * 2, round(pw * 0.12)
            canto = (f"255*lte(pow(max(abs(X-W/2)-(W/2-{r})\\,0)\\,2)+pow(max(abs(Y-H/2)-(H/2-{r})\\,0)\\,2)\\,{r * r})")
            g.append(f"[{copia(a, b)}]{recorte_rosto(pw, ph, fx, fy, W, H, 0.8)},format=yuva420p,"
                     f"geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='{canto}'[pm{i}]")
            margem = W * 0.025
            px = margem if e.get("pip", "esquerda") == "esquerda" else W - pw - margem
            camada(f"[{atual}][pm{i}]overlay={px:.0f}:{H - ph - margem:.0f}:eof_action=pass:{quando}")
            continue
        if tipo == "foco":  # holofote: escurece tudo fora da área
            ax, ay, aw, ah = (v * d for v, d in zip(e["area"], (W, H, W, H)))
            escuro = "color=0x01103A@0.65:t=fill"
            for bx, by, bw, bh in ((0, 0, W, ay), (0, ay + ah, W, H - ay - ah), (0, ay, ax, ah),
                                   (ax + aw, ay, W - ax - aw, ah)):
                if bw > 0 and bh > 0:
                    camada(f"drawbox=x={bx:.0f}:y={by:.0f}:w={bw:.0f}:h={bh:.0f}:{escuro}:{quando}")
            camada(f"drawbox=x={ax:.0f}:y={ay:.0f}:w={aw:.0f}:h={ah:.0f}:color=0x{CREME[1:]}@0.9:t=4:{quando}")
            continue
        if tipo == "popup":  # recorta a área e mostra ampliada na frente
            ax, ay, aw, ah = (v * d for v, d in zip(e["area"], (W, H, W, H)))
            k = e.get("escala", 1.6)
            ow, oh = min(aw * k, W * 0.9), min(ah * k, H * 0.9)
            ox = min(max(ax + aw / 2 - ow / 2, W * 0.05), W * 0.95 - ow)
            oy = min(max(ay + ah / 2 - oh / 2, H * 0.05), H * 0.95 - oh)
            g.append(f"[{copia(a, b)}]crop={aw:.0f}:{ah:.0f}:{ax:.0f}:{ay:.0f},scale={ow:.0f}:{oh:.0f}[u{i}]")
            camada(f"drawbox=x={ox - 6:.0f}:y={oy - 6:.0f}:w={ow + 12:.0f}:h={oh + 12:.0f}:color=0x{CREME[1:]}:t=fill:{quando}")
            camada(f"[{atual}][u{i}]overlay={ox:.0f}:{oy:.0f}:eof_action=pass:{quando}")
            continue
        mov = os.path.join(pasta, "elementos", f"E{i:02d}_{tipo}.mov")
        if not os.path.exists(mov):
            raise SystemExit(f"falta {mov}: rode elementos.py antes")
        entradas += ["-itsoffset", f"{a:.3f}", "-i", mov]
        camada(f"[{atual}][{idx}:v]overlay=eof_action=pass:{quando}")
        idx += 1
    if plano.get("legendas"):
        ass = os.path.join(pasta, "legendas.ass")
        print(f"  {legendas(plano, tr, W, H, ass)} legendas ({plano.get('legenda_estilo', 'padrão')})")
        camada(f"ass='{ass}':fontsdir='{FONTES}'")
    g.append(f"[{atual}]" + ("scale=-2:540," if previa else "") + "format=yuv420p[vout]")

    script = os.path.join(pasta, "filtro.txt")
    with open(script, "w", encoding="utf-8") as f:
        f.write(";\n".join(g))
    nome = os.path.splitext(os.path.basename(plano["fonte"]))[0]
    if previa:
        out = os.path.join(pasta, "previa.mp4" if not trecho else f"previa_{trecho[0]:.0f}-{trecho[1]:.0f}.mp4")
        vcod = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "28"]
    else:
        os.makedirs(FINAL, exist_ok=True)
        out = os.path.join(FINAL, f"{nome}_editado.mp4")
        vcod = ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-profile:v", "high"]
    janela = ["-ss", f"{trecho[0]:.3f}", "-to", f"{trecho[1]:.3f}"] if trecho else []
    cmd = (["ffmpeg", "-v", "error", "-stats", "-y"] + entradas +
           ["-filter_complex_script", script, "-map", "[vout]", "-map", "0:a", "-r", f"{info['fps']:.3f}"] +
           janela + vcod + ["-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out])
    print(f"passada 2: montando {total:.0f}s ({len(abertura)} trechos de abertura, {len(manter)} trechos, "
          f"{len(els)} elementos)...", flush=True)
    subprocess.run(cmd, check=True)
    gravar(os.path.join(pasta, "ultima_montagem.json"), {"saida": out, "comando": cmd})
    print(f"pronto: {out}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("fonte")
    ap.add_argument("--previa", action="store_true")
    ap.add_argument("--trecho", nargs=2, type=float, metavar=("DE", "ATE"),
                    help="só este pedaço do vídeo editado (segundos), para aprovar o estilo antes do vídeo todo")
    ap.add_argument("--crf", type=int, default=20, help="qualidade do final (menor = melhor e maior)")
    a = ap.parse_args()
    montar(a.fonte, a.previa, a.trecho, a.crf)
