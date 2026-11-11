#!/usr/bin/env python3
"""Thumbnail "número de peito" (episódio 21: recorde de 4 km em 19:20), no padrão do canal (marinho, creme, taupe):
a pessoa recortada com contorno branco, título grande à esquerda e um número de peito de corrida com o tempo.

    python3 edicao/ferramentas/thumb_pr.py edicao/bruto/video10.mkv --rosto 112 \\
        --titulo "RECORDE|NOS 4 KM" --sub "Dia 21/30" --numero 21 --itens "4 KM · 19:20" "PACE 4:50"
Saída: edicao/final/<nome>_thumb.jpg (e .png).
"""
import argparse
import math
import os
import subprocess

import cairo

from comum import FINAL, preparar
from thumb import W, H, argb, arredondado, quadro, texto
from thumb_jogo import recorte
from thumb_relogio import CINZA, CREME, NAVY, TAUPE, fundo


def numero_peito(ctx, x, y, num, linhas, ang, escala=1.0):
    """Número de peito de corrida: papel creme com faixa taupe, alfinetes nos cantos, número grande e o tempo."""
    w, h = 420, 300
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(ang))
    ctx.scale(escala, escala)
    arredondado(ctx, 10, 14, w, h, 18)
    ctx.set_source_rgba(0, 0, 0, 0.35)
    ctx.fill()
    arredondado(ctx, 0, 0, w, h, 18)
    ctx.set_source_rgb(*CREME)
    ctx.fill()
    arredondado(ctx, 0, 0, w, 64, 18)
    ctx.rectangle(0, 40, w, 24)
    ctx.set_source_rgb(*TAUPE)
    ctx.fill()
    texto(ctx, "MELHORANDO MINHA VIDA · 30 DIAS", 26, 42, 22, NAVY)
    ctx.select_font_face("Poppins", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(150)
    e = ctx.text_extents(num)
    texto(ctx, num, (w - e.x_advance) / 2, 205, 150, NAVY)
    for i, ln in enumerate(linhas):
        ctx.set_font_size(30)
        e = ctx.text_extents(ln)
        texto(ctx, ln, (w - e.x_advance) / 2, 252 + i * 34, 30, NAVY)
    for px, py in ((22, 84), (w - 22, 84), (22, h - 20), (w - 22, h - 20)):  # alfinetes
        ctx.new_sub_path()
        ctx.arc(px, py, 8, 0, 2 * math.pi)
        ctx.set_source_rgb(*CINZA)
        ctx.fill()
    ctx.restore()


def montar(a):
    preparar()
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    fundo(ctx)
    import numpy as np
    img = quadro(a.fonte, a.rosto)
    img[..., :3] = np.clip(img[..., :3].astype(np.float32) * a.luz, 0, 255).astype(np.uint8)
    pessoa = recorte(img, a.altura, a.contorno, a.cortar_esq, a.cortar_dir)
    ps, _buf = argb(pessoa)
    ctx.set_source_surface(ps, W - pessoa.width + a.desloc[0], H - pessoa.height + a.desloc[1])
    ctx.paint()
    y = 150
    for i, ln in enumerate(a.titulo.split("|")):
        tam = a.tamanho
        texto(ctx, ln, 54 + 6, y + 6, tam, NAVY)
        texto(ctx, ln, 54, y, tam, CREME if i == 0 else TAUPE)
        y += tam * 0.98
    texto(ctx, a.sub, 60, y - 30, 40, CINZA, "Source Serif 4", cairo.FONT_WEIGHT_BOLD, italico=True)
    numero_peito(ctx, 70, y + 20, a.numero, a.itens, -6, 0.95)
    nome = os.path.splitext(os.path.basename(a.fonte))[0]
    png = os.path.join(FINAL, f"{nome}_thumb.png")
    surf.write_to_png(png)
    jpg = png[:-4] + ".jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", png, "-q:v", "2", jpg], check=True)
    print(f"pronto: {jpg}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("fonte")
    ap.add_argument("--rosto", type=float, required=True)
    ap.add_argument("--titulo", required=True, help='linhas separadas por "|"')
    ap.add_argument("--tamanho", type=int, default=104)
    ap.add_argument("--sub", default="")
    ap.add_argument("--itens", nargs="*", default=[])
    ap.add_argument("--altura", type=int, default=700)
    ap.add_argument("--contorno", type=int, default=8)
    ap.add_argument("--cortar-esq", type=float, default=0.0)
    ap.add_argument("--cortar-dir", type=float, default=0.0)
    ap.add_argument("--desloc", type=int, nargs=2, default=[30, 30])
    ap.add_argument("--numero", default="21")
    ap.add_argument("--luz", type=float, default=1.0, help="multiplica o brilho do quadro antes do recorte")
    montar(ap.parse_args())
