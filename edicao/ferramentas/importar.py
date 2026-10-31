#!/usr/bin/env python3
"""Etapa 1: prepara o vídeo da câmera para o kit, sem perder qualidade.

    python3 edicao/ferramentas/importar.py ~/Downloads/IMG_1234.MOV [nome] [--cor=neutra] [--4k]
        -> edicao/bruto/<nome>.mkv

- HDR (iPhone: HLG/Dolby Vision, BT.2020, 10 bits) vira SDR BT.709 com tonemapping "hable" (branco de referência
  203 nits): preserva as altas luzes do rosto sob sol ou luz fria. O "mobius" com 100 nits, usado antes, estourava
  rosto e janela e deixava as cores saturadas demais (queixa do usuário nos episódios 10 e 11).
- Tratamento de cor "cinema" (padrão): saturação 0,92, sombras levemente frias, meios-tons e altas quentes, curva
  suave que segura os brancos. --cor neutra desliga.
- Até 4K: reduz para 1080p com lanczos (mais nítido que gravar em 1080p) ou mantém (--4k).
- Taxa de quadros variável vira fixa (30 ou 60): o corte quadro a quadro do montar.py precisa disso para a voz
  não descolar da boca.
- Vídeo quase sem perda (x264 crf 12, quadro-chave a cada 1 s) e áudio PCM 48 kHz, para nenhuma etapa seguinte
  depender de outra compressão.
"""
import json
import os
import subprocess
import sys

from comum import BRUTO

HDR = {"arib-std-b67", "smpte2084"}
TONEMAP = ["zscale=t=linear:npl=203", "format=gbrpf32le", "zscale=p=bt709", "tonemap=hable:desat=0.4",
           "zscale=t=bt709:m=bt709:r=tv", "format=yuv420p", "eq=gamma=1.22:contrast=1.03"]
CINEMA = ["eq=saturation=0.92",
          "colorbalance=rs=-0.02:bs=0.03:rm=0.04:gm=0.01:bm=-0.03:rh=0.05:gh=0.02:bh=-0.05",
          "curves=all='0/0.02 0.5/0.52 0.85/0.86 1/0.97'"]


def sondar(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate,avg_frame_rate,color_transfer,pix_fmt", "-of", "json", arq],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)["streams"][0]


def fracao(s):
    n, d = s.split("/")
    return float(n) / float(d) if float(d) else 0.0


def importar(arq, nome=None, cor="cinema", k4=False):
    v = sondar(arq)
    nome = nome or os.path.splitext(os.path.basename(arq))[0]
    destino = os.path.join(BRUTO, nome + ".mkv")
    fps_med = fracao(v["avg_frame_rate"]) or fracao(v["r_frame_rate"])
    fps = 60 if fps_med > 45 else 30
    filtros = list(TONEMAP) if v.get("color_transfer") in HDR else []
    if cor == "cinema":
        filtros += CINEMA
    if v["width"] > 1920 and not k4:
        filtros.append("scale=1920:1080:flags=lanczos")
    filtros += ["format=yuv420p", f"fps={fps}"]
    print(f"{os.path.basename(arq)}: {v['width']}x{v['height']}, {fps_med:.2f} fps, "
          f"{'HDR ' + v['color_transfer'] if v.get('color_transfer') in HDR else 'SDR'} -> {fps} fps SDR BT.709",
          flush=True)
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", "-i", arq, "-map", "0:v:0", "-map", "0:a:0",
                    "-vf", ",".join(filtros), "-c:v", "libx264", "-preset", "faster", "-crf", "12",
                    "-x264-params", f"keyint={fps}", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-colorspace", "bt709", "-c:a", "pcm_s16le", "-ar", "48000", destino], check=True)
    print(f"pronto: {destino}")
    return destino


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    importar(args[0], *(args[1:2]), cor="neutra" if "--cor=neutra" in sys.argv else "cinema", k4="--4k" in sys.argv)
