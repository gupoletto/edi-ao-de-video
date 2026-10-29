#!/usr/bin/env python3
"""Etapa 1: prepara o vídeo da câmera para o kit, sem perder qualidade.

    python3 edicao/ferramentas/importar.py ~/Downloads/IMG_1234.MOV [nome]
        -> edicao/bruto/<nome>.mkv

- HDR (iPhone: HLG/Dolby Vision, BT.2020, 10 bits) vira SDR BT.709 com tonemapping "mobius": sem isso as cores
  saem lavadas e os elementos gráficos (que são SDR) destoam do vídeo.
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


def sondar(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate,avg_frame_rate,color_transfer,pix_fmt", "-of", "json", arq],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)["streams"][0]


def fracao(s):
    n, d = s.split("/")
    return float(n) / float(d) if float(d) else 0.0


def importar(arq, nome=None):
    v = sondar(arq)
    nome = nome or os.path.splitext(os.path.basename(arq))[0]
    destino = os.path.join(BRUTO, nome + ".mkv")
    fps_med = fracao(v["avg_frame_rate"]) or fracao(v["r_frame_rate"])
    fps = 60 if fps_med > 45 else 30
    filtros = []
    if v.get("color_transfer") in HDR:
        filtros += ["zscale=t=linear:npl=100", "format=gbrpf32le", "zscale=p=bt709", "tonemap=mobius:desat=0",
                    "zscale=t=bt709:m=bt709:r=tv"]
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
    importar(sys.argv[1], *(sys.argv[2:3]))
