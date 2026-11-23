"""Folha de prévia de um episódio com os mesmos efeitos do vídeo final (soco, câmera viva, molas).

Uso: python3 previa.py <episodio> <seg:t> [<seg:t> ...] [--saida folha.png]
  ex.: python3 previa.py story_lego 0:0.1 0:3 2:0.1 2:1.5   (seg = índice da cena, t = segundos dentro dela)
Gera uma tira com os quadros lado a lado (270x480 cada). Conferir antes do render completo.
"""
import importlib
import os
import sys

import cairo
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core  # noqa: E402


def main(argv):
    saida = "previa_folha.png"
    if "--saida" in argv:
        i = argv.index("--saida")
        saida = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    ep = importlib.import_module("episodes." + argv[0])
    core.setup()
    segs = core.preparar(ep.SEGMENTS)
    print(round(sum(s.dur for s in segs), 1), [round(s.dur, 1) for s in segs])
    pontos = [tuple(map(float, x.split(":"))) for x in argv[1:]]
    bg = core.background()
    folha = Image.new("RGB", (270 * len(pontos), 480))
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, core.W, core.H)
    ctx = cairo.Context(surf)
    for j, (k, t) in enumerate(pontos):
        core.desenhar_quadro(ctx, segs, segs[int(k)].t0 + t, bg)
        surf.flush()
        img = Image.frombuffer("RGBA", (core.W, core.H), bytes(surf.get_data()), "raw", "BGRA", 0, 1).convert("RGB")
        folha.paste(img.resize((270, 480)), (j * 270, 0))
    folha.save(saida)
    print(saida)


if __name__ == "__main__":
    main(sys.argv[1:])
